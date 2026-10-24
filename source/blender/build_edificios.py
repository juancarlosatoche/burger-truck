# -*- coding: utf-8 -*-
"""
Construye los 5 EDIFICIOS de fondo de la plaza (estilo cozy low-poly), siguiendo la imagen de Ignacio:
reference/environment/edificios_plaza.jpg

Archivo que crea: assets/models/environment/edificios.glb, con la pieza "edificios" y adentro uno por edificio:
  edificio_ladrillo  → ladrillo con tanque de agua en el techo
  edificio_torre     → torre azul delgada
  edificio_tiendas   → terracota con tiendas y toldos de rayas
  edificio_plantas   → crema escalonado con balcones y plantas
  edificio_esquina   → gris con la esquina redonda
Cada edificio es distinto (nada de copiar y pegar, regla de Chong-U).

Las ventanas encendidas usan el material "luz_ventana": el juego las prende al anochecer.
Las ventanas apagadas usan "ventana_oscura".

No está escalado: 1 metro aquí = 1 unidad del juego (X = x del juego, Y = -z del juego, Z = arriba),
igual que la plaza. Los edificios van en los mismos lugares que los que dibuja el código,
con el frente mirando hacia la plaza (hacia -X).

Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
"""
import bpy, bmesh, math, os, random
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

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
for datos in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.collections):
    for x in list(datos):
        datos.remove(x)

azar = random.Random(11)   # siempre el mismo "azar": las mismas ventanas prendidas cada vez
M = {
    'azul': mat('fachada_azul', 0x55708f, 0.85),
    'terracota': mat('fachada_terracota', 0xa9563a, 0.85),
    'crema': mat('fachada_crema', 0xdcc9a3, 0.85),
    'ladrillo': mat('fachada_ladrillo', 0x8e4a34, 0.9),
    'ladrillo_oscuro': mat('ladrillo_junta', 0x6e3626, 0.9),
    'pizarra': mat('fachada_pizarra', 0x5c6670, 0.85),
    'gris': mat('fachada_gris', 0x6d737c, 0.85),
    'gris_claro': mat('franja_gris', 0x9aa1aa, 0.8),
    'marco': mat('marco_ventana', 0xe8dcc4, 0.7),
    'techo': mat('techo', 0x4a4f57, 0.9),
    'oscuro': mat('oscuro', 0x2a2d33, 0.8),
    'madera': mat('madera_tanque', 0x8a6a4a, 0.85),
    'metal': mat('metal', 0x7d848c, 0.5, 0.6),
    'rojo': mat('toldo_rojo', 0xc0442f, 0.8),
    'blanco': mat('toldo_blanco', 0xf1e8d8, 0.8),
    'maceta': mat('maceta', 0xb5651d, 0.8),
    'planta': mat('planta', 0x5e8f4a, 0.9),
    'planta2': mat('planta_clara', 0x7aa85a, 0.9),
    'vidrio': mat('ventana_oscura', 0x26364a, 0.3, 0.2),
    # "luz_": el juego las prende al anochecer
    'luz': mat('luz_ventana', 0xffd88a, 0.4, 0, emit=0xffc46a, strength=1.0),
}

edificios = empty('edificios')

def ventana(pieza, nombre, cara, x, u, z, w, h, prob=0.45, marco=True):
    """Una ventana en la cara 'cara' (-X = frente, +Y / -Y = lados) del edificio.
    x = plano de la fachada, u = posición a lo largo de la fachada, z = abajo de la ventana."""
    luz = azar.random() < prob
    vid = M['luz'] if luz else M['vidrio']
    if cara == '-X':
        if marco:
            box(nombre + '_m', x - 0.06, x, u - w / 2 - 0.1, u + w / 2 + 0.1, z - 0.1, z + h + 0.1, M['marco'], pieza)
            box(nombre + '_r', x - 0.14, x, u - w / 2 - 0.14, u + w / 2 + 0.14, z - 0.16, z - 0.08, M['marco'], pieza)  # repisa
        box(nombre, x - 0.12, x - 0.03, u - w / 2, u + w / 2, z, z + h, vid, pieza)  # el vidrio sale un poco del marco (sin parpadeo)
    else:
        s = 1 if cara == '+Y' else -1
        if marco:
            box(nombre + '_m', u - w / 2 - 0.1, u + w / 2 + 0.1, *sorted((x, x + 0.06 * s)), z - 0.1, z + h + 0.1, M['marco'], pieza)
        box(nombre, u - w / 2, u + w / 2, *sorted((x + 0.03 * s, x + 0.12 * s)), z, z + h, vid, pieza)

def fila_ventanas(pieza, base, cara, x, u0, u1, cols, pisos, z0, alto_piso, w=1.0, h=1.5, prob=0.45, marco=True):
    for p in range(pisos):
        for c in range(cols):
            u = u0 + (c + 0.5) * (u1 - u0) / cols
            ventana(pieza, '%s_v%s_%d_%d' % (base, cara, p, c), cara, x, u, z0 + p * alto_piso + 0.8, w, h, prob, marco)

def caja_edificio(pieza, nombre, x0, x1, y0, y1, z0, z1, m, cornisa=True):
    box(nombre, x0, x1, y0, y1, z0, z1, m, pieza)
    if cornisa:
        box(nombre + '_cornisa', x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, z1, z1 + 0.35, M['marco'], pieza, bevel=0.04)
        box(nombre + '_techo', x0, x1, y0, y1, z1 + 0.35, z1 + 0.45, M['techo'], pieza)

def antena(pieza, nombre, x, y, z, alto=2.2):
    beam(nombre, (x, y, z), (x, y, z + alto), 0.07, M['metal'], pieza)
    for k, a in enumerate((0.6, 0.9, 1.2)):
        beam(nombre + '_b%d' % k, (x, y - a * 0.5, z + alto - 0.25 * k), (x, y + a * 0.5, z + alto - 0.25 * k), 0.05, M['metal'], pieza)

def aire(pieza, nombre, x, y, z):
    box(nombre, x - 0.6, x + 0.6, y - 0.5, y + 0.5, z, z + 0.8, M['gris_claro'], pieza, bevel=0.05)
    cyl(nombre + '_ventilador', (x, y, z + 0.82), 0.35, 0.04, 'Z', M['oscuro'], pieza, segs=10)

def puerta(pieza, nombre, x, u, ancho=1.2, alto=2.3):
    box(nombre + '_marco', x - 0.1, x, u - ancho / 2 - 0.12, u + ancho / 2 + 0.12, 0, alto + 0.12, M['marco'], pieza)
    box(nombre, x - 0.14, x, u - ancho / 2, u + ancho / 2, 0, alto, M['oscuro'], pieza)

def planta(pieza, nombre, x, y, z, r=0.35, grande=False):
    cyl(nombre + '_maceta', (x, y, z + 0.2), r * 0.8, 0.4, 'Z', M['maceta'], pieza, segs=8, r2=r)
    o = cyl(nombre, (x, y, z + 0.4 + r), r * 1.1, r * 1.6, 'Z', M['planta' if azar.random() < 0.5 else 'planta2'], pieza, segs=7, r2=r * 0.4)
    if grande:
        cyl(nombre + '_copa', (x, y, z + 0.4 + r * 2.2), r * 0.9, r * 1.2, 'Z', M['planta2'], pieza, segs=7, r2=r * 0.2)

# Lugares (los mismos que en el código): [x, z, ancho a lo largo de z, alto]. En Blender: Y = -z.
def lugar(x, z, w):
    return x - 3, x + 3, -z - w / 2, -z + w / 2

piezas = []

# ---------- 1. Ladrillo con tanque de agua (x 82, z 30) ----------
p = empty('edificio_ladrillo', edificios); piezas.append(p)
x0, x1, y0, y1 = lugar(82, 30, 9)
caja_edificio(p, 'planta_baja', x0, x1, y0, y1, 0, 3.6, M['pizarra'], cornisa=False)
box('franja', x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, 3.6, 3.85, M['marco'], p)
caja_edificio(p, 'ladrillo', x0, x1, y0, y1, 3.85, 12, M['ladrillo'])
for k in range(10):   # líneas de ladrillo (juntas) en el frente
    box('junta_%d' % k, x0 - 0.03, x0, y0, y1, 4.4 + k * 0.78, 4.46 + k * 0.78, M['ladrillo_oscuro'], p)
fila_ventanas(p, 'lad', '-X', x0, y0 + 0.6, y1 - 0.6, 3, 3, 3.85, 2.6, 1.1, 1.5)
fila_ventanas(p, 'lad', '+Y', y1, x0 + 0.5, x1 - 0.5, 2, 3, 3.85, 2.6, 0.9, 1.4)
fila_ventanas(p, 'lad', '-Y', y0, x0 + 0.5, x1 - 0.5, 2, 3, 3.85, 2.6, 0.9, 1.4)
box('vitrina_a', x0 - 0.1, x0, y0 + 0.5, -30 - 1.0, 0.5, 2.9, M['luz'], p)
box('vitrina_b', x0 - 0.1, x0, -30 + 1.0, y1 - 0.5, 0.5, 2.9, M['vidrio'], p)
puerta(p, 'puerta', x0, -30)
tx, ty, tz = 82.6, -31.4, 12.45   # tanque de agua sobre patas
for sx in (-1, 1):
    for sy in (-1, 1):
        beam('tanque_pata_%d_%d' % (sx, sy), (tx + sx * 1.0, ty + sy * 1.0, tz), (tx + sx * 0.8, ty + sy * 0.8, tz + 2.2), 0.14, M['oscuro'], p)
beam('tanque_cruz_a', (tx - 0.9, ty - 0.9, tz + 0.4), (tx + 0.9, ty + 0.9, tz + 1.8), 0.07, M['oscuro'], p)
beam('tanque_cruz_b', (tx + 0.9, ty - 0.9, tz + 0.4), (tx - 0.9, ty + 0.9, tz + 1.8), 0.07, M['oscuro'], p)
cyl('tanque', (tx, ty, tz + 3.1), 1.1, 1.8, 'Z', M['madera'], p, segs=10)
for k in (0.5, 1.3):
    cyl('tanque_aro_%d' % k, (tx, ty, tz + 2.2 + k), 1.13, 0.08, 'Z', M['oscuro'], p, segs=10)
cyl('tanque_techo', (tx, ty, tz + 4.35), 1.2, 0.7, 'Z', M['madera'], p, segs=10, r2=0.05)
antena(p, 'antena', 81.5, -27.6, 12.45)

# ---------- 2. Torre azul delgada (x 84, z 41) ----------
p = empty('edificio_torre', edificios); piezas.append(p)
x0, x1, y0, y1 = lugar(84, 41, 7)
caja_edificio(p, 'torre', x0, x1, y0, y1, 0, 18, M['azul'])
box('zocalo', x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, 0, 0.6, M['pizarra'], p)
fila_ventanas(p, 'tor', '-X', x0, y0 + 0.5, y1 - 0.5, 3, 6, 1.6, 2.7, 0.9, 1.6)
fila_ventanas(p, 'tor', '+Y', y1, x0 + 0.5, x1 - 0.5, 2, 6, 1.6, 2.7, 0.9, 1.6)
fila_ventanas(p, 'tor', '-Y', y0, x0 + 0.5, x1 - 0.5, 2, 6, 1.6, 2.7, 0.9, 1.6)
puerta(p, 'puerta', x0, -41)
aire(p, 'aire', 84.8, -42.2, 18.45)
antena(p, 'antena', 83.2, -39.6, 18.45, 2.8)

# ---------- 3. Terracota con tiendas y toldos (x 83, z 52) ----------
p = empty('edificio_tiendas', edificios); piezas.append(p)
x0, x1, y0, y1 = lugar(83, 52, 10)
caja_edificio(p, 'tiendas', x0, x1, y0, y1, 0, 3.6, M['crema'], cornisa=False)
box('franja', x0 - 0.18, x1 + 0.18, y0 - 0.18, y1 + 0.18, 3.6, 3.9, M['marco'], p, bevel=0.03)
caja_edificio(p, 'pisos', x0, x1, y0, y1, 3.9, 14, M['terracota'])
for k in range(3):   # franjas entre pisos
    box('linea_piso_%d' % k, x0 - 0.06, x0, y0, y1, 6.4 + k * 2.5, 6.55 + k * 2.5, M['marco'], p)
fila_ventanas(p, 'ter', '-X', x0, y0 + 0.4, y1 - 0.4, 5, 4, 3.9, 2.5, 0.95, 1.45)
fila_ventanas(p, 'ter', '+Y', y1, x0 + 0.5, x1 - 0.5, 2, 4, 3.9, 2.5, 0.9, 1.4)
fila_ventanas(p, 'ter', '-Y', y0, x0 + 0.5, x1 - 0.5, 2, 4, 3.9, 2.5, 0.9, 1.4)
# Dos tiendas con vitrina y toldo de rayas, y una puerta al medio
for t, uc in enumerate((-52 - 3.0, -52 + 3.0)):
    box('vitrina_%d_marco' % t, x0 - 0.08, x0, uc - 1.75, uc + 1.75, 0.4, 3.0, M['marco'], p)
    box('vitrina_%d' % t, x0 - 0.12, x0, uc - 1.6, uc + 1.6, 0.55, 2.85, M['luz'] if t == 0 else M['vidrio'], p)
    for k in range(7):   # toldo inclinado de rayas
        u = uc - 1.9 + k * (3.8 / 7)
        prism('toldo_%d_%d' % (t, k), [(x0, 3.4), (x0 - 1.1, 2.9), (x0 - 1.1, 2.75), (x0, 3.25)], 'Y', u, u + 3.8 / 7,
              M['rojo'] if k % 2 == 0 else M['blanco'], p)
puerta(p, 'puerta', x0, -52, 1.3)

# ---------- 4. Crema escalonado con balcones y plantas (x 85, z 63) ----------
p = empty('edificio_plantas', edificios); piezas.append(p)
x0, x1, y0, y1 = lugar(85, 63, 8)
caja_edificio(p, 'nivel_1', x0, x1, y0, y1, 0, 12, M['crema'])
caja_edificio(p, 'nivel_2', x0 + 1.4, x1, y0 + 1.2, y1, 12.45, 16.5, M['crema'])
caja_edificio(p, 'nivel_3', x0 + 2.6, x1, y0 + 2.6, y1 - 0.4, 16.95, 20, M['crema'])
fila_ventanas(p, 'cre1', '-X', x0, y0 + 0.5, y1 - 0.5, 3, 4, 0, 3.0, 1.0, 1.5)
fila_ventanas(p, 'cre2', '-X', x0 + 1.4, y0 + 1.6, y1 - 0.5, 2, 1, 12.45, 3.0, 1.2, 1.7)
fila_ventanas(p, 'cre3', '-X', x0 + 2.6, y0 + 3.0, y1 - 0.8, 2, 1, 16.95, 3.0, 0.9, 1.3)
fila_ventanas(p, 'cre1', '+Y', y1, x0 + 0.5, x1 - 0.5, 2, 4, 0, 3.0, 0.9, 1.4)
fila_ventanas(p, 'cre1', '-Y', y0, x0 + 0.5, x1 - 0.5, 2, 4, 0, 3.0, 0.9, 1.4)
for piso in (1, 2, 3):   # balcones con baranda y plantas
    z = piso * 3.0 + 0.2
    uc = -63 + (1.1 if piso % 2 else -1.4)
    box('balcon_%d' % piso, x0 - 1.0, x0, uc - 1.3, uc + 1.3, z, z + 0.15, M['marco'], p, bevel=0.03)
    beam('baranda_%d_a' % piso, (x0 - 1.0, uc - 1.3, z + 0.9), (x0 - 1.0, uc + 1.3, z + 0.9), 0.06, M['oscuro'], p)
    for k in range(7):
        u = uc - 1.3 + k * 2.6 / 6
        beam('baranda_%d_p%d' % (piso, k), (x0 - 1.0, u, z + 0.15), (x0 - 1.0, u, z + 0.9), 0.04, M['oscuro'], p)
    planta(p, 'planta_balcon_%d_a' % piso, x0 - 0.5, uc - 0.8, z + 0.15)
    planta(p, 'planta_balcon_%d_b' % piso, x0 - 0.5, uc + 0.7, z + 0.15, 0.28)
for k, (dx, dy) in enumerate(((0.6, 1.8), (0.6, 3.6), (0.7, 5.6))):   # jardín en las terrazas
    planta(p, 'planta_terraza_%d' % k, x0 + dx, y0 + dy, 12.45, 0.45, grande=k == 1)
planta(p, 'planta_techo', x0 + 3.2, y0 + 4.5, 20.45, 0.5, grande=True)
for k in range(3):   # jardineras abajo
    box('jardinera_%d' % k, x0 - 0.8, x0 - 0.1, -63 - 3 + k * 2.4, -63 - 1.6 + k * 2.4, 0, 0.5, M['maceta'], p)
    cyl('jardinera_%d_planta' % k, (x0 - 0.45, -63 - 2.3 + k * 2.4, 0.75), 0.55, 0.5, 'Z', M['planta2'], p, segs=7, r2=0.3)
puerta(p, 'puerta', x0, -63 + 2.8, 1.1)

# ---------- 5. Gris con esquina redonda (x 82, z 73) ----------
p = empty('edificio_esquina', edificios); piezas.append(p)
x0, x1, y0, y1 = lugar(82, 73, 9)
R = 2.6   # radio de la esquina redonda (la que mira a la plaza y a la calle)
def contorno(cr, g=0.0):
    pts = [(x1 + g, y0 - g), (x1 + g, y1 + g), (x0 + cr, y1 + g)]
    for k in range(1, 6):
        a = math.pi / 2 + k * (math.pi / 2) / 6
        pts.append((x0 + cr + math.cos(a) * (cr + g), y1 - cr + math.sin(a) * (cr + g)))
    pts += [(x0 - g, y1 - cr), (x0 - g, y0 - g)]
    return list(reversed(pts))
prism('esquina', contorno(R), 'Z', 0, 11, M['gris'], p)
for k, z in enumerate((3.3, 6.0, 8.7)):   # franjas claras entre pisos
    prism('franja_%d' % k, contorno(R, 0.15), 'Z', z, z + 0.3, M['gris_claro'], p)
prism('cornisa', contorno(R, 0.25), 'Z', 11, 11.4, M['gris_claro'], p)
prism('techo', contorno(R, 0.0), 'Z', 11.4, 11.5, M['techo'], p)
fila_ventanas(p, 'gri', '-X', x0, y0 + 0.5, y1 - R - 0.2, 3, 3, 3.6, 2.7, 1.1, 1.4)
fila_ventanas(p, 'gri', '+Y', y1, x0 + R + 0.2, x1 - 0.5, 2, 3, 3.6, 2.7, 1.0, 1.4)
fila_ventanas(p, 'gri', '-Y', y0, x0 + 0.5, x1 - 0.5, 2, 3, 3.6, 2.7, 0.9, 1.4)
for k in range(2):   # ventanas en la curva (sin marco)
    a = math.pi / 2 + (k + 1) * (math.pi / 2) / 3
    cx, cy = x0 + R + math.cos(a) * (R + 0.02), y1 - R + math.sin(a) * (R + 0.02)
    for piso in range(3):
        z = 4.4 + piso * 2.7
        vid = M['luz'] if azar.random() < 0.45 else M['vidrio']
        o = box('curva_v_%d_%d' % (k, piso), cx - 0.05, cx + 0.05, cy - 0.45, cy + 0.45, z, z + 1.4, vid, p)
        o.data.transform(Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(a - math.pi, 4, 'Z') @ Matrix.Translation((-cx, -cy, 0)))
box('vitrina', x0 - 0.1, x0, y0 + 0.5, y1 - R - 0.3, 0.5, 2.8, M['luz'], p)
puerta(p, 'puerta', x0, -73 + 2.2, 1.1)
aire(p, 'aire', 83.2, -75.2, 11.5)

glb = os.path.join(REPO, 'assets', 'models', 'environment', 'edificios.glb')
os.makedirs(os.path.dirname(glb), exist_ok=True)
exportar_para_juego(edificios, piezas, glb)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO, 'source', 'blender', 'edificios.blend'))
