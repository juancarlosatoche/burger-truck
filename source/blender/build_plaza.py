# -*- coding: utf-8 -*-
"""
Construye la PLAZA donde se estaciona el food truck (estilo cozy low-poly, como truck_exterior_night.jpg).

Pieza que busca el juego:
  - plaza: mesas con sombrilla y sillas, postes con guirnaldas de foquitos, 6 árboles distintos
    (robles, pinos, abedul, arbusto grande), macetas con flores, basurero, marco de la pizarra del menú
    y dos faroles antiguos. Las luces de verdad, el texto del menú, los edificios y la calle los dibuja el código.
La plaza no está escalada: 1 metro aquí = 1 unidad del juego (X = x del juego, Y = -z del juego).

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el modelo. Guarda source/blender/plaza.blend
     y exporta assets/models/environment/plaza.glb (lo que carga el juego).
  3. Si cambias números aquí y lo vuelves a correr, se rearma todo.
     Si prefieres mover cosas a mano en Blender, NO lo vuelvas a correr después:
     exporta tú con File → Export → glTF 2.0 (.glb) al mismo archivo.

Reglas que el juego necesita:
  - Todo cuelga de "escala_juego" (en la plaza la escala es 1: un metro de Blender = un metro del juego).
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
    'madera': mat('madera', 0x9a6232, 0.7),
    'madera_clara': mat('madera_clara', 0xc48a52, 0.65),
    'madera_oscura': mat('madera_oscura', 0x5d3a24, 0.75),
    'metal_oscuro': mat('metal_oscuro', 0x263238, 0.5, 0.4),
    'tela_crema': mat('tela_crema', 0xf1e3c6, 0.9),
    'tela_naranja': mat('tela_naranja', 0xf4a261, 0.9),
    'tela_turquesa': mat('tela_turquesa', 0x2a9d8f, 0.9),
    'cojin': mat('cojin', 0xe76f51, 0.9),
    'cable': mat('cable', 0x222222, 0.6),
    'tronco': mat('tronco', 0x5d4037, 0.9),
    'tronco_blanco': mat('tronco_blanco', 0xe8e2d6, 0.8),
    'hoja1': mat('hoja_oscura', 0x2e6b34, 0.9),
    'hoja2': mat('hoja_media', 0x3b7d3a, 0.9),
    'hoja3': mat('hoja_clara', 0x4a8a3f, 0.9),
    'hoja4': mat('hoja_azulada', 0x2a5e3a, 0.9),
    'pino': mat('pino', 0x24553a, 0.9),
    'maceta': mat('maceta', 0xb5651d, 0.85),
    'arbusto': mat('arbusto', 0x43a047, 0.9),
    'flor_roja': mat('flor_roja', 0xe63946, 0.7),
    'flor_amarilla': mat('flor_amarilla', 0xffd166, 0.7),
    'basurero': mat('basurero', 0x3e6b48, 0.6, 0.3),
    'pizarra_marco': mat('pizarra_marco', 0x6d4c41, 0.7),
    # "luz_": se prenden al anochecer (el juego las controla)
    'foquito': mat('luz_foquitos', 0xfff1b0, 0.4, 0, emit=0xffc65e, strength=1.0),
    'farol': mat('luz_farol', 0xfff1b0, 0.3, 0, emit=0xffd45e, strength=1.0),
}

root = empty('escala_juego')   # la plaza NO está escalada: 1 metro = 1 unidad del juego
fijo = empty('plaza', root)

def P(x, z):
    """Del juego (x, z) a Blender (X, Y): Y = -z."""
    return x, -z

def ico(name, center, r, m, parent, sub=1, sz=1.0):
    """Esfera facetada (low-poly) para copas de árbol y arbustos; sz la aplasta o estira en altura."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    bmesh.ops.scale(bm, vec=(1, 1, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    return from_bm(name, bm, m, parent)

# =====================================================================
# Mesas con sombrilla (mismo lugar que las del código) y sillas con respaldo
# =====================================================================
for k, ((gx, gz), tela) in enumerate((((59, 45), 'tela_naranja'), ((59, 55.5), 'tela_turquesa'))):
    x, y = P(gx, gz)
    cyl('mesa_tapa_%d' % k, (x, y, 1.1), 0.9, 0.07, 'Z', M['madera_clara'], fijo, segs=10)
    cyl('mesa_pie_%d' % k, (x, y, 0.55), 0.06, 1.05, 'Z', M['metal_oscuro'], fijo, segs=6)
    for a in (0, 90):
        r = math.radians(a)
        beam('mesa_base_%d_%d' % (k, a), (x - 0.4 * math.cos(r), y - 0.4 * math.sin(r), 0.03), (x + 0.4 * math.cos(r), y + 0.4 * math.sin(r), 0.03), 0.06, M['metal_oscuro'], fijo)
    # sombrilla: poste de madera y tela facetada de 8 gajos (alternando colores)
    beam('sombrilla_poste_%d' % k, (x, y, 1.1), (x, y, 3.95), 0.06, M['madera'], fijo)
    N, R = 8, 1.9
    for i in range(N):
        a0, a1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
        bm = bmesh.new()   # gajo con un poco de grosor: se ve de arriba y de abajo
        top = [bm.verts.new((x, y, 3.95)), bm.verts.new((x + R * math.cos(a0), y + R * math.sin(a0), 3.25)), bm.verts.new((x + R * math.cos(a1), y + R * math.sin(a1), 3.25))]
        bot = [bm.verts.new((v.co.x, v.co.y, v.co.z - 0.03)) for v in top]
        bm.faces.new(top)
        bm.faces.new(list(reversed(bot)))
        for a, b in ((0, 1), (1, 2), (2, 0)):
            bm.faces.new((top[a], bot[a], bot[b], top[b]))
        from_bm('sombrilla_gajo_%d_%d' % (k, i), bm, M[tela] if i % 2 == 0 else M['tela_crema'], fijo)
    cyl('sombrilla_punta_%d' % k, (x, y, 4.0), 0.07, 0.12, 'Z', M['madera'], fijo, segs=6, r2=0.02)
    # dos sillas donde estaban los bancos del código (x ± 1.3), mirando a la mesa
    for s in (-1, 1):
        cx = x + s * 1.3
        box('silla_asiento_%d_%d' % (k, s), cx - 0.28, cx + 0.28, y - 0.28, y + 0.28, 0.66, 0.74, M['madera_clara'], fijo, bevel=0.015)
        box('silla_cojin_%d_%d' % (k, s), cx - 0.24, cx + 0.24, y - 0.24, y + 0.24, 0.74, 0.78, M['cojin'], fijo, bevel=0.015)
        for i, (dx, dy) in enumerate(((-0.23, -0.23), (0.23, -0.23), (-0.23, 0.23), (0.23, 0.23))):
            box('silla_pata_%d_%d_%d' % (k, s, i), cx + dx - 0.03, cx + dx + 0.03, y + dy - 0.03, y + dy + 0.03, 0.0, 0.66, M['madera'], fijo)
        bx = cx + s * 0.25
        for i, dy in enumerate((-0.23, 0.23)):
            box('silla_poste_%d_%d_%d' % (k, s, i), bx - 0.03, bx + 0.03, y + dy - 0.03, y + dy + 0.03, 0.74, 1.4, M['madera'], fijo)
        for j in range(3):
            box('silla_tabla_%d_%d_%d' % (k, s, j), bx - 0.02, bx + 0.02, y - 0.22, y + 0.22, 0.9 + j * 0.16, 0.98 + j * 0.16, M['madera_clara'], fijo)

# =====================================================================
# Guirnaldas de foquitos en postes de madera (la del código + dos más cruzando la plaza)
# =====================================================================
POSTES = {'a': (57, 42), 'b': (57, 58), 'c': (64.5, 50)}
for nombre, (gx, gz) in POSTES.items():
    x, y = P(gx, gz)
    box('poste_' + nombre, x - 0.08, x + 0.08, y - 0.08, y + 0.08, 0.0, 4.8, M['madera'], fijo)
    box('poste_base_' + nombre, x - 0.16, x + 0.16, y - 0.16, y + 0.16, 0.0, 0.12, M['metal_oscuro'], fijo)
    box('poste_gancho_' + nombre, x - 0.03, x + 0.03, y - 0.03, y + 0.03, 4.8, 4.95, M['metal_oscuro'], fijo)

def guirnalda(nombre, p0, p1, n, colgado=0.7, alto=4.55):
    (x0, y0), (x1, y1) = P(*p0), P(*p1)
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, alto - math.sin(t * math.pi) * colgado))
    for i in range(n):
        beam('%s_cable_%d' % (nombre, i), pts[i], pts[i + 1], 0.025, M['cable'], fijo)
    for i in range(1, n):
        x, y, z = pts[i]
        cyl('%s_socket_%d' % (nombre, i), (x, y, z - 0.06), 0.035, 0.08, 'Z', M['cable'], fijo, segs=6)
        cyl('%s_foco_%d' % (nombre, i), (x, y, z - 0.17), 0.1, 0.16, 'Z', M['foquito'], fijo, segs=6, r2=0.05)

guirnalda('guirnalda_frente', POSTES['a'], POSTES['b'], 16)        # la que ya existía (sobre la fila)
guirnalda('guirnalda_norte', POSTES['a'], POSTES['c'], 10, 0.6)
guirnalda('guirnalda_sur', POSTES['b'], POSTES['c'], 10, 0.6)

# =====================================================================
# Árboles variados (en los lugares de los del código; ninguno igual)
# =====================================================================
def roble(nombre, gx, gz, s, hojas):
    x, y = P(gx, gz)
    cyl(nombre + '_tronco', (x, y, 1.2 * s), 0.2 * s, 2.4 * s, 'Z', M['tronco'], fijo, segs=7, r2=0.14 * s)
    beam(nombre + '_rama', (x, y, 1.8 * s), (x + 0.6 * s, y - 0.3 * s, 2.6 * s), 0.12 * s, M['tronco'], fijo)
    for j, (dx, dy, dz, r) in enumerate(((0, 0, 3.2, 1.3), (0.7, -0.3, 2.9, 0.95), (-0.6, 0.4, 3.0, 1.0), (0.1, 0.2, 3.9, 0.9))):
        ico('%s_copa_%d' % (nombre, j), (x + dx * s, y + dy * s, dz * s), r * s, M[hojas[j % len(hojas)]], fijo)

def pino(nombre, gx, gz, s):
    x, y = P(gx, gz)
    cyl(nombre + '_tronco', (x, y, 0.6 * s), 0.18 * s, 1.2 * s, 'Z', M['tronco'], fijo, segs=6)
    for j, (z, r, h) in enumerate(((1.6, 1.4, 1.6), (2.7, 1.1, 1.4), (3.7, 0.75, 1.2), (4.5, 0.4, 0.9))):
        cyl('%s_capa_%d' % (nombre, j), (x, y, z * s), r * s, h * s, 'Z', M['pino'], fijo, segs=7, r2=0.05 * s)

def abedul(nombre, gx, gz, s):
    x, y = P(gx, gz)
    cyl(nombre + '_tronco', (x, y, 1.6 * s), 0.12 * s, 3.2 * s, 'Z', M['tronco_blanco'], fijo, segs=6, r2=0.08 * s)
    for k in range(3):
        box('%s_mancha_%d' % (nombre, k), x - 0.125 * s, x - 0.11 * s, y - 0.05 * s, y + 0.05 * s, (0.8 + k * 0.7) * s, (0.9 + k * 0.7) * s, M['cable'], fijo)
    ico(nombre + '_copa', (x, y, 3.6 * s), 0.95 * s, M['hoja3'], fijo, sz=1.5)
    ico(nombre + '_copa2', (x + 0.3 * s, y - 0.2 * s, 3.0 * s), 0.6 * s, M['hoja3'], fijo, sz=1.3)

def arbusto_grande(nombre, gx, gz, s):
    x, y = P(gx, gz)
    cyl(nombre + '_tronco', (x, y, 0.8 * s), 0.16 * s, 1.6 * s, 'Z', M['tronco'], fijo, segs=6)
    for j, (dx, dy, dz, r, m) in enumerate(((0, 0, 2.1, 1.2, 'hoja4'), (0.9, 0.2, 1.8, 0.85, 'hoja2'), (-0.8, -0.3, 1.9, 0.9, 'hoja1'), (0.2, -0.7, 2.6, 0.75, 'hoja2'))):
        ico('%s_copa_%d' % (nombre, j), (x + dx * s, y + dy * s, dz * s), r * s, M[m], fijo, sz=0.85)

roble('arbol_1', 64, 44, 0.85, ['hoja1', 'hoja2'])
pino('arbol_2', 65, 56, 1.0)
abedul('arbol_3', 63, 50.5, 1.15)
roble('arbol_4', 67.5, 48, 1.1, ['hoja2', 'hoja3', 'hoja1'])
arbusto_grande('arbol_5', 70, 53, 1.0)
pino('arbol_6', 69, 42.5, 1.25)

# =====================================================================
# Macetas con flores, basurero, pizarra del menú (el texto lo dibuja el código)
# =====================================================================
for k, (gx, gz) in enumerate(((55.4, 53.6), (55.4, 47.2))):
    x, y = P(gx, gz)
    cyl('maceta_%d' % k, (x, y, 0.25), 0.3, 0.5, 'Z', M['maceta'], fijo, segs=8, r2=0.22)
    cyl('maceta_borde_%d' % k, (x, y, 0.5), 0.33, 0.06, 'Z', M['maceta'], fijo, segs=8)
    ico('maceta_arbusto_%d' % k, (x, y, 0.78), 0.34, M['arbusto'], fijo, sz=0.9)
    for j, (dx, dy, col) in enumerate(((0.18, 0.1, 'flor_roja'), (-0.15, 0.17, 'flor_amarilla'), (0.05, -0.22, 'flor_roja'), (-0.2, -0.1, 'flor_amarilla'))):
        ico('maceta_flor_%d_%d' % (k, j), (x + dx, y + dy, 0.98), 0.06, M[col], fijo, sub=1)
x, y = P(55.4, 56.2)
cyl('basurero', (x, y, 0.45), 0.3, 0.9, 'Z', M['basurero'], fijo, segs=8, r2=0.26)
cyl('basurero_tapa', (x, y, 0.93), 0.32, 0.08, 'Z', M['metal_oscuro'], fijo, segs=8, r2=0.28)
cyl('basurero_franja', (x, y, 0.6), 0.285, 0.06, 'Z', M['flor_amarilla'], fijo, segs=8)
# Pizarra del menú: marco de madera y patas (la pizarra con el texto queda en X=55.6)
x, y = P(55.6, 46.6)
box('pizarra_marco_arriba', 55.62, 55.72, -47.38, -45.82, 2.18, 2.28, M['pizarra_marco'], fijo)
box('pizarra_marco_abajo', 55.62, 55.72, -47.38, -45.82, 0.72, 0.82, M['pizarra_marco'], fijo)
box('pizarra_fondo', 55.66, 55.72, -47.3, -45.9, 0.8, 2.2, M['pizarra_marco'], fijo)
for s, yy in ((-1, -47.38), (1, -45.82)):
    box('pizarra_pata_frente_%d' % s, 55.62, 55.72, yy - 0.04 * s - 0.04, yy - 0.04 * s + 0.04, 0.0, 2.3, M['pizarra_marco'], fijo)
    beam('pizarra_pata_atras_%d' % s, (55.75, yy, 2.2), (56.35, yy, 0.0), 0.07, M['pizarra_marco'], fijo)

# =====================================================================
# Faroles de estilo antiguo (mismo lugar que los del código)
# =====================================================================
def farol(nombre, gx, gz, alto, cabeza):
    x, y = P(gx, gz)
    hx, hy = P(*cabeza)
    cyl(nombre + '_base', (x, y, 0.2), 0.18, 0.4, 'Z', M['metal_oscuro'], fijo, segs=8, r2=0.1)
    cyl(nombre + '_poste', (x, y, alto / 2), 0.06, alto, 'Z', M['metal_oscuro'], fijo, segs=8)
    if (hx, hy) != (x, y):
        beam(nombre + '_brazo', (x, y, alto - 0.1), (hx, hy, alto - 0.1), 0.05, M['metal_oscuro'], fijo)
    cz = alto + 0.05
    box(nombre + '_lampara', hx - 0.14, hx + 0.14, hy - 0.14, hy + 0.14, cz - 0.05, cz + 0.33, M['farol'], fijo)
    for i, (dx, dy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        box('%s_marco_%d' % (nombre, i), hx + dx * 0.15 - 0.02, hx + dx * 0.15 + 0.02, hy + dy * 0.15 - 0.02, hy + dy * 0.15 + 0.02, cz - 0.07, cz + 0.35, M['metal_oscuro'], fijo)
    cyl(nombre + '_techo', (hx, hy, cz + 0.42), 0.26, 0.16, 'Z', M['metal_oscuro'], fijo, segs=4, r2=0.04)
    box(nombre + '_piso', hx - 0.19, hx + 0.19, hy - 0.19, hy + 0.19, cz - 0.1, cz - 0.05, M['metal_oscuro'], fijo)

farol('farol_fila', 56.5, 50, 4.8, (56.5, 50))      # el que ilumina a los clientes
farol('farol_calle', 47, 62, 4.35, (47.4, 62))      # el de la calle de atrás

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

blend_path = os.path.join(REPO, 'source', 'blender', 'plaza.blend')
glb_path = os.path.join(REPO, *'assets/models/environment/plaza.glb'.split('/'))
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [fijo], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
