"""Realistic decoration sprites for Prop-Pack Rescue: moss, hanging moss, grass tufts, mud puddles.
All drawn at 4 pixels per game pixel (to match Enhanced mode) with soft, anti-aliased edges."""
import numpy as np
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, '.')
from make_textures import fbm, light, ramp, blur   # shared noise/lighting helpers

OUT = './'   # writes the images into the current folder

def save_rgba(rgb, a, name):
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), 'RGBA')
    img.save(OUT + name + '.png', optimize=True)

MOSS = [(0, (16, 24, 8)), (0.35, (40, 58, 20)), (0.7, (82, 100, 40)), (1, (150, 158, 80))]   # olive, natural

def moss_carpet(seed, w=96, h=36):
    """Moss growing along the top of a floor, lumpy on top and draping over the front edge."""
    rng = np.random.default_rng(seed)
    n = max(w, h) * 2
    big = fbm(n, rng, 4, 6)[:h, :w]; fine = fbm(n, rng, 32, 3)[:h, :w]
    y, x = np.mgrid[0:h, 0:w]
    edge = 10 + (fbm(n, rng, 10, 4)[0, :w] - 0.5) * 18              # lumpy, irregular top outline
    drape = 20 + (fbm(n, rng, 8, 4)[1, :w]) * 14                     # how far it hangs down the edge
    ends = np.clip(np.minimum(x, w - 1 - x) / 14, 0, 1)            # feathered ends so neighbours blend
    top = edge[None, :] + (1 - ends) * 10
    bottom = drape[None, :] * (0.4 + 0.6 * ends)
    a = np.clip((y - top) / 3, 0, 1) * np.clip((bottom + 6 - y) / 4, 0, 1)
    a *= np.clip(big * 2.2, 0, 1) ** 0.3 * np.clip((fine - 0.12) * 5, 0, 1)
    a = (blur(a, 1) * 0.6 + a * 0.4) * ends ** 0.7
    hmap = big * 0.7 + fine * 0.6
    lit, _ = light(hmap, 8)
    col = ramp(np.clip(lit * 0.8 + fine * 0.4, 0, 1), MOSS)
    specks = (rng.random((h, w)) > 0.99) & (a > 0.5)
    col[specks] = (170, 175, 100)
    col *= (0.7 + 0.3 * np.clip((y - top) / 10, 0, 1))[..., None] ** -0.2   # tips catch more light
    return col, np.clip(a, 0, 1)

def moss_patch(seed, w=28, h=56):
    """A patch of moss on a vertical wall face."""
    rng = np.random.default_rng(seed)
    n = 64
    f = fbm(n, rng, 4, 5)[:h, :w]; fine = fbm(n, rng, 24, 3)[:h, :w]
    y, x = np.mgrid[0:h, 0:w]
    blob = 1 - np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    a = np.clip((blob + (f - 0.5) * 0.9) * 3, 0, 1) * np.clip((fine - 0.2) * 4, 0, 1)
    a = blur(a, 1) * 0.6 + a * 0.4
    lit, _ = light(f * 0.7 + fine * 0.5, 8)
    col = ramp(np.clip(lit * 0.8 + fine * 0.35, 0, 1), MOSS)
    return col, a

def moss_hanging(seed, w=64, h=56):
    """Strands of moss hanging from a ceiling."""
    rng = np.random.default_rng(seed)
    img = Image.new('RGBA', (w * 4, h * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # a mat along the top
    for i in range(70):
        cx = rng.uniform(0, w * 4); cy = rng.uniform(0, 22); r = rng.uniform(6, 16)
        g = int(rng.uniform(40, 110))
        d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=(int(g * 0.55), int(g * 0.75), int(g * 0.3), 255))
    # strands
    for i in range(26):
        x0 = rng.uniform(8, w * 4 - 8); length = rng.uniform(40, h * 4 - 10); sway = rng.uniform(-14, 14)
        pts = []
        for k in range(12):
            t = k / 11; pts.append((x0 + sway * t * t + np.sin(t * 6 + i) * 3, 10 + length * t))
        for k in range(11):
            t = k / 11; g = int(55 + 95 * (1 - t) * rng.uniform(0.7, 1))
            wdt = max(1, int(5 * (1 - t)) + 1)
            d.line([pts[k], pts[k + 1]], fill=(int(g * 0.65), int(g * 0.8), int(g * 0.35), int(255 * (1 - t * 0.6))), width=wdt)
    img = img.resize((w, h), Image.LANCZOS)
    return img

def grass_tuft(seed, w=48, h=44):
    """A tuft of thin grass blades, anti-aliased by drawing large and shrinking."""
    rng = np.random.default_rng(seed)
    S = 4; img = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    base_x = w * S / 2; base_y = h * S - 2
    blades = int(rng.uniform(14, 22))
    order = sorted(range(blades), key=lambda i: rng.random())
    for i in order:
        bx = base_x + rng.normal(0, w * S * 0.12)
        ln = rng.uniform(0.45, 0.98) * h * S
        lean = rng.normal(0, 0.45)
        curve = lean * rng.uniform(0.5, 1.5)
        wid = rng.uniform(3.5, 7.5)
        segs = 10
        for k in range(segs):
            t0, t1 = k / segs, (k + 1) / segs
            def pt(t, side):
                xx = bx + np.sin(lean) * ln * t + curve * ln * t * t * 0.4
                yy = base_y - np.cos(lean) * ln * t
                ww = wid * (1 - t) ** 0.8
                return (xx + side * ww / 2, yy)
            poly = [pt(t0, -1), pt(t1, -1), pt(t1, 1), pt(t0, 1)]
            dark = rng.uniform(0.75, 1.0)
            g = 60 + 130 * t0
            col = (int((25 + 90 * t0 * t0) * dark), int(g * dark), int((15 + 30 * t0) * dark), 255)
            d.polygon(poly, fill=col)
        # light catching one side of the blade
        hx = bx + np.sin(lean) * ln * 0.6 + curve * ln * 0.36 * 0.4
        d.line([(bx, base_y), (hx, base_y - np.cos(lean) * ln * 0.6)], fill=(190, 220, 120, 70), width=1)
    return img.resize((w, h), Image.LANCZOS)

def puddle(seed, w=104, h=30):
    """A shallow mud puddle seen from the side: water sits in a dip in the floor.
    Top: a bright reflective surface line. Below: murky water getting darker with depth.
    Around it: a darker ring of wet mud."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(float)
    cx = w / 2; surf = 6.0; halfw = w / 2 - 8
    across = np.clip(1 - ((x - cx) / halfw) ** 2, 0, 1)
    wob = (fbm(128, rng, 6, 3)[:h, :w] - 0.5) * 3
    depth = 3 + 13 * across ** 0.7 + wob                 # deepest in the middle
    inside = (y >= surf) & (y <= surf + depth) & (across > 0.02)
    rgb = np.zeros((h, w, 3)); a = np.zeros((h, w))
    # damp mud rim around the dip
    rim = (y >= surf - 1) & (y <= surf + depth + 4) & (np.abs(x - cx) <= halfw + 6)
    rgb[rim] = (38, 26, 16); a[rim] = 0.55
    # the water: reflection at the top fading to murky brown
    t = np.clip((y - surf) / np.maximum(depth, 1), 0, 1)
    wc = ramp(t, [(0, (150, 150, 140)), (0.18, (92, 84, 70)), (0.55, (58, 44, 30)), (1, (34, 24, 15))])
    rgb[inside] = wc[inside]; a[inside] = 0.95
    # bright surface line, fading toward the ends
    line = (y >= surf - 0.5) & (y < surf + 1.5) & (across > 0.02)
    rgb[line] = (225, 225, 215); a[line] = 0.6 + 0.4 * across[line]
    # soft reflection band just under the surface
    band = inside & (y >= surf + 2) & (y < surf + 4)
    rgb[band] = rgb[band] * 0.6 + np.array((140, 140, 130)) * 0.4 * (0.5 + 0.5 * np.sin(x[band] * 0.12 + seed))[..., None]
    a = blur(a, 1) * 0.5 + a * 0.5
    return rgb, np.clip(a, 0, 1)

if __name__ == '__main__':
    for i in range(3):
        rgb, a = moss_carpet(600 + i); save_rgba(rgb, a, f'moss_top{i}')
        grass_tuft(700 + i).save(OUT + f'grass{i}.png', optimize=True)
    for i in range(2):
        rgb, a = moss_patch(650 + i); save_rgba(rgb, a, f'moss_side{i}')
        moss_hanging(680 + i).save(OUT + f'moss_hang{i}.png', optimize=True)
        rgb, a = puddle(800 + i); save_rgba(rgb, a, f'puddle{i}')
    print('done')
