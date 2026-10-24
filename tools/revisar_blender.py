# -*- coding: utf-8 -*-
"""
Revisa que TODOS los scripts de Blender (source/blender/build_*.py) usen las herramientas compartidas
de source/blender/lib_blender.py, en vez de tener su propia copia.

Uso:  python3 tools/revisar_blender.py
Sale con error (código 1) si algo no cumple. GitHub lo corre en cada pull request
(.github/workflows/revisar.yml), así que un script que no cumpla no puede pasar sin que se note.

Qué revisa en cada build_*.py:
  1. que tenga la línea  from lib_blender import *
  2. que NO vuelva a definir una herramienta que ya está en lib_blender (box, mat, exportar_para_juego...)
  3. que NO exporte por su cuenta (bpy.ops.export_scene.gltf solo va en lib_blender: usa guardar() o exportar_para_juego())
  4. que el archivo sea Python válido
"""
import ast, glob, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, '..', 'source', 'blender')


def herramientas_compartidas():
    arbol = ast.parse(open(os.path.join(CARPETA, 'lib_blender.py'), encoding='utf-8').read())
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, 'id', '') == '__all__' for t in nodo.targets):
            return set(ast.literal_eval(nodo.value))
    sys.exit('lib_blender.py no tiene __all__')


def revisar(ruta, compartidas):
    nombre = os.path.basename(ruta)
    texto = open(ruta, encoding='utf-8').read()
    try:
        arbol = ast.parse(texto)
    except SyntaxError as e:
        return [f'{nombre}: no es Python válido (línea {e.lineno}): {e.msg}']
    errores = []
    importa = any(isinstance(n, ast.ImportFrom) and n.module == 'lib_blender' and any(a.name == '*' for a in n.names)
                  for n in arbol.body)
    if not importa:
        errores.append(f'{nombre}: falta "from lib_blender import *" (copia el comienzo de _plantilla.py)')
    for n in ast.walk(arbol):
        if isinstance(n, ast.FunctionDef) and n.name in compartidas:
            errores.append(f'{nombre}, línea {n.lineno}: vuelve a definir "{n.name}", que ya está en lib_blender.py. Bórrala y usa la compartida.')
        if isinstance(n, ast.Attribute) and n.attr == 'gltf' and 'export_scene' in ast.unparse(n):
            errores.append(f'{nombre}, línea {n.lineno}: exporta por su cuenta. Usa guardar() o exportar_para_juego() de lib_blender.py.')
    return errores


def main():
    compartidas = herramientas_compartidas()
    scripts = sorted(glob.glob(os.path.join(CARPETA, 'build_*.py')))
    errores = [e for s in scripts for e in revisar(s, compartidas)]
    for e in errores:
        print('❌', e)
    if errores:
        sys.exit(1)
    print(f'✅ {len(scripts)} scripts de Blender usan lib_blender.py')


if __name__ == '__main__':
    main()
