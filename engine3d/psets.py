from .gsets import *
from .hsets import _tx

TY = dict(design='hoodie', skin='#f0c8a0', arms='#2a5ad8', shirt='#2a5ad8', pants='#2a2a3a', cuff='#f0c8a0', hair='short', haircol='#c8862a', shoes='#ff4a4a')
RAY = dict(design='collar', skin='#d8a070', arms='#b8342a', shirt='#b8342a', pants='#3a3a52', cuff='#d8a070', hair='bald_beard', haircol='#3a2414', shoes='#3a2a1a')
DADP = dict(design='collar', skin='#f0c8a0', arms='#3a5a8a', shirt='#3a5a8a', pants='#4a4a54', cuff='#f0c8a0', hair='short', haircol='#8a5a2a', shoes='#222')
MOMP = dict(design='tee', skin='#f0c8a0', arms='#8a3a6a', shirt='#8a3a6a', pants='#2a2a3a', cuff='#f0c8a0', hair='long', haircol='#8a5a2a', skirt='#8a3a6a', shoes='#222')
COUSIN = dict(design='hoodie', skin='#c98a5a', arms='#3ab07a', shirt='#3ab07a', pants='#2a2a3a', cuff='#c98a5a', hair='curly', haircol='#1a1410', shoes='#fff')

def flannel_extra(out, base, hm, arms):
    for y in (2.6, 3.2, 3.8):
        out.append(box((0, y, 0.52), (2.02, 0.08, 0.04), '#2a1a1a', parent=base))
    for x in (-0.5, 0.5):
        out.append(box((x, 3.0, 0.52), (0.08, 2.0, 0.04), '#2a1a1a', parent=base))

def apron_mom(out, base, hm, arms):
    out.append(box((0, 2.5, 0.53), (1.5, 2.0, 0.05), '#f4e8d8', parent=base, rl=1))

def pickle_label():
    k = 'pickle_lbl'
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (400, 300), (240, 230, 190, 255)); d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 391, 291), outline=(40, 110, 40), width=10)
    d.text((200, 120), 'PICKLES', font=ImageFont.truetype(FONT_ANTON, 96), fill=(40, 110, 40), anchor='mm')
    d.text((200, 225), 'EXTRA TIGHT LID', font=ImageFont.truetype(FONT_ANTON, 36), fill=(160, 40, 30), anchor='mm')
    _tx[k] = im; return im

def cran_label():
    k = 'cran_lbl'
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (400, 400), (170, 20, 40, 255)); d = ImageDraw.Draw(im)
    d.text((200, 150), 'CRANBERRY', font=ImageFont.truetype(FONT_ANTON, 74), fill=(255, 240, 220), anchor='mm')
    d.text((200, 250), 'SAUCE', font=ImageFont.truetype(FONT_ANTON, 90), fill=(255, 240, 220), anchor='mm')
    _tx[k] = im; return im

def jar(sc, pos, R=None, s=1.0, lid_open=0.0, lid_fly=None, shake=0.0, t=0.0, glow=0.0):
    j = shake * 0.05 * math.sin(t * 70)
    base = M4((pos[0] + j, pos[1], pos[2]), R if R is not None else np.eye(3))
    S = np.eye(4); S[:3, :3] *= s; base = base @ S
    out = [box((0, 0.6, 0), (0.95, 1.2, 0.95), '#9ad89a', parent=base, rl=2, emit=0.12 + glow),
           box((0, 0.5, 0), (0.7, 0.9, 0.7), '#3a8a2a', parent=base, rl=3)]
    for k in range(4):
        out.append(box((-0.2 + 0.14 * k, 0.6, 0.36), (0.12, 0.7, 0.12), '#2a6a1a', parent=base, rl=4))
    lb = box((0, 0.55, 0.48), (0.8, 0.55, 0.02), '#ffffff', parent=base, nocast=True); lb.tex['pz'] = (pickle_label(), False); out.append(lb)
    if lid_fly is None:
        out.append(box((0, 1.25 + 0.4 * lid_open, 0), (1.0, 0.18, 1.0), '#d8b030', parent=base, rl=2, R=rot(lid_open * 90)))
    sc.add(out)
    if lid_fly is not None:
        d = lid_fly
        sc.add(box((pos[0] + 1.2 * d, pos[1] + 1.3 * s + 6 * d - 6 * d * d, pos[2] + 0.6 * d), (1.0 * s, 0.18 * s, 1.0 * s), '#d8b030', rl=2, R=rot(d * 900, d * 500, 0)))

def held_jar(side='both', t=0.0, shake=0.0):
    def ex(out, base, hm, arms):
        j = shake * 0.05 * math.sin(t * 70)
        am = arms['la'] @ M4((-0.75 + j, -1.15, 0.2))
        out.append(box((0, 0.1, 0), (0.95, 1.2, 0.95), '#9ad89a', parent=am, rl=2, emit=0.15))
        out.append(box((0, 0.0, 0), (0.7, 0.9, 0.7), '#3a8a2a', parent=am, rl=3))
        out.append(box((0, 0.75, 0), (1.0, 0.18, 1.0), '#d8b030', parent=am, rl=2))
    return ex

def pickle_held(bite=0.0):
    def ex(out, base, hm, arms):
        out.append(box((0, -1.3, 0.4), (0.3, 0.3, 0.9 * (1 - 0.35 * bite)), '#4a9a2a', parent=arms['ra'], rl=4))
    return ex

def phone_up(out, base, hm, arms):
    pm = arms['ra'] @ M4((0, -1.0, 0.3), rot(0, 90, 0))
    out.append(box((0, 0, 0), (0.55, 0.13, 0.95), '#111114', parent=pm, rl=1))
    out.append(box((0, -0.08, 0), (0.45, 0.02, 0.8), '#bfe6ff', parent=pm, emit=1.4, shade=False))
    out.append(box((0.15, 0.08, 0.35), (0.12, 0.05, 0.12), '#ff2a2a', parent=pm, emit=2.0))

def toolbox_held(out, base, hm, arms):
    out.append(box((0, -1.5, 0.2), (1.2, 0.6, 0.5), '#c42a2a', parent=arms['ra'], rl=1))
    out.append(box((0, -1.1, 0.2), (0.6, 0.12, 0.12), '#222', parent=arms['ra']))

def turkey_leg(out, base, hm, arms):
    out.append(box((0, -1.35, 0.35), (0.45, 0.45, 0.6), '#a8641e', parent=arms['ra'], rl=4))
    out.append(box((0, -1.35, -0.05), (0.14, 0.14, 0.5), '#f4ecd8', parent=arms['ra'], rl=2))

def dog(sc, pos, yaw=0.0, t=0.0, shake=0.0, hide=False):
    j = shake * 0.05 * math.sin(t * 60)
    base = M4((pos[0] + j, pos[1], pos[2]), rot(yaw))
    tan = '#c8964a'
    out = [box((0, 1.0 - 0.3 * hide, 0), (0.9, 0.8, 1.8), tan, parent=base, rl=2),
           box((0, 1.5 - 0.4 * hide, 1.05), (0.75, 0.7, 0.75), tan, parent=base, rl=2),
           box((0, 1.38 - 0.4 * hide, 1.5), (0.4, 0.3, 0.3), '#e8c890', parent=base, rl=2),
           box((0, 1.48 - 0.4 * hide, 1.67), (0.14, 0.12, 0.06), '#111', parent=base, rl=2)]
    for sx in (-0.3, 0.3):
        out.append(box((sx, 1.95 - 0.4 * hide - 0.25 * hide, 0.95), (0.18, 0.4, 0.25), '#8a5a2a', parent=base, rl=2, R=rot(0, 0, sx * 60 * hide)))
        out.append(box((sx * 0.6, 1.62 - 0.4 * hide, 1.43), (0.12, 0.14, 0.04), '#111', parent=base))
        out.append(box((sx * 0.6 + 0.02, 1.64 - 0.4 * hide, 1.45), (0.05, 0.05, 0.02), '#fff', parent=base, emit=0.5))
    for sx in (-0.3, 0.3):
        for sz in (-0.6, 0.6):
            out.append(box((sx, 0.35, sz), (0.25, 0.7 - 0.3 * hide, 0.25), tan, parent=base, rl=1))
    out.append(box((0, 1.3 - 0.3 * hide, -1.0), (0.15, 0.15, 0.6), tan, parent=base, rl=2, R=rot(0, 30 - 60 * hide, 0)))
    sc.add(out)

def chair(sc, pos, yaw=0.0, col='#7a4a2a'):
    base = M4(pos, rot(yaw))
    sc.add([box((0, 1.6, 0), (1.6, 0.2, 1.6), col, parent=base, mat='wood'), box((0, 3.0, -0.75), (1.6, 2.6, 0.2), col, parent=base, mat='wood')] +
           [box((sx, 0.8, sz), (0.18, 1.6, 0.18), col, parent=base) for sx in (-0.65, 0.65) for sz in (-0.65, 0.65)])

def lawn_chair(sc, pos, yaw=0.0, col='#2a8ad8'):
    base = M4(pos, rot(yaw))
    sc.add([box((0, 1.1, 0), (1.7, 0.15, 1.5), col, parent=base), box((0, 2.0, -0.8), (1.7, 1.8, 0.12), col, parent=base, R=rot(0, -15, 0))] +
           [box((sx, 0.55, sz), (0.08, 1.1, 0.08), '#c0c0c8', parent=base) for sx in (-0.8, 0.8) for sz in (-0.7, 0.7)])

# ---------------- dining room ----------------
SEATS = [(-4.6, 'gm'), (-2.3, 'dad'), (0.0, 'ray'), (2.3, 'mom'), (4.6, 'cousin')]
def dining(sc, t, mood='warm', light=1.0):
    sc.sky = (C('#ffb070'), C('#ffe0b0')); sc.suncol = C((0.4, 0.3, 0.2)); sc.sun = np.array([0.5, -0.6, -0.6])
    sc.ambient = C((0.36, 0.32, 0.29)) if mood == 'warm' else C((0.26, 0.26, 0.32))
    room(sc, 22, 18, 9, '#b88a5a', '#6a4a2a', floor_tile=1.0, floor_j=0.06, ceil='#e8dcc8')
    sc.add(box((0, 2.0, -8.9), (22, 4.0, 0.1), '#8a4a2a', nocast=True, mat='wood'))
    window(sc, (-6, 5.2, -8.95), 4, 3, sky='#ffb070', emit=1.0); window(sc, (6, 5.2, -8.95), 4, 3, sky='#ffb070', emit=1.0)
    bn = box((0, 7.4, -8.85), (9, 1.4, 0.06), '#fff', nocast=True)
    bn.tex['pz'] = (sign_img('HAPPY THANKSGIVING', (150, 60, 20), (255, 220, 120), size=(1300, 200), fs=130), True); sc.add(bn)
    rr = random.Random(4)
    for k in range(16):
        x = -10 + k * 1.33
        sc.add(box((x, 8.3 - 0.4 * abs(math.sin(k)), -8.8), (0.6, 0.6, 0.06), rr.choice(['#d8742a', '#c43a1a', '#e8b020', '#8a3a1a']), R=rot(0, 0, 45), nocast=True))
    # table + feast
    sc.add(box((0, 2.3, -1.0), (12, 0.25, 3.6), '#f4ecd8', rl=1), box((0, 1.15, -1.0), (11.4, 2.3, 3.2), '#7a4a2a', mat='wood'))
    sc.add(box((0, 2.95, -1.0), (2.4, 1.1, 1.8), '#b06a24', rl=4), box((0, 3.55, -1.0), (1.8, 0.5, 1.4), '#c07a34', rl=4),
           box((1.15, 2.9, -0.4), (0.5, 0.5, 0.9), '#a05a1a', rl=4), box((-1.15, 2.9, -0.4), (0.5, 0.5, 0.9), '#a05a1a', rl=4),
           box((0, 2.48, -1.0), (3.0, 0.1, 2.4), '#ffffff', rl=4))
    for (x, c) in ((-3.2, '#f4e8a0'), (3.2, '#c42a3a'), (-5.0, '#7aa83a'), (5.0, '#e8a83a')):
        sc.add(box((x, 2.6, -1.2), (1.0, 0.4, 1.0), '#ffffff', rl=4), box((x, 2.82, -1.2), (0.8, 0.2, 0.8), c, rl=4))
    for x in (-1.8, 1.8):
        candle(sc, (x, 2.43, -0.2), t, s=0.8)
    for x, _ in SEATS:
        chair(sc, (x, 0, -3.4))
        sc.add(box((x, 2.46, -2.2), (0.9, 0.05, 0.9), '#ffffff', rl=4))
    sc.lights.append(dict(pos=(0, 7.5, -1), col='#ffd8a0', I=0.35 * light, r=12))
    sc.add(box((0, 8.6, -1), (2.4, 0.4, 1.2), '#c8a050', rl=2), box((0, 8.3, -1), (2.0, 0.15, 0.9), '#fff4d0', emit=1.4 * light, shade=False))

def family(sc, t, faces=None, ray_leg=True, cousin_film=False, stand=False):
    f = faces or {}
    for x, who in SEATS:
        pz = dict(sit=True, ll=90, rl=90, y=0.45, ra=40, la=40, re=50, le=50)
        o = dict(gm=GRANDMA, dad=DADP, ray=RAY, mom=MOMP, cousin=COUSIN)[who]
        ex = dict(gm=grandma_extra, dad=None, ray=flannel_extra, mom=apron_mom, cousin=None)[who]
        if who == 'ray' and ray_leg:
            pz.update(ra=70, re=80); ex = combine(flannel_extra, turkey_leg)
        if who == 'cousin' and cousin_film:
            pz.update(ra=100, re=60); ex = phone_up
        character(sc, (x, -0.15, -3.3), yaw=0, pose=pz, face=f.get(who, f.get('all', 'smile')), blob=False, scale=1.0 if who != 'ray' else 1.12, extra=ex, **o)

# ---------------- kitchen ----------------
def kitchen(sc, t, steam=0.0):
    sc.sky = (C('#ffb070'), C('#ffe0b0')); sc.suncol = C((0.35, 0.28, 0.2)); sc.ambient = C((0.46, 0.44, 0.42))
    room(sc, 18, 14, 8.5, '#d8e8e0', '#e8e4dc', floor_tile=1.0, floor_j=0.04, ceil='#f4f4f4', floor_mat='checker')
    sc.add(box((0, 1.6, -5.8), (16, 3.2, 2.2), '#f4f4f4', rl=1), box((0, 3.3, -5.6), (16.4, 0.2, 2.6), '#3a3a42', rl=1))
    for x in np.arange(-7, 7.1, 2.0):
        sc.add(box((x, 1.6, -4.68), (1.8, 2.8, 0.05), '#e8e8e8'), box((x + 0.6, 2.4, -4.62), (0.1, 0.5, 0.08), '#888'))
    sc.add(box((0, 6.0, -6.6), (16, 2.6, 0.8), '#f4f4f4', rl=1))
    window(sc, (0, 5.4, -6.95), 4, 2.4, sky='#ffd8a0', emit=1.0)
    # island with sink + faucet (Tyler stands behind it facing the camera)
    sc.add(box((0, 1.6, -1.8), (6, 3.2, 2.2), '#3a5a8a', rl=1), box((0, 3.3, -1.8), (6.4, 0.2, 2.6), '#e8e4dc', rl=1))
    sx = 1.7
    sc.add(box((sx, 3.36, -1.8), (2.0, 0.06, 1.4), '#a8b0b8'), box((sx + 0.6, 4.2, -2.7), (0.2, 1.6, 0.2), '#c8c8d0', rl=1), box((sx + 0.6, 4.9, -2.3), (0.2, 0.2, 0.9), '#c8c8d0', rl=1))
    if steam > 0:
        sc.add(box((sx + 0.6, 4.1, -1.9), (0.18, 1.4, 0.18), '#bfe6ff', emit=0.6))
        rr = random.Random(int(t * 6))
        for j in range(9):
            ph = (t * 0.8 + j / 9) % 1
            sc.add(box((sx + 0.8 + rr.uniform(0, 1.0), 3.6 + ph * 3.0, -1.8 + rr.uniform(-0.5, 0.5)), (0.25 + 0.5 * ph,) * 3, '#ffffff', emit=0.3, shade=False, nocast=True, rl=4))
    sc.lights.append(dict(pos=(0, 7, -2), col='#fff4e0', I=0.5, r=12))

# ---------------- outside ----------------
def street_day(sc, t):
    house(sc, t, night_=False)
    sc.sky = (C('#7ab0ff'), C('#ffe0c0')); sc.ambient = C((0.56, 0.52, 0.5)); sc.suncol = C((0.55, 0.45, 0.35))
    sc.fog = C((0.95, 0.85, 0.75)); sc.fogd = 0.006
    sc.add(box((6.5, -0.42, 11), (7, 1, 12), '#4a4a50', bg=True, mat='asphalt'))
    rr = random.Random(8)
    for k in range(60):
        sc.add(box((rr.uniform(-20, 20), 0.04, rr.uniform(-4, 22)), (0.4, 0.04, 0.4), rr.choice(['#d8742a', '#c43a1a', '#e8b020']), R=rot(rr.uniform(0, 90)), nocast=True))
    for tx in (-14, 14):
        sc.add(box((tx, 5.2, -1), (4.4, 3.2, 4.4), '#d8742a'))

CAR = (6.5, 0, 9.0)
def family_car(sc, t, door_off=0.0, door_open=0.0):
    x, y, z = CAR
    sc.add(box((x, 1.6, z), (4.2, 1.8, 8.0), '#3a7ad8', rl=1), box((x, 3.1, z - 0.6), (3.8, 1.4, 4.4), '#3a7ad8', rl=1),
           box((x, 3.15, z - 0.6), (3.9, 1.0, 3.8), '#9ad0ff', emit=0.2))
    for sz in (-2.6, 2.6):
        for sx in (-2.1, 2.1):
            sc.add(box((x + sx, 0.8, z + sz), (0.6, 1.6, 1.6), '#1a1a1a', rl=4))
    # driver door on the -x side
    if door_off <= 0:
        hm = M4((x - 2.12, 0, z + 0.8), rot(-70 * door_open))
        sc.add(box((0, 2.2, -1.1), (0.15, 2.6, 2.2), '#3a7ad8', parent=hm, rl=1), box((-0.02, 3.0, -1.1), (0.16, 0.9, 1.8), '#9ad0ff', parent=hm, emit=0.2))
    else:
        d = min(1.0, door_off)
        hm = M4((x - 2.6 - 0.8 * d, 0.2 + 1.8 * (1 - d) ** 2, z - 0.3), rot(20 * d, 0, -85 * d))
        sc.add(box((0, 1.3, 0), (0.15, 2.6, 2.2), '#3a7ad8', parent=hm, rl=1), box((-0.02, 2.1, 0), (0.16, 0.9, 1.8), '#9ad0ff', parent=hm, emit=0.2))

NEIGH = [(-3.4, 20.0), (-1.0, 20.6), (1.4, 20.0), (3.8, 20.8)]
def neighbors(sc, t, cheer=False, faces=None):
    outs = [KIDS[0], JALEN, DAD, MOM_OLD]
    for k, (x, z) in enumerate(NEIGH):
        lawn_chair(sc, (x, 0, z), yaw=180, col=['#2a8ad8', '#e83a3a', '#3ab07a', '#ffb020'][k])
        if cheer:
            pz = dict(ra=150 - 20 * abs(math.sin(t * 9 + k)), la=150 - 20 * abs(math.sin(t * 9 + k + 1)), re=10, le=10)
            character(sc, (x, 0.3 * abs(math.sin(t * 9 + k)), z), yaw=180, pose=pz, face='roar', **outs[k])
        else:
            pz = dict(sit=True, ll=90, rl=90, y=0.45, ra=60, la=40, re=100 if k % 2 == 0 else 40, le=40)
            character(sc, (x, -0.6, z), yaw=180, pose=pz, face=(faces or ['snicker', 'smirk', 'holdlaugh', 'smirk'])[k], blob=False, **outs[k])
            if k % 2 == 0:
                sc.add(box((x + 0.6, 2.4, z - 1.0), (0.5, 0.6, 0.5), '#e82a2a', rl=1), box((x + 0.6, 2.75, z - 1.0), (0.45, 0.2, 0.45), '#fff8d0', rl=4))
