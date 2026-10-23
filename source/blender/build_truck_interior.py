# -*- coding: utf-8 -*-
"""
Construye la cocina de ADENTRO del food truck (estilo cozy low-poly).

Piezas que busca el juego:
  - interior_static: mostradores, campana, repisas, caja registradora, máquina de sodas, salsas.
  - interior_middle: marco y luz de la ventanilla, comandas (se ESTIRAN con "Ampliar").
  - interior_rear: marco de la puerta de atrás (se CORRE con "Ampliar").
  - nevera_bisagra: la puerta de la nevera; el código la hace girar al abrir/cerrar.
Lo que se puede tocar con clic (plancha, plato, computadora, ingredientes) lo sigue dibujando el código.

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el modelo. Guarda source/blender/truck_interior.blend
     y exporta assets/models/props/truck_interior.glb (lo que carga el juego).
  3. Si cambias números aquí y lo vuelves a correr, se rearma todo.
     Si prefieres mover cosas a mano en Blender, NO lo vuelvas a correr después:
     exporta tú con File → Export → glTF 2.0 (.glb) al mismo archivo.

Reglas que el juego necesita:
  - Todo cuelga de "escala_juego" (×0.5 ancho/largo, ×0.56 alto): aquí se ve en metros del juego.
  - Ejes: +X = lado de la ventanilla / derecha, +Y = adelante, Z = arriba.
  - Los nombres de las piezas de arriba (los "empty") los busca el código: no los cambies.
  - Materiales "luz_..." brillan más de noche; "brillo_..." brillan siempre.
  - Los colores usan los mismos números (hex) que el código, para que se vean igual en el juego.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

# Carpeta del repo (este archivo vive en source/blender/)
def carpeta_repo():
    try:  # corriendo desde el editor de texto de Blender
        t = bpy.context.space_data.text
        if t and t.filepath:
            return os.path.abspath(os.path.join(os.path.dirname(bpy.path.abspath(t.filepath)), '..', '..'))
    except AttributeError:
        pass
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
REPO = carpeta_repo()

# ---------- Utilidades ----------
def hexrgb(h):
    return ((h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255)

def mat(name, col, rough=0.5, metal=0.0, emit=None, strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*hexrgb(col), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*hexrgb(emit), 1)
        b.inputs['Emission Strength'].default_value = strength
    m.diffuse_color = (*hexrgb(col), 1)
    return m

def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o

def empty(name, parent=None):
    o = link(bpy.data.objects.new(name, None))
    o.parent = parent
    o.empty_display_size = 0.5
    return o

def from_bm(name, bm, m, parent):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me))
    o.parent = parent
    return o

def box(name, x0, x1, y0, y1, z0, z1, m, parent, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    s = Vector((x1 - x0, y1 - y0, z1 - z0))
    for v in bm.verts:
        v.co = Vector((c.x + v.co.x * s.x, c.y + v.co.y * s.y, c.z + v.co.z * s.z))
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect='EDGES', clamp_overlap=True)
    return from_bm(name, bm, m, parent)

def prism(name, pts, axis, a0, a1, m, parent):
    """Perfil 2D extruido a lo largo de un eje. axis 'X': pts=(y,z); 'Y': (x,z); 'Z': (x,y)."""
    def P(u, v, a):
        return {'X': (a, u, v), 'Y': (u, a, v), 'Z': (u, v, a)}[axis]
    bm = bmesh.new()
    A = [bm.verts.new(P(u, v, a0)) for u, v in pts]
    B = [bm.verts.new(P(u, v, a1)) for u, v in pts]
    bm.faces.new(A)
    bm.faces.new(list(reversed(B)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A[i], A[j], B[j], B[i]))
    return from_bm(name, bm, m, parent)

def cyl(name, center, r, depth, axis, m, parent, segs=10, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    rot = {'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(-math.pi / 2, 4, 'X'),
           'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(center) @ rot, verts=bm.verts)
    return from_bm(name, bm, m, parent)

def beam(name, p0, p1, w, m, parent):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(w, w, d.length), verts=bm.verts)
    R = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ R, verts=bm.verts)
    return from_bm(name, bm, m, parent)

def text(name, body, size, center, m, parent, extrude=0.05):
    """Letras 3D que miran hacia +X y se leen de izquierda a derecha para quien está en la fila."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body, cu.size, cu.extrude = body, size, extrude
    cu.align_x, cu.align_y = 'CENTER', 'CENTER'
    tmp = link(bpy.data.objects.new(name + '_tmp', cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.transform(Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))  # texto X→Y, Y→Z, Z→X
    me.transform(Matrix.Translation(center))
    me.materials.clear()
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me))
    o.parent = parent
    return o

# ---------- Escena limpia (borra todo lo de la escena, pero deja abierto este script) ----------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
for datos in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
    for x in list(datos):
        datos.remove(x)

M = {
    'acero': mat('acero', 0xcfd4d8, 0.3, 0.75),
    'acero_claro': mat('acero_claro', 0xe3e7ea, 0.22, 0.8),
    'gabinete': mat('gabinete', 0xaab2ba, 0.35, 0.6),
    'cromo': mat('cromo', 0xdfe4e8, 0.18, 0.9),
    'oscuro': mat('oscuro', 0x1a1a1e, 0.7),
    'nevera': mat('nevera', 0xdde3ea, 0.22, 0.65),
    'madera': mat('madera', 0xa86a3c, 0.6),
    'carton': mat('carton', 0xc89b62, 0.85),
    'vidrio': mat('vidrio_frasco', 0xcfe8ee, 0.1, 0.1),
    'blanco': mat('blanco', 0xf4f4f0, 0.35),
    'rojo': mat('rojo', 0xd90429, 0.3),
    'amarillo': mat('amarillo', 0xffb703, 0.3),
    'verde': mat('verde', 0x52b788, 0.5),
    'azul_oscuro': mat('azul_oscuro', 0x2b2d42, 0.3, 0.3),
    'papel': mat('papel', 0xfffbe8, 0.8),
    'tela': mat('tela', 0x3d7ea6, 0.9),
    # "brillo_": brillan siempre (luces de adentro del truck)
    'brillo_calido': mat('brillo_calido', 0xfff1d0, 0.3, 0, emit=0xffd9a0, strength=1.0),
    'brillo_azul': mat('brillo_azul', 0xbfe6ff, 0.3, 0, emit=0x7cc8ff, strength=1.0),
    'brillo_pantalla': mat('brillo_pantalla', 0x1d3557, 0.3, 0, emit=0x4fa3ff, strength=1.0),
}

root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # metros del juego → unidades internas del código (igual que el truck de afuera)
fijo = empty('interior_static', root)    # muebles que no se mueven
medio = empty('interior_middle', root)   # cosas a lo largo de la ventanilla: se ESTIRAN con "Ampliar"
atras = empty('interior_rear', root)     # marco de la puerta de atrás: se CORRE con "Ampliar"
bisagra = empty('nevera_bisagra', root)  # la puerta de la nevera gira alrededor de este punto

# ---------- Medidas de adentro (metros del juego; vienen del código) ----------
# Paredes: atrás X=-2.6, ventanilla X=+2.6, frente Y=+5.4, puerta de atrás Y=-5.4, techo Z=5.85
TOP = 1.62          # altura de los mostradores (donde se ponen el plato y los panes)
X_COC0, X_COC1 = -2.6, -1.22   # mostrador de cocinar (con la plancha)
Y_COC0, Y_COC1 = -4.1, 0.9
X_SRV0, X_SRV1 = 1.22, 2.6     # mostrador de servir (lado de la ventanilla)
Y_SRV0, Y_SRV1 = -4.0, 4.0

# =====================================================================
# Mostrador de cocinar con plancha, campana y utensilios
# =====================================================================
def gabinete(prefix, x0, x1, y0, y1, frente_x, sentido, puertas, parent):
    """Mueble de acero: zócalo oscuro, cuerpo, tapa, puertas con manija en el lado del pasillo."""
    box(prefix + '_zocalo', min(x0, x1) + 0.06 * (sentido < 0), max(x0, x1) - 0.06 * (sentido > 0), y0, y1, 0.0, 0.12, M['oscuro'], parent)
    box(prefix + '_cuerpo', x0, x1, y0, y1, 0.12, TOP - 0.06, M['gabinete'], parent)
    box(prefix + '_tapa', x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, TOP - 0.06, TOP, M['acero_claro'], parent, bevel=0.01)
    paso = (y1 - y0) / puertas
    for i in range(puertas):
        a, b = y0 + i * paso + 0.06, y0 + (i + 1) * paso - 0.06
        fx0, fx1 = (frente_x, frente_x + 0.025) if sentido > 0 else (frente_x - 0.025, frente_x)
        box('%s_puerta_%d' % (prefix, i), fx0, fx1, a, b, 0.22, TOP - 0.2, M['acero'], parent)
        hx0, hx1 = (fx1, fx1 + 0.05) if sentido > 0 else (fx0 - 0.05, fx0)
        box('%s_manija_%d' % (prefix, i), hx0, hx1, a + 0.15, b - 0.15, TOP - 0.36, TOP - 0.31, M['cromo'], parent)

gabinete('cocina', X_COC0, X_COC1, Y_COC0, Y_COC1, X_COC1, +1, 4, fijo)
# Alrededor de la plancha (la plancha misma la dibuja el código, porque se puede hacer clic en ella)
G_Y0, G_Y1 = -1.62, 0.82
box('plancha_borde_frente', -1.3, -1.22, G_Y0, G_Y1, TOP, TOP + 0.09, M['cromo'], fijo)
box('plancha_canaleta', -1.24, -1.12, G_Y0, G_Y1, TOP - 0.12, TOP - 0.02, M['acero'], fijo)
box('plancha_protector_atras', -2.6, -2.5, G_Y0, G_Y1, TOP, TOP + 0.5, M['acero'], fijo)
for y in (G_Y0 - 0.04, G_Y1):
    box('plancha_protector_lado_%d' % int(y * 10), -2.6, -1.3, y, y + 0.04, TOP, TOP + 0.28, M['acero'], fijo)
for i, y in enumerate((-1.25, -0.6, 0.05, 0.6)):
    cyl('perilla_%d' % i, (-1.17, y, TOP - 0.24), 0.07, 0.06, 'X', M['oscuro'], fijo, segs=8)
    cyl('perilla_aro_%d' % i, (-1.2, y, TOP - 0.24), 0.09, 0.02, 'X', M['cromo'], fijo, segs=8)
# Pared de acero detrás del mostrador
box('salpicadero', -2.6, -2.57, Y_COC0, Y_COC1, TOP, 2.75, M['acero_claro'], fijo)
# Campana sobre la plancha
prism('campana', [(-2.6, 3.55), (-1.45, 3.55), (-1.45, 3.7), (-1.85, 4.35), (-2.6, 4.45)], 'Y', G_Y0 - 0.25, G_Y1 + 0.25, M['acero'], fijo)
box('campana_filtro', -2.52, -1.55, G_Y0 - 0.15, G_Y1 + 0.15, 3.52, 3.56, M['oscuro'], fijo)
for y in (-1.1, 0.3):
    box('campana_luz_%d' % int(y * 10), -2.0, -1.7, y - 0.25, y + 0.25, 3.5, 3.53, M['brillo_calido'], fijo)
box('campana_tubo', -2.6, -2.15, -0.75, 0.0, 4.4, 5.85, M['acero'], fijo)
# Barra con utensilios colgados (sobre la zona de los panes)
RX = -2.47
box('barra_utensilios', RX - 0.03, RX + 0.03, -3.95, -1.95, 3.2, 3.25, M['cromo'], fijo)
for y in (-3.95, -1.95):
    box('soporte_barra_%d' % int(-y * 10), -2.6, RX, y - 0.02, y + 0.02, 3.2, 3.25, M['cromo'], fijo)
# espátula
beam('espatula_mango', (RX, -3.7, 3.18), (RX, -3.7, 2.85), 0.04, M['oscuro'], fijo)
box('espatula_hoja', RX - 0.01, RX + 0.01, -3.82, -3.58, 2.55, 2.86, M['cromo'], fijo)
# cucharón
beam('cucharon_mango', (RX, -3.25, 3.18), (RX, -3.25, 2.75), 0.03, M['cromo'], fijo)
cyl('cucharon_taza', (RX + 0.04, -3.25, 2.7), 0.1, 0.1, 'Z', M['cromo'], fijo, segs=8, r2=0.06)
# pinzas
for k in (-1, 1):
    beam('pinzas_%d' % k, (RX, -2.85, 3.18), (RX, -2.85 + k * 0.06, 2.7), 0.025, M['cromo'], fijo)
# batidor
beam('batidor_mango', (RX, -2.5, 3.18), (RX, -2.5, 2.95), 0.04, M['oscuro'], fijo)
cyl('batidor_alambre', (RX, -2.5, 2.8), 0.04, 0.3, 'Z', M['cromo'], fijo, segs=6, r2=0.09)
# toalla
box('toalla', RX + 0.02, RX + 0.05, -2.3, -2.05, 2.75, 3.22, M['tela'], fijo)

# =====================================================================
# Repisas con frascos, platos y cajas (pared de atrás, por encima de la cabeza)
# =====================================================================
def repisa(nombre, y0, y1, z, parent):
    box(nombre, -2.6, -2.2, y0, y1, z, z + 0.05, M['madera'], parent, bevel=0.01)
    for y in (y0 + 0.15, y1 - 0.15):
        prism(nombre + '_soporte_%d' % int(y * 10), [(-2.6, z), (-2.32, z), (-2.6, z - 0.25)], 'Y', y - 0.02, y + 0.02, M['oscuro'], parent)

repisa('repisa_alta', -4.0, -1.9, 4.45, fijo)
repisa('repisa_baja', -4.0, -1.9, 3.75, fijo)
for i, (y, tapa) in enumerate(((-3.75, 'rojo'), (-3.45, 'amarillo'), (-3.15, 'verde'))):  # frascos
    cyl('frasco_%d' % i, (-2.4, y, 3.8 + 0.14), 0.1, 0.28, 'Z', M['vidrio'], fijo, segs=8)
    cyl('frasco_tapa_%d' % i, (-2.4, y, 3.8 + 0.31), 0.105, 0.06, 'Z', M[tapa], fijo, segs=8)
for i in range(5):  # pila de platos
    cyl('plato_pila_%d' % i, (-2.4, -2.65, 3.81 + i * 0.035), 0.17, 0.03, 'Z', M['blanco'], fijo, segs=12, r2=0.15)
for i, y in enumerate((-2.25, -2.05)):  # tazas
    cyl('taza_%d' % i, (-2.4, y, 3.88), 0.06, 0.13, 'Z', M['blanco'], fijo, segs=8)
for i, y in enumerate((-3.7, -3.2)):  # cajas de cartón
    box('caja_%d' % i, -2.55, -2.25, y - 0.2, y + 0.2, 4.5, 4.78, M['carton'], fijo, bevel=0.01)
cyl('aceite', (-2.4, -2.7, 4.65), 0.07, 0.4, 'Z', M['amarillo'], fijo, segs=8)
cyl('aceite_tapa', (-2.4, -2.7, 4.88), 0.03, 0.06, 'Z', M['rojo'], fijo, segs=6)
for i in range(3):  # pila de platos hondos
    cyl('tazon_%d' % i, (-2.4, -2.2, 4.53 + i * 0.07), 0.13, 0.08, 'Z', M['blanco'], fijo, segs=10, r2=0.09)
# Repisa entre la cocina y la nevera: provisiones
repisa('repisa_provisiones', 1.1, 3.15, 3.0, fijo)
for i, y in enumerate((1.4, 1.85, 2.3)):
    box('caja_pan_%d' % i, -2.55, -2.25, y - 0.18, y + 0.18, 3.05, 3.35, M['carton'], fijo, bevel=0.01)
cyl('sal', (-2.4, 2.75, 3.15), 0.06, 0.2, 'Z', M['blanco'], fijo, segs=8)
cyl('pimienta', (-2.4, 2.95, 3.15), 0.06, 0.2, 'Z', M['oscuro'], fijo, segs=8)

# =====================================================================
# Nevera: marco de arriba y zócalo (la puerta va en "nevera_bisagra")
# =====================================================================
box('nevera_tapa', -2.65, -1.12, 3.3, 5.1, 4.28, 4.5, M['acero'], fijo, bevel=0.02)
box('nevera_luz', -1.13, -1.1, 3.55, 4.85, 4.35, 4.43, M['brillo_azul'], fijo)
box('nevera_zocalo', -2.6, -1.12, 3.35, 5.05, 0.0, 0.11, M['oscuro'], fijo)
# Puerta (en la misma posición que la puerta del código, cerrada) y su manija
HINGE = Vector((-1.15, 3.35, 1.8))
puerta = [
    box('nevera_puerta', -1.21, -1.09, 3.36, 5.05, 0.11, 4.28, M['nevera'], bisagra, bevel=0.015),
    box('nevera_puerta_borde', -1.215, -1.205, 3.36, 5.05, 0.11, 4.28, M['oscuro'], bisagra),
    box('nevera_manija', -1.05, -1.0, 4.8, 4.86, 1.45, 2.65, M['cromo'], bisagra, bevel=0.01),
    box('nevera_manija_pie1', -1.09, -1.04, 4.8, 4.86, 1.5, 1.56, M['cromo'], bisagra),
    box('nevera_manija_pie2', -1.09, -1.04, 4.8, 4.86, 2.54, 2.6, M['cromo'], bisagra),
    box('nevera_placa', -1.09, -1.08, 3.75, 4.55, 3.55, 3.8, M['brillo_azul'], bisagra),
]
for o in puerta:
    o.data.transform(Matrix.Translation(-HINGE))   # la puerta se dibuja relativa a la bisagra
bisagra.location = HINGE

# =====================================================================
# Mostrador de servir: caja registradora, máquina de sodas, salsas
# =====================================================================
gabinete('servicio', X_SRV0, X_SRV1, Y_SRV0, Y_SRV1, X_SRV0, -1, 6, fijo)
# Caja registradora (en el mismo lugar que la del código)
box('caja_reg_base', 1.48, 2.12, -3.15, -2.45, TOP, TOP + 0.2, M['oscuro'], fijo, bevel=0.02)
box('caja_reg_cajon', 1.46, 1.48, -3.08, -2.52, TOP + 0.04, TOP + 0.14, M['acero'], fijo)
prism('caja_reg_teclado', [(1.5, TOP + 0.2), (1.95, TOP + 0.2), (1.95, TOP + 0.34), (1.6, TOP + 0.26)], 'Y', -3.1, -2.5, M['oscuro'], fijo)
for r in range(3):
    for c in range(4):
        box('tecla_%d_%d' % (r, c), 1.56 + r * 0.12, 1.64 + r * 0.12, -3.02 + c * 0.13, -2.94 + c * 0.13,
            TOP + 0.24 + r * 0.025, TOP + 0.27 + r * 0.025, M['blanco'] if (r + c) % 3 else M['amarillo'], fijo)
box('caja_reg_poste', 1.98, 2.06, -2.84, -2.76, TOP + 0.2, TOP + 0.45, M['oscuro'], fijo)
prism('caja_reg_pantalla', [(1.9, TOP + 0.45), (2.05, TOP + 0.45), (2.05, TOP + 0.66), (1.97, TOP + 0.66)], 'Y', -3.0, -2.6, M['oscuro'], fijo)
prism('caja_reg_pantalla_luz', [(1.89, TOP + 0.48), (1.92, TOP + 0.48), (1.96, TOP + 0.63), (1.93, TOP + 0.63)], 'Y', -2.97, -2.63, M['brillo_pantalla'], fijo)
cyl('propinas', (2.2, -3.6, TOP + 0.13), 0.12, 0.26, 'Z', M['vidrio'], fijo, segs=8)
cyl('propinas_monedas', (2.2, -3.6, TOP + 0.04), 0.1, 0.06, 'Z', M['amarillo'], fijo, segs=8)
# Máquina de sodas (mismo lugar y tamaño que la del código)
box('soda_cuerpo', 1.38, 2.25, 1.7, 3.1, TOP, TOP + 1.08, M['azul_oscuro'], fijo, bevel=0.03)
box('soda_frente', 1.35, 1.38, 1.78, 3.02, TOP + 0.3, TOP + 0.8, M['acero'], fijo)
box('soda_letrero', 1.35, 1.38, 1.78, 3.02, TOP + 0.84, TOP + 1.02, M['brillo_calido'], fijo)
for i, (y, col) in enumerate(((2.0, 'rojo'), (2.4, 'amarillo'), (2.8, 'verde'))):
    box('soda_sabor_%d' % i, 1.34, 1.35, y - 0.13, y + 0.13, TOP + 0.87, TOP + 0.99, M[col], fijo)
    cyl('soda_boquilla_%d' % i, (1.31, y, TOP + 0.42), 0.04, 0.1, 'Z', M['oscuro'], fijo, segs=6)
    box('soda_boton_%d' % i, 1.33, 1.35, y - 0.06, y + 0.06, TOP + 0.6, TOP + 0.7, M[col], fijo)
box('soda_bandeja', 1.2, 1.38, 1.78, 3.02, TOP, TOP + 0.05, M['cromo'], fijo)
# Salsas (en el lugar de las del código)
for nombre, y, col in (('ketchup', 0.8, 'rojo'), ('mostaza', 1.04, 'amarillo')):
    cyl(nombre, (1.8, y, TOP + 0.16), 0.08, 0.32, 'Z', M[col], fijo, segs=8)
    cyl(nombre + '_tapa', (1.8, y, TOP + 0.35), 0.06, 0.06, 'Z', M['blanco'], fijo, segs=8)
    cyl(nombre + '_punta', (1.8, y, TOP + 0.43), 0.035, 0.1, 'Z', M['blanco'], fijo, segs=6, r2=0.008)
# Servilletero y vasos
box('servilletero', 1.85, 2.15, 3.3, 3.55, TOP, TOP + 0.22, M['cromo'], fijo, bevel=0.02)
box('servilletas', 1.88, 2.12, 3.33, 3.52, TOP + 0.22, TOP + 0.25, M['papel'], fijo)
for i in range(4):
    cyl('vaso_%d' % i, (2.0, 3.8, TOP + 0.08 + i * 0.06), 0.09, 0.16, 'Z', M['rojo'] if i == 3 else M['blanco'], fijo, segs=10, r2=0.07)

# =====================================================================
# interior_middle: marco de la ventanilla, luz cálida y comandas (se estiran)
# =====================================================================
box('ventana_marco_abajo', 2.48, 2.6, -5.3, 5.3, 1.72, 1.86, M['madera'], medio, bevel=0.02)
box('ventana_marco_arriba', 2.48, 2.6, -5.3, 5.3, 3.54, 3.7, M['madera'], medio, bevel=0.02)
box('ventana_luz', 2.42, 2.56, -5.1, 5.1, 3.49, 3.56, M['brillo_calido'], medio)
box('comandas_barra', 2.36, 2.42, -3.6, 3.6, 3.36, 3.41, M['cromo'], medio)
for i, y in enumerate((-3.1, -2.4, 2.3, 3.0)):   # papelitos con pedidos (lejos del plato y la pantalla)
    box('comanda_%d' % i, 2.38, 2.4, y - 0.14, y + 0.14, 3.0, 3.36, M['papel'], medio)
    box('comanda_raya_%d' % i, 2.375, 2.38, y - 0.1, y + 0.1, 3.2, 3.22, M['rojo'], medio)

# =====================================================================
# interior_rear: marco de la puerta de atrás (se corre con "Ampliar")
# =====================================================================
for s in (-1, 1):
    box('puerta_marco_%d' % s, s * 1.0 - 0.1 * (s < 0), s * 1.0 + 0.1 * (s > 0), -5.4, -5.33, 0.0, 3.86, M['acero'], atras)
box('puerta_marco_arriba', -1.1, 1.1, -5.4, -5.33, 3.78, 3.9, M['acero'], atras)
box('puerta_gancho', -1.6, -1.5, -5.4, -5.32, 3.1, 3.18, M['cromo'], atras)
box('delantal', -1.68, -1.42, -5.37, -5.33, 2.1, 3.12, M['rojo'], atras)

# ---------- Guardar y exportar ----------
def exportar_para_juego(root, piezas, glb_path):
    """Exporta una COPIA donde las partes de cada pieza se unen por material
    (muchos menos "draw calls" = más rápido en el navegador). La escena se queda con las partes separadas."""
    col = bpy.data.collections.new('para_el_juego')
    bpy.context.scene.collection.children.link(col)
    col.objects.link(root)
    temporales, n_tri = [], 0
    for pieza in piezas:
        col.objects.link(pieza)
        grupos = {}
        for o in [c for c in pieza.children if c.type == 'MESH']:
            grupos.setdefault(o.data.materials[0].name, []).append(o)
        for mname, objs in grupos.items():
            bm = bmesh.new()
            for o in objs:
                bm.from_mesh(o.data)
            n_tri += sum(len(f.verts) - 2 for f in bm.faces)
            me = bpy.data.meshes.new(pieza.name + '_' + mname)
            bm.to_mesh(me)
            bm.free()
            me.materials.append(bpy.data.materials[mname])
            unido = bpy.data.objects.new(pieza.name + '_' + mname, me)
            col.objects.link(unido)
            unido.parent = pieza
            temporales.append(unido)
    vl = bpy.context.view_layer
    vl.active_layer_collection = vl.layer_collection.children[col.name]
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_yup=True, export_apply=True,
                              export_cameras=False, export_lights=False, use_active_collection=True)
    vl.active_layer_collection = vl.layer_collection
    for o in temporales:
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    bpy.data.collections.remove(col)
    print('OK %s: %d mallas para el juego, ~%d triángulos, %.0f KB' % (
        os.path.basename(glb_path), len(temporales), n_tri, os.path.getsize(glb_path) / 1024))

blend_path = os.path.join(REPO, 'source', 'blender', 'truck_interior.blend')
glb_path = os.path.join(REPO, *'assets/models/props/truck_interior.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo, medio, atras, bisagra], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
