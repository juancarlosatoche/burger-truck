# 🍔 Burger Truck — Casa 3D Primera Persona

A first-person game made by Ignacio: wake up at night, learn the controls, sleep, do the morning chores, drive your food truck to its spot and run a burger business until 11 PM.

Built with plain HTML + [Three.js r128](https://threejs.org/). No install, no build step.

## Play

- **Online:** once GitHub Pages is on → `https://juancarlosatoche.github.io/burger-truck/`
- **On your computer:** open a terminal in this folder and run
  ```
  python -m http.server 8000
  ```
  then open <http://localhost:8000>. (Double-clicking `index.html` works today, but once the game loads 3D models and sounds from `assets/`, browsers block that unless it's served this way.)

## Where things are

| Folder | What goes there |
|---|---|
| `index.html` | The game (v5 is the baseline) |
| `reference/` | Generated images that guide the art: mockups, style targets, turnaround sheets, environment and prop references, before/after screenshots |
| `source/` | Working files: Blender projects, raw Tripo exports, raw audio. Heavy files here go through Git LFS |
| `assets/` | Final files the game loads: `.glb` models, textures, `.mp3`/`.ogg` sounds. Keep them small |
| `prompts/` | Ready-to-use prompts for the image generator, Tripo and ElevenLabs |
| `docs/` | The pipeline, the asset list and the decision log |

## How we're improving it

We follow the asset pipeline from Chong-U's video (see [`docs/PIPELINE.md`](docs/PIPELINE.md)): pick an art direction from generated mockups, then make characters, props, environment and sound in parallel, and bring them into the game one at a time while comparing against the reference images.

## Rules of the house

- The game stays **readable by Ignacio**: Spanish comments, same structure, new parts marked `✨ NUEVO`.
- **No API keys** in the code or the repo. Generate assets in each tool's website and commit the files.
- Every visual change gets a **before/after screenshot** in `reference/screenshots/`.
