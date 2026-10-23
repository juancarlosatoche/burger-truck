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
| Customer A, B, C (green hoodie, blue jacket, pink sweater) | Truck window queue | P1 | idle, walk, impatient (tap foot, arms crossed), happy_jump, angry_stomp, wave | 🖼️ `reference/turnarounds/customer_a\|b\|c` |
| Delivery driver | Behind the truck | P2 | walk, idle, carry (crate in `hand_R`) | 🖼️ `reference/turnarounds/delivery_driver` |
| Player hands (first person) | Holding ingredients; both hands on the steering wheel while driving (see `driving_first_person.jpg`) | P1 | grab, hold (socket `hand_R`), steer (both hands) || 🖼️ `reference/turnarounds/player_hands.png` |
| Friend (phone avatar, 2D) | Phone message | P3 | (image only) | ⬜ |

## Food truck (track 2B)

| Asset | Priority | Notes | Status |
|---|---|---|---|
| Truck exterior: body, cab, wheels, canopy, sign | P1 | Look defined by `truck_exterior_night.jpg`: red lower body, cream upper body, faceted shapes, hinged service window with awning, lit "BURGER TRUCK" sign topped with a burger. Must allow the **"Ampliar"** upgrade: build it in **front / middle / rear** modules so the middle can be stretched or repeated | 🖼️ |
| Truck cab interior: steering wheel, dashboard with speedometer, rear-view mirror with burger air-freshener, side mirror, windshield frame, visible hood | P1 | **New** (first-person driving). Look defined by `driving_first_person.jpg` | 🖼️ |
| Truck interior: walls, floor, ceiling lights | P1 | Same modular rule | ⬜ |
| Fridge with opening door | P1 | Door as a separate object (it animates) | ⬜ |
| Grill (flat-top) | P1 | | ⬜ |
| Service counter, plate | P1 | | ⬜ |
| Ingredients: bun bottom, bun top, raw patty, cooked patty, cheese, lettuce, tomato | P1 | 7 small models, each must also look right in the hand | ⬜ |
| Cash register, soda machine, ketchup, mustard | P2 | | ⬜ |
| Computer (monitor + keyboard) | P2 | Screen stays a canvas texture drawn in code | ⬜ |
| Rear door with window, EXIT sign, wall clock | P2 | Clock face stays drawn in code (it shows game time) | ⬜ |

## Plaza and street (track 2B)

| Asset | Priority | Status |
|---|---|---|
| Umbrella tables with stools (×2) | P2 | ⬜ |
| String lights on poles | P2 | ⬜ |
| Street lamps | P2 | ⬜ |
| Menu chalkboard (text stays drawn in code) | P2 | ⬜ |
| Trees (3–4 varieties, not copy-paste) | P2 | ⬜ |
| Planters, trash bin | P3 | ⬜ |
| Background buildings with lit windows | P3 | ⬜ |
| Road, sidewalk, grass textures | P2 | ⬜ |
| Yellow parking zone and arrow (driving) | P3 | Can stay in code | ⬜ |

## House (track 2B)

| Asset | Area | Priority | Status |
|---|---|---|---|
| Bed, nightstand, bedside lamp | Bedroom | P1 (first thing seen) | ⬜ |
| Sofa, coffee table, plant, rug, painting | Living room | P2 | ⬜ |
| Front double door, windows | Living room | P2 | ⬜ |
| Kitchen cabinets, counter, upper cabinets, fridge | Kitchen | P1 (morning missions) | ⬜ |
| Sink with tap, dish rack | Kitchen | P1 | ⬜ |
| Dishes (dirty → clean) | Kitchen | P1 | ⬜ |
| Egg carton, eggs, frying pan, fried eggs | Kitchen | P1 | ⬜ |
| Bread loaf, toaster, toast | Kitchen | P1 | ⬜ |
| Dining table, chairs, breakfast plate | Kitchen | P2 | ⬜ |
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
