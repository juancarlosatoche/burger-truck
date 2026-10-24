# Instructions for AI assistants working on this repo

This is a kid's game (Ignacio). Keep it his.

## The game

- `index.html` is the whole game: HTML, Tailwind (CDN) and Three.js **r128** from CDN, with no build step.
- Game flow:
  1. Night tutorial
  2. Phone message
  3. Sleep
  4. Morning missions in the kitchen
  5. Drive the truck to the yellow zone
  6. Burger shift from 5 PM to 11 PM: customers, deliveries, upgrades, the in-truck computer with its apps
- Scenes are switched with `currentScene`: `'HOME'`, `'DRIVE'`, `'FOOD_TRUCK'`.
- **Before editing `index.html`, read `docs/MAPA.md`**: which function does what, and the coordinates of every area. Don't read `index.html` top to bottom; jump to the functions the map names. When you add, rename or delete a function, update the map. `python3 tools/revisar_mapa.py` checks it, and GitHub runs it on every pull request.

## Rules

1. **Readable by a kid.** Keep the existing structure and names. Comments in **Spanish**. Mark new code with `✨ NUEVO` and a one-line Spanish explanation.
2. **Don't rewrite working systems** to add art. Swap the visual and keep the logic.
3. **Always keep a fallback.** If a `.glb` or sound fails to load, the code-drawn version must still show, and the game must never crash.
4. **Three.js r128 only.** Load add-ons from `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/...` (for example `loaders/GLTFLoader.js`). Don't use ES-module imports or newer Three.js APIs.
5. **Runtime assets live in `assets/`** and are loaded with relative paths. They must be small: models under 3 MB, SFX under 100 KB.
   - **When you change any `.glb`, update `VERSION_MODELOS` in `index.html`** (for example `?v=2026-10-24a`). Browsers keep old copies of models; without a new version, players get new code with old models.
6. **No API keys, ever.** The repo is public.
7. **Steer with images.** Before changing visuals:
   - read the style target in `reference/style-targets/`;
   - after the change, take a screenshot from the same angle into `reference/screenshots/`;
   - compare the two and list the concrete differences.
8. **One asset family per change.** Update the status in `docs/ASSET_LIST.md` and record decisions in `docs/DECISIONS.md`.

## Blender scripts

- Every model is built by a script `source/blender/build_<name>.py`. **Start new ones by copying `source/blender/_plantilla.py`.**
- Shared tools (`box`, `cyl`, `beam`, `prism`, `text`, `mat`, `empty`, `limpiar`, `guardar`, `exportar_para_juego`, `REPO`) live in **`source/blender/lib_blender.py`**. Scripts import them with `from lib_blender import *`. **Never copy them into a build script.** A shape useful for several models goes into `lib_blender.py`.
- Before committing, run `python3 tools/revisar_blender.py`. GitHub runs it on every pull request (`.github/workflows/revisar.yml`) and it fails if a script redefines a shared tool, exports on its own, or doesn't import the library.
- Scripts run from the terminal too: `pip install bpy` (Python 3.13), then `python3 source/blender/build_<name>.py`. The export is deterministic, so if you change `lib_blender.py`, re-run all scripts and check that the `.glb` files you didn't mean to change stay byte-identical.

## Testing

**Use `tools/probar.py`. Don't write a new test or screenshot script.** It serves the game, opens it in a headless browser, and reports console errors and models that failed to load.

- `python3 tools/probar.py --lista`: the named camera views and gameplay tests.
- `python3 tools/probar.py freidora plato`: photos from named views, combined into **one** image, `tools/capturas/hoja.png`. Look at that one image, not each photo.
- `python3 tools/probar.py --prueba todas`: gameplay tests (burger, fries, combo, plate rules).
- Options: `--hora 21`, `--js "<code run before each photo>"`, `--ancho 420` (smaller = faster and fewer tokens), `--referencia` (copies each photo to `reference/screenshots/<view>_<date>.png` for rule 7), `--interfaz` (keep the HUD).
- Exit code 1 means a console error, a model that failed, or a failed test.
- **One-off angle:** `--ojo x,y,z --mira x,y,z` (add `--en truck` for truck measurements, `--escena casa` for the house). No need to edit the tool.
- Views are aimed at *places*, so a new model in the same spot needs no change. Add a view to `VISTAS` only for an area you'll photograph again and again. **New mechanic?** Add a test to `PRUEBAS`.
- Without internet for the CDNs, it downloads Three.js r128 into `tools/.vendor/` with npm. In the cloud there's no graphics card, so rendering is slow (about 15 s per view); it's much faster on a normal computer.
- Setup: `pip install playwright pillow`, then `python3 -m playwright install chromium`.
- Still play the whole loop by hand once in a real browser before a big merge: tutorial → missions → drive → serve one customer.

## Where the pipeline is described

`docs/PIPELINE.md` (stages), `docs/ASSET_LIST.md` (what to make), `prompts/` (ready prompts).
