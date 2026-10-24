# -*- coding: utf-8 -*-
"""
Revisa que docs/MAPA.md siga correcto con respecto a index.html.

Uso:  python3 tools/revisar_mapa.py
Sale con error (código 1) si:
  1. el mapa nombra una función `nombre()` que ya no existe en index.html
  2. el mapa nombra una constante `NOMBRE` que ya no existe (const NOMBRE / let NOMBRE)
  3. el mapa nombra un «landmark» (un comentario) que ya no está en index.html
  4. hay una función de primer nivel en index.html que el mapa no nombra (¡agrégala donde corresponda!)
GitHub lo corre en cada pull request (.github/workflows/revisar.yml).
"""
import os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
codigo = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
mapa = open(os.path.join(REPO, 'docs', 'MAPA.md'), encoding='utf-8').read()

# Todas las funciones (también las de adentro de init() y las flecha: const nombre = (...) =>)
funciones_codigo = set(re.findall(r'^\s*(?:async\s+)?function\s+(\w+)\s*\(', codigo, re.M))
funciones_codigo |= set(re.findall(r'\b(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>', codigo))
# Las que el mapa DEBE nombrar: solo las de primer nivel (8 espacios), no las ayudantes de adentro de init()
funciones_principales = set(re.findall(r'^ {8}(?:async\s+)?function\s+(\w+)\s*\(', codigo, re.M))
funciones_mapa = set(re.findall(r'`(\w+)\(\)`', mapa))
constantes_mapa = set(re.findall(r'`([A-Z][A-Z0-9_]+)`', mapa))
landmarks = re.findall(r'«([^»]+)»', mapa)

errores = []
for f in sorted(funciones_mapa - funciones_codigo):
    errores.append(f'el mapa nombra `{f}()`, pero ya no existe en index.html')
for c in sorted(constantes_mapa):
    if not re.search(r'\b(?:const|let|var)\s+' + c + r'\b', codigo):
        errores.append(f'el mapa nombra `{c}`, pero no hay "const {c}" en index.html')
for l in landmarks:
    if l not in codigo:
        errores.append(f'el mapa usa el landmark «{l}», pero ese texto ya no está en index.html')
for f in sorted(funciones_principales - funciones_mapa):
    errores.append(f'la función {f}() de index.html no está en docs/MAPA.md: agrégala en la sección que corresponda')

for e in errores:
    print('❌', e)
if errores:
    sys.exit(1)
print(f'✅ docs/MAPA.md al día: {len(funciones_mapa)} funciones, {len(constantes_mapa)} constantes, {len(landmarks)} landmarks')
