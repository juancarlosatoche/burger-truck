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
- [ ] **Next:** generate the other 4 style targets (bedroom at night, kitchen in the morning, driving, truck exterior) using the style line and this image as reference.

## Graybox notes (play v5 and write what isn't fun yet)

-
