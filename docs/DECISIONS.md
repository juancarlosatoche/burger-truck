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

## Art direction (Stage 1)

- [ ] Chosen mockup: `reference/mockups/…`
- [ ] Style in words: palette, materials, lighting, proportions, outline yes/no
- [ ] Style line to paste into every later prompt:
  > Style: …

## Graybox notes (play v5 and write what isn't fun yet)

-
