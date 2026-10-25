# -*- coding: utf-8 -*-
"""
Construye las MANOS DEL JUGADOR (estilo cozy low-poly, facetado), siguiendo
reference/turnarounds/player_hands.png y las manos del volante de reference/style-targets/driving_first_person.jpg:
piel clara, manga azul que termina en la muñeca, dedos con nudillos y uñitas.

Piezas que busca el juego (assets/models/characters/manos.glb):
  - mano_sostener: mano derecha con la palma hacia arriba (para cocinar y llevar cosas) y su antebrazo.
                   Va pegada a la cámara, en el mismo lugar que la mano del código (buildHand).
                   Lo que llevas se apoya sobre la palma (el "socket" del código: 0.01, 0.035, -0.06).
  - manos_volante: las DOS manos agarrando el volante, con sus antebrazos.
                   Están en las medidas del volante (cab_volante de build_truck_cab.py): centro del volante
                   en (0, 0, 0), el volante es el plano X-Z y el conductor está hacia -Y.
                   El código las pone DENTRO del volante, así giran con él cuando doblas.

Cada mano se arma con "cascos" (la forma más chica que envuelve unos puntos) = caras planas, como el dibujo.
Ejes de una mano "en reposo": los dedos apuntan a +Y, el dorso mira a +Z, el pulgar derecho va a -X.

Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
Desde la terminal: python3 build_manos.py   (con el módulo bpy instalado)
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
M = {   # colores tomados del dibujo de las manos
    'piel': mat('piel', 0xe9a877, 0.6),
    'una': mat('una', 0xf6cfae, 0.4),
    'manga': mat('manga_azul', 0x44659e, 0.85),
    'puno': mat('puno_azul', 0x37548a, 0.85),
}
TAM = 1.5   # las manos de dibujo animado son un poco grandes (el volante del truck también lo es)

root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # como el volante; el código le quita la escala a mano_sostener
sostener = empty('mano_sostener', root)
volante = empty('manos_volante', root)


# =====================================================================
# Herramientas de esta pieza
# =====================================================================
def casco(nombre, pts, m, padre):
    """Envuelve los puntos con la forma más chica posible: queda facetada, como el dibujo."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    r = bmesh.ops.convex_hull(bm, input=vs)
    sobra = [v for v in r['geom_interior'] + r['geom_unused'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.delete(bm, geom=sobra, context='VERTS')
    return from_bm(nombre, bm, m, padre)

def anillo(c, d, lado, r, aplasta=0.85, n=6, gira=0.0):
    """n puntos en círculo alrededor del eje d (lado = hacia el costado), aplastado en la otra dirección."""
    d = d.normalized()
    u = (lado - d * lado.dot(d)).normalized()
    w = d.cross(u)
    return [c + u * r * math.cos(gira + 2 * math.pi * k / n) + w * r * aplasta * math.sin(gira + 2 * math.pi * k / n) for k in range(n)]


# Dedos: (nombre, base x, base y, radio, largos de las 3 falanges)
DEDOS = [
    ('indice', -0.0255, 0.086, 0.0112, (0.036, 0.022, 0.019)),
    ('medio', -0.0085, 0.090, 0.0117, (0.040, 0.025, 0.020)),
    ('anular', 0.0090, 0.087, 0.0110, (0.037, 0.023, 0.019)),
    ('menique', 0.0255, 0.079, 0.0096, (0.029, 0.018, 0.016)),
]
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))

def mano_en_reposo(pose):
    """Devuelve las partes de una mano DERECHA en su posición de reposo, como listas de (nombre, puntos, material).
    pose = {'doblar': [(a1, a2, a3) por dedo, en grados], 'abrir': [grados por dedo], 'pulgar': [direcciones]}"""
    partes = []
    # Palma: muñeca, nudillos, el dorso un poquito abombado y el músculo del pulgar
    palma = anillo(Vector((0, 0.0, 0)), Y, X, 0.026, 0.55, 8)
    for x, y in ((-0.034, 0.082), (-0.012, 0.089), (0.009, 0.087), (0.032, 0.077)):
        palma += [Vector((x, y, 0.012)), Vector((x, y, -0.011))]
    palma += [Vector((0, 0.045, 0.017)), Vector((-0.015, 0.05, 0.016)), Vector((0.02, 0.04, 0.015)),
              Vector((-0.031, 0.028, -0.014)), Vector((0.03, 0.03, -0.01)), Vector((0, 0.05, -0.015))]
    partes.append(('palma', palma, M['piel']))
    partes.append(('muneca', anillo(Vector((0, 0.01, 0)), Y, X, 0.024, 0.62, 8) + anillo(Vector((0, -0.045, 0)), Y, X, 0.025, 0.65, 8), M['piel']))
    puntas = {}
    # Los cuatro dedos: cada falange es un casco entre dos anillos; se doblan hacia la palma (-Z)
    for i, (nombre, bx, by, r, largos) in enumerate(DEDOS):
        abrir = Matrix.Rotation(math.radians(-pose['abrir'][i]), 3, 'Z')
        p, giro_total = Vector((bx, by - 0.006, -0.001)), 0.0
        cadena = [p.copy()]
        for k, largo in enumerate(largos):
            giro_total += math.radians(pose['doblar'][i][k])
            d = abrir @ Matrix.Rotation(-giro_total, 3, 'X') @ Y
            lado = abrir @ X
            r0, r1 = r * (0.94 ** k), r * (0.94 ** (k + 1))
            inicio = p - d * r0 * 0.7          # se mete un poco en la falange anterior (sin huecos al doblar)
            fin = p + d * largo
            pts = anillo(inicio, d, lado, r0) + anillo(fin - d * r1 * 0.5, d, lado, r1 * 0.95)
            if k == 2:
                pts += [fin + d * r1 * 0.25]   # puntita redondeada
                arriba = d.cross(lado).normalized() * -1   # el lado del dorso
                if arriba.dot(Matrix.Rotation(-giro_total, 3, 'X') @ Z) < 0: arriba = -arriba
                # uñita: una laminita clara sobre el dorso de la última falange
                c = p + d * largo * 0.62 + arriba * r1 * 0.78
                partes.append((nombre + '_una', anillo(c - d * largo * 0.28, d, lado, r1 * 0.7, 0.18, 6)
                               + anillo(c + d * largo * 0.26, d, lado, r1 * 0.62, 0.18, 6), M['una']))
            partes.append(('%s_%d' % (nombre, k), pts, M['piel']))
            p = fin
            cadena.append(p.copy())
        puntas[nombre] = cadena
    # Pulgar: sale del costado de la palma hacia -X; sus direcciones vienen en la pose
    p = Vector((-0.024, 0.02, -0.008))
    for k, (largo, d) in enumerate(zip((0.034, 0.03, 0.025), pose['pulgar'])):
        d = Vector(d).normalized()
        r0, r1 = (0.0125, 0.0112, 0.0102, 0.0094)[k], (0.0125, 0.0112, 0.0102, 0.0094)[k + 1]
        lado = Z if abs(d.dot(Z)) < 0.9 else X
        inicio = p - d * r0 * 0.6
        fin = p + d * largo
        pts = anillo(inicio, d, lado, r0, 0.8) + anillo(fin - d * r1 * 0.5, d, lado, r1, 0.8)
        if k == 2:
            pts += [fin + d * r1 * 0.25]
            arriba = (d.cross(X) if abs(d.dot(X)) < 0.95 else Z).normalized()
            if arriba.dot(Vector((-0.5, 0, 1))) < 0: arriba = -arriba
            c = p + d * largo * 0.62 + arriba * r1 * 0.76
            partes.append(('pulgar_una', anillo(c - d * largo * 0.28, d, arriba.cross(d), r1 * 0.72, 0.18, 6)
                           + anillo(c + d * largo * 0.26, d, arriba.cross(d), r1 * 0.64, 0.18, 6), M['una']))
        partes.append(('pulgar_%d' % k, pts, M['piel']))
        p = fin
    return partes, puntas


def poner_mano(nombre, pose, T, padre, izquierda=False):
    """Arma la mano (derecha, o izquierda como espejo) y la mueve con la matriz T. Devuelve las puntas de los dedos."""
    partes, puntas = mano_en_reposo(pose)
    espejo = Matrix.Scale(-1, 4, X) if izquierda else Matrix.Identity(4)
    for n, pts, m in partes:
        casco('%s_%s' % (nombre, n), [T @ (espejo @ p) for p in pts], m, padre)
    return {k: [T @ (espejo @ p) for p in v] for k, v in puntas.items()}


def manga(nombre, muneca, codo, padre, arriba=Z):
    """Antebrazo con la manga azul: un poquito más ancha en la muñeca (como en el dibujo) y un puño más oscuro."""
    muneca, codo = Vector(muneca), Vector(codo)
    d = (codo - muneca).normalized()
    lado = (arriba.cross(d)).normalized()
    a = muneca + d * 0.022 * TAM
    casco(nombre + '_puno', anillo(a, d, lado, 0.035 * TAM, 0.82, 8, 0.2) + anillo(a + d * 0.018 * TAM, d, lado, 0.035 * TAM, 0.82, 8, 0.2), M['puno'], padre)
    casco(nombre + '_manga', anillo(a + d * 0.012 * TAM, d, lado, 0.033 * TAM, 0.8, 8, 0.2) + anillo(codo, d, lado, 0.042 * TAM, 0.8, 8, 0.2), M['manga'], padre)


def matriz(origen, eje_x, eje_y, eje_z, tam=TAM):
    """Matriz que lleva la mano en reposo a su lugar: sus ejes X, Y, Z van a eje_x, eje_y, eje_z."""
    R = Matrix((eje_x, eje_y, eje_z)).transposed().to_4x4()
    return Matrix.Translation(origen) @ R @ Matrix.Scale(tam, 4)


# =====================================================================
# 1) MANO PARA COCINAR: palma hacia arriba, dedos un poquito doblados (como el dibujo de "sostener")
# =====================================================================
POSE_SOSTENER = {
    'doblar': [(24, 26, 16), (20, 24, 14), (24, 26, 16), (30, 30, 18)],
    'abrir': [-4, -1, 2, 6],
    'pulgar': [(-0.65, 0.65, -0.35), (-0.4, 0.88, -0.2), (-0.22, 0.95, -0.15)],
}
# Palma arriba = mano girada media vuelta sobre los dedos (el pulgar queda a la derecha, +X)
# El centro de la palma queda justo debajo del "socket" del código (Blender 0.01, 0.06, 0.035)
T = matriz(Vector((0, 0, 0)), -X, Y, -Z)
centro_palma = T @ Vector((0, 0.05, -0.014))
T = Matrix.Translation(Vector((0.01, 0.06, 0.02)) - centro_palma) @ T
poner_mano('sostener', POSE_SOSTENER, T, sostener)
muneca = T @ Vector((0, -0.03, 0))
manga('sostener', muneca, muneca + Vector((0.03, -0.34, -0.09)), sostener)


# =====================================================================
# 2) MANOS EN EL VOLANTE: puño cerrado alrededor del aro, a las "10 y 10"
# =====================================================================
R_VOLANTE = 0.3          # radio del aro (igual que build_truck_cab.py)
ANG_DER, ANG_IZQ = 56, 124   # dónde agarra cada mano (grados, 0 = a la derecha, 90 = arriba): así se ven desde el asiento
TAM_VOLANTE = 1.75           # un poco más grandes: el volante del truck es grandote
POSE_VOLANTE = {
    'doblar': [(62, 88, 55), (66, 90, 55), (70, 90, 52), (74, 88, 50)],
    'abrir': [-3, 0, 2, 5],
    'pulgar': [(-0.7, 0.55, -0.45), (-0.3, 0.8, -0.55), (0.15, 0.75, -0.6)],
}
_, cadena = mano_en_reposo(POSE_VOLANTE)
# Centro del "túnel" que forman los dedos doblados (ahí pasa el aro del volante)
pts_medio = cadena['medio'] + cadena['anular']
agarre = sum(pts_medio, Vector()) / len(pts_medio)
agarre.x = 0.0
DORSO_AFUERA, DORSO_ATRAS = 1.0, 0.35   # el dorso mira hacia afuera del aro (y un poco al conductor): los dedos lo envuelven
CODOS = {'der': Vector((0.36, -0.46, -0.16)), 'izq': Vector((-0.36, -0.46, -0.16))}

for lado, ang in (('der', ANG_DER), ('izq', ANG_IZQ)):
    a = math.radians(ang)
    afuera = Vector((math.cos(a), 0, math.sin(a)))
    tangente = Vector((-math.sin(a), 0, math.cos(a)))   # a lo largo del aro, contra el reloj
    P = afuera * R_VOLANTE                               # punto del aro donde agarra
    ez = (afuera * DORSO_AFUERA + Vector((0, -1, 0)) * DORSO_ATRAS).normalized()   # dorso
    ex = -tangente                                       # nudillos a lo largo del aro, pulgar hacia arriba
    ex = (ex - ez * ex.dot(ez)).normalized()
    ey = ez.cross(ex)                                     # hacia donde apuntarían los dedos estirados
    # (la izquierda es el espejo de la derecha: su pulgar ya está en +X, así que la misma cuenta la deja arriba)
    T = matriz(Vector((0, 0, 0)), ex, ey, ez, TAM_VOLANTE)
    T = Matrix.Translation(P - T @ agarre) @ T
    poner_mano('volante_' + lado, POSE_VOLANTE, T, volante, izquierda=(lado == 'izq'))
    muneca = T @ Vector((0, -0.03, 0))
    manga('volante_' + lado, muneca, CODOS[lado], volante, arriba=ez)

guardar(root, [sostener, volante], 'assets/models/characters/manos.glb', 'manos.blend')
