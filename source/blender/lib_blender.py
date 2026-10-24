# -*- coding: utf-8 -*-
"""
Herramientas COMPARTIDAS para todos los scripts de Blender del juego (los build_*.py).

Cada build_*.py empieza con estas líneas (cópialas de _plantilla.py):

    import bpy, os, sys
    try:  # corriendo desde el editor de texto de Blender
        sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
    except AttributeError:  # corriendo desde la terminal
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import importlib, lib_blender; importlib.reload(lib_blender)
    from lib_blender import *

Así, si cambias algo aquí, todos los modelos lo usan, y no hay que copiar estas funciones en cada script.
El "reload" hace que Blender lea los cambios de este archivo sin tener que cerrarlo.

Qué trae:
  REPO                carpeta del juego (para guardar los .glb en assets/)
  mat(...)            material con color hex (como en el código del juego), brillo y luz
  empty(...)          "pieza" vacía que agrupa partes; el juego busca las piezas por nombre
  box, prism, cyl,    formas básicas: caja, perfil extruido, cilindro/cono,
  beam, text, ico     barra entre dos puntos, letras 3D, esfera facetada (copas de árbol)
  unir(...)           junta varias partes en UN objeto, cada una con su material (para hacer copias)
  mat_colores(...)    material de un solo color por punto, para unir(..., colores=...)
  limpiar()           borra la escena (para empezar de cero)
  exportar_para_juego(root, piezas, glb_path)   exporta el .glb (une las partes por material)
  guardar(root, piezas, ruta_glb, nombre_blend) exporta el .glb y guarda el .blend
     ...con copias=[pieza]: los hijos de esa pieza se exportan como copias (muchos árboles, un solo modelo)
  Vector, Matrix, math, bmesh, random, os       para no tener que importarlos en cada script

Regla: NO copies estas funciones en un build_*.py. Si necesitas una forma nueva que sirva
para varios modelos, agrégala AQUÍ. tools/revisar_blender.py revisa que se cumpla.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

__all__ = ['bpy', 'bmesh', 'math', 'os', 'random', 'Vector', 'Matrix', 'REPO', 'carpeta_repo',
           'hexrgb', 'mat', 'link', 'empty', 'from_bm', 'box', 'prism', 'cyl', 'beam', 'text', 'ico',
           'mat_colores', 'unir', 'limpiar', 'exportar_para_juego', 'guardar']


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

def ico(name, center, r, m, parent, sub=1, sz=1.0):
    """Esfera facetada (low-poly) para copas de árbol y arbustos; sz la aplasta o estira en altura."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    bmesh.ops.scale(bm, vec=(1, 1, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    return from_bm(name, bm, m, parent)

def mat_colores(name, rough=0.85):
    """Material que toma el color de cada punto del modelo (colores pintados con unir(..., colores=...))."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodos = m.node_tree.nodes
    b = nodos['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    c = nodos.new('ShaderNodeVertexColor')
    c.layer_name = 'Color'
    m.node_tree.links.new(c.outputs['Color'], b.inputs['Base Color'])
    return m

def unir(name, partes, parent, colores=None):
    """Junta varias partes (box, cyl, ico...) en UN solo objeto; cada parte conserva su material.
    Sirve para hacer un modelo y luego ponerle copias por todos lados (ver copias= en guardar).
    colores=mat_colores(...): en vez de varios materiales, pinta cada parte con el color de su material
    y usa uno solo. Así el juego dibuja todo el modelo de una vez (mucho más rápido con muchas copias)."""
    mats = []
    bm = bmesh.new()
    for o in partes:
        m = o.data.materials[0]
        if m not in mats:
            mats.append(m)
        for p in o.data.polygons:
            p.material_index = mats.index(m)
        bm.from_mesh(o.data)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if colores is None:
        for m in mats:
            me.materials.append(m)
    else:
        pintura = me.color_attributes.new('Color', 'FLOAT_COLOR', 'CORNER')
        for p in me.polygons:
            col = mats[p.material_index].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
            for i in p.loop_indices:
                pintura.data[i].color = tuple(col)
            p.material_index = 0
        me.materials.append(colores)
    for o in partes:
        datos = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(datos)
    nuevo = link(bpy.data.objects.new(name, me))
    nuevo.parent = parent
    return nuevo

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


# ---------- Escena limpia (borra todo lo de la escena, pero deja abierto el script) ----------
def limpiar():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for datos in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for x in list(datos):
            datos.remove(x)
    for c in list(bpy.data.collections):  # por si un export anterior dejó una colección
        bpy.data.collections.remove(c)


# ---------- Guardar y exportar ----------
def exportar_para_juego(root, piezas, glb_path, copias=()):
    """Exporta una COPIA donde las partes de cada pieza se unen por material
    (muchos menos "draw calls" = más rápido en el navegador). La escena se queda con las partes separadas.
    copias: piezas cuyos hijos son copias de unos pocos modelos (hechas con objeto.copy()). Esas NO se unen:
    el .glb guarda cada modelo una vez y dónde va cada copia, y el juego las dibuja juntas."""
    col = bpy.data.collections.new('para_el_juego')
    bpy.context.scene.collection.children.link(col)
    col.objects.link(root)
    temporales, n_tri = [], 0
    for pieza in copias:
        col.objects.link(pieza)
        hijos = [c for c in pieza.children if c.type == 'MESH']
        for o in hijos:
            col.objects.link(o)
        n_tri += sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in hijos)
        print('   %s: %d copias de %d modelos' % (pieza.name, len(hijos), len({o.data.name for o in hijos})))
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


def guardar(root, piezas, ruta_glb, nombre_blend, copias=()):
    """Exporta assets/<ruta_glb> para el juego y guarda source/blender/<nombre_blend>.
    Ejemplo: guardar(root, [cuerpo, canasta], 'assets/models/props/freidora.glb', 'freidora.blend')
    copias=[pieza] para piezas llenas de copias (como los árboles del bosque): ver exportar_para_juego."""
    glb = os.path.join(REPO, *ruta_glb.split('/'))
    os.makedirs(os.path.dirname(glb), exist_ok=True)
    exportar_para_juego(root, piezas, glb, copias)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO, 'source', 'blender', nombre_blend))
