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
