from .hsets import *
from .hsets import _tx

# ---------------- characters ----------------
HERO = dict(design='hoodie', skin='#f0c8a0', arms='#f2a23a', shirt='#f2a23a', pants='#3a4a6a', cuff='#f0c8a0', hair='short', haircol='#6a3a1a', shoes='#e8e8e8')
BRO = dict(design='tee_logo', skin='#f0c8a0', arms='#2a3aa8', shirt='#2a3aa8', pants='#1c1c26', cuff='#f0c8a0', hair='short', haircol='#6a3a1a', shoes='#ffd24a')
MAYA = dict(design='tee', skin='#c98a5a', shirt='#9a4aff', pants='#2a2a3a', cuff='#c98a5a', hair='long', haircol='#2a1410', skirt='#ff7ac8', shoes='#ffffff')
GRANDMA = dict(design='collar', skin='#e8c0a0', arms='#8a5ab0', shirt='#8a5ab0', pants='#5a4a6a', cuff='#e8c0a0', hair='gray', haircol='#d8d8de', skirt='#6a4a8a', shoes='#3a2a2a')
HEROGUY = dict(design='tee_logo', skin='#e8b890', arms='#d42a3a', shirt='#2a6ad8', pants='#d42a3a', cuff='#e8b890', hair='short', haircol='#1a1a1a', shoes='#d42a3a')
BULLIES = [dict(KIDS[i]) for i in range(len(KIDS))]

def glasses_extra(out, base, hm, arms):
    for sx in (-0.3, 0.3):
        out.append(box((sx, 0.72, 0.62), (0.42, 0.32, 0.04), '#3a2a2a', parent=hm, rl=1))
        out.append(box((sx, 0.72, 0.6), (0.32, 0.22, 0.04), '#e8f4ff', parent=hm, emit=0.15))
    out.append(box((0, 0.76, 0.62), (0.2, 0.06, 0.04), '#3a2a2a', parent=hm))

def apron_extra(out, base, hm, arms):
    out.append(box((0, 2.6, 0.53), (1.6, 2.2, 0.06), '#ffffff', parent=base, rl=1))
    out.append(box((0, 2.3, 0.57), (0.9, 0.5, 0.03), '#ff9ab8', parent=base, rl=1))

def grandma_extra(out, base, hm, arms):
    glasses_extra(out, base, hm, arms); apron_extra(out, base, hm, arms)
    out.append(box((0, 1.45, -0.2), (0.7, 0.55, 0.7), '#d8d8de', parent=hm, rl=4))   # bun

def cape_extra(out, base, hm, arms):
    out.append(box((0, 2.6, -0.62), (2.1, 3.2, 0.08), '#d42a3a', parent=base @ M4((0, 0, 0), rot(0, -8, 0)), rl=1))
    out.append(box((0, 0.72, 0.62), (1.25, 0.3, 0.05), '#111', parent=hm, rl=1))
    out.append(box((0, 3.2, 0.54), (0.6, 0.6, 0.04), '#ffd24a', parent=base, rl=3, emit=0.3))

def bolt_hands(t, strength=1.0):
    def ex(out, base, hm, arms):
        rb = random.Random(int(t * 15))
        for side in ('ra', 'la'):
            for j in range(int(4 * strength) + 1):
                x0, y0 = 0.0, -1.3
                for q in range(3):
                    ang = rb.uniform(-80, 80)
                    out.append(box((x0, y0, 0), (0.07, 0.42, 0.07), '#fff6a0', parent=arms[side], emit=2.6, shade=False, nocast=True, R=rot(0, 0, ang)))
                    x0 += math.sin(math.radians(ang)) * 0.38; y0 -= math.cos(math.radians(ang)) * 0.38
    return ex

def combine(*exs):
    exs = [e for e in exs if e]
    def ex(out, base, hm, arms):
        for e in exs: e(out, base, hm, arms)
    return ex

# ---------------- toast ----------------
def toast(sc, pos, R=None, s=1.0, butter=True, glow=0.0, parent=None):
    base = (parent if parent is not None else np.eye(4)) @ M4(pos, R if R is not None else np.eye(3))
    out = [box((0, 0, 0), (1.0 * s, 1.05 * s, 0.22 * s), '#a8641e', parent=base, rl=2, emit=0.12 * glow),
           box((0, 0, 0), (0.86 * s, 0.9 * s, 0.24 * s), '#e8a848', parent=base, rl=1, emit=0.2 * glow),
           box((0, 0.5 * s, 0), (0.75 * s, 0.25 * s, 0.22 * s), '#a8641e', parent=base, rl=4)]
    if butter:
        out.append(box((0.05 * s, 0.02 * s, 0.13 * s), (0.34 * s, 0.3 * s, 0.05 * s), '#fff09a', parent=base, rl=2, emit=0.25 + 0.3 * glow))
    sc.add(out)

def pop_fx(sc, pos, dt, scale=1.0, seed=0):
    """golden burst + crumbs + steam right after a POP (dt seconds after)"""
    if dt < 0 or dt > 0.9: return
    rr = random.Random(seed)
    k = dt / 0.9
    for j in range(18):
        a = rr.uniform(0, 2 * math.pi); el = rr.uniform(-0.4, 1.2); sp = rr.uniform(2.5, 5) * scale
        d = sp * dt
        p = (pos[0] + math.cos(a) * d * math.cos(el), pos[1] + math.sin(el) * d - 3 * dt * dt, pos[2] + math.sin(a) * d * math.cos(el))
        sz = 0.16 * (1 - k) * scale
        if sz > 0.01:
            sc.add(box(p, (sz, sz, sz), rr.choice(['#fff2a0', '#ffd24a', '#ffffff']), emit=2.0, shade=False, nocast=True, rl=4))
    for j in range(8):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(0.3, 1.0) * scale * (0.4 + dt)
        sc.add(box((pos[0] + math.cos(a) * d, pos[1] + dt * 1.6 + j * 0.1, pos[2] + math.sin(a) * d), (0.3 * scale * (1 - k), 0.3 * scale * (1 - k), 0.3 * scale * (1 - k)), '#ffffff', emit=0.5, shade=False, nocast=True, rl=4))
    if dt < 0.25:
        r = (0.4 + dt * 6) * scale
        for j in range(12):
            a = j / 12 * 2 * math.pi
            sc.add(box((pos[0] + math.cos(a) * r, pos[1] + math.sin(a) * r, pos[2]), (0.08, 0.3, 0.08), '#fff6c0', emit=3, shade=False, nocast=True, R=rot(0, 0, math.degrees(a) - 90)))
    sc.lights.append(dict(pos=(pos[0], pos[1] + 0.5, pos[2] + 0.8), col='#ffc860', I=2.2 * (1 - k) * scale, r=4.5))

def toast_rise(dt):
    """height of a popped slice over the hands after dt seconds"""
    if dt < 0: return None
    return 1.2 * math.sin(min(dt, 0.35) / 0.35 * math.pi / 2) - (max(0, dt - 0.35) ** 2) * 0.0

def snow(sc, t, center, n=220, area=14.0, top=16.0, wind=6.0, size=0.11):
    rr = random.Random(55)
    cx, cy, cz = center
    for k in range(n):
        x0 = rr.uniform(-area, area); z = cz + rr.uniform(-area, area); sp = rr.uniform(2.5, 4.5)
        y = top - ((t * sp + rr.uniform(0, top)) % top)
        x = cx + ((x0 + (top - y) / sp * wind + area) % (2 * area)) - area
        sc.add(box((x, cy + y, z), (size, size, size), '#ffffff', emit=0.9, shade=False, nocast=True, rl=4))

def candle(sc, pos, t, s=1.0):
    fl = 1 + 0.15 * math.sin(t * 21 + pos[0]) + 0.08 * math.sin(t * 33)
    sc.add(box((pos[0], pos[1] + 0.3 * s, pos[2]), (0.25 * s, 0.6 * s, 0.25 * s), '#f4ecd8', rl=1),
           box((pos[0], pos[1] + 0.7 * s, pos[2]), (0.1 * s, 0.2 * s * fl, 0.1 * s), '#ffb030', emit=3, shade=False, rl=4, nocast=True))
    sc.lights.append(dict(pos=(pos[0], pos[1] + 1.0 * s, pos[2] + 0.3), col='#ff9a40', I=1.4 * fl, r=5.5))

# ---------------- birthday living room ----------------
def bday_banner():
    k = 'bday10'
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (1400, 260), (255, 120, 180, 255)); d = ImageDraw.Draw(im)
    rr = random.Random(3)
    for _ in range(90):
        x, y = rr.randint(0, 1400), rr.randint(0, 260); r = rr.randint(3, 7)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rr.choice([(255, 230, 90), (120, 220, 255), (255, 255, 255)]))
    d.text((700, 130), 'HAPPY 10TH BIRTHDAY!', font=ImageFont.truetype(FONT_ANTON, 160), fill=(255, 255, 255), anchor='mm', stroke_width=8, stroke_fill=(180, 40, 110))
    _tx[k] = im; return im

CAKE = (0, 2.35, 1.2)
def party_room(sc, t, candles=True, mood=0.0):
    """mood 0 = bright party, 1 = cold awkward silence"""
    sc.sky = (C('#9fd0ff'), C('#e6f4ff'))
    sc.ambient = C(lerp((0.46, 0.42, 0.4), (0.38, 0.4, 0.47), mood)); sc.suncol = C(lerp((0.4, 0.36, 0.3), (0.24, 0.24, 0.28), mood))
    room(sc, 20, 18, 8.5, '#ffd8a8', '#9a6a44', floor_tile=1.0, floor_j=0.06)
    window(sc, (-5, 4.6, -8.95), 4, 3, sky='#bfe4ff', emit=1.0); window(sc, (5, 4.6, -8.95), 4, 3, sky='#bfe4ff', emit=1.0)
    sc.add(box((0, 0.03, 0.5), (10, 0.06, 8), '#5ab0d8', bg=True, mat='carpet'))
    bn = box((0, 7.3, -8.9), (9, 1.6, 0.06), '#fff', nocast=True); bn.tex['pz'] = (bday_banner(), False); sc.add(bn)
    # table + cake
    sc.add(box((0, 1.0, 1.2), (5.0, 0.2, 3.0), '#ffffff', rl=1), box((0, 0.5, 1.2), (4.6, 1.0, 2.6), '#e8e0d8'))
    cx, top, cz = CAKE[0], 1.1, CAKE[2]
    sc.add(box((cx, top + 0.45, cz), (1.6, 0.9, 1.6), '#ffeef4', rl=1), box((cx, top + 0.92, cz), (1.64, 0.12, 1.64), '#5ac8ff', rl=2),
           box((cx, top + 1.3, cz), (1.05, 0.65, 1.05), '#ff9ac8', rl=1), box((cx, top + 1.64, cz), (1.08, 0.08, 1.08), '#ffffff', rl=2))
    ct = top + 1.68
    if candles:
        fl = 1 + 0.18 * math.sin(t * 23) + 0.1 * math.sin(t * 37)
        sc.add(box((cx - 0.25, ct + 0.3, cz), (0.12, 0.6, 0.12), '#5ac8ff', rl=1, emit=0.3))
        for (ox, oy, w, h) in ((0.12, 0.3, 0.1, 0.6), (0.42, 0.3, 0.1, 0.6), (0.27, 0.05, 0.4, 0.1), (0.27, 0.55, 0.4, 0.1)):
            sc.add(box((cx + ox, ct + oy, cz), (w, h, 0.12), '#5ac8ff', rl=1, emit=0.3))
        for fx in (-0.25, 0.27):
            sc.add(box((cx + fx, ct + 0.72 + (0.0 if fx < 0 else -0.05), cz), (0.1, 0.22 * fl, 0.1), '#ffb030', emit=3, shade=False, rl=4, nocast=True))
        sc.lights.append(dict(pos=(cx, ct + 1.0, cz + 0.6), col='#ffb050', I=1.4 * fl, r=4))
    else:
        sc.add(box((cx - 0.25, ct + 0.3, cz), (0.12, 0.6, 0.12), '#5ac8ff', rl=1))
        for (ox, oy, w, h) in ((0.12, 0.3, 0.1, 0.6), (0.42, 0.3, 0.1, 0.6), (0.27, 0.05, 0.4, 0.1), (0.27, 0.55, 0.4, 0.1)):
            sc.add(box((cx + ox, ct + oy, cz), (w, h, 0.12), '#5ac8ff', rl=1))
    # balloons
    cols = ['#ff5a8a', '#5ac8ff', '#ffd24a', '#8aff6a', '#c07aff', '#ff8a3a']
    for k, (x, z) in enumerate(((-7, -6), (-6, -4.5), (-7.5, -3), (7, -6), (6.2, -4.6), (7.6, -3.2), (-3, -7.5), (3, -7.5))):
        y = 6.6 + 0.15 * math.sin(t * 1.1 + k)
        sc.add(box((x, y, z), (1.0, 1.25, 1.0), cols[k % 6], rl=4), box((x, (y - 0.6) / 2, z), (0.03, y - 0.6, 0.03), '#dddddd', nocast=True))
    rr = random.Random(6)
    for _ in range(40):
        sc.add(box((rr.uniform(-6, 6), 0.08, rr.uniform(-3, 6)), (0.15, 0.02, 0.15), rr.choice(['#ffd24a', '#ff5a8a', '#5ac8ff', '#ffffff']), R=rot(rr.uniform(0, 90)), nocast=True))
    for (x, z, s_, c, rc) in ((-6.5, 3, 1.0, '#8a3aff', '#ffd24a'), (-5.6, 4.2, 0.8, '#ff5a8a', '#ffffff'), (6.2, 3.6, 0.9, '#5ac8ff', '#ff5a8a')):
        sc.add(box((x, s_ / 2, z), (s_, s_, s_), c, rl=1), box((x, s_ / 2, z), (s_ + 0.03, s_ + 0.03, 0.14), rc), box((x, s_ / 2, z), (0.14, s_ + 0.03, s_ + 0.03), rc))
    sc.lights.append(dict(pos=(0, 7, 2), col='#fff0d8', I=0.3 * (1 - 0.6 * mood), r=12))

def party_hat_c(col): return party_hat(col)

# ---------------- school ----------------
def schoolyard(sc, t, mood=0.0):
    sc.sky = (C(lerp(C('#6ab0ff'), C('#8a9ab0'), mood)), C(lerp(C('#dff0ff'), C('#c8ccd4'), mood)))
    sc.ambient = C(lerp((0.62, 0.62, 0.62), (0.5, 0.52, 0.58), mood)); sc.suncol = C(lerp((0.55, 0.5, 0.4), (0.25, 0.26, 0.3), mood))
    sc.sun = np.array([0.5, -0.8, 0.3]); sc.fog = C((0.85, 0.88, 0.95)); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#5aa84a', bg=True, mat='grass'))
    sc.add(box((0, -0.45, 2), (40, 1, 18), '#4a4a52', bg=True, mat='asphalt'))
    for x in np.arange(-16, 17, 4):
        sc.add(box((x, 0.06, 2), (0.15, 0.02, 3), '#f0f0f0', nocast=True))
    # school building
    sc.add(box((0, 6, -14), (44, 12, 6), '#c8584a', mat='wall'), box((0, 12.3, -14), (45, 0.6, 6.4), '#8a3a32'))
    for x in np.arange(-18, 19, 4.5):
        for y in (3.5, 8.5):
            sc.add(box((x, y, -10.95), (2.4, 2.2, 0.1), '#9ad0ff', emit=0.3, shade=False))
    sg = box((0, 10.6, -10.9), (12, 1.6, 0.1), '#fff', nocast=True)
    sg.tex['pz'] = (sign_img('SUPER ACADEMY', (30, 50, 120), (255, 220, 80)), True); sc.add(sg)
    sc.add(box((0, 2.5, -10.95), (3.4, 5, 0.12), '#5a3a22', mat='wood'))
    for x in (-24, 24):
        sc.add(box((x, 3, -2), (1.2, 6, 1.2), '#5a3a22'), box((x, 7, -2), (6, 4, 6), '#3a8a3a', rl=3))

def classroom_hall(sc):
    school(sc)

def cafeteria(sc, t, mood=0.0):
    sc.sky = (C('#9fd0ff'), C('#e6f4ff'))
    sc.ambient = C(lerp((0.62, 0.62, 0.64), (0.48, 0.5, 0.58), mood)); sc.suncol = C((0.3, 0.3, 0.3))
    sc.sun = np.array([0.2, -1, 0.1])
    room(sc, 26, 22, 9, '#e8ecd8', '#d8d8d0', floor_tile=1.4, floor_j=0.06, ceil='#f4f4f4', floor_mat='tile')
    for x in (-7, 7):
        window(sc, (x, 5, -10.95), 6, 3.4, sky='#cfe8ff', emit=1.0)
    for (x, z) in ((-6.5, -4), (6.5, -4), (-6.5, 3.5), (6.5, 3.5), (0, -0.5)):
        sc.add(box((x, 1.6, z), (6.5, 0.2, 2.4), '#e8e8e8', rl=1), box((x, 0.8, z), (6.0, 1.6, 0.3), '#8a8a92'))
        for bz in (z - 1.9, z + 1.9):
            sc.add(box((x, 0.9, bz), (6.0, 0.2, 0.9), '#3a6ad0', rl=1), box((x, 0.45, bz), (5.8, 0.9, 0.2), '#8a8a92'))
    for z in np.arange(-8, 9, 6):
        sc.add(box((0, 8.95, z), (5, 0.1, 1.2), '#ffffff', emit=1.4, shade=False))
    sc.lights.append(dict(pos=(0, 8, 0), col='#ffffff', I=0.5 * (1 - 0.5 * mood), r=14))

def tray(sc, pos, R=None):
    base = M4(pos, R if R is not None else np.eye(3))
    sc.add([box((0, 0, 0), (1.6, 0.08, 1.1), '#e86a3a', parent=base, rl=1),
            box((-0.4, 0.1, 0), (0.5, 0.12, 0.7), '#f4e08a', parent=base, rl=2),
            box((0.35, 0.18, -0.2), (0.35, 0.3, 0.35), '#ffffff', parent=base, rl=1),
            box((0.35, 0.1, 0.25), (0.5, 0.1, 0.35), '#5ab04a', parent=base, rl=2)])

# ---------------- grandma's diner ----------------
def diner_sign(text='GRANDMA\'S DINER'):
    return neon_img(text, (255, 120, 60))

def diner(sc, t, mood='sunday', lights=1.0, sign_text="GRANDMA'S"):
    """mood: sunday (warm), empty (grey), night (lamp), dark (blackout), candle"""
    warm = mood in ('sunday', 'final')
    if mood == 'sunday':
        sc.sky = (C('#ffcf8a'), C('#fff0d0')); sc.ambient = C((0.43, 0.38, 0.33)); sc.suncol = C((0.42, 0.34, 0.24))
    elif mood == 'empty':
        sc.sky = (C('#9aa4b4'), C('#d0d4dc')); sc.ambient = C((0.38, 0.39, 0.43)); sc.suncol = C((0.18, 0.18, 0.2))
    elif mood in ('night', 'final'):
        sc.sky = (C('#141a3a'), C('#2a2a50')); sc.ambient = C((0.3, 0.28, 0.36)); sc.suncol = C((0.05, 0.05, 0.08))
    else:  # dark / candle
        sc.sky = (C('#0a0e20'), C('#141a30')); sc.ambient = C((0.17, 0.19, 0.28)); sc.suncol = C((0.05, 0.05, 0.08))
    sc.sun = np.array([0.4, -0.7, -0.6])
    room(sc, 20, 16, 8, '#f4e2c4', '#ffffff', floor_tile=1.0, floor_j=0.04, ceil='#f4ecdc', floor_mat='checker')
    sc.add(box((0, 2.0, -7.9), (20, 4.0, 0.1), '#2aa8a0', nocast=True))   # teal wainscot back wall
    skyc = {'sunday': '#ffd890', 'empty': '#b8c0cc', 'night': '#1a2050', 'final': '#1a2050', 'dark': '#0a1028', 'candle': '#0a1028'}[mood]
    for x in (-5.5, 5.5):
        window(sc, (x, 4.6, 7.95), 5, 3, R=rot(180), sky=skyc, emit=1.0 if mood in ('sunday', 'empty') else 0.6)
    # counter along the back, stools in front
    sc.add(box((0, 1.6, -4.6), (12, 3.2, 1.6), '#d84a4a', rl=1), box((0, 3.3, -4.6), (12.6, 0.2, 2.0), '#f0f0f0', rl=1),
           box((0, 1.6, -3.78), (12, 0.3, 0.05), '#ffffff'))
    for x in np.arange(-5, 5.1, 2.5):
        sc.add(box((x, 2.1, -2.9), (1.2, 0.3, 1.2), '#d84a4a', rl=3), box((x, 1.0, -2.9), (0.2, 2.0, 0.2), '#c0c0c8'))
    # back shelf, toaster, coffee, pie case
    sc.add(box((0, 5.6, -7.6), (12, 0.2, 0.8), '#8a5a3a'))
    for k, x in enumerate(np.arange(-5, 5.1, 1.2)):
        sc.add(box((x, 6.0, -7.6), (0.5, 0.7, 0.5), ['#ff8a8a', '#ffd24a', '#8ad0ff', '#ffffff'][k % 4], rl=2))
    sc.add(box((-3.2, 3.75, -4.8), (1.2, 0.7, 0.8), '#c8c8d0', rl=2), box((-3.2, 4.12, -4.8), (0.9, 0.05, 0.15), '#333'))   # toaster
    sc.add(box((2.8, 3.9, -4.8), (1.6, 1.0, 1.0), '#cfe8f0', rl=1, emit=0.1), box((2.8, 3.7, -4.8), (1.0, 0.25, 0.6), '#e8c06a', rl=3))  # pie case
    sg = box((0, 6.9, -7.85), (7, 1.5, 0.1), '#200', nocast=True); sg.tex['pz'] = (neon_img(sign_text, (255, 120, 60)), True); sc.add(sg)
    # booths on the sides
    for x in (-7.8, 7.8):
        for z in (-0.5, 4.0):
            sc.add(box((x, 1.6, z), (2.2, 0.15, 2.0), '#f4f4f4', rl=1), box((x, 0.8, z), (0.3, 1.6, 0.3), '#999'))
            for dz in (-1.5, 1.5):
                sc.add(box((x, 0.9, z + dz), (2.4, 0.9, 0.9), '#d84a4a', rl=2), box((x, 2.0, z + dz + (0.35 if dz > 0 else -0.35)), (2.4, 2.2, 0.35), '#d84a4a', rl=2))
    # pendant lamps
    on = lights > 0.5 and mood not in ('dark', 'candle')
    for x in (-4, 0, 4):
        sc.add(box((x, 7.4, -2.5), (0.05, 1.2, 0.05), '#333'), box((x, 6.7, -2.5), (1.0, 0.5, 1.0), '#2aa8a0', rl=2),
               box((x, 6.42, -2.5), (0.6, 0.1, 0.6), '#fff4d0', emit=1.5 if on else 0, shade=not on))
        if on: sc.lights.append(dict(pos=(x, 6.0, -2.3), col='#ffd8a0', I=0.45 * lights if mood != 'final' else 0.55, r=7))
    if mood == 'sunday': sc.lights.append(dict(pos=(0, 5, 5), col='#ffc880', I=0.35, r=12))
    if mood in ('night', 'final') and on: sc.lights.append(dict(pos=(0, 5, 1), col='#ffb878', I=0.5, r=10))

def bills(sc, pos, n=14):
    rr = random.Random(2)
    for k in range(n):
        p = (pos[0] + rr.uniform(-0.8, 0.8), pos[1] + k * 0.012, pos[2] + rr.uniform(-0.5, 0.5))
        b = box(p, (0.75, 0.01, 0.95), '#f4f4ee', R=rot(rr.uniform(-40, 40)), nocast=True)
        sc.add(b)
        if k % 3 == 0: sc.add(box((p[0], p[1] + 0.008, p[2] + 0.2), (0.4, 0.008, 0.1), '#d82a2a', R=rot(rr.uniform(-40, 40)), nocast=True))

# ---------------- street: diner vs hero cafe ----------------
def hero_cafe_img():
    k = 'herocafe'
    if k in _tx: return _tx[k]
    _tx[k] = neon_img('HERO CAFE', (80, 200, 255)); return _tx[k]

def toast_kid_sign():
    k = 'tksign'
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (1400, 360), (40, 16, 10, 255)); d = ImageDraw.Draw(im)
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    f1 = ImageFont.truetype(FONT_ANTON, 90); f2 = ImageFont.truetype(FONT_ANTON, 170)
    for dd in (gd, d):
        pass
    gd.text((700, 95), 'HOME OF THE', font=f1, fill=(255, 190, 60, 255), anchor='mm', stroke_width=14, stroke_fill=(255, 160, 40, 255))
    gd.text((700, 240), 'TOAST KID', font=f2, fill=(255, 190, 60, 255), anchor='mm', stroke_width=16, stroke_fill=(255, 160, 40, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(20)); im = Image.alpha_composite(im, glow); d = ImageDraw.Draw(im)
    d.text((700, 95), 'HOME OF THE', font=f1, fill=(255, 250, 230), anchor='mm', stroke_width=4, stroke_fill=(255, 150, 40))
    d.text((700, 240), 'TOAST KID', font=f2, fill=(255, 250, 230), anchor='mm', stroke_width=5, stroke_fill=(255, 150, 40))
    _tx[k] = im; return im

def city_street(sc, t, tod='day', diner_lit=True, cafe_lit=True, city_lights=True, new_sign=False, snow_on=False, line=None, cafe_crowd=False):
    """diner on the left (x<0), Hero Cafe across the street on the right; street runs along z"""
    if tod == 'day':
        sc.sky = (C('#5aa0ff'), C('#dff0ff')); sc.ambient = C((0.55, 0.53, 0.52)); sc.suncol = C((0.5, 0.45, 0.38))
        sc.fog = C((0.85, 0.9, 1.0)); sc.fogd = 0.006
    elif tod == 'grey':
        sc.sky = (C('#8a94a4'), C('#c8ccd4')); sc.ambient = C((0.52, 0.53, 0.56)); sc.suncol = C((0.2, 0.2, 0.22))
        sc.fog = C((0.75, 0.78, 0.82)); sc.fogd = 0.01
    elif tod == 'dawn':
        sc.sky = (C('#6a8ad8'), C('#ffc89a')); sc.ambient = C((0.58, 0.54, 0.54)); sc.suncol = C((0.6, 0.45, 0.32))
        sc.fog = C((1.0, 0.85, 0.75)); sc.fogd = 0.006
    else:  # night / blackout
        sc.sky = (C('#0a1020'), C('#1e2a48')); sc.ambient = C((0.26, 0.3, 0.42)); sc.suncol = C((0.14, 0.16, 0.24))
        sc.fog = C((0.12, 0.15, 0.24)); sc.fogd = 0.02 if snow_on else 0.012
        sc.stars = 0.3 if not snow_on else 0.0
    sc.sun = np.array([0.5, -0.7, -0.4])
    snowy = snow_on or tod == 'night_snow'
    gcol = '#e8eef8' if snowy else '#5a5a62'
    sc.add(box((0, -0.5, 0), (200, 1, 200), '#e8eef8' if snowy else '#7a7a80', bg=True, mat='concrete'))
    sc.add(box((0, -0.45, 0), (10, 1, 200), '#f0f4fa' if snowy else '#3a3a42', bg=True, mat='asphalt' if not snowy else 'concrete'))
    if not snowy:
        for z in np.arange(-60, 60, 5):
            sc.add(box((0, 0.06, z), (0.2, 0.02, 2.4), '#f0d040', nocast=True))
    for sx in (-1, 1):
        sc.add(box((sx * 5.6, 0.12, 0), (1.2, 0.25, 200), '#b0b0b8' if not snowy else '#ffffff'))
    # ---- diner (left) ----
    dx = -11
    sc.add(box((dx, 4.5, -2), (10, 9, 12), '#f0e0c0', mat='wall'), box((dx, 9.2, -2), (10.6, 0.5, 12.6), '#2aa8a0'))
    lit_c = '#ffcf80' if diner_lit else '#1a2030'
    for z in (-6, 2):
        sc.add(box((dx + 5.02, 3.8, z), (0.1, 3.0, 3.6), lit_c, emit=1.2 if diner_lit else 0.05, shade=False))
    sc.add(box((dx + 5.02, 2.8, -2), (0.12, 5.2, 2.6), '#d84a4a'), box((dx + 5.08, 3.6, -2), (0.06, 2.4, 1.6), lit_c, emit=1.0 if diner_lit else 0.0, shade=False))
    # awning
    for k in range(8):
        sc.add(box((dx + 5.8, 6.2, -7.25 + k * 1.5 + 0.75), (1.6, 0.15, 1.5), '#d84a4a' if k % 2 == 0 else '#ffffff', R=rot(0, 0, -20)))
    sg = box((dx + 5.2, 7.7, -2), (0.12, 1.6, 7.0), '#300', nocast=True)
    img = toast_kid_sign() if new_sign else neon_img("GRANDMA'S", (255, 120, 60))
    sg.tex['px'] = (img, diner_lit); sc.add(sg)
    if diner_lit: sc.lights.append(dict(pos=(dx + 7, 4, -2), col='#ffb060', I=1.6 if tod != 'day' else 0.8, r=9))
    # ---- hero cafe (right) ----
    cx = 12
    sc.add(box((cx, 7, -2), (12, 14, 14), '#e8f0ff', mat='wall'), box((cx - 6.02, 3.6, -2), (0.1, 5.6, 12), '#8ad8ff' if cafe_lit else '#1a2030', emit=0.8 if cafe_lit else 0.02, shade=False))
    for z in np.arange(-8, 4.1, 3):
        sc.add(box((cx - 6.1, 3.6, z), (0.15, 5.8, 0.2), '#c0c8d8'))
    cs = box((cx - 6.2, 10.4, -2), (0.12, 2.6, 10), '#012', nocast=True); cs.tex['nx'] = (hero_cafe_img(), cafe_lit); sc.add(cs)
    sc.add(box((cx - 6.3, 12.6, -2), (0.4, 1.4, 1.4), '#ffd24a', rl=3, emit=0.6 if cafe_lit else 0))
    if cafe_lit: sc.lights.append(dict(pos=(cx - 8, 4, -2), col='#8ad0ff', I=1.2 if tod != 'day' else 0.6, r=9))
    # ---- skyline ----
    rr = random.Random(12)
    for k in range(26):
        bx = rr.uniform(-40, 40); bz = rr.uniform(-60, -22); bh = rr.uniform(14, 36); bw = rr.uniform(5, 9)
        sc.add(box((bx, bh / 2, bz), (bw, bh, bw), rr.choice(['#5a6478', '#6a7088', '#4a5268', '#7a8098']), bg=True))
        if city_lights:
            for j in range(int(bh // 3)):
                if rr.random() < 0.5:
                    sc.add(box((bx + rr.uniform(-bw / 3, bw / 3), 2 + j * 3, bz + bw / 2 + 0.05), (0.8, 0.9, 0.05), '#ffe7a0', emit=1.4 if tod in ('night', 'night_snow') else 0.4, shade=False, nocast=True, bg=True))
    for z in np.arange(-40, 30, 14):
        for sx in (-1, 1):
            x = sx * 6.6
            sc.add(box((x, 4, z), (0.25, 8, 0.25), '#2a2a30'), box((x - sx * 0.8, 8.0, z), (1.8, 0.2, 0.3), '#2a2a30'))
            lampon = city_lights and tod not in ('day', 'grey', 'dawn')
            sc.add(box((x - sx * 1.5, 7.8, z), (0.7, 0.25, 0.5), '#fff0c0' if lampon else '#555', emit=2 if lampon else 0, shade=not lampon))
            if lampon and abs(z) < 20: sc.lights.append(dict(pos=(x - sx * 1.5, 7, z), col='#ffd890', I=0.7, r=7))
    if snowy:
        for k in range(30):
            sc.add(box((rr.uniform(-8, 8) + (-10 if k % 2 else 10), 0.15, rr.uniform(-30, 20)), (rr.uniform(1, 3), 0.35, rr.uniform(1, 3)), '#ffffff', rl=4))

def power_pole(sc, pos, lean=0.0, wire_down=True):
    R = rot(0, 0, lean)
    sc.add(box((pos[0], pos[1] + 5, pos[2]), (0.4, 10, 0.4), '#5a3a22', R=R), box((pos[0], pos[1] + 9.2, pos[2]), (3.2, 0.3, 0.3), '#5a3a22', R=R))
    if wire_down:
        for k in range(6):
            sc.add(box((pos[0] + 1.4, pos[1] + 8.8 - k * 1.5, pos[2] + 0.4 * k), (0.06, 1.6, 0.06), '#111', R=rot(0, 20 * math.sin(k), 10)))
