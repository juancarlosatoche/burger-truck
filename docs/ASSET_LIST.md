# Asset list

This list is taken from `index.html` v5, and covers everything the game currently draws in code.

**Priority:**

- **P1** — the player sees it constantly
- **P2** — the player sees it often
- **P3** — background or brief

**Status:** ⬜ todo · 🖼️ reference done · 🧊 model done · ✅ in game

## Characters (track 2A, one shared skeleton)

| Asset | Where in game | Priority | Animations needed | Status |
|---|---|---|---|---|
| Customers A, B, C (green hoodie, blue jacket, pink sweater) | Truck window queue | P1 | idle, walk, impatient, happy_jump, angry_stomp, wave | ✅ in game **without skeleton** (`assets/models/characters/customer_a\|b\|c.glb`, 1.1–1.3 MB each, ~25k triangles). Move with the old code animations (bounce, sway, jump, turn red). Need Blender rig; B has dark smudges on chin/neck from Tripo |
| Delivery driver | Behind the truck | P2 | walk, idle, carry (crate in `hand_R`) | 🖼️ `reference/turnarounds/delivery_driver` |
| Player hands (first person) | Holding ingredients; both hands on the steering wheel while driving (see `driving_first_person.jpg`) | P1 | grab, hold (socket `hand_R`), steer (both hands) || 🖼️ `reference/turnarounds/player_hands.png` |
| Friend (phone avatar, 2D) | Phone message | P3 | (image only) | ⬜ |

## Food truck (track 2B)

| Asset | Priority | Notes | Status |
|---|---|---|---|
| Truck exterior: body, cab, wheels, canopy, sign | P1 | Look defined by `truck_exterior_night.jpg`: red lower body, cream upper body, faceted shapes, hinged service window with awning, lit "BURGER TRUCK" sign topped with a burger. Must allow the **"Ampliar"** upgrade: build it in **front / middle / rear** modules so the middle can be stretched or repeated | ✅ in game (`assets/models/props/food_truck.glb`, 273 KB, ~5.7k triangles). Built by `source/blender/build_food_truck.py` → `source/blender/food_truck.blend`. Pieces: `truck_front`, `truck_middle` (stretches), `truck_rear` (slides back), `truck_sign`. Code-drawn body stays as fallback |
| Truck cab interior: steering wheel, dashboard with speedometer, rear-view mirror with burger air-freshener, side mirror, windshield frame, visible hood | P1 | **New** (first-person driving). Look defined by `driving_first_person.jpg` | ✅ in game via `truck_cab.glb` (`source/blender/build_truck_cab.py`, 83 KB): wheel turns when steering; windows of `food_truck.glb` are now real openings with transparent glass |
| Truck interior: walls, floor, ceiling lights | P1 | Same modular rule | 🟡 walls, floor and ceiling still drawn in code; window frame, warm light strip and rear door frame from Blender (stretch with "Ampliar") |
| Fridge with opening door | P1 | Door as a separate object (it animates) | ✅ in game via `truck_interior.glb` (`source/blender/build_truck_interior.py`): door is `nevera_bisagra`, placed in the code's hinge; inside of the fridge still code |
| Grill (flat-top) | P1 | | ✅ in game via `truck_interior.glb` (`source/blender/build_truck_interior.py`): cabinet, knobs, guards and range hood; the clickable grill plate itself stays code |
| Service counter, plate | P1 | | ✅ in game via `truck_interior.glb` (`source/blender/build_truck_interior.py`): both counters; the clickable plate stays code |
| Ingredients: bun bottom, bun top, raw patty, cooked patty, cheese, lettuce, tomato | P1 | 7 small models, each must also look right in the hand | ⬜ |
| Cash register, soda machine, ketchup, mustard | P2 | | ✅ in game via `truck_interior.glb` (`source/blender/build_truck_interior.py`) (plus shelves, jars, utensils, napkins, cups, order tickets) |
| Deep fryer with wire basket (new: fries) | P1 | Reference: `reference/props/freidora_*.jpg` (Ignacio). Basket as a separate piece so it can move | ✅ in game via `freidora.glb` (`source/blender/build_freidora_papas.py`, 83 KB): `freidora_cuerpo`, `freidora_aceite`, `freidora_canasta` (code lowers it into the oil while frying); clicks stay on the code shapes |
| Raw fries tray in the fridge (new: fries) | P1 | Reference: `reference/props/papas_crudas.jpg` (Ignacio) | ✅ in game via `papas_crudas.glb` (`source/blender/build_freidora_papas.py`, 59 KB): also shown in the hand |
| Fries box and cooked fries | P1 | Red box with 🍟, no real brand logos | 🟡 drawn in code |
| Computer (monitor + keyboard) | P2 | Screen stays a canvas texture drawn in code | ⬜ |
| Rear door with window, EXIT sign, wall clock | P2 | Clock face stays drawn in code (it shows game time) | ⬜ |

## Plaza and street (track 2B)

| Asset | Priority | Status |
|---|---|---|
| Umbrella tables with stools (×2) | P2 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): wooden chairs with backs instead of stools |
| String lights on poles | P2 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): 3 strands on wooden posts (2 new, crossing the plaza) |
| Street lamps | P2 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): old-style lanterns; the real lights stay code |
| Menu chalkboard (text stays drawn in code) | P2 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): frame and legs |
| Trees (3–4 varieties, not copy-paste) | P2 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): 2 oaks, 2 pines, 1 birch, 1 big bush |
| Planters, trash bin | P3 | ✅ `assets/models/environment/plaza.glb` (`source/blender/build_plaza.py`): planters with flowers |
| Background buildings with lit windows | P3 | ✅ in game via `assets/models/environment/edificios.glb` (`source/blender/build_edificios.py`, 413 KB, ~7.4k triangles). Reference: `reference/environment/edificios_plaza.jpg` (Ignacio). 5 different buildings; windows with material `luz_ventana` light up at dusk. Code boxes stay as fallback |
| Road, sidewalk, grass textures | P2 | ⬜ |
| Yellow parking zone and arrow (driving) | P3 | Can stay in code | ⬜ |

## House (track 2B)

| Asset | Area | Priority | Status |
|---|---|---|---|
| Bed, nightstand, bedside lamp | Bedroom | P1 (first thing seen) | ✅ in game via `assets/models/environment/bedroom.glb` (`source/blender/build_bedroom.py`, 71 KB): wooden bed, blanket, pillows, nightstand with drawer and books, crystal lamp, phone, rug, slippers. Walls, floor and window stay code |
| Sofa, coffee table, plant, rug, painting | Living room | P2 | ⬜ |
| Front double door, windows | Living room | P2 | ⬜ |
| Kitchen cabinets, counter, upper cabinets, fridge | Kitchen | P1 (morning missions) | ✅ in game via `assets/models/environment/house_kitchen.glb` (`source/blender/build_house_kitchen.py`): shaker doors, drawers, oven, stove, hood, tiles, fridge with magnets and a drawing |
| Sink with tap, dish rack | Kitchen | P1 | ✅ in game via `assets/models/environment/house_kitchen.glb` (`source/blender/build_house_kitchen.py`) |
| Dishes (dirty → clean) | Kitchen | P1 | ⬜ |
| Egg carton, eggs, frying pan, fried eggs | Kitchen | P1 | 🟡 carton and pan from Blender (clicks stay on the code shapes); eggs and fried eggs still code (they change during the mission) |
| Bread loaf, toaster, toast | Kitchen | P1 | 🟡 toaster from Blender (click stays on the code shape); bread, slices and toast still code |
| Dining table, chairs, breakfast plate | Kitchen | P2 | ✅ in game via `assets/models/environment/house_kitchen.glb` (`source/blender/build_house_kitchen.py`): table, chairs, fruit bowl, vase, hanging lamp; the breakfast plate stays code (clickable) |
| House exterior, roof, garden trees, path | Outside | P2 (seen while driving) | ⬜ |

## Audio (track 2C)

See [`prompts/04_audio_elevenlabs.md`](../prompts/04_audio_elevenlabs.md) for the full list with prompts.

| Group | Count | Priority |
|---|---|---|
| Kitchen and truck SFX (sizzle, fridge, register, plate, door…) | ~16 | P1 |
| House SFX (dishes, scrub, frying eggs, toaster pop, lamp click, phone buzz) | ~8 | P1 |
| Driving (engine idle and rev, horn, brake) | 4 | P2 |
| Customer voice lines in Spanish (order, thanks, angry), 3+ voices | ~18 | P1 |
| Music: night/tutorial, morning, rush hour | 3 loops | P2 |
| Ambience: night crickets, street | 2 loops | P3 |

## Stays in code (no asset needed)

These stay as code on purpose. They're dynamic, or they already look right.

- Sky and time of day
- Bloom and color grading
- Text on the HUD, the computer, the menu board and the clock
- Speech bubbles and patience bars
- Collisions
