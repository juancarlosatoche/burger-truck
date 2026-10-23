# Asset pipeline (adapted from Chong-U)

Chong-U's workflow, adapted to this game: Three.js in one HTML page instead of Rust/WASM, and single-player, so his multiplayer and netcode steps don't apply.

```
Stage 0  Graybox ................ DONE (v5: all game mechanics work with code-drawn art)
Stage 1  Art direction .......... 4 mockups → pick 1 → style target
Stage 2  Assets IN PARALLEL ..... 2A characters │ 2B environment & props │ 2C audio
Stage 3  Integration ............ load .glb / audio into index.html, one asset family at a time
Stage 4  Steering loop .......... screenshot vs. style target → fix → repeat
Stage 5  Feel polish ............ exaggerated animations, sockets, juice
```

His key lesson: **telling the AI to "make it look better" doesn't work. Giving it a target image does.** Every stage below produces or uses a reference image.

---

## Stage 0: Graybox ✅

`index.html` (v5) is the graybox. Every mechanic works with art drawn in code:

- night tutorial
- phone message and sleep
- morning missions
- driving the truck
- serving customers
- deliveries
- upgrades
- the computer with its apps

Chong-U's test: the game should be fun **before** the art goes in. Play it and note anything that isn't fun in `docs/DECISIONS.md` before investing in assets.

## Stage 1: Art direction

| | |
|---|---|
| **Tool** | Image generator |
| **Prompt** | [`prompts/01_art_direction.md`](../prompts/01_art_direction.md) |
| **Output** | `reference/mockups/` (4 images) → chosen one copied to `reference/style-targets/` |
| **Done when** | One style target is chosen and the style is written down in `docs/DECISIONS.md` (colors, materials, lighting, proportions) |

1. Generate **4 distinct** mockups of the same scene (truck window, customers, dusk), one per style.
2. Pick one. You can also mix two, as Chong-U did: "between this one and this one".
3. Generate 2–3 more images in the chosen style for the **other scenes**: bedroom at night, kitchen in the morning, truck exterior while driving. These become the style targets for Stage 4.

**Everything after this depends on the style target, so don't skip it.**

## Stage 2: Assets, in parallel

The three tracks don't depend on each other, so run them at the same time.

### 2A: Characters (image generator → Tripo → Blender)

| | |
|---|---|
| **Prompt** | [`prompts/02_character_turnarounds.md`](../prompts/02_character_turnarounds.md) |
| **Output** | `reference/turnarounds/` → `source/tripo/` → `source/blender/characters.blend` → `assets/models/characters/*.glb` |

1. **Turnaround sheet per character:** front, side, back and ¾ view on a plain background, in the chosen style. Start with the 3 customer types and the delivery driver.
2. **Tripo** (image → 3D): upload the turnaround and download the `.glb` into `source/tripo/`.
3. **Blender:**
   - **One shared skeleton for all characters**, so the same animations work on every mesh. This was Chong-U's main rule.
   - Animations: `idle`, `walk`, `impatient`, `happy_jump`, `angry_stomp`, `wave`, `carry`.
   - Add an empty named `hand_R` in the right hand as the **socket** for held objects (the delivery crate, a burger).
4. **Export** each character as `.glb` into `assets/models/characters/`, with the animations included. Aim for under 3 MB each.

### 2B: Environment & props (image generator → Blender)

| | |
|---|---|
| **Prompt** | [`prompts/03_environment_props.md`](../prompts/03_environment_props.md) |
| **Output** | `reference/environment/`, `reference/props/` → `source/blender/*.blend` → `assets/models/props/`, `assets/models/environment/` |

1. **Reference images:** generate isolated props on a plain background and one layout image per area.
2. **Blender:** model **modular** pieces (counter section, wall panel, umbrella table) so they can be reused.
   - Avoid copy-paste repetition: vary the trees and props.
   - Chong-U's note: "stop having repetitive things."
3. **Export** to `.glb`. Bake simple textures. Keep each prop under 1 MB.

**Priority order** (most visible first):

1. Food truck exterior and interior
2. Ingredients
3. Plaza: umbrellas, lights, trees
4. House kitchen
5. Bedroom

### 2C: Audio (ElevenLabs)

| | |
|---|---|
| **Prompt** | [`prompts/04_audio_elevenlabs.md`](../prompts/04_audio_elevenlabs.md) |
| **Output** | `source/audio-raw/` (originals) → `assets/audio/{sfx,voice,music}/` (trimmed `.mp3`, mono for SFX) |

Generate the clips in the ElevenLabs website and download them. **Never put the API key in the game.**

## Stage 3: Integration

Bring in **one asset family per change**, so each can be tested and undone:

1. Ingredients and plate
2. Truck
3. Customers
4. Delivery driver
5. Plaza
6. House
7. Audio

- Three.js r128 needs `GLTFLoader` (`three@0.128.0/examples/js/loaders/GLTFLoader.js`) and an `AnimationMixer` per character.
- Keep the code-drawn version as a **fallback** if a model fails to load, so the game never breaks.
- Test through `python -m http.server`, not by double-clicking the file.

## Stage 4: Steering loop

For each area:

1. Take a screenshot in the same camera angle as its style target and save it to `reference/screenshots/<area>_<date>.png`.
2. Put it side by side with the target and list concrete differences: "shadows too dark", "water is a flat plane", "trees are copy-pasted".
3. Give the AI **both images plus the list**. Re-screenshot and repeat until it matches.

## Stage 5: Feel polish

- **Exaggerated animations:** easy to read and whimsical (Chong-U's rule).
- **Socket check:** held items are actually in the hand and disappear when thrown or delivered.
- **Juice:** particles, squash and stretch, pop-ups. Sounds wired to every action.

---

## Commit conventions

- One asset or one change per commit. Example: `add: customer_a.glb with idle/walk`.
- Commit the **reference image together with** the asset made from it, so you can always see where it came from.
- Tag playable milestones: `v5-graybox`, `v6-art-direction`, `v7-characters`, and so on.
