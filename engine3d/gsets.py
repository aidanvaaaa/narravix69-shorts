from .bsets import *
from .hsets import _tx, medal_extra

TYLER = dict(design='tee', skin='#f0c8a0', arms='#f0c8a0', shirt='#e8e8ec', pants='#2a2a3a', cuff='#f0c8a0', hair='short', haircol='#c8862a', shoes='#ff4a4a')
TYLER_SUIT = dict(design='collar', skin='#f0c8a0', arms='#1c1c26', shirt='#1c1c26', pants='#1c1c26', cuff='#ffffff', hair='short', haircol='#c8862a', shoes='#111111')
JESS = dict(design='tee', skin='#e8b48a', arms='#e8b48a', shirt='#ff5a9a', pants='#ff5a9a', cuff='#e8b48a', hair='long', haircol='#3a1e10', skirt='#ff5a9a', shoes='#ffffff')
BUFF = [dict(design='tee', skin='#c98a5a', arms='#c98a5a', shirt='#1c1c22', pants='#c98a5a', cuff='#c98a5a', hair='short', haircol='#111', shoes='#f4f4f4'),
        dict(design='tee', skin='#f0c8a0', arms='#d42a3a', shirt='#d42a3a', pants='#f0c8a0', cuff='#e8e8e8', hair='short', haircol='#3a2a1a', shoes='#1a1a1a'),
        dict(design='tee', skin='#8a5a3a', arms='#8a5a3a', shirt='#2a6ad8', pants='#22222a', cuff='#8a5a3a', hair='bald', haircol='#111', shoes='#ff7a1a'),
        dict(design='tee', skin='#e8b890', arms='#e8b890', shirt='#2aa85a', pants='#e8b890', cuff='#e8b890', hair='short', haircol='#d8b060', shoes='#5ad8ff')]
FIT = [dict(shorts='#4a4a52', belt='#c42a2a', bands=None, phones=True, band=None, stripe=None, logo='#ffd24a'),
       dict(shorts='#1a1a1e', belt=None, bands='#ffffff', phones=False, band=None, stripe=None, logo='#ffffff'),
       dict(shorts=None, belt='#3a2a1a', bands='#ff7a1a', phones=False, band=None, stripe='#ffffff', logo='#ffffff'),
       dict(shorts='#1c2a5a', belt=None, bands='#1c2a5a', phones=False, band='#ffffff', stripe=None, logo='#1c2a5a')]
def fit_extra(i, more=None):
    f = FIT[i % 4]
    def ex(out, base, hm, arms):
        if f['shorts']:
            out.append(box((0, 1.55, 0), (2.08, 1.0, 1.08), f['shorts'], parent=base, rl=1))
            out.append(box((0, 1.08, 0.545), (2.0, 0.06, 0.02), '#ffffff', parent=base))
        if f['stripe']:
            for sx in (-1.02, 1.02):
                out.append(box((sx, 1.0, 0), (0.04, 2.0, 0.3), f['stripe'], parent=base))
        if f['belt']:
            out.append(box((0, 2.12, 0), (2.12, 0.42, 1.12), f['belt'], parent=base, rl=1))
            out.append(box((0, 2.12, 0.57), (0.45, 0.3, 0.04), '#c8c8d0', parent=base))
        if f['bands']:
            for side in ('ra', 'la'):
                out.append(box((0, -0.9, 0), (0.62, 0.28, 0.62), f['bands'], parent=arms[side], rl=1))
        if f['phones']:
            out.append(box((0, 4.15, -0.1), (1.5, 0.22, 1.1), '#222', parent=base, rl=2))
            for sx in (-0.65, 0.65):
                out.append(box((sx, 4.2, 0.35), (0.3, 0.4, 0.3), '#e82a2a', parent=base, rl=3))
        if f['band']:
            out.append(box((0, 0.98, 0), (1.42, 0.2, 1.42), f['band'], parent=hm, rl=1))
        out.append(box((0, 3.3, 0.53), (0.6, 0.45, 0.03), f['logo'], parent=base, rl=1))
        if more: more(out, base, hm, arms)
    return ex

TRAINER = dict(design='collar', skin='#e8b890', arms='#e8b890', shirt='#ff8a1a', pants='#1c1c24', cuff='#e8b890', hair='short', haircol='#2a1a10', shoes='#fff')
COACH = dict(design='collar', skin='#d8a070', arms='#2a3a6a', shirt='#2a3a6a', pants='#3a3a44', cuff='#d8a070', hair='bald', haircol='#111', shoes='#222')

def headband(col='#e82a2a'):
    def ex(out, base, hm, arms):
        out.append(box((0, 0.98, 0), (1.42, 0.22, 1.42), col, parent=hm, rl=1))
        out.append(box((0.3, 0.98, -0.75), (0.25, 0.14, 0.3), col, parent=hm, R=rot(0, 30, 0)))
        for side in ('ra', 'la'):
            out.append(box((0, -0.95, 0), (0.62, 0.22, 0.62), col, parent=arms[side], rl=1))
    return ex

def whistle_extra(out, base, hm, arms):
    out.append(box((0, 3.6, 0.53), (0.08, 0.9, 0.04), '#222', parent=base))
    out.append(box((0, 3.1, 0.6), (0.25, 0.18, 0.2), '#d8d8e0', parent=base, rl=2))
    out.append(box((0.5, 2.6, 0.62), (0.7, 0.9, 0.06), '#f4f4f4', parent=base))

def tie_extra(out, base, hm, arms):
    out.append(box((0, 3.6, 0.53), (0.32, 0.9, 0.04), '#c42a4a', parent=base, rl=1))
    out.append(box((-0.5, 3.75, 0.54), (0.35, 0.2, 0.04), '#ffffff', parent=base))
    out.append(box((0.5, 3.75, 0.54), (0.35, 0.2, 0.04), '#ffffff', parent=base))

def corsage_extra(out, base, hm, arms):
    out.append(box((0, -0.95, 0), (0.6, 0.35, 0.6), '#ffffff', parent=arms['la'], rl=4))
    out.append(box((0, -0.85, 0.32), (0.3, 0.3, 0.1), '#ff7ab4', parent=arms['la'], rl=4))

def five_lb_img():
    k = 'fivelb'
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (256, 256), (255, 106, 184, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 246, 246), radius=40, outline=(255, 255, 255), width=10)
    d.text((128, 128), '5 LB', font=ImageFont.truetype(FONT_ANTON, 96), fill=(255, 255, 255), anchor='mm')
    _tx[k] = im; return im

def label_img(text, bg, fg, size=(512, 512), fs=110, sub=None):
    k = ('lbl', text, bg, fg, size, sub)
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', size, bg + (255,)); d = ImageDraw.Draw(im)
    d.rectangle((14, 14, size[0] - 15, size[1] - 15), outline=fg, width=12)
    d.text((size[0] / 2, size[1] / 2 - (40 if sub else 0)), text, font=ImageFont.truetype(FONT_ANTON, fs), fill=fg, anchor='mm')
    if sub: d.text((size[0] / 2, size[1] / 2 + 80), sub, font=ImageFont.truetype(FONT_ANTON, int(fs * 0.45)), fill=fg, anchor='mm')
    _tx[k] = im; return im

def tex_box(sc, pos, size, img, R=None, face='pz', emissive=False, col='#ffffff', emit=0.0):
    b = box(pos, size, col, R=R, nocast=True, emit=emit, shade=not emissive)
    b.tex[face] = (img, emissive); sc.add(b)

def held(kind, side='ra', shake=0.0, t=0.0):
    """object held in a hand: 'cup', 'dumbbell', 'scoop', 'shaker', 'phone', 'clipboard'"""
    def ex(out, base, hm, arms):
        j = shake * 0.06 * math.sin(t * 70)
        am = arms[side] @ M4((j, 0, 0))
        if kind == 'cup':
            out.append(box((0, -1.3, 0.35), (0.42, 0.6, 0.42), '#d82a2a', parent=am, rl=1))
            out.append(box((0, -1.02, 0.35), (0.36, 0.04, 0.36), '#ff3a5a', parent=am, emit=0.3))
        elif kind == 'dumbbell':
            out.append(box((0, -1.25, 0.28), (0.16, 0.16, 0.95), '#9a9aa4', parent=am, rl=1))
            for z in (-0.18, 0.74):
                pl = box((0, -1.25, z), (0.62, 0.62, 0.22), '#ff6ab8', parent=am, rl=2)
                pl.tex['px'] = (five_lb_img(), False); pl.tex['nx'] = (five_lb_img(), False); out.append(pl)
        elif kind == 'scoop':
            out.append(box((0, -1.3, 0.3), (0.3, 0.25, 0.3), '#ffffff', parent=am, rl=2))
            out.append(box((0, -1.2, 0.3), (0.24, 0.06, 0.24), '#ff4ad8', parent=am))
        elif kind == 'shaker':
            out.append(box((0, -1.4, 0.3), (0.45, 0.85, 0.45), '#2a2a2a', parent=am, rl=1))
            out.append(box((0, -1.0, 0.3), (0.4, 0.15, 0.4), '#ff4a4a', parent=am, rl=1))
            lb = box((0, -1.42, 0.54), (0.42, 0.5, 0.02), '#ffffff', parent=am, nocast=True); lb.tex['pz'] = (label_img('PROTEIN', (230, 40, 40), (255, 255, 255), size=(300, 360), fs=70), False); out.append(lb)
        elif kind == 'phone':
            out.append(box((0, -1.25, 0.25), (0.12, 0.6, 0.35), '#111', parent=am, rl=1))
        elif kind == 'clipboard':
            out.append(box((0, -1.3, 0.4), (0.06, 0.9, 0.7), '#8a5a3a', parent=am))
            out.append(box((0.04, -1.3, 0.4), (0.02, 0.8, 0.6), '#ffffff', parent=am))
    return ex

# ---------------- gym ----------------
BENCH = (0, 0, 0)
BAR_Y = 4.25
BAR_Z = -1.35
def gym(sc, t, dark=False, crowd=None, lights_on=1.0):
    sc.sky = (C('#0a0a10'), C('#14141e')); sc.suncol = C((0.05, 0.05, 0.06))
    sc.ambient = C((0.42, 0.42, 0.46)) if not dark else C((0.18, 0.2, 0.28))
    room(sc, 30, 26, 10, '#2a2c34', '#1e1e24', floor_tile=1.5, floor_j=0.04, ceil='#202228', floor_mat='carpet')
    sc.add(box((0, 2.0, -12.9), (30, 4.0, 0.1), '#e8c020', nocast=True))     # yellow stripe
    # mirrors back wall
    sc.add(box((0, 6.2, -12.88), (22, 4.0, 0.06), '#a8c8dc', emit=0.15))
    for x in np.arange(-11, 11.1, 5.5):
        sc.add(box((x, 6.2, -12.84), (0.15, 4.1, 0.06), '#888'))
    for k, (txt, x) in enumerate((('NO PAIN NO GAIN', -9), ('BEAST MODE', 9))):
        p = box((x, 8.9, -12.82), (6.5, 1.1, 0.06), '#fff', nocast=True)
        p.tex['pz'] = (sign_img(txt, (20, 20, 24), (255, 210, 40), size=(1000, 170), fs=120), True); sc.add(p)
    # ceiling light strips
    for z in (-8, -2, 4, 10):
        sc.add(box((0, 9.9, z), (16, 0.1, 0.6), '#ffffff', emit=1.6 * lights_on, shade=lights_on < 0.5))
    if lights_on > 0.5:
        sc.lights.append(dict(pos=(0, 8.5, 0), col='#f0f4ff', I=0.55, r=16))
        sc.lights.append(dict(pos=(0, 8.5, -8), col='#f0f4ff', I=0.4, r=12))
    # dumbbell rack (right wall)
    sc.add(box((13.4, 1.2, -2), (1.6, 0.2, 12), '#3a3a40'), box((13.4, 2.4, -2), (1.6, 0.2, 12), '#3a3a40'))
    for z in np.arange(-7.5, 4, 1.1):
        for y in (1.5, 2.7):
            sc.add(box((13.4, y, z), (1.2, 0.5, 0.5), '#2a2a2a', rl=2))
    # plate trees, squat rack (left)
    for z in (-8, 6):
        for k in range(6):
            sc.add(box((-13.6, 1.0 + k * 0.45, z), (0.5, 2.2 - k * 0.15, 2.2 - k * 0.15), '#1a1a1a', rl=4))
    sc.add(box((-11, 4.5, -3), (0.3, 9, 0.3), '#c42a2a'), box((-8, 4.5, -3), (0.3, 9, 0.3), '#c42a2a'), box((-9.5, 8.9, -3), (3.4, 0.3, 0.3), '#c42a2a'))
    # main bench (center)
    bench_press(sc, BENCH)

def bench_press(sc, p, bar=True):
    x, y, z = p
    sc.add(box((x, 1.6, z), (1.4, 0.3, 5.2), '#c42a2a', rl=1), box((x, 0.8, z + 1.8), (0.3, 1.6, 0.3), '#333'), box((x, 0.8, z - 1.8), (0.3, 1.6, 0.3), '#333'),
           box((x, 0.1, z), (1.6, 0.2, 4.6), '#333'))
    for sx in (-1.5, 1.5):
        sc.add(box((x + sx, 2.6, z - 1.9), (0.25, 5.2, 0.25), '#2a2a30'), box((x + sx, 4.65, z - 1.65), (0.35, 0.15, 0.5), '#888'))

def barbell(sc, y, z=BAR_Z, x0=0, plates=0, tilt=0.0, shake=0.0, t=0.0):
    j = shake * 0.05 * math.sin(t * 60)
    base = M4((x0, y + j, z), rot(0, 0, tilt))
    out = [box((0, 0, 0), (7.0, 0.14, 0.14), '#c8c8d0', parent=base, rl=1)]
    for sx in (-1, 1):
        out.append(box((sx * 2.9, 0, 0), (1.2, 0.22, 0.22), '#a8a8b0', parent=base, rl=1))
        out.append(box((sx * 2.25, 0, 0), (0.12, 0.4, 0.4), '#888', parent=base, rl=2))
        for k in range(plates):
            out.append(box((sx * (2.45 + k * 0.28), 0, 0), (0.24, 2.2, 2.2), '#1a1a1a', parent=base, rl=4))
    sc.add(out)

def broomstick(sc, y, z=BAR_Z, shake=0.0, t=0.0):
    j = shake * 0.06 * math.sin(t * 60)
    sc.add(box((0, y + j, z), (6.5, 0.12, 0.12), '#c8964a', rl=1))
    sc.add(box((3.6, y + j, z), (0.9, 0.5, 0.7), '#e8d08a', rl=1), box((4.15, y + j, z), (0.3, 0.6, 0.9), '#d8c070'))

def lying_tyler(sc, face='focus', pose=None, extra=None, skin=None, outfit=None):
    o = dict(outfit or TYLER)
    if skin: o['skin'] = skin; o['cuff'] = skin; o['arms'] = skin if o['arms'] == TYLER['arms'] else o['arms']
    p = dict(ra=90, la=90, re=0, le=0)
    if pose: p.update(pose)
    character(sc, (0, 2.25, 2.6), root_R=rot(0, -90, 0), pose=p, face=face, blob=False, idle=False, extra=extra, **o)

def aura2(sc, gt, pos, strength=1.0, lying=False, skip_front=True):
    n = 64
    for k in range(n):
        ph = (gt * 2.1 + (k * 0.618) % 1.0) % 1.0
        a = k / n * 2 * math.pi + gt * 0.6
        if lying:
            x = pos[0] + math.cos(a) * 1.6; z = pos[2] + math.sin(a) * 2.8; y = pos[1] + ph * 4.5
        else:
            r = 1.45 + 0.25 * math.sin(gt * 9 + k)
            x = pos[0] + math.cos(a) * r * 1.05; z = pos[2] + math.sin(a) * r * 0.7; y = pos[1] + 0.2 + ph * 7.2 * (0.8 + 0.2 * math.sin(k))
            if skip_front and z > pos[2] + 0.2 and abs(x - pos[0]) < 1.25: continue
        sz = (0.75 * (1 - ph) ** 0.7 + 0.12) * strength
        col = '#bff6ff' if ph < 0.15 else ('#46c8ff' if ph < 0.55 else '#1f5cff')
        sc.add(box((x, y, z), (sz * 0.65, sz * 2.0, sz * 0.65), col, emit=1.3, shade=False, rl=4, nocast=True, R=rot(0, 0, math.sin(gt * 7 + k) * 10)))
    if int(gt * 12) % 3 != 0:
        rb = random.Random(int(gt * 12))
        for j in range(2):
            x0 = pos[0] + rb.choice((-1, 1)) * rb.uniform(1.4, 2.1); y0 = pos[1] + rb.uniform(1.5, 5.0); z0 = pos[2] + rb.uniform(-1.0, 1.0)
            for q in range(4):
                ang = rb.uniform(-70, 70)
                sc.add(box((x0, y0, z0), (0.05, 0.5, 0.05), '#dff8ff', emit=2.2, shade=False, nocast=True, R=rot(0, 0, ang)))
                x0 += math.sin(math.radians(ang)) * 0.45; y0 -= math.cos(math.radians(ang)) * 0.45
    sc.lights.append(dict(pos=(pos[0], pos[1] + 3.0, pos[2] + 1.8), col='#2a78ff', I=(0.9 + 0.25 * math.sin(gt * 19)) * strength, r=4.0))

def sweat(sc, gt, center, n=14, spread=1.6, seed=0):
    rr = random.Random(seed)
    for k in range(n):
        ph = (gt * 1.6 + rr.random()) % 1.0
        a = rr.uniform(0, 2 * math.pi); sp = rr.uniform(1.5, 3.0)
        x = center[0] + math.cos(a) * sp * ph * spread * 0.6; z = center[2] + math.sin(a) * sp * ph * spread * 0.6
        y = center[1] + 2.2 * ph - 4.0 * ph * ph
        sc.add(box((x, y, z), (0.13, 0.18, 0.13), '#8ad8ff', emit=0.6, shade=False, nocast=True, rl=4))

# ---------------- homecoming dance ----------------
def hoco_banner():
    k = 'hoco'
    if k in _tx: return _tx[k]
    W_, H_ = 1600, 260
    im = Image.new('RGB', (W_, H_))
    for x in range(W_):
        a = x / W_; ImageDraw.Draw(im).line((x, 0, x, H_), fill=(int(120 + 100 * a), int(30 + 20 * a), int(200 - 60 * a)))
    im = im.convert('RGBA'); d = ImageDraw.Draw(im)
    rr_ = random.Random(2)
    for _ in range(120):
        x, y, r = rr_.randint(0, W_), rr_.randint(0, H_), rr_.randint(2, 6); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 140, 160))
    d.rectangle((0, 0, W_ - 1, H_ - 1), outline=(255, 210, 90), width=10)
    f = ImageFont.truetype(FONT_ANTON, 170)
    d.text((W_ / 2 + 6, H_ / 2 + 8), 'HOMECOMING', font=f, fill=(30, 0, 50), anchor='mm')
    d.text((W_ / 2, H_ / 2), 'HOMECOMING', font=f, fill=(255, 240, 200), anchor='mm', stroke_width=6, stroke_fill=(200, 140, 30))
    _tx[k] = im; return im

def dance_hall(sc, t, crowd=True):
    sc.sky = (C('#05030a'), C('#0a0614')); sc.suncol = C((0.04, 0.03, 0.06)); sc.ambient = C((0.26, 0.2, 0.36))
    room(sc, 32, 28, 11, '#2a1a40', '#1a1a24', floor_tile=1.6, floor_j=0.05, ceil='#140c20', floor_mat='checker')
    bn = box((0, 8.2, -13.85), (14, 2.27, 0.08), '#fff', nocast=True); bn.tex['pz'] = (hoco_banner(), True); sc.add(bn)
    # balloon arch
    cols = ['#ffd24a', '#c07aff', '#ffffff', '#ff7ab4']
    for k in range(26):
        a = math.pi * k / 25
        sc.add(box((math.cos(a) * 7.5, 0.6 + math.sin(a) * 7.0, -13.2), (1.0, 1.15, 1.0), cols[k % 4], rl=4))
    # disco ball + moving colored spots
    sc.add(box((0, 9.6, -2), (1.4, 1.4, 1.4), '#d8d8e8', rl=4, emit=0.6), box((0, 10.5, -2), (0.05, 1.0, 0.05), '#888'))
    for k, c in enumerate(('#ff3ab4', '#3ab0ff', '#b03aff', '#ffd23a')):
        a = t * 0.9 + k * 1.57
        px, pz = math.cos(a) * 6, -2 + math.sin(a) * 6
        sc.add(box((px, 0.03, pz), (2.6, 0.02, 2.6), c, emit=1.0, shade=False, rl=4, nocast=True))
        sc.lights.append(dict(pos=(px, 3.0, pz), col=c, I=0.9, r=6))
    rr = random.Random(int(t * 6))
    for j in range(24):
        sc.add(box((rr.uniform(-14, 14), rr.uniform(3, 10), rr.uniform(-13, 10)), (0.08, 0.08, 0.08), '#ffffff', emit=2.5, shade=False, nocast=True, rl=4))
    # punch table (right)
    sc.add(box((9.5, 2.0, -6), (5, 0.2, 2.4), '#ffffff', rl=1), box((9.5, 1.0, -6), (4.8, 2.0, 2.2), '#c07aff'),
           box((9.5, 2.6, -6), (1.6, 1.0, 1.6), '#ffd0e0', rl=4, emit=0.1), box((9.5, 2.9, -6), (1.3, 0.1, 1.3), '#e82a4a', emit=0.2))
    for k in range(5):
        sc.add(box((8.0 + k * 0.7, 2.4, -5.3), (0.3, 0.45, 0.3), '#d82a2a', rl=1))
    sc.lights.append(dict(pos=(0, 8, 2), col='#c8a0ff', I=0.35, r=16))
    if crowd:
        for k, (x, z) in enumerate(((-8, -9.5), (-5, -10.5), (-2, -11), (3, -10.5), (6.5, -10), (-11, -5), (11, -6), (-11, 3), (12, 2))):
            bob = 0.15 * abs(math.sin(t * 6 + k))
            o = [KIDS[k % len(KIDS)], JALEN, KIDS[(k + 2) % len(KIDS)]][k % 3]
            character(sc, (x, bob, z), yaw=180 * (z > -5) + 20 * math.sin(k), pose=dict(ra=60 + 60 * abs(math.sin(t * 6 + k)), la=40, re=40), face='grin', **o)
