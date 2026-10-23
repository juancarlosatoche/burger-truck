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

## Rules

1. **Readable by a kid.** Keep the existing structure and names. Comments in **Spanish**. Mark new code with `✨ NUEVO` and a one-line Spanish explanation.
2. **Don't rewrite working systems** to add art. Swap the visual and keep the logic.
3. **Always keep a fallback.** If a `.glb` or sound fails to load, the code-drawn version must still show, and the game must never crash.
4. **Three.js r128 only.** Load add-ons from `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/...` (for example `loaders/GLTFLoader.js`). Don't use ES-module imports or newer Three.js APIs.
5. **Runtime assets live in `assets/`** and are loaded with relative paths. They must be small: models under 3 MB, SFX under 100 KB.
6. **No API keys, ever.** The repo is public.
7. **Steer with images.** Before changing visuals:
   - read the style target in `reference/style-targets/`;
   - after the change, take a screenshot from the same angle into `reference/screenshots/`;
   - compare the two and list the concrete differences.
8. **One asset family per change.** Update the status in `docs/ASSET_LIST.md` and record decisions in `docs/DECISIONS.md`.

## Testing

- Serve it locally, because file:// blocks loading models: `python -m http.server 8000` → http://localhost:8000
- Check the browser console for errors.
- Play the whole loop at least once: tutorial → missions → drive → serve one customer.

## Where the pipeline is described

`docs/PIPELINE.md` (stages), `docs/ASSET_LIST.md` (what to make), `prompts/` (ready prompts).
