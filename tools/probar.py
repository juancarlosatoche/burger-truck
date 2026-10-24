# -*- coding: utf-8 -*-
"""
PROBAR EL JUEGO: abre el juego en un navegador invisible, toma fotos desde cámaras con nombre,
corre pruebas de juego y avisa si hay errores en la consola o modelos que no cargaron.

Instalar una vez:   pip install playwright pillow   y luego   python3 -m playwright install chromium
(Si no hay internet para los CDN, se baja Three.js r128 con npm a tools/.vendor/ y se usa esa copia.)

Ejemplos:
  python3 tools/probar.py --lista                      ver las vistas y pruebas que hay
  python3 tools/probar.py freidora                     una foto de la freidora
  python3 tools/probar.py freidora nevera plato        tres vistas en UNA hoja (tools/capturas/hoja.png)
  python3 tools/probar.py plaza --hora 21              la plaza a las 9 PM
  python3 tools/probar.py todas                        todas las vistas en una hoja
  python3 tools/probar.py --prueba papas combo         pruebas de juego (sin fotos)
  python3 tools/probar.py --ojo 60,3,45 --mira 84,8,52   cualquier ángulo, sin editar este archivo
  python3 tools/probar.py --ojo 0,1.6,1 --mira -0.9,1,1 --en truck   igual, con medidas del truck
  python3 tools/probar.py --ojo 2,2.1,0 --mira 4,1,-3 --escena casa  igual, en la casa
  python3 tools/probar.py freidora --js "freidora.estado='lista'"   correr código antes de la foto
  python3 tools/probar.py freidora --referencia        además guarda la foto en reference/screenshots/

Sale con código 1 si hay errores en la consola, modelos que fallaron o pruebas que no pasaron.
"""
import argparse, datetime, functools, http.server, json, os, shutil, socket, subprocess, sys, threading, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..'))
VENDOR = os.path.join(AQUI, '.vendor')
CAPTURAS = os.path.join(AQUI, 'capturas')

# =====================================================================
# VISTAS: dónde va la cámara.
#   escena: 'truck' (adentro o afuera del food truck, en la plaza), 'casa' o 'manejar'
#   en:     'truck' = medidas del truck (como en buildFoodTruckKitchen), 'mundo' = medidas del mundo
#   ojo / mira: posición de la cámara y el punto al que mira
#   hora:   hora por defecto (17 = 5 PM ... 23 = 11 PM)
# Para agregar una vista nueva, copia una línea y cambia los números.
# =====================================================================
VISTAS = {
    # --- adentro del truck ---
    'ventanilla': dict(escena='truck', en='truck', ojo=(-0.6, 1.5, 0.2), mira=(2.5, 1.45, 0.2), hora=18.5, que='mostrador y clientes, como el style target truck_window_dusk'),
    'freidora':   dict(escena='truck', en='truck', ojo=(-0.45, 1.25, 1.35), mira=(-0.95, 0.95, 1.05), hora=18, que='freidora de cerca'),
    'plancha':    dict(escena='truck', en='truck', ojo=(0.1, 1.45, 0.9), mira=(-0.95, 0.95, 0.2), hora=18, que='plancha, freidora y panes'),
    'nevera':     dict(escena='truck', en='truck', ojo=(0.25, 1.95, -1.75), mira=(-0.75, 1.85, -2.15), hora=18, que='nevera abierta con los ingredientes'),
    'plato':      dict(escena='truck', en='truck', ojo=(-0.3, 1.45, 0.3), mira=(0.9, 0.95, 0.3), hora=18, que='plato, cajas de papas, computadora y caja'),
    'puerta':     dict(escena='truck', en='truck', ojo=(0.0, 1.45, -1.5), mira=(0.0, 1.2, 2.75), hora=18, que='pasillo hacia la puerta de atrás'),
    # --- afuera, en la plaza ---
    'truck_afuera': dict(escena='truck', en='mundo', ojo=(62, 2.2, 40), mira=(51, 2.5, 50), hora=21, que='el truck y la fila, como truck_exterior_night'),
    'plaza':        dict(escena='truck', en='mundo', ojo=(58, 2.2, 50), mira=(84, 9, 51), hora=21, que='plaza, guirnaldas y edificios de noche'),
    'edificios':    dict(escena='truck', en='mundo', ojo=(66, 3, 34), mira=(84, 8, 52), hora=18, que='los 5 edificios de lado'),
    'calle':        dict(escena='truck', en='mundo', ojo=(50, 2.2, 70), mira=(50, 1.5, 58), hora=19, que='calle de atrás, donde llega el repartidor'),
    # --- casa ---
    'cuarto':     dict(escena='casa', en='mundo', ojo=(1.8, 2.1, 0.5), mira=(4, 1.0, -3.5), hora=23.5, que='cuarto de noche, como bedroom_night'),
    'sala':       dict(escena='casa', en='mundo', ojo=(-1.8, 2.1, -1.8), mira=(-3.6, 0.7, 2.0), hora=16.4, que='sala con el sofá'),
    'cocina_casa': dict(escena='casa', en='mundo', ojo=(0, 2.1, -5.6), mira=(0, 1.2, -10), hora=16.4, que='cocina-comedor de la mañana, como kitchen_morning'),
    # --- manejando ---
    'manejar':    dict(escena='manejar', que='primera persona en la cabina, como driving_first_person'),
}

# =====================================================================
# PRUEBAS DE JUEGO: código que corre en la página y devuelve {ok, log}.
# Usan las mismas funciones del juego (pickUpItem, usarFreidora, placeItemOnPlate, serveCustomer...).
# =====================================================================
JS_AYUDA = """
window.__prueba = {
  poner: (t) => { heldItem = { type: t, label: LBL[t] || t }; placeItemOnPlate(); },
  limpiar: () => { while (plateGroup.children.length > 1) plateGroup.remove(plateGroup.children[1]); burgerStack.length = 0; heldItem = null; updateHeld3DMesh(); },
  aviso: () => document.getElementById('job-banner').innerText,
  servir: (nombre) => { const c = frontCustomer(); c.recipe = RECIPES.find(r => r.n === nombre); const antes = money; serveCustomer(c); return money - antes; },
};
"""
PRUEBAS = {
    'hamburguesa': ('Arma una Clásica y la sirve', """async () => {
        const P = __prueba, log = []; P.limpiar();
        ['PAN_ABAJO', 'CARNE_COCINADA', 'QUESO', 'PAN_ARRIBA'].forEach(P.poner); log.push(P.aviso());
        const ganó = P.servir('Clásica'); log.push('cobró $' + ganó);
        return { ok: ganó > 0 && burgerStack.length === 0, log };
    }"""),
    'papas': ('Nevera → freidora → caja → plato → cliente', """async () => {
        const P = __prueba, log = []; P.limpiar();
        const cruda = interactableObjects.find(o => o.userData.ingredientType === 'PAPAS_CRUDAS');
        if (!cruda) return { ok: false, log: ['no hay papas crudas en la nevera'] };
        pickUpItem(cruda); usarFreidora(); log.push('freidora: ' + freidora.estado);
        // El tiempo de la freidora avanza con cada cuadro dibujado. Sin tarjeta de video hay pocos cuadros,
        // así que se adelanta el reloj de la freidora (lo que se prueba es que termine y se puedan sacar las papas).
        await new Promise(r => setTimeout(r, 500)); freidora.t = TIEMPO_FREIR - 0.01;
        const t0 = Date.now(); while (freidora.estado !== 'lista' && Date.now() - t0 < 30000) await new Promise(r => setTimeout(r, 100));
        log.push('freidora: ' + freidora.estado);
        usarFreidora(); usarCajaPapas(); log.push('en la mano: ' + (heldItem && heldItem.type));
        placeItemOnPlate(); const ganó = P.servir('Papas Fritas'); log.push('cobró $' + ganó);
        return { ok: ganó > 0, log };
    }"""),
    'combo': ('Papas primero y hamburguesa al lado = Combo Clásica, con más paciencia', """async () => {
        const P = __prueba, log = []; P.limpiar();
        P.poner('PAPAS_CAJA'); ['PAN_ABAJO', 'CARNE_COCINADA', 'QUESO', 'PAN_ARRIBA'].forEach(P.poner); log.push(P.aviso());
        const combo = RECIPES.find(r => r.n === 'Combo Clásica'), ok1 = platoCoincide(combo) && !platoCoincide(RECIPES[0]);
        const ganó = P.servir('Combo Clásica'); log.push('cobró $' + ganó);
        log.push('paciencia extra de los combos: ' + COMBO_TIEMPO_EXTRA + ' s');
        return { ok: ok1 && ganó > 0 && COMBO_TIEMPO_EXTRA > 0, log };
    }"""),
    'errores_plato': ('El plato rechaza papas crudas, papas sin caja y dos cajas', """async () => {
        const P = __prueba, log = []; P.limpiar();
        P.poner('PAPAS_CRUDAS'); const a = burgerStack.length === 0; log.push(P.aviso());
        P.poner('PAPAS_FRITAS'); const b = burgerStack.length === 0; log.push(P.aviso());
        P.poner('PAPAS_CAJA'); P.poner('PAPAS_CAJA'); const c = burgerStack.length === 1; log.push(P.aviso());
        P.limpiar(); return { ok: a && b && c, log };
    }"""),
}


# ---------- Servidor local (sirve la carpeta del juego) ----------
def servidor():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); puerto = s.getsockname()[1]; s.close()
    class Callado(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):   # no llenar la pantalla con cada archivo pedido
            pass
    manejador = functools.partial(Callado, directory=REPO)
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', puerto), manejador)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, puerto


# ---------- ¿Hay internet para los CDN? Si no, usar Three.js r128 local ----------
def hay_cdn():
    try:
        urllib.request.urlopen('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', timeout=5).read(100)
        return True
    except Exception:
        return False


def three_local():
    carpeta = os.path.join(VENDOR, 'node_modules', 'three')
    if not os.path.exists(os.path.join(carpeta, 'build', 'three.min.js')):
        print('⏳ Sin acceso a los CDN: bajando three@0.128.0 con npm a tools/.vendor/ (solo la primera vez)...')
        os.makedirs(VENDOR, exist_ok=True)
        subprocess.run(['npm', 'install', '--silent', '--prefix', VENDOR, 'three@0.128.0'], check=True)
    return carpeta


def ruta_offline(carpeta_three, puerto):
    def ruta(r):
        u = r.request.url
        if u.startswith('http://127.0.0.1:%d' % puerto):
            return r.continue_()
        if 'three.min.js' in u:
            return r.fulfill(path=os.path.join(carpeta_three, 'build', 'three.min.js'), content_type='application/javascript')
        if '/three@0.128.0/' in u:
            return r.fulfill(path=os.path.join(carpeta_three, *u.split('/three@0.128.0/')[1].split('?')[0].split('/')), content_type='application/javascript')
        return r.fulfill(body='', content_type='text/plain')   # Tailwind y fuentes: no hacen falta para las fotos
    return ruta


# ---------- Preparar cada escena ----------
def ir_a(pg, escena, estado):
    if estado.get('escena') == escena:
        return
    if escena == 'truck':
        pg.evaluate("""() => { foodTruckGroup.position.set(50, 0, 50); foodTruckGroup.rotation.y = 0; teleportToFoodTruck(true); }""")
        time.sleep(2.5)
    elif escena == 'casa':
        pg.evaluate("""() => { currentScene = 'HOME'; setSceneLights('HOME'); }""")
    elif escena == 'manejar':
        pg.evaluate("startDriving(true)")
        time.sleep(4)
    pg.evaluate("""() => { document.getElementById('mobile-controls').classList.add('hidden'); fallbackMode = false; renderer.setPixelRatio(1); }""")
    estado['escena'] = escena


def poner_hora(pg, escena, hora):
    if hora is None:
        return
    if escena == 'truck':
        pg.evaluate("(h) => { gameMin = Math.max(0, Math.min(359, (h - 17) * 60)); setTimeOfDay(17 + gameMin / 60); }", hora)
    elif escena == 'casa':
        pg.evaluate("(h) => { homeHour = h; setTimeOfDay(h); }", hora)


def poner_camara(pg, v):
    if 'ojo' not in v:
        return
    pg.evaluate("""([en, ojo, mira]) => {
        const a = new THREE.Vector3(...ojo), b = new THREE.Vector3(...mira);
        if (en === 'truck') { foodTruckGroup.updateMatrixWorld(true); foodTruckGroup.localToWorld(a); foodTruckGroup.localToWorld(b); }
        camera.position.copy(a); camera.lookAt(b);
    }""", [v.get('en', 'mundo'), list(v['ojo']), list(v['mira'])])


# ---------- Hoja de contactos: varias fotos en una imagen con su nombre ----------
def hoja(fotos, salida):
    from PIL import Image, ImageDraw
    ims = [(n, Image.open(p).convert('RGB')) for n, p in fotos]
    w, h = ims[0][1].size
    cols = 1 if len(ims) == 1 else 2 if len(ims) <= 4 else 3
    filas = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * w, filas * h), (20, 20, 24))
    d = ImageDraw.Draw(out)
    for i, (n, im) in enumerate(ims):
        x, y = (i % cols) * w, (i // cols) * h
        out.paste(im, (x, y))
        if len(ims) > 1:
            d.rectangle([x, y, x + 8 * len(n) + 14, y + 22], fill=(0, 0, 0))
            d.text((x + 7, y + 5), n, fill=(255, 220, 120))
    out.save(salida)


def main():
    ap = argparse.ArgumentParser(description='Prueba el juego y toma fotos desde cámaras con nombre.')
    ap.add_argument('vistas', nargs='*', help='nombres de vistas (o "todas")')
    ap.add_argument('--lista', action='store_true', help='muestra las vistas y pruebas que hay')
    ap.add_argument('--prueba', nargs='+', default=[], help='pruebas de juego (o "todas")')
    # ✨ Cámara libre: un ángulo cualquiera sin agregar una vista a VISTAS (sale con el nombre "libre")
    ap.add_argument('--ojo', help='posición de la cámara "x,y,z"')
    ap.add_argument('--mira', help='punto al que mira la cámara "x,y,z" (hace falta con --ojo)')
    ap.add_argument('--en', choices=['mundo', 'truck'], default='mundo', help='medidas de --ojo y --mira: del mundo (por defecto) o del truck')
    ap.add_argument('--escena', choices=['truck', 'casa', 'manejar'], default='truck', help='escena para la cámara libre (por defecto truck, que incluye la plaza)')
    ap.add_argument('--hora', type=float, help='hora para todas las vistas (17 a 23 en el truck)')
    ap.add_argument('--js', help='código JavaScript que corre antes de cada foto')
    ap.add_argument('--ancho', type=int, default=640, help='ancho de cada foto (más chica = más rápida y gasta menos)')
    ap.add_argument('--interfaz', action='store_true', help='dejar visibles los letreros y botones del juego')
    ap.add_argument('--referencia', action='store_true', help='copiar cada foto a reference/screenshots/<vista>_<fecha>.png')
    # Para que "--ojo -0.4,1.3,1.3" funcione (argparse cree que "-0.4,..." es otra opción), se pega como "--ojo=-0.4,..."
    argv, i = [], 0
    while i < len(sys.argv[1:]):
        x = sys.argv[1 + i]
        if x in ('--ojo', '--mira') and i + 1 < len(sys.argv[1:]):
            argv.append(x + '=' + sys.argv[2 + i]); i += 2
        else:
            argv.append(x); i += 1
    a = ap.parse_args(argv)

    if a.ojo or a.mira:
        try:
            ojo, mira = [tuple(float(x) for x in t.split(',')) for t in (a.ojo, a.mira)]
            assert len(ojo) == 3 and len(mira) == 3
        except (AttributeError, ValueError, AssertionError):
            sys.exit('Usa --ojo x,y,z y --mira x,y,z juntos, con 3 números cada uno (ej: --ojo 60,3,45 --mira 84,8,52).')
        VISTAS['libre'] = dict(escena=a.escena, en=a.en, ojo=ojo, mira=mira, que='cámara libre')
        a.vistas.append('libre')
    if a.lista or (not a.vistas and not a.prueba):
        print('VISTAS:'); [print('  %-13s %s' % (k, v['que'])) for k, v in VISTAS.items()]
        print('  (o una cámara libre: --ojo x,y,z --mira x,y,z [--en truck] [--escena casa])')
        print('PRUEBAS:'); [print('  %-13s %s' % (k, v[0])) for k, v in PRUEBAS.items()]
        return
    vistas = list(VISTAS) if 'todas' in a.vistas else a.vistas
    pruebas = list(PRUEBAS) if 'todas' in a.prueba else a.prueba
    malas = [v for v in vistas if v not in VISTAS] + [p for p in pruebas if p not in PRUEBAS]
    if malas:
        sys.exit('No existe: %s. Usa --lista para ver los nombres.' % ', '.join(malas))

    from playwright.sync_api import sync_playwright
    httpd, puerto = servidor()
    offline = not hay_cdn()
    t0, problemas, errores, modelos = time.time(), [], [], {}
    os.makedirs(CAPTURAS, exist_ok=True)
    with sync_playwright() as p:
        args = ['--ignore-gpu-blocklist'] + (['--use-gl=angle', '--use-angle=swiftshader'] if sys.platform.startswith('linux') else [])
        nav = p.chromium.launch(args=args)
        pg = nav.new_page(viewport={'width': a.ancho, 'height': int(a.ancho * 0.625)})
        if offline:
            pg.route('**/*', ruta_offline(three_local(), puerto))
        pg.on('console', lambda m: errores.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errores.append('ERROR DE JS: %s' % e))
        pg.on('response', lambda r: modelos.__setitem__(r.url.split('/')[-1].split('?')[0], r.status) if '.glb' in r.url else None)
        pg.on('requestfailed', lambda r: modelos.__setitem__(r.url.split('/')[-1].split('?')[0], 'falló') if '.glb' in r.url else None)
        pg.goto('http://127.0.0.1:%d/index.html' % puerto, wait_until='load', timeout=180000)
        pg.wait_for_load_state('networkidle', timeout=180000)
        time.sleep(2)
        if not a.interfaz:
            pg.add_style_tag(content='body>div:not(#canvas-container){display:none!important} canvas{position:fixed;top:0;left:0}')
        pg.evaluate("document.getElementById('instructions').style.display = 'none'")
        pg.evaluate(JS_AYUDA)
        estado, fotos = {}, []

        for nombre in pruebas:
            ir_a(pg, 'truck', estado)
            r = pg.evaluate(PRUEBAS[nombre][1])
            print('%s prueba %s' % ('✅' if r['ok'] else '❌', nombre)); [print('     ' + x) for x in r['log']]
            if not r['ok']:
                problemas.append('prueba %s' % nombre)

        for nombre in vistas:
            v = VISTAS[nombre]
            ir_a(pg, v['escena'], estado)
            poner_hora(pg, v['escena'], a.hora if a.hora is not None else v.get('hora'))
            poner_camara(pg, v)
            if a.js:
                pg.evaluate('() => { %s }' % a.js)
            time.sleep(1.5)
            ruta = os.path.join(CAPTURAS, nombre + '.png')
            pg.screenshot(path=ruta, timeout=180000)
            fotos.append((nombre, ruta))
            if a.referencia:
                destino = os.path.join(REPO, 'reference', 'screenshots', '%s_%s.png' % (nombre, datetime.date.today().isoformat()))
                shutil.copy(ruta, destino)
                print('📁 guardada en', os.path.relpath(destino, REPO))
        nav.close()
    httpd.shutdown()

    if fotos:
        salida = os.path.join(CAPTURAS, 'hoja.png')
        hoja(fotos, salida)
        print('📸 %d vista(s) → %s' % (len(fotos), os.path.relpath(salida, os.getcwd())))
    malos = {k: v for k, v in modelos.items() if v not in (200, 304)}
    print('🧊 modelos: %d cargados%s' % (len(modelos) - len(malos), (', FALLARON: %s' % malos) if malos else ''))
    errores = [e for e in errores if 'favicon' not in e]
    if errores:
        print('⚠️  errores en la consola:'); [print('     ' + e[:300]) for e in errores[:15]]
    print('⏱️  %.0f s%s' % (time.time() - t0, ' (sin internet: Three.js local)' if offline else ''))
    if malos or errores or problemas:
        sys.exit(1)


if __name__ == '__main__':
    main()
