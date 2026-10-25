# Mapa de `index.html`

**Read this before editing `index.html`** (about 3,300 lines). Jump to a place with `grep -n "function nombre" index.html`, or search for the comment text shown between « » (a landmark). There are no line numbers here on purpose: they change with every edit.

`tools/revisar_mapa.py` checks that every name and landmark here still exists, and that every function in `index.html` is listed. **When you add, rename or delete a function, update this file.**

## Coordinates (where things are in the world)

| Place | Where | Notes |
|---|---|---|
| House | around `(0, 0, 0)`; bedroom `x>1`, living room `x<1`, kitchen-dining `z≈-8` | Eye height `HOME_EYE` = 2.1. Front door at `z=5` |
| Food truck, parked | `foodTruckGroup` at `(50, 0, 50)`, rotation 0 | Scale `(TRUCK_SCALE, TRUCK_HEIGHT, TRUCK_SCALE)` = (2, 1.8, 2). Truck parts use **truck measurements**: x across (−1.4 back wall … +1.4 service window), z along (−2.75 driver side … +2.75 rear door), y up (counter top ≈ 0.9) |
| Truck kitchen (truck measurements) | fridge `(-0.95, 1.0, -2.1)`, grill `(-0.95, 0.94, 0.2)`, fryer `(-0.95, 0.9, 1.08)`, plate `(0.9, 0.9, 0)`, computer `(0.93, 1.16, 0.85)`, fries boxes `(0.92, 0.9, 0.5)` | Eye height inside `TRUCK_EYE` = 2.6 (world) |
| Plaza (world) | customers queue at `x≈54, z≈50`; tables `x=59`; trees `x 63–70`; buildings `x 82–85, z 30–73`; street behind `z≈78` | Plaza models are not scaled: 1 Blender metre = 1 game unit |
| Drive start | truck at `(14, 0, 24)`, target zone at `(50, 50)` | `drive` object holds speed and heading |
| Forest and dirt road | dirt road from `(2, 21)` east, then south along `x≈36`, ending on the paved yard behind the plaza (`pave2`, `x 37–73, z 56–74`) at `(44, 67)`; pond `(18, 41)`; mushroom clearing `(24, 61)` | Blender model `bosque.glb`. No trees on the road, the plaza block `x 42–100, z 26–88` or the house `x −16–18, z −16–20` |

Scenes: `currentScene` is `'HOME'`, `'DRIVE'` or `'FOOD_TRUCK'`. `setSceneLights()` switches lights; `setTimeOfDay()` sets sky and lamps from the hour.

## If you want to change…

### Food, recipes and the plate
- **Menu, prices, combos:** `RECIPES` (+ `LBL` names, `EMO` emojis). `esCombo()`, `COMBO_TIEMPO_EXTRA`.
- **Does the plate match a recipe:** `platoCoincide()`. Messages when something is placed: `avisarPlato()`.
- **Ingredients in the fridge (shape, colour, shelf):** `INGREDIENT_DEFS`, filled by `restockAll()`, counted by `stockCount()`.
- **Food textures:** `foodMat()`.
- **Putting things on the plate:** `placeItemOnPlate()`. **Holding things:** `pickUpItem()`, `updateHeld3DMesh()`, `dropHeldItem()`, `updateHoldingUI()`.
- **Grill:** `cookPattyOnGrill()`, `pickUpCookedPatty()`.
- **Fries:** `construirFreidora()`, `usarFreidora()`, `actualizarFreidora()` (timer `TIEMPO_FREIR`), colour raw → golden `pintarPapasFreidora()`, `construirCajasPapas()`, `usarCajaPapas()`, `hacerCajaPapas()`, `hacerPalitos()`.

### Clicking and the cross-hair prompt
- **What a click does in the truck:** `handleWorldInteraction()` (by `userData.type`: 'FRIDGE_DOOR', 'INGREDIENT', 'GRILL', 'FRYER', 'FRIES_BOX', 'PLATE', 'CLIENT', 'DELIVERY', 'COMPUTER').
- **Prompt text when aiming:** `checkInteractionRaycast()`. Clickable things are in `interactableObjects`.
- **Clicks in the house:** `homeAPI` (inside `init()`, landmark «🌙 Fases»).
- **Pop-up messages:** `showBannerNotification()`.

### Customers, money and the day
- **Customer bodies and faces:** `makePerson()`, `animatePerson()`, Tripo models `ponerModeloCliente()` (`ARCHIVOS_CLIENTES`).
- **Queue:** `spawnCustomer()`, `fillQueue()`, `updateCustomers()`, `releaseCustomer()`, `custLabel()`, positions `CUST_Z`.
- **Speech bubble:** `makeBubble()`.
- **Serving and tips:** `serveCustomer()`.
- **Clock, day, money HUD:** `updateTycoon()`, `drawClock()`, `setHud()`. Day runs 5 PM–11 PM.
- **Upgrades:** `UPG`, `renderMejoras()`, `buyUpgrade()`; "Ampliar" stretches the truck in `applyTruckExt()`.
- **Supply delivery:** `doOrder()`, `updateDelivery()`, `collectDelivery()`, `missingUnits()`.

### The computer (FoodOS)
- `openPC()`, `closePC()`, `openApp()`; apps `renderEntrega()`, `renderRecetas()`, `renderPedidos()` (+ `deliverOrder()`, `CLIENTES`, `CALLES`), `renderMejoras()`, `startSnake()`, `stopSnake()`.
- Recipe pinned on screen: `pinRecipe()`, `updateRecipeHUD()`. Monitor texture: `updateComputerScreen()`.

### House and morning missions
- **House walls and furniture (code-drawn):** inside `init()`, from landmark «Outer Walls» to «Jardín frente a la casa». Collision boxes: «Cajas de choque», used by `collideHome()`.
- **Kitchen-dining and missions (plates, breakfast), tutorial, phone, sleep:** inside `init()`, from landmark «🏠 AMPLIACIÓN» to «Cielo, mano y post-procesado».
- **Front door:** `updateDoor()`. Sun beam and dust: `buildSunBeam()`, `updateDust()`. Waking up: `startWakeUpSequence()`.

### Food truck and plaza (code-drawn)
- **Truck kitchen layout:** `buildFoodTruckKitchen()`. Rear door: `updateTruckDoor()`.
- **Truck body:** `buildTruckExterior()`. **Plaza, buildings, lamps, street:** `buildTruckSurroundings()`.
- **Steel, tile, grill textures:** `truckTex()`. Any canvas texture: `makeTex()`, `speckle()`.

### Driving
- `startDriving()`, `driveUpdate()`, yellow target `buildDriveZone()`. Arrival calls `teleportToFoodTruck()`.

### Blender models (each one hides its code-drawn version when it loads)
- Entry point `cargarModelos()`; version string `VERSION_MODELOS` (**bump it when a `.glb` changes**). Helper `piezaDeModelo()`.
- `cargarModeloTruck()`, `cargarModeloCabina()`, `cargarModeloCocina()`, `cargarModeloPlaza()`, `cargarModeloEdificios()`, `cargarModeloBosque()` (forest and dirt road, drawn as instanced copies by 100 m zones), `cargarModeloDormitorio()`, `cargarModeloCocinaCasa()`, `cargarModeloFreidora()`, `cargarModeloPapasCrudas()` (+ `vestirPapasCrudas()`), `cargarModeloPapasFritas()` (+ `vestirCajaPapas()`: fries box, fries in the box, in the hand and in the fryer basket), `cargarModeloManos()` (+ `ponerManosVolante()`: player hands for cooking and on the steering wheel).

### Look: light, sky, glow
- Sky and stars: `buildSky()`. Hour → colours and lamps: `setTimeOfDay()`, table `TOD`. Lamps that glow at dusk are registered in `lampMats` / `lampLights`.
- Bloom and colour grading: `setupPost()`. Reflections: `buildEnvMap()`, `shiny()`.
- First-person hand: `buildHand()`, `updateHand()`. Blender hands: `cargarModeloManos()`; the wheel hands turn `GIRO_MANOS` (35%) as much as the wheel.

### Startup, controls, main loop
- `init()` builds everything and sets up the controls (landmarks «Joystick virtual», «Mirar arrastrando»). Main loop: `animate()`. Window size: `onWindowResize()`.
- Mouse lock and its fallback: `safeLock()`, `enableFallback()`, `lockFailedNotice()`.
