# Stage 2A: Character turnaround sheets (for Tripo)

**Tool:** image generator, then Tripo
**Save to:** `reference/turnarounds/<character>.png` → Tripo export to `source/tripo/<character>.glb`

## Why turnarounds

Tripo builds a much more accurate 3D model when it can see the character from all sides. Chong-U always gives it **front, side, back and ¾ views**, especially for anything at the back like hair buns, caps or ponytails.

## How to generate each sheet

1. **Attach** `reference/style-targets/truck_exterior_night.jpg`. The 3 customers come from that image, so the generator can copy their exact look.
2. Paste the **full prompt** for the character (below). Each one already includes the shared turnaround instructions and the style.
3. Save the result as `reference/turnarounds/<file name>.png`.

**Tips:**

- **A-pose** (arms slightly away from the body) on every sheet. Tripo and Blender rigging work best that way.
- **Same body proportions** for everyone (about 5 heads tall, slightly large head). One shared skeleton then fits all of them, which was Chong-U's main rule.
- If one view comes out different from the others (a different hairstyle in the back view, say), regenerate the **whole sheet**. Don't mix views from different generations.
- Tripo may ask for **separate pictures** per view instead of one sheet. If so, send the sheet to Claude and it will crop it into 4 images.

## The characters

### 1. Customer A: green hoodie (`customer_a.png`)

> Match the art style of the attached image. Character turnaround sheet for a 3D game model of the woman in the green hoodie from the attached image. Four views of the same character side by side, evenly spaced, full body, same scale: front view, left side view, back view, three-quarter front view. Neutral A-pose with arms slightly away from the body. Character: a cheerful young woman, shoulder-length straight brown hair with a side part, light skin, simple friendly face with small dark eyes and a soft smile, bright green hoodie with a front pocket, grey slim jeans, green sneakers. Body about 5 heads tall with a slightly large head. Smooth, rounded, stylized low-poly 3D look with soft gradient shading. Plain light-grey background, even soft lighting, no shadows on the floor, no text, no labels.

### 2. Customer B: blue jacket (`customer_b.png`)

> Match the art style of the attached image. Character turnaround sheet for a 3D game model of the man in the blue jacket from the attached image. Four views of the same character side by side, evenly spaced, full body, same scale: front view, left side view, back view, three-quarter front view. Neutral A-pose with arms slightly away from the body. Character: a friendly young man, short brown hair with a small quiff, light tan skin, simple friendly face with small dark eyes and a soft smile, slate-blue denim jacket over a white t-shirt, dark blue jeans, brown leather shoes. Body about 5 heads tall with a slightly large head. Smooth, rounded, stylized low-poly 3D look with soft gradient shading. Plain light-grey background, even soft lighting, no shadows on the floor, no text, no labels.

### 3. Customer C: pink sweater (`customer_c.png`)

> Match the art style of the attached image. Character turnaround sheet for a 3D game model of the person in the pink sweater from the attached image. Four views of the same character side by side, evenly spaced, full body, same scale: front view, left side view, back view, three-quarter front view. Neutral A-pose with arms slightly away from the body. Character: a cheerful young person with short dark curly hair, dark brown skin, simple friendly face with small dark eyes and a soft smile, dusty-pink crewneck sweater, blue jeans, navy and white sneakers. Body about 5 heads tall with a slightly large head. Smooth, rounded, stylized low-poly 3D look with soft gradient shading. Plain light-grey background, even soft lighting, no shadows on the floor, no text, no labels.

### 4. Delivery driver (`delivery_driver.png`)

Not in any image yet. Attach the same exterior image for the style only.

> Match the art style of the attached image, using the same body proportions as the customers in it. Character turnaround sheet for a 3D game model. Four views of the same character side by side, evenly spaced, full body, same scale: front view, left side view, back view, three-quarter front view. Neutral A-pose with arms slightly away from the body. Character: a friendly delivery worker, orange uniform polo shirt with a small box logo on the chest, orange cap, dark grey work trousers with side pockets, sturdy brown boots, work gloves, medium skin, short black hair, simple friendly face with a big smile. Body about 5 heads tall with a slightly large head. Smooth, rounded, stylized low-poly 3D look with soft gradient shading. Plain light-grey background, even soft lighting, no shadows on the floor, no text, no labels.

### 5. Player hands (`player_hands.png`)

Attach `reference/style-targets/driving_first_person.jpg` instead. The hands should match the ones on the steering wheel.

> Match the art style of the hands on the steering wheel in the attached image. Game asset reference sheet of a pair of first-person player hands and forearms: light skin, blue long sleeves ending at the wrist. Show them in three poses side by side: (1) both hands open, palms down, front view; (2) right hand palm up as if holding a small burger, side view; (3) both hands gripping an invisible steering wheel, front view. Smooth, rounded, stylized low-poly 3D look with soft gradient shading. Plain light-grey background, even soft lighting, no text, no labels.

## Tripo settings

- **Mode:** Image to 3D, multi-view if available. Upload all four views.
- **Target:** stylized; enable texture.
- **Download:** `.glb` into `source/tripo/`.

Tripo's auto-rig is fine for quick tests. For the final characters, rig in Blender with **one shared skeleton**; see `docs/PIPELINE.md` stage 2A.
