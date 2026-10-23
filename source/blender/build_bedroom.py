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

blend_path = os.path.join(REPO, 'source', 'blender', 'bedroom.blend')
glb_path = os.path.join(REPO, *'assets/models/environment/bedroom.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo, colchon, pantalla], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
