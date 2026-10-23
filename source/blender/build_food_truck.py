# -*- coding: utf-8 -*-
"""
Construye el food truck en Blender (estilo "cozy low-poly": formas facetadas, colores planos).

Cómo usarlo en Blender:
  1. Abre Blender → pestaña "Scripting" → "Open" → elige este archivo → botón ▶ (Run Script).
  2. Se borra la escena y se arma el truck. Puedes moverlo, cambiar colores, etc.
  3. Para el juego: File → Export → glTF 2.0 (.glb) → assets/models/props/food_truck.glb
     (o vuelve a correr este script, que también guarda el .blend y exporta el .glb).

Reglas que el juego necesita (no las cambies sin avisar):
  - Hay 4 piezas: truck_front (cabina), truck_middle (se ESTIRA con "Ampliar"),
    truck_rear (se CORRE hacia atrás con "Ampliar") y truck_sign (letrero).
  - truck_middle mide exactamente de Y = -5.69 a Y = +5.69.
  - Todo cuelga de "escala_juego": el truck se ve aquí en su tamaño real del juego,
    y esa escala lo convierte a las unidades internas del código (×2 ancho/largo, ×1.8 alto).
  - Ejes: +X = lado de la ventanilla, +Y = frente (cabina), Z = arriba.
  - Los materiales que empiezan con "luz_" brillan más de noche (el juego los controla).
  - Los colores están en los mismos números que usa el código (hex), para que se vean igual.
"""
import bpy, bmesh, math, os, sys
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

# ---------- Medidas (metros del juego) ----------
W_IN, W_OUT = 2.81, 2.89      # pared exterior: justo afuera de las paredes de adentro (2.80)
L = 5.69                      # mitad del largo de la caja (truck_middle va de -L a +L)
H = 6.03                      # alto de las paredes
SKIRT, RED_TOP, STRIPE_TOP = 0.25, 1.62, 1.80
WIN_TOP = 3.60                # la ventanilla va de 1.80 a 3.60
DOOR_W, DOOR_H = 1.0, 3.78    # hueco de la puerta trasera (mitad del ancho, alto)
WHEEL_R, WHEEL_Y = 0.62, 3.4

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

def banded_wall(prefix, axis_fixed, fixed0, fixed1, span0, span1, parent, top=H, skip=None):
    """Pared con franjas: faldón oscuro, rojo, línea blanca, crema. axis_fixed='X' → pared lateral."""
    def B(n, z0, z1, m, proud=0.0):
        if axis_fixed == 'X':
            a0, a1 = (fixed0 - proud, fixed1) if fixed0 < 0 else (fixed0, fixed1 + proud)
            return box(n, a0, a1, span0, span1, z0, z1, m, parent)
        a0, a1 = (fixed0 - proud, fixed1) if fixed0 < 0 else (fixed0, fixed1 + proud)
        return box(n, span0, span1, a0, a1, z0, z1, m, parent)
    B(prefix + '_faldon', 0.0, SKIRT, M['oscuro'])
    B(prefix + '_rojo', SKIRT, RED_TOP, M['rojo'])
    B(prefix + '_linea', RED_TOP, STRIPE_TOP, M['blanco'], proud=0.02)
    z_cream = WIN_TOP if skip == 'ventana' else STRIPE_TOP
    B(prefix + '_crema', z_cream, top, M['crema'])

# ---------- Escena limpia (borra todo lo de la escena, pero deja abierto este script) ----------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
for datos in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
    for x in list(datos):
        datos.remove(x)

M = {
    'rojo': mat('pintura_roja', 0xc8102e, 0.35, 0.15),
    'crema': mat('crema', 0xf6ead2, 0.45, 0.05),
    'blanco': mat('blanco', 0xffffff, 0.4),
    'cromo': mat('cromo', 0xdfe4e8, 0.2, 0.9),
    'oscuro': mat('oscuro', 0x1a1a1e, 0.7),
    'llanta': mat('llanta', 0x151515, 0.9),
    'vidrio': mat('vidrio', 0x1e2a38, 0.08, 0.6),
    'madera': mat('madera', 0xa86a3c, 0.6),
    'tablero': mat('tablero_letrero', 0x3b2416, 0.6),
    'letras': mat('luz_letrero', 0xffe7b0, 0.4, 0, emit=0xffc46b, strength=1.0),
    'faros': mat('luz_faros', 0xfffbe8, 0.3, 0, emit=0xfff2c8, strength=1.0),
    'freno': mat('luz_freno', 0xff2a2a, 0.3, 0, emit=0xff1a1a, strength=1.0),
    'toldo_luz': mat('luz_toldo', 0xfff1b0, 0.3, 0, emit=0xffc65e, strength=1.0),
    'pan': mat('pan', 0xe09a4a, 0.6, 0, emit=0x6b3a10, strength=1.0),
    'carne': mat('carne', 0x5a2e1a, 0.7),
    'queso': mat('queso', 0xffc531, 0.5),
    'lechuga': mat('lechuga', 0x4caf50, 0.6),
    'amarillo': mat('amarillo', 0xffd166, 0.45),
}

root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # metros del juego → unidades internas del código
front = empty('truck_front', root)
middle = empty('truck_middle', root)
rear = empty('truck_rear', root)
sign = empty('truck_sign', root)

# =====================================================================
# truck_middle: la caja de la cocina (se estira con "Ampliar")
# =====================================================================
banded_wall('lado_atras', 'X', -W_OUT, -W_IN, -L, L, middle)                 # lado sin ventana
banded_wall('lado_ventana', 'X', W_IN, W_OUT, -L, L, middle, skip='ventana')  # lado de la ventanilla
# Marco de la ventanilla
box('marco_arriba', W_OUT, W_OUT + 0.06, -L, L, WIN_TOP - 0.08, WIN_TOP + 0.04, M['cromo'], middle)
for s in (-1, 1):
    y0, y1 = (-L, -L + 0.12) if s < 0 else (L - 0.12, L)
    box('marco_lado_%d' % s, W_IN, W_OUT + 0.06, y0, y1, STRIPE_TOP, WIN_TOP, M['cromo'], middle)
# Repisa de madera afuera (donde se apoyan los clientes)
box('repisa', W_OUT, W_OUT + 0.55, -L + 0.2, L - 0.2, STRIPE_TOP - 0.06, STRIPE_TOP + 0.06, M['madera'], middle, bevel=0.025)
for y in (-3.6, 0.0, 3.6):
    prism('soporte_repisa_%d' % int(y), [(W_OUT, STRIPE_TOP - 0.06), (W_OUT + 0.45, STRIPE_TOP - 0.06), (W_OUT, STRIPE_TOP - 0.5)],
          'Y', y - 0.05, y + 0.05, M['cromo'], middle)
# Toldo con bisagra (sube hacia afuera) y sus brazos
t0, t1 = (W_OUT + 0.02, WIN_TOP + 0.12), (W_OUT + 2.1, WIN_TOP + 0.62)
tdx, tdz = t1[0] - t0[0], t1[1] - t0[1]
tl = math.hypot(tdx, tdz)
nx, nz = -tdz / tl * 0.09, tdx / tl * 0.09
prism('toldo', [t0, t1, (t1[0] + nx, t1[1] + nz), (t0[0] + nx, t0[1] + nz)], 'Y', -L + 0.05, L - 0.05, M['crema'], middle)
prism('toldo_borde', [(t1[0] - 0.02, t1[1] - 0.12), (t1[0] + 0.06, t1[1] - 0.1), (t1[0] + nx + 0.06, t1[1] + nz + 0.02), (t1[0], t1[1])],
      'Y', -L + 0.05, L - 0.05, M['rojo'], middle)
box('toldo_luces', W_OUT + 0.05, W_OUT + 0.17, -L + 0.3, L - 0.3, WIN_TOP - 0.02, WIN_TOP + 0.03, M['toldo_luz'], middle)
for s in (-1, 1):
    beam('brazo_toldo_%d' % s, (W_OUT + 0.05, s * (L - 0.35), STRIPE_TOP + 0.3), (t1[0] - 0.1, s * (L - 0.35), t1[1] - 0.05), 0.06, M['cromo'], middle)
# Techo: placa blanca + corona facetada crema
box('techo', -W_OUT - 0.08, W_OUT + 0.08, -L, L, H, H + 0.1, M['blanco'], middle)
CROWN = [(-W_OUT - 0.08, H + 0.1), (W_OUT + 0.08, H + 0.1), (W_OUT - 0.35, H + 0.42), (-W_OUT + 0.35, H + 0.42)]
prism('techo_corona', CROWN, 'Y', -L, L, M['crema'], middle)
box('aire_acondicionado', -1.3, -0.2, -3.6, -1.4, H + 0.42, H + 0.85, M['cromo'], middle, bevel=0.06)
for i in range(4):
    box('rejilla_aire_%d' % i, -1.31, -0.19, -3.4 + i * 0.5, -3.3 + i * 0.5, H + 0.5, H + 0.78, M['oscuro'], middle)

# =====================================================================
# truck_front: cabina, pared delantera, ruedas de adelante
# =====================================================================
banded_wall('frente', 'Y', 5.61, L, -W_OUT, W_OUT, front)
prism('techo_corona_frente', CROWN, 'Y', L, L + 0.08, M['crema'], front)
box('techo_frente', -W_OUT - 0.08, W_OUT + 0.08, L, L + 0.08, H, H + 0.1, M['blanco'], front)
CW = 2.72  # mitad del ancho de la cabina
prism('cabina_abajo', [(L, SKIRT), (8.2, SKIRT), (8.35, 0.55), (8.35, 1.95), (8.15, 2.2), (L, 2.2)], 'X', -CW, CW, M['rojo'], front)
prism('cabina_arriba', [(L, 2.2), (7.57, 2.2), (7.0, 3.85), (6.8, 4.02), (L, 4.02)], 'X', -CW, CW, M['crema'], front)
box('cabina_linea', -CW - 0.02, CW + 0.02, L, 8.37, RED_TOP, STRIPE_TOP, M['blanco'], front)
box('cabina_faldon', -CW + 0.02, CW - 0.02, L, 8.2, 0.0, SKIRT, M['oscuro'], front)
# Parabrisas inclinado
d = Vector((7.0 - 7.57, 3.85 - 2.2)).normalized()
n = Vector((d.y, -d.x)) * 0.02
a, b = Vector((7.57, 2.2)) + d * 0.12, Vector((7.0, 3.85)) - d * 0.12
prism('parabrisas', [tuple(a), tuple(b), tuple(b + n), tuple(a + n)], 'X', -CW + 0.18, CW - 0.18, M['vidrio'], front)
# Ventanas laterales, manijas y espejos
for s in (-1, 1):
    x0, x1 = (CW, CW + 0.02) if s > 0 else (-CW - 0.02, -CW)
    prism('ventana_cabina_%d' % s, [(5.9, 2.42), (7.35, 2.42), (6.92, 3.62), (5.9, 3.62)], 'X', x0, x1, M['vidrio'], front)
    box('puerta_linea_%d' % s, x0, x1 + 0.005 * s, 5.82, 5.86, SKIRT + 0.1, 3.75, M['oscuro'], front)
    box('manija_%d' % s, x0 - 0.02 * (s < 0), x1 + 0.02 * (s > 0), 6.0, 6.3, 2.05, 2.12, M['cromo'], front)
    beam('brazo_espejo_%d' % s, (s * CW, 7.3, 2.6), (s * (CW + 0.35), 7.3, 2.75), 0.05, M['oscuro'], front)
    box('espejo_%d' % s, s * (CW + 0.32) - 0.05, s * (CW + 0.32) + 0.05, 7.15, 7.45, 2.6, 3.25, M['oscuro'], front, bevel=0.02)
# Frente: parrilla, faros, parachoques
box('parrilla', -1.05, 1.05, 8.35, 8.39, 0.75, 1.6, M['cromo'], front)
for i in range(4):
    box('parrilla_raya_%d' % i, -1.0, 1.0, 8.39, 8.41, 0.85 + i * 0.2, 0.92 + i * 0.2, M['oscuro'], front)
for s in (-1, 1):
    cyl('faro_%d' % s, (s * 1.85, 8.37, 1.25), 0.24, 0.06, 'Y', M['faros'], front, segs=10)
    cyl('aro_faro_%d' % s, (s * 1.85, 8.355, 1.25), 0.3, 0.05, 'Y', M['cromo'], front, segs=10)
    box('direccional_%d' % s, s * 2.35 - 0.12, s * 2.35 + 0.12, 8.35, 8.39, 1.15, 1.35, M['toldo_luz'], front)
box('parachoques', -CW - 0.05, CW + 0.05, 8.3, 8.6, 0.28, 0.62, M['cromo'], front, bevel=0.05)
# Logo redondo en el lado sin ventana (no se estira porque va en la pieza del frente)
LX = -W_OUT
cyl('logo_disco', (LX - 0.02, 2.6, 3.9), 1.05, 0.04, 'X', M['amarillo'], front, segs=16)
cyl('logo_borde', (LX - 0.01, 2.6, 3.9), 1.15, 0.03, 'X', M['rojo'], front, segs=16)
cyl('logo_pan_abajo', (LX - 0.08, 2.6, 3.45), 0.62, 0.08, 'X', M['pan'], front, segs=12, r2=None)
box('logo_carne', LX - 0.13, LX - 0.04, 1.95, 3.25, 3.62, 3.82, M['carne'], front, bevel=0.03)
box('logo_queso', LX - 0.15, LX - 0.04, 2.0, 3.2, 3.82, 3.9, M['queso'], front)
box('logo_lechuga', LX - 0.14, LX - 0.04, 1.92, 3.28, 3.9, 3.98, M['lechuga'], front)
prism('logo_pan_arriba', [(1.92, 3.98), (3.28, 3.98), (3.15, 4.3), (2.85, 4.5), (2.35, 4.5), (2.05, 4.3)], 'X', LX - 0.15, LX - 0.04, M['pan'], front)
box('logo_pan_base', LX - 0.13, LX - 0.04, 1.98, 3.22, 3.3, 3.55, M['pan'], front, bevel=0.04)

# =====================================================================
# Ruedas con guardabarros (las de atrás van en truck_rear para correrse)
# =====================================================================
def wheels(parent, y, tag):
    for s in (-1, 1):
        x = s * (W_OUT + 0.08)
        cyl('llanta_%s_%d' % (tag, s), (x, y, WHEEL_R), WHEEL_R, 0.42, 'X', M['llanta'], parent, segs=12)
        cyl('rin_%s_%d' % (tag, s), (x + s * 0.05, y, WHEEL_R), 0.32, 0.36, 'X', M['cromo'], parent, segs=8)
        cyl('tapa_%s_%d' % (tag, s), (x + s * 0.1, y, WHEEL_R), 0.12, 0.3, 'X', M['oscuro'], parent, segs=6)
        # guardabarros facetado (medio octágono)
        R0, R1 = WHEEL_R + 0.12, WHEEL_R + 0.3
        angs = [math.radians(a) for a in (0, 36, 72, 108, 144, 180)]
        for k in range(5):
            a0, a1 = angs[k], angs[k + 1]
            pts = [(y + R0 * math.cos(a0), WHEEL_R + R0 * math.sin(a0)), (y + R1 * math.cos(a0), WHEEL_R + R1 * math.sin(a0)),
                   (y + R1 * math.cos(a1), WHEEL_R + R1 * math.sin(a1)), (y + R0 * math.cos(a1), WHEEL_R + R0 * math.sin(a1))]
            xa, xb = (W_OUT - 0.01, W_OUT + 0.32) if s > 0 else (-W_OUT - 0.32, -W_OUT + 0.01)
            prism('guardabarros_%s_%d_%d' % (tag, s, k), pts, 'X', xa, xb, M['rojo'], parent)

wheels(front, WHEEL_Y, 'adelante')

# =====================================================================
# truck_rear: pared trasera con hueco de puerta, luces, ruedas de atrás
# =====================================================================
for s in (-1, 1):
    x0, x1 = (DOOR_W + 0.02, W_OUT) if s > 0 else (-W_OUT, -DOOR_W - 0.02)
    banded_wall('atras_%d' % s, 'Y', -L, -5.61, x0, x1, rear)
box('atras_dintel', -DOOR_W - 0.02, DOOR_W + 0.02, -L, -5.61, DOOR_H + 0.02, H, M['crema'], rear)
box('marco_puerta_arriba', -DOOR_W - 0.08, DOOR_W + 0.08, -L - 0.05, -L, DOOR_H, DOOR_H + 0.1, M['cromo'], rear)
for s in (-1, 1):
    box('marco_puerta_%d' % s, s * DOOR_W - 0.08 * (s < 0) - 0.02 * (s > 0), s * DOOR_W + 0.08 * (s > 0) + 0.02 * (s < 0),
        -L - 0.05, -L, 0.0, DOOR_H + 0.1, M['cromo'], rear)
    box('luz_trasera_%d' % s, s * 2.45 - 0.18, s * 2.45 + 0.18, -L - 0.05, -L, 1.0, 1.45, M['freno'], rear, bevel=0.02)
    box('parachoques_atras_%d' % s, s * 1.75 - 0.6, s * 1.75 + 0.6, -L - 0.25, -L, 0.28, 0.58, M['cromo'], rear, bevel=0.04)
box('escalon', -DOOR_W, DOOR_W, -L - 0.45, -L, 0.0, 0.12, M['cromo'], rear)
prism('techo_corona_atras', CROWN, 'Y', -L - 0.08, -L, M['crema'], rear)
box('techo_atras', -W_OUT - 0.08, W_OUT + 0.08, -L - 0.08, -L, H, H + 0.1, M['blanco'], rear)
# Esquineras (tapan la unión de las paredes)
for sx in (-1, 1):
    box('esquina_atras_%d' % sx, sx * W_OUT - 0.06, sx * W_OUT + 0.06, -L - 0.06, -L + 0.06, SKIRT, H, M['crema'], rear)
    box('esquina_frente_%d' % sx, sx * W_OUT - 0.06, sx * W_OUT + 0.06, L - 0.06, L + 0.06, SKIRT, H, M['crema'], front)
wheels(rear, -WHEEL_Y, 'atras')

# =====================================================================
# truck_sign: letrero "BURGER TRUCK" con hamburguesa encima
# =====================================================================
SX = 2.25                      # cerca del borde del techo, mirando a la fila
SZ0, SZ1 = H + 0.7, H + 2.35
for y in (-2.4, 2.4):
    box('poste_letrero_%d' % int(y), SX - 0.25, SX - 0.1, y - 0.07, y + 0.07, H + 0.1, SZ0 + 0.1, M['oscuro'], sign)
box('tablero', SX - 0.12, SX + 0.06, -3.3, 3.3, SZ0, SZ1, M['tablero'], sign, bevel=0.06)
box('tablero_borde', SX + 0.02, SX + 0.09, -3.2, 3.2, SZ0 + 0.08, SZ0 + 0.14, M['letras'], sign)
text('letras_burger', 'BURGER', 1.0, (SX + 0.12, 0.0, SZ0 + 1.2), M['letras'], sign, extrude=0.05)
text('letras_truck', 'TRUCK', 0.62, (SX + 0.12, 0.0, SZ0 + 0.42), M['letras'], sign, extrude=0.05)
BZ = SZ1 + 0.05                # hamburguesa
cyl('hamb_pan_abajo', (SX - 0.03, 0, BZ + 0.12), 0.75, 0.24, 'Z', M['pan'], sign, segs=12, r2=0.68)
cyl('hamb_carne', (SX - 0.03, 0, BZ + 0.33), 0.8, 0.18, 'Z', M['carne'], sign, segs=12)
box('hamb_queso', SX - 0.65, SX + 0.6, -0.62, 0.62, BZ + 0.42, BZ + 0.47, M['queso'], sign)
cyl('hamb_lechuga', (SX - 0.03, 0, BZ + 0.5), 0.86, 0.06, 'Z', M['lechuga'], sign, segs=9)
cyl('hamb_pan_arriba1', (SX - 0.03, 0, BZ + 0.66), 0.8, 0.26, 'Z', M['pan'], sign, segs=12, r2=0.62)
cyl('hamb_pan_arriba2', (SX - 0.03, 0, BZ + 0.9), 0.62, 0.22, 'Z', M['pan'], sign, segs=12, r2=0.3)

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

blend_path = os.path.join(REPO, 'source', 'blender', 'food_truck.blend')
glb_path = os.path.join(REPO, 'assets', 'models', 'props', 'food_truck.glb')
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
exportar_para_juego(root, [front, middle, rear, sign], glb_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)   # el .blend guarda cada parte con su nombre
