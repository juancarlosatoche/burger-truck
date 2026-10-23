# The chosen style: "cozy dusk, stylized low-poly"

**Style target:** [`reference/style-targets/truck_window_dusk.jpg`](../reference/style-targets/truck_window_dusk.jpg)

This file is the single source of truth for the look of the game.

**When you use an image generator:**

- Paste the **style line** at the end of every prompt in `prompts/` (it replaces `{STYLE}`).
- **Attach the style target image too**, and add: *"Match the art style of the attached image."* Generators keep a style much more consistently with an image than with words alone.

## Style line (copy this)

> Style: stylized 3D game art with a cozy dusk mood. Trees, bread and simple props use soft faceted low-poly shapes with smooth gradient shading; characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Lighting: deep indigo-to-sunset-orange sky, warm amber practical lights (string bulbs, street lamps, kitchen lights) with gentle bloom, soft shadows, light ambient occlusion. No outlines, no text.

## The style in detail

| Aspect | What we see in the target | Rule for new assets |
|---|---|---|
| **Shapes** | Two levels of detail. Environment and props are low-poly with visible facets (trees, bread loaf). Characters and food are smooth and rounded. | Props and environment: low-poly, about 200–2,000 triangles each. Characters and food: smooth, but still simple. |
| **Characters** | About 5 heads tall, slightly big heads, simple faces (dot-ish eyes, small smile), casual clothes in muted colors (green hoodie, blue jacket), varied skin tones and hair. | One shared body type, so one skeleton fits all. Vary outfit, hair and skin. |
| **Palette** | Sky: deep navy and indigo, with orange and pink at the horizon. Interior: warm amber, cream and tan. Accents: food reds, greens and yellows. | Keep saturation for **food and accents only**. Walls, furniture and the street stay muted. |
| **Materials** | Brushed steel counters and trays, warm wood window frame and shelves, matte walls, slightly glossy food. | Steel: metallic with soft reflections. Wood: warm and slightly rough. No plastic-looking shine. |
| **Lighting** | Dusk sky, warm lights everywhere (string bulbs, street lamp, ceiling strip), soft shadows and gentle glow on the bulbs. | The game's time-of-day system and bloom already match this direction. Tune toward the target, not away from it. |
| **Camera** | First person, eye level, looking through the service window over the counter. | Re-shoot comparison screenshots from this angle (see `docs/PIPELINE.md` stage 4). |

## Ideas the mockup suggests (not decided yet)

These appeared in the image but aren't in the game. Note them, but don't add them without deciding first.

- **Fries and drinks** in the orders. The game has only burgers today, though the soda machine already exists.
- **Ingredient trays** on the counter (lettuce, tomato, cheese, patties) instead of taking everything from the fridge.
- **Hinged service window** with a prop rod, an extractor hood, and shelves with jars and utensils.
- The **order screen** on the computer showing the customer's picture.
