from .tsets import *
from .hsets import _tx

# ---------------- characters ----------------
KIDH = dict(design='hoodie', skin='#d9a27a', arms='#3a7ad8', shirt='#3a7ad8', pants='#2a2a33', cuff='#d9a27a', hair='curly', haircol='#1a1410', shoes='#f0f0f0')
TEEN = dict(design='tee_logo', skin='#d9a27a', arms='#d9a27a', shirt='#2f2f3a', pants='#1c1c24', cuff='#d9a27a', hair='curly', haircol='#1a1410', shoes='#e84a4a')
FIRE = dict(design='collar', skin='#c88a62', arms='#c8a040', shirt='#c8a040', pants='#c8a040', cuff='#3a3a3a', hair='short', haircol='#222', shoes='#222')
def helmet_extra(out, base, hm, arms):
    out.append(box((0, 1.25, 0), (1.5, 0.55, 1.5), '#c42a2a', parent=hm, rl=3))
    out.append(box((0, 1.0, 0.25), (1.8, 0.12, 1.9), '#c42a2a', parent=hm, rl=2))
    out.append(box((0, 1.3, 0.78), (0.4, 0.4, 0.06), '#ffd24a', parent=hm, emit=0.3))
    for y in (2.4, 3.3):
        out.append(box((0, y, 0.52), (2.02, 0.16, 0.06), '#e8f070', parent=base, emit=0.6))

RUST = '#b0602a'; RUST2 = '#7a3a1a'
# ---------------- Bolt ----------------
def bolt(sc, pos, yaw=0.0, t=0.0, eye=1.0, arm_l=10.0, arm_r=10.0, melt=0.0, look=0.0, bob=True, scale=1.0, eye_col='#5af0ff', dust=0.0, light=True, tilt=0.0, ext_l=0.0, lean_l=0.0):
    """small rusty robot. eye 0..1 brightness; arm angles (deg forward/up); melt 0..1; look = head pitch (+ up)"""
    b = 0.06 * abs(math.sin(t * 9)) if bob and melt == 0 else 0.0
    S = np.eye(4); S[:3, :3] *= scale
    base = M4(pos, rot(yaw, 0, tilt + 22 * melt)) @ S
    sq = 1 - 0.38 * melt
    body = base @ M4((0, b, 0))
    rc = lerp(C(RUST), C('#5a4032'), melt); rc2 = lerp(C(RUST2), C('#3a2a20'), melt)
    out = [box((0, 0.42, 0), (0.75, 0.75, 0.5), '#2a2a2a', parent=base, rl=4),           # wheel
           box((0, 0.42, 0), (0.3, 0.3, 0.56), '#888', parent=base, rl=2),
           box((0, 0.95, 0), (0.5, 0.35, 0.4), '#555', parent=base),                     # neck to wheel
           box((0, 1.55 * sq + 0.2 * melt, 0), (1.6, 1.3 * sq, 1.15), rc, parent=body, rl=1),     # torso
           box((0.35, 1.75 * sq, 0.585), (0.45, 0.35, 0.04), rc2, parent=body, rl=1),
           box((-0.4, 1.3 * sq, 0.585), (0.3, 0.25, 0.04), rc2, parent=body, rl=1),
           box((0, 1.55 * sq, 0.6), (0.6, 0.18, 0.04), '#3a3a3a', parent=body)]
    # dented panel lines
    for k in range(3):
        out.append(box((-0.15 + k * 0.2, 1.05 * sq + 0.08, 0.59), (0.06, 0.06, 0.03), '#2a2a2a', parent=body))
    # arms (pivot at shoulders)
    for side, ang in ((-1, arm_r), (1, arm_l)):
        ext = ext_l if side == 1 else 0.0
        am = body @ M4((side * 0.92, 2.0 * sq, 0), rot(0, ang + 15 * melt, side * -8 + (lean_l if side == 1 else 0)))
        L = 0.85 + ext
        out.append(box((0, -L / 2, 0), (0.22, L, 0.22), '#6a6a6a' if melt < 0.5 else '#2a2a2a', parent=am, rl=1))
        if ext > 0:
            # telescoping rings
            for k in range(1, int(ext / 0.6) + 1):
                out.append(box((0, -0.4 - k * 0.6, 0), (0.3, 0.1, 0.3), rc2, parent=am, rl=1))
            # hand opens into a little umbrella canopy
            out.append(box((0, -L - 0.08, 0), (0.34, 0.25, 0.34), rc, parent=am, rl=2))
            cm = am @ M4((0, -L - 0.2, 0), rot(0, 0, -(lean_l - 8)))
            out.append(box((0, -0.05, 0), (2.7, 0.12, 2.3), rc, parent=cm, rl=1))
            out.append(box((0, -0.12, 0), (2.4, 0.06, 2.0), rc2, parent=cm, rl=1))
            for cx in (-1.3, 1.3):
                out.append(box((cx, 0.08, 0), (0.12, 0.3, 2.3), rc, parent=cm, rl=1))
        else:
            out.append(box((0, -0.92, 0), (0.34, 0.25, 0.34), rc, parent=am, rl=2))
    # head
    hm = body @ M4((0, 2.25 * sq + 0.5, 0), rot(0, -look, 18 * melt))
    out += [box((0, 0, 0), (1.35, 1.0 * (1 - 0.2 * melt), 1.1), rc, parent=hm, rl=1),
            box((0, 0.62, 0), (0.06, 0.4, 0.06), '#444', parent=hm),
            box((0, 0.86, 0), (0.18, 0.18, 0.18), '#e84a3a' if melt < 0.5 else '#2a2a2a', parent=hm, rl=4, emit=0.3 * (1 - melt))]
    # one big eye (right) + cracked dead eye (left)
    ec = C(eye_col)
    out.append(box((0.3, 0.05, 0.56), (0.5, 0.5, 0.05), '#1a1a1a', parent=hm, rl=4))
    out.append(box((0.3, 0.05, 0.59), (0.36, 0.36, 0.04), ec * (0.25 + 0.75 * eye) if eye > 0.02 else '#111', parent=hm, rl=4, emit=2.4 * eye, shade=eye < 0.05))
    out.append(box((-0.32, 0.05, 0.56), (0.32, 0.32, 0.05), '#1e2226', parent=hm, rl=4))
    out.append(box((-0.32, 0.08, 0.59), (0.04, 0.34, 0.03), '#9aa4aa', parent=hm, R=rot(0, 0, 30)))
    out.append(box((-0.28, 0.0, 0.59), (0.04, 0.2, 0.03), '#9aa4aa', parent=hm, R=rot(0, 0, -40)))
    out.append(box((0, -0.3, 0.56), (0.5, 0.06, 0.03), '#2a2a2a', parent=hm))
    if dust > 0:
        out.append(box((0, 0.52, 0), (1.3, 0.05 * dust + 0.01, 1.05), '#9a9488', parent=hm))
        out.append(box((0, 2.22 * sq, 0), (1.55, 0.05 * dust + 0.01, 1.1), '#9a9488', parent=body))
    sc.add(out)
    eyew = hm @ np.array([0.3, 0.05, 0.9, 1.0])
    if light and eye > 0.05:
        sc.lights.append(dict(pos=tuple(eyew[:3]), col=eye_col, I=1.2 * eye, r=4.5))
    return tuple((hm @ np.array([0.3, 0.05, 0.6, 1]))[:3])

def shiny_bot(sc, pos, yaw=0.0, t=0.0, col='#eef3fa', visor='#3ab0ff', fly=0.0, arm=10.0, kind=0):
    b = 0.05 * math.sin(t * 3 + pos[0])
    base = M4((pos[0], pos[1] + b + fly, pos[2]), rot(yaw))
    out = [box((0, 1.6, 0), (1.5, 1.7, 1.0), col, parent=base, rl=3),
           box((0, 2.95, 0), (1.3, 1.0, 1.0), col, parent=base, rl=3),
           box((0, 2.95, 0.51), (1.05, 0.42, 0.04), '#10141c', parent=base, rl=4),
           box((-0.24, 2.97, 0.54), (0.18, 0.18, 0.03), visor, parent=base, rl=4, emit=2.2),
           box((0.24, 2.97, 0.54), (0.18, 0.18, 0.03), visor, parent=base, rl=4, emit=2.2),
           box((0, 1.7, 0.51), (0.5, 0.5, 0.04), visor, parent=base, rl=4, emit=1.2),
           box((0, 0.5, 0), (1.0, 0.5, 0.8), '#c8d0dc', parent=base, rl=3)]
    for side in (-1, 1):
        am = base @ M4((side * 0.95, 2.2, 0), rot(0, arm, side * -6))
        out.append(box((0, -0.5, 0), (0.3, 1.0, 0.3), col, parent=am, rl=3))
    if kind == 1:
        out.append(box((0, 3.6, 0), (0.12, 0.5, 0.12), visor, parent=base, emit=1.5))
    sc.add(out)
    if fly > 0.05:
        for side in (-0.4, 0.4):
            fl = 0.6 + 0.3 * math.sin(t * 30 + side)
            sc.add(box((pos[0] + side, pos[1] + fly - 0.2 + b, pos[2]), (0.3, fl, 0.3), '#7ad8ff', emit=3, shade=False, rl=4, nocast=True))
    return base

def robot_box(sc, pos, open_=0.0, col='#c8a070', yaw=0.0):
    base = M4(pos, rot(yaw))
    out = [box((0, 0.9, 0), (2.4, 1.8, 2.4), col, parent=base, mat='wood')]
    for sx in (-1, 1):
        fm = base @ M4((sx * 1.2, 1.8, 0), rot(0, 0, sx * -110 * open_))
        out.append(box((-sx * 0.6, 0.03, 0), (1.2, 0.06, 2.4), col, parent=fm))
    sc.add(out)

def hud_text(sc, lines, frac_y=0.62, width=0.8, bg=(10, 30, 50), fg=(120, 240, 255), d=2.0, fs=90, size=(900, 180)):
    """a flat label floating in front of the camera (must be called after sc.cam is set)"""
    cam = sc.cam
    p = np.array(cam['pos'], float); tg = np.array(cam['target'], float)
    f = tg - p; f /= np.linalg.norm(f)
    up = np.array([0, 1.0, 0]); r = np.cross(f, up); r /= np.linalg.norm(r); u = np.cross(r, f)
    hh = d * math.tan(math.radians(cam.get('fov', 50)) / 2); hw = hh * 720 / 1280
    w = 2 * hw * width; h = w * size[1] / size[0]
    c = p + f * d + u * (hh * (2 * frac_y - 1))
    Rm = np.stack([r, u, -f], axis=1)
    key = ('hud', tuple(lines), bg, fg, size, fs)
    if key not in _tx:
        im = Image.new('RGBA', size, bg + (255,)); dr = ImageDraw.Draw(im)
        fnt = ImageFont.truetype(FONT_POPPINS, fs)
        dr.rectangle((4, 4, size[0] - 5, size[1] - 5), outline=fg, width=6)
        dr.text((size[0] / 2, size[1] / 2), lines[0], font=fnt, fill=fg, anchor='mm')
        _tx[key] = im
    bx = box(tuple(c), (w, h, 0.002), '#ffffff', R=Rm, nocast=True, shade=False, emit=1.0)
    bx.tex['pz'] = (_tx[key], True); sc.add(bx)

# ---------------- school yard (first day) ----------------
def academy_sign_img():
    k = 'academy_pro'
    if k in _tx: return _tx[k]
    W_, H_ = 1600, 250
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 255))
    g = Image.new('RGB', (1, H_))
    for y in range(H_):
        a = y / H_; g.putpixel((0, y), (int(18 + 20 * (1 - a)), int(32 + 40 * (1 - a)), int(78 + 70 * (1 - a))))
    im.paste(g.resize((W_, H_)), (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W_ - 1, H_ - 1), outline=(212, 170, 60), width=14)
    d.rectangle((22, 22, W_ - 23, H_ - 23), outline=(255, 226, 140), width=4)
    # shine band
    sh = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.polygon([(0, 30), (W_, 0), (W_, 70), (0, 100)], fill=(255, 255, 255, 26)); im = Image.alpha_composite(im, sh); d = ImageDraw.Draw(im)
    def star(cx, cy, r, col):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; rr_ = r if i % 2 == 0 else r * 0.45
            pts.append((cx + math.cos(a) * rr_, cy + math.sin(a) * rr_))
        d.polygon(pts, fill=col)
    for cx in (140, W_ - 140):
        d.ellipse((cx - 82, H_ / 2 - 82, cx + 82, H_ / 2 + 82), fill=(212, 170, 60)); d.ellipse((cx - 68, H_ / 2 - 68, cx + 68, H_ / 2 + 68), fill=(24, 44, 110))
        star(cx, H_ / 2 + 4, 52, (255, 226, 140))
    f = ImageFont.truetype(FONT_ANTON, 160)
    d.text((W_ / 2 + 5, H_ / 2 + 7), 'SUPER ACADEMY', font=f, fill=(5, 10, 30), anchor='mm')
    d.text((W_ / 2, H_ / 2), 'SUPER ACADEMY', font=f, fill=(255, 255, 255), anchor='mm', stroke_width=5, stroke_fill=(212, 170, 60))
    _tx[k] = im; return im

def robot_day_img():
    k = 'robotday_pro'
    if k in _tx: return _tx[k]
    W_, H_ = 1600, 230
    im = Image.new('RGB', (W_, H_))
    for x in range(W_):
        a = x / W_
        c = (int(30 + 150 * a), int(190 - 120 * a), int(255 - 20 * a))
        ImageDraw.Draw(im).line((x, 0, x, H_), fill=c)
    im = im.convert('RGBA'); d = ImageDraw.Draw(im)
    rr_ = random.Random(4)
    for _ in range(60):
        x, y, r = rr_.randint(0, W_), rr_.randint(0, H_), rr_.randint(3, 8)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 60))
    d.rectangle((0, 0, W_ - 1, 16), fill=(255, 255, 255)); d.rectangle((0, H_ - 17, W_ - 1, H_ - 1), fill=(255, 255, 255))
    def bot_icon(cx, cy, s, flip=1):
        d.rounded_rectangle((cx - 55 * s, cy - 40 * s, cx + 55 * s, cy + 45 * s), radius=int(16 * s), fill=(255, 255, 255))
        d.rounded_rectangle((cx - 42 * s, cy - 22 * s, cx + 42 * s, cy + 12 * s), radius=int(10 * s), fill=(20, 24, 40))
        for ex in (-20, 20): d.ellipse((cx + (ex - 9) * s, cy + (-14) * s, cx + (ex + 9) * s, cy + 4 * s), fill=(90, 240, 255))
        d.line((cx, cy - 40 * s, cx, cy - 66 * s), fill=(255, 255, 255), width=int(7 * s)); d.ellipse((cx - 11 * s, cy - 80 * s, cx + 11 * s, cy - 58 * s), fill=(255, 90, 90))
        d.rounded_rectangle((cx - 22 * s, cy + 22 * s, cx + 22 * s, cy + 32 * s), radius=4, fill=(20, 24, 40))
    bot_icon(150, H_ / 2 + 18, 1.0); bot_icon(W_ - 150, H_ / 2 + 18, 1.0)
    f = ImageFont.truetype(FONT_ANTON, 150)
    d.text((W_ / 2 + 6, H_ / 2 + 8), 'ROBOT DAY!', font=f, fill=(20, 10, 60, 200), anchor='mm')
    d.text((W_ / 2, H_ / 2), 'ROBOT DAY!', font=f, fill=(255, 255, 255), anchor='mm', stroke_width=6, stroke_fill=(30, 20, 90))
    _tx[k] = im; return im

def first_day(sc, t, mood=0.0, banner=True):
    schoolyard(sc, t, mood=mood)
    # metal-framed academy sign with spotlights
    sc.add(box((0, 10.75, -10.88), (13.6, 2.4, 0.2), '#20242c', rl=1))
    sg = box((0, 10.75, -10.76), (13.0, 2.03, 0.06), '#fff', nocast=True); sg.tex['pz'] = (academy_sign_img(), True); sc.add(sg)
    for x in (-4.5, 0, 4.5):
        sc.add(box((x, 12.15, -10.4), (0.5, 0.25, 0.7), '#2a2a30', rl=1), box((x, 12.02, -10.15), (0.35, 0.06, 0.3), '#fff6d8', emit=2.0, shade=False))
    if banner:
        bn = box((0, 6.1, -10.8), (13.0, 1.87, 0.08), '#fff', nocast=True)
        bn.tex['pz'] = (robot_day_img(), True); sc.add(bn)
        for x in (-6.5, 6.5):
            sc.add(box((x, 6.1, -10.82), (0.12, 2.1, 0.12), '#d8d8e0'))

# ---------------- bedroom ----------------
def kid_room(sc, t, night_=True, lamp=False, glow=0.0, smoke_=0.0, fire_=0.0, door_open=0.0, shelf_eye=0.0, new_room=False):
    if night_:
        sc.sky = (C('#0a1028'), C('#1a2448')); sc.ambient = C((0.2, 0.22, 0.34)); sc.suncol = C((0.12, 0.14, 0.24))
    else:
        sc.sky = (C('#9fd0ff'), C('#e6f4ff')); sc.ambient = C((0.5, 0.5, 0.5)); sc.suncol = C((0.4, 0.38, 0.32))
    sc.sun = np.array([0.4, -0.6, -0.7])
    wall = '#6a7ab8' if not new_room else '#7a8a9a'
    room(sc, 16, 14, 8, wall, '#7a5a3a', floor_tile=1.0, floor_j=0.06, ceil='#d8d8e0', walls='nsw')
    # east wall with a door hole at z=2
    sc.add(box((8.25, 4, -4.0), (0.5, 8, 6), wall, bg=True, mat='wall'), box((8.25, 4, 5.5), (0.5, 8, 3), wall, bg=True, mat='wall'),
           box((8.25, 7.3, 2.0), (0.5, 1.4, 4.0), wall, bg=True, mat='wall'))
    # door (swings in, or smashed)
    if door_open < 0.99:
        hm = M4((8.05, 0, 0.3), rot(-100 * door_open))
        sc.add(box((0, 3.3, 1.7), (0.2, 6.5, 3.3), '#e8e0d0', parent=hm, mat='wood'))
    sc.add(box((9.5, 3.3, 2.0), (2.5, 6.5, 4.0), '#ff7a20' if fire_ > 0 else '#1a1a22', emit=1.5 * fire_, shade=fire_ == 0))
    window(sc, (2.0, 4.4, -6.95), 3.6, 3.0, sky='#18224a' if night_ else '#bfe4ff', emit=0.5 if night_ else 1.0, moon=night_)
    bed(sc, (-5.2, 0, -3.0), yaw=0, blanket='#3a6ad8', length=7, width=4.2)
    # rug, desk, posters
    sc.add(box((0, 0.03, 1.5), (6, 0.06, 4), '#d84a4a', bg=True, mat='carpet'))
    sc.add(box((5.5, 2.4, -5.8), (3.5, 0.2, 2.0), '#8a5a3a', mat='wood'), box((5.5, 1.2, -5.8), (3.3, 2.4, 1.8), '#7a4a2a', mat='wood'))
    poster(sc, (-7.97, 5.2, 1.5), rot(90), 2.4, 3.0, 'ROBOT', 2)
    # shelf with robot eye
    sc.add(box((-2.5, 5.6, -6.75), (3.2, 0.15, 0.5), '#8a5a3a'))
    for k, (x, c) in enumerate(((-3.6, '#ffd24a'), (-3.1, '#5ac8ff'))):
        sc.add(box((x, 6.0, -6.75), (0.35, 0.7, 0.35), c, rl=2))
    if shelf_eye >= 0:
        sc.add(box((-2.0, 5.95, -6.7), (0.55, 0.55, 0.3), '#1a1a1a', rl=4))
        e = shelf_eye
        sc.add(box((-2.0, 5.95, -6.53), (0.38, 0.38, 0.05), lerp(C('#1a2a30'), C('#5af0ff'), min(1, e)), rl=4, emit=2.6 * e, shade=e < 0.05))
        if e > 0.05: sc.lights.append(dict(pos=(-2.0, 5.9, -5.8), col='#5af0ff', I=1.6 * e, r=6))
    if lamp:
        sc.add(box((-2.0, 1.1, -5.6), (1.2, 2.2, 1.2), '#6a4a2a', mat='wood'))
        lamp_(sc, (-2.0, 2.2, -5.6))
    sc.lights.append(dict(pos=(2.0, 4.4, -5.5), col='#8aa0ff', I=0.35 if night_ else 0.8, r=8))
    if fire_ > 0:
        sc.ambient = C((0.32, 0.18, 0.12)); sc.fog = C((0.35, 0.22, 0.16)); sc.fogd = 0.05 * smoke_ + 0.01
        for p in ((7.0, 0, 5.0), (7.2, 0, -3.0), (4.5, 0, -6.2), (-7.0, 0, 3.0)):
            fire(sc, p, t + p[0], s_=1.6 * fire_)
    if smoke_ > 0:
        rr = random.Random(21)
        for k in range(22):
            x = rr.uniform(-8, 8) + math.sin(t * 0.4 + k) * 0.8; z = rr.uniform(-7, 7)
            y = 8.2 - rr.uniform(0, 1.8 * smoke_) + 0.15 * math.sin(t + k)
            s_ = rr.uniform(1.8, 3.2); g = rr.uniform(0.1, 0.17)
            sc.add(box((x, y, z), (s_, s_ * 0.7, s_), (g, g * 0.95, g * 0.9), rl=4, nocast=True))

def lamp_(sc, pos):
    sc.add(box((pos[0], pos[1] + 0.1, pos[2]), (0.5, 0.2, 0.5), '#3a3a3a', rl=1), box((pos[0], pos[1] + 0.9, pos[2]), (0.8, 0.7, 0.8), '#ffe2a8', emit=1.2, shade=False, rl=1))
    sc.lights.append(dict(pos=(pos[0], pos[1] + 1.2, pos[2] + 0.6), col='#ffd8a0', I=1.0, r=6))

# ---------------- garage ----------------
def garage(sc, t, door=0.0, bulb=True, dust=0.0):
    """door: 0 open (light pours in), 1 closed"""
    sc.sky = (C('#141a2a'), C('#22283a')); sc.ambient = C((0.2, 0.21, 0.27)); sc.suncol = C((0.08, 0.08, 0.12))
    room(sc, 14, 12, 7, '#7a7a80', '#6a6a6e', floor_tile=1.6, floor_j=0.05, ceil='#5a5a60', floor_mat='concrete', walls='nwe')
    # garage door (south wall), rolls down from the top
    h = 7 * door
    for k in range(int(max(1, h // 0.9)) + 1):
        y = 7 - k * 0.9 - 0.45
        if y < 7 - h: break
        sc.add(box((0, y, 6.2), (14, 0.85, 0.15), '#d8d8dc'))
    if door < 0.98:
        sc.add(box((0, (7 - h) / 2, 6.6), (14, 7 - h, 0.1), '#24305a', emit=0.5, shade=False))
        sc.lights.append(dict(pos=(0, (7 - h) / 2, 5.0), col='#8aa0e0', I=1.4 * (1 - door), r=12))
    # shelves, boxes, bike, tools
    for z in (-4.5, 0, 4):
        sc.add(box((-6.5, 3.5, z), (0.9, 0.15, 3.0), '#5a4030'), box((-6.5, 5.5, z), (0.9, 0.15, 3.0), '#5a4030'))
        sc.add(box((-6.5, 4.0, z - 0.6), (0.8, 0.9, 1.0), '#b08a5a', mat='wood'), box((-6.5, 6.0, z + 0.7), (0.7, 0.7, 0.9), '#a07a4a', mat='wood'))
    sc.add(box((5.6, 1.0, -4.5), (2.0, 2.0, 2.0), '#a07a4a', mat='wood'), box((5.2, 2.5, -4.6), (1.4, 1.0, 1.4), '#b08a5a', mat='wood'))
    sc.add(box((4.0, 0.9, 2.5), (0.2, 1.8, 3.0), '#3a7ad8'), box((4.0, 0.5, 1.2), (0.2, 1.0, 1.0), '#222', rl=4), box((4.0, 0.5, 3.8), (0.2, 1.0, 1.0), '#222', rl=4))
    # cobwebs grow with dust
    if dust > 0.2:
        for (x, z) in ((-6.8, -5.8), (6.8, -5.8)):
            for k in range(4):
                sc.add(box((x * 0.95, 6.6 - k * 0.2, z * 0.95), (0.02, 0.02, 1.2 + k * 0.3), '#e0e0e0', R=rot(45 * (1 if x > 0 else -1)), nocast=True, emit=0.2))
    if bulb:
        sc.add(box((0, 6.6, 0), (0.05, 0.8, 0.05), '#222'), box((0, 6.1, 0), (0.35, 0.45, 0.35), '#fff2c0', emit=2.0, shade=False, rl=4))
        sc.lights.append(dict(pos=(0, 5.8, 0), col='#ffe0a0', I=0.7, r=9))
    rr = random.Random(3)
    for k in range(int(30 * (0.3 + dust))):
        sc.add(box((rr.uniform(-5, 5), (rr.uniform(0.5, 6) + t * 0.1) % 6.5 + 0.3, rr.uniform(-5, 5)), (0.04, 0.04, 0.04), '#d8d0c0', emit=0.4, shade=False, nocast=True, rl=4))

# ---------------- house exterior / fire / ruins ----------------
def house(sc, t, fire_=0.0, collapse=0.0, ruins=False, night_=True, upstairs_lit=False, smoke_on=True):
    if night_:
        sc.sky = (C('#06070e'), C('#1a1420') if fire_ == 0 else C('#3a1a10')); sc.ambient = C((0.18, 0.18, 0.28)); sc.suncol = C((0.06, 0.06, 0.1))
        sc.fog = C((0.12, 0.1, 0.12) if fire_ == 0 else (0.3, 0.15, 0.08)); sc.fogd = 0.012
    else:
        sc.sky = (C('#8a929e'), C('#c4c8ce')); sc.ambient = C((0.56, 0.56, 0.6)); sc.suncol = C((0.3, 0.3, 0.32))
        sc.fog = C((0.7, 0.72, 0.75)); sc.fogd = 0.012
    sc.sun = np.array([0.5, -0.7, -0.5])
    sc.add(box((0, -0.5, 0), (200, 1, 200), '#3a6a32' if not ruins else '#4a4a44', bg=True, mat='grass'))
    sc.add(box((0, -0.45, 18), (200, 1, 8), '#3a3a3e', bg=True, mat='asphalt'))
    sc.add(box((0, -0.42, 11), (3, 1, 10), '#9a9a9a', bg=True))
    wallc = '#d8c8a8'
    if not ruins:
        drop = 6 * ease(collapse)
        sc.add(box((0, 4.5, 0), (16, 9, 10), wallc, mat='wood'))
        sc.add(box((0, 11.25, 0), (16, 4.5, 10), wallc, mat='wood'))
        # roof (collapses)
        sc.add(box((-4.2, 15.8 - drop, 0), (9.5, 0.6, 11), '#4a2a2a', R=rot(0, 0, 38 + 20 * collapse)), box((4.2, 15.8 - drop, 0), (9.5, 0.6, 11), '#4a2a2a', R=rot(0, 0, -38 - 20 * collapse)))
        for (x, y) in ((-4.5, 4.4), (4.5, 4.4), (-4.5, 11.4), (3.0, 11.4)):
            lit = fire_ > 0 and (y > 8 or fire_ > 0.5)
            col = '#ff8a20' if lit else ('#ffd88a' if (upstairs_lit and y > 8) else '#1a2245')
            sc.add(box((x, y, 5.02), (2.6, 2.4, 0.1), col, emit=2.0 if lit else (1.2 if upstairs_lit and y > 8 else 0.3), shade=False),
                   box((x, y, 5.05), (2.9, 0.2, 0.2), '#eee'), box((x, y, 5.05), (0.2, 2.6, 0.2), '#eee'))
        sc.add(box((0, 1.7, 5.05), (2.2, 3.4, 0.15), '#5a3020'))
    else:
        for (x, z, w, h, d) in ((-7.6, 0, 0.8, 4.5, 10), (7.6, 0, 0.8, 3.0, 10), (0, -4.8, 16, 2.6, 0.8), (-3, 4.8, 6, 2.0, 0.8), (5, 4.8, 4, 1.2, 0.8)):
            sc.add(box((x, h / 2, z), (w, h, d), '#2a221e', mat='wood'))
        rr = random.Random(9)
        for k in range(30):
            sc.add(box((rr.uniform(-7, 7), 0.2 + rr.uniform(0, 0.6), rr.uniform(-4, 4)), (rr.uniform(0.5, 2.5), 0.25, 0.3), rr.choice(['#1a1410', '#2a201a', '#3a2a22']), R=rot(rr.uniform(0, 180), rr.uniform(-20, 20), rr.uniform(-20, 20))))
        sc.add(box((0, 0.05, 0), (15, 0.1, 9.5), '#2a2622', bg=True))
        for k in range(5 if smoke_on else 0):
            smoke(sc, (rr.uniform(-6, 6), -1.5, rr.uniform(-3, 3)), t + k, s_=0.5)
    if fire_ > 0 and not ruins:
        for p in ((-4.5, 10.2, 5.4), (3.0, 10.2, 5.4), (-4.5, 3.2, 5.4), (0, 13.6, 2), (-5, 14, 0), (5, 13.5, -1)):
            fire(sc, p, t + p[0], s_=2.2 * fire_)
        for k in range(4): smoke(sc, (-6 + k * 4, 14, 0), t + k, s_=1.4)
    # trees + fence
    for tx in (-14, 14):
        sc.add(box((tx, 2, -1), (0.9, 4, 0.9), '#3a2a1a'), box((tx, 5.2, -1), (4.2, 3, 4.2), '#2a5a2a' if not ruins else '#3a3a30'))

def truck(sc, pos, t):
    sc.add(box((pos[0], 2.2, pos[2]), (14, 3.4, 4.2), '#c41a1a', rl=1), box((pos[0] + 5.4, 3.0, pos[2]), (3.2, 3.0, 4.0), '#d42a2a', rl=1),
           box((pos[0], 4.2, pos[2]), (11, 0.4, 1.0), '#c0c0c8'))
    for x in (-4.5, 4.5):
        for z in (-2.1, 2.1):
            sc.add(box((pos[0] + x, 0.8, pos[2] + z), (1.6, 1.6, 0.5), '#1a1a1a', rl=4))
    on = (t * 3) % 1 < 0.5
    sc.add(box((pos[0] + 5.6, 4.7, pos[2] - 1), (0.6, 0.35, 0.6), '#ff2a2a', emit=3 if on else 0.2), box((pos[0] + 5.6, 4.7, pos[2] + 1), (0.6, 0.35, 0.6), '#2a6aff', emit=0.2 if on else 3))
    sc.lights.append(dict(pos=(pos[0] + 5.6, 5.5, pos[2]), col='#ff2a2a' if on else '#2a6aff', I=1.6, r=12))

def memory_chip(sc, pos, t, glow=1.0, R=None):
    base = M4(pos, R if R is not None else np.eye(3))
    sc.add([box((0, 0, 0), (0.9, 0.08, 0.6), '#1a5a2a', parent=base, rl=1),
            box((0, 0.07, 0), (0.4, 0.08, 0.3), '#222', parent=base, rl=1),
            box((0.0, 0.12, 0), (0.2, 0.02, 0.15), '#5af0ff', parent=base, emit=2.5 * glow)])
    for k in range(6):
        sc.add(box((-0.35 + k * 0.14, 0.05, 0.3), (0.06, 0.02, 0.06), '#ffd24a', parent=base, emit=0.5))
    sc.lights.append(dict(pos=(pos[0], pos[1] + 0.6, pos[2] + 0.4), col='#5af0ff', I=1.0 * glow, r=3.5))
