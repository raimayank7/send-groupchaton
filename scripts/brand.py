"""Send brand pictures, made once from the Help ones (same GroupChatOn bubble, orange + white paper plane instead of teal + ?).
   python -X utf8 scripts/brand.py      (needs Pillow; reads ../groupchaton-tools/assets/brand from C:\\ClaudeAi or next to this
   project, writes static/brand/*)"""
import os, re
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = next(p for p in (os.path.join(HERE, '..', 'groupchaton-tools', 'assets', 'brand'),
                       r'C:\ClaudeAi\GroupChatOn\groupchaton-tools\assets\brand') if os.path.isdir(p))
OUT = os.path.join(HERE, 'static', 'brand')
TEAL, ORANGE = (13, 148, 136), (234, 88, 12)

def near(c, ref, d=70): return sum((a - b) ** 2 for a, b in zip(c, ref)) < d * d

def plane(draw, cx, cy, s):
    """A paper plane in 100-unit space centred on (50, 50), scaled by s (pixels per unit)."""
    P = lambda x, y: (cx + (x - 50) * s, cy + (y - 50) * s)
    draw.polygon([P(12, 46), P(88, 14), P(70, 86), P(48, 64)], fill='white')          # the wing
    draw.polygon([P(48, 64), P(88, 14), P(40, 88)], fill=(255, 255, 255, 170))         # the fold, a little see-through
    draw.line([P(48, 64), P(88, 14)], fill=ORANGE + (255,), width=max(1, round(3 * s)))  # the crease

def convert(name, out):
    im = Image.open(os.path.join(SRC, name)).convert('RGBA')
    W, H = im.size
    px = im.load()
    teal = [(x, y) for y in range(H) for x in range(W) if px[x, y][3] > 200 and near(px[x, y][:3], TEAL, 40)]
    x0, x1 = min(p[0] for p in teal), max(p[0] for p in teal)
    y0, y1 = min(p[1] for p in teal), max(p[1] for p in teal)
    is_teal = lambda c: c[3] > 40 and near(c[:3], TEAL, 90)
    # holes inside the bubble = non-teal pixels the bubble's edge can't reach (the ? and its dot)
    seen = set()
    stack = [(x, y) for x in range(x0, x1 + 1) for y in (y0, y1)] + [(x, y) for y in range(y0, y1 + 1) for x in (x0, x1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (x0 <= x <= x1 and y0 <= y <= y1) or is_teal(px[x, y]): continue
        seen.add((x, y)); stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    holes = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if (x, y) not in seen and not is_teal(px[x, y])]
    for x, y in holes: px[x, y] = ORANGE + (255,)
    for y in range(y0 - 2, min(H, y1 + 3)):
        for x in range(max(0, x0 - 2), min(W, x1 + 3)):
            r, g, b, a = px[x, y]
            if a == 0: continue
            if near((r, g, b), TEAL, 90):
                px[x, y] = ORANGE + (a,)
            elif g > r + 25 and b > r + 15 and abs(g - b) < 40:   # teal mixed with black/white at an edge
                k = (g + b) / (TEAL[1] + TEAL[2])
                px[x, y] = tuple(min(255, round(c * k)) for c in ORANGE) + (a,)
    hx0, hx1 = min(p[0] for p in holes), max(p[0] for p in holes)
    hy0, hy1 = min(p[1] for p in holes), max(p[1] for p in holes)
    s = (hy1 - hy0 + 1) / 64          # the ? is about 64 units tall
    big = Image.new('RGBA', (W * 4, H * 4), (0, 0, 0, 0))   # draw 4x larger, then shrink, for smooth edges
    plane(ImageDraw.Draw(big), (hx0 + hx1) / 2 * 4, (hy0 + hy1) / 2 * 4 + 2 * s * 4, s * 4 * 0.95)
    im = Image.alpha_composite(im, big.resize((W, H), Image.LANCZOS))
    im.save(os.path.join(OUT, out))
    return im

os.makedirs(OUT, exist_ok=True)
convert('help-logo-light.png', 'logo-light.png')
convert('help-logo-dark.png', 'logo-dark.png')
ic = convert('help-favicon-512.png', 'favicon-512.png')
for n in (192, 48, 32): ic.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, 'favicon-%d.png' % n))
ic.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, 'apple-touch-icon.png'))
ic.save(os.path.join(OUT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
m = Image.new('RGBA', (512, 512), (255, 255, 255, 255))   # maskable app icon: the mark on a white tile with a safe margin
m.alpha_composite(ic.resize((360, 360), Image.LANCZOS), (76, 76))
m.save(os.path.join(OUT, 'maskable-512.png'))
svg = open(os.path.join(SRC, 'help-mark.svg'), encoding='utf-8').read().replace('#0D9488', '#EA580C').replace('GroupChatOn Help', 'Send by GroupChatOn')
svg = re.sub(r'<g transform="translate\(390 270\) scale\(5.0\)">.*</g></svg>',
    '<g transform="translate(390 270) scale(5.0)"><path d="M12 46 88 14 70 86 48 64Z" fill="#fff"/>'
    '<path d="M48 64 88 14 40 88Z" fill="#fff" fill-opacity=".67"/><path d="M48 64 88 14" stroke="#EA580C" stroke-width="3"/></g></svg>',
    svg, flags=re.S)
open(os.path.join(OUT, 'mark.svg'), 'w', encoding='utf-8').write(svg)
print('brand pictures written to', OUT)
