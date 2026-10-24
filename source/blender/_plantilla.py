# -*- coding: utf-8 -*-
"""
PLANTILLA para un modelo nuevo. Cópiala como build_<nombre>.py y cambia lo que dice CAMBIA.

Construye <QUÉ ES> (estilo cozy low-poly), siguiendo reference/props/<imagen>.jpg.   ← CAMBIA

Piezas que busca el juego:                                                          ← CAMBIA
  - <nombre_pieza>: <qué es y si se mueve>

Ejes: +X = <hacia dónde>, Y = -z del juego, Z = arriba.                              ← CAMBIA
Cómo usarlo: Blender → pestaña "Scripting" → "Open" → este archivo → ▶ (Run Script).
Desde la terminal: python3 build_<nombre>.py   (con el módulo bpy instalado)
"""
# ---------- Herramientas compartidas (NO las copies aquí: viven en lib_blender.py) ----------
import bpy, os, sys
try:  # corriendo desde el editor de texto de Blender
    sys.path.insert(0, os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath)))
except AttributeError:  # corriendo desde la terminal
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, lib_blender; importlib.reload(lib_blender)
from lib_blender import *

limpiar()
M = {   # los colores usan los mismos números (hex) que el código del juego         ← CAMBIA
    'acero': mat('acero', 0xc4cacf, 0.32, 0.8),
    'luz': mat('luz_ejemplo', 0xffb347, 0.3, 0, emit=0xff8a1e, strength=2.0),  # "luz_": brilla más de noche
}
root = empty('escala_juego')
root.scale = (0.5, 0.5, 1 / 1.8)   # dentro del truck; en la plaza o la casa usa (1, 1, 1)  ← CAMBIA
pieza = empty('nombre_pieza', root)                                                  # ← CAMBIA

box('ejemplo', -0.2, 0.2, -0.2, 0.2, 0, 0.3, M['acero'], pieza, bevel=0.01)          # ← CAMBIA

guardar(root, [pieza], 'assets/models/props/nombre.glb', 'nombre.blend')             # ← CAMBIA
