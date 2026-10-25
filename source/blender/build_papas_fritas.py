# -*- coding: utf-8 -*-
"""
Construye las PAPAS FRITAS y la CAJA ROJA de papas (estilo cozy low-poly).
Antes eran palitos dibujados con código que parecían fideos; ahora son papas gorditas,
con bordes suaves, puntitas más tostadas y tres tonos de dorado (no todas salen iguales).

Piezas que busca el juego (assets/models/props/papas_fritas.glb):
  - caja_papas:    la caja roja vacía (más ancha arriba, con el frente curvo, franja y dibujito amarillos)
  - papas_caja:    las papas paradas que se asoman por arriba de la caja (van con la caja)
  - papas_sueltas: un montoncito de papas para llevar en la mano (recién sacadas de la freidora)
  - papas_canasta: papas acostadas que llenan la canasta de la freidora. El código las pinta
                   de pálido a dorado mientras se fríen (busca los materiales "papa_frita...")

Medidas: las MISMAS del código del juego (hacerCajaPapas / hacerPalitos), así el modelo
reemplaza a lo dibujado sin mover nada. Por eso aquí la escala es (1, 1, 1).
Ejes: X = X del juego, Y = -z del juego, Z = arriba. El origen es el centro de abajo de cada pieza.

Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
Desde la terminal: python3 build_papas_fritas.py   (con el módulo bpy instalado)
"""
# ---------- Herramientas compartidas (NO las copies aquí: viven en lib_blender.py) ----------
import bpy, os, sys
try:  # corriendo desde el editor de texto de Blender
    sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
except AttributeError:  # corriendo desde la terminal
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, lib_blender; importlib.reload(lib_blender)
from lib_blender import *

azar = random.Random(11)   # siempre el mismo "azar", para que salga igual cada vez

limpiar()
M = {
    # Tres dorados distintos + puntitas tostadas (el código busca los que empiezan con "papa_frita")
    'papa': mat('papa_frita', 0xf2b440, 0.45),
    'clara': mat('papa_frita_clara', 0xf7cb62, 0.45),
    'dorada': mat('papa_frita_dorada', 0xe0962a, 0.45),
    'punta': mat('papa_frita_punta', 0xb8701f, 0.55),
    'sal': mat('sal', 0xfff8e6, 0.3),
    'roja': mat('caja_roja', 0xd62828, 0.5),
    'adentro': mat('caja_adentro', 0xa81c1c, 0.6),
    'amarilla': mat('caja_amarilla', 0xffd166, 0.45),
}
TONOS = [M['papa'], M['papa'], M['clara'], M['dorada']]   # la mayoría dorado normal

root = empty('escala_juego')   # escala (1, 1, 1): medidas del código del juego
caja = empty('caja_papas', root)
papas_caja = empty('papas_caja', root)
sueltas = empty('papas_sueltas', root)
canasta = empty('papas_canasta', root)


# =====================================================================
# Una papa: palito con bordes biselados (brillan suave) y puntitas más tostadas
# =====================================================================
G = 0.0115   # grosor de cada papa
cuantas = [0]
def papa(p0, p1, padre, grosor=G, sal=False):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    largo = d.length
    cuantas[0] += 1
    n = 'papa_%d' % cuantas[0]
    giro = azar.uniform(0, math.pi / 2)   # cada papa girada distinto sobre sí misma
    R = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4() @ Matrix.Rotation(giro, 4, 'Z')
    ancho = grosor * azar.uniform(0.9, 1.1)
    punta = min(0.0045, largo * 0.06)
    def palito(nombre, z0, z1, w, m, bisel):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.scale(bm, vec=(w, w * azar.uniform(0.85, 1.0), z1 - z0), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0, 0, (z0 + z1) / 2), verts=bm.verts)
        if bisel:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bisel, segments=1, affect='EDGES', clamp_overlap=True)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(p0) @ R, verts=bm.verts)
        return from_bm(nombre, bm, m, padre)
    palito(n, punta, largo - punta, ancho, azar.choice(TONOS), ancho * 0.2)
    # puntitas tostadas: un poquito más delgadas y metidas en la papa (si sobresalen parecen lápices)
    palito(n + '_punta_a', 0.0005, punta + 0.001, ancho * 0.96, M['punta'], ancho * 0.2)
    palito(n + '_punta_b', largo - punta - 0.001, largo - 0.0005, ancho * 0.96, M['punta'], ancho * 0.2)
    dn = d.normalized()
    arriba = Vector((0, 0, 1)) - dn * dn.z   # "arriba" de la papa (sirve si no está parada)
    if sal and arriba.length > 0.3:   # granitos de sal arriba de la papa
        arriba.normalize()
        for k in range(2):
            t = azar.uniform(0.25, 0.8)
            c = p0 + d * t + arriba * ancho * 0.55
            box(n + '_sal%d' % k, c.x - 0.0015, c.x + 0.0015, c.y - 0.0015, c.y + 0.0015, c.z - 0.0012, c.z + 0.0012, M['sal'], padre)


def papa_acostada(centro, angulo, largo, padre, inclina=0.0, sal=False):
    """Papa acostada (casi horizontal), centrada en 'centro', girada 'angulo' alrededor de Z."""
    d = Vector((math.cos(angulo), math.sin(angulo), inclina)).normalized() * largo / 2
    c = Vector(centro)
    papa(c - d, c + d, padre, sal=sal)


# =====================================================================
# 1) CAJA ROJA: más ancha arriba, el frente y la espalda suben en curva
# =====================================================================
ABAJO, ARRIBA = 0.04, 0.056          # mitad del lado abajo y arriba
H_LADO, H_PICO, E = 0.112, 0.13, 0.003   # alto de los lados, alto del pico del frente, grosor del cartón
COLS = 8                             # columnas de cada pared (para que la curva se vea suave)

def altura(s, curva):   # s va de -1 a 1 a lo largo de la pared
    return H_LADO + (H_PICO - H_LADO) * (1 - s * s) if curva else H_LADO

def punto(lado, s, z, adentro=0.0):
    """Punto en la pared 'lado' (0 frente +X, 1 izquierda +Y, 2 espalda -X, 3 derecha -Y) a la altura z."""
    medio = ABAJO + (ARRIBA - ABAJO) * (z / H_PICO) - adentro
    a = lado * math.pi / 2
    n = Vector((math.cos(a), math.sin(a), 0))       # hacia afuera
    t = Vector((-math.sin(a), math.cos(a), 0))      # a lo largo de la pared
    return n * medio + t * medio * s + Vector((0, 0, z))

bm = bmesh.new()
for lado in range(4):
    curva = lado in (0, 2)   # frente y espalda con curva
    fuera_ab, fuera_ar, dentro_ab, dentro_ar = [], [], [], []
    for i in range(COLS + 1):
        s = -1 + 2 * i / COLS
        h = altura(s, curva)
        fuera_ab.append(bm.verts.new(punto(lado, s, 0)))
        fuera_ar.append(bm.verts.new(punto(lado, s, h)))
        dentro_ab.append(bm.verts.new(punto(lado, s, 0.004, E)))
        dentro_ar.append(bm.verts.new(punto(lado, s, h, E)))
    for i in range(COLS):
        bm.faces.new((fuera_ab[i], fuera_ab[i + 1], fuera_ar[i + 1], fuera_ar[i]))
        bm.faces.new((dentro_ab[i + 1], dentro_ab[i], dentro_ar[i], dentro_ar[i + 1]))
        bm.faces.new((fuera_ar[i], fuera_ar[i + 1], dentro_ar[i + 1], dentro_ar[i]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
# Pared de afuera roja, de adentro más oscura: se separan por la dirección de la cara
me = bpy.data.meshes.new('caja_paredes')
bm.normal_update()
for f in bm.faces:
    c = f.calc_center_median()
    f.material_index = 0 if f.normal.dot(Vector((c.x, c.y, 0))) >= 0 or abs(f.normal.z) > 0.7 else 1
bm.to_mesh(me); bm.free()
me.materials.append(M['roja']); me.materials.append(M['adentro'])
paredes = link(bpy.data.objects.new('caja_paredes', me)); paredes.parent = caja
# El juego une las partes por material: separo las de adentro en su propio objeto
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == 0], context='FACES')
me2 = bpy.data.meshes.new('caja_adentro'); bm.to_mesh(me2); bm.free()
me2.materials.append(M['adentro'])
for p in me2.polygons: p.material_index = 0
o2 = link(bpy.data.objects.new('caja_adentro', me2)); o2.parent = caja
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == 1], context='FACES')
bm.to_mesh(me); bm.free()
while len(me.materials) > 1: me.materials.pop()
# Fondo
box('caja_fondo', -ABAJO, ABAJO, -ABAJO, ABAJO, 0, 0.004, M['roja'], caja)

# Franja amarilla alrededor (un poquito afuera de la pared) y dibujito de papas en frente y espalda
def calco(nombre, lado, pts):
    """Calcomanía plana sobre la pared: pts = [(s, z), ...] (s de -1 a 1 a lo largo, z en metros)."""
    bm = bmesh.new()
    afuera = [bm.verts.new(punto(lado, s, z, -0.0012)) for s, z in pts]
    pegado = [bm.verts.new(punto(lado, s, z, 0.0002)) for s, z in pts]
    bm.faces.new(afuera); bm.faces.new(list(reversed(pegado)))
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((afuera[i], afuera[j], pegado[j], pegado[i]))
    return from_bm(nombre, bm, M['amarilla'], caja)

for lado in range(4):
    calco('franja_%d' % lado, lado, [(-1.0, 0.03), (1.0, 0.03), (1.0, 0.042), (-1.0, 0.042)])
for lado in (0, 2):
    # tres papitas en abanico arriba de un vasito (dibujo simple, sin marcas de verdad)
    calco('dibujo_vaso_%d' % lado, lado, [(-0.2, 0.052), (0.2, 0.052), (0.3, 0.08), (-0.3, 0.08)])
    for k, (s, inc) in enumerate(((-0.18, -0.1), (-0.06, -0.03), (0.06, 0.03), (0.18, 0.1))):
        alto = 0.1 if k in (1, 2) else 0.094
        calco('dibujo_papa_%d_%d' % (lado, k), lado,
              [(s - 0.03, 0.081), (s + 0.03, 0.081), (s + 0.03 + inc, alto), (s - 0.03 + inc, alto)])

# =====================================================================
# 2) PAPAS EN LA CAJA: paradas, abriéndose en abanico hacia afuera
# =====================================================================
FILAS = 6
for i in range(FILAS):
    for j in range(FILAS):
        if (i in (0, FILAS - 1)) and (j in (0, FILAS - 1)) and azar.random() < 0.5:
            continue   # algunas esquinas vacías: así no parece una reja
        u = (-1 + 2 * (i + azar.uniform(0.2, 0.8)) / FILAS) * 0.82
        v = (-1 + 2 * (j + azar.uniform(0.2, 0.8)) / FILAS) * 0.82
        z0 = azar.uniform(0.03, 0.06)
        largo = azar.uniform(0.095, 0.125)
        base = Vector((u * (ABAJO + 0.006), v * (ABAJO + 0.006), z0))
        # se abren hacia afuera, más las de las orillas
        tope = Vector((u * 0.03 + azar.uniform(-0.008, 0.008), v * 0.03 + azar.uniform(-0.008, 0.008), 0))
        d = (Vector((0, 0, 1)) + tope / 0.1).normalized()
        papa(base, base + d * largo, papas_caja, grosor=0.0128)

# =====================================================================
# 3) PAPAS SUELTAS (en la mano): un montoncito en capas cruzadas
# =====================================================================
for capa, (z, n, r) in enumerate(((0.008, 7, 0.032), (0.021, 6, 0.026), (0.034, 4, 0.018), (0.046, 2, 0.01))):
    for k in range(n):
        a = azar.uniform(0, math.pi)
        c = (azar.uniform(-r, r), azar.uniform(-r, r), z + azar.uniform(-0.002, 0.003))
        papa_acostada(c, a, azar.uniform(0.07, 0.1), sueltas, inclina=azar.uniform(-0.12, 0.12), sal=capa >= 2)

# =====================================================================
# 4) PAPAS EN LA CANASTA DE LA FREIDORA: acostadas en capas, sin salirse de la canasta
# =====================================================================
LX, LY = 0.088, 0.098   # mitad del espacio de adentro de la canasta (X y Y)
for capa, (z, n) in enumerate(((0.008, 12), (0.021, 11), (0.034, 9), (0.046, 6))):
    for k in range(n):
        a = azar.uniform(0, math.pi)
        largo = azar.uniform(0.09, 0.15)
        dx, dy = abs(math.cos(a)) * largo / 2, abs(math.sin(a)) * largo / 2
        if dx > LX * 0.95 or dy > LY * 0.95:   # muy larga para ese ángulo: la acorto
            largo *= min(LX * 0.95 / max(dx, 1e-6), LY * 0.95 / max(dy, 1e-6))
            dx, dy = abs(math.cos(a)) * largo / 2, abs(math.sin(a)) * largo / 2
        c = (azar.uniform(-(LX - dx), LX - dx), azar.uniform(-(LY - dy), LY - dy), z + azar.uniform(-0.002, 0.003))
        papa_acostada(c, a, largo, canasta, inclina=azar.uniform(-0.1, 0.1))

guardar(root, [caja, papas_caja, sueltas, canasta], 'assets/models/props/papas_fritas.glb', 'papas_fritas.blend')
