from .engine import *

NARR = dict(design='hoodie', skin='#a8714a', shirt='#161618', pants='#111113', cuff='#a8714a', hair='beanie', haircol='#141416', shoes='#0c0c0e', chain=True, grill=True, slit=True)
FUTURE = dict(design='torn', skin='#946042', shirt='#1c1c1e', pants='#111113', cuff='#946042', hair='beanie_beard', haircol='#141416', shoes='#0c0c0e', chain=True, grill=True, slit=True)
MOM = dict(design='collar', skin='#e2b48c', shirt='#f2f2f2', pants='#e2b48c', cuff='#e2b48c', hair='long', haircol='#4a2c1a', skirt='#3d5a8a', shoes='#f0f0f0')
MOM_OLD = dict(design='tee', skin='#e2b48c', shirt='#c94f6a', pants='#e2b48c', cuff='#e2b48c', hair='long', haircol='#4a2c1a', skirt='#3d3d4a')
JALEN = dict(design='tee_logo', skin='#7a4a2c', shirt='#3fbf4a', pants='#2a2a40', cuff='#3fbf4a', hair='curly', haircol='#141414')
DAD = dict(design='tee', skin='#b88a68', shirt='#5a6070', pants='#3a3a48', cuff='#b88a68', hair='bald_beard', haircol='#2a1a10')
KIDS = [dict(skin='#f1c9a0', shirt='#e84a4a', pants='#2a2a40', cuff='#f1c9a0', hair='short', haircol='#5a3a1a'),
        dict(skin='#5a3a24', shirt='#f4f4f4', pants='#3a5a9a', cuff='#5a3a24', hair='bandana', haircol='#c42020', chain='silver', design='tee', shoes='#f0f0f0'),
        dict(skin='#ffd9b8', shirt='#4a8ae8', pants='#ffd9b8', cuff='#ffd9b8', hair='long', haircol='#e6c25a', skirt='#2a3a7a', shoes='#f0f0f0'),
        dict(skin='#c48a5c', shirt='#c42a2a', pants='#8a8a92', cuff='#c48a5c', hair='cap_back', haircol='#c42a2a', design='hoodie', shoes='#f0f0f0', chain='silver'),
        dict(skin='#8a5a3a', shirt='#ff8ad0', pants='#8a5a3a', cuff='#8a5a3a', hair='long', haircol='#1a1a1a', skirt='#1c1c22', shoes='#1c1c22'),
        dict(skin='#f0c090', shirt='#2f8a4a', pants='#3a5a9a', cuff='#f0c090', hair='cap_back', haircol='#222', design='flannel', shoes='#c8a060'),
        dict(skin='#7a4a2c', shirt='#6a2fb0', pants='#6a2fb0', cuff='#7a4a2c', hair='durag', haircol='#1c1c1c', design='jersey', arms='#7a4a2c', shoes='#f0f0f0', chain='silver'),
        dict(skin='#6a4228', shirt='#ff9a3a', pants='#2a3a60', cuff='#6a4228', hair='short', haircol='#111')]

PHONE_PRESS = (0, 0, 0)

def poster(sc, pos, R, w, h, kind, seed=0):
    b = box(pos, (w, h, 0.05), '#ffffff', R=R, nocast=True); b.tex['pz'] = (poster_img(kind, seed), False); sc.add(b)

_pc = {}
def poster_img(kind, seed=0):
    if (kind, seed) in _pc: return _pc[(kind, seed)]
    im = Image.new('RGBA', (360, 500), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    rr = random.Random(seed)
    pal = [((40, 30, 90), (255, 90, 160)), ((10, 60, 90), (90, 230, 255)), ((90, 30, 20), (255, 200, 60)), ((20, 70, 40), (140, 255, 120))][seed % 4]
    for y in range(500): d.line((0, y, 360, y), fill=tuple(int(a + (b - a) * y / 500 * 0.6) for a, b in zip(pal[0], pal[1])))
    f = ImageFont.truetype(FONT_ANTON, 70)
    for k in range(5):
        x = rr.randint(20, 300); y = rr.randint(150, 420); r = rr.randint(15, 50)
        d.ellipse((x - r, y - r, x + r, y + r), fill=pal[1])
    d.text((25, 30), kind, font=f, fill=(255, 255, 255))
    d.rectangle((0, 0, 359, 499), outline=(240, 240, 240), width=10)
    _pc[(kind, seed)] = im
    return im

def plant(sc, pos, s=1.0):
    sc.add(box((pos[0], pos[1] + 0.5 * s, pos[2]), (1.0 * s, 1.0 * s, 1.0 * s), '#b0603a', rl=1),
           box((pos[0], pos[1] + 1.25 * s, pos[2]), (0.15, 0.6 * s, 0.15), '#3a6a2a'),
           box((pos[0], pos[1] + 1.8 * s, pos[2]), (1.3 * s, 0.9 * s, 1.3 * s), '#3f8f3a', rl=3),
           box((pos[0] + 0.3 * s, pos[1] + 2.3 * s, pos[2] - 0.2 * s), (0.9 * s, 0.7 * s, 0.9 * s), '#4aa043', rl=3))

def ceiling_lamp(sc, pos, on=False, col='#fff2d0'):
    sc.add(box((pos[0], pos[1] - 0.15, pos[2]), (0.15, 0.3, 0.15), '#555'),
           box((pos[0], pos[1] - 0.5, pos[2]), (1.6, 0.4, 1.6), col if on else '#e8e8e8', rl=3, emit=1.5 if on else 0.15, shade=not on, nocast=True))

def night(sc, amb=(0.44, 0.47, 0.72), sun=(0.26, 0.29, 0.52)):
    sc.sky = (C('#0a1236'), C('#2b3c80')); sc.ambient = C(amb); sc.suncol = C(sun); sc.stars = 1.0
    sc.sun = np.array([0.5, -1.0, -0.3])

def day(sc):
    sc.sky = (C('#5fa8ff'), C('#dff2ff')); sc.ambient = C((0.62, 0.62, 0.66)); sc.suncol = C((0.55, 0.52, 0.44))
    sc.sun = np.array([-0.4, -1.0, -0.5])

_banner = None
def banner_img():
    global _banner
    if _banner is None:
        im = Image.new('RGBA', (1400, 260), (14, 12, 18, 255)); d = ImageDraw.Draw(im)
        rr = random.Random(9)
        for _ in range(120):
            x, y = rr.randint(0, 1400), rr.randint(0, 260); r = rr.randint(2, 5)
            d.ellipse((x - r, y - r, x + r, y + r), fill=rr.choice([(255, 214, 90), (200, 120, 255), (255, 255, 255)]))
        f = ImageFont.truetype(FONT_ANTON, 170)
        d.text((700, 130), 'HAPPY 17TH BIRTHDAY', font=f, fill=(255, 205, 70), anchor='mm', stroke_width=6, stroke_fill=(120, 70, 10))
        d.rectangle((0, 0, 1399, 259), outline=(255, 205, 70), width=12)
        _banner = im
    return _banner

def birthday_decor(sc, t):
    # two-tier cake on the nightstand
    cx, cz, top = 0.05, -6.7, 2.2
    sc.add(box((cx, top + 0.3, cz), (1.05, 0.6, 1.05), '#fff4f8', rl=1),
           box((cx, top + 0.58, cz), (1.09, 0.1, 1.09), '#ff6fae', rl=2),
           box((cx, top + 0.83, cz), (0.72, 0.45, 0.72), '#ff8ac0', rl=1),
           box((cx, top + 1.06, cz), (0.75, 0.07, 0.75), '#ffffff', rl=2))
    for k, (dx, dz, h) in enumerate(((-0.45, 0.53, 0.22), (-0.1, 0.53, 0.3), (0.3, 0.53, 0.18), (0.53, 0.2, 0.25), (0.53, -0.3, 0.2))):
        sc.add(box((cx + dx, top + 0.5 - h / 2, cz + dz), (0.12, h, 0.06), '#ff6fae', rl=2))
    rr = random.Random(4)
    for _ in range(14):
        sc.add(box((cx + rr.uniform(-0.3, 0.3), top + 1.1, cz + rr.uniform(-0.3, 0.3)), (0.05, 0.03, 0.12), rr.choice(['#ffd24a', '#5ad0ff', '#7aff7a', '#ff5a5a']), R=rot(rr.uniform(0, 180))))
    gold = '#ffd24a'; ct = top + 1.1
    # "1" candle
    sc.add(box((cx - 0.18, ct + 0.22, cz + 0.05), (0.09, 0.44, 0.09), gold, rl=1, emit=0.3))
    # "7" candle
    sc.add(box((cx + 0.17, ct + 0.4, cz + 0.05), (0.28, 0.08, 0.09), gold, rl=1, emit=0.3),
           box((cx + 0.2, ct + 0.19, cz + 0.05), (0.08, 0.42, 0.09), gold, R=rot(0, 0, -22), rl=1, emit=0.3))
    fl = 1 + 0.18 * math.sin(t * 23) + 0.1 * math.sin(t * 37)
    for fx in (cx - 0.18, cx + 0.27):
        wob = 0.015 * math.sin(t * 17 + fx * 9)
        sc.add(box((fx, ct + 0.49, cz + 0.05), (0.02, 0.08, 0.02), '#111', nocast=True),
               box((fx, ct + 0.56, cz + 0.05), (0.11, 0.13 * fl, 0.11), '#ff4a00', emit=2.2, shade=False, rl=4, nocast=True),
               box((fx + wob, ct + 0.64 + 0.02 * fl, cz + 0.05), (0.065, 0.16 * fl, 0.065), '#ffd860', emit=3, shade=False, rl=4, nocast=True),
               box((fx, ct + 0.55, cz + 0.08), (0.04, 0.06, 0.02), '#fffbe0', emit=3, shade=False, rl=4, nocast=True))
    sc.lights.append(dict(pos=(cx, ct + 0.8, cz + 0.4), col='#ffb050', I=1.5 * fl, r=3.0))
    # banner over the bed
    bn = box((3.0, 6.7, -7.92), (7.0, 1.3, 0.06), '#111', nocast=True); bn.tex['pz'] = (banner_img(), False); sc.add(bn)
    # gold "1" "7" foil balloons
    by = 4.6 + 0.12 * math.sin(t * 1.3)
    sc.add(box((5.6, by, -6.0), (0.55, 2.3, 0.35), gold, rl=2, emit=0.25))
    sc.add(box((6.75, by + 0.95, -6.0), (1.3, 0.45, 0.35), gold, rl=2, emit=0.25),
           box((6.95, by - 0.15, -6.0), (0.5, 2.0, 0.35), gold, R=rot(0, 0, -18), rl=2, emit=0.25))
    for bx in (5.6, 6.8):
        sc.add(box((bx, (by - 1.2) / 2, -6.0), (0.03, by - 1.2, 0.03), '#eeeeee', nocast=True))
    # balloon cluster near the ceiling
    cols = ['#111111', '#ffd24a', '#8a3aff', '#ffffff', '#ffd24a', '#111111', '#c03aff', '#ffd24a']
    for k, (x, z) in enumerate(((-3, -2), (-2.2, -2.8), (-3.6, -3.2), (-1.4, -1.6), (-2.8, -0.8), (-4.2, -1.8), (-1.8, -3.9), (-3.4, -4.4))):
        y = 6.6 + 0.4 * ((k * 7) % 3) / 2 + 0.15 * math.sin(t * 1.1 + k)
        sc.add(box((x, y, z), (1.0, 1.2, 1.0), cols[k], rl=4, emit=0.15 if cols[k] == '#ffd24a' else 0))
        sc.add(box((x, y - 0.75, z), (0.12, 0.15, 0.12), cols[k], rl=2))
        sc.add(box((x, y - 2.3, z), (0.03, 3.0, 0.03), '#dddddd', nocast=True))
    # streamers
    for k, (x0, c) in enumerate(((-6.5, '#ffd24a'), (-3.0, '#8a3aff'), (0.5, '#ffd24a'), (6.0, '#c03aff'))):
        for j in range(6):
            sc.add(box((x0 + j * 0.45, 7.9 - 0.45 * math.sin(j / 5 * math.pi), -7.85), (0.5, 0.12, 0.04), c, nocast=True, R=rot(0, 0, 25 * math.cos(j / 5 * math.pi))))
    # presents
    for (x, z, s_, c, rc) in ((-0.6, -2.4, 1.0, '#8a3aff', '#ffd24a'), (-0.4, -1.1, 0.75, '#111111', '#ffd24a'), (-1.6, -1.8, 0.85, '#ffd24a', '#111111')):
        sc.add(box((x, s_ / 2, z), (s_, s_, s_), c, rl=1),
               box((x, s_ / 2, z), (s_ + 0.03, s_ + 0.03, 0.14), rc), box((x, s_ / 2, z), (0.14, s_ + 0.03, s_ + 0.03), rc),
               box((x, s_ + 0.1, z), (0.35, 0.2, 0.2), rc, rl=3))
    for _ in range(45):
        sc.add(box((rr.uniform(-5.5, 0.5), 0.07, rr.uniform(-1, 3.5)), (0.14, 0.02, 0.14), rr.choice(['#ffd24a', '#8a3aff', '#ffffff', '#ff5ab4']), R=rot(rr.uniform(0, 90)), nocast=True))

# ---------------- bedroom ----------------
def bedroom(sc, lamp_on=False, cake=False, candle_t=0.0, clock='3:06', phone_screen=None, lying=True, face='neutral',
            sit_up=0.0, phone_at_ear=False, nface=None, phone_buzz=0.0, glow=0.0, narr_pose=None, toss=0.0):
    night(sc)
    room(sc, 16, 16, 8, '#4f62a3', '#6a4a33', floor_tile=0.9, floor_j=0.1, ceil='#c8c8d8')
    window(sc, (-4.5, 4.6, -7.95), 3.6, 3.0, sky='#16255a', emit=0.9)
    sc.lights.append(dict(pos=(-4.5, 5, -5), col='#5f7fd0', I=0.8, r=7))
    sc.add(box((-4.5, 6.5, -7.6), (5.2, 0.15, 0.2), '#ccc'))
    bed(sc, (3, 0, -4.2), blanket='#2f4f9f')
    nightstand(sc, (-0.5, 0, -6.9))
    bookshelf(sc, (-7.2, 0, -2), yaw=90)
    sc.add(box((6.8, 1.6, 2), (2.2, 0.2, 4), '#6b4429'), box((6.8, 0.8, 0.3), (2, 1.6, 0.2), '#6b4429'), box((6.8, 0.8, 3.7), (2, 1.6, 0.2), '#6b4429'))
    sc.add(box((-3, 0.03, 1), (6, 0.06, 5), '#3a7ad0', bg=True, mat='carpet'))
    for (px, pz, sx, sz) in ((0, -7.9, 16, 0.15), (7.9, 0, 0.15, 16), (-7.9, 0, 0.15, 16)):
        sc.add(box((px, 7.85, pz), (sx, 0.12, sz), '#c04dff', emit=2.2, shade=False, nocast=True))
    sc.lights.append(dict(pos=(0, 7.2, -6.5), col='#a040ff', I=1.1, r=6))
    sc.lights.append(dict(pos=(6.5, 7.2, 1), col='#ff40c0', I=0.9, r=6))
    sc.lights.append(dict(pos=(-6.5, 7.2, 2), col='#6050ff', I=0.9, r=6))
    # gaming chair + desk stuff + clutter
    sc.add(box((4.6, 1.6, 2.2), (1.6, 0.4, 1.6), '#111', rl=1), box((4.0, 3.0, 2.2), (0.35, 2.6, 1.5), '#d02040', rl=1),
           box((4.6, 0.8, 2.2), (0.2, 1.2, 0.2), '#333'), box((4.6, 0.15, 2.2), (1.4, 0.15, 1.4), '#222', rl=1))
    sc.add(box((5.95, 1.83, 2.2), (0.5, 0.06, 1.5), '#ff3cc8', emit=1.2, shade=False, nocast=True))
    sc.add(box((-2.0, 0.15, 3.5), (1.4, 0.3, 1.0), '#c83a3a', rl=2, mat='carpet', R=rot(25)), box((-0.8, 0.12, 4.4), (1.2, 0.24, 0.9), '#3a7ac8', rl=2, mat='carpet', R=rot(-40)))
    sc.add(box((6.9, 0.6, -6.6), (0.9, 1.2, 0.9), '#555', rl=1), box((6.9, 1.25, -6.6), (0.7, 0.2, 0.7), '#ddd', rl=3))
    sc.add(box((-7.6, 6.0, -5.2), (0.6, 0.15, 3.0), '#5e3b23', mat='wood'))
    for k, c in enumerate(('#ffcc33', '#33ccff', '#ff5555')):
        sc.add(box((-7.6, 6.45, -6.3 + k), (0.4, 0.75, 0.4), c, rl=2))
    poster(sc, (7.97, 4.6, -3.5), rot(-90), 2.2, 3.0, 'GAME', 0)
    poster(sc, (7.97, 4.6, 0.0), rot(-90), 2.2, 3.0, 'OBBY', 1)
    poster(sc, (-7.97, 5.0, 4.5), rot(90), 2.0, 2.8, 'LVL 99', 2)
    for cx in (-6.9, -2.1):
        sc.add(box((cx, 4.4, -7.75), (0.9, 4.6, 0.25), '#7a2f3f', rl=1, mat='carpet'))
    plant(sc, (-6.6, 0, -6.6), 1.0)
    ceiling_lamp(sc, (0, 8, -1))
    sc.add(box((6.8, 2.6, 2), (1.0, 1.6, 2.2), '#151518', rl=1), box((6.3, 2.6, 2), (0.05, 1.3, 1.9), '#2a3a6a', emit=0.3, shade=False, nocast=True),
           box((6.8, 1.75, 2), (0.6, 0.12, 0.6), '#222'), box((5.9, 1.75, 2.2), (0.6, 0.06, 1.6), '#2a2a2a', rl=1))
    # clock
    ck = box((-1.0, 2.52, -6.75), (0.9, 0.6, 0.45), '#18181c')
    ck.tex['pz'] = (text_tex([clock], size=(300, 170), bg=(10, 10, 12), fg=(255, 50, 50), font=FONT_ANTON, fs=120), True)
    sc.add(ck)
    sc.lights.append(dict(pos=(-0.9, 2.6, -6.2), col='#ff3030', I=0.35, r=1.5))
    if cake:
        birthday_decor(sc, candle_t)
    if lamp_on: lamp(sc, (-0.2, 2.2, -7.2))
    # phone on pillow
    if not phone_at_ear:
        bz = (math.sin(phone_buzz * 90) * 0.022) if phone_buzz else 0
        ph = box((4.6 + bz, 2.27, -7.0), (0.6, 0.12, 1.05), '#111114', R=rot(15 + bz * 40))
        if phone_screen is not None:
            ph.tex['py'] = (phone_screen, True)
            sc.lights.append(dict(pos=(4.6, 3.0, -7.0), col='#9fd8ff', I=1.4 + glow, r=2.6 + glow))
        sc.add(ph)
    # narrator
    if lying:
        R = rot(0, -90 + sit_up * 90, 0) @ rot(toss, 0, 0)
        pos = (3, 2.3 + sit_up * 0.1, -2.2 - sit_up * 3.0)
        pose = dict(ll=0, rl=0, la=0, ra=0, lar=5, rar=5)
        if sit_up > 0.5:
            pose.update(ll=90 * sit_up, rl=90 * sit_up)
            R = rot(0, 0, 0); pos = (3, 0.35, -5.6)
            pose.update(ll=90, rl=90)
        if phone_at_ear:
            pose.update(ra=150, rar=-28)
        if narr_pose: pose.update(narr_pose)
        character(sc, pos, root_R=R, pose=pose, face=nface or face, blob=False,
                  phone='r_screen' if phone_at_ear else None, **NARR)
        if sit_up < 0.5:
            sc.add(box((3, 2.95, -1.6), (4.2, 0.25, 4.0), '#2f4f9f', jitter=0.0))
        else:
            sc.add(box((3, 2.55, -2.4), (4.2, 0.8, 4.6), '#2f4f9f'))

# ---------------- house hallway ----------------
def hallway(sc, dad_door=0.0, front_light=1.0, dad=False, dad_face='blank', zzz=False, sign=False, knock=0.0, narr=None,
            moon=True, feet=None):
    night(sc, amb=(0.4, 0.43, 0.68), sun=(0.14, 0.16, 0.3))
    sc.fog = C('#0a0c1c'); sc.fogd = 0.022
    room(sc, 8, 30, 8, '#4a5582', '#5a3c28', floor_tile=0.8, floor_j=0.1, ceil='#9a9ab0', z0=0, holes=(('e', -4, 3.6, 6.8), ('w', -8, 3.6, 6.8)))
    sc.add(box((0, 0.03, 0), (3.2, 0.06, 26), '#8a2e2e', bg=True, mat='carpet'))
    # front door at south end (z=+15) facing north
    shake_off = math.sin(knock * 60) * 0.06 * (knock > 0)
    door(sc, (shake_off, 0, 14.95), R=rot(180), color='#6a3d22', hinge_left=True, behind='#05050a')
    # light under door
    sc.add(box((0, 0.06, 14.7), (3.0, 0.1, 0.3), '#ffd27a', emit=2.0 * front_light, shade=False))
    sc.lights.append(dict(pos=(0, 0.4, 14.2), col='#ffcf80', I=1.6 * front_light, r=3.2))
    if feet is not None:
        for fx in (-0.55 + feet, 0.45 + feet):
            sc.add(box((fx, 0.07, 14.52), (0.55, 0.14, 0.05), '#000000', shade=False, nocast=True))
    # small window next to door
    if moon:
        window(sc, (-3.95, 4.5, 11), 1.4, 2.6, R=rot(90), sky='#1d2f6a', emit=0.9)
        sc.lights.append(dict(pos=(-2.5, 4.5, 11), col='#6f8fe0', I=0.9, r=4))
    # dad's door on east wall
    hm = door(sc, (3.99, 0, -4), R=rot(-90), open_deg=dad_door, color='#7a4a2a', hinge_left=False, behind='#020204')
    # narrator door on west wall (open, lit faintly blue)
    door(sc, (-3.99, 0, -8), R=rot(90), open_deg=70, color='#7a4a2a', hinge_left=True, behind='#101a3a')
    sc.lights.append(dict(pos=(-2.8, 3, -8), col='#6f9fff', I=0.8, r=3))
    # pictures / table
    sc.add(box((-3.9, 4.6, 3), (0.1, 1.8, 2.4), '#d8c7a0'), box((-3.95, 4.6, 3), (0.12, 2.1, 2.7), '#3a2414'))
    sc.add(box((3.4, 1.4, 6), (1.2, 0.15, 2.4), '#5a3822'), box((3.4, 0.7, 5.0), (1, 1.4, 0.15), '#5a3822'), box((3.4, 0.7, 7.0), (1, 1.4, 0.15), '#5a3822'))
    sc.add(box((3.4, 1.9, 6.5), (0.5, 0.8, 0.5), '#3b7a4a'))
    sc.add(box((3.4, 1.65, 5.4), (0.4, 0.4, 0.4), '#333', rl=2), box((3.4, 2.3, 5.4), (0.1, 0.9, 0.1), '#333'),
           box((3.4, 2.95, 5.4), (0.8, 0.6, 0.8), '#ffd8a0', emit=1.4, shade=False, rl=1, nocast=True))
    sc.lights.append(dict(pos=(3.0, 3.0, 5.4), col='#ffbf70', I=1.3, r=4))
    for k, z in enumerate((-12, -9.8, 0.5, 2.6)):
        sd = -1 if k < 2 else 1
        ph = box((sd * 3.9, 4.6 + 0.4 * (k % 2), z), (0.1, 1.2, 1.0), '#eee', nocast=True)
        ph.tex['nx' if sd > 0 else 'px'] = (poster_img(['FAM', 'MOM', 'LOL', 'SUN'][k], k), False); sc.add(ph)
        sc.add(box((sd * 3.95, 4.6 + 0.4 * (k % 2), z), (0.12, 1.4, 1.2), '#3a2414'))
    sc.add(box((0, 0.04, 13.2), (3.0, 0.08, 2.0), '#5a4a3a', bg=True, mat='carpet'))
    for z in (-10, -2, 6):
        ceiling_lamp(sc, (0, 8, z))
    for k, z in enumerate((9.5, 10.5)):
        sc.add(box((3.9, 5.2, z), (0.2, 0.2, 0.2), '#d8b45a', rl=3), box((3.7, 4.2, z), (0.5, 2.0, 1.0), ['#3a5a8a', '#7a3a2a'][k], rl=2, mat='carpet'))
    sc.add(box((-3.9, 4.8, -13), (0.1, 1.6, 2.0), '#cfc0a0'), box((-3.95, 4.8, -13), (0.12, 1.9, 2.3), '#3a2414'))
    sc.add(box((3.9, 4.8, 1.5), (0.1, 1.4, 1.4), '#a0b8cf'), box((3.95, 4.8, 1.5), (0.12, 1.7, 1.7), '#3a2414'))
    if sign:
        fr = box((-3.86, 4.3, -1.5), (0.15, 3.4, 3.4), '#3a2414')
        sc.add(fr)
        pl = box((-3.8, 4.3, -1.5), (0.1, 3.0, 3.0), '#e8d8b2')
        pl.tex['px'] = (text_tex(["Who's in", "the house", "with you?"], size=(600, 600), fs=100), False)
        sc.lights.append(dict(pos=(-1.5, 5, -1.5), col='#ffe6b0', I=1.2, r=3))
        sc.add(pl)
    if dad:
        character(sc, (5.6, 0, -4.0), yaw=-90, face=dad_face, pose=dict(la=2, ra=2), idle=False, **DAD)
        sc.lights.append(dict(pos=(4.2, 5.5, -3.0), col='#5a6fc0', I=0.9, r=2.5))
    if zzz:
        pass
    if narr:
        narr(sc)
    return hm

# ---------------- exterior street ----------------
def street(sc, lamp=True, house_lights=True):
    night(sc, amb=(0.42, 0.46, 0.72), sun=(0.3, 0.34, 0.6))
    sc.fog = C('#1a2450'); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#3f8a3a', bg=True, mat='grass'))
    sc.add(box((0, 0.02, 10), (160, 0.1, 9), '#3a3a3e', bg=True, mat='asphalt'))
    for x in range(-60, 61, 8):
        sc.add(box((x, 0.09, 10), (3, 0.03, 0.3), '#d8c84a', bg=True))
    sc.add(box((0, 0.12, 3.5), (160, 0.24, 4), '#a8a8ae', bg=True, mat='tile'))
    # houses
    for hx, col, rcol in ((-14, '#c9b48a', '#5a2f2a'), (6, '#9ab0c4', '#3a3f55'), (26, '#c48a7a', '#3a2a2a')):
        hz = -10
        sc.add(box((hx, 4, hz), (16, 8, 10), col, mat='wood'))
        sc.add(box((hx - 4.2, 10.2, hz), (9.5, 0.6, 11), rcol, R=rot(0, 0, 38)))
        sc.add(box((hx + 4.2, 10.2, hz), (9.5, 0.6, 11), rcol, R=rot(0, 0, -38)))
        sc.add(box((hx, 9.5, hz), (10, 3, 9.6), col))
        for wx in (-4.5, 4.5):
            w = box((hx + wx, 4.6, hz + 5.02), (2.6, 2.4, 0.1), '#ffd88a' if house_lights else '#1a2245', emit=1.4 if house_lights else 0.4, shade=False)
            sc.add(w, box((hx + wx, 4.6, hz + 5.05), (2.9, 0.2, 0.2), '#eee'), box((hx + wx, 4.6, hz + 5.05), (0.2, 2.6, 0.2), '#eee'))
            pass
        if house_lights: sc.lights.append(dict(pos=(hx, 4.2, hz + 6.8), col='#ffc870', I=1.3, r=6))
        sc.add(box((hx + 1.6, 3.9, hz + 5.25), (0.4, 0.5, 0.4), '#fff0b0', emit=2, shade=False, nocast=True))
        sc.add(box((hx, 1.7, hz + 5.05), (2.2, 3.4, 0.15), '#5a3020'))
        sc.add(box((hx, 0.2, hz + 7), (2.6, 0.2, 4), '#9a9a9a', bg=True))
    # trees
    for tx in (-24, -4, 16, 36):
        sc.add(box((tx, 2, -3), (0.9, 4, 0.9), '#5a3a22'))
        sc.add(box((tx, 5.2, -3), (4.2, 3, 4.2), '#2f6a33'), box((tx, 7.2, -3), (2.8, 2, 2.8), '#367a3a'))
    for fx in np.arange(-30, 40, 1.2):
        sc.add(box((fx, 0.9, 1.3), (0.25, 1.8, 0.2), '#efefef'))
    sc.add(box((5, 1.3, 1.3), (70, 0.2, 0.15), '#efefef'), box((5, 0.6, 1.3), (70, 0.2, 0.15), '#efefef'))
    for bx in (-18, -10, 2, 10, 22, 30):
        sc.add(box((bx, 0.8, -4.2), (2.2, 1.6, 1.6), '#2f7a33', rl=4))
    sc.add(box((-13, 1.6, 2.2), (0.2, 3.2, 0.2), '#555'), box((-13, 3.4, 2.2), (0.8, 0.7, 1.4), '#3a5aa0', rl=2))
    if lamp:
        for lx in (-8, 14):
            sc.add(box((lx, 4, 5.8), (0.3, 8, 0.3), '#333'), box((lx, 8.1, 6.4), (0.3, 0.3, 1.6), '#333'),
                   box((lx, 7.85, 6.9), (0.9, 0.3, 0.9), '#fff2c0', emit=2.5, shade=False))
            sc.lights.append(dict(pos=(lx, 7.4, 6.9), col='#ffe0a0', I=2.2, r=7))
    sc.add(box((-60, 45, -90), (9, 9, 1), '#f4f2e0', emit=2.5, shade=False, rl=4, nocast=True))
    for hx, col in ((-34, '#a8c48a'), (46, '#d8c07a')):
        sc.add(box((hx, 4, -10), (14, 8, 10), col, mat='wood'), box((hx, 9.2, -10), (10, 2.6, 9.6), '#3a3040'))
        sc.add(box((hx - 3, 4.6, -4.95), (2.6, 2.4, 0.1), '#ffd88a', emit=1.4, shade=False))
    for px_ in (-20, 4, 28):
        sc.add(box((px_, 6, -3.8), (0.35, 12, 0.35), '#5a4030'), box((px_, 11.2, -3.8), (3, 0.25, 0.25), '#5a4030'))
    sc.add(box((-8, 11.0, -3.8), (48, 0.06, 0.06), '#111'), box((-8, 11.3, -3.6), (48, 0.06, 0.06), '#111'))
    car(sc, (-20, 0, 13), yaw=-90, color='#2a6ad0', lights=False)

def car(sc, pos, yaw=0, color='#c42a2a', lights=True, R=None, wreck=False, underglow=None, bounce=0.0, convertible=False):
    base = M4((pos[0], pos[1] + bounce, pos[2]), R if R is not None else rot(yaw))
    if underglow:
        sc.add(box((0, 0.35, 0), (4.0, 0.1, 8.6), underglow, parent=base, emit=2.5, shade=False, nocast=True))
        gp = base @ np.array([0, 0.2, 0, 1]); sc.lights.append(dict(pos=gp[:3], col=underglow, I=1.6, r=4))
    if wreck:
        sc.add(box((0, 2.2, 3.6), (4.4, 0.4, 2.6), color, parent=base @ M4((0, 0, 0), rot(0, -25, 8))),
               box((-1.0, 1.4, 4.4), (2.6, 1.2, 1.4), '#2a2a2a', parent=base, R=rot(20, 10, 15)),
               box((0, 2.75, -0.6), (4.4, 0.9, 4.0), '#0a0a0a', parent=base))
    if convertible:
        out = [box((0, 0.9, 0), (4.6, 0.6, 9.4), color, parent=base),
               box((0, 1.6, 3.2), (4.6, 0.9, 3.0), color, parent=base), box((0, 1.6, -3.6), (4.6, 0.9, 2.2), color, parent=base),
               box((2.15, 1.6, -0.5), (0.3, 0.9, 5.2), color, parent=base), box((-2.15, 1.6, -0.5), (0.3, 0.9, 5.2), color, parent=base),
               box((0, 1.25, -0.4), (4.0, 0.2, 5.0), '#2a1a1a', parent=base),
               box((0, 2.5, 1.6), (4.2, 1.0, 0.1), '#9fd0ff', parent=base, R=rot(0, -20, 0), emit=0.3),
               box((0, 1.7, -1.2), (3.8, 1.0, 0.6), '#2a1a1a', parent=base), box((0, 1.7, 0.9), (3.8, 1.0, 0.6), '#2a1a1a', parent=base)]
    else:
        out = [box((0, 1.4, 0), (4.6, 1.5, 9.4), color, parent=base),
               box((0, 2.75, -0.6), (4.2, 1.3, 5.0), color, parent=base),
               box((0, 2.75, -0.6), (4.3, 1.0, 4.6), '#1b2a44', parent=base),
               box((0, 2.75, -0.6), (4.0, 1.1, 5.1), '#1b2a44', parent=base)]
    for wx in (-2.2, 2.2):
        for wz in (-3, 3):
            out.append(box((wx, 0.75, wz), (0.7, 1.5, 1.5), '#151515', parent=base))
    out.append(box((-1.5, 1.6, 4.72), (1.0, 0.45, 0.1), '#fff6d0', parent=base, emit=2 if lights else 0, shade=not lights))
    out.append(box((1.5, 1.6, 4.72), (1.0, 0.45, 0.1), '#fff6d0', parent=base, emit=2 if lights else 0, shade=not lights))
    out.append(box((-1.6, 1.6, -4.72), (1.0, 0.4, 0.1), '#ff2020', parent=base, emit=1.5, shade=False))
    out.append(box((1.6, 1.6, -4.72), (1.0, 0.4, 0.1), '#ff2020', parent=base, emit=1.5, shade=False))
    sc.add(out)
    if lights:
        hp = base @ np.array([0, 1.6, 7, 1]); sc.lights.append(dict(pos=hp[:3], col='#fff0c0', I=2, r=6))
    sc.blobs.append((pos[0], 0.0, pos[2], 3.8, 1.0))
    return base

# ---------------- living room (day) ----------------
_newsframes = None
def tv_tex(t=0.0):
    global _newsframes
    import glob as _g
    if _newsframes is None:
        fs = sorted(_g.glob(os.path.join(os.path.dirname(TEXDIR), 'newsframes', '*.jpg')))
        _newsframes = [Image.open(f).convert('RGBA') for f in fs]
    idx = int(t * 6) % 4
    key = ('tv', idx)
    if key in _pc: return _pc[key]
    if _newsframes:
        src = _newsframes[idx % len(_newsframes)]
        im = src.crop((0, 300, 720, 705)).resize((640, 360))
    else:
        im = Image.new('RGBA', (640, 360), (20, 20, 40, 255))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_ANTON, 44); f2 = ImageFont.truetype(FONT_ANTON, 26)
    d.rectangle((0, 268, 250, 316), fill=(200, 20, 20)); d.text((12, 268), 'BREAKING NEWS', font=f2 if False else ImageFont.truetype(FONT_ANTON, 36), fill=(255, 255, 255))
    d.rectangle((0, 316, 640, 360), fill=(255, 255, 255)); d.text((12, 320), 'DEADLY CRASH ON ROUTE 9 · CAR FLIPPED', font=f2, fill=(20, 20, 20))
    d.rectangle((540, 16, 624, 52), fill=(200, 20, 20)); d.text((556, 16), 'LIVE', font=f2, fill=(255, 255, 255))
    _pc[key] = im
    return im

def livingroom(sc, t=0.0, mom=True):
    sc.sky = (C('#9fd0ff'), C('#e6f4ff')); sc.ambient = C((0.6, 0.58, 0.55)); sc.suncol = C((0.45, 0.42, 0.35))
    room(sc, 18, 16, 8, '#e8d3a8', '#8a6a4a', floor_tile=1.0, floor_j=0.06)
    window(sc, (5, 4.5, -7.95), 4, 3, sky='#bfe4ff', emit=1.0)
    sc.add(box((0, 0.03, 0), (9, 0.06, 7), '#c46a5a', bg=True, mat='carpet'))
    stand = box((0, 1, -7), (6, 2, 1.4), '#4a3020'); sc.add(stand)
    tv = box((0, 3.6, -7.2), (5.6, 3.2, 0.3), '#0a0a0a'); sc.add(tv)
    scr = box((0, 3.6, -7.03), (5.2, 2.9, 0.05), '#222'); scr.tex['pz'] = (tv_tex(t), True); sc.add(scr)
    sc.lights.append(dict(pos=(0, 3.6, -5.5), col='#ff8a6a', I=0.8 + 0.3 * math.sin(t * 17), r=5))
    # couch facing tv
    sc.add(box((0, 1, 4), (8, 2, 2.6), '#b75a4a', rl=1, mat='carpet'), box((0, 2.3, 5.1), (8, 3.2, 0.8), '#a8503f', rl=1, mat='carpet'),
           box((-4.2, 1.6, 4), (0.8, 1.6, 2.6), '#a8503f', rl=1, mat='carpet'), box((4.2, 1.6, 4), (0.8, 1.6, 2.6), '#a8503f', rl=1, mat='carpet'))
    bookshelf(sc, (-8.2, 0, -3), yaw=90)
    plant(sc, (7.5, 0, -6.5), 1.2); plant(sc, (-7.5, 0, 6.5), 1.0)
    poster(sc, (-8.97, 5, 3), rot(90), 3.0, 2.2, 'HOME', 3)
    lamp(sc, (5.5, 0, 4.5), on=False)
    if mom:
        character(sc, (0, -0.2, 3.6), yaw=180, pose=dict(ll=90, rl=90, la=55, ra=55, le=115, re=115, lar=-6, rar=-6, lay=10, ray=10, sit=True, y=0.4, hp=-8),
                  face='tears', blob=False, **MOM_OLD)

# ---------------- school hallway ----------------
def school(sc):
    sc.sky = (C('#9fd0ff'), C('#e6f4ff')); sc.ambient = C((0.62, 0.62, 0.66)); sc.suncol = C((0.35, 0.35, 0.33))
    sc.sun = np.array([0.2, -1, 0.1])
    room(sc, 12, 70, 9, '#d9dde8', '#d6d6d0', floor_tile=1.4, floor_j=0.07, ceil='#eeeeee', floor_mat='tile')
    rng = random.Random(5)
    for side in (-1, 1):
        x = side * 5.6
        for z in np.arange(-33, 33, 1.6):
            col = '#3a6ad0' if side < 0 else '#d04a4a'
            sc.add(box((x, 3.0, z), (1.6, 6, 1.5), col, mat='locker'))
    for k, z in enumerate(np.arange(-30, 31, 6)):
        poster(sc, (-5.97, 7.4, z + 1.5), rot(90), 1.6, 2.0, ['READ', 'MATH', 'GO!', 'ART', 'WIN'][k % 5], k)
        poster(sc, (5.97, 7.4, z - 1.5), rot(-90), 1.6, 2.0, ['CLUB', 'GG', 'SCI', 'DANCE', 'VOTE'][k % 5], k + 1)
    ban = box((0, 7.6, -20), (8, 1.4, 0.1), '#ffffff', nocast=True)
    ban.tex['pz'] = (text_tex(['GO TIGERS!'], size=(800, 140), bg=(230, 120, 30), fg=(255, 255, 255), font=FONT_ANTON, fs=100), False); sc.add(ban)
    ex = box((0, 8.4, -34.9), (1.6, 0.6, 0.1), '#ffffff', nocast=True)
    ex.tex['pz'] = (text_tex(['EXIT'], size=(320, 120), bg=(200, 20, 20), fg=(255, 255, 255), font=FONT_ANTON, fs=90), True); sc.add(ex)
    for z in (-11, 9):
        sc.add(box((4.4, 1.1, z), (1.0, 2.2, 1.0), '#3a7a4a', rl=1), box((4.4, 2.25, z), (1.1, 0.12, 1.1), '#2a5a3a', rl=1))
    sc.add(box((-4.6, 2.4, 4.5), (1.0, 0.5, 1.2), '#cfd4dc', rl=1), box((-4.6, 1.2, 4.5), (0.6, 2.0, 0.6), '#aab', rl=1))
    for z in np.arange(-30, 31, 8):
        sc.add(box((0, 8.95, z), (4, 0.1, 1.2), '#ffffff', emit=1.5, shade=False))
        sc.lights.append(dict(pos=(0, 8, z), col='#ffffff', I=0.35, r=6)) if abs(z) < 12 else None

def kid_crowd(sc, positions, t, phones=True, look_at=None, faces=None):
    for i, (x, z, yaw) in enumerate(positions):
        k = KIDS[i % len(KIDS)]
        y = yaw
        if look_at is not None:
            y = math.degrees(math.atan2(look_at[0] - x, look_at[1] - z))
        pose = dict(ra=150, rar=-28) if phones else dict()
        pose['hy'] = 0
        f = faces[i % len(faces)] if faces else 'neutral'
        character(sc, (x, 0, z), yaw=y, pose=pose, phone='r_screen' if phones else None, face=f, **k)

# ---------------- void / red room ----------------
def void(sc, lt=0.0):
    sc.sky = (C('#000000'), C('#000000')); sc.ambient = C((0.04, 0.04, 0.07)); sc.suncol = C((0, 0, 0))
    sc.add(box((0, -0.5, 0), (80, 1, 80), '#2a2a34', bg=True, mat='concrete'))
    sc.fog = C('#000000'); sc.fogd = 0.05
    sc.lights.append(dict(pos=(0, 9, 0), col='#c8d8ff', I=3.0, r=4.5))
    sc.add(box((0, 0.01, 0), (6, 0.02, 6), '#3a3a48', bg=True))

def redroom(sc, lt=0.0, flick=1.0):
    sc.sky = (C('#000'), C('#000')); sc.ambient = C((0.3, 0.1, 0.12)); sc.suncol = C((0, 0, 0))
    room(sc, 14, 14, 8, '#3a2a2e', '#2a1e1a', floor_tile=1.2, floor_j=0.12, ceil='#222')
    sc.fog = C('#080000'); sc.fogd = 0.03
    sc.lights.append(dict(pos=(1.5, 6.5, 4), col='#ff3a3a', I=3.2 * flick, r=7))
    sc.lights.append(dict(pos=(-3, 3, 5), col='#6a1010', I=0.8, r=6))
    # boarded window, overturned stuff
    window(sc, (3, 4.5, -6.95), 3.4, 2.8, sky='#100808', emit=0.2)
    for k, (yy, rr) in enumerate(((5.2, 12), (4.2, -8), (3.6, 4))):
        sc.add(box((3, yy, -6.6), (4.4, 0.45, 0.2), '#5a3a22', R=rot(0, 0, rr)))
    sc.add(box((-4, 0.6, -3), (3, 1.2, 1.8), '#4a3020', R=rot(30, 0, 80)))
    sc.add(box((-2.5, 0.4, -5), (1.5, 0.8, 1.5), '#555', R=rot(20)))
    # a door behind being pressed
    door(sc, (-3.5, 0, -6.95), color='#3a2010', behind='#000')


def add_rain(sc, t, center, n=150, area=12.0, top=14.0):
    rr = random.Random(77)
    cx, cy, cz = center
    for k in range(n):
        x = cx + rr.uniform(-area, area); z = cz + rr.uniform(-area, area)
        y = top - ((t * 28 + rr.uniform(0, top)) % top)
        sc.add(box((x, y, z), (0.035, 0.9, 0.035), '#b8d4ff', emit=0.8, shade=False, nocast=True, R=rot(0, 0, 8)))

def highway(sc, t=0.0):
    night(sc, amb=(0.36, 0.4, 0.66), sun=(0.22, 0.25, 0.45))
    sc.fog = C('#141a36'); sc.fogd = 0.012
    sc.add(box((0, -0.5, 0), (200, 1, 200), '#2f6a2c', bg=True, mat='grass'))
    sc.add(box((0, 0.02, 0), (200, 0.1, 11), '#26262a', bg=True, mat='asphalt'))
    for x in range(-90, 91, 7):
        sc.add(box((x, 0.09, 0), (3, 0.03, 0.25), '#e8d24a', bg=True))
    sc.add(box((0, 0.09, -5.0), (200, 0.03, 0.2), '#eeeeee', bg=True), box((0, 0.09, 5.0), (200, 0.03, 0.2), '#eeeeee', bg=True))
    sc.add(box((0, 1.0, -6.6), (200, 0.5, 0.15), '#9aa0a8'))
    for x in range(-90, 91, 4):
        sc.add(box((x, 0.5, -6.6), (0.2, 1.0, 0.2), '#7a8088'))
    for tx in range(-60, 61, 9):
        sc.add(box((tx + 2, 2, -12), (0.9, 4, 0.9), '#4a3020'), box((tx + 2, 5.4, -12), (4.4, 3.4, 4.4), '#24552a', rl=3), box((tx + 2, 7.6, -12), (3, 2, 3), '#2c6430', rl=3))
    for lx in (-40, -12, 30):
        sc.add(box((lx, 5, -7.5), (0.3, 10, 0.3), '#444'), box((lx, 10.1, -6.6), (0.3, 0.3, 2.0), '#444'),
               box((lx, 9.85, -5.8), (1.0, 0.3, 0.9), '#ffe8b0', emit=2.5, shade=False, nocast=True))
        sc.lights.append(dict(pos=(lx, 9.3, -5.6), col='#ffd890', I=1.6, r=8))
    sc.add(box((-60, 45, -90), (9, 9, 1), '#f4f2e0', emit=2.5, shade=False, rl=4, nocast=True))

def pole(sc, pos, bend=0.0):
    base = M4(pos, rot(0, 0, -bend))
    sc.add(box((0, 5, 0), (0.45, 10, 0.45), '#6a6a70', parent=base), box((0, 10, 1.0), (0.3, 0.3, 2.0), '#6a6a70', parent=base))

def fire(sc, pos, t, s_=1.0):
    rr = random.Random(5)
    for k in range(9):
        ph = (t * 2.2 + k / 9) % 1.0
        x = pos[0] + rr.uniform(-0.9, 0.9) * s_; z = pos[2] + rr.uniform(-0.9, 0.9) * s_
        y = pos[1] + ph * 2.6 * s_
        sz = (0.9 - ph * 0.6) * s_ * (0.8 + 0.4 * rr.random())
        col = '#fff0a0' if ph < 0.2 else ('#ffb020' if ph < 0.55 else '#ff4a10')
        sc.add(box((x, y, z), (sz, sz * 1.3, sz), col, emit=2.6, shade=False, rl=4, nocast=True))
    fl = 1 + 0.25 * math.sin(t * 19) + 0.15 * math.sin(t * 31)
    sc.lights.append(dict(pos=(pos[0], pos[1] + 1.2, pos[2] + 1.0), col='#ff8a30', I=2.8 * fl, r=6))

def smoke(sc, pos, t, s_=1.0):
    rr = random.Random(8)
    for k in range(10):
        ph = (t * 0.45 + k / 10) % 1.0
        x = pos[0] + rr.uniform(-0.7, 0.7) + ph * 2.0; z = pos[2] + rr.uniform(-0.7, 0.7)
        y = pos[1] + 2.0 + ph * 9 * s_
        sz = (1.0 + ph * 3.2) * s_
        g = 0.13 + 0.1 * rr.random()
        sc.add(box((x, y, z), (sz, sz, sz), (g, g, g + 0.02), rl=4, nocast=True))

def police(sc, pos, yaw, t, ph=0.0, kind='cop'):
    base = M4(pos, rot(yaw))
    if kind == 'cop':
        sc.add(box((0, 1.3, 0), (4.4, 1.4, 9.0), '#f2f2f2', parent=base), box((0, 1.3, 2.4), (4.45, 1.45, 2.8), '#111', parent=base),
               box((0, 1.3, -3.2), (4.45, 1.45, 2.4), '#111', parent=base), box((0, 2.6, -0.4), (4.0, 1.2, 4.6), '#151a25', parent=base))
        on = int(t * 7 + ph) % 2 == 0
        sc.add(box((-0.8, 3.35, -0.4), (1.4, 0.3, 0.7), '#ff2020', parent=base, emit=3 if on else 0.3, shade=False),
               box((0.8, 3.35, -0.4), (1.4, 0.3, 0.7), '#2050ff', parent=base, emit=0.3 if on else 3, shade=False))
        lp = base @ np.array([0, 4.2, -0.4, 1])
        sc.lights.append(dict(pos=lp[:3], col='#ff2020' if on else '#2050ff', I=2.6, r=8))
    else:
        sc.add(box((0, 2.4, 0), (4.6, 3.8, 10), '#f4f4f4', parent=base, rl=1), box((0, 2.0, 0), (4.65, 0.5, 10.05), '#d02020', parent=base),
               box((0, 2.4, 4.2), (4.0, 1.4, 1.7), '#1a2230', parent=base))
        on = int(t * 5 + ph) % 2 == 0
        sc.add(box((-1.2, 4.45, 4.5), (1.2, 0.3, 0.6), '#ff2020', parent=base, emit=3 if on else 0.3, shade=False),
               box((1.2, 4.45, 4.5), (1.2, 0.3, 0.6), '#ff2020', parent=base, emit=0.3 if on else 3, shade=False))
    for wx in (-2.1, 2.1):
        for wz in (-3, 3):
            sc.add(box((wx, 0.7, wz), (0.6, 1.4, 1.4), '#151515', parent=base))

def crash_site(sc, t):
    highway(sc, t)
    pole(sc, (6, 0, -5.6), bend=22)
    # overturned wreck against the pole
    car(sc, (3.4, 3.5, -2.6), R=rot(70, 0, 178), color='#b82424', lights=False, wreck=True)
    fire(sc, (4.8, 0.4, -2.0), t, 1.2); smoke(sc, (4.8, 0.4, -2.0), t, 1.1)
    rr = random.Random(12)
    for k in range(40):
        x = rr.uniform(-14, 3); z = rr.uniform(-4.5, 4.5)
        if rr.random() < 0.5:
            sc.add(box((x, 0.08, z), (rr.uniform(0.1, 0.25), 0.04, rr.uniform(0.1, 0.25)), '#bfe4ff', emit=0.5, R=rot(rr.uniform(0, 90)), nocast=True))
        else:
            sc.add(box((x, 0.12, z), (rr.uniform(0.2, 0.8), 0.15, rr.uniform(0.2, 0.6)), rr.choice(['#b82424', '#222', '#555']), R=rot(rr.uniform(0, 90), 0, rr.uniform(-20, 20))))
    sc.add(box((-6, 0.75, 2.5), (0.6, 1.5, 1.5), '#151515', R=rot(30, 0, 80)))
    for k in range(12):
        sc.add(box((-13 + k * 1.1, 0.07, 1.2 + 0.4 * math.sin(k)), (1.0, 0.05, 0.22), '#0c0c0c', R=rot(8), nocast=True))
    police(sc, (-9, 0, 6.5), 75, t, 0); police(sc, (12, 0, 6), -100, t, 1)
    police(sc, (-20, 0, -1.5), 90, t, 0, kind='amb')
    for k, x in enumerate(np.arange(-5, 11, 2.0)):
        sc.add(box((x, 0.45, 3.6), (0.5, 0.9, 0.5), '#ff7a10', rl=2), box((x, 0.6, 3.6), (0.55, 0.15, 0.55), '#ffffff', rl=1))
        if k < 7: sc.add(box((x + 1, 0.8, 3.6), (2.0, 0.12, 0.04), '#ffd800', emit=0.4, nocast=True))
    character(sc, (-4.5, 0, 6.0), yaw=200, pose=dict(ra=60, re=40), face='worried', idle=True,
              skin='#c48a5c', shirt='#1a2440', pants='#1a2440', cuff='#c48a5c', hair='cap', haircol='#1a2440', design='collar', shoes='#111')
