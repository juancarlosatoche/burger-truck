# Prompts: bosque del camino (casa → plaza)

**Para qué sirven:** son las imágenes de referencia para el bosque que se ve al manejar de la casa a la plaza (etapa 2B de `docs/PIPELINE.md`). Hoy ese camino es pasto vacío: el truck sale en `(14, 24)` y estaciona en `(50, 50)`.

**Cómo usarlos:**

1. Copia el prompt en inglés tal cual. Ya trae la línea de estilo de `00_style.md` al final.
2. Adjunta las imágenes que dice **"Adjuntar"**. La primera siempre es el estilo del juego.
3. Guarda la imagen que más te guste en la carpeta que dice **"Guardar como"**.
4. Si sale con texto, logos o fondo de color, pide otra vez: *"Same image, plain light-grey background, no text."*

**"Vibrante" sin romper el estilo:** el estilo guarda los colores fuertes para la comida y los acentos. El bosque se ve vivo con **flores, hojas de varios verdes y algunos árboles de otoño como acento**, y con la luz dorada de la tarde. No con verde neón.

---

## A. Hoja de árboles y plantas (lo más importante)

**Adjuntar:**

1. `reference/style-targets/driving_first_person.jpg` (estilo del juego visto al manejar)
2. `reference/style-targets/truck_window_dusk.jpg` (mira los árboles facetados de la plaza)

**Guardar como:** `reference/environment/bosque_hoja.png`

> Game environment reference sheet: a set of stylized low-poly forest plants for a cozy driving game, each isolated and spaced out on a plain light-grey background, front view, no text. Include: three different broadleaf trees (a big round oak, a tall oval tree, a wide umbrella-shaped tree) in several fresh greens from lime to deep emerald; two different pine trees (one tall and slim, one short and wide); a white-bark birch with yellow-green leaves; one flowering tree with pink blossoms; one autumn tree with orange and red leaves as an accent; two round bushes (one with small yellow flowers); a clump of ferns; a patch of tall grass; a cluster of red-capped mushrooms; small wildflower patches in purple, yellow and white; three mossy grey rocks of different sizes; a fallen log and a tree stump. Clear faceted shapes: tree crowns made of a few chunky low-poly blobs, simple tapered trunks, easy to model. Lively, varied and colorful, but natural, not neon. Match the art style of the attached images. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

---

## B. El camino visto desde el asiento del conductor (el objetivo de estilo)

**Adjuntar:**

1. `reference/style-targets/driving_first_person.jpg` (estilo y ángulo de cámara)
2. `reference/screenshots/driving_first_person_2026-10-23_zona.jpg` (cómo se ve hoy: pasto vacío)
3. `reference/environment/bosque_hoja.png` (la imagen A, para que use los mismos árboles)

**Guardar como:** `reference/style-targets/camino_bosque.png`

> First-person view from the driver's seat of a cute food truck, steering wheel and dashboard at the bottom of the frame, driving on a gently curving dirt road through a vibrant low-poly forest in late golden-hour afternoon. Trees of varied shapes, sizes and greens line both sides of the road, with a few pink-blossom and orange autumn trees as accents, flowering bushes, ferns, mushrooms, mossy rocks and wildflowers along the edges. The road stays wide and clear, trees set back a few metres from it. Warm sun rays slant through the trees, soft fog in the distance, and far ahead at the end of the road the warm glow of a small plaza with string lights. Match the art style of the attached images. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

---

## C. Plano visto desde arriba (opcional, ayuda a acomodar los árboles)

**Adjuntar:** la imagen A.

**Guardar como:** `reference/environment/bosque_plano.png`

> Top-down game level floor plan, stylized low-poly, of a forest between a small house in the bottom-left corner and a small town plaza with string lights in the top-right corner. A dirt road curves gently from the house to the plaza. Dense, varied forest on both sides of the road, thinning into a few scattered trees and flower meadows near the house and near the plaza. Small details: a little pond with reeds, a clearing with mushrooms, a few rocks. Clean, readable, soft colors, no text, no labels.

---

**Para Blender:**

- **Cada árbol es un modelo distinto** (unos 10 tipos, de la hoja A), y el script los reparte con variación de tamaño, giro y color. Nada de copiar y pegar el mismo árbol (regla de Chong-U).
- **El camino queda libre:** la ruta de `(14, 24)` a `(50, 50)` tiene unos 10 m de ancho sin árboles. Lo denso queda a los lados.
- Pocos polígonos: 200–800 triángulos por árbol. Todo junto en **un solo `.glb` de menos de 3 MB**, con las copias unidas por material para que el juego vaya rápido.
- No tapar la casa, la plaza ni los edificios. El bosque se va abriendo cerca de los dos.
