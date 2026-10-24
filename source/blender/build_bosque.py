# -*- coding: utf-8 -*-
"""
Construye el BOSQUE del camino entre la casa y la plaza (estilo cozy low-poly), siguiendo:
  reference/environment/bosque_hoja.png   (los árboles y plantas, uno por uno)
  reference/environment/bosque_plano.png  (cómo se reparten: bosque denso, laguna, claro con hongos)
  reference/style-targets/camino_bosque.png (cómo se ve desde el asiento del conductor)

Piezas que busca el juego:
  - bosque:   la raíz (si no está, el juego no carga nada)
  - plantas:  copias de ~20 modelos de árboles y plantas. El juego dibuja juntas las copias iguales.
  - camino:   camino de tierra de donde arranca el truck hasta el patio pavimentado de atrás de la plaza
  - laguna:   laguna con juncos

Ejes: X = x del juego, Y = -z del juego, Z = arriba. 1 metro = 1 unidad del juego (no está escalado).
Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
Desde la terminal: python3 build_bosque.py   (con el módulo bpy instalado)

Para cambiar el bosque: los modelos están en "MODELOS", dónde va cada cosa en "DÓNDE VA CADA COSA".
Cambia SEMILLA para otro reparto al azar (siempre sale igual con la misma semilla).
"""
# ---------- Herramientas compartidas (NO las copies aquí: viven en lib_blender.py) ----------
import bpy, os, sys
try:  # corriendo desde el editor de texto de Blender
    sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
except AttributeError:  # corriendo desde la terminal
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, lib_blender; importlib.reload(lib_blender)
from lib_blender import *

SEMILLA = 7
limpiar()
# Estos colores se pintan en cada parte de las plantas; cada copia cambia un poquito de tono (lo hace el juego)
M = {
    'tronco': mat('tronco', 0x6b4a2f, 0.9), 'tronco_oscuro': mat('tronco_oscuro', 0x4a3324, 0.9),
    'tronco_blanco': mat('tronco_blanco', 0xeee8dc, 0.8), 'mancha': mat('mancha', 0x2a2522, 0.9),
    'madera_clara': mat('madera_clara', 0xc9a27a, 0.9),
    'hoja_verde': mat('hoja_verde', 0x4f9a3a, 0.85), 'hoja_lima': mat('hoja_lima', 0x8cc63f, 0.85),
    'hoja_esmeralda': mat('hoja_esmeralda', 0x2f7d45, 0.85), 'hoja_oliva': mat('hoja_oliva', 0x9aa035, 0.85),
    'hoja_dorada': mat('hoja_dorada', 0xd2a72a, 0.85), 'hoja_naranja': mat('hoja_naranja', 0xe5782a, 0.85),
    'hoja_rojiza': mat('hoja_rojiza', 0xc9502c, 0.85), 'hoja_rosa': mat('hoja_rosa', 0xf2a2c6, 0.8),
    'hoja_amarilla': mat('hoja_amarilla', 0xe6cf3a, 0.85),
    'hoja_pino': mat('hoja_pino', 0x2f6e5c, 0.85), 'hoja_pino_verde': mat('hoja_pino_verde', 0x3e7f3c, 0.85),
    'hoja_arbusto': mat('hoja_arbusto', 0x3f7d36, 0.85), 'hoja_helecho': mat('hoja_helecho', 0x5c9a3a, 0.85),
    'hoja_pasto': mat('hoja_pasto', 0x7fae45, 0.85), 'tallo': mat('tallo', 0x4c7a34, 0.85),
    'baya': mat('baya', 0xd8262e, 0.5), 'flor_amarilla': mat('flor_amarilla', 0xf4c430, 0.6),
    'flor_morada': mat('flor_morada', 0x9b6bd1, 0.6), 'flor_blanca': mat('flor_blanca', 0xf4f1e8, 0.6),
    'flor_rosa': mat('flor_rosa', 0xf28fb3, 0.6), 'cardo': mat('cardo', 0x8a5fb0, 0.7),
    'hongo_rojo': mat('hongo_rojo', 0xd23b2f, 0.55), 'hongo_cafe': mat('hongo_cafe', 0xb07a4a, 0.7),
    'hongo_pie': mat('hongo_pie', 0xf0e6d0, 0.7),
    'roca': mat('roca', 0x8b8f93, 0.95), 'musgo': mat('musgo', 0x86a83a, 0.95),
    'agua': mat('agua', 0x5fb4c4, 0.35), 'orilla': mat('orilla', 0x7a6a48, 0.95),
    'junco': mat('junco', 0x5b7a2e, 0.85), 'junco_punta': mat('junco_punta', 0x6b4426, 0.9),
    'camino': mat('camino', 0xc49a62, 0.95), 'camino_borde': mat('camino_borde', 0x8f8a4a, 0.95),
}
# Todos los árboles y plantas usan UN material, con el color pintado en cada parte (ver unir en lib_blender.py)
PLANTA = mat_colores('planta', 0.85)
root = empty('bosque')   # la raíz; el bosque NO está escalado: 1 metro = 1 unidad del juego
plantas = empty('plantas', root)
camino = empty('camino', root)
laguna = empty('laguna', root)
modelos = empty('modelos_sueltos')   # aquí se arman los modelos antes de repartir las copias

def P(x, z):
    """Del juego (x, z) a Blender (X, Y): Y = -z."""
    return x, -z

# =====================================================================
# Ayudantes para armar plantas
# =====================================================================
def abollar(o, rng, k):
    """Mueve un poquito cada punto, para que las copas no se vean perfectas."""
    for v in o.data.vertices:
        v.co += Vector((rng.uniform(-k, k), rng.uniform(-k, k), rng.uniform(-k, k)))
    return o

def copa(partes, rng, centro, r, m, sz=1.0):
    """Una "bola" de hojas: con 80 caras si es muy grande, con 20 si no (como las copas facetadas de la hoja)."""
    o = ico('copa', centro, r, M[m], modelos, sub=2 if r > 1.1 else 1, sz=sz)
    partes.append(abollar(o, rng, r * 0.09))

def hoja_plana(partes, p0, p1, ancho, m, grosor=0.02):
    """Hoja o brizna con forma de rombo, de p0 (base) a p1 (punta)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    lado = d.cross(Vector((0, 0, 1)))
    lado = (lado if lado.length > 1e-4 else Vector((1, 0, 0))).normalized() * ancho / 2
    arriba = lado.cross(d).normalized() * grosor
    medio = p0 + d * 0.4
    bm = bmesh.new()
    a, b = bm.verts.new(p0), bm.verts.new(p1)
    i, dd = bm.verts.new(medio - lado), bm.verts.new(medio + lado)
    s, n = bm.verts.new(medio + arriba), bm.verts.new(medio - arriba)
    for c in ((a, i, s), (a, s, dd), (a, dd, n), (a, n, i), (b, s, i), (b, dd, s), (b, n, dd), (b, i, n)):
        bm.faces.new(c)
    partes.append(from_bm('hoja', bm, M[m], modelos))

def punto_en(rng, centro, r, arriba=0.0):
    """Un punto en la superficie de una bola (para poner bayas o flores encima)."""
    d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(arriba, 1))).normalized()
    return Vector(centro) + d * r

# =====================================================================
# MODELOS (cada uno se arma una sola vez; luego se reparten copias)
# =====================================================================
def roble(nombre, hojas, semilla):
    """Roble grande: tronco grueso con dos ramas y una copa de muchas bolas (como "Mature Oak")."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 0.25), 0.55, 0.5, 'Z', M['tronco'], modelos, segs=7, r2=0.32))
    partes.append(cyl('t', (0, 0, 1.6), 0.32, 2.7, 'Z', M['tronco'], modelos, segs=7, r2=0.2))
    partes.append(beam('r', (0, 0, 2.0), (1.0, 0.3, 3.1), 0.2, M['tronco'], modelos))
    partes.append(beam('r', (0, 0, 2.2), (-0.9, -0.4, 3.2), 0.18, M['tronco'], modelos))
    for j, (dx, dy, dz, r) in enumerate(((0, 0, 4.0, 1.55), (1.3, 0.3, 3.5, 1.15), (-1.2, -0.4, 3.6, 1.2),
                                         (0.3, 1.2, 3.4, 1.05), (-0.3, -1.2, 3.3, 1.05), (0.6, -0.3, 4.9, 1.05),
                                         (-0.6, 0.5, 4.7, 1.0))):
        copa(partes, rng, (dx + rng.uniform(-0.2, 0.2), dy + rng.uniform(-0.2, 0.2), dz), r, hojas[j % len(hojas)])
    return unir(nombre, partes, modelos, colores=PLANTA)

def arce(nombre, hojas, semilla):
    """Arce joven: tronco delgado y copa chica de bolas (como "Young Maple")."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 1.2), 0.16, 2.4, 'Z', M['tronco'], modelos, segs=6, r2=0.1))
    partes.append(beam('r', (0, 0, 1.7), (0.5, 0.2, 2.4), 0.09, M['tronco'], modelos))
    for j, (dx, dy, dz, r) in enumerate(((0, 0, 3.2, 0.85), (0.6, 0.2, 2.7, 0.65), (-0.55, -0.2, 2.8, 0.65),
                                         (0.1, -0.6, 2.6, 0.6), (-0.1, 0.5, 3.7, 0.6))):
        copa(partes, rng, (dx, dy, dz), r, hojas[j % len(hojas)])
    return unir(nombre, partes, modelos, colores=PLANTA)

def sicomoro(nombre, hojas, semilla):
    """Sicomoro: copa alta y ovalada, con algunas bolas de otro color (como "Sycamore")."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 1.3), 0.22, 2.6, 'Z', M['tronco'], modelos, segs=7, r2=0.14))
    for j, (dx, dy, dz, r) in enumerate(((0, 0, 2.9, 1.1), (0.7, 0.3, 3.6, 0.95), (-0.7, -0.2, 3.5, 0.95),
                                         (0.2, -0.6, 4.3, 0.9), (-0.2, 0.6, 4.4, 0.85), (0, 0, 5.1, 0.8),
                                         (0.6, -0.5, 2.7, 0.75))):
        copa(partes, rng, (dx, dy, dz), r, hojas[j % len(hojas)], sz=1.1)
    return unir(nombre, partes, modelos, colores=PLANTA)

def paraguas(nombre, hojas, semilla):
    """Árbol ancho como un paraguas: tronco alto y copa aplastada."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 1.6), 0.22, 3.2, 'Z', M['tronco_oscuro'], modelos, segs=7, r2=0.14))
    for a in range(3):
        ang = a * 2.1
        partes.append(beam('r', (0, 0, 2.8), (1.2 * math.cos(ang), 1.2 * math.sin(ang), 3.7), 0.12, M['tronco_oscuro'], modelos))
    for j in range(6):
        ang = j * math.pi / 3 + rng.uniform(-0.2, 0.2)
        copa(partes, rng, (1.5 * math.cos(ang), 1.5 * math.sin(ang), 3.9 + rng.uniform(-0.2, 0.2)), 1.05, hojas[j % len(hojas)], sz=0.6)
    copa(partes, rng, (0, 0, 4.3), 1.2, hojas[0], sz=0.6)
    return unir(nombre, partes, modelos, colores=PLANTA)

def abeto(nombre, capas, alto, ancho, m):
    """Abeto: conos apilados, cada uno más chico (como "Spruce" y "Small Fir")."""
    partes = [cyl('t', (0, 0, 0.35), 0.18 * ancho / 1.6, 0.7, 'Z', M['tronco'], modelos, segs=6)]
    for j in range(capas):
        f = j / max(1, capas - 1)
        z0 = 0.6 + f * (alto - 1.6)
        r = ancho * (1 - 0.72 * f)
        partes.append(cyl('c', (0, 0, z0 + r * 0.55), r, r * 1.15, 'Z', M[m], modelos, segs=8, r2=r * 0.08))
    partes.append(cyl('c', (0, 0, alto - 0.35), ancho * 0.22, 0.75, 'Z', M[m], modelos, segs=6, r2=0.0))
    return unir(nombre, partes, modelos, colores=PLANTA)

def pino_alto(nombre, semilla):
    """Pino alto: tronco largo con ramas cortas y matas de agujas (como "Pine")."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 3.2), 0.2, 6.4, 'Z', M['tronco'], modelos, segs=6, r2=0.1))
    for j in range(6):
        z = 2.6 + j * 0.7
        ang = j * 2.4
        largo = 0.9 - j * 0.08
        fin = (largo * math.cos(ang), largo * math.sin(ang), z + 0.3)
        partes.append(beam('r', (0, 0, z), fin, 0.08, M['tronco'], modelos))
        copa(partes, rng, fin, 0.62 - j * 0.04, 'hoja_pino', sz=0.55)
    copa(partes, rng, (0, 0, 6.7), 0.55, 'hoja_pino', sz=0.8)
    return unir(nombre, partes, modelos, colores=PLANTA)

def abedul(nombre, hojas, semilla):
    """Abedul: tronco blanco con manchas negras y muchas bolitas de hojas (como "White Birch")."""
    rng, partes = random.Random(semilla), []
    partes.append(cyl('t', (0, 0, 2.6), 0.13, 5.2, 'Z', M['tronco_blanco'], modelos, segs=6, r2=0.07))
    for k in range(7):
        z, ang = 0.4 + k * 0.6, rng.uniform(0, 6.3)
        x, y = 0.12 * math.cos(ang), 0.12 * math.sin(ang)
        partes.append(box('m', x - 0.05, x + 0.05, y - 0.05, y + 0.05, z, z + 0.06, M['mancha'], modelos))
    for k in range(3):
        ang = k * 2.1 + 0.5
        partes.append(beam('r', (0, 0, 3.0 + k * 0.6), (0.6 * math.cos(ang), 0.6 * math.sin(ang), 3.6 + k * 0.6), 0.05, M['tronco_blanco'], modelos))
    for k in range(10):
        ang, h = rng.uniform(0, 6.3), rng.uniform(3.0, 5.6)
        rr = 0.8 * (1 - (h - 3.0) / 3.5) + 0.2
        copa(partes, rng, (rr * math.cos(ang), rr * math.sin(ang), h), rng.uniform(0.35, 0.5), hojas[k % len(hojas)])
    return unir(nombre, partes, modelos, colores=PLANTA)

def alamos(nombre, semilla):
    """Grupo de álamos: tres troncos blancos delgados con bolas amarillas (como "Aspen Cluster")."""
    rng, partes = random.Random(semilla), []
    for k, (x, y, h) in enumerate(((0, 0, 3.6), (0.5, 0.3, 2.9), (-0.3, 0.45, 2.5))):
        partes.append(cyl('t', (x, y, h / 2), 0.08, h, 'Z', M['tronco_blanco'], modelos, segs=5, r2=0.05))
        for j in range(3):
            copa(partes, rng, (x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), h - 0.3 + j * 0.35), 0.48 - j * 0.07,
                 ['hoja_amarilla', 'hoja_lima', 'hoja_dorada'][(j + k) % 3])
    return unir(nombre, partes, modelos, colores=PLANTA)

def florido(nombre, semilla):
    """Árbol con flores rosadas: tronco oscuro torcido y copa rosada (el acento de la imagen del camino)."""
    rng, partes = random.Random(semilla), []
    partes.append(beam('t', (0, 0, 0), (0.3, 0.1, 1.8), 0.24, M['tronco_oscuro'], modelos))
    partes.append(beam('t', (0.3, 0.1, 1.8), (0.1, -0.1, 2.6), 0.18, M['tronco_oscuro'], modelos))
    partes.append(beam('r', (0.25, 0.08, 1.7), (-0.6, 0.3, 2.5), 0.12, M['tronco_oscuro'], modelos))
    for j, (dx, dy, dz, r) in enumerate(((0.1, 0, 3.1, 1.0), (0.8, 0.3, 2.8, 0.75), (-0.7, 0.3, 2.8, 0.8),
                                         (0.2, -0.7, 2.7, 0.7), (0, 0.6, 3.6, 0.7), (-0.3, -0.3, 3.7, 0.65))):
        copa(partes, rng, (dx, dy, dz), r, 'hoja_rosa')
    return unir(nombre, partes, modelos, colores=PLANTA)

def arbusto(nombre, hoja, adorno, n_adornos, semilla):
    """Arbusto de bolas, con bayas rojas o florecitas amarillas encima (como "Berry Bush" y "Gorse")."""
    rng, partes = random.Random(semilla), []
    bolas = ((0, 0, 0.5, 0.55), (0.45, 0.15, 0.4, 0.42), (-0.42, -0.1, 0.42, 0.45), (0.05, -0.4, 0.38, 0.4))
    for dx, dy, dz, r in bolas:
        copa(partes, rng, (dx, dy, dz), r, hoja, sz=0.85)
    for k in range(n_adornos):
        dx, dy, dz, r = bolas[k % len(bolas)]
        p = punto_en(rng, (dx, dy, dz), r * 0.95, arriba=-0.2)
        partes.append(box('a', p.x - 0.055, p.x + 0.055, p.y - 0.055, p.y + 0.055, p.z - 0.055, p.z + 0.055, M[adorno], modelos))  # cajita: 12 triángulos
    return unir(nombre, partes, modelos, colores=PLANTA)

def helechos(nombre, semilla):
    """Mata de helechos: hojas largas que salen del centro y se doblan (como "Ground Ferns")."""
    rng, partes = random.Random(semilla), []
    for k in range(8):
        ang = k * 0.785 + rng.uniform(-0.2, 0.2)
        largo = rng.uniform(0.7, 1.0)
        medio = (largo * 0.5 * math.cos(ang), largo * 0.5 * math.sin(ang), 0.55)
        hoja_plana(partes, (0, 0, 0.05), medio, 0.32, 'hoja_helecho')
        hoja_plana(partes, medio, (largo * math.cos(ang), largo * math.sin(ang), 0.3), 0.26, 'hoja_helecho')
    return unir(nombre, partes, modelos, colores=PLANTA)

def cardos(nombre, semilla):
    """Cardos: tallos con cabezas moradas (como "Thistle Cluster")."""
    rng, partes = random.Random(semilla), []
    for k in range(4):
        x, y, h = rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0.55, 0.9)
        partes.append(beam('s', (x, y, 0), (x, y, h), 0.035, M['tallo'], modelos))
        hoja_plana(partes, (x, y, 0.15), (x + 0.25, y, 0.3), 0.12, 'tallo')
        partes.append(ico('c', (x, y, h + 0.04), 0.09, M['cardo'], modelos, sub=1))
    return unir(nombre, partes, modelos, colores=PLANTA)

def hongos(nombre, sombrero, semilla):
    """Grupito de hongos con sombrero (rojos con puntos blancos, o cafés)."""
    rng, partes = random.Random(semilla), []
    for k in range(4):
        x, y = rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3)
        h, r = rng.uniform(0.12, 0.3), rng.uniform(0.09, 0.17)
        partes.append(cyl('p', (x, y, h / 2), r * 0.35, h, 'Z', M['hongo_pie'], modelos, segs=6))
        partes.append(cyl('s', (x, y, h + r * 0.3), r, r * 0.7, 'Z', M[sombrero], modelos, segs=8, r2=r * 0.25))
        if sombrero == 'hongo_rojo':
            for j in range(3):
                ang = rng.uniform(0, 6.3)
                partes.append(ico('d', (x + r * 0.55 * math.cos(ang), y + r * 0.55 * math.sin(ang), h + r * 0.45), r * 0.15, M['flor_blanca'], modelos))
    return unir(nombre, partes, modelos, colores=PLANTA)

def roca(nombre, semilla, aplastada=0.6):
    """Roca gris con musgo arriba."""
    rng, partes = random.Random(semilla), []
    o = ico('r', (0, 0, 0.3), 0.6, M['roca'], modelos, sub=1, sz=aplastada)
    partes.append(abollar(o, rng, 0.12))
    o = ico('m', (0.05, 0.05, 0.3 + 0.6 * aplastada * 0.75), 0.42, M['musgo'], modelos, sub=1, sz=0.3)
    partes.append(abollar(o, rng, 0.05))
    return unir(nombre, partes, modelos, colores=PLANTA)

def flores(nombre, colores, semilla):
    """Mata de flores silvestres: tallitos con florecitas de colores y hojas abajo."""
    rng, partes = random.Random(semilla), []
    copa(partes, rng, (0, 0, 0.05), 0.28, 'hoja_pasto', sz=0.45)
    for k in range(6):
        x, y, h = rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), rng.uniform(0.25, 0.45)
        hoja_plana(partes, (x, y, 0), (x, y, h), 0.04, 'tallo', grosor=0.01)
        partes.append(ico('f', (x, y, h + 0.03), 0.075, M[colores[k % len(colores)]], modelos, sub=1, sz=0.7))
    return unir(nombre, partes, modelos, colores=PLANTA)

def pasto(nombre, semilla):
    """Mata de pasto alto."""
    rng, partes = random.Random(semilla), []
    for k in range(9):
        ang, incl = rng.uniform(0, 6.3), rng.uniform(0.1, 0.35)
        h = rng.uniform(0.45, 0.8)
        hoja_plana(partes, (0, 0, 0), (incl * math.cos(ang), incl * math.sin(ang), h), 0.08,
                   'hoja_pasto' if k % 3 else 'hoja_lima', grosor=0.01)
    return unir(nombre, partes, modelos, colores=PLANTA)

def tronco_caido(nombre):
    """Tronco caído con los cortes claros y un poco de musgo."""
    partes = [cyl('t', (0, 0, 0.32), 0.32, 3.0, 'X', M['tronco'], modelos, segs=7)]
    for x in (-1.51, 1.51):
        partes.append(cyl('c', (x, 0, 0.32), 0.27, 0.03, 'X', M['madera_clara'], modelos, segs=7))
    partes.append(ico('m', (0.3, 0, 0.6), 0.45, M['musgo'], modelos, sub=1, sz=0.25))
    partes.append(beam('r', (-0.6, 0, 0.5), (-0.9, 0.3, 1.0), 0.07, M['tronco'], modelos))
    return unir(nombre, partes, modelos, colores=PLANTA)

def tocon(nombre):
    """Tocón: lo que queda de un árbol cortado."""
    partes = [cyl('t', (0, 0, 0.25), 0.42, 0.5, 'Z', M['tronco'], modelos, segs=8, r2=0.36),
              cyl('c', (0, 0, 0.51), 0.33, 0.02, 'Z', M['madera_clara'], modelos, segs=8)]
    for k in range(4):
        ang = k * 1.57 + 0.4
        partes.append(beam('r', (0, 0, 0.12), (0.7 * math.cos(ang), 0.7 * math.sin(ang), 0.0), 0.12, M['tronco'], modelos))
    return unir(nombre, partes, modelos, colores=PLANTA)

# Cada modelo: (cómo se llama, el objeto, tamaño mínimo y máximo de sus copias)
VERDES = ['hoja_verde', 'hoja_lima', 'hoja_esmeralda']
MODELOS = {
    'roble_verde':   (roble('roble_verde', VERDES, 1), 0.85, 1.25),
    'roble_dorado':  (roble('roble_dorado', ['hoja_oliva', 'hoja_dorada', 'hoja_verde'], 2), 0.85, 1.2),
    'arce_lima':     (arce('arce_lima', ['hoja_lima', 'hoja_verde'], 3), 0.9, 1.3),
    'arce_amarillo': (arce('arce_amarillo', ['hoja_amarilla', 'hoja_oliva', 'hoja_lima'], 4), 0.9, 1.3),
    'sicomoro':      (sicomoro('sicomoro', ['hoja_esmeralda', 'hoja_verde', 'hoja_naranja'], 5), 0.9, 1.2),
    'paraguas':      (paraguas('paraguas', ['hoja_verde', 'hoja_esmeralda'], 6), 0.9, 1.15),
    'otono':         (roble('otono', ['hoja_naranja', 'hoja_rojiza', 'hoja_dorada'], 7), 0.75, 1.0),
    'florido':       (florido('florido', 8), 0.9, 1.2),
    'abeto':         (abeto('abeto', 6, 7.0, 1.7, 'hoja_pino'), 0.85, 1.3),
    'abeto_verde':   (abeto('abeto_verde', 5, 5.5, 1.5, 'hoja_pino_verde'), 0.85, 1.25),
    'abeto_chico':   (abeto('abeto_chico', 3, 2.8, 1.0, 'hoja_pino_verde'), 0.8, 1.2),
    'pino_alto':     (pino_alto('pino_alto', 9), 0.9, 1.25),
    'abedul':        (abedul('abedul', ['hoja_lima', 'hoja_amarilla'], 10), 0.9, 1.2),
    'alamos':        (alamos('alamos', 11), 0.9, 1.3),
    'arbusto_bayas': (arbusto('arbusto_bayas', 'hoja_arbusto', 'baya', 14, 12), 0.8, 1.3),
    'arbusto_flores': (arbusto('arbusto_flores', 'hoja_esmeralda', 'flor_amarilla', 16, 13), 0.8, 1.2),
    'helechos':      (helechos('helechos', 14), 0.8, 1.3),
    'cardos':        (cardos('cardos', 15), 0.9, 1.2),
    'hongos_rojos':  (hongos('hongos_rojos', 'hongo_rojo', 16), 0.9, 1.4),
    'hongos_cafes':  (hongos('hongos_cafes', 'hongo_cafe', 17), 0.9, 1.4),
    'roca':          (roca('roca', 18), 0.6, 1.6),
    'roca_alta':     (roca('roca_alta', 19, aplastada=0.9), 0.6, 1.3),
    'flores_moradas': (flores('flores_moradas', ['flor_morada', 'flor_blanca', 'flor_morada'], 20), 0.9, 1.3),
    'flores_amarillas': (flores('flores_amarillas', ['flor_amarilla', 'flor_blanca'], 21), 0.9, 1.3),
    'flores_rosas':  (flores('flores_rosas', ['flor_rosa', 'flor_blanca', 'flor_amarilla'], 22), 0.9, 1.3),
    'pasto':         (pasto('pasto', 23), 0.8, 1.4),
    'tronco_caido':  (tronco_caido('tronco_caido'), 0.8, 1.2),
    'tocon':         (tocon('tocon'), 0.8, 1.2),
}

# =====================================================================
# EL CAMINO de tierra (puntos en medidas del juego: x, z)
# =====================================================================
# Termina entrando al patio pavimentado de atrás de la plaza (x 37–73, z 56–74): desde ahí se dobla al norte hacia el recuadro amarillo.
CAMINO = [(2, 21), (7, 23.4), (14, 23.6), (22, 23.8), (28, 24.8), (32.5, 28.8), (35, 36), (35.8, 46), (35.8, 54), (36.6, 61), (39.5, 65.5), (44, 67)]
ANCHO, BORDE = 2.6, 0.75   # mitad del ancho de la tierra, y la franja más oscura de cada lado

def curva(puntos, paso=1.0):
    """Curva suave que pasa por todos los puntos (Catmull-Rom), con un punto cada ~1 metro."""
    pts = [Vector((x, z)) for x, z in puntos]
    pts = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    salida = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        n = max(2, int((p2 - p1).length / paso))
        for k in range(n):
            t = k / n
            salida.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    salida.append(pts[-2])
    return salida

def franja(nombre, linea, a, b, m, alto=0.008):
    """Franja de suelo a lo largo de una curva, entre las distancias a y b del centro (negativas = a la izquierda)."""
    bm = bmesh.new()
    filas = []
    for i, p in enumerate(linea):
        d = (linea[min(i + 1, len(linea) - 1)] - linea[max(i - 1, 0)]).normalized()
        n = Vector((-d.y, d.x))
        filas.append([bm.verts.new((*P(*(p + n * s)), alto)) for s in (a, b)])
    for f0, f1 in zip(filas, filas[1:]):
        bm.faces.new((f0[0], f1[0], f1[1], f0[1]))
    return from_bm(nombre, bm, M[m], camino)

LINEAS = [curva(CAMINO)]
for k, linea in enumerate(LINEAS):
    franja('tierra_%d' % k, linea, -ANCHO, ANCHO, 'camino')
    franja('borde_izq_%d' % k, linea, -ANCHO - BORDE, -ANCHO, 'camino_borde', 0.006)
    franja('borde_der_%d' % k, linea, ANCHO, ANCHO + BORDE, 'camino_borde', 0.006)
PUNTOS_CAMINO = [p for linea in LINEAS for p in linea]

def lejos_del_camino(x, z):
    """Distancia (en metros) al centro del camino más cercano."""
    return min((Vector((x, z)) - p).length for p in PUNTOS_CAMINO)

# =====================================================================
# LA LAGUNA con juncos (como en el plano)
# =====================================================================
LAGUNA, LAGUNA_R = (18.0, 41.0), (6.0, 4.0)
lx, ly = P(*LAGUNA)
o = cyl('orilla', (0, 0, 0.004), 1.0, 0.008, 'Z', M['orilla'], laguna, segs=16)
o.data.transform(Matrix.Diagonal((LAGUNA_R[0] + 0.7, LAGUNA_R[1] + 0.7, 1, 1)) )
o.data.transform(Matrix.Translation((lx, ly, 0)))
o = cyl('agua', (0, 0, 0.02), 1.0, 0.01, 'Z', M['agua'], laguna, segs=16)
o.data.transform(Matrix.Diagonal((LAGUNA_R[0], LAGUNA_R[1], 1, 1)))
o.data.transform(Matrix.Translation((lx, ly, 0)))
rng_l = random.Random(SEMILLA + 100)
for k in range(14):
    ang = rng_l.uniform(0, 6.3)
    x, y = lx + (LAGUNA_R[0] + 0.2) * math.cos(ang), ly + (LAGUNA_R[1] + 0.2) * math.sin(ang)
    for j in range(3):
        jx, jy, h = x + rng_l.uniform(-0.3, 0.3), y + rng_l.uniform(-0.3, 0.3), rng_l.uniform(0.9, 1.5)
        beam('junco_%d_%d' % (k, j), (jx, jy, 0), (jx, jy, h), 0.04, M['junco'], laguna)
        if j == 0:
            cyl('punta_%d' % k, (jx, jy, h - 0.1), 0.05, 0.25, 'Z', M['junco_punta'], laguna, segs=5)

# =====================================================================
# DÓNDE VA CADA COSA (medidas del juego: x, z)
# =====================================================================
ZONAS_BOSQUE = [(-62, 45, 14, 116), (18, 104, -10, 34), (42, 104, 88, 116), (-62, -16, -30, 14)]
SIN_ARBOLES = [(-16, 18, -16, 20),    # la casa y su jardín
               (45, 100, 34, 88),     # la plaza, los edificios, la fila de clientes y la calle
               (20, 45, 71, 86),      # al lado de la calle
               (36, 74, 55, 75),      # el patio pavimentado (pave2), donde el camino llega
               (76, 104, 24, 88)]     # pegado a los edificios
CLARO, CLARO_R = (24.0, 61.0), 5.5    # claro del bosque con hongos y rocas

def dentro(x, z, zonas):
    return any(x0 <= x <= x1 and z0 <= z <= z1 for x0, x1, z0, z1 in zonas)

def en_laguna(x, z, margen):
    return ((x - LAGUNA[0]) / (LAGUNA_R[0] + margen)) ** 2 + ((z - LAGUNA[1]) / (LAGUNA_R[1] + margen)) ** 2 < 1

rng = random.Random(SEMILLA)
cuantas = {}
def poner(tipo, x, z, giro=None):
    """Pone una copia del modelo 'tipo' en (x, z), con tamaño y giro al azar."""
    proto, s0, s1 = MODELOS[tipo]
    n = cuantas.get(tipo, 0)
    cuantas[tipo] = n + 1
    o = proto if n == 0 else link(proto.copy())   # .copy() comparte la forma: el .glb la guarda una sola vez
    o.name = '%s_%03d' % (tipo, n)
    o.parent = plantas
    o.location = (*P(x, z), 0)
    o.rotation_euler = (0, 0, rng.uniform(0, 6.283) if giro is None else giro)
    s = rng.uniform(s0, s1)
    o.scale = (s, s, s)

def elegir(opciones):
    total = sum(p for _, p in opciones)
    r = rng.uniform(0, total)
    for tipo, p in opciones:
        r -= p
        if r <= 0:
            return tipo
    return opciones[-1][0]

# Cerca del camino: más color (flores rosadas, otoño, abedules). Lejos: más pinos y robles.
CERCA = [('roble_verde', 3), ('arce_lima', 3), ('arce_amarillo', 1.5), ('sicomoro', 2), ('florido', 2.4), ('otono', 1.6),
         ('abedul', 1.5), ('alamos', 1), ('abeto', 1.5), ('abeto_verde', 1.2), ('paraguas', 1.2), ('abeto_chico', 1)]
LEJOS = [('roble_verde', 2.5), ('roble_dorado', 2), ('abeto', 3), ('abeto_verde', 2.5), ('pino_alto', 2), ('sicomoro', 1.5),
         ('arce_lima', 1.2), ('arce_amarillo', 1), ('abedul', 1), ('alamos', 0.8), ('paraguas', 1), ('abeto_chico', 1),
         ('otono', 0.5), ('florido', 0.3)]
ABAJO = [('arbusto_bayas', 2), ('arbusto_flores', 1.5), ('helechos', 3), ('pasto', 3), ('flores_moradas', 1),
         ('flores_amarillas', 1), ('flores_rosas', 0.8), ('roca', 1), ('roca_alta', 0.5), ('hongos_cafes', 0.8),
         ('cardos', 0.8), ('tocon', 0.3), ('tronco_caido', 0.3)]
ORILLA = [('flores_moradas', 2), ('flores_amarillas', 2), ('flores_rosas', 1.5), ('hongos_rojos', 1.5), ('hongos_cafes', 1),
          ('roca', 1.2), ('arbusto_bayas', 1.5), ('arbusto_flores', 1.2), ('helechos', 1.5), ('pasto', 1.5), ('cardos', 0.8)]

# 1) Árboles: una cuadrícula con cada punto movido al azar (así no quedan en fila)
PASO = 4.4
z = -30.0
while z < 116:
    x = -62.0
    while x < 104:
        px, pz = x + rng.uniform(-1.6, 1.6), z + rng.uniform(-1.6, 1.6)
        x += PASO
        if not dentro(px, pz, ZONAS_BOSQUE) or dentro(px, pz, SIN_ARBOLES) or en_laguna(px, pz, 2.5):
            continue
        if (Vector((px, pz)) - Vector(CLARO)).length < CLARO_R + 1.5:
            continue
        d = lejos_del_camino(px, pz)
        if d < 6.8:
            continue
        cerca_de_algo = Vector((px, pz)).length < 34 or (px > 36 and pz > 20)   # se abre cerca de la casa y la plaza
        borde = px < -40 or pz > 98   # más allá de donde llega el truck: solo para que el bosque no se corte de golpe
        if rng.random() < (0.45 if cerca_de_algo else 0.3 if borde else 0.07):
            continue
        poner(elegir(CERCA if d < 16 else LEJOS), px, pz)
    z += PASO

# 2) Plantas bajas por todo el bosque
z = -30.0
while z < 116:
    x = -62.0
    while x < 104:
        px, pz = x + rng.uniform(-1.3, 1.3), z + rng.uniform(-1.3, 1.3)
        x += 3.4
        if not dentro(px, pz, ZONAS_BOSQUE) or dentro(px, pz, SIN_ARBOLES) or en_laguna(px, pz, 0.8):
            continue
        if lejos_del_camino(px, pz) < ANCHO + BORDE + 0.6 or rng.random() < (0.85 if px < -40 or pz > 98 else 0.5):
            continue
        poner(elegir(ABAJO), px, pz)
    z += 3.4

# 3) Las orillas del camino, llenas de flores, hongos y rocas (como la imagen del camino)
rng_o = random.Random(SEMILLA + 1)
for linea in LINEAS:
    for i in range(len(linea)):
        p = linea[i]
        d = (linea[min(i + 1, len(linea) - 1)] - linea[max(i - 1, 0)]).normalized()
        n = Vector((-d.y, d.x))
        for lado in (-1, 1):
            if rng_o.random() < 0.2:
                continue
            q = p + n * lado * rng_o.uniform(ANCHO + BORDE + 0.5, ANCHO + BORDE + 2.6) + d * rng_o.uniform(-0.6, 0.6)
            if dentro(q.x, q.y, SIN_ARBOLES[1:]):   # nada en la plaza, la calle ni el patio pavimentado
                continue
            if lejos_del_camino(q.x, q.y) < ANCHO + BORDE + 0.4:
                continue
            poner(elegir(ORILLA), q.x, q.y)

# 4) El claro: un círculo de hongos rojos, rocas y un tocón (como en el plano)
cx, cz = CLARO
for k in range(9):
    ang = k * 0.7 + rng.uniform(-0.2, 0.2)
    r = rng.uniform(1.5, 3.5)
    poner('hongos_rojos' if k % 3 else 'hongos_cafes', cx + r * math.cos(ang), cz + r * math.sin(ang))
for dx, dz, tipo in ((3.8, 1.0, 'roca_alta'), (4.2, -0.6, 'roca'), (-3.6, 2.4, 'roca'), (0.4, -4.0, 'tocon'), (-2.5, -3.2, 'tronco_caido')):
    poner(tipo, cx + dx, cz + dz)
for k in range(6):   # flores alrededor de la laguna
    ang = k * 1.05 + 0.3
    poner(['flores_moradas', 'flores_amarillas', 'flores_rosas'][k % 3],
          LAGUNA[0] + (LAGUNA_R[0] + 1.6) * math.cos(ang), LAGUNA[1] + (LAGUNA_R[1] + 1.6) * math.sin(ang))

print('Copias por modelo:', ', '.join('%s %d' % kv for kv in sorted(cuantas.items())))
sin_usar = [t for t in MODELOS if t not in cuantas]
assert not sin_usar, 'Modelos sin ninguna copia: %s' % sin_usar   # cada modelo debe aparecer al menos una vez

guardar(root, [camino, laguna], 'assets/models/environment/bosque.glb', 'bosque.blend', copias=[plantas])
