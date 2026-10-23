# -*- coding: utf-8 -*-
"""
Construye la COCINA-COMEDOR de la casa (estilo cozy low-poly, como kitchen_morning.jpg).

Pieza que busca el juego:
  - cocina_casa: mueble de abajo con puertas, cajones, horno, estufa, lavaplatos y grifo, escurridor,
    azulejos, muebles de arriba, campana, nevera con imanes y un dibujo, mesa con sillas,
    frutero, florero y lámpara colgante. También la tostadora, la sartén y el cartón de huevos
    (se ven aquí, pero el clic lo sigue recibiendo el código, en el mismo lugar).
La casa no está escalada: 1 metro aquí = 1 unidad del juego. Paredes, piso y techo los dibuja el código.

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el modelo. Guarda source/blender/house_kitchen.blend
     y exporta assets/models/environment/house_kitchen.glb (lo que carga el juego).
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
    'madera': mat('madera_cocina', 0xb0743f, 0.55),
    'madera_marco': mat('madera_marco', 0x9a6232, 0.55),
    'madera_mesa': mat('madera_mesa', 0xc48a52, 0.55),
    'zocalo': mat('zocalo', 0x3e2a22, 0.7),
    'piedra': mat('piedra', 0xe0dace, 0.3, 0.05),
    'acero': mat('acero', 0xcfd4d8, 0.35, 0.3),   # poco metálico: en la casa el reflejo del cielo lo pintaba de azul
    'cromo': mat('cromo', 0xe4e8eb, 0.25, 0.35),
    'oscuro': mat('oscuro', 0x15181b, 0.35),
    'gris': mat('gris', 0x3a3f45, 0.5),
    'vidrio_horno': mat('vidrio_horno', 0x20262c, 0.1, 0.4),
    'azulejo': mat('azulejo', 0xdfeef0, 0.3),
    'azulejo_linea': mat('azulejo_linea', 0xb9cfd3, 0.5),
    'nevera': mat('nevera', 0xe9e4d4, 0.3, 0.1),
    'crema': mat('crema_tostadora', 0xf2e8d0, 0.3, 0.2),
    'carton': mat('carton_huevos', 0xc8b79a, 1.0),
    'papel': mat('papel', 0xfffbe8, 0.8),
    'rojo': mat('rojo', 0xd9534f, 0.5),
    'amarillo': mat('amarillo', 0xf4c430, 0.5),
    'azul': mat('azul', 0x3a7bd5, 0.5),
    'verde': mat('verde', 0x4caf50, 0.6),
    'naranja': mat('naranja', 0xf28c28, 0.6),
    'blanco': mat('blanco', 0xf4f1ea, 0.35),
    'terracota': mat('terracota', 0xc0643c, 0.8),
    'brillo_lampara': mat('brillo_lampara', 0xfff4e0, 0.5, 0, emit=0xffe0b0, strength=1.0),
}

root = empty('escala_juego')       # la casa NO está escalada: 1 metro = 1 unidad del juego
fijo = empty('cocina_casa', root)

# ---------- Medidas (vienen del código; X = x, Y = -z, Z = altura) ----------
# Pared del fondo: su cara de adentro está en Y = 10.85. Mostrador: X -5.9..2.1, Y 10.05..10.95, alto 0.9.
# Lo que se toca con clic (platos, huevos, pan, sartén, tostadora, plato del desayuno) lo sigue manejando el código.
CX0, CX1, CY0, CY1 = -5.9, 2.1, 10.05, 10.85
WALL = 10.85
TOP = 0.95

# =====================================================================
# Mueble de abajo: puertas con marco, cajones, horno y lavaplatos
# =====================================================================
box('mueble_zocalo', CX0, CX1, CY0 + 0.08, CY1, 0.0, 0.1, M['zocalo'], fijo)
box('mueble_cuerpo', CX0, CX1, CY0, CY1, 0.1, 0.9, M['madera'], fijo)
box('mesada', CX0 - 0.05, CX1 + 0.05, CY0 - 0.05, WALL, 0.9, TOP, M['piedra'], fijo, bevel=0.01)

def puerta(nombre, x0, x1, z0, z1, manija='arriba'):
    """Puerta estilo "shaker": marco, panel hundido y manija de metal (mira hacia la sala, -Y)."""
    box(nombre, x0, x1, CY0 - 0.025, CY0, z0, z1, M['madera_marco'], fijo)
    box(nombre + '_panel', x0 + 0.07, x1 - 0.07, CY0 - 0.03, CY0 - 0.025, z0 + 0.07, z1 - 0.07, M['madera'], fijo)
    if manija == 'arriba':
        box(nombre + '_manija', (x0 + x1) / 2 - 0.1, (x0 + x1) / 2 + 0.1, CY0 - 0.07, CY0 - 0.03, z1 - 0.1, z1 - 0.07, M['cromo'], fijo)
    else:
        xm = x1 - 0.1 if manija == 'der' else x0 + 0.1
        box(nombre + '_manija', xm - 0.015, xm + 0.015, CY0 - 0.07, CY0 - 0.03, z1 - 0.35, z1 - 0.1, M['cromo'], fijo)

# Tramos del mueble (de izquierda a derecha). El horno va debajo de la estufa (X -0.85..0.05).
tramos = [(-5.85, -4.85), (-4.8, -3.8), (-3.75, -2.75), (-2.7, -1.7), (-1.65, -0.9), (0.1, 1.1), (1.15, 2.05)]
for i, (x0, x1) in enumerate(tramos):
    if i == 1:   # debajo del lavaplatos: dos puertas, sin cajón
        puerta('puerta_lavaplatos_a', x0 + 0.02, (x0 + x1) / 2 - 0.01, 0.14, 0.86, 'der')
        puerta('puerta_lavaplatos_b', (x0 + x1) / 2 + 0.01, x1 - 0.02, 0.14, 0.86, 'izq')
        continue
    puerta('cajon_%d' % i, x0 + 0.02, x1 - 0.02, 0.68, 0.86)
    puerta('puerta_%d' % i, x0 + 0.02, x1 - 0.02, 0.14, 0.64, 'der' if i % 2 else 'izq')
# Horno
box('horno', -0.85, 0.05, CY0 - 0.03, CY0, 0.12, 0.86, M['acero'], fijo)
box('horno_vidrio', -0.75, -0.05, CY0 - 0.035, CY0 - 0.03, 0.22, 0.62, M['vidrio_horno'], fijo)
box('horno_manija', -0.7, -0.1, CY0 - 0.09, CY0 - 0.05, 0.68, 0.72, M['cromo'], fijo)
for i, x in enumerate((-0.7, -0.5, -0.2, 0.0)):
    cyl('perilla_estufa_%d' % i, (x, CY0 - 0.05, 0.8), 0.03, 0.04, 'Y', M['oscuro'], fijo, segs=8)
# Estufa encima (la sartén del código va encima de las hornillas)
box('estufa', -0.85, 0.05, 10.12, 10.88, TOP, 1.0, M['oscuro'], fijo)
for i, (x, z) in enumerate(((-0.6, -10.67), (-0.2, -10.67), (-0.6, -10.33), (-0.2, -10.33))):
    cyl('hornilla_%d' % i, (x, -z, 1.006), 0.11, 0.012, 'Z', M['gris'], fijo, segs=10)
    cyl('hornilla_centro_%d' % i, (x, -z, 1.013), 0.04, 0.012, 'Z', M['oscuro'], fijo, segs=8)
# Lavaplatos (la espuma del código aparece aquí al fregar) y grifo
SX = -4.3
box('lavaplatos_fondo', SX - 0.47, SX + 0.47, 10.22, 10.78, TOP, TOP + 0.003, M['acero'], fijo)
for nombre, x0, x1, y0, y1 in (('borde_a', SX - 0.5, SX + 0.5, 10.18, 10.22), ('borde_b', SX - 0.5, SX + 0.5, 10.78, 10.82),
                               ('borde_c', SX - 0.5, SX - 0.46, 10.18, 10.82), ('borde_d', SX + 0.46, SX + 0.5, 10.18, 10.82)):
    box('lavaplatos_' + nombre, x0, x1, y0, y1, TOP, TOP + 0.03, M['cromo'], fijo)
cyl('grifo_base', (SX, 10.8, TOP + 0.03), 0.04, 0.06, 'Z', M['cromo'], fijo, segs=8)
beam('grifo_tubo', (SX, 10.8, TOP + 0.03), (SX, 10.8, TOP + 0.35), 0.035, M['cromo'], fijo)
beam('grifo_curva', (SX, 10.8, TOP + 0.35), (SX, 10.62, TOP + 0.3), 0.035, M['cromo'], fijo)
beam('grifo_manija', (SX + 0.08, 10.8, TOP + 0.08), (SX + 0.16, 10.76, TOP + 0.12), 0.02, M['cromo'], fijo)
# Escurridor de platos
box('escurridor', -3.62, -2.78, 10.3, 10.72, TOP, TOP + 0.02, M['acero'], fijo)
for k in range(6):
    box('escurridor_varilla_%d' % k, -3.55 + k * 0.14, -3.53 + k * 0.14, 10.32, 10.7, TOP + 0.02, TOP + 0.12, M['cromo'], fijo)

# Azulejos en la pared, entre la mesada y los muebles de arriba
box('azulejos', CX0, CX1, WALL - 0.01, WALL, TOP, 1.55, M['azulejo'], fijo)
for k in range(1, 4):
    box('azulejo_linea_h%d' % k, CX0, CX1, WALL - 0.012, WALL - 0.01, TOP + k * 0.15, TOP + k * 0.15 + 0.008, M['azulejo_linea'], fijo)
for k in range(1, 27):
    x = CX0 + k * 0.3
    box('azulejo_linea_v%d' % k, x, x + 0.008, WALL - 0.012, WALL - 0.01, TOP, 1.55, M['azulejo_linea'], fijo)

# =====================================================================
# Muebles de arriba (con puertas) y campana sobre la estufa
# =====================================================================
UY0 = 10.5
def mueble_arriba(prefix, x0, x1):
    box(prefix, x0, x1, UY0, WALL, 2.2, 3.0, M['madera'], fijo)
    n = max(1, round((x1 - x0) / 0.6))
    paso = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * paso + 0.02, x0 + (i + 1) * paso - 0.02
        box('%s_puerta_%d' % (prefix, i), a, b, UY0 - 0.025, UY0, 2.23, 2.97, M['madera_marco'], fijo)
        box('%s_panel_%d' % (prefix, i), a + 0.07, b - 0.07, UY0 - 0.03, UY0 - 0.025, 2.3, 2.9, M['madera'], fijo)
        xm = b - 0.08 if i % 2 == 0 else a + 0.08
        box('%s_manija_%d' % (prefix, i), xm - 0.012, xm + 0.012, UY0 - 0.06, UY0 - 0.03, 2.27, 2.47, M['cromo'], fijo)
mueble_arriba('arriba_izq', CX0, -0.9)
mueble_arriba('arriba_der', 0.25, CX1)
prism('campana', [(10.35, 2.15), (WALL, 2.15), (WALL, 2.45), (10.6, 2.45)], 'X', -0.95, 0.15, M['acero'], fijo)
box('campana_tubo', -0.6, -0.2, 10.6, WALL, 2.45, 3.5, M['acero'], fijo)
box('campana_luz', -0.75, -0.05, 10.42, 10.6, 2.145, 2.15, M['brillo_lampara'], fijo)

# =====================================================================
# Cosas sobre la mesada (lejos de lo que se toca con clic)
# =====================================================================
# Tostadora, sartén y cartón de huevos: se ven aquí, pero el clic lo recibe el código (en el mismo lugar)
box('tostadora', 0.86, 1.34, 10.36, 10.64, TOP, 1.16, M['crema'], fijo, bevel=0.04)
for k, x in enumerate((1.02, 1.18)):
    box('tostadora_ranura_%d' % k, x - 0.025, x + 0.025, 10.4, 10.6, 1.16, 1.165, M['oscuro'], fijo)
box('tostadora_palanca', 1.34, 1.38, 10.47, 10.53, 1.05, 1.09, M['oscuro'], fijo)
cyl('sarten', (-0.6, 10.33, 1.06), 0.17, 0.05, 'Z', M['oscuro'], fijo, segs=12, r2=0.14)
cyl('sarten_fondo', (-0.6, 10.33, 1.086), 0.14, 0.002, 'Z', M['gris'], fijo, segs=12)
beam('sarten_mango', (-0.6, 10.19, 1.07), (-0.6, 9.97, 1.08), 0.035, M['madera_mesa'], fijo)
box('carton', -2.5, -2.1, 10.38, 10.62, TOP, 1.0, M['carton'], fijo)
for i in range(3):
    for j in range(2):
        cyl('carton_hueco_%d_%d' % (i, j), (-2.39 + i * 0.09, 10.45 + j * 0.1, 1.01), 0.04, 0.03, 'Z', M['carton'], fijo, segs=6, r2=0.03)
box('carton_tapa', -2.5, -2.1, 10.61, 10.64, TOP + 0.05, TOP + 0.24, M['carton'], fijo)
# Tabla de picar (detrás del pan), frasco de cucharas, hervidor, toallas de papel
box('tabla_picar', -2.05, -1.45, 10.78, 10.83, TOP, TOP + 0.38, M['madera_mesa'], fijo, bevel=0.01)
cyl('frasco_cucharas', (0.42, 10.7, TOP + 0.1), 0.07, 0.2, 'Z', M['terracota'], fijo, segs=8)
for k, (dx, dy) in enumerate(((-0.02, 0.0), (0.02, 0.02), (0.0, -0.02))):
    beam('cuchara_%d' % k, (0.42 + dx, 10.7 + dy, TOP + 0.15), (0.42 + dx * 3, 10.7 + dy * 3, TOP + 0.38), 0.02, M['madera_mesa'], fijo)
cyl('hervidor', (1.75, 10.62, TOP + 0.11), 0.12, 0.22, 'Z', M['rojo'], fijo, segs=10, r2=0.09)
cyl('hervidor_tapa', (1.75, 10.62, TOP + 0.24), 0.06, 0.04, 'Z', M['oscuro'], fijo, segs=8)
beam('hervidor_pico', (1.86, 10.62, TOP + 0.12), (1.95, 10.62, TOP + 0.2), 0.03, M['rojo'], fijo)
cyl('papel_cocina', (-5.3, 10.75, 1.25), 0.06, 0.26, 'X', M['papel'], fijo, segs=10)
box('papel_soporte', -5.45, -5.43, 10.78, WALL, 1.18, 1.32, M['cromo'], fijo)

# =====================================================================
# Nevera (dos puertas, imanes y un dibujo de Ignacio 🖍️)
# =====================================================================
FX0, FX1, FY0, FY1 = 4.45, 5.35, 10.0, 10.8
box('nevera', FX0, FX1, FY0 + 0.03, FY1, 0.0, 2.0, M['nevera'], fijo, bevel=0.04)
box('nevera_puerta_arriba', FX0 + 0.02, FX1 - 0.02, FY0, FY0 + 0.03, 1.42, 1.97, M['nevera'], fijo, bevel=0.01)
box('nevera_puerta_abajo', FX0 + 0.02, FX1 - 0.02, FY0, FY0 + 0.03, 0.05, 1.39, M['nevera'], fijo, bevel=0.01)
box('nevera_manija_arriba', FX0 + 0.06, FX0 + 0.1, FY0 - 0.05, FY0, 1.47, 1.75, M['cromo'], fijo)
box('nevera_manija_abajo', FX0 + 0.06, FX0 + 0.1, FY0 - 0.05, FY0, 0.95, 1.3, M['cromo'], fijo)
box('dibujo', 4.75, 5.15, FY0 - 0.005, FY0, 0.85, 1.2, M['papel'], fijo)
box('dibujo_sol', 4.98, 5.08, FY0 - 0.007, FY0 - 0.005, 1.08, 1.16, M['amarillo'], fijo)
box('dibujo_casa', 4.82, 4.97, FY0 - 0.007, FY0 - 0.005, 0.9, 1.02, M['rojo'], fijo)
box('dibujo_pasto', 4.77, 5.13, FY0 - 0.007, FY0 - 0.005, 0.86, 0.9, M['verde'], fijo)
for k, (x, z, col) in enumerate(((4.7, 1.8, 'rojo'), (5.0, 1.65, 'azul'), (5.2, 1.85, 'amarillo'), (4.95, 1.22, 'verde'))):
    cyl('iman_%d' % k, (x, FY0 - 0.01, z), 0.035, 0.02, 'Y', M[col], fijo, segs=6)

# =====================================================================
# Mesa del comedor con sillas, frutero, florero y lámpara colgante
# =====================================================================
TX, TY = 2.8, 7.6   # centro de la mesa (el plato del desayuno del código va en el centro)
box('mesa', TX - 1.0, TX + 1.0, TY - 0.6, TY + 0.6, 0.72, 0.8, M['madera_mesa'], fijo, bevel=0.015)
for i, (dx, dy) in enumerate(((-0.9, -0.5), (0.9, -0.5), (-0.9, 0.5), (0.9, 0.5))):
    box('mesa_pata_%d' % i, TX + dx - 0.04, TX + dx + 0.04, TY + dy - 0.04, TY + dy + 0.04, 0.0, 0.72, M['madera_marco'], fijo)
for k, cy in enumerate((6.6, 8.6)):   # sillas (el respaldo va del lado de afuera de la mesa)
    afuera = -1 if cy < TY else 1
    box('silla_asiento_%d' % k, TX - 0.25, TX + 0.25, cy - 0.25, cy + 0.25, 0.42, 0.48, M['madera_mesa'], fijo, bevel=0.01)
    for i, (dx, dy) in enumerate(((-0.21, -0.21), (0.21, -0.21), (-0.21, 0.21), (0.21, 0.21))):
        box('silla_pata_%d_%d' % (k, i), TX + dx - 0.025, TX + dx + 0.025, cy + dy - 0.025, cy + dy + 0.025, 0.0, 0.42, M['madera_marco'], fijo)
    yb = cy + afuera * 0.22
    for i, dx in enumerate((-0.21, 0.21)):
        box('silla_poste_%d_%d' % (k, i), TX + dx - 0.025, TX + dx + 0.025, yb - 0.025, yb + 0.025, 0.48, 1.0, M['madera_marco'], fijo)
    for j in range(3):
        box('silla_tabla_%d_%d' % (k, j), TX - 0.2, TX + 0.2, yb - 0.015, yb + 0.015, 0.6 + j * 0.13, 0.66 + j * 0.13, M['madera_mesa'], fijo)
# Frutero con naranjas, florero con flores
cyl('frutero', (2.05, 7.95, 0.84), 0.16, 0.08, 'Z', M['blanco'], fijo, segs=10, r2=0.2)
for k, (dx, dy) in enumerate(((-0.06, -0.04), (0.07, 0.0), (0.0, 0.07), (0.01, -0.02))):
    cyl('naranja_%d' % k, (2.05 + dx, 7.95 + dy, 0.92 + (0.05 if k == 3 else 0)), 0.055, 0.1, 'Z', M['naranja'], fijo, segs=7, r2=0.04)
cyl('florero', (3.55, 7.3, 0.9), 0.06, 0.2, 'Z', M['azul'], fijo, segs=8, r2=0.04)
for k, (dx, dy, col) in enumerate(((0.0, 0.0, 'amarillo'), (0.06, 0.03, 'rojo'), (-0.05, 0.04, 'blanco'))):
    beam('tallo_%d' % k, (3.55, 7.3, 0.98), (3.55 + dx, 7.3 + dy, 1.18), 0.012, M['verde'], fijo)
    cyl('flor_%d' % k, (3.55 + dx, 7.3 + dy, 1.2), 0.04, 0.03, 'Z', M[col], fijo, segs=6)
# Lámpara colgante facetada sobre la mesa
beam('lampara_cable', (TX, TY, 3.5), (TX, TY, 2.75), 0.015, M['oscuro'], fijo)
cyl('lampara_colgante_arriba', (TX, TY, 2.68), 0.08, 0.14, 'Z', M['blanco'], fijo, segs=6, r2=0.04)
cyl('lampara_colgante_abajo', (TX, TY, 2.55), 0.2, 0.12, 'Z', M['blanco'], fijo, segs=6, r2=0.08)
cyl('lampara_colgante_luz', (TX, TY, 2.485), 0.17, 0.01, 'Z', M['brillo_lampara'], fijo, segs=6)

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

blend_path = os.path.join(REPO, 'source', 'blender', 'house_kitchen.blend')
glb_path = os.path.join(REPO, *'assets/models/environment/house_kitchen.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
