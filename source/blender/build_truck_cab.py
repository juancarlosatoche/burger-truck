# -*- coding: utf-8 -*-
"""
Construye la CABINA por dentro del food truck, para manejar en primera persona (como driving_first_person.jpg).

Piezas que busca el juego:
  - cab_static: tablero con velocímetro, radio, consola, asientos, paneles de puertas, viseras,
    espejo retrovisor con el ambientador de hamburguesa.
  - cab_volante: el volante (plano, mirando al conductor). El código lo inclina y lo gira al doblar.
El conductor va a la izquierda: sus ojos están en (-1.35, 5.95, 3.45) en metros del juego.

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el modelo. Guarda source/blender/truck_cab.blend
     y exporta assets/models/props/truck_cab.glb (lo que carga el juego).
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
    'tablero': mat('tablero_cabina', 0x3a3f47, 0.6, 0.1),
    'tablero_claro': mat('tablero_claro', 0x5a616b, 0.55, 0.1),
    'oscuro': mat('oscuro', 0x1a1a1e, 0.7),
    'piso': mat('piso_cabina', 0x26292e, 0.9),
    'asiento': mat('asiento', 0x2f3e52, 0.85),
    'cromo': mat('cromo', 0xdfe4e8, 0.18, 0.9),
    'espejo': mat('espejo', 0xb8c4cc, 0.05, 0.95),
    'crema': mat('crema', 0xf6ead2, 0.45, 0.05),
    'rojo': mat('rojo', 0xd90429, 0.4),
    'pan': mat('pan', 0xe09a4a, 0.6),
    'carne': mat('carne', 0x5a2e1a, 0.7),
    'lechuga': mat('lechuga', 0x4caf50, 0.6),
    'queso': mat('queso', 0xffc531, 0.5),
    'brillo_reloj': mat('brillo_reloj', 0xf4f8ff, 0.3, 0, emit=0xcfe6ff, strength=1.0),
    'brillo_radio': mat('brillo_radio', 0x1d3557, 0.3, 0, emit=0x4fd1ff, strength=1.0),
    'brillo_techo': mat('brillo_techo', 0xfff6e0, 0.3, 0, emit=0xffe2b0, strength=1.0),
}

root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # igual que el truck de afuera
fijo = empty('cab_static', root)     # tablero, asientos, espejo, ambientador
volante = empty('cab_volante', root) # el volante: el código lo inclina y lo hace girar al doblar

# ---------- Medidas de la cabina (metros del juego) ----------
# Piso de la cabina Z=2.2, techo Z=3.85, ancho X=±2.68, de Y=5.69 (pared de la cocina) a Y≈7.5 (parabrisas)
# El conductor va a la IZQUIERDA (X negativo): ojos en (-1.35, 5.95, 3.45)
DRV = -1.35
FLOOR, ROOF = 2.2, 3.85

# Piso y tablero
box('piso', -2.66, 2.66, 5.7, 7.45, FLOOR, FLOOR + 0.03, M['piso'], fijo)
prism('tablero', [(6.85, FLOOR), (7.47, FLOOR), (7.36, 2.48), (7.02, 2.55), (6.85, 2.5)], 'X', -2.66, 2.66, M['tablero'], fijo)
box('tablero_franja', -2.66, 2.66, 6.83, 6.86, 2.42, 2.46, M['cromo'], fijo)
# Visera de los relojes, velocímetro y gasolina (detrás del volante)
prism('visera_relojes', [(6.85, 2.48), (7.0, 2.48), (7.0, 2.6), (6.93, 2.6)], 'X', DRV - 0.4, DRV + 0.4, M['tablero'], fijo)
cyl('velocimetro', (DRV - 0.2, 6.84, 2.33), 0.12, 0.03, 'Y', M['brillo_reloj'], fijo, segs=14)
cyl('velocimetro_aro', (DRV - 0.2, 6.845, 2.33), 0.14, 0.02, 'Y', M['cromo'], fijo, segs=14)
beam('velocimetro_aguja', (DRV - 0.2, 6.82, 2.33), (DRV - 0.29, 6.82, 2.4), 0.015, M['rojo'], fijo)
cyl('gasolina', (DRV + 0.2, 6.84, 2.33), 0.08, 0.03, 'Y', M['brillo_reloj'], fijo, segs=12)
beam('gasolina_aguja', (DRV + 0.2, 6.82, 2.33), (DRV + 0.24, 6.82, 2.39), 0.012, M['rojo'], fijo)
# Radio y consola del centro
box('radio', -0.3, 0.3, 6.83, 6.85, 2.26, 2.4, M['brillo_radio'], fijo)
for i in range(4):
    box('radio_boton_%d' % i, -0.27 + i * 0.16, -0.17 + i * 0.16, 6.82, 6.84, 2.21, 2.24, M['cromo'], fijo)
box('consola', -0.35, 0.35, 6.3, 6.85, FLOOR, 2.42, M['tablero'], fijo, bevel=0.03)
beam('palanca', (0.0, 6.55, 2.42), (0.0, 6.5, 2.7), 0.04, M['cromo'], fijo)
cyl('palanca_pomo', (0.0, 6.5, 2.73), 0.06, 0.08, 'Z', M['oscuro'], fijo, segs=8)
# Guantera (lado del copiloto)
box('guantera', 0.7, 1.9, 6.835, 6.85, 2.26, 2.4, M['tablero_claro'], fijo)
box('guantera_manija', 1.2, 1.4, 6.825, 6.835, 2.35, 2.38, M['cromo'], fijo)
# Columna del volante (el volante mismo va en "cab_volante")
WC = Vector((DRV, 6.62, 2.62))   # centro del volante
beam('columna', (DRV, 6.95, 2.35), (DRV, WC.y + 0.05, WC.z - 0.03), 0.09, M['oscuro'], fijo)

# Asientos (el del conductor queda detrás de la cámara)
for nombre, xc in (('asiento_conductor', DRV), ('asiento_copiloto', 1.3)):
    box(nombre, xc - 0.6, xc + 0.6, 5.75, 6.35, FLOOR, 2.62, M['asiento'], fijo, bevel=0.05)
    box(nombre + '_espalda', xc - 0.6, xc + 0.6, 5.72, 5.92, 2.62, 3.55, M['asiento'], fijo, bevel=0.05)
    box(nombre + '_cabecera', xc - 0.35, xc + 0.35, 5.73, 5.9, 3.55, 3.78, M['asiento'], fijo, bevel=0.04)
# Paneles de las puertas (por dentro) y apoyabrazos
for s in (-1, 1):
    x0, x1 = (2.6, 2.67) if s > 0 else (-2.67, -2.6)
    box('panel_puerta_%d' % s, x0, x1, 5.75, 7.4, FLOOR, 2.42, M['tablero'], fijo)
    xa, xb = (2.45, 2.6) if s > 0 else (-2.6, -2.45)
    box('apoyabrazos_%d' % s, xa, xb, 6.0, 6.9, 2.5, 2.58, M['tablero_claro'], fijo, bevel=0.02)
# Techo: luz, viseras
box('luz_techo', -0.3, 0.3, 6.2, 6.5, ROOF - 0.03, ROOF, M['brillo_techo'], fijo)
for s, (x0, x1) in ((-1, (-2.3, -0.4)), (1, (0.4, 2.3))):
    box('visera_%d' % s, x0, x1, 6.7, 6.98, ROOF - 0.07, ROOF - 0.02, M['crema'], fijo, bevel=0.01)
# Espejo retrovisor con ambientador de hamburguesa 🍔 (pegado al techo: así no tapan el camino)
MX = -0.45
beam('espejo_brazo', (MX, 6.92, ROOF), (MX, 6.92, 3.8), 0.04, M['oscuro'], fijo)
box('espejo_marco', MX - 0.3, MX + 0.3, 6.86, 6.94, 3.68, 3.82, M['oscuro'], fijo, bevel=0.02)
box('espejo_vidrio', MX - 0.27, MX + 0.27, 6.855, 6.86, 3.7, 3.8, M['espejo'], fijo)
beam('ambientador_hilo', (MX, 6.9, 3.68), (MX, 6.9, 3.62), 0.008, M['oscuro'], fijo)
AZ = 3.5   # arriba, para que no tape el camino
cyl('ambientador_pan_abajo', (MX, 6.9, AZ), 0.07, 0.03, 'Y', M['pan'], fijo, segs=10)
box('ambientador_carne', MX + (-0.075), MX + 0.075, 6.885, 6.915, AZ + 0.02, AZ + 0.05, M['carne'], fijo)
box('ambientador_queso', MX + (-0.07), MX + 0.07, 6.882, 6.918, AZ + 0.05, AZ + 0.065, M['queso'], fijo)
box('ambientador_lechuga', MX + (-0.08), MX + 0.08, 6.884, 6.916, AZ + 0.065, AZ + 0.08, M['lechuga'], fijo)
prism('ambientador_pan_arriba', [(MX - 0.075, AZ + 0.08), (MX + 0.075, AZ + 0.08), (MX + 0.05, AZ + 0.13), (MX - 0.05, AZ + 0.13)], 'Y', 6.885, 6.915, M['pan'], fijo)

# =====================================================================
# Volante: plano (mirando al conductor), centrado en su empty; el código lo inclina y lo gira
# =====================================================================
partes = []
R, N = 0.3, 12
for i in range(N):   # aro hecho de 12 tramos (low-poly)
    a0, a1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
    p0 = (WC.x + R * math.cos(a0), WC.y, WC.z + R * math.sin(a0))
    p1 = (WC.x + R * math.cos(a1), WC.y, WC.z + R * math.sin(a1))
    partes.append(beam('volante_aro_%d' % i, p0, p1, 0.055, M['oscuro'], volante))
for k, ang in enumerate((90, 210, 330)):   # 3 rayos
    a = math.radians(ang)
    partes.append(beam('volante_rayo_%d' % k, (WC.x, WC.y, WC.z), (WC.x + R * math.cos(a), WC.y, WC.z + R * math.sin(a)), 0.04, M['tablero_claro'], volante))
partes.append(cyl('volante_centro', (WC.x, WC.y - 0.01, WC.z), 0.1, 0.06, 'Y', M['tablero_claro'], volante, segs=10))
partes.append(cyl('volante_logo', (WC.x, WC.y - 0.045, WC.z), 0.05, 0.01, 'Y', M['rojo'], volante, segs=8))
for o in partes:
    o.data.transform(Matrix.Translation(-WC))   # relativo al centro del volante
volante.location = WC

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

blend_path = os.path.join(REPO, 'source', 'blender', 'truck_cab.blend')
glb_path = os.path.join(REPO, *'assets/models/props/truck_cab.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo, volante], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
