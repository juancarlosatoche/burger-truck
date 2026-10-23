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
