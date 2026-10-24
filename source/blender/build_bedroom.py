# -*- coding: utf-8 -*-
"""
Construye los muebles del DORMITORIO (estilo cozy low-poly, como bedroom_night.jpg).

Piezas que busca el juego:
  - dormitorio: cama de madera, cobija, almohadas, mesita con cajón y libros, base de la lámpara,
    celular, alfombra y pantuflas.
  - cama_colchon: el colchón (se le hace clic para dormir).
  - lampara_pantalla: la pantalla de la lámpara (se le hace clic para prender/apagar; usa el material del código).
La casa no está escalada: 1 metro aquí = 1 unidad del juego. Las paredes y el piso los dibuja el código.

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el modelo. Guarda source/blender/bedroom.blend
     y exporta assets/models/environment/bedroom.glb (lo que carga el juego).
  3. Si cambias números aquí y lo vuelves a correr, se rearma todo.
     Si prefieres mover cosas a mano en Blender, NO lo vuelvas a correr después:
     exporta tú con File → Export → glTF 2.0 (.glb) al mismo archivo.

Reglas que el juego necesita:
  - Todo cuelga de "escala_juego" (en la casa la escala es 1: un metro de Blender = un metro del juego).
  - Ejes: +X = lado de la ventanilla / derecha, +Y = adelante, Z = arriba.
  - Los nombres de las piezas de arriba (los "empty") los busca el código: no los cambies.
  - Materiales "luz_..." brillan más de noche; "brillo_..." brillan siempre.
  - Los colores usan los mismos números (hex) que el código, para que se vean igual en el juego.
"""
# ---------- Herramientas compartidas (NO las copies aquí: viven en lib_blender.py) ----------
import bpy, os, sys
try:  # corriendo desde el editor de texto de Blender
    sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
except AttributeError:  # corriendo desde la terminal
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, lib_blender; importlib.reload(lib_blender)
from lib_blender import *


limpiar()

M = {
    'madera': mat('madera', 0x8a5a3a, 0.6),
    'madera_oscura': mat('madera_oscura', 0x5d3a24, 0.65),
    'madera_clara': mat('madera_clara', 0xb07a4c, 0.6),
    'colchon': mat('colchon', 0xf5f2ec, 0.95),
    'sabana': mat('sabana', 0xe8e4dc, 0.95),
    'cobija': mat('cobija', 0x4a6a8a, 0.95),
    'cobija_borde': mat('cobija_borde', 0x6f8fae, 0.95),
    'almohada': mat('almohada', 0xf0eee8, 0.95),
    'alfombra': mat('alfombra', 0xb5654a, 1.0),
    'alfombra_borde': mat('alfombra_borde', 0xf2d7a6, 1.0),
    'cristal': mat('cristal_lampara', 0xe8d9b8, 0.15, 0.2),
    'oscuro': mat('oscuro', 0x1a1a1e, 0.5),
    'pantalla_cel': mat('brillo_celular', 0x1d3557, 0.3, 0, emit=0x4fa3ff, strength=1.0),
    'pantufla': mat('pantufla', 0x3f8f6a, 0.95),
    'libro_rojo': mat('libro_rojo', 0xc0392b, 0.7),
    'libro_azul': mat('libro_azul', 0x2e86c1, 0.7),
    'libro_amarillo': mat('libro_amarillo', 0xf4c430, 0.7),
    # la pantalla de la lámpara: en el juego usa el material del código (así se prende y se apaga con clic)
    'pantalla': mat('luz_pantalla_lampara', 0xffe2b8, 0.6, 0, emit=0xffb866, strength=1.0),
}

root = empty('escala_juego')        # la casa NO está escalada: aquí 1 metro = 1 unidad del juego
fijo = empty('dormitorio', root)     # cama, mesita, alfombra, pantuflas...
colchon = empty('cama_colchon', root)          # el colchón: se le hace clic para dormir
pantalla = empty('lampara_pantalla', root)     # la pantalla de la lámpara: se le hace clic para prender/apagar

# ---------- Medidas (vienen del código; X = x, Y = -z, Z = altura) ----------
# Cama: centro (4, -3) → X 2.9..5.1, Y 1.5..4.5. Colchón arriba en Z = 0.95.
# Cabecero contra la pared en Y ≈ 4.7. Mesita: centro (2.4, -4.2), 0.8 de lado.
BX0, BX1, BY0, BY1 = 2.9, 5.1, 1.5, 4.5

# =====================================================================
# Cama de madera
# =====================================================================
for i, (x, y) in enumerate(((BX0 + 0.08, BY0 + 0.08), (BX1 - 0.08, BY0 + 0.08), (BX0 + 0.08, BY1 - 0.08), (BX1 - 0.08, BY1 - 0.08))):
    box('pata_cama_%d' % i, x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0.0, 0.3, M['madera_oscura'], fijo)
box('base_cama', BX0, BX1, BY0, BY1, 0.22, 0.55, M['madera'], fijo, bevel=0.03)
box('pie_cama', BX0 - 0.02, BX1 + 0.02, BY0 - 0.08, BY0, 0.0, 0.78, M['madera'], fijo, bevel=0.02)
# Cabecero facetado con un panel más oscuro (como vetas de madera)
prism('cabecero', [(BX0 - 0.05, 0.0), (BX1 + 0.05, 0.0), (BX1 + 0.05, 1.3), (BX1 - 0.25, 1.5), (BX0 + 0.25, 1.5), (BX0 - 0.05, 1.3)],
      'Y', 4.62, 4.76, M['madera'], fijo)
box('cabecero_panel', BX0 + 0.25, BX1 - 0.25, 4.6, 4.62, 0.75, 1.3, M['madera_oscura'], fijo)
for k in range(4):
    box('cabecero_veta_%d' % k, BX0 + 0.35, BX1 - 0.35, 4.595, 4.6, 0.86 + k * 0.11, 0.88 + k * 0.11, M['madera_clara'], fijo)

# Colchón (pieza aparte porque se le hace clic) y sábana
box('colchon', BX0 + 0.05, BX1 - 0.05, BY0 + 0.1, BY1 - 0.1, 0.55, 0.95, M['colchon'], colchon, bevel=0.05)
box('sabana_arriba', BX0 + 0.06, BX1 - 0.06, 2.8, BY1 - 0.12, 0.95, 0.97, M['sabana'], fijo)
# Cobija: arriba y caída a los lados (facetada). Llega hasta Y=2.86: al despertar, la cámara está en Y=3 sobre el colchón
box('cobija', BX0 + 0.02, BX1 - 0.02, BY0 + 0.05, 2.8, 0.95, 1.03, M['cobija'], fijo, bevel=0.02)
for s in (-1, 1):
    xe = BX1 - 0.02 if s > 0 else BX0 + 0.02
    pts = [(xe, 1.03), (xe + s * 0.06, 0.98), (xe + s * 0.08, 0.55), (xe, 0.55)]
    if s < 0:
        pts = [(x, z) for x, z in pts]
    prism('cobija_lado_%d' % s, pts, 'Y', BY0 + 0.05, 2.8, M['cobija'], fijo)
prism('cobija_pie', [(BY0 + 0.05, 1.03), (BY0 - 0.01, 0.98), (BY0 - 0.03, 0.62), (BY0 + 0.05, 0.62)], 'X', BX0 + 0.02, BX1 - 0.02, M['cobija'], fijo)
box('cobija_doblez', BX0 + 0.01, BX1 - 0.01, 2.62, 2.86, 1.0, 1.08, M['cobija_borde'], fijo, bevel=0.03)
# Almohadas (dos, un poco giradas no: facetadas con bisel)
for i, x in enumerate((3.5, 4.5)):
    box('almohada_%d' % i, x - 0.42, x + 0.42, 3.75, 4.35, 0.95, 1.16, M['almohada'], fijo, bevel=0.07)

# =====================================================================
# Mesita de noche con cajón, lámpara de cristal y el celular 📱
# =====================================================================
NX0, NX1, NY0, NY1 = 2.0, 2.8, 3.8, 4.6
for i, (x, y) in enumerate(((NX0 + 0.06, NY0 + 0.06), (NX1 - 0.06, NY0 + 0.06), (NX0 + 0.06, NY1 - 0.06), (NX1 - 0.06, NY1 - 0.06))):
    box('pata_mesita_%d' % i, x - 0.04, x + 0.04, y - 0.04, y + 0.04, 0.0, 0.12, M['madera_oscura'], fijo)
box('mesita', NX0 + 0.02, NX1 - 0.02, NY0 + 0.02, NY1 - 0.02, 0.12, 0.76, M['madera'], fijo)
box('mesita_tapa', NX0 - 0.03, NX1 + 0.03, NY0 - 0.03, NY1 + 0.03, 0.76, 0.8, M['madera_clara'], fijo, bevel=0.01)
box('mesita_cajon', NX0 + 0.08, NX1 - 0.08, NY0, NY0 + 0.02, 0.48, 0.7, M['madera_clara'], fijo)
cyl('mesita_perilla', (2.4, NY0 - 0.02, 0.59), 0.03, 0.04, 'Y', M['oscuro'], fijo, segs=6)
box('mesita_hueco', NX0 + 0.08, NX1 - 0.08, NY0 + 0.0, NY0 + 0.02, 0.18, 0.42, M['madera_oscura'], fijo)
for i, (col, h) in enumerate((('libro_rojo', 0.05), ('libro_azul', 0.04), ('libro_amarillo', 0.05))):   # libros en el hueco
    z0 = 0.19 + sum((0.05, 0.04, 0.05)[:i])
    box('libro_%d' % i, NX0 + 0.14 + 0.02 * i, NX1 - 0.16 - 0.03 * i, NY0 + 0.06, NY1 - 0.12, z0, z0 + h - 0.005, M[col], fijo)
# Lámpara: base de cristal facetada + pantalla (pieza aparte)
cyl('lampara_base', (2.4, 4.2, 0.83), 0.08, 0.06, 'Z', M['madera_oscura'], fijo, segs=8)
cyl('lampara_cristal_abajo', (2.4, 4.2, 0.9), 0.1, 0.08, 'Z', M['cristal'], fijo, segs=6, r2=0.13)
cyl('lampara_cristal_arriba', (2.4, 4.2, 0.98), 0.13, 0.08, 'Z', M['cristal'], fijo, segs=6, r2=0.06)
cyl('lampara_pantalla', (2.4, 4.2, 1.11), 0.2, 0.26, 'Z', M['pantalla'], pantalla, segs=8, r2=0.13)
# Celular
box('celular', 2.15, 2.3, 3.9, 4.18, 0.8, 0.815, M['oscuro'], fijo, bevel=0.005)
box('celular_pantalla', 2.16, 2.29, 3.91, 4.17, 0.815, 0.818, M['pantalla_cel'], fijo)

# =====================================================================
# Alfombra al lado de la cama y pantuflas
# =====================================================================
box('alfombra_borde', 1.2, 2.75, 1.1, 3.6, 0.0, 0.015, M['alfombra_borde'], fijo)
box('alfombra', 1.28, 2.67, 1.18, 3.52, 0.0, 0.02, M['alfombra'], fijo)
for k in range(3):
    box('alfombra_raya_%d' % k, 1.28, 2.67, 1.6 + k * 0.6, 1.68 + k * 0.6, 0.0, 0.022, M['alfombra_borde'], fijo)
for i, x in enumerate((2.2, 2.45)):
    box('pantufla_%d' % i, x - 0.08, x + 0.08, 2.0, 2.32, 0.02, 0.08, M['pantufla'], fijo, bevel=0.03)
    box('pantufla_punta_%d' % i, x - 0.08, x + 0.08, 2.2, 2.32, 0.08, 0.12, M['pantufla'], fijo, bevel=0.03)

# ---------- Guardar y exportar ----------
blend_path = os.path.join(REPO, 'source', 'blender', 'bedroom.blend')
glb_path = os.path.join(REPO, *'assets/models/environment/bedroom.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo, colchon, pantalla], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
