# Stage 2C: Audio with ElevenLabs

**Tool:** ElevenLabs website, in three parts:

- **Sound Effects** for SFX
- **Text to Speech** for voices
- **Music** for the background loops

**Save to:**

- Originals: `source/audio-raw/`
- What the game loads: `assets/audio/sfx/`, `assets/audio/voice/`, `assets/audio/music/`

**Rules:**

- Download the clips and commit the files. **Never put the API key in `index.html`**; the repo is public.
- Trim the silence at the start and end.
- SFX: mono `.mp3`, under 100 KB each. Music: stereo `.mp3`, under 2 MB each.
- File names: lowercase, no spaces, matching the names below.

## Sound effects

| File | Prompt | Length |
|---|---|---|
| `sfx/grill_sizzle_loop` | Beef patty sizzling on a hot flat-top grill, steady loop | 6s |
| `sfx/fridge_open` | Commercial fridge door opening with a soft seal pop | 1s |
| `sfx/fridge_close` | Fridge door closing with a soft thud | 1s |
| `sfx/fridge_hum_loop` | Low refrigerator hum, quiet, seamless loop | 5s |
| `sfx/pickup` | Light cartoon pop, picking up a small food item | 0.3s |
| `sfx/plate_place` | Food item placed softly on a ceramic plate | 0.4s |
| `sfx/register_chaching` | Cash register drawer opening with a bright cha-ching bell | 1s |
| `sfx/coins` | Handful of coins clinking, cheerful | 0.8s |
| `sfx/door_truck` | Metal food truck door swinging open with a short creak | 1s |
| `sfx/door_house` | Wooden front door opening, gentle | 1s |
| `sfx/footsteps_wood` | Footsteps on a wooden floor, sneakers, 4 steps | 2s |
| `sfx/footsteps_metal` | Footsteps on a metal food truck floor, 4 steps | 2s |
| `sfx/ui_click` | Soft UI click | 0.2s |
| `sfx/error_buzz` | Gentle cartoon "wrong" buzz, not harsh | 0.5s |
| `sfx/success_jingle` | Short happy cartoon success jingle | 1.5s |
| `sfx/delivery_truck` | Small delivery van arriving and stopping, with handbrake | 3s |
| `sfx/dishes_clink` | Ceramic dishes clinking together in a sink | 1s |
| `sfx/scrub` | Scrubbing a plate with a sponge and soapy water | 1s |
| `sfx/eggs_frying_loop` | Eggs frying in a pan with butter, gentle sizzle loop | 5s |
| `sfx/toaster_pop` | Toaster popping up toast | 0.8s |
| `sfx/lamp_click` | Bedside lamp switch click | 0.2s |
| `sfx/phone_buzz` | Smartphone vibrating twice on a wooden nightstand | 1.5s |
| `sfx/engine_idle_loop` | Small diesel food truck engine idling, loop | 5s |
| `sfx/engine_rev` | Small truck accelerating from stop | 2s |
| `sfx/horn` | Friendly short truck horn honk, two beeps | 1s |
| `sfx/brake` | Truck braking to a stop on grass and gravel | 1.5s |
| `sfx/ambience_night_loop` | Quiet night ambience, crickets, distant city, loop | 15s |
| `sfx/ambience_plaza_loop` | Evening city plaza ambience, light chatter, distant traffic, loop | 15s |

## Voice lines (Text to Speech, in Spanish)

Use **3–4 different voices**: young, adult, older, and one for the friend. Set them **expressive** and not robotic. Save as `voice/<voice>_<line>.mp3`, for example `voice/a_order_clasica.mp3`.

| Line id | Text |
|---|---|
| `order_clasica` | ¡Hola! Una Clásica, por favor. |
| `order_completa` | Quiero una Completa, ¡con todo! |
| `order_vegetal` | Para mí una Vegetal, gracias. |
| `order_doble` | ¡Una Doble! Tengo mucha hambre. |
| `thanks` | ¡Mmm, qué rica! ¡Gracias! |
| `thanks_fast` | ¡Wow, qué rápido! ¡Toma, una propina! |
| `impatient` | Ehh… ¿falta mucho? |
| `angry` | ¡Uff, me cansé de esperar! ¡Me voy! |
| `wrong` | Mmm… esto no es lo que pedí. |
| `friend_phone` (friend voice) | ¡Hola amigo! Te conseguí un trabajo en un food truck. ¡Empiezas mañana! |
| `delivery_arrive` (driver voice) | ¡Pedido de materiales! Te lo dejo aquí atrás. |

## Music (loops)

| File | Prompt | Length |
|---|---|---|
| `music/night_tutorial_loop` | Calm cozy lo-fi lullaby, soft piano and gentle synth pads, nighttime, relaxing, seamless loop, no vocals | 60s |
| `music/morning_loop` | Bright cheerful acoustic morning tune, ukulele and light percussion, kitchen chores, seamless loop, no vocals | 60s |
| `music/rush_loop` | Upbeat funky cooking-game music, bass, brass stabs, energetic but friendly, seamless loop, no vocals | 60s |
