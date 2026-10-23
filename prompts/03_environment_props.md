# Stage 2B: Environment & prop references (for Blender)

**Tool:** image generator, then Blender
**Save to:** `reference/props/<prop>.png`, `reference/environment/<area>.png`

These images tell the modeler (you, or an AI working in Blender) **what to build**. Add the style line from Stage 1 at the end of every prompt.

## Prop sheets (isolated objects)

> Game prop reference sheet: {OBJECTS}, each object isolated, shown in front and three-quarter view, plain light-grey background, soft even lighting, no text. {STYLE}

Suggested batches (one image each):

1. **Ingredients:**
   - bottom bun
   - top bun with sesame seeds
   - raw beef patty
   - grilled beef patty with grill marks
   - cheese slice
   - lettuce leaf
   - tomato slice
2. **Truck kitchen:**
   - stainless steel fridge (door open and closed)
   - flat-top grill
   - cash register
   - soda dispenser
   - ketchup and mustard squeeze bottles
   - small computer monitor and keyboard
3. **Plaza:**
   - round table with umbrella and two stools
   - string light pole
   - street lamp
   - chalkboard menu stand
   - planter
   - trash bin
   - 3 different stylized trees
4. **Home kitchen:**
   - stack of dirty plates and a clean plate
   - egg carton
   - frying pan with two fried eggs
   - bread loaf
   - toaster with toast popping up
   - sink with tap
5. **Bedroom and living room:**
   - bed with pillows and blanket
   - nightstand with lamp
   - sofa
   - coffee table with plant
   - framed painting
   - rug

## Food truck (modular, because the "Ampliar" upgrade makes it longer)

> Food truck design reference sheet: a red and cream burger food truck, shown from left side, right side (with serving window and canopy open), front and back (with rear door). Built from three clear sections, cab, middle kitchen box and rear section, so the middle can be extended. Plain grey background, no text except a "BURGER TRUCK" sign on the roof. {STYLE}

## Layout images (one per area)

> Top-down floor plan illustration for a video game level: {AREA}. Clear readable layout, labeled zones only with icons, plain background. {STYLE}

- **House:** "bedroom, living room, kitchen-dining at the back, front door to a garden path."
- **Truck interior:** "a long narrow food truck kitchen with fridge at the front, grill counter on the left, service counter and window on the right, rear exit door."
- **Plaza:** "a small plaza with a food truck parking spot, customer queue area at the service window, two umbrella tables, string lights, trees, a street behind the truck for deliveries."

## For Blender

When modeling from these references:

- Build **modular pieces** (counter section, wall panel) and reuse them.
- Vary repeated objects. Chong-U: "stop having repetitive things", so no copy-pasted trees.
- Name objects clearly (`fridge_door`, `grill_top`, `truck_middle`). The game finds and animates parts by name.
- Export each prop as `.glb` (+Y up, apply transforms) into `assets/models/props/`.
