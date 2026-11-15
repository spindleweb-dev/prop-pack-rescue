# Prop-Pack Rescue

A from-scratch remake of the gameplay of Activision's **H.E.R.O.** (1984), written in plain
JavaScript + HTML Canvas as a learning project. All code and graphics are original.

**Play it:** open `index.html` in any modern browser – no install or build step needed.

## Controls

| Key | Action |
|---|---|
| ← → | Move |
| ↑ (hold) | Prop-pack (fly) |
| Space | Laser |
| ↓ | Drop dynamite |
| P | Pause |
| M | Mute |
| G | Switch Classic (chunky 320×200) / Enhanced (4× HD) graphics |
| T | Realistic textures and natural details (moss, grass, puddles) on/off |
| 1–9, 0 | Testing: jump straight to level 1–10 (also buttons in the tuning panel) |

## Features

- 10 levels of mine shafts with flip-screen rooms, like the Atari 2600 original – each with its own
  name, rock colour and power supply
- Acceleration-based physics with a live tuning panel (top-right of the page)
- Segmented laser, dynamite with realistic explosions, breakable walls
- Gold & copper ore veins – mine them for money ($)
- Old West gold run: nuggets go into a satchel (max 12) that makes you heavier and drains power
  faster. Bank them at an ore cart in a back gallery (it rolls off into the tunnel with your gold and
  an empty one comes back), a rope-and-pulley bucket hoist, or a timber ore chute.
  Banking 8+ nuggets at once earns a 25% big-haul bonus. Die and the satchel spills; rescuing the
  miner banks whatever you're carrying. Timber mine supports shore up the shafts.
- Creatures: bats, spiders, moths, wall snakes (lunge out of holes; only hittable when out) and
  armoured scorpions (need a sustained laser burst or dynamite)
- Recorded sound effects with a compressor/limiter mix bus

## How the code is organised

Everything lives in `index.html`. The script is split into numbered sections:

1. **Constants** – every tunable number in one place
2. **Level data** – maps drawn as text, one character per tile
3. **Input & audio** – keyboard, Web Audio synth, embedded samples, mixer
4. **World helpers** – tile lookups and collision
5. **Game logic** – player, laser, dynamite, mining, enemies, game states
6. **Drawing** – Classic (rectangles) and Enhanced (gradients, lighting, particles) renderers
7. **Main loop** – fixed 60 Hz update + render

The sound recordings and textures are embedded as base64 in a second `<script>` block at the end of the file.

The textures are generated, not downloaded: `tools/make_textures.py` builds seamless rock, brick, backdrop,
ore and lava textures from lit height maps (layered noise + Voronoi stone cells). Run it with Python 3,
NumPy and Pillow to regenerate or tweak them. `tools/make_decorations.py` makes the moss, hanging moss,
grass and mud-puddle sprites; each level's `deco` setting controls how much of each appears.
`tools/check_levels.py` holds the maps for levels 5–10 and checks every miner is reachable,
every creature has room to move, and places the ore veins.

## Credits

Sound effects (embedded, trimmed and re-encoded):
- Explosion – "dragon-studio" (explosion sound effect 425455)
- Laser – "soundreality" (attack laser 128280)
- Helicopter – "flutie8211" (helicopter hovering 598081)

Check each sound's original licence page before publishing and add links here.

H.E.R.O. is a trademark of Activision. This is an unofficial fan remake for education;
it contains no original Activision code or assets.
