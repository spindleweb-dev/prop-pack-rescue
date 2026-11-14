"""Procedural, seamless (tileable) "photo-style" textures for Prop-Pack Rescue.

Each material is built the way texture artists do it:
  1. a HEIGHT MAP from layered noise (fBm) and Voronoi "stone cells"
  2. NORMALS from the height map's slopes
  3. LIGHTING: light from the top-left, plus ambient occlusion in the cracks
  4. a COLOUR ramp per material / per level
Everything wraps around at the edges, so the textures tile with no seams.
"""
import numpy as np
from PIL import Image

OUT = './'   # writes the images into the current folder

# ---------------------------------------------------------------- noise helpers
def value_noise(n, cells, rng):
    """Tileable value noise: a random lattice (cells x cells) smoothly interpolated, wrapping."""
    lat = rng.random((cells, cells))
    y, x = np.mgrid[0:n, 0:n] * (cells / n)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    x1 = (x0 + 1) % cells; y1 = (y0 + 1) % cells; x0 %= cells; y0 %= cells
    a = lat[y0, x0] * (1 - fx) + lat[y0, x1] * fx
    b = lat[y1, x0] * (1 - fx) + lat[y1, x1] * fx
    return a * (1 - fy) + b * fy

def fbm(n, rng, base=4, octaves=6, gain=0.5):
    tot = np.zeros((n, n)); amp = 1.0; norm = 0
    for o in range(octaves):
        cells = base * 2 ** o
        if cells > n: break
        tot += amp * value_noise(n, cells, rng); norm += amp; amp *= gain
    return tot / norm

def voronoi(n, count, rng, jitter_aspect=1.0):
    """Tileable Voronoi: returns F1, F2 distances and the id of the nearest cell."""
    pts = rng.random((count, 2))
    y, x = (np.mgrid[0:n, 0:n] + 0.5) / n
    best1 = np.full((n, n), 9.0); best2 = np.full((n, n), 9.0); ids = np.zeros((n, n), int)
    for i, (px, py) in enumerate(pts):
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                d = np.sqrt(((x - (px + ox)) * jitter_aspect) ** 2 + (y - (py + oy)) ** 2)
                closer = d < best1
                best2 = np.where(closer, best1, np.minimum(best2, d))
                ids = np.where(closer, i, ids)
                best1 = np.where(closer, d, best1)
    return best1, best2, ids

def blur(a, r):
    """Cheap tileable box blur (wraps)."""
    out = a.copy()
    for _ in range(2):
        acc = np.zeros_like(out)
        for d in range(-r, r + 1): acc += np.roll(out, d, 0)
        out = acc / (2 * r + 1)
        acc = np.zeros_like(out)
        for d in range(-r, r + 1): acc += np.roll(out, d, 1)
        out = acc / (2 * r + 1)
    return out

def light(h, strength=6.0, ldir=(-0.55, -0.65, 0.52)):
    """Lambert lighting from a height map (wrap-around slopes)."""
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    nz = 1.0 / np.sqrt(dx * dx + dy * dy + 1)
    nx, ny = -dx * nz, -dy * nz
    L = np.array(ldir); L = L / np.linalg.norm(L)
    return np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1), (nx, ny, nz)

def ramp(t, stops):
    """Colour ramp: stops = [(pos, (r,g,b)), ...]"""
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1); k = ((t - p0) / max(p1 - p0, 1e-6))[..., None]
        out[m] = (np.array(c0) * (1 - k) + np.array(c1) * k)[m]
    return out

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def mix(a, b, k): return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))

def save(arr, name, quality=88, alpha=None):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if alpha is not None:
        img = Image.fromarray(np.dstack([arr, np.clip(alpha * 255, 0, 255).astype(np.uint8)]), 'RGBA')
        img.save(OUT + name + '.png', optimize=True)
    else:
        Image.fromarray(arr, 'RGB').save(OUT + name + '.jpg', quality=quality, optimize=True)

# ---------------------------------------------------------------- materials
# Level palettes (dark, mid, light) – match the game's rock colours
LEVELS = [
    dict(name='L1', rock='#b86a2c', wall='#e8c070', bg='#24140a'),
    dict(name='L2', rock='#5f8a2a', wall='#d0d878', bg='#121c0a'),
    dict(name='L3', rock='#2f62a8', wall='#98c0f0', bg='#0a1426'),
    dict(name='L4', rock='#8a3aa8', wall='#e0a8f0', bg='#1a0c24'),
]

def rock_texture(pal, seed, n=256):
    rng = np.random.default_rng(seed)
    f1, f2, ids = voronoi(n, 30, rng, 0.85)             # big stones
    g1, g2, gids = voronoi(n, 90, rng)                  # small pebbles packed in between
    edge = f2 - f1
    stones = np.clip(edge * 9, 0, 1)
    stones = blur(stones, 3)                            # round the stones off (no sharp facets)
    stones = 1 - (1 - stones) ** 2.2                    # dome-shaped profile
    pebbles = blur(np.clip((g2 - g1) * 16, 0, 1), 1) * 0.35
    cellh = rng.random(ids.max() + 1)[ids]
    detail = fbm(n, rng, 8, 6)
    grit = fbm(n, rng, 48, 3)
    h = np.maximum(stones * (0.6 + 0.4 * cellh), pebbles) + detail * 0.28 + grit * 0.07
    lit, _ = light(h, 6.0)
    ao = np.clip(1 - (blur(h, 5) - h) * 3.0, 0.3, 1)
    base = hexrgb(pal['rock'])
    base = mix(base, (128, 118, 108), 0.38)             # real rock is less saturated
    dark, mid, lightc = mix(base, (0, 0, 0), 0.6), base, mix(base, (250, 240, 225), 0.38)
    hue2 = mix(base, (110, 90, 70), 0.5)                # some stones a different mineral
    tone = np.clip(0.3 + cellh * 0.35 + (detail - 0.5) * 0.7, 0, 1)
    col = ramp(tone, [(0, dark), (0.55, mid), (1, lightc)])
    alt = (rng.random(ids.max() + 1)[ids] > 0.78)
    col[alt] = col[alt] * 0.55 + np.array(ramp(tone, [(0, mix(hue2, (0, 0, 0), 0.5)), (1, mix(hue2, (255, 240, 220), 0.3))]))[alt] * 0.45
    strata = (np.sin((np.mgrid[0:n, 0:n][0] / n) * np.pi * 2 * 6 + detail * 6) * 0.5 + 0.5) * 0.12   # faint layering
    shade = (0.25 + 0.95 * lit) * ao * (0.94 + strata)
    out = col * shade[..., None]
    fl = rng.random((n, n)) > 0.997
    out[fl] = np.minimum(out[fl] * 1.5 + 35, 255)
    return out

def backdrop_texture(pal, seed, n=256):
    rng = np.random.default_rng(seed)
    f1, f2, ids = voronoi(n, 14, rng)
    h = np.clip((f2 - f1) * 6, 0, 1) * 0.6 + fbm(n, rng, 4, 6) * 0.7
    lit, _ = light(h, 3.0)
    ao = np.clip(1 - (blur(h, 6) - h) * 2.5, 0.5, 1)
    base = hexrgb(pal['bg']); rockc = hexrgb(pal['rock'])
    c1 = mix(base, (0, 0, 0), 0.4); c2 = mix(base, rockc, 0.28); c3 = mix(base, rockc, 0.5)
    col = ramp(fbm(n, rng, 4, 4), [(0, c1), (0.5, c2), (1, c3)])
    return col * ((0.45 + 0.7 * lit) * ao)[..., None]

def brick_texture(pal, seed, w=64, hgt=128):
    """Breakable wall: 16px brick courses (4 per game tile at 4x), offset every other course."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:hgt, 0:w]
    course = y // 16
    xs = (x + (course % 2) * 16) % w
    bx = xs // 32
    brick_id = course * 4 + bx
    lx = xs % 32; ly = y % 16
    d_edge = np.minimum(np.minimum(lx, 31 - lx), np.minimum(ly, 15 - ly)).astype(float)
    hmap = np.clip(d_edge / 3.0, 0, 1) ** 0.7          # bevelled bricks, sunken mortar
    nb = fbm(max(w, hgt), rng, 8, 5)[:hgt, :w]
    chips = (fbm(max(w, hgt), rng, 16, 3)[:hgt, :w] > 0.68) & (d_edge < 5)
    hmap = hmap * 0.8 + nb * 0.25 - chips * 0.35
    lit, _ = light(hmap, 5.0)
    base = hexrgb(pal['wall'])
    var = rng.random(brick_id.max() + 1)[brick_id]
    col = ramp(np.clip(var * 0.6 + nb * 0.5, 0, 1),
               [(0, mix(base, (60, 30, 10), 0.45)), (0.5, base), (1, mix(base, (255, 250, 235), 0.3))])
    mortar = d_edge < 1.2
    col[mortar] = np.array(mix(base, (40, 30, 25), 0.75))
    shade = 0.35 + 0.85 * lit
    return col * shade[..., None]

def ore_texture(kind, seed, n=64):
    """A cluster of metallic nuggets with transparent background."""
    rng = np.random.default_rng(seed)
    y, x = (np.mgrid[0:n, 0:n] + 0.5)
    field = np.zeros((n, n))
    for _ in range(14):
        cx, cy = rng.uniform(10, n - 10, 2); r = rng.uniform(6, 11)
        sq = rng.uniform(0.7, 1.3)
        field += np.exp(-(((x - cx) / (r * sq)) ** 2 + ((y - cy) / (r / sq)) ** 2) * 1.6)
    rough = fbm(n, rng, 8, 4)
    h = field + rough * 0.25
    alpha = np.clip((field - 0.4) * 5, 0, 1)
    _, (nx, ny, nz) = light(h, 9.0)
    L = np.array([-0.5, -0.7, 0.55]); L = L / np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # specular (Blinn) – metals are shiny
    H = L + np.array([0, 0, 1]); H = H / np.linalg.norm(H)
    spec = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** 28
    if kind == 'gold':
        col = ramp(diff, [(0, (90, 55, 5)), (0.45, (205, 150, 30)), (0.8, (255, 215, 80)), (1, (255, 245, 190))])
    else:
        col = ramp(diff, [(0, (90, 35, 12)), (0.45, (205, 105, 50)), (0.8, (250, 160, 100)), (1, (255, 220, 190))])
        verd = (fbm(n, rng, 16, 3) > 0.7) & (alpha > 0.5)
        col[verd] = col[verd] * 0.4 + np.array((70, 170, 140)) * 0.6   # green patina
    out = col + spec[..., None] * 255
    return out, alpha

def lava_texture(seed, n=128):
    rng = np.random.default_rng(seed)
    f1, f2, ids = voronoi(n, 16, rng)
    crack = np.clip(1 - (f2 - f1) * 10, 0, 1) ** 2      # bright between crust plates
    warm = fbm(n, rng, 4, 5)
    heat = np.clip(crack * 0.9 + warm * 0.45 - 0.1, 0, 1)
    col = ramp(heat, [(0, (40, 8, 2)), (0.25, (120, 20, 0)), (0.5, (230, 70, 5)), (0.75, (255, 160, 20)), (1, (255, 245, 170))])
    crust = (1 - crack) * (fbm(n, rng, 16, 3) * 0.4)
    lit, _ = light(crust, 4.0)
    return col * (0.75 + 0.35 * lit)[..., None]

if __name__ == '__main__':
    for i, pal in enumerate(LEVELS):
        save(rock_texture(pal, 100 + i), f"rock_{pal['name']}", 86)
        save(backdrop_texture(pal, 200 + i), f"bg_{pal['name']}", 82)
        save(brick_texture(pal, 300 + i), f"brick_{pal['name']}", 88)
    for k, kind in enumerate(['gold', 'copper']):
        rgb, a = ore_texture(kind, 400 + k)
        save(rgb, f'ore_{kind}', alpha=a)
    save(lava_texture(500), 'lava', 88)
    print('done')
