# Decision log

Newest at the bottom. Write down the **why**, so a future you (or an AI) doesn't undo it.

## 2026-10-22: Project setup

- **Stay on Three.js** in a single `index.html`, not Rust/WASM. Ignacio must be able to read and edit the game, and Three.js loads `.glb` models and audio fine.
- **Single-player.** Chong-U's multiplayer, netcode and Colyseus steps are out of scope.
- **v5 is the graybox baseline.** It's committed unchanged and tagged `v5-graybox`.
- **Public repo** `juancarlosatoche/burger-truck`, so it can be hosted free on GitHub Pages. (We first tried `ignacioatoche`, but Claude could not get push access there; Ignacio can be added as a collaborator.)
- **Git LFS only for `source/`.** GitHub Pages can't serve LFS files, so runtime assets in `assets/` stay in normal git and must stay small.
- **Tools:** image generator, Tripo, Blender (on the home computer), ElevenLabs.
- **No API keys in the repo.** Assets are generated in each tool's website and committed as files.

## 2026-10-22: Art direction chosen (Stage 1)

- [x] **Chosen mockup:** style **D, "Cozy low-poly with glow"**, from `prompts/01_art_direction.md`. Saved as `reference/mockups/mockup_D_cozy_lowpoly_glow.jpg`, and as the first style target `reference/style-targets/truck_window_dusk.jpg`.
- [x] **Style:**
  - Faceted low-poly environment and props, but smooth rounded characters and food.
  - Indigo-to-sunset sky with warm amber lights, **strong bloom** on string lights and signs, volumetric warm light and soft fog.
  - Brushed steel and warm wood. No outlines.
- [x] **Style line and full breakdown:** [`prompts/00_style.md`](../prompts/00_style.md).
- **Why it fits:** low-poly props are quick to model in Blender and keep `.glb` files small for GitHub Pages. The dusk lighting matches the game's existing time-of-day system and bloom.
- **Not decided yet:** fries, drinks and ingredient trays seen in the mockup. They're listed in `prompts/00_style.md` as ideas.
- [x] **Done:** generate the other 4 style targets (bedroom at night, kitchen in the morning, driving, truck exterior) using the style line and this image as reference.

## Graybox notes (play v5 and write what isn't fun yet)

-

## 2026-10-22: Style targets for every scene

All 5 style targets are in `reference/style-targets/`. Each visual change is compared against the target for its scene (Stage 4 of `docs/PIPELINE.md`):

| Scene in the game | Style target | Time of day |
|---|---|---|
| Night tutorial, bedroom | `bedroom_night.jpg` | Night: blue moonlight plus a warm lamp |
| Morning missions, kitchen | `kitchen_morning.jpg` | Golden morning sun beams |
| Driving the truck | `driving_first_person.jpg` | Late afternoon, golden haze |
| Truck from outside, plaza | `truck_exterior_night.jpg` | Night, string lights |
| Serving at the window | `truck_window_dusk.jpg` | Dusk to night |

## 2026-10-22: Driving becomes first person

- **Decision:** the drive to the parking zone is played **from the driver's seat**, like `driving_first_person.jpg`. This replaces v5's camera behind and above the truck.
- **Why:** the whole game is first person; this keeps it consistent and more immersive.
- **What it will need (not done yet):**
  - A truck **cab interior** model: wheel, dashboard, mirrors, burger air-freshener. Added to `docs/ASSET_LIST.md`.
  - **Player hands** that hold the steering wheel.
  - A change to the driving camera in `driveUpdate()`: camera inside the cab, plus steering-wheel rotation. It will be done when the truck model goes in, keeping Ignacio's driving logic (speed, steering, parking zone) as it is.
- **To check when we get there:** in first person it's harder to see the parking zone, so the yellow zone and arrow may need to be bigger or brighter.

## 2026-10-22: First Tripo models in the game (Customers A, B, C, preview)

- **What:** `customer_a.glb`, `customer_b.glb` and `customer_c.glb` from Tripo replace the code-drawn customer bodies. Customers take turns A, B, C, A… so the line always shows different people.
- **Why now:** to show the kids the pipeline working end to end (image → Tripo → game) before rigging.
- **Optimized** from Tripo's ~10 MB each (≈210k triangles, three 4096 textures) to **1.1–1.3 MB** each (≈25k triangles, 1024 textures) with `gltf-transform` (weld, simplify, resize). Originals stay out of the repo for now; keep them locally.
- **Texture check:** Customer B's dark smudges on the chin and neck are in Tripo's original too (compared side by side), not caused by the optimization. Fix later in Blender (texture paint) or by regenerating.
- **No skeleton yet.** The model goes inside the existing `rig` group, so it reuses Ignacio's code animations: walk bounce, sway, happy jump, angry shake. Arms, legs and the face don't move until the Blender rig (Stage 2A, step 3).
- **Fallback:** if the model can't load (for example when opening `index.html` by double-click), the code-drawn customers appear as before.
- **Compared with the style target** (`reference/screenshots/truck_window_2026-10-22_customers_abc.jpg`). Differences to fix later:
  - Customers stand lower and further from the window than in the target.
  - The game's sky is lighter and pinker; the target is deep indigo with an orange horizon.
  - The counter and plate are flat white; the target has brushed steel, ingredient trays and warmer interior light.

## 2026-10-23: Characters paused; Stage 2B starts with the food truck exterior

- **Decision:** rigging the customers (Stage 2A) is postponed. Work moves to Blender for everything else (truck, rooms, plaza), most visible first: truck exterior → truck interior → cab → bedroom → kitchen → plaza.
- **How the Blender models are made:** Claude writes a Blender Python script per asset (`source/blender/build_*.py`), which builds the model at the game's exact sizes, saves the `.blend` and exports the `.glb`. Juan Carlos and Ignacio open the `.blend` in Blender and tweak anything. Re-running the script rebuilds from scratch, so tweaks made only in the `.blend` must be exported by hand (File → Export → glTF 2.0).
- **The `.blend` isn't committed from Claude's side** (its large-file upload is blocked there). Running the script in Blender recreates `source/blender/food_truck.blend`; commit it from GitHub Desktop after tweaking.
- **Colors:** the materials use the same hex numbers as the code (`0xc8102e` red, `0xf6ead2` cream…), so the model matches the rest of the game. In Blender they look paler than in the game; that's expected.

## 2026-10-23: Food truck exterior from Blender (`food_truck.glb`)

- **What:** new body for the truck, in four pieces so the **"Ampliar"** upgrade keeps working:
  - `truck_front`: cab with windshield, mirrors, grille, headlights, front wheels, round burger logo;
  - `truck_middle`: side walls, window frame, wooden ledge, hinged awning with light strip, roof and air conditioner. It **stretches**;
  - `truck_rear`: back wall with the door opening, tail lights, step, rear wheels. It **slides back**;
  - `truck_sign`: 3D "BURGER TRUCK" letters that glow at night, with a burger on top. It now travels with the truck (the old sign stayed in the plaza).
- **Fits the code:** the walls sit just outside the interior walls, the window and the rear door opening are the same size, and everything hangs from an empty `escala_juego` that converts real game size to the code's units (×2 wide/long, ×1.8 tall).
- **Code:** `cargarModeloTruck()` loads it, hides the code-drawn body, the old canopy and the plaza sign, and registers the middle/rear pieces in `truckParts`. Materials named `luz_…` join `lampMats`, so they brighten at dusk. If the file can't load, the code-drawn truck stays (tested).
- **Compared with the style target** `truck_exterior_night.jpg` (screenshots `reference/screenshots/truck_exterior_2026-10-23_*.jpg`). Differences to fix later:
  - The target's upper body is more faceted, with angled panels near the roof; ours is mostly flat with a faceted roof crown.
  - The target's sign is tilted and bigger, sitting closer to the awning, and lights hang from it.
  - The target has a warmer, brighter interior seen through the window, with shelves, utensils and a range hood. That will come with the truck interior.
  - In the target the cab is on the left as seen from the queue; in the game it's on the right. The layout is the game's, so it stays.
  - The target's wheels have bigger chrome rims, and the red is a little darker and warmer.

## 2026-10-23: Truck kitchen interior from Blender (`truck_interior.glb`)

- **What:** `source/blender/build_truck_interior.py` builds the kitchen inside the truck: both steel counters with cabinet doors, grill surround with knobs and a range hood, wall shelves with jars, plates and boxes, hanging utensils and a towel, fridge top and kick plate, a new cash register, soda machine, ketchup and mustard bottles, napkins and cups, a wooden window frame with a warm light strip, order tickets, and the rear door frame with an apron. **190 KB, ~3.3k triangles.**
- **Clicks keep working:** what the player clicks stays drawn by the code (grill plate, order plate, computer, ingredients). The fridge door from Blender (`nevera_bisagra`) goes inside the code's hinge, so it opens and closes as before; the code's door is hidden but still receives the click. All five clicks tested.
- **"Ampliar":** `interior_middle` (window frame, light, tickets) stretches like the walls; `interior_rear` (door frame) slides back.
- **Code:** `cargarModeloCocina()` loads it and hides the code-drawn counters, register, soda machine and bottles. New helper `piezaDeModelo()` applies the Blender scale to a piece. If the file can't load, the code-drawn kitchen stays (tested).
- **Scripts are now safe to run inside Blender:** they no longer reset Blender (which closed the script editor), they find the repo folder from the open script, and they export a merged copy, so the scene keeps every part separate for tweaking. `build_food_truck.py` was updated the same way; its `.glb` is unchanged.
- **Compared with `truck_window_dusk.jpg`** (screenshots `reference/screenshots/truck_interior_2026-10-23_*.jpg`, `truck_window_2026-10-23_blender.jpg`). Differences to fix later:
  - The target's walls are warm orange; ours are still the code's white tile.
  - The target has steel ingredient trays (lettuce, tomato, cheese) on the counter. They're left out for now, because they'd look clickable but aren't.
  - The target's lighting is warmer and dimmer, with a strong orange ceiling light.
  - The target has a bun bag, a spatula and napkins in the foreground near the grill.
  - The window frame now matches the target (wood).

## 2026-10-23: First-person driving with the cab from Blender (`truck_cab.glb`)

- **What:** the decision from 2026-10-22 ("driving becomes first person") is now in the game. `source/blender/build_truck_cab.py` builds the inside of the cab:
  - dashboard with speedometer and fuel gauge, radio, gear stick, glove box;
  - seats, door panels, sun visors, roof light;
  - the rear-view mirror with the **burger air freshener**;
  - a steering wheel (`cab_volante`). **83 KB, ~1.3k triangles.**
- **Truck body change:** the top of the cab in `food_truck.glb` is now hollow, with real openings for the windshield and side windows. The game makes the `vidrio` material transparent, so you can see out from the seat and see the dashboard from outside.
- **Code (`driveUpdate`):** when both the truck body and the cab have loaded, the camera sits in the driver's seat on the left (`OJOS_CONDUCTOR`), looking ahead and a little down (`MIRADA_CONDUCTOR`). The wheel turns when you steer (A/D or joystick). Ignacio's driving logic (speed, steering, parking zone) is unchanged. If a model doesn't load, the old camera behind the truck is used (tested).
- **Parking zone check:** from the seat, the yellow zone, the arrow and the light beam are easy to see (`reference/screenshots/driving_first_person_2026-10-23_zona.jpg`), so they didn't need to be bigger.
- **Compared with `driving_first_person.jpg`:**
  - The target shows the player's **hands** on the wheel. They'll come with the characters track (2A).
  - The speedometer sits below the view; the target shows it through the wheel.
  - The target's light is warm golden haze. The game's late-afternoon sky is more purple.
  - The target's dashboard has more detail (vents, buttons), and the hood shows the truck's colors.
  - The steering wheel tilts inside the truck's stretched scale (×2 wide, ×1.8 tall), so it's about 10% oval. That's barely visible.
## 2026-10-23: Bedroom furniture from Blender (`bedroom.glb`)

- **What:** `source/blender/build_bedroom.py` builds:
  - a wooden bed with legs, footboard and a faceted headboard with a darker grain panel;
  - mattress, sheet, a blue blanket draping over the sides, and two pillows;
  - a nightstand with drawer, knob and books, a faceted crystal lamp, and the phone that gets the friend's message;
  - a striped rug and green slippers.

  **71 KB, ~1.1k triangles.** The house isn't scaled, so the Blender model is in real game units (scale 1).
- **Clicks:** the house ignores hidden objects when checking clicks, so the Blender **mattress** (`cama_colchon`) and **lamp shade** (`lampara_pantalla`) take over the clicks from the code ones. The shade uses the code's lamp material, so clicking still turns the lamp on and off. Both clicks tested.
- **Unchanged:** the collision boxes of the bed and nightstand, the wake-up camera, the tutorial. The blanket stops at Y=2.86, so the camera that wakes up on the mattress isn't inside it.
- **Code:** `cargarModeloDormitorio()` is called from the house setup (`init`). If the file can't load, the code-drawn furniture stays (tested).
- **Compared with `bedroom_night.jpg`:**
  - The target is much darker. The moonlight comes through the window onto a wood floor, and the lamp is the main warm light. In the game the room is evenly lit by the ceiling light.
  - The target's walls are plain gray-beige, without the code's speckled texture.
  - The target's floor has long planks; the game's has a parquet pattern.
  - The bed and lamp now match the style. The target's lamp shade is wider; ours keeps the code's size, because it is also the click target.
## 2026-10-23: House kitchen from Blender (`house_kitchen.glb`)

- **What:** `source/blender/build_house_kitchen.py` builds:
  - honey-wood base cabinets with shaker doors, drawers and handles, a stone counter, oven and stove;
  - a sink with tap, a dish rack and a tiled backsplash;
  - upper cabinets with doors and a range hood;
  - a cream fridge with magnets and a child's drawing;
  - a table with two chairs, a fruit bowl, a vase with flowers and a faceted hanging lamp;
  - counter details: cutting board, spoon jar, kettle, paper towels.

  **203 KB, ~3.6k triangles.** Scale 1, like the bedroom.
- **Clicks and missions unchanged:** the code-drawn cabinets, fridge, table and chairs are hidden; their collision boxes stay.
  - The clickable things that never change (frying pan, toaster, egg carton) are drawn by Blender, but the click still lands on the code shape in the same place. Its *material* is switched off instead of hiding it, because the house only lets you click visible objects.
  - Things that change during the mission (dirty plates, eggs, bread, slices, toast, fried eggs, foam, breakfast plate) stay code.
  - Clicks tested: pan, toaster, eggs, plates, breakfast plate.
- **Metal:** steel and chrome are only slightly metallic in this model. Fully metallic, they reflected the blue sky map and looked navy.
- **Code:** `cargarModeloCocinaCasa()` is called from `init`. If the file can't load, the code-drawn kitchen stays (tested).
- **Compared with `kitchen_morning.jpg`:**
  - The target has a big window over the sink, with golden sun beams. Our back wall has no window; windows belong to the walls (still code).
  - The target's light is strong, warm and low; ours is even and flat.
  - The target's plates are colorful and its cups are on the counter; ours are the code's mission plates.
  - The target's eggs sit in a 6-egg carton; ours shows the code's 2 eggs in the Blender carton.
  - Cabinets, stove, pan, toaster, table and chairs now match the style.
## 2026-10-23: Plaza from Blender (`plaza.glb`)

- **What:** `source/blender/build_plaza.py` builds:
  - two tables with faceted striped umbrellas (orange/cream and teal/cream) and wooden chairs with cushions;
  - three strands of string lights on wooden posts. One is the original over the queue; two are new and cross the plaza over the tables, like the style target;
  - six different trees (two oaks, two pines, a birch, a big bush) in the places of the code trees, so there's no copy-paste;
  - planters with flowers, a green trash bin, the menu board's frame and legs, and two old-style lanterns.

  **256 KB, ~4.4k triangles.** Scale 1, world positions (Blender Y = −z of the game).
- **What stays code:** the actual lights (PointLights), the menu text, the buildings, the pavement, the street and the clock.
- **Night lights:** the `luz_foquitos` and `luz_farol` materials join `lampMats`, so they brighten at dusk like the code bulbs did.
- **Code:** `cargarModeloPlaza()` hides the 72 code-drawn pieces it replaces. If the file can't load, they stay (tested).
- **Compared with `truck_exterior_night.jpg`:**
  - Matches now: string lights crossing the plaza on wooden posts, umbrella tables with wooden chairs, rounded dark-green trees, lantern street lamps.
  - The target has benches and a low wall around the plaza, and its trees are bigger and darker.
  - The target's ground is warm stone with a lit lawn; ours is the code's gray pavement tiles.
  - The target's umbrellas are all cream; ours are striped, to tell the two tables apart.

## 2026-10-23: Model versions (fix: solid wall when driving)

- **Problem:** after merging, the windshield looked like a cream wall from the driver's seat. The browser was still using an **old copy of `food_truck.glb`** (from before the cab windows were opened) with the new code.
- **Fix:** every model is now loaded with `VERSION_MODELOS` (for example `food_truck.glb?v=2026-10-23c`), so browsers fetch the model that matches the code. **Rule (also in `CLAUDE.md`): when any `.glb` changes, update `VERSION_MODELOS`.**
- **Also:** the rear-view mirror and the burger air freshener moved up near the roof. They were covering the yellow parking zone on the right side of the windshield (`reference/screenshots/driving_first_person_2026-10-23_fixed.jpg`).

## 2026-10-23: Papas fritas en el menú (idea de Ignacio)

- Nuevo plato **Papas Fritas** ($8): papas crudas de la nevera (estante alto) → freidora con aceite (4.5 s, se van dorando) → caja roja de papas → plato → cliente.
- La freidora va entre la plancha y los panes; las cajas, junto al plato. Las dos se dibujan con código, así funcionan con o sin el modelo de Blender.
- Las papas se sirven solas (no en el mismo plato que una hamburguesa). Un combo hamburguesa + papas puede ser el siguiente paso.
- Las cajas son rojas con una 🍟, sin logos de marcas reales.

## 2026-10-23: Combos hamburguesa + papas (idea de Ignacio)

- Nuevos platos **Combo Clásica** ($18) y **Combo Completa** ($24): la hamburguesa y una caja de papas en el mismo plato. La caja va **al lado** de la hamburguesa, así que se puede poner antes o después.
- Los clientes que piden combo tienen **30 s más de paciencia** (`COMBO_TIEMPO_EXTRA`), porque hay que hacer dos cosas.
- `platoCoincide(receta)` revisa el plato para hamburguesas, papas y combos; lo usan los clientes, los pedidos a domicilio y los avisos.
- Si arman una Clásica sin papas, el aviso recuerda que con papas sería el Combo Clásica.

## 2026-10-23: Freidora, papas crudas y edificios hechos en Blender

- Ignacio generó las referencias con `prompts/05_papas_freidora_edificios.md`. Están en `reference/props/` y `reference/environment/`.
- **Freidora:** la canasta es una pieza aparte. Mientras fríe, baja al aceite con las papas adentro, y sube cuando están listas. El foquito naranja titila mientras fríe. El aceite es un poco transparente para ver las papas.
- **Papas crudas:** bandeja de acero con palitos pálidos, en la nevera y en la mano. Las del código siguen recibiendo el clic (son invisibles).
- **Edificios:** 5 distintos (ladrillo con tanque, torre azul, tiendas con toldos, crema con balcones, esquina redonda), en los mismos lugares que las cajas de antes. No dan ni reciben sombras: están lejos, y así se ven más limpios y el juego va más rápido.
- Los tres modelos se cargan aparte. Si alguno falla, se queda el dibujado con código.

## 2026-10-23: Herramientas de Blender compartidas

- Los 8 scripts `build_*.py` tenían copias idénticas de las mismas 12 funciones (unas 147 líneas cada uno). Ahora viven en `source/blender/lib_blender.py` y cada script las importa.
- **Por qué:** los scripts nuevos son mucho más cortos, y escribirlos gasta menos tokens. Un arreglo en `lib_blender.py` sirve para todos los modelos.
- **Comprobado:** los 9 `.glb` salen byte por byte iguales antes y después del cambio.
- **Cómo se garantiza:** `_plantilla.py` es el punto de partida de los scripts nuevos; `tools/revisar_blender.py` falla si un script no importa la librería, redefine una herramienta o exporta por su cuenta; GitHub lo corre en cada pull request; y `CLAUDE.md` tiene la regla para cualquier sesión de IA.

## 2026-10-23: Herramienta para probar y tomar fotos (`tools/probar.py`)

- Antes, cada cambio escribía su propio script de prueba y lo corregía varias veces, y se tomaban muchas fotos sueltas. Eso gastaba muchos tokens.
- Ahora hay **vistas con nombre** (freidora, nevera, plato, plaza, cuarto, manejar…) y **pruebas de juego** (hamburguesa, papas, combo, reglas del plato) en un solo archivo. Varias vistas salen en **una sola imagen**.
- La herramienta pone el truck en la plaza antes de entrar (con `teleportToFoodTruck` solo, el truck se queda donde empieza el manejo).
- En la prueba de papas se adelanta el reloj de la freidora, porque sin tarjeta de video hay muy pocos cuadros por segundo.

## 2026-10-23: Mapa del código (`docs/MAPA.md`)

- `index.html` tiene unas 3.300 líneas, y cada cambio empezaba buscando y leyendo pedazos. El mapa dice qué función hace qué y dónde está cada área en el mundo.
- Va en un archivo aparte, no en `CLAUDE.md`, porque `CLAUDE.md` se lee completo al empezar cada sesión, aunque no se toque el código.
- Usa nombres de funciones y comentarios («landmarks»), no números de línea, que cambian con cada edición.
- `tools/revisar_mapa.py` falla si el mapa nombra algo que ya no existe o si falta una función nueva. GitHub lo corre en cada pull request.

## 2026-10-23: Bosque y camino de tierra entre la casa y la plaza

- Las referencias salieron de `prompts/06_bosque_camino.md`: la hoja de plantas (`reference/environment/bosque_hoja.png`), el plano (`bosque_plano.png`) y el objetivo de estilo desde el asiento del conductor (`reference/style-targets/camino_bosque.png`).
- **Camino:** sale de donde arranca el truck `(14, 24)`, sigue recto al este, dobla al sur por `x≈36` y entra al patio pavimentado de atrás de la plaza. Desde ahí se dobla al norte y se entra al recuadro amarillo mirando a la flecha, como pide el juego. La lógica de manejo no cambió. Los árboles no chocan con el truck: el camino tiene unos 13 m libres para que manejar siga siendo fácil.
- **Bosque:** 28 modelos (robles, arces, sicomoro, árbol paraguas, árbol de otoño, árbol de flores rosadas, abetos, pino alto, abedul, álamos, arbustos con bayas y con flores, helechos, cardos, hongos, rocas con musgo, flores, pasto, tronco caído, tocón), repartidos al azar con la misma semilla. ~1.260 plantas en total. Cerca del camino hay más color (flores rosadas, otoño); lejos, más pinos y robles. Hay una laguna con juncos y un claro con hongos, como en el plano. No hay árboles en la casa, la plaza, la fila de clientes, la calle ni el patio.
- **"Vibrante" sin romper el estilo:** el color fuerte va en flores, bayas, el árbol rosado y los de otoño; las hojas son de varios verdes naturales.
- **Para que vaya rápido:** cada modelo se guarda una sola vez en el `.glb` con dónde va cada copia (opción `copias=` de `guardar()`), y el juego dibuja juntas las copias iguales (`InstancedMesh`) por zonas de 100 m. Cada planta usa **un solo material** con los colores pintados en sus partes (`unir(..., colores=mat_colores(...))`), así un árbol entero es una sola llamada de dibujo: el bosque pasó de 892 grupos a 110. Las plantas chiquitas no dan sombra.
- **Pasto:** el pasto del mundo (`buildTruckSurroundings`) pasó de casi negro a un verde más fresco, como en el objetivo de estilo. También se ve en la plaza.
- **Herramientas nuevas en `lib_blender.py`:** `ico` (estaba copiada en `build_plaza.py`), `unir`, `mat_colores` y `copias=`. Los 12 `.glb` de antes salen byte por byte iguales.
- **`tools/probar.py`:** ahora espera a que el juego cambie de escena antes de poner la cámara. Sin tarjeta gráfica los cuadros son lentos, y el teletransporte al truck llegaba tarde y metía la cámara adentro del truck.
- **Diferencias que quedan con el objetivo de estilo:** el objetivo tiene rayos de sol entre los árboles y más neblina dorada; los árboles del objetivo están un poco más pegados al camino; y la casa no se ve al empezar a manejar (el juego la esconde al salir).

## 2026-10-24: Papas fritas y manos del jugador hechas en Blender (idea de Ignacio)

- **Qué pidió Ignacio:** mejor calidad gráfica en las papas cuando terminan de freírse, y en las manos del jugador al cocinar y al manejar.
- **Papas (`source/blender/build_papas_fritas.py` → `papas_fritas.glb`):** antes eran palitos delgados con rayas que parecían fideos. Ahora son papas gorditas con bordes biselados, puntitas tostadas, tres tonos de dorado y granitos de sal. El modelo tiene las mismas medidas que el código, así que reemplaza sin mover nada:
  - en la canasta de la freidora: el código las pinta de pálidas a doradas mientras se fríen (`pintarPapasFreidora()`), igual que antes;
  - en la mano: un montoncito de papas (`papas_sueltas`);
  - la caja roja: más ancha arriba, con el frente curvo, franja amarilla y un dibujito de papas (sin marcas de verdad), y las papas asomándose por arriba. Las cajas del código siguen recibiendo el clic (son invisibles).
- **Manos (`source/blender/build_manos.py` → `manos.glb`):** siguen `reference/turnarounds/player_hands.png`: piel facetada, nudillos, uñitas y manga **azul** (como la referencia; la mano del código tenía manga roja). No tienen esqueleto: son dos poses fijas.
  - `mano_sostener`: palma arriba, dedos un poco doblados; lo que llevas se apoya en la palma (mismo socket que antes). Es más grande que una mano real (×1.5), como en los dibujos animados; por eso las papas en la mano también se ven un poco más grandes.
  - `manos_volante`: las dos manos agarrando el aro a las "10 y 10", con el dorso hacia afuera y los pulgares sobre el aro. Solo se ven mientras manejas (si no, habría manos flotando en el truck estacionado).
  - Al doblar, las manos giran el **35 %** de lo que gira el volante (`GIRO_MANOS`). Como el aro es redondo, siguen agarrándolo; si giraran todo (hasta 90°), el brazo cruzaba toda la pantalla.
- **Comparado con `driving_first_person.jpg`:** las manos ahora están en el volante. En la referencia se ven los dedos doblados sobre el aro; en el juego se ven el dorso y los pulgares, porque la cámara está más arriba. Fotos: `reference/screenshots/manejar_2026-10-24.png`, `freidora_2026-10-24.png`, `plato_2026-10-24.png` (antes: `papas_manos_2026-10-24_antes.png`).
- **Si no cargan los modelos**, se ven las papas y la mano del código, como antes (no hay manos en el volante).

