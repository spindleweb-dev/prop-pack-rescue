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

## Features

- Chapter 1: 4 levels of mine shafts with large 32×18-tile flip-screen rooms
- Acceleration-based physics with a live tuning panel (top-right of the page)
- Segmented laser, dynamite with realistic explosions, breakable walls
- Gold & copper ore veins – mine them for money ($)
- Recorded sound effects with a compressor/limiter mix bus

## How the code is organised

Everything lives in `index.html`. The script is split into numbered sections:

1. **Constants** – every tunable number in one place
2. **Level data** – maps drawn as text, one character per tile (each room is 32×18)
3. **Input & audio** – keyboard, Web Audio synth, embedded samples, mixer
4. **World helpers** – tile lookups and collision
5. **Game logic** – player, laser, dynamite, mining, enemies, game states
6. **Drawing** – Classic (rectangles) and Enhanced (gradients, lighting, particles) renderers
7. **Main loop** – fixed 60 Hz update + render

The sound recordings are embedded as base64 in a second `<script>` block at the end of the file.

## Credits

Sound effects (embedded, trimmed and re-encoded):
- Explosion – "dragon-studio" (explosion sound effect 425455)
- Laser – "soundreality" (attack laser 128280)
- Helicopter – "flutie8211" (helicopter hovering 598081)

Check each sound's original licence page before publishing and add links here.

H.E.R.O. is a trademark of Activision. This is an unofficial fan remake for education;
it contains no original Activision code or assets.
