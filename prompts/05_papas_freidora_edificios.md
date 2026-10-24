# Prompts: papas crudas, freidora y edificios de la plaza

**Para qué sirven:** son las imágenes de referencia para modelar en Blender (etapa 2B de `docs/PIPELINE.md`).

**Cómo usarlos:**

1. Copia el prompt en inglés tal cual. Ya trae la línea de estilo de `00_style.md` al final.
2. Adjunta las imágenes que dice **"Adjuntar"**. La primera siempre es el estilo del juego.
3. Guarda la imagen que más te guste en la carpeta que dice **"Guardar como"**.
4. Si sale con texto, logos o fondo de color, pide otra vez: *"Same image, plain light-grey background, no text."*

---

## A. Papas crudas en la nevera

**Adjuntar:**

1. `reference/style-targets/truck_window_dusk.jpg` (estilo del juego: mira las bandejas de acero con comida)
2. `reference/screenshots/nevera_papas_2026-10-23.png` (cómo se ven hoy, en el estante de arriba)

**Guardar como:** `reference/props/papas_crudas.png`

> Game prop reference sheet: a small rectangular stainless-steel food container (like a restaurant prep pan), filled with raw cut potato sticks, pale cream-yellow with slightly darker ends, neatly piled and a few sticks sticking up. Next to it, the same container covered with a clear lid, and two whole raw potatoes with light brown skin. Each object isolated, shown in front view, three-quarter view and top view, plain light-grey background, soft even lighting, no text. Simple shapes that are easy to model: the container is a box with rounded corners and a thin rim, each potato stick is a simple long box. Match the art style of the attached image. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

**Para Blender:** que quepa en el estante de la nevera (más o menos 30 × 20 cm). Las papas crudas deben verse claramente **más pálidas** que las fritas.

---

## B. Freidora

**Adjuntar:**

1. `reference/style-targets/truck_window_dusk.jpg` (estilo del juego: acero cepillado, luz cálida)
2. `reference/screenshots/freidora_2026-10-23.png` (dónde está hoy: entre la plancha y los panes)

**Guardar como:** `reference/props/freidora.png`

> Game prop reference sheet: a compact countertop deep fryer for a food truck, brushed stainless steel body, an open top showing hot golden oil, one wire frying basket with a black handle that sticks out toward the front, two round red control knobs and a small glowing orange "on" light on the front panel. Show it four times: front view, three-quarter view, the basket lowered into bubbling oil with pale raw fries, and the basket lifted up and hooked above the oil with golden crispy fries dripping. Also show the wire basket alone, separate from the fryer. Plain light-grey background, soft even lighting, no text, no brand logos. Chunky, simple, low-poly shapes that are easy to model. Match the art style of the attached image. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

**Para Blender:** la **canasta va como pieza aparte** (`freidora_canasta`), para que el juego pueda bajarla al aceite y subirla cuando las papas estén listas. El aceite también aparte (`freidora_aceite`), porque el código lo hace brillar. Tamaño en el mostrador: unos 36 × 38 cm.

---

## C. Edificios de la plaza

**Adjuntar:**

1. `reference/style-targets/truck_exterior_night.jpg` (estilo del juego: edificios de fondo con ventanas cálidas)
2. `reference/style-targets/truck_window_dusk.jpg` (los mismos edificios vistos desde la ventanilla)
3. `reference/screenshots/plaza_2026-10-23_from_window.jpg` (cómo se ven hoy: cajas con ventanas iguales)

**Guardar como:** `reference/environment/edificios_plaza.png`

> Game environment reference sheet: five different stylized low-poly city buildings for the background of a small plaza at dusk, each isolated side by side on a plain light-grey background. Vary them: a tall slim apartment tower, a wide four-story building with ground-floor shops and striped awnings, a stepped building with balconies and rooftop plants, a brick building with a water tank on the roof, and a short corner building with a rounded corner. Muted facade colors (dusty blue, terracotta, cream, slate grey). Windows are simple rectangles in rows, some glowing warm amber and some dark, so the buildings feel lived in at night. Rooftop details: antennas, air-conditioning boxes, water tanks. Front view and three-quarter view of each, soft even lighting, no text, no signs with words. Match the art style of the attached images. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

**Opcional, una segunda imagen para ver cómo se ven juntos (adjuntar las mismas 3):**

**Guardar como:** `reference/environment/edificios_plaza_skyline.png`

> Wide view of a cozy city skyline behind a small plaza at dusk, seen at eye level from a food truck service window: five varied low-poly buildings of different heights and colors, warm glowing windows scattered across the facades, rooftop water tanks and antennas, string lights and trees in the foreground plaza, soft fog between the buildings. Match the art style of the attached images. Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

**Para Blender:**

- Cada edificio distinto. Nada de copiar y pegar el mismo (regla de Chong-U).
- Las ventanas como **caras separadas con material propio**, para que el código las prenda al anochecer, como hace hoy.
- Pocos polígonos: se ven de lejos. Unos 500 triángulos por edificio.
