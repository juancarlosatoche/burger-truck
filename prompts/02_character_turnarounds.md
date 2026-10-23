# Stage 2A: Character turnaround sheets (for Tripo)

**Tool:** image generator, then Tripo
**Save to:** `reference/turnarounds/<character>.png` → Tripo export to `source/tripo/<character>.glb`

## Why turnarounds

Tripo builds a much more accurate 3D model when it can see the character from all sides. Chong-U always gives it **front, side, back and ¾ views**, especially for anything at the back like hair buns, caps or ponytails.

## Template

Replace `{STYLE}` with the style line chosen in Stage 1, and `{CHARACTER}` with a description from the list below.

> Character turnaround sheet for a 3D game model. Four views of the same character side by side, evenly spaced, full body, same scale: front view, left side view, back view, three-quarter front view. Neutral A-pose with arms slightly away from the body. Plain light-grey background, even soft lighting, no shadows on the floor, no text, no labels.
> Character: {CHARACTER}
> {STYLE}

**Tips:**

- Keep the **A-pose**. Tripo and Blender rigging work best with arms slightly away from the body.
- Same proportions for every customer: big head, short body, chunky shoes. One skeleton then fits all of them.
- If one view comes out inconsistent, regenerate just that sheet. Don't mix views from different generations.

## Characters

1. **Customer A:** "a cheerful young adult with short messy hair, colorful t-shirt, jeans, sneakers, friendly big eyes."
2. **Customer B:** "a kind middle-aged person with a hair bun, cardigan, long skirt or trousers, small round glasses."
3. **Customer C:** "a teenager with a backwards baseball cap, hoodie, shorts and high-top sneakers."
4. **Delivery driver:** "a delivery worker in an orange uniform polo and cap, dark work trousers, sturdy boots, gloves."
5. **Player hand (first person):** generate a separate image: "a single cartoon right hand and forearm with a red sleeve and cream cuff, palm up as if holding something, three views: top, side, front; plain grey background."

## Tripo settings

- **Mode:** Image to 3D, multi-view if available. Upload all four views.
- **Target:** stylized; enable texture.
- **Download:** `.glb` into `source/tripo/`.

Tripo's auto-rig is fine for quick tests. For the final characters, rig in Blender with **one shared skeleton**; see `docs/PIPELINE.md` stage 2A.
