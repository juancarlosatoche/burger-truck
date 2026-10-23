# The chosen style: D, "Cozy low-poly with glow"

**Style target:** [`reference/style-targets/truck_window_dusk.jpg`](../reference/style-targets/truck_window_dusk.jpg)

**Original prompt that produced it:** the shared scene from `01_art_direction.md` plus:

> Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and sign, volumetric warm light, soft fog, cozy sunset mood.

The style line below keeps that wording and adds what the image actually shows, such as the smooth characters and the materials. That way, scenes that aren't the truck window still come out matching.

This file is the single source of truth for the look of the game.

**When you use an image generator:**

- Paste the **style line** at the end of every prompt in `prompts/` (it replaces `{STYLE}`).
- **Attach the style target image too**, and add: *"Match the art style of the attached image."* Generators keep a style much more consistently with an image than with words alone.

## Style line (copy this)

> Style: stylized low-poly 3D, faceted shapes with smooth gradient lighting, strong bloom on the string lights and signs, volumetric warm light, soft fog, cozy sunset mood. Characters are smooth, rounded and friendly, with simple faces, slightly large heads and soft clothing folds. Materials: brushed stainless steel, warm wood, matte painted walls, fresh saturated food colors. Deep indigo-to-sunset-orange sky, warm amber lights, soft shadows. No outlines, no text.

## The style in detail

| Aspect | What we see in the target | Rule for new assets |
|---|---|---|
| **Shapes** | Two levels of detail. Environment and props are low-poly with visible facets (trees, bread loaf). Characters and food are smooth and rounded. | Props and environment: low-poly, about 200–2,000 triangles each. Characters and food: smooth, but still simple. |
| **Characters** | About 5 heads tall, slightly big heads, simple faces (dot-ish eyes, small smile), casual clothes in muted colors (green hoodie, blue jacket), varied skin tones and hair. | One shared body type, so one skeleton fits all. Vary outfit, hair and skin. |
| **Palette** | Sky: deep navy and indigo, with orange and pink at the horizon. Interior: warm amber, cream and tan. Accents: food reds, greens and yellows. | Keep saturation for **food and accents only**. Walls, furniture and the street stay muted. |
| **Materials** | Brushed steel counters and trays, warm wood window frame and shelves, matte walls, slightly glossy food. | Steel: metallic with soft reflections. Wood: warm and slightly rough. No plastic-looking shine. |
| **Lighting** | Dusk sky, warm lights everywhere (string bulbs, street lamp, ceiling strip), soft shadows, **strong glow** on bulbs and signs, warm haze and soft fog in the distance. | The game's time-of-day system, bloom and fog already exist. Push them toward the target: stronger bloom on lights, warmer fog. |
| **Camera** | First person, eye level, looking through the service window over the counter. | Re-shoot comparison screenshots from this angle (see `docs/PIPELINE.md` stage 4). |

## Ideas the mockup suggests (not decided yet)

These appeared in the image but aren't in the game. Note them, but don't add them without deciding first.

- **Fries and drinks** in the orders. The game has only burgers today, though the soda machine already exists.
- **Ingredient trays** on the counter (lettuce, tomato, cheese, patties) instead of taking everything from the fridge.
- **Hinged service window** with a prop rod, an extractor hood, and shelves with jars and utensils.
- The **order screen** on the computer showing the customer's picture.
