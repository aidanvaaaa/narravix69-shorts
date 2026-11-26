"""Hand-drawn style art: painted backgrounds, blocky characters with faces, bubbles."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config

BW, BH = 1280, 2272          # background canvas (bigger than the 1080x1920 frame for camera moves)
GROUND = int(BH * 0.70)      # ground line on the background canvas
OUT = (0, 0, 0)
_fonts = {}


def font(size):
    if size not in _fonts:
        try:
            _fonts[size] = ImageFont.truetype(config.FONT, size)
        except OSError:
            _fonts[size] = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    return _fonts[size]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


# ----------------------------------------------------------------- backgrounds
def _gradient(img, top, bottom, y0=0, y1=None):
    y1 = y1 or img.height
    arr = np.array(img)
    t = np.linspace(0, 1, y1 - y0)[:, None]
    for i in range(3):
        arr[y0:y1, :, i] = (top[i] + (bottom[i] - top[i]) * t)
    return Image.fromarray(arr)


def _ob(d, box, fill, w=6, kind="rect", r=18):
    """Outlined shape, cartoon style."""
    if kind == "ellipse":
        d.ellipse(box, fill=fill, outline=OUT, width=w)
    elif kind == "round":
        d.rounded_rectangle(box, r, fill=fill, outline=OUT, width=w)
    else:
        d.rectangle(box, fill=fill, outline=OUT, width=w)


def _poly(d, pts, fill, w=6):
    d.polygon(pts, fill=fill, outline=OUT)
    d.line(pts + [pts[0]], fill=OUT, width=w, joint="curve")


def _cloud(d, x, y, s, col=(255, 255, 255)):
    blobs = [(-1.0, 0.1, 0.8), (-0.3, -0.35, 1.0), (0.5, -0.1, 0.85), (1.1, 0.15, 0.65), (0.1, 0.25, 0.9)]
    for bx, by, r in blobs:  # outline pass
        rr = r * s + 5
        d.ellipse((x + bx * s - rr, y + by * s - rr, x + bx * s + rr, y + by * s + rr), fill=OUT)
    for bx, by, r in blobs:
        rr = r * s
        d.ellipse((x + bx * s - rr, y + by * s - rr, x + bx * s + rr, y + by * s + rr), fill=col)


def _hills(d, base, amp, col, rnd, freq=2.0, y=None):
    y = y if y is not None else GROUND
    ph = rnd.random() * 6
    pts = [(0, BH)]
    for x in range(0, BW + 40, 40):
        pts.append((x, y - amp * (0.5 + 0.5 * math.sin(x / BW * math.pi * freq + ph)) - base))
    pts.append((BW, BH))
    _poly(d, pts, col, 5)


def _tree(d, x, y, s, leaf=(70, 170, 70), trunk=(120, 80, 45)):
    _ob(d, (x - 0.12 * s, y - 0.5 * s, x + 0.12 * s, y), trunk, 5)
    _ob(d, (x - 0.45 * s, y - 1.25 * s, x + 0.45 * s, y - 0.45 * s), leaf, 6, "round", int(0.12 * s))
    d.rectangle((x - 0.3 * s, y - 1.12 * s, x - 0.1 * s, y - 1.0 * s), fill=shade(leaf, 1.25))


def _pine(d, x, y, s, col=(40, 120, 80), snow=False):
    _ob(d, (x - 0.08 * s, y - 0.3 * s, x + 0.08 * s, y), (110, 70, 40), 4)
    for i in range(3):
        top = y - 0.3 * s - i * 0.35 * s
        _poly(d, [(x - (0.5 - i * 0.12) * s, top), (x + (0.5 - i * 0.12) * s, top), (x, top - 0.55 * s)], col, 5)
        if snow:
            d.polygon([(x - 0.12 * s, top - 0.38 * s), (x + 0.12 * s, top - 0.38 * s), (x, top - 0.55 * s)], fill=(250, 250, 255))


def _building(d, x, w, h, col, win=(255, 236, 140), lit=0.8, rnd=None, ground=None):
    g = ground or GROUND
    _ob(d, (x, g - h, x + w, g), col, 6)
    rnd = rnd or random
    for yy in range(int(g - h + 30), int(g - 40), 70):
        for xx in range(int(x + 22), int(x + w - 40), 60):
            c = win if rnd.random() < lit else shade(col, 0.7)
            d.rectangle((xx, yy, xx + 30, yy + 40), fill=c, outline=shade(col, 0.5), width=3)


def _ground(d, col, top=None, stripes=None):
    top = top or GROUND
    d.rectangle((0, top, BW, BH), fill=col)
    d.line((0, top, BW, top), fill=OUT, width=6)
    if stripes:
        for i in range(12):
            y = top + 30 + i * 60
            d.line((0, y, BW, y), fill=stripes, width=3)


def _sun(d, x, y, r, col=(255, 220, 90)):
    d.ellipse((x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5), fill=lerp(col, (255, 255, 255), 0.6))
    _ob(d, (x - r, y - r, x + r, y + r), col, 6, "ellipse")


def paint_background(kind, seed=0):
    rnd = random.Random(seed)
    img = Image.new("RGB", (BW, BH))
    sky = {
        "space": ((10, 6, 30), (60, 20, 90)), "night_city": ((20, 16, 60), (90, 50, 120)),
        "lava": ((60, 10, 10), (230, 90, 30)), "desert": ((255, 170, 90), (255, 225, 160)),
        "pyramids": ((250, 160, 80), (255, 225, 160)), "snow": ((170, 200, 235), (235, 245, 255)),
        "battlefield": ((120, 110, 110), (210, 170, 140)), "forest": ((120, 200, 220), (200, 240, 210)),
        "factory": ((150, 150, 160), (210, 200, 190)),
    }.get(kind, ((80, 160, 245), (190, 230, 255)))
    img = _gradient(img, *sky)
    d = ImageDraw.Draw(img)

    if kind not in ("space", "night_city", "classroom", "house", "factory", "lava"):
        _sun(d, rnd.randint(200, BW - 200), rnd.randint(250, 500), 90)
    if kind in ("space", "night_city"):
        for _ in range(260):
            x, y, r = rnd.randint(0, BW), rnd.randint(0, int(BH * 0.65)), rnd.choice([1, 2, 2, 3])
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 230))
        _ob(d, (BW - 380, 260, BW - 180, 460), (245, 240, 200), 6, "ellipse")

    if kind == "space":
        _ob(d, (120, 900, 520, 1300), (90, 150, 255), 7, "ellipse")
        d.ellipse((220, 980, 380, 1100), fill=(90, 200, 110))
        d.arc((40, 1040, 600, 1160), 160, 380, fill=(240, 200, 120), width=14)
        _ob(d, (-200, GROUND, BW + 200, BH + 900), (150, 140, 170), 7, "ellipse")
        for _ in range(9):
            x, y, r = rnd.randint(0, BW), rnd.randint(GROUND + 80, BH - 100), rnd.randint(30, 80)
            d.ellipse((x - r, y - r * 0.5, x + r, y + r * 0.5), fill=(120, 110, 140), outline=OUT, width=4)
    elif kind in ("night_city", "blocky_city"):
        night = kind == "night_city"
        x = -40
        while x < BW:
            w, h = rnd.randint(170, 280), rnd.randint(500, 1100)
            col = rnd.choice([(70, 70, 120), (90, 60, 110), (50, 80, 120)]) if night else \
                rnd.choice([(230, 120, 110), (120, 170, 230), (250, 200, 110), (150, 210, 150), (210, 160, 230)])
            _building(d, x, w, h, col, lit=0.55 if night else 0.9, rnd=rnd)
            x += w + rnd.randint(-10, 20)
        _ground(d, (70, 70, 80))
        for i in range(0, BW, 160):
            d.rectangle((i, GROUND + 200, i + 90, GROUND + 220), fill=(250, 230, 120))
    elif kind in ("grass_plains", "castle", "village", "sky", "forest"):
        _hills(d, 120, 220, (120, 200, 110), rnd, 1.5)
        _hills(d, 30, 150, (90, 185, 85), rnd, 2.5)
        if kind == "castle":
            cx = BW // 2
            _ob(d, (cx - 420, GROUND - 620, cx + 420, GROUND - 40), (175, 175, 190), 7)
            for tx in (cx - 470, cx + 330):
                _ob(d, (tx, GROUND - 860, tx + 140, GROUND - 40), (160, 160, 178), 7)
                _poly(d, [(tx - 20, GROUND - 860), (tx + 160, GROUND - 860), (tx + 70, GROUND - 1030)], (200, 70, 70))
            for bx in range(cx - 420, cx + 420, 70):
                d.rectangle((bx, GROUND - 680, bx + 40, GROUND - 620), fill=(175, 175, 190), outline=OUT, width=5)
            _ob(d, (cx - 110, GROUND - 300, cx + 110, GROUND - 40), (90, 60, 40), 7, "round", 80)
            d.line((cx + 400, GROUND - 1030, cx + 400, GROUND - 1180), fill=OUT, width=6)
            _poly(d, [(cx + 400, GROUND - 1180), (cx + 520, GROUND - 1140), (cx + 400, GROUND - 1100)], (60, 120, 230))
        if kind == "village":
            for i, hx in enumerate(range(40, BW, 330)):
                col = [(240, 220, 180), (230, 200, 160), (250, 235, 200)][i % 3]
                _ob(d, (hx, GROUND - 330, hx + 260, GROUND - 40), col, 6)
                _poly(d, [(hx - 30, GROUND - 330), (hx + 290, GROUND - 330), (hx + 130, GROUND - 520)], (170, 90, 60))
                _ob(d, (hx + 100, GROUND - 170, hx + 160, GROUND - 40), (110, 70, 40), 5)
        if kind in ("grass_plains", "forest", "village", "castle"):
            n = 9 if kind == "forest" else 4
            for _ in range(n):
                _tree(d, rnd.randint(0, BW), GROUND - rnd.randint(30, 140), rnd.randint(200, 330))
        _ground(d, (110, 190, 90) if kind != "village" else (190, 160, 110))
        for _ in range(60):
            x, y = rnd.randint(0, BW), rnd.randint(GROUND + 20, BH)
            d.line((x, y, x + 6, y - 18), fill=(70, 150, 60), width=4)
        if kind == "sky":
            d.rectangle((0, GROUND, BW, BH), fill=(150, 210, 255))
            for _ in range(5):
                _cloud(d, rnd.randint(0, BW), rnd.randint(GROUND + 100, BH - 200), rnd.randint(90, 150))
    elif kind in ("ocean", "beach", "ship_deck"):
        sea_top = GROUND - 380
        d.rectangle((0, sea_top, BW, BH), fill=(40, 130, 210))
        for i in range(14):
            y = sea_top + 30 + i * 70
            for x in range(-40, BW, 140):
                d.arc((x + (i % 2) * 70, y, x + 120 + (i % 2) * 70, y + 40), 200, 340, fill=(200, 235, 255), width=5)
        if kind == "beach":
            _poly(d, [(0, GROUND), (BW, GROUND - 60), (BW, BH), (0, BH)], (245, 215, 150))
            px = 200
            d.line((px, GROUND - 20, px + 60, GROUND - 600), fill=(130, 90, 50), width=34)
            for a in range(0, 360, 60):
                ex, ey = px + 60 + 230 * math.cos(math.radians(a)), GROUND - 600 + 120 * math.sin(math.radians(a)) + 60
                d.line((px + 60, GROUND - 600, ex, ey), fill=(60, 160, 70), width=40)
        if kind == "ship_deck":
            _ground(d, (160, 110, 70), stripes=(120, 80, 50))
            for x in range(0, BW, 120):
                d.rectangle((x, GROUND - 160, x + 26, GROUND), fill=(140, 95, 60), outline=OUT, width=4)
            d.rectangle((0, GROUND - 180, BW, GROUND - 150), fill=(140, 95, 60), outline=OUT, width=5)
            d.line((BW - 260, GROUND - 160, BW - 260, 120), fill=(110, 75, 45), width=40)
            _poly(d, [(BW - 240, 200), (BW - 40, 360), (BW - 240, 700)], (245, 240, 225))
    elif kind in ("desert", "pyramids", "arena"):
        if kind == "pyramids":
            for px, s in ((300, 700), (850, 900), (1150, 500)):
                _poly(d, [(px - s * 0.6, GROUND), (px + s * 0.6, GROUND), (px, GROUND - s * 0.75)], (225, 180, 100))
                for k in range(1, 8):
                    yy = GROUND - s * 0.75 * k / 8
                    half = s * 0.6 * (1 - k / 8)
                    d.line((px - half, yy, px + half, yy), fill=(190, 150, 80), width=3)
        if kind == "arena":
            d.rectangle((0, GROUND - 900, BW, GROUND), fill=(205, 170, 120))
            for row in range(3):
                y = GROUND - 900 + row * 280
                for x in range(-20, BW, 160):
                    d.rounded_rectangle((x + 20, y + 40, x + 130, y + 260), 55, fill=(120, 80, 50), outline=OUT, width=5)
                d.line((0, y, BW, y), fill=OUT, width=5)
            for _ in range(140):
                x, y = rnd.randint(0, BW), rnd.randint(GROUND - 900, GROUND - 640)
                d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=rnd.choice([(240, 200, 150), (200, 150, 110), (250, 230, 90)]))
        _hills(d, -20, 90, (240, 200, 120), rnd, 3, GROUND + 20) if kind != "arena" else None
        _ground(d, (235, 195, 120) if kind != "arena" else (225, 190, 130))
        if kind == "desert":
            for cx in (250, 1000):
                _ob(d, (cx - 35, GROUND - 330, cx + 35, GROUND + 10), (80, 170, 80), 6, "round", 30)
                _ob(d, (cx - 120, GROUND - 230, cx - 60, GROUND - 120), (80, 170, 80), 5, "round", 25)
    elif kind == "snow":
        _hills(d, 120, 240, (235, 242, 255), rnd, 1.5)
        for _ in range(6):
            _pine(d, rnd.randint(0, BW), GROUND - rnd.randint(40, 160), rnd.randint(260, 380), snow=True)
        _ground(d, (245, 248, 255))
    elif kind == "lava":
        _poly(d, [(150, GROUND - 100), (BW // 2 - 120, GROUND - 1000), (BW // 2 + 120, GROUND - 1000), (BW - 150, GROUND - 100)], (80, 50, 50))
        d.polygon([(BW // 2 - 120, GROUND - 1000), (BW // 2 + 120, GROUND - 1000), (BW // 2 + 60, GROUND - 800), (BW // 2 - 80, GROUND - 760)], fill=(255, 120, 30))
        _ground(d, (70, 45, 45))
        d.rectangle((0, GROUND + 260, BW, GROUND + 420), fill=(255, 110, 20))
        for x in range(0, BW, 90):
            d.ellipse((x, GROUND + 280, x + 60, GROUND + 330), fill=(255, 210, 80))
    elif kind == "battlefield":
        _hills(d, 60, 140, (130, 120, 90), rnd, 2)
        for x in range(0, BW, 180):
            d.line((x, GROUND - 10, x + 30, GROUND - 160), fill=(110, 80, 50), width=12)
        for fx, col in ((240, (200, 50, 50)), (1000, (50, 90, 200))):
            d.line((fx, GROUND - 60, fx, GROUND - 520), fill=OUT, width=8)
            _poly(d, [(fx, GROUND - 520), (fx + 200, GROUND - 470), (fx, GROUND - 420)], col)
        _ground(d, (120, 100, 75))
    elif kind in ("classroom", "house", "factory"):
        wall = {"classroom": (240, 225, 180), "house": (190, 215, 245), "factory": (170, 170, 175)}[kind]
        d.rectangle((0, 0, BW, GROUND), fill=wall)
        _ground(d, (190, 140, 90) if kind != "factory" else (110, 110, 115), stripes=(160, 115, 70) if kind != "factory" else (90, 90, 95))
        if kind == "classroom":
            _ob(d, (160, 500, BW - 160, 1050), (40, 90, 60), 10)
            d.text((260, 600), "2 + 2 = ?", font=font(110), fill=(240, 240, 230))
            _ob(d, (60, 300, 200, 440), (255, 255, 255), 6, "ellipse")
        if kind == "house":
            _ob(d, (BW - 560, 420, BW - 140, 900), (150, 210, 255), 10)
            d.line((BW - 350, 420, BW - 350, 900), fill=OUT, width=8)
            d.line((BW - 560, 660, BW - 140, 660), fill=OUT, width=8)
            _cloud(d, BW - 330, 560, 50)
            _ob(d, (80, GROUND - 260, 620, GROUND + 40), (230, 90, 90), 7, "round", 30)
            _ob(d, (90, GROUND - 330, 280, GROUND - 230), (255, 255, 255), 6, "round", 30)
            _ob(d, (760, GROUND - 420, 800, GROUND), (90, 70, 50), 5)
            _poly(d, [(700, GROUND - 420), (860, GROUND - 420), (820, GROUND - 540), (740, GROUND - 540)], (250, 220, 120))
        if kind == "factory":
            for gx, gy, r in ((300, 600, 160), (900, 500, 110), (1050, 850, 90)):
                d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=(120, 120, 130), outline=OUT, width=7)
                for a in range(0, 360, 45):
                    ex, ey = gx + (r + 30) * math.cos(math.radians(a)), gy + (r + 30) * math.sin(math.radians(a))
                    d.line((gx, gy, ex, ey), fill=(120, 120, 130), width=40)
                d.ellipse((gx - r * 0.35, gy - r * 0.35, gx + r * 0.35, gy + r * 0.35), fill=wall, outline=OUT, width=6)
            d.rectangle((0, 1150, BW, 1200), fill=(200, 120, 60), outline=OUT, width=5)
    else:
        _ground(d, (120, 190, 100))

    if kind not in ("space", "night_city", "classroom", "house", "factory", "lava"):
        for _ in range(3):
            _cloud(d, rnd.randint(0, BW), rnd.randint(150, 700), rnd.randint(60, 110))

    # painted finish: soften, add paper grain and a warm vignette
    img = img.filter(ImageFilter.GaussianBlur(1.1))
    arr = np.asarray(img).astype(np.float32)
    grain = np.random.default_rng(seed).normal(0, 6, (BH // 4, BW // 4, 1)).astype(np.float32)
    grain = np.asarray(Image.fromarray(np.clip(grain[:, :, 0] + 128, 0, 255).astype(np.uint8)).resize((BW, BH), Image.BICUBIC)).astype(np.float32)[:, :, None] - 128
    yy, xx = np.mgrid[0:BH, 0:BW]
    vig = 1 - 0.28 * (((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH / 2) / (BH / 2)) ** 2) ** 1.4
    arr = arr * vig[:, :, None] + grain
    arr[:, :, 0] *= 1.03
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ particles
PARTICLES = {"space": "stars", "night_city": "stars", "snow": "snow", "lava": "embers",
             "battlefield": "embers", "ocean": "bubbles", "desert": "dust", "pyramids": "dust",
             "arena": "dust"}


def draw_particles(d, kind, t, seed):
    p = PARTICLES.get(kind, "clouds")
    rnd = random.Random(seed)
    if p == "stars":
        for _ in range(40):
            x, y, ph = rnd.randint(0, config.W), rnd.randint(0, 900), rnd.random() * 6
            a = 0.5 + 0.5 * math.sin(t * 3 + ph)
            r = 2 + 3 * a
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, int(180 + 70 * a)))
    elif p == "snow":
        for _ in range(70):
            x0, sp, r = rnd.randint(0, config.W), rnd.uniform(80, 200), rnd.randint(4, 9)
            y = (rnd.randint(0, config.H) + t * sp) % config.H
            x = x0 + 30 * math.sin(t + x0)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))
    elif p == "embers":
        for _ in range(45):
            x0, sp, r = rnd.randint(0, config.W), rnd.uniform(60, 160), rnd.randint(3, 7)
            y = config.H - (rnd.randint(0, config.H) + t * sp) % config.H
            d.ellipse((x0 - r, y - r, x0 + r, y + r), fill=(255, rnd.randint(120, 200), 40))
    elif p == "bubbles":
        for _ in range(25):
            x0, sp, r = rnd.randint(0, config.W), rnd.uniform(60, 140), rnd.randint(8, 20)
            y = config.H - (rnd.randint(0, config.H) + t * sp) % config.H
            d.ellipse((x0 - r, y - r, x0 + r, y + r), outline=(220, 245, 255), width=3)
    elif p == "dust":
        for _ in range(40):
            x = (rnd.randint(0, config.W) + t * rnd.uniform(40, 120)) % config.W
            y, r = rnd.randint(900, config.H), rnd.randint(2, 5)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 225, 170))
    else:  # drifting clouds
        for _ in range(2):
            x = (rnd.randint(0, config.W) + t * rnd.uniform(15, 35)) % (config.W + 400) - 200
            _cloud(d, x, rnd.randint(140, 520), rnd.randint(45, 75))


# ----------------------------------------------------------------- characters
SKIN = (245, 205, 48)
SHIRTS = [(60, 120, 230), (230, 70, 70), (70, 180, 90), (250, 160, 40), (150, 90, 210), (40, 170, 190)]


def char_palette(role, idx, seed):
    rnd = random.Random(seed * 31 + idx)
    if role == "hero":
        return {"shirt": (60, 120, 230), "pants": (40, 50, 80), "skin": SKIN}
    if role == "villain":
        return {"shirt": (170, 30, 40), "pants": (30, 30, 30), "skin": (200, 210, 220)}
    return {"shirt": rnd.choice(SHIRTS[1:]), "pants": rnd.choice([(40, 50, 80), (70, 60, 50), (30, 30, 30)]), "skin": SKIN}


OUTFIT_SHIRT = {"knight": (170, 175, 190), "viking": (140, 100, 60), "pharaoh": (245, 235, 210),
                "samurai": (160, 40, 40), "astronaut": (240, 240, 245), "peasant": (150, 110, 70),
                "king": (150, 40, 150), "soldier": (90, 110, 70), "worker": (240, 130, 40),
                "scientist": (245, 245, 245), "pirate": (40, 40, 50), "gladiator": (190, 150, 90),
                "chef": (250, 250, 250)}


def _limb(d, px, py, length, width, ang, col):
    """Rotated rectangle hanging from pivot (px,py); ang in degrees, 0 = straight down."""
    a = math.radians(ang)
    dx, dy = math.sin(a), math.cos(a)
    nx, ny = dy, -dx
    hw = width / 2
    ex, ey = px + dx * length, py + dy * length
    pts = [(px + nx * hw, py + ny * hw), (ex + nx * hw, ey + ny * hw), (ex - nx * hw, ey - ny * hw), (px - nx * hw, py - ny * hw)]
    d.polygon(pts, fill=col, outline=OUT)
    d.line(pts + [pts[0]], fill=OUT, width=max(3, int(width * 0.09)), joint="curve")
    return ex, ey


def _face(d, cx, cy, s, mood, talking, blink, look=0.0):
    ew = 0.075 * s
    eyy = cy - 0.03 * s
    wide = mood in ("shocked", "scared")
    for side in (-1, 1):
        ex = cx + side * 0.09 * s + look * 0.02 * s
        if blink or mood == "tired":
            d.line((ex - ew, eyy, ex + ew, eyy), fill=OUT, width=max(4, int(0.018 * s)))
        else:
            r = ew * (1.25 if wide else 1.0)
            d.ellipse((ex - r * 0.75, eyy - r, ex + r * 0.75, eyy + r), fill=OUT)
            d.ellipse((ex - r * 0.3, eyy - r * 0.7, ex + r * 0.05, eyy - r * 0.25), fill=(255, 255, 255))
        bw = max(4, int(0.02 * s))
        by = eyy - 0.11 * s
        if mood == "angry":
            d.line((ex - side * 0.07 * s, by - 0.03 * s, ex + side * 0.05 * s, by + 0.02 * s), fill=OUT, width=bw)
        elif mood in ("sad", "scared"):
            d.line((ex - side * 0.07 * s, by + 0.02 * s, ex + side * 0.05 * s, by - 0.03 * s), fill=OUT, width=bw)
        elif wide:
            d.arc((ex - 0.06 * s, by - 0.06 * s, ex + 0.06 * s, by + 0.02 * s), 200, 340, fill=OUT, width=bw)
    my = cy + 0.1 * s
    mw = 0.1 * s
    lw = max(4, int(0.02 * s))
    if talking:
        d.ellipse((cx - mw * 0.6, my - 0.04 * s, cx + mw * 0.6, my + 0.06 * s), fill=(90, 20, 30), outline=OUT, width=lw)
    elif wide:
        d.ellipse((cx - 0.045 * s, my - 0.04 * s, cx + 0.045 * s, my + 0.07 * s), fill=(90, 20, 30), outline=OUT, width=lw)
    elif mood in ("sad", "angry", "scared"):
        d.arc((cx - mw, my, cx + mw, my + 0.1 * s), 200, 340, fill=OUT, width=lw)
    elif mood == "smug":
        d.arc((cx - mw * 0.4, my - 0.06 * s, cx + mw * 1.1, my + 0.04 * s), 10, 150, fill=OUT, width=lw)
    elif mood == "neutral" or mood == "tired":
        d.line((cx - mw * 0.6, my + 0.02 * s, cx + mw * 0.6, my + 0.02 * s), fill=OUT, width=lw)
    else:
        d.chord((cx - mw, my - 0.07 * s, cx + mw, my + 0.07 * s), 0, 180, fill=(90, 20, 30), outline=OUT, width=lw)


def _hat(d, outfit, cx, top, s, hw):
    lw = max(4, int(0.016 * s))
    if outfit == "knight":   # open-face shell, never covers the face
        d.chord((cx - hw - 0.03 * s, top - 0.06 * s, cx + hw + 0.03 * s, top + 0.22 * s), 180, 360, fill=(180, 185, 200), outline=OUT, width=lw)
        d.rectangle((cx - hw - 0.03 * s, top + 0.07 * s, cx - hw + 0.03 * s, top + 0.3 * s), fill=(180, 185, 200), outline=OUT, width=lw)
        d.rectangle((cx + hw - 0.03 * s, top + 0.07 * s, cx + hw + 0.03 * s, top + 0.3 * s), fill=(180, 185, 200), outline=OUT, width=lw)
        d.polygon([(cx - 0.02 * s, top - 0.06 * s), (cx + 0.02 * s, top - 0.06 * s), (cx, top - 0.2 * s)], fill=(220, 50, 50))
    elif outfit in ("viking", "gladiator", "soldier"):
        col = {"viking": (160, 160, 170), "gladiator": (200, 160, 60), "soldier": (80, 100, 60)}[outfit]
        d.chord((cx - hw - 0.02 * s, top - 0.08 * s, cx + hw + 0.02 * s, top + 0.2 * s), 180, 360, fill=col, outline=OUT, width=lw)
        if outfit == "viking":
            for side in (-1, 1):
                d.polygon([(cx + side * hw, top + 0.02 * s), (cx + side * (hw + 0.12 * s), top - 0.2 * s), (cx + side * (hw - 0.04 * s), top - 0.02 * s)], fill=(250, 245, 225), outline=OUT)
        if outfit == "gladiator":
            d.rectangle((cx - 0.03 * s, top - 0.22 * s, cx + 0.03 * s, top - 0.06 * s), fill=(210, 40, 40), outline=OUT, width=lw)
    elif outfit == "pharaoh":
        d.polygon([(cx - hw - 0.08 * s, top + 0.4 * s), (cx - hw, top - 0.04 * s), (cx + hw, top - 0.04 * s), (cx + hw + 0.08 * s, top + 0.4 * s), (cx + hw - 0.02 * s, top + 0.4 * s), (cx + hw - 0.02 * s, top + 0.06 * s), (cx - hw + 0.02 * s, top + 0.06 * s), (cx - hw + 0.02 * s, top + 0.4 * s)], fill=(240, 200, 60), outline=OUT)
        for k in range(4):
            y = top + 0.08 * s + k * 0.08 * s
            d.line((cx - hw - 0.06 * s, y, cx - hw, y), fill=(40, 70, 160), width=lw * 2)
            d.line((cx + hw, y, cx + hw + 0.06 * s, y), fill=(40, 70, 160), width=lw * 2)
    elif outfit == "samurai":
        d.rounded_rectangle((cx - 0.04 * s, top - 0.12 * s, cx + 0.04 * s, top + 0.01 * s), 8, fill=(30, 30, 30))
    elif outfit == "king":
        pts = [(cx - hw, top), (cx - hw, top - 0.14 * s), (cx - hw / 2, top - 0.06 * s), (cx, top - 0.16 * s), (cx + hw / 2, top - 0.06 * s), (cx + hw, top - 0.14 * s), (cx + hw, top)]
        d.polygon(pts, fill=(250, 210, 50), outline=OUT)
        d.ellipse((cx - 0.025 * s, top - 0.06 * s, cx + 0.025 * s, top - 0.01 * s), fill=(220, 40, 60))
    elif outfit == "worker":
        d.chord((cx - hw - 0.03 * s, top - 0.1 * s, cx + hw + 0.03 * s, top + 0.12 * s), 180, 360, fill=(250, 210, 40), outline=OUT, width=lw)
        d.rectangle((cx - hw - 0.06 * s, top, cx + hw + 0.06 * s, top + 0.025 * s), fill=(250, 210, 40), outline=OUT, width=lw)
    elif outfit == "peasant":
        d.polygon([(cx - hw - 0.12 * s, top + 0.02 * s), (cx + hw + 0.12 * s, top + 0.02 * s), (cx, top - 0.14 * s)], fill=(230, 200, 110), outline=OUT)
    elif outfit == "pirate":
        d.polygon([(cx - hw - 0.08 * s, top + 0.02 * s), (cx + hw + 0.08 * s, top + 0.02 * s), (cx + hw * 0.6, top - 0.14 * s), (cx - hw * 0.6, top - 0.14 * s)], fill=(30, 30, 35), outline=OUT)
        d.text((cx - 0.03 * s, top - 0.12 * s), "x", font=font(max(12, int(0.08 * s))), fill=(255, 255, 255))
    elif outfit == "chef":
        d.rounded_rectangle((cx - hw * 0.8, top - 0.22 * s, cx + hw * 0.8, top + 0.02 * s), 20, fill=(255, 255, 255), outline=OUT, width=lw)
    elif outfit == "scientist":
        d.rectangle((cx - hw, top + 0.04 * s, cx + hw, top + 0.08 * s), fill=(60, 60, 60))
        for side in (-1, 1):
            d.ellipse((cx + side * 0.09 * s - 0.05 * s, top + 0.01 * s, cx + side * 0.09 * s + 0.05 * s, top + 0.11 * s), fill=(170, 220, 240), outline=OUT, width=lw)
    elif outfit == "hoodie":
        d.arc((cx - hw - 0.04 * s, top - 0.04 * s, cx + hw + 0.04 * s, top + 0.5 * s), 180, 360, fill=OUT, width=lw * 3)


def draw_character(spec, pal, t, lt, dur, s, talking=False, seed=0):
    """Draws one character on its own RGBA layer. Returns (layer, anchor_x, anchor_y_feet, head_xy)."""
    action, mood, outfit = spec["action"], spec["mood"], spec["outfit"]
    L = int(s * 1.5)
    img = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, feet = L / 2, L * 0.86
    sp = {"run": 14, "walk": 7, "fight": 10, "celebrate": 9, "work": 8}.get(action, 2.5)
    ph = t * sp + seed
    leg_a = arm_a = 0.0
    arm_l = arm_r = None
    bob = abs(math.sin(ph)) * 0.015 * s if action in ("walk", "run") else math.sin(t * 2.2 + seed) * 0.008 * s
    if action in ("walk", "run"):
        amp = 34 if action == "run" else 22
        leg_a = math.sin(ph) * amp
        arm_a = -leg_a * 1.2
    shirt = OUTFIT_SHIRT.get(outfit, pal["shirt"])
    pants = pal["pants"]
    skin = pal["skin"]
    if outfit == "astronaut":
        pants = (230, 230, 235)
    leg_len, leg_w = 0.3 * s, 0.13 * s
    hip_y = feet - leg_len - bob
    torso_h, torso_w = 0.32 * s, 0.42 * s
    sh_y = hip_y - torso_h
    head = 0.34 * s
    # cape for king / gladiator sits behind everything
    if outfit in ("king",):
        d.polygon([(cx - torso_w / 2, sh_y + 10), (cx + torso_w / 2, sh_y + 10), (cx + torso_w * 0.75, feet - 0.02 * s), (cx - torso_w * 0.75, feet - 0.02 * s)], fill=(200, 30, 50), outline=OUT)
    for side, a in ((-1, leg_a), (1, -leg_a)):
        _limb(d, cx + side * 0.1 * s, hip_y - 4, leg_len, leg_w, a, pants)
    d.rounded_rectangle((cx - torso_w / 2, sh_y, cx + torso_w / 2, hip_y), int(0.04 * s), fill=shirt, outline=OUT, width=max(4, int(0.018 * s)))
    if outfit == "scientist":
        d.line((cx, sh_y + 6, cx, hip_y - 4), fill=(200, 200, 200), width=6)
    if outfit == "samurai":
        for k in range(3):
            y = sh_y + 0.06 * s + k * 0.08 * s
            d.line((cx - torso_w / 2 + 6, y, cx + torso_w / 2 - 6, y), fill=(240, 200, 60), width=max(3, int(0.012 * s)))
    if outfit == "chef":
        for k in range(3):
            d.ellipse((cx - 0.02 * s, sh_y + 0.07 * s + k * 0.08 * s, cx + 0.02 * s, sh_y + 0.11 * s + k * 0.08 * s), fill=OUT)
    # arms by action
    base_l, base_r = 8 + arm_a, -8 - arm_a
    if action in ("shock", "scared") or mood == "scared":
        base_l, base_r = 150 + math.sin(t * 30) * 8, -150 - math.sin(t * 30) * 8
    elif action == "celebrate":
        base_l, base_r = 160 + math.sin(ph) * 15, -160 + math.sin(ph) * 15
    elif action == "float":
        base_l, base_r = 70 + math.sin(t * 2) * 15, -70 - math.sin(t * 2) * 15
    elif action == "fight":
        punch = math.sin(ph) > 0
        base_l, base_r = (95 if punch else 30), (-30 if punch else -95)
    elif action == "think":
        base_l, base_r = 10, -150
    elif action == "work":
        base_l, base_r = 10, -120 + math.sin(ph) * 50
    elif action == "talk" or talking:
        base_l, base_r = 12, -35 - abs(math.sin(t * 4)) * 35
    elif action == "sad":
        base_l, base_r = 4, -4
    arm_len, arm_w = 0.3 * s, 0.12 * s
    hl = _limb(d, cx - torso_w / 2 - arm_w * 0.35, sh_y + arm_w * 0.5, arm_len, arm_w, base_l, shirt)
    hr = _limb(d, cx + torso_w / 2 + arm_w * 0.35, sh_y + arm_w * 0.5, arm_len, arm_w, base_r, shirt)
    for hx, hy in (hl, hr):
        r = arm_w * 0.5
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=skin, outline=OUT, width=max(3, int(0.012 * s)))
    if action == "work":
        hx, hy = hr
        d.line((hx, hy, hx + 0.12 * s, hy - 0.12 * s), fill=(110, 80, 50), width=int(0.03 * s))
        d.rectangle((hx + 0.08 * s, hy - 0.18 * s, hx + 0.2 * s, hy - 0.1 * s), fill=(120, 120, 130), outline=OUT, width=4)
    if outfit in ("knight", "samurai", "gladiator", "viking") and action == "fight":
        hx, hy = hl
        d.line((hx, hy, hx + 0.05 * s, hy - 0.42 * s), fill=(220, 225, 235), width=int(0.035 * s))
        d.line((hx - 0.07 * s, hy - 0.02 * s, hx + 0.07 * s, hy + 0.02 * s), fill=(120, 80, 40), width=int(0.03 * s))
    # head
    neck_y = sh_y + 4
    top = neck_y - head
    hw = head * 0.56
    d.rounded_rectangle((cx - hw, top, cx + hw, neck_y), int(0.07 * s), fill=skin, outline=OUT, width=max(4, int(0.018 * s)))
    if outfit == "astronaut":
        d.rounded_rectangle((cx - hw - 0.05 * s, top - 0.05 * s, cx + hw + 0.05 * s, neck_y + 0.03 * s), int(0.12 * s), outline=(200, 230, 255), width=int(0.025 * s))
    blink = (t * 0.7 + seed) % 3.3 < 0.12
    look = math.sin(t * 0.8 + seed) if action == "think" else 0
    face_mood = mood
    if action == "shock":
        face_mood = "shocked"
    if action == "celebrate" and mood == "neutral":
        face_mood = "happy"
    talk_open = talking and (math.sin(t * 22) > -0.2)
    if action == "sleep":
        blink, talk_open = True, False
    _face(d, cx, (top + neck_y) / 2, s, face_mood, talk_open, blink, look)
    if outfit == "pirate":
        d.ellipse((cx + 0.04 * s, top + 0.1 * s, cx + 0.14 * s, top + 0.2 * s), fill=OUT)
    _hat(d, outfit, cx, top, s, hw)
    head_xy = (cx, top)

    # whole-body transforms
    angle, dx, dy, sc = 0.0, 0.0, 0.0, 1.0
    p = min(1.0, lt / max(0.01, dur))
    if action == "jump":
        dy = -abs(math.sin(t * 4)) * 0.25 * s
    elif action == "float":
        dy = -0.18 * s - math.sin(t * 1.8 + seed) * 0.06 * s
        angle = math.sin(t * 1.2 + seed) * 12
    elif action == "shock":
        dx = math.sin(t * 40) * 0.012 * s
    elif action == "fall":
        angle = -min(80, lt * 160)
        dy = min(0.1 * s, lt * 0.2 * s)
    elif action == "sleep":
        angle, dy = 90, 0.23 * s
        d.text((cx + 0.25 * s, top - 0.2 * s - (t * 30 % 40)), "z Z", font=font(max(14, int(0.12 * s))), fill=(255, 255, 255), stroke_width=4, stroke_fill=OUT)
    elif action == "grow":
        sc = 0.8 + 0.6 * p
    elif action == "shrink":
        sc = 1.2 - 0.6 * p
    elif action == "sad":
        dy = 0.01 * s
    if angle:
        pivot = (cx, feet - 0.48 * s) if action == "sleep" else (cx, feet)
        img = img.rotate(angle, resample=Image.BICUBIC, center=pivot)
    if sc != 1.0:
        n = max(8, int(L * sc))
        img = img.resize((n, n), Image.BICUBIC)
        cx, feet = cx * sc, feet * sc
        head_xy = (head_xy[0] * sc, head_xy[1] * sc)
    return img, cx - dx, feet - dy, (head_xy[0] + dx, head_xy[1] + dy)


# ------------------------------------------------------------- speech bubbles
def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_bubble(img, text, hx, hy, pop=1.0, min_y=260):
    """Bubbly cloud speech bubble pointing at a head at (hx, hy)."""
    d = ImageDraw.Draw(img)
    fnt = font(int(64 * pop))
    lines = wrap(text, fnt, 560)
    lh = int(fnt.size * 1.15)
    tw = max(fnt.getlength(l) for l in lines)
    th = lh * len(lines)
    bw, bh = tw + 90, th + 70
    bx = min(max(hx - bw / 2, 30), config.W - bw - 30)
    by = max(hy - bh - 120, min_y)
    cx, cy = bx + bw / 2, by + bh / 2
    blobs = []
    n = 9
    for k in range(n):
        a = 2 * math.pi * k / n
        blobs.append((cx + math.cos(a) * bw * 0.42, cy + math.sin(a) * bh * 0.38, min(bw, bh) * 0.32))
    blobs.append((cx, cy, min(bw, bh) * 0.5))
    tails = [(hx + (cx - hx) * 0.35, hy - 60 + (cy - hy) * 0.35, 18), (hx + (cx - hx) * 0.18, hy - 40 + (cy - hy) * 0.18, 11)]
    for x, y, r in blobs + tails:
        d.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill=OUT)
    for x, y, r in blobs + tails:
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))
    d.rounded_rectangle((cx - bw * 0.42, cy - bh * 0.36, cx + bw * 0.42, cy + bh * 0.36), 30, fill=(255, 255, 255))
    y = cy - th / 2
    for l in lines:
        d.text((cx - fnt.getlength(l) / 2, y), l, font=fnt, fill=(20, 20, 20))
        y += lh
