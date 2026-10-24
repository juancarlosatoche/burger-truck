# -*- coding: utf-8 -*-
"""
Construye la FREIDORA y las PAPAS CRUDAS (estilo cozy low-poly), siguiendo las imágenes de Ignacio:
reference/props/freidora_frente.jpg, freidora_friendo.jpg, freidora_canasta_arriba.jpg, freidora_canasta.jpg
y reference/props/papas_crudas.jpg.

Archivos que crea:
  - assets/models/props/freidora.glb, con 3 piezas que busca el juego:
      freidora_cuerpo  → la caja de acero, perillas rojas y el foquito naranja ("luz_piloto")
      freidora_aceite  → el aceite dorado (el código lo hace transparente y brillante)
      freidora_canasta → la canasta de alambre con mango negro (el código la BAJA al aceite y la SUBE)
  - assets/models/props/papas_crudas.glb, con la pieza "papas_crudas": bandeja de acero con papas crudas.

Medidas en metros del juego. Ejes: +X = hacia el pasillo (donde está el jugador), Y = -z del juego, Z = arriba.
El origen (0, 0, 0) es el centro de abajo: así se apoya sobre el mostrador o el estante.

Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
"""
# ---------- Herramientas compartidas (NO las copies aquí: viven en lib_blender.py) ----------
import bpy, os, sys
try:  # corriendo desde el editor de texto de Blender
    sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
except AttributeError:  # corriendo desde la terminal
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, lib_blender; importlib.reload(lib_blender)
from lib_blender import *


azar = random.Random(7)   # siempre el mismo "azar", para que salga igual cada vez

# =====================================================================
# 1) FREIDORA
# =====================================================================
limpiar()
M = {
    'acero': mat('acero_freidora', 0xc4cacf, 0.32, 0.8),
    'cromo': mat('cromo', 0xdfe4e8, 0.18, 0.9),
    'pozo': mat('pozo_oscuro', 0x2a2522, 0.6, 0.3),
    'aceite': mat('aceite', 0xd99a1e, 0.05, 0.2, emit=0x7a4200, strength=0.5),
    'alambre': mat('alambre', 0xd0d5da, 0.25, 0.9),
    'mango': mat('mango_negro', 0x1c1c20, 0.5),
    'perilla': mat('perilla_roja', 0xc1121f, 0.35),
    'panel': mat('panel', 0xb3babf, 0.4, 0.7),
    # "luz_": el foquito de encendido brilla (más de noche)
    'luz': mat('luz_piloto', 0xffb347, 0.3, 0, emit=0xff8a1e, strength=2.0),
}
root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # metros del juego → unidades de adentro del truck (como la cocina de Blender)
cuerpo = empty('freidora_cuerpo', root)
aceite = empty('freidora_aceite', root)
canasta = empty('freidora_canasta', root)

X, Y = 0.36, 0.38           # mitad del ancho (hacia el pasillo) y mitad del largo
Z0, Z1, T = 0.04, 0.34, 0.05  # abajo, arriba, grosor de las paredes
# Patitas
for sx in (-1, 1):
    for sy in (-1, 1):
        box('pata_%d_%d' % (sx, sy), sx * (X - 0.05) - 0.025, sx * (X - 0.05) + 0.025, sy * (Y - 0.05) - 0.025, sy * (Y - 0.05) + 0.025, 0, Z0, M['mango'], cuerpo)
# Caja de acero con un pozo para el aceite
box('base', -X, X, -Y, Y, Z0, 0.2, M['acero'], cuerpo, bevel=0.01)
box('pared_frente', X - T, X, -Y, Y, 0.2, Z1, M['acero'], cuerpo, bevel=0.008)
box('pared_atras', -X, -X + T, -Y, Y, 0.2, Z1, M['acero'], cuerpo, bevel=0.008)
box('pared_izq', -X + T, X - T, -Y, -Y + T, 0.2, Z1, M['acero'], cuerpo, bevel=0.008)
box('pared_der', -X + T, X - T, Y - T, Y, 0.2, Z1, M['acero'], cuerpo, bevel=0.008)
box('pozo', -X + T, X - T, -Y + T, Y - T, 0.2, 0.205, M['pozo'], cuerpo)
# Borde brillante arriba
for nombre, a in (('borde_frente', (X - T - 0.01, X + 0.01, -Y - 0.01, Y + 0.01)), ('borde_atras', (-X - 0.01, -X + T + 0.01, -Y - 0.01, Y + 0.01)),
                  ('borde_izq', (-X, X, -Y - 0.01, -Y + T + 0.01)), ('borde_der', (-X, X, Y - T - 0.01, Y + 0.01))):
    box(nombre, *a, Z1, Z1 + 0.018, M['cromo'], cuerpo, bevel=0.005)
# Salpicadero atrás (del lado de la pared)
box('salpicadero', -X - 0.01, -X + 0.03, -Y, Y, Z1, Z1 + 0.16, M['acero'], cuerpo, bevel=0.01)
# Panel de controles al frente: dos perillas rojas y el foquito naranja
box('panel', X, X + 0.012, -Y + 0.06, Y - 0.06, 0.07, 0.21, M['panel'], cuerpo, bevel=0.004)
for s in (-1, 1):
    cyl('perilla_%d' % s, (X + 0.035, s * 0.17, 0.14), 0.045, 0.045, 'X', M['perilla'], cuerpo, segs=8)
    box('perilla_raya_%d' % s, X + 0.057, X + 0.062, s * 0.17 - 0.008, s * 0.17 + 0.008, 0.14, 0.18, M['cromo'], cuerpo)
cyl('foquito', (X + 0.02, 0, 0.14), 0.022, 0.02, 'X', M['luz'], cuerpo, segs=10)

# Aceite (debajo del borde, para que se vea el pozo)
box('aceite', -X + T, X - T, -Y + T, Y - T, 0.255, 0.275, M['aceite'], aceite)

# Canasta de alambre (posición: BAJADA en el aceite; el código la sube)
CX, CY, CZ0, CZ1, A = 0.22, 0.24, 0.12, 0.30, 0.008
for i, z in enumerate((CZ0, 0.18, 0.24, CZ1)):   # anillos
    w = A * (1.8 if z == CZ1 else 1)
    beam('anillo_%d_a' % i, (-CX, -CY, z), (CX, -CY, z), w, M['alambre'], canasta)
    beam('anillo_%d_b' % i, (-CX, CY, z), (CX, CY, z), w, M['alambre'], canasta)
    beam('anillo_%d_c' % i, (-CX, -CY, z), (-CX, CY, z), w, M['alambre'], canasta)
    beam('anillo_%d_d' % i, (CX, -CY, z), (CX, CY, z), w, M['alambre'], canasta)
k = 0
for x in [-CX + i * 0.073 for i in range(7)]:   # alambres verticales, lados largos
    for y in (-CY, CY):
        beam('v_%d' % k, (x, y, CZ0), (x, y, CZ1), A, M['alambre'], canasta); k += 1
for y in [-CY + i * 0.08 for i in range(1, 6)]:  # alambres verticales, lados cortos
    for x in (-CX, CX):
        beam('v_%d' % k, (x, y, CZ0), (x, y, CZ1), A, M['alambre'], canasta); k += 1
for i in range(1, 6):                            # fondo en cuadrícula
    x = -CX + i * 0.073
    beam('fondo_x_%d' % i, (x, -CY, CZ0), (x, CY, CZ0), A, M['alambre'], canasta)
    y = -CY + i * 0.08
    beam('fondo_y_%d' % i, (-CX, y, CZ0), (CX, y, CZ0), A, M['alambre'], canasta)
# Ganchos de atrás (para colgarla) y mango negro hacia el pasillo
for s in (-1, 1):
    beam('gancho_sube_%d' % s, (-CX, s * 0.1, CZ1), (-CX - 0.02, s * 0.1, CZ1 + 0.07), A * 1.5, M['alambre'], canasta)
    beam('gancho_baja_%d' % s, (-CX - 0.02, s * 0.1, CZ1 + 0.07), (-CX - 0.07, s * 0.1, CZ1 + 0.02), A * 1.5, M['alambre'], canasta)
    beam('barra_mango_%d' % s, (CX, s * 0.035, CZ1), (0.42, s * 0.035, CZ1 + 0.07), A * 1.6, M['alambre'], canasta)
box('placa_mango', CX - 0.005, CX + 0.012, -0.06, 0.06, CZ1 - 0.08, CZ1 + 0.005, M['alambre'], canasta)
mango = cyl('mango', (0.51, 0, CZ1 + 0.08), 0.026, 0.2, 'X', M['mango'], canasta, segs=8)

REPO_GLB = os.path.join(REPO, 'assets', 'models', 'props')
os.makedirs(REPO_GLB, exist_ok=True)
exportar_para_juego(root, [cuerpo, aceite, canasta], os.path.join(REPO_GLB, 'freidora.glb'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO, 'source', 'blender', 'freidora.blend'))

# =====================================================================
# 2) PAPAS CRUDAS: bandeja de acero llena de palitos de papa
# =====================================================================
limpiar()
M = {
    'acero': mat('acero_bandeja', 0xdfe3e7, 0.35, 0.45),
    'cromo': mat('cromo', 0xe3e7ea, 0.2, 0.9),
    'papa': mat('papa_cruda', 0xf0e0aa, 0.6),
    'punta': mat('papa_cruda_punta', 0xd9c48a, 0.65),
}
root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)
papas = empty('papas_crudas', root)
BX, BY, BZ, G = 0.13, 0.105, 0.085, 0.01   # mitad del largo, mitad del ancho, alto, grosor
box('fondo', -BX + 0.01, BX - 0.01, -BY + 0.01, BY - 0.01, 0, G, M['acero'], papas, bevel=0.004)
box('lado_a', -BX, BX, -BY, -BY + G, 0, BZ, M['acero'], papas, bevel=0.003)
box('lado_b', -BX, BX, BY - G, BY, 0, BZ, M['acero'], papas, bevel=0.003)
box('lado_c', -BX, -BX + G, -BY, BY, 0, BZ, M['acero'], papas, bevel=0.003)
box('lado_d', BX - G, BX, -BY, BY, 0, BZ, M['acero'], papas, bevel=0.003)
box('borde_a', -BX - 0.012, BX + 0.012, -BY - 0.012, -BY + 0.004, BZ - 0.006, BZ + 0.004, M['cromo'], papas)
box('borde_b', -BX - 0.012, BX + 0.012, BY - 0.004, BY + 0.012, BZ - 0.006, BZ + 0.004, M['cromo'], papas)
box('borde_c', -BX - 0.012, -BX + 0.004, -BY, BY, BZ - 0.006, BZ + 0.004, M['cromo'], papas)
box('borde_d', BX - 0.004, BX + 0.012, -BY, BY, BZ - 0.006, BZ + 0.004, M['cromo'], papas)
# Palitos de papa: acostados en capas, y unos pocos asomándose hacia arriba
L, P = 0.2, 0.02   # largo y grosor de cada palito
def palito(nombre, centro, ang_z, ang_y):
    R = Matrix.Rotation(ang_z, 4, 'Z') @ Matrix.Rotation(ang_y, 4, 'Y')
    a = R @ Vector((-L / 2, 0, 0)) + Vector(centro)
    b = R @ Vector((L / 2, 0, 0)) + Vector(centro)
    beam(nombre, a, b, P, M['papa'], papas)
    for k, p in enumerate((a, b)):   # puntitas un poco más oscuras
        d = (b - a).normalized() * 0.006 * (1 if k else -1)
        beam(nombre + '_punta%d' % k, p, p + d, P * 1.02, M['punta'], papas)
n = 0
for capa, z in enumerate((0.022, 0.044, 0.066, 0.088)):
    for i in range(5 if capa < 3 else 3):
        y = -BY + 0.03 + i * (2 * BY - 0.06) / 4 + azar.uniform(-0.008, 0.008)
        palito('papa_%d' % n, (azar.uniform(-0.01, 0.01), y if capa < 3 else azar.uniform(-0.06, 0.06), z), azar.uniform(-0.25, 0.25), azar.uniform(-0.06, 0.06)); n += 1
for i in range(3):   # asomándose
    palito('papa_%d' % n, (azar.uniform(-0.04, 0.04), azar.uniform(-0.05, 0.05), 0.11), azar.uniform(-1.2, 1.2), azar.uniform(0.35, 0.6)); n += 1

exportar_para_juego(root, [papas], os.path.join(REPO_GLB, 'papas_crudas.glb'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO, 'source', 'blender', 'papas_crudas.blend'))
