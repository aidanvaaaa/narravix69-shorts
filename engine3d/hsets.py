from .sets import *

KID = dict(design='tee', arms='#f0c8a0', skin='#f0c8a0', shirt='#f4f4f4', pants='#2a3f7a', cuff='#f0c8a0', hair='cap', haircol='#d42a2a', shoes='#1c1c22')
KID_BACK = dict(KID, hair='cap_back')
TONY = dict(design='collar', skin='#d9a57a', shirt='#9a1f2a', pants='#2a2a33', cuff='#d9a57a', hair='short', haircol='#1a1410', shoes='#1a1a1a')
FRIEND = dict(design='tee', skin='#f2c094', shirt='#e83c9a', pants='#2f8a4a', cuff='#f2c094', hair='curly', haircol='#c8642a', shoes='#f0f0f0')
MAYOR = dict(design='collar', skin='#e6c0a0', shirt='#1d2a55', pants='#1d2a55', cuff='#e6c0a0', hair='short', haircol='#bfbfc6', shoes='#111')
CHEF = dict(design='tee', skin='#8a5a3a', shirt='#f4f4f4', pants='#333', cuff='#8a5a3a', hair='short', haircol='#111', shoes='#222')
CARD = '#b07a40'

def mustache(col):
    def ex(out, base, hm, arms):
        out.append(box((0, 0.42, 0.66), (0.7, 0.16, 0.1), col, parent=hm, rl=2))
    return ex

def party_hat(col, extra=None):
    def ex(out, base, hm, arms):
        for k, (w, y) in enumerate(((0.75, 1.45), (0.52, 1.75), (0.3, 2.02))):
            out.append(box((0.15, y, 0), (w, 0.32, w), col if k != 1 else '#ffffff', parent=hm @ M4((0, 0, 0), rot(0, 0, -10)), rl=3))
        out.append(box((0.27, 2.22, 0), (0.2, 0.2, 0.2), '#ffd24a', parent=hm @ M4((0, 0, 0), rot(0, 0, -10)), rl=4))
        if extra: extra(out, base, hm, arms)
    return ex

def tony_extra(out, base, hm, arms):
    mustache('#1a1410')(out, base, hm, arms)
    out.append(box((0, 2.9, 0.52), (1.7, 1.9, 0.08), '#ffffff', parent=base, rl=1))
    out.append(box((0.55, 3.55, 0.6), (0.45, 0.18, 0.03), '#ffd24a', parent=base))

def chef_extra(out, base, hm, arms):
    out.append(box((0, 1.55, 0), (1.35, 0.5, 1.35), '#ffffff', parent=hm, rl=2))
    out.append(box((0, 2.05, 0), (1.55, 0.7, 1.55), '#ffffff', parent=hm, rl=4))

def mayor_extra(out, base, hm, arms):
    mustache('#bfbfc6')(out, base, hm, arms)
    out.append(box((0, 1.35, 0), (1.6, 0.12, 1.6), '#111', parent=hm, rl=1))
    out.append(box((0, 1.95, 0), (1.15, 1.2, 1.15), '#111', parent=hm, rl=1))
    out.append(box((0, 1.5, 0), (1.18, 0.2, 1.18), '#7a3ab0', parent=hm))
    out.append(box((0, 3.05, 0.53), (0.45, 2.5, 0.06), '#7a3ab0', parent=base @ M4((0, 0, 0), rot(0, 0, 38))))
    out.append(box((0.45, 2.55, 0.58), (0.35, 0.35, 0.06), '#ffd24a', parent=base, rl=4, emit=0.2))

def medal_extra(out, base, hm, arms):
    for k in range(9):
        u = -1 + 2 * k / 8
        out.append(box((u * 0.55, 3.9 - (1 - u * u) * 0.75, 0.53), (0.18, 0.12, 0.06), '#2050d0', parent=base, rl=1))
    out.append(box((0, 3.0, 0.6), (0.62, 0.62, 0.1), '#ffd24a', parent=base, rl=4, emit=0.45))
    out.append(box((0, 3.0, 0.66), (0.36, 0.36, 0.03), '#fff2a0', parent=base, rl=4, emit=0.7))

def slushie_extra(out, base, hm, arms):
    out.append(box((0, -1.25, 0.35), (0.45, 0.8, 0.45), '#4ac0ff', parent=arms['ra'], rl=1, emit=0.2))
    out.append(box((0.1, -0.7, 0.35), (0.06, 0.6, 0.06), '#ff3a3a', parent=arms['ra']))

# ---------- textures ----------
_tx = {}
def logo_img():
    if 'logo' in _tx: return _tx['logo']
    im = Image.new('RGBA', (512, 512), (200, 149, 90, 255)); d = ImageDraw.Draw(im)
    d.ellipse((96, 60, 416, 380), fill=(196, 40, 40))
    d.polygon([(256, 110), (170, 330), (342, 330)], fill=(255, 200, 80))
    for (x, y) in ((240, 220), (280, 270), (220, 290)):
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(196, 40, 40))
    d.text((256, 440), 'SLICE TOWN', font=ImageFont.truetype(FONT_ANTON, 70), fill=(255, 255, 255), anchor='mm', stroke_width=4, stroke_fill=(120, 30, 30))
    _tx['logo'] = im; return im

def sign_img(text, bg, fg, size=(1000, 260), fs=170, font=FONT_ANTON):
    k = (text, bg, fg, size, fs)
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', size, bg + (255,)); d = ImageDraw.Draw(im)
    d.text((size[0] / 2, size[1] / 2), text, font=ImageFont.truetype(font, fs), fill=fg, anchor='mm', stroke_width=6, stroke_fill=(60, 20, 20))
    _tx[k] = im; return im

def clock_img(sec_frac):
    k = ('clock', round(sec_frac, 2))
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((20, 20, 492, 492), fill=(255, 250, 240), outline=(200, 30, 30), width=26)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line((256 + 190 * math.sin(a), 256 - 190 * math.cos(a), 256 + 215 * math.sin(a), 256 - 215 * math.cos(a)), fill=(40, 40, 40), width=10)
    a = sec_frac * 2 * math.pi
    d.line((256, 256, 256 + 190 * math.sin(a), 256 - 190 * math.cos(a)), fill=(220, 30, 30), width=12)
    d.line((256, 256, 256 + 120 * math.sin(a / 12 + 1), 256 - 120 * math.cos(a / 12 + 1)), fill=(30, 30, 30), width=16)
    d.ellipse((236, 236, 276, 276), fill=(30, 30, 30))
    _tx[k] = im; return im

# ---------- pizza boxes ----------
def pbox(sc, pos, yaw=0.0, s=1.0, R=None):
    base = M4(pos, R if R is not None else rot(yaw))
    b = box((0, 0.25 * s, 0), (3.0 * s, 0.5 * s, 3.0 * s), CARD, parent=base, rl=1)
    b.tex['py'] = (logo_img(), False)
    sc.add(b)

def pbox_stack(sc, pos, n, yaw=0.0, wobble=0.0, t=0.0):
    for k in range(n):
        dx = math.sin(k * 1.7 + t * 2) * wobble
        pbox(sc, (pos[0] + dx, pos[1] + k * 0.52, pos[2] + math.cos(k * 2.3) * wobble * 0.5), yaw + (k * 37 % 7 - 3))


# ---------- party props ----------





def party_street(sc, t, crowd=True, stage=True, n=14, crowd_face='grin', look_at=None, cheer=False, ncrowd_rows=2):
    night(sc, amb=(0.5, 0.48, 0.72), sun=(0.3, 0.3, 0.5))
    sc.sky = (C('#1a1450'), C('#5a3a9a')); sc.fog = C('#3a2a6a'); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#8a7ab0', bg=True, mat='tile'))
    sc.add(box((0, 0.02, -2), (160, 0.08, 14), '#3a3a52', bg=True, mat='asphalt'))
    # houses around
    for hx, col, rcol in ((-22, '#f2c4d8', '#5a3a7a'), (-6, '#c8e4ff', '#3a4a8a'), (10, '#fff0b0', '#7a3a3a'), (26, '#c8f0d0', '#3a6a5a')):
        hz = -18
        sc.add(box((hx, 4, hz), (14, 8, 9), col, mat='wood'))
        sc.add(box((hx - 3.6, 9.6, hz), (8.4, 0.6, 9.6), rcol, R=rot(0, 0, 38)), box((hx + 3.6, 9.6, hz), (8.4, 0.6, 9.6), rcol, R=rot(0, 0, -38)))
        sc.add(box((hx, 9.2, hz), (9, 2.6, 9.2), col))
        for wx in (-3.5, 3.5):
            sc.add(box((hx + wx, 4.8, hz + 4.55), (2.4, 2.2, 0.1), '#ffd88a', emit=1.4, shade=False, nocast=True))
    # distant pine hills
    for k, x in enumerate(range(-60, 61, 12)):
        sc.add(box((x, 6 + (k % 3) * 2, -50), (10, 14 + (k % 2) * 6, 6), '#3a6a5a', rl=2, R=rot(0, 0, 45)))
    # lamp posts and string lights
    for lx in (-14, 14):
        sc.add(box((lx, 4.5, 6), (0.3, 9, 0.3), '#222'), box((lx, 4.5, -10), (0.3, 9, 0.3), '#222'))
        sc.add(box((lx, 9.2, 6), (0.7, 0.7, 0.7), '#fff0c0', emit=2.2, shade=False, rl=3, nocast=True))
    string_lights(sc, (-14, 8.8, 6), (14, 8.8, 6), sag=1.4, n=30, t=t, lantern=True)
    string_lights(sc, (-14, 8.8, -10), (14, 8.8, -10), sag=1.4, n=30, t=t)
    for lx in (-14, 14):
        string_lights(sc, (lx, 8.8, -10), (lx, 8.8, 6), sag=1.6, t=t)
    string_lights(sc, (-14, 8.8, -2), (14, 8.8, -2), sag=1.8, n=30, t=t)
    bunting(sc, (-14, 8.0, 6), (14, 8.0, 6), n=24, sag=1.0)
    sc.lights.append(dict(pos=(0, 7, 0), col='#ffb0e0', I=1.4, r=12))
    sc.lights.append(dict(pos=(-12, 7, -4), col='#a0c0ff', I=1.0, r=10))
    sc.lights.append(dict(pos=(12, 7, -4), col='#ffd890', I=1.0, r=10))
    if stage:
        sc.add(box((0, 0.8, -12), (14, 1.6, 6), '#5a3a2a', mat='wood'), box((0, 6.0, -14.8), (14, 9, 0.4), '#2a1a4a'))
        bn = box((0, 9.2, -14.5), (10, 1.8, 0.1), '#ffd24a', nocast=True)
        bn.tex['pz'] = (sign_img('SUMMER BASH', (255, 210, 74), (200, 40, 120)), True); sc.add(bn)
        for sx in (-6.5, 6.5):
            sc.add(box((sx, 3.6, -12), (1.6, 4.0, 1.6), '#1a1a1a', rl=1))
            pulse = 1 + 0.08 * abs(math.sin(t * 8))
            sc.add(box((sx, 3.2, -11.15), (1.1 * pulse, 1.1 * pulse, 0.1), '#333', rl=4))
        for k, sx in enumerate((-5, -2, 2, 5)):
            sc.add(box((sx, 10.4, -13.5), (0.6, 0.6, 0.6), ['#ff5ab4', '#5ab4ff', '#ffd24a', '#5aff7a'][k], emit=2.5, shade=False, rl=3, nocast=True))
    if crowd:
        rr = random.Random(3)
        for k in range(n):
            row = k % ncrowd_rows
            x = -11 + (k // ncrowd_rows) * (22 / max(1, n // ncrowd_rows)) + rr.uniform(-0.6, 0.6)
            z = -5 + row * 3.2 + rr.uniform(-0.5, 0.5)
            yw = rr.uniform(-25, 25) + (180 if look_at == 'back' else 0)
            if isinstance(look_at, tuple):
                yw = math.degrees(math.atan2(look_at[0] - x, look_at[1] - z))
            dancer(sc, (x, 0, z), k, t, yaw=yw, face=crowd_face, cheer=cheer)
    confetti(sc, t, (0, 0, 0), area=14, n=70)




# ---------- pizza shop ----------
def shop_interior(sc, t, window_party=True, stack_h=0, flying=0.0, ceiling_hole=False):
    sc.sky = (C('#1a1450'), C('#5a3a9a'))
    sc.ambient = C((0.4, 0.37, 0.36)); sc.suncol = C((0.26, 0.23, 0.19)); sc.sun = np.array([0.3, -1.0, -0.4])
    room(sc, 18, 16, 9, '#c86a4a', '#a8743f', floor_tile=1.0, floor_j=0.08, ceil='#f4ecd8', floor_mat='wood')
    # back wall: brick lower band + window to the party
    sc.add(box((0, 1.6, -7.85), (18, 3.2, 0.25), '#8a3a2a', mat='tile'))
    if window_party:
        sc.add(box((0, 5.6, -7.95), (9, 4, 0.1), '#2a1a5a', emit=0.6, shade=False, nocast=True))
        rr = random.Random(5)
        for k in range(14):
            sc.add(box((rr.uniform(-4.2, 4.2), rr.uniform(4.0, 7.4), -7.9), (0.22, 0.22, 0.05), rr.choice(['#ff5ab4', '#ffd24a', '#5ab4ff', '#5aff7a']), emit=2.5 * (0.6 + 0.4 * math.sin(t * 4 + k)), shade=False, nocast=True))
        for k in range(3):
            age = ((t + k * 0.6) % 1.8) / 1.8
            cx, cy = (-2.5 + k * 2.5, 6.5 - k * 0.5)
            for j in range(12):
                a = j / 12 * 2 * math.pi; r = 1.4 * eout(age / 0.6)
                sc.add(box((cx + r * math.cos(a), cy + r * math.sin(a), -7.88), (0.15, 0.15, 0.04), ['#ff5ab4', '#ffd24a', '#5af0ff'][k], emit=3 * (1 - age), shade=False, nocast=True))
        for fx in (-4.6, 0, 4.6):
            sc.add(box((fx, 5.6, -7.82), (0.25, 4.2, 0.2), '#f4f4f4', nocast=True))
        sc.add(box((0, 3.5, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True), box((0, 7.7, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True))
    # pizza oven (right)
    sc.add(box((6.5, 1.5, -5.5), (4.5, 3, 4), '#7a4a3a', mat='tile'), box((6.5, 4.0, -5.5), (4.2, 2.4, 3.8), '#9a5a3a', rl=4))
    fl = 1 + 0.2 * math.sin(t * 17)
    sc.add(box((6.5, 3.5, -3.55), (1.8, 1.1, 0.1), '#ff7a20', emit=2.5 * fl, shade=False, rl=2, nocast=True))
    sc.lights.append(dict(pos=(6.5, 3.6, -2.5), col='#ff8a30', I=1.6 * fl, r=5))
    # menu board + logo
    mb = box((-5.5, 6.6, -7.7), (4.5, 2.4, 0.1), '#222', nocast=True)
    mb.tex['pz'] = (sign_img('SLICE TOWN', (40, 30, 30), (255, 210, 80), size=(900, 480), fs=150), True); sc.add(mb)
    # ceiling lamps
    for x in (-4, 4):
        ceiling_lamp(sc, (x, 9, -1), on=True)
        sc.lights.append(dict(pos=(x, 7.8, -1), col='#ffe8c0', I=0.6, r=7))
    # prep table where the kid works
    sc.add(box((0, 2.3, 0), (8, 0.25, 4), '#9a6a40', mat='wood'))
    for lx in (-3.6, 3.6):
        for lz in (-1.7, 1.7):
            sc.add(box((lx, 1.1, lz), (0.25, 2.2, 0.25), '#888'))
    # flat box pile on table
    for k in range(6):
        sc.add(box((-2.6, 2.48 + k * 0.07, -0.2), (3.0, 0.06, 3.0), '#c08a50' if k % 2 else CARD))
    # stack of finished boxes
    if stack_h:
        pbox_stack(sc, (2.9, 2.43, -0.2), stack_h, wobble=0.04, t=t)
    # big alarm clock
    ck = box((3.8, 3.3, 1.4), (1.6, 1.6, 0.6), '#d42a2a', rl=3, R=rot(-20)); ck.tex['pz'] = (clock_img(round((t * 0.5 % 1) * 24) / 24), False); sc.add(ck)

def shop_exterior(sc, t, through_roof=0.0, bird=0.0):
    night(sc, amb=(0.55, 0.52, 0.74), sun=(0.35, 0.33, 0.55))
    sc.sky = (C('#2a2070'), C('#9a6ab0')); sc.fog = C('#4a3a7a'); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#5a8a4a', bg=True, mat='grass'))
    sc.add(box((0, 0.02, 10), (160, 0.08, 10), '#3a3a48', bg=True, mat='asphalt'))
    for x in range(-40, 41, 5):
        sc.add(box((x, 0.08, 10), (2.4, 0.03, 0.3), '#ffffff', bg=True))
    sc.add(box((0, 0.12, 3.5), (160, 0.24, 4), '#b8b0c0', bg=True, mat='tile'))
    # building
    sc.add(box((0, 5, -4), (20, 10, 10), '#2fa8a0', mat='wood'))
    sc.add(box((0, 10.2, -4), (20.6, 0.5, 10.6), '#e8e0d0'))
    sc.add(box((0, 1.0, 1.05), (20.2, 2.0, 0.2), '#c84a3a', mat='tile'))
    sg = box((0, 8.4, 1.1), (12, 2.6, 0.3), '#fff4e0'); sg.tex['pz'] = (sign_img('SLICE TOWN', (255, 244, 224), (220, 60, 50)), True); sc.add(sg)
    lg = box((-8, 8.4, 1.2), (2.6, 2.6, 0.3), '#c42a2a', rl=4); lg.tex['pz'] = (logo_img(), True); sc.add(lg)
    for k in range(10):
        sc.add(box((-9 + k * 2, 6.2, 1.9), (2.0, 0.3, 1.8), '#ffffff' if k % 2 else '#d42a2a', R=rot(0, 20, 0)))
    sc.add(box((-3.5, 3.6, 1.06), (5, 4, 0.1), '#ffe0a0', emit=1.2, shade=False, nocast=True), box((5, 3.0, 1.06), (3, 5.2, 0.1), '#ffe0a0', emit=1.0, shade=False, nocast=True))
    nh = box((-3.5, 2.6, 1.15), (2.2, 1.0, 0.05), '#fff'); nh.tex['pz'] = (sign_img('NOW HIRING', (255, 255, 255), (200, 30, 30), size=(600, 260), fs=110), False); sc.add(nh)
    sc.lights.append(dict(pos=(0, 4, 4), col='#ffd890', I=1.4, r=9))
    if through_roof > 0:
        hgt = 10 + through_roof * 26
        n = int(hgt / 0.52)
        for k in range(20, n):
            pbox(sc, (1.5 + math.sin(k * 0.4) * 0.15, k * 0.52, -4), k * 7 % 11 - 5)
        rr = random.Random(2)
        for j in range(18):
            u = min(1, through_roof * 3)
            sc.add(box((1.5 + rr.uniform(-3, 3) * (1 + u), 10.5 + rr.uniform(0, 3) * u, -4 + rr.uniform(-3, 3)), (0.6, 0.15, 0.5), '#e8e0d0', R=rot(rr.uniform(0, 180), rr.uniform(-40, 40), 0)))
        if bird > 0:
            top = n * 0.52 + 0.3
            by = top + 6 * (1 - ease(bird))
            flap = math.sin(TIME[0] * 30) * 35 * (1 - ease(bird) * 0.8)
            sc.add(box((1.5, by + 0.5, -4), (0.7, 0.7, 1.1), '#3a8ae0', rl=3), box((1.5, by + 1.05, -3.6), (0.55, 0.55, 0.55), '#3a8ae0', rl=4),
                   box((1.5, by + 1.05, -3.25), (0.2, 0.12, 0.3), '#ffb020'),
                   box((1.05, by + 0.6, -4), (0.7, 0.08, 0.6), '#2a6ac0', R=rot(0, 0, flap)), box((1.95, by + 0.6, -4), (0.7, 0.08, 0.6), '#2a6ac0', R=rot(0, 0, -flap)))

# ================= SUMMER BASH v2: sunset beach park =================









def summer_park(sc, t, crowd=True, stage=True, n=14, crowd_face='grin', look_at=None, cheer=False, ncrowd_rows=2):
    dk = dusk_of(t)
    top = lerp(C('#4a8ae8'), C('#1a2058'), dk); bot = lerp(C('#ffb36a'), C('#ff6a4a'), dk)
    sc.sky = (top, bot); sc.stars = 1.0 * max(0, dk - 0.4) / 0.6
    sc.ambient = C(lerp((0.62, 0.55, 0.5), (0.42, 0.38, 0.55), dk)); sc.suncol = C(lerp((0.75, 0.55, 0.35), (0.35, 0.22, 0.25), dk))
    sc.sun = np.array([0.7, -0.45, 0.5]); sc.fog = C(lerp((1.0, 0.75, 0.55), (0.5, 0.35, 0.45), dk)); sc.fogd = 0.006
    sc.add(box((-45, 9 - 4 * dk, -120), (16, 16, 1), lerp(C('#fff0a0'), C('#ff7a3a'), dk), emit=2.6, shade=False, rl=4, nocast=True))
    sc.add(box((0, -0.5, -10), (200, 1, 60), '#5aa84a', bg=True, mat='grass'))
    sc.add(box((0, -0.45, -48), (200, 1, 16), '#f0d8a0', bg=True, mat='concrete'))
    sc.add(box((0, -0.55, -120), (300, 1, 130), lerp(C('#2a8ad8'), C('#1a3a7a'), dk), bg=True, emit=0.25, shade=False))
    rr = random.Random(4)
    for k in range(24):
        sc.add(box((rr.uniform(-60, 60), 0.0, rr.uniform(-110, -60)), (rr.uniform(1, 3), 0.05, 0.15), '#ffe8b0', emit=1.5 * (0.5 + 0.5 * math.sin(t * 3 + k)), shade=False, nocast=True, bg=True))
    for k, (px, pz) in enumerate(((-24, -16), (-16, -30), (18, -18), (26, -34), (-30, -6), (32, -4), (8, -38))):
        palm(sc, (px, 0, pz), h=8 + k % 3 * 1.5, lean=8 + k * 3, t=t)
    for k, (ux, uz) in enumerate(((-20, -44), (-10, -46), (12, -45), (22, -43))):
        umbrella(sc, (ux, -0.05, uz), ['#ff4a4a', '#3a8aff', '#ffd24a', '#5aff7a'][k], '#ffffff')
    ferris(sc, (-34, 0, -52), t)
    ice_cream_truck(sc, (19, 0, -12), yaw=-30)
    for k, x in enumerate((-16, -8, 8, 16)):
        tiki(sc, (x, 0, 7), t)
    for k, (bx, bz) in enumerate(((-6, 3), (7, 1), (-12, -2))):
        beach_ball(sc, (bx, 0, bz), t, k)
    sc.lights.append(dict(pos=(0, 8, 2), col='#ffb070', I=0.9, r=14))
    if dk > 0.2: sc.lights.append(dict(pos=(0, 6, 6), col='#ff9a40', I=1.2 * dk, r=12))
    if stage:
        sc.add(box((0, 0.8, -12), (14, 1.6, 6), '#b07a40', mat='wood'), box((0, 6.0, -14.8), (14, 9, 0.4), '#2a6ab0'))
        for sx in (-6.8, 6.8):
            sc.add(box((sx, 5.6, -12.5), (0.6, 8, 0.6), '#8a6a3a'))
        sc.add(box((0, 10.0, -12.5), (15, 0.6, 7), '#d8b060', rl=1), box((0, 10.5, -12.5), (13, 0.5, 6), '#c8a050', rl=1))
        bn = box((0, 8.6, -14.5), (10, 1.8, 0.1), '#ffd24a', nocast=True)
        bn.tex['pz'] = (sign_img('SUMMER BASH', (255, 140, 60), (255, 255, 255)), True); sc.add(bn)
        for sx in (-5.5, 5.5):
            sc.add(box((sx, 3.6, -12), (1.6, 4.0, 1.6), '#1a1a1a', rl=1))
            pulse = 1 + 0.08 * abs(math.sin(t * 8))
            sc.add(box((sx, 3.2, -11.15), (1.1 * pulse, 1.1 * pulse, 0.1), '#333', rl=4))
        for k, sx in enumerate((-4.5, -1.5, 1.5, 4.5)):
            sc.add(box((sx, 2.1, -9.5), (1.2, 2.2, 0.15), ['#ff5ab4', '#5ab4ff', '#ffd24a', '#5aff7a'][k], R=rot(0, -10, 0), rl=2))
    if crowd:
        rr = random.Random(3)
        for k in range(n):
            row = k % ncrowd_rows
            x = -11 + (k // ncrowd_rows) * (22 / max(1, n // ncrowd_rows)) + rr.uniform(-0.6, 0.6)
            z = -5 + row * 3.2 + rr.uniform(-0.5, 0.5)
            yw = rr.uniform(-25, 25) + (180 if look_at == 'back' else 0)
            if isinstance(look_at, tuple):
                yw = math.degrees(math.atan2(look_at[0] - x, look_at[1] - z))
            dancer(sc, (x, 0, z), k, t, yaw=yw, face=crowd_face, cheer=cheer)

party_street = summer_park

_shop_interior_v1 = shop_interior
def shop_interior(sc, t, window_party=True, stack_h=0, flying=0.0, ceiling_hole=False):
    _shop_interior_v1(sc, t, window_party=False, stack_h=stack_h)
    # sunset view through the window with the beach park ferris wheel
    sc.add(box((0, 6.6, -7.97), (9, 2.0, 0.1), '#ff9a6a', emit=1.0, shade=False, nocast=True),
           box((0, 4.6, -7.97), (9, 2.0, 0.1), '#ffc07a', emit=1.1, shade=False, nocast=True),
           box((2.6, 4.4, -7.93), (1.4, 1.4, 0.05), '#fff2a0', emit=2.0, shade=False, rl=4, nocast=True))
    for k in range(8):
        a = k / 8 * 2 * math.pi + t * 0.25
        sc.add(box((-2.4 + math.cos(a) * 1.3, 5.8 + math.sin(a) * 1.3, -7.9), (0.25, 0.25, 0.04), ['#ff5a5a', '#ffd24a', '#5ab4ff', '#ffffff'][k % 4], emit=2.5, shade=False, nocast=True))
    for fx in (-4.6, 0, 4.6):
        sc.add(box((fx, 5.6, -7.82), (0.25, 4.2, 0.2), '#f4f4f4', nocast=True))
    sc.add(box((0, 3.5, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True), box((0, 7.7, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True))

_shop_exterior_v1 = shop_exterior
def shop_exterior(sc, t, through_roof=0.0, bird=0.0):
    _shop_exterior_v1(sc, t, through_roof, bird)
    sc.sky = (C('#4a8ae8'), C('#ffb36a')); sc.stars = 0.0
    sc.ambient = C((0.62, 0.55, 0.5)); sc.suncol = C((0.75, 0.55, 0.35)); sc.sun = np.array([0.7, -0.45, 0.5])
    sc.fog = C((1.0, 0.75, 0.55)); sc.fogd = 0.006

# ================= box v2: each flap folds on its own, with a pizza inside =================


# ---------- party props ----------
def string_lights(sc, p0, p1, sag=1.2, n=16, t=0.0, lantern=False):
    cols = ['#ff5a5a', '#ffd24a', '#5aff7a', '#5ab4ff', '#ff7af0', '#ffffff']
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    for k in range(n + 1):
        u = k / n
        p = p0 * (1 - u) + p1 * u; p[1] -= sag * 4 * u * (1 - u)
        sc.add(box(p, (0.03, 0.03, 0.03), '#222', nocast=True))
        if 0 < k < n:
            c = cols[k % len(cols)]; tw = 0.8 + 0.4 * math.sin(t * 3 + k)
            if lantern and k % 3 == 0:
                sc.add(box(p - [0, 0.7, 0], (0.8, 1.0, 0.8), ['#ffb0e0', '#c8a0ff', '#a0e0ff'][k % 3], emit=1.4 * tw, shade=False, rl=4, nocast=True))
            else:
                sc.add(box(p - [0, 0.2, 0], (0.22, 0.28, 0.22), c, emit=2.2 * tw, shade=False, rl=4, nocast=True))

def bunting(sc, p0, p1, n=12, sag=0.6):
    cols = ['#ff5a5a', '#ffd24a', '#5ab4ff', '#5aff7a', '#ff7af0']
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    for k in range(1, n):
        u = k / n; p = p0 * (1 - u) + p1 * u; p[1] -= sag * 4 * u * (1 - u)
        sc.add(box(p - [0, 0.35, 0], (0.6, 0.7, 0.04), cols[k % 5], nocast=True, R=rot(math.degrees(math.atan2(p1[0] - p0[0], p1[2] - p0[2])) + 90)))

def fireworks(sc, t, centers, period=1.7):
    for ci, (cx, cy, cz, col) in enumerate(centers):
        age = ((t + ci * 0.53) % period) / period
        if age > 0.85: continue
        r = 5.5 * eout(age / 0.6)
        fade = max(0.0, 1 - age / 0.85)
        for k in range(22):
            a = k / 22 * 2 * math.pi; b = (k % 3 - 1) * 0.5
            p = (cx + r * math.cos(a) * math.cos(b), cy + r * math.sin(a) * math.cos(b) - 2.5 * age * age, cz + r * math.sin(b))
            sz = 0.45 * fade + 0.1
            sc.add(box(p, (sz, sz, sz), col, emit=3.0 * fade, shade=False, rl=4, nocast=True))
        if fade > 0.3: sc.lights.append(dict(pos=(cx, cy, cz + 3), col=col, I=1.2 * fade, r=14))

def confetti(sc, t, center, area=10, n=60, top=10):
    rr = random.Random(21)
    cols = ['#ff5a5a', '#ffd24a', '#5ab4ff', '#5aff7a', '#ff7af0', '#ffffff']
    for k in range(n):
        x = center[0] + rr.uniform(-area, area); z = center[2] + rr.uniform(-area, area)
        y = top - ((t * 2.2 + rr.uniform(0, top)) % top)
        sc.add(box((x + math.sin(t * 3 + k) * 0.3, y, z), (0.18, 0.02, 0.12), rr.choice(cols), emit=0.4, shade=False, nocast=True, R=rot(t * 200 + k * 40, k * 30, t * 150)))


def party_street(sc, t, crowd=True, stage=True, n=14, crowd_face='grin', look_at=None, cheer=False, ncrowd_rows=2):
    night(sc, amb=(0.5, 0.48, 0.72), sun=(0.3, 0.3, 0.5))
    sc.sky = (C('#1a1450'), C('#5a3a9a')); sc.fog = C('#3a2a6a'); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#8a7ab0', bg=True, mat='tile'))
    sc.add(box((0, 0.02, -2), (160, 0.08, 14), '#3a3a52', bg=True, mat='asphalt'))
    # houses around
    for hx, col, rcol in ((-22, '#f2c4d8', '#5a3a7a'), (-6, '#c8e4ff', '#3a4a8a'), (10, '#fff0b0', '#7a3a3a'), (26, '#c8f0d0', '#3a6a5a')):
        hz = -18
        sc.add(box((hx, 4, hz), (14, 8, 9), col, mat='wood'))
        sc.add(box((hx - 3.6, 9.6, hz), (8.4, 0.6, 9.6), rcol, R=rot(0, 0, 38)), box((hx + 3.6, 9.6, hz), (8.4, 0.6, 9.6), rcol, R=rot(0, 0, -38)))
        sc.add(box((hx, 9.2, hz), (9, 2.6, 9.2), col))
        for wx in (-3.5, 3.5):
            sc.add(box((hx + wx, 4.8, hz + 4.55), (2.4, 2.2, 0.1), '#ffd88a', emit=1.4, shade=False, nocast=True))
    # distant pine hills
    for k, x in enumerate(range(-60, 61, 12)):
        sc.add(box((x, 6 + (k % 3) * 2, -50), (10, 14 + (k % 2) * 6, 6), '#3a6a5a', rl=2, R=rot(0, 0, 45)))
    # lamp posts and string lights
    for lx in (-14, 14):
        sc.add(box((lx, 4.5, 6), (0.3, 9, 0.3), '#222'), box((lx, 4.5, -10), (0.3, 9, 0.3), '#222'))
        sc.add(box((lx, 9.2, 6), (0.7, 0.7, 0.7), '#fff0c0', emit=2.2, shade=False, rl=3, nocast=True))
    string_lights(sc, (-14, 8.8, 6), (14, 8.8, 6), sag=1.4, n=30, t=t, lantern=True)
    string_lights(sc, (-14, 8.8, -10), (14, 8.8, -10), sag=1.4, n=30, t=t)
    for lx in (-14, 14):
        string_lights(sc, (lx, 8.8, -10), (lx, 8.8, 6), sag=1.6, t=t)
    string_lights(sc, (-14, 8.8, -2), (14, 8.8, -2), sag=1.8, n=30, t=t)
    bunting(sc, (-14, 8.0, 6), (14, 8.0, 6), n=24, sag=1.0)
    sc.lights.append(dict(pos=(0, 7, 0), col='#ffb0e0', I=1.4, r=12))
    sc.lights.append(dict(pos=(-12, 7, -4), col='#a0c0ff', I=1.0, r=10))
    sc.lights.append(dict(pos=(12, 7, -4), col='#ffd890', I=1.0, r=10))
    if stage:
        sc.add(box((0, 0.8, -12), (14, 1.6, 6), '#5a3a2a', mat='wood'), box((0, 6.0, -14.8), (14, 9, 0.4), '#2a1a4a'))
        bn = box((0, 9.2, -14.5), (10, 1.8, 0.1), '#ffd24a', nocast=True)
        bn.tex['pz'] = (sign_img('SUMMER BASH', (255, 210, 74), (200, 40, 120)), True); sc.add(bn)
        for sx in (-6.5, 6.5):
            sc.add(box((sx, 3.6, -12), (1.6, 4.0, 1.6), '#1a1a1a', rl=1))
            pulse = 1 + 0.08 * abs(math.sin(t * 8))
            sc.add(box((sx, 3.2, -11.15), (1.1 * pulse, 1.1 * pulse, 0.1), '#333', rl=4))
        for k, sx in enumerate((-5, -2, 2, 5)):
            sc.add(box((sx, 10.4, -13.5), (0.6, 0.6, 0.6), ['#ff5ab4', '#5ab4ff', '#ffd24a', '#5aff7a'][k], emit=2.5, shade=False, rl=3, nocast=True))
    if crowd:
        rr = random.Random(3)
        for k in range(n):
            row = k % ncrowd_rows
            x = -11 + (k // ncrowd_rows) * (22 / max(1, n // ncrowd_rows)) + rr.uniform(-0.6, 0.6)
            z = -5 + row * 3.2 + rr.uniform(-0.5, 0.5)
            yw = rr.uniform(-25, 25) + (180 if look_at == 'back' else 0)
            if isinstance(look_at, tuple):
                yw = math.degrees(math.atan2(look_at[0] - x, look_at[1] - z))
            dancer(sc, (x, 0, z), k, t, yaw=yw, face=crowd_face, cheer=cheer)
    confetti(sc, t, (0, 0, 0), area=14, n=70)

def dj_booth(sc, pos, t):
    x, y, z = pos
    sc.add(box((x, y + 1.3, z), (5, 2.6, 2), '#1a1a22', rl=1))
    for dx in (-1.3, 1.3):
        sc.add(box((x + dx, y + 2.65, z), (1.4, 0.1, 1.4), '#222'), box((x + dx, y + 2.72, z), (1.1, 0.04, 1.1), '#5af0ff', emit=1.5 * (0.6 + 0.4 * abs(math.sin(t * 8))), shade=False, rl=4, R=rot(t * 300)))
    sc.add(box((x, y + 1.3, z + 1.02), (4.6, 0.3, 0.05), '#ff3ac8', emit=2, shade=False))
    sc.lights.append(dict(pos=(x, y + 4, z + 2), col='#ff5af0', I=1.5, r=6))

def bounce_house(sc, pos, t):
    x, y, z = pos
    sq = 1 + 0.06 * math.sin(t * 7)
    base = M4((x, y, z), np.diag([1 / math.sqrt(sq), sq, 1 / math.sqrt(sq)]))
    sc.add(box((0, 2.5, 0), (8, 5, 8), '#ff5a5a', parent=base, rl=2))
    sc.add(box((0, 2.0, 4.05), (4, 3.6, 0.2), '#2a1a4a', parent=base, rl=2))
    for cx in (-4, 4):
        for cz in (-4, 4):
            sc.add(box((cx, 4, cz), (1.8, 8, 1.8), ['#5ab4ff', '#ffd24a'][(cx > 0) ^ (cz > 0)], parent=base, rl=3))
            sc.add(box((cx, 8.4, cz), (2.0, 1.4, 2.0), '#ff7af0', parent=base, rl=4))
    sc.add(box((0, 5.6, 0), (8.6, 0.8, 8.6), '#ffd24a', parent=base, rl=2))

def foam(sc, pos, t):
    rr = random.Random(9)
    x, y, z = pos
    sc.add(box((x - 4, 1.2, z), (1.4, 2.4, 1.4), '#5a5a6a', rl=1), box((x - 3.2, 2.2, z), (1.2, 0.5, 0.5), '#5a5a6a', rl=1))
    for k in range(40):
        ph = (t * 0.6 + k / 40) % 1.0
        px = x - 2.5 + ph * 7 + rr.uniform(-1, 1); py = y + 0.5 + rr.uniform(0, 3.2) * (0.3 + ph); pz = z + rr.uniform(-2.5, 2.5)
        s_ = 0.6 + rr.random() * 1.0
        sc.add(box((px, py, pz), (s_, s_ * 0.8, s_), '#ffffff', rl=4, emit=0.15, nocast=True))

# ---------- pizza shop ----------
def shop_interior(sc, t, window_party=True, stack_h=0, flying=0.0, ceiling_hole=False):
    sc.sky = (C('#1a1450'), C('#5a3a9a'))
    sc.ambient = C((0.4, 0.37, 0.36)); sc.suncol = C((0.26, 0.23, 0.19)); sc.sun = np.array([0.3, -1.0, -0.4])
    room(sc, 18, 16, 9, '#c86a4a', '#a8743f', floor_tile=1.0, floor_j=0.08, ceil='#f4ecd8', floor_mat='wood')
    # back wall: brick lower band + window to the party
    sc.add(box((0, 1.6, -7.85), (18, 3.2, 0.25), '#8a3a2a', mat='tile'))
    if window_party:
        sc.add(box((0, 5.6, -7.95), (9, 4, 0.1), '#2a1a5a', emit=0.6, shade=False, nocast=True))
        rr = random.Random(5)
        for k in range(14):
            sc.add(box((rr.uniform(-4.2, 4.2), rr.uniform(4.0, 7.4), -7.9), (0.22, 0.22, 0.05), rr.choice(['#ff5ab4', '#ffd24a', '#5ab4ff', '#5aff7a']), emit=2.5 * (0.6 + 0.4 * math.sin(t * 4 + k)), shade=False, nocast=True))
        for k in range(3):
            age = ((t + k * 0.6) % 1.8) / 1.8
            cx, cy = (-2.5 + k * 2.5, 6.5 - k * 0.5)
            for j in range(12):
                a = j / 12 * 2 * math.pi; r = 1.4 * eout(age / 0.6)
                sc.add(box((cx + r * math.cos(a), cy + r * math.sin(a), -7.88), (0.15, 0.15, 0.04), ['#ff5ab4', '#ffd24a', '#5af0ff'][k], emit=3 * (1 - age), shade=False, nocast=True))
        for fx in (-4.6, 0, 4.6):
            sc.add(box((fx, 5.6, -7.82), (0.25, 4.2, 0.2), '#f4f4f4', nocast=True))
        sc.add(box((0, 3.5, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True), box((0, 7.7, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True))
    # pizza oven (right)
    sc.add(box((6.5, 1.5, -5.5), (4.5, 3, 4), '#7a4a3a', mat='tile'), box((6.5, 4.0, -5.5), (4.2, 2.4, 3.8), '#9a5a3a', rl=4))
    fl = 1 + 0.2 * math.sin(t * 17)
    sc.add(box((6.5, 3.5, -3.55), (1.8, 1.1, 0.1), '#ff7a20', emit=2.5 * fl, shade=False, rl=2, nocast=True))
    sc.lights.append(dict(pos=(6.5, 3.6, -2.5), col='#ff8a30', I=1.6 * fl, r=5))
    # menu board + logo
    mb = box((-5.5, 6.6, -7.7), (4.5, 2.4, 0.1), '#222', nocast=True)
    mb.tex['pz'] = (sign_img('SLICE TOWN', (40, 30, 30), (255, 210, 80), size=(900, 480), fs=150), True); sc.add(mb)
    # ceiling lamps
    for x in (-4, 4):
        ceiling_lamp(sc, (x, 9, -1), on=True)
        sc.lights.append(dict(pos=(x, 7.8, -1), col='#ffe8c0', I=0.6, r=7))
    # prep table where the kid works
    sc.add(box((0, 2.3, 0), (8, 0.25, 4), '#9a6a40', mat='wood'))
    for lx in (-3.6, 3.6):
        for lz in (-1.7, 1.7):
            sc.add(box((lx, 1.1, lz), (0.25, 2.2, 0.25), '#888'))
    # flat box pile on table
    for k in range(6):
        sc.add(box((-2.6, 2.48 + k * 0.07, -0.2), (3.0, 0.06, 3.0), '#c08a50' if k % 2 else CARD))
    # stack of finished boxes
    if stack_h:
        pbox_stack(sc, (2.9, 2.43, -0.2), stack_h, wobble=0.04, t=t)
    # big alarm clock
    ck = box((3.8, 3.3, 1.4), (1.6, 1.6, 0.6), '#d42a2a', rl=3, R=rot(-20)); ck.tex['pz'] = (clock_img(round((t * 0.5 % 1) * 24) / 24), False); sc.add(ck)

def shop_exterior(sc, t, through_roof=0.0, bird=0.0):
    night(sc, amb=(0.55, 0.52, 0.74), sun=(0.35, 0.33, 0.55))
    sc.sky = (C('#2a2070'), C('#9a6ab0')); sc.fog = C('#4a3a7a'); sc.fogd = 0.008
    sc.add(box((0, -0.5, 0), (160, 1, 160), '#5a8a4a', bg=True, mat='grass'))
    sc.add(box((0, 0.02, 10), (160, 0.08, 10), '#3a3a48', bg=True, mat='asphalt'))
    for x in range(-40, 41, 5):
        sc.add(box((x, 0.08, 10), (2.4, 0.03, 0.3), '#ffffff', bg=True))
    sc.add(box((0, 0.12, 3.5), (160, 0.24, 4), '#b8b0c0', bg=True, mat='tile'))
    # building
    sc.add(box((0, 5, -4), (20, 10, 10), '#2fa8a0', mat='wood'))
    sc.add(box((0, 10.2, -4), (20.6, 0.5, 10.6), '#e8e0d0'))
    sc.add(box((0, 1.0, 1.05), (20.2, 2.0, 0.2), '#c84a3a', mat='tile'))
    sg = box((0, 8.4, 1.1), (12, 2.6, 0.3), '#fff4e0'); sg.tex['pz'] = (sign_img('SLICE TOWN', (255, 244, 224), (220, 60, 50)), True); sc.add(sg)
    lg = box((-8, 8.4, 1.2), (2.6, 2.6, 0.3), '#c42a2a', rl=4); lg.tex['pz'] = (logo_img(), True); sc.add(lg)
    for k in range(10):
        sc.add(box((-9 + k * 2, 6.2, 1.9), (2.0, 0.3, 1.8), '#ffffff' if k % 2 else '#d42a2a', R=rot(0, 20, 0)))
    sc.add(box((-3.5, 3.6, 1.06), (5, 4, 0.1), '#ffe0a0', emit=1.2, shade=False, nocast=True), box((5, 3.0, 1.06), (3, 5.2, 0.1), '#ffe0a0', emit=1.0, shade=False, nocast=True))
    nh = box((-3.5, 2.6, 1.15), (2.2, 1.0, 0.05), '#fff'); nh.tex['pz'] = (sign_img('NOW HIRING', (255, 255, 255), (200, 30, 30), size=(600, 260), fs=110), False); sc.add(nh)
    sc.lights.append(dict(pos=(0, 4, 4), col='#ffd890', I=1.4, r=9))
    if through_roof > 0:
        hgt = 10 + through_roof * 26
        n = int(hgt / 0.52)
        for k in range(20, n):
            pbox(sc, (1.5 + math.sin(k * 0.4) * 0.15, k * 0.52, -4), k * 7 % 11 - 5)
        rr = random.Random(2)
        for j in range(18):
            u = min(1, through_roof * 3)
            sc.add(box((1.5 + rr.uniform(-3, 3) * (1 + u), 10.5 + rr.uniform(0, 3) * u, -4 + rr.uniform(-3, 3)), (0.6, 0.15, 0.5), '#e8e0d0', R=rot(rr.uniform(0, 180), rr.uniform(-40, 40), 0)))
        if bird > 0:
            top = n * 0.52 + 0.3
            by = top + 6 * (1 - ease(bird))
            flap = math.sin(TIME[0] * 30) * 35 * (1 - ease(bird) * 0.8)
            sc.add(box((1.5, by + 0.5, -4), (0.7, 0.7, 1.1), '#3a8ae0', rl=3), box((1.5, by + 1.05, -3.6), (0.55, 0.55, 0.55), '#3a8ae0', rl=4),
                   box((1.5, by + 1.05, -3.25), (0.2, 0.12, 0.3), '#ffb020'),
                   box((1.05, by + 0.6, -4), (0.7, 0.08, 0.6), '#2a6ac0', R=rot(0, 0, flap)), box((1.95, by + 0.6, -4), (0.7, 0.08, 0.6), '#2a6ac0', R=rot(0, 0, -flap)))

# ================= SUMMER BASH v2: sunset beach park =================
def beach_extra(k):
    def ex(out, base, hm, arms):
        if k % 2 == 0:
            out.append(box((0, 0.72, 0.67), (1.25, 0.28, 0.08), '#111', parent=hm, rl=1))
            out.append(box((0, 0.84, 0.66), (1.3, 0.06, 0.06), '#222', parent=hm))
        cols = ['#ff5ab4', '#ffd24a', '#ff7a3a', '#c05aff']
        for j in range(10):
            a = j / 10 * 2 * math.pi
            out.append(box((math.sin(a) * 0.75, 3.95 - abs(math.cos(a)) * 0.05, math.cos(a) * 0.45 + 0.05), (0.32, 0.22, 0.22), cols[(j + k) % 4], parent=base, rl=4))
    return ex

def dancer(sc, pos, k, t, yaw=0, hat=True, face='grin', cheer=False):
    ph = k * 1.3
    b = abs(math.sin(t * 6 + ph)) * 0.35
    if cheer:
        pose = dict(ra=135, la=135, re=10 + 15 * math.sin(t * 9 + ph), le=10, y=b, hy=10 * math.sin(t * 3 + ph))
    else:
        pose = dict(ra=40 + 60 * abs(math.sin(t * 6 + ph)), la=40 + 60 * abs(math.cos(t * 6 + ph)), re=60, le=60, y=b, lk=20 * b, rk=20 * b, hy=15 * math.sin(t * 3 + ph))
    o = KIDS[k % len(KIDS)]
    character(sc, pos, yaw=yaw, pose=pose, face=face, extra=beach_extra(k), **o)

def dusk_of(t):
    return ease((t - 73.0) / 5.0)

def palm(sc, pos, h=9, lean=12, t=0.0):
    base = M4(pos, rot(pos[0] * 7 % 360, 0, lean))
    for k in range(7):
        sc.add(box((0, k * h / 7 + 0.5, 0), (0.75 - k * 0.04, h / 7 + 0.05, 0.75 - k * 0.04), '#8a6a3a' if k % 2 else '#7a5a30', parent=base, rl=1))
    top = base @ M4((0, h + 0.3, 0))
    for j in range(7):
        a = j / 7 * 360 + math.sin(t * 1.5 + j) * 4
        sc.add(box((0, 0, 2.0), (1.2, 0.12, 4.2), '#2f9a3a', parent=top @ M4((0, 0, 0), rot(a, 25, 0)), rl=1))
    sc.add(box((0.3, -0.2, 0.2), (0.5, 0.5, 0.5), '#5a3a1a', parent=top, rl=4), box((-0.3, -0.25, -0.1), (0.5, 0.5, 0.5), '#5a3a1a', parent=top, rl=4))

def umbrella(sc, pos, c1, c2):
    x, y, z = pos
    sc.add(box((x, y + 2.2, z), (0.15, 4.4, 0.15), '#eee'))
    sc.add(box((x, y + 4.4, z), (4.2, 0.35, 4.2), c1, rl=4), box((x, y + 4.62, z), (2.6, 0.3, 2.6), c2, rl=4), box((x, y + 4.8, z), (1.0, 0.25, 1.0), c1, rl=4))
    sc.add(box((x + 1.5, y + 0.03, z + 1.2), (1.6, 0.04, 3.0), c2, bg=True))

def ferris(sc, pos, t, r=12):
    x, y, z = pos
    sc.add(box((x - 4, y + r / 2, z), (0.5, r + 2, 0.5), '#ddd', R=rot(0, 0, -18)), box((x + 4, y + r / 2, z), (0.5, r + 2, 0.5), '#ddd', R=rot(0, 0, 18)))
    cy = y + r + 1
    cols = ['#ff5a5a', '#ffd24a', '#5ab4ff', '#5aff7a', '#ff7af0', '#ffffff']
    for k in range(12):
        a = k / 12 * 2 * math.pi + t * 0.25
        sc.add(box((x + math.cos(a) * r / 2, cy + math.sin(a) * r / 2, z), (0.2, r, 0.2), '#e8e8e8', R=rot(0, 0, math.degrees(a) + 90)))
        cx_, cy_ = x + math.cos(a) * r, cy + math.sin(a) * r
        sc.add(box((cx_, cy_ - 0.8, z), (1.4, 1.4, 1.4), cols[k % 6], rl=2, emit=0.6))
        sc.add(box((cx_, cy_, z + 0.2), (0.35, 0.35, 0.35), '#fff6c0', emit=2.5, shade=False, rl=4, nocast=True))
    for k in range(36):
        a = k / 36 * 2 * math.pi + t * 0.25
        sc.add(box((x + math.cos(a) * r, cy + math.sin(a) * r, z), (1.1, 0.25, 0.25), '#f0f0f0', R=rot(0, 0, math.degrees(a) + 90)))

def tiki(sc, pos, t):
    x, y, z = pos
    sc.add(box((x, y + 2, z), (0.3, 4, 0.3), '#6a4a2a'), box((x, y + 4.2, z), (0.6, 0.5, 0.6), '#4a3a2a', rl=1))
    fl = 1 + 0.2 * math.sin(t * 15 + x)
    sc.add(box((x, y + 4.75 + 0.05 * fl, z), (0.35 * fl, 0.6 * fl, 0.35 * fl), '#ff8a20', emit=2.5, shade=False, rl=4, nocast=True))

def beach_ball(sc, pos, t, k):
    x, y, z = pos
    yy = y + 1 + abs(math.sin(t * 2.5 + k)) * 5
    R = rot(t * 120 + k * 50, t * 80, 0)
    sc.add(box((x, yy, z), (1.0, 1.0, 1.0), '#ffffff', R=R, rl=4), box((x, yy, z), (1.02, 0.36, 1.02), '#ff4a4a', R=R, rl=4), box((x, yy, z), (0.36, 1.03, 1.03), '#3a8aff', R=R, rl=4))

def ice_cream_truck(sc, pos, yaw=0):
    base = M4(pos, rot(yaw))
    sc.add(box((0, 2.6, 0), (4.6, 4.0, 8.5), '#ffffff', parent=base, rl=1), box((0, 1.0, 0), (4.65, 0.6, 8.55), '#ff7ab8', parent=base))
    sc.add(box((2.33, 3.0, 0.5), (0.05, 1.8, 3.5), '#2a1a3a', parent=base))
    cone = box((0, 5.6, 1), (0.9, 1.4, 0.9), '#e8b060', parent=base, rl=2); sc.add(cone)
    sc.add(box((0, 6.6, 1), (1.4, 1.2, 1.4), '#ffb0d8', parent=base, rl=4), box((0, 7.3, 1), (0.4, 0.4, 0.4), '#d42a2a', parent=base, rl=4))
    for wx in (-2.2, 2.2):
        for wz in (-2.8, 2.8):
            sc.add(box((wx, 0.7, wz), (0.6, 1.4, 1.4), '#151515', parent=base))

def summer_park(sc, t, crowd=True, stage=True, n=14, crowd_face='grin', look_at=None, cheer=False, ncrowd_rows=2):
    dk = dusk_of(t)
    top = lerp(C('#4a8ae8'), C('#1a2058'), dk); bot = lerp(C('#ffb36a'), C('#ff6a4a'), dk)
    sc.sky = (top, bot); sc.stars = 1.0 * max(0, dk - 0.4) / 0.6
    sc.ambient = C(lerp((0.62, 0.55, 0.5), (0.42, 0.38, 0.55), dk)); sc.suncol = C(lerp((0.75, 0.55, 0.35), (0.35, 0.22, 0.25), dk))
    sc.sun = np.array([0.7, -0.45, 0.5]); sc.fog = C(lerp((1.0, 0.75, 0.55), (0.5, 0.35, 0.45), dk)); sc.fogd = 0.006
    sc.add(box((-45, 9 - 4 * dk, -120), (16, 16, 1), lerp(C('#fff0a0'), C('#ff7a3a'), dk), emit=2.6, shade=False, rl=4, nocast=True))
    sc.add(box((0, -0.5, -10), (200, 1, 60), '#5aa84a', bg=True, mat='grass'))
    sc.add(box((0, -0.45, -48), (200, 1, 16), '#f0d8a0', bg=True, mat='concrete'))
    sc.add(box((0, -0.55, -120), (300, 1, 130), lerp(C('#2a8ad8'), C('#1a3a7a'), dk), bg=True, emit=0.25, shade=False))
    rr = random.Random(4)
    for k in range(24):
        sc.add(box((rr.uniform(-60, 60), 0.0, rr.uniform(-110, -60)), (rr.uniform(1, 3), 0.05, 0.15), '#ffe8b0', emit=1.5 * (0.5 + 0.5 * math.sin(t * 3 + k)), shade=False, nocast=True, bg=True))
    for k, (px, pz) in enumerate(((-24, -16), (-16, -30), (18, -18), (26, -34), (-30, -6), (32, -4), (8, -38))):
        palm(sc, (px, 0, pz), h=8 + k % 3 * 1.5, lean=8 + k * 3, t=t)
    for k, (ux, uz) in enumerate(((-20, -44), (-10, -46), (12, -45), (22, -43))):
        umbrella(sc, (ux, -0.05, uz), ['#ff4a4a', '#3a8aff', '#ffd24a', '#5aff7a'][k], '#ffffff')
    ferris(sc, (-34, 0, -52), t)
    ice_cream_truck(sc, (19, 0, -12), yaw=-30)
    for k, x in enumerate((-16, -8, 8, 16)):
        tiki(sc, (x, 0, 7), t)
    for k, (bx, bz) in enumerate(((-6, 3), (7, 1), (-12, -2))):
        beach_ball(sc, (bx, 0, bz), t, k)
    sc.lights.append(dict(pos=(0, 8, 2), col='#ffb070', I=0.9, r=14))
    if dk > 0.2: sc.lights.append(dict(pos=(0, 6, 6), col='#ff9a40', I=1.2 * dk, r=12))
    if stage:
        sc.add(box((0, 0.8, -12), (14, 1.6, 6), '#b07a40', mat='wood'), box((0, 6.0, -14.8), (14, 9, 0.4), '#2a6ab0'))
        for sx in (-6.8, 6.8):
            sc.add(box((sx, 5.6, -12.5), (0.6, 8, 0.6), '#8a6a3a'))
        sc.add(box((0, 10.0, -12.5), (15, 0.6, 7), '#d8b060', rl=1), box((0, 10.5, -12.5), (13, 0.5, 6), '#c8a050', rl=1))
        bn = box((0, 8.6, -14.5), (10, 1.8, 0.1), '#ffd24a', nocast=True)
        bn.tex['pz'] = (sign_img('SUMMER BASH', (255, 140, 60), (255, 255, 255)), True); sc.add(bn)
        for sx in (-5.5, 5.5):
            sc.add(box((sx, 3.6, -12), (1.6, 4.0, 1.6), '#1a1a1a', rl=1))
            pulse = 1 + 0.08 * abs(math.sin(t * 8))
            sc.add(box((sx, 3.2, -11.15), (1.1 * pulse, 1.1 * pulse, 0.1), '#333', rl=4))
        for k, sx in enumerate((-4.5, -1.5, 1.5, 4.5)):
            sc.add(box((sx, 2.1, -9.5), (1.2, 2.2, 0.15), ['#ff5ab4', '#5ab4ff', '#ffd24a', '#5aff7a'][k], R=rot(0, -10, 0), rl=2))
    if crowd:
        rr = random.Random(3)
        for k in range(n):
            row = k % ncrowd_rows
            x = -11 + (k // ncrowd_rows) * (22 / max(1, n // ncrowd_rows)) + rr.uniform(-0.6, 0.6)
            z = -5 + row * 3.2 + rr.uniform(-0.5, 0.5)
            yw = rr.uniform(-25, 25) + (180 if look_at == 'back' else 0)
            if isinstance(look_at, tuple):
                yw = math.degrees(math.atan2(look_at[0] - x, look_at[1] - z))
            dancer(sc, (x, 0, z), k, t, yaw=yw, face=crowd_face, cheer=cheer)

party_street = summer_park

_shop_interior_v1 = shop_interior
def shop_interior(sc, t, window_party=True, stack_h=0, flying=0.0, ceiling_hole=False):
    _shop_interior_v1(sc, t, window_party=False, stack_h=stack_h)
    # sunset view through the window with the beach park ferris wheel
    sc.add(box((0, 6.6, -7.97), (9, 2.0, 0.1), '#ff9a6a', emit=1.0, shade=False, nocast=True),
           box((0, 4.6, -7.97), (9, 2.0, 0.1), '#ffc07a', emit=1.1, shade=False, nocast=True),
           box((2.6, 4.4, -7.93), (1.4, 1.4, 0.05), '#fff2a0', emit=2.0, shade=False, rl=4, nocast=True))
    for k in range(8):
        a = k / 8 * 2 * math.pi + t * 0.25
        sc.add(box((-2.4 + math.cos(a) * 1.3, 5.8 + math.sin(a) * 1.3, -7.9), (0.25, 0.25, 0.04), ['#ff5a5a', '#ffd24a', '#5ab4ff', '#ffffff'][k % 4], emit=2.5, shade=False, nocast=True))
    for fx in (-4.6, 0, 4.6):
        sc.add(box((fx, 5.6, -7.82), (0.25, 4.2, 0.2), '#f4f4f4', nocast=True))
    sc.add(box((0, 3.5, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True), box((0, 7.7, -7.8), (9.4, 0.25, 0.3), '#f4f4f4', nocast=True))

_shop_exterior_v1 = shop_exterior
def shop_exterior(sc, t, through_roof=0.0, bird=0.0):
    _shop_exterior_v1(sc, t, through_roof, bird)
    sc.sky = (C('#4a8ae8'), C('#ffb36a')); sc.stars = 0.0
    sc.ambient = C((0.62, 0.55, 0.5)); sc.suncol = C((0.75, 0.55, 0.35)); sc.sun = np.array([0.7, -0.45, 0.5])
    sc.fog = C((1.0, 0.75, 0.55)); sc.fogd = 0.006

# ================= box v2: each flap folds on its own, with a pizza inside =================
def pizza(sc, base, y, D):
    for k in range(4):
        sc.add(box((0, y + 0.06, 0), (D, 0.12, D * 0.42), '#d8963e', parent=base @ M4((0, 0, 0), rot(k * 45)), rl=1))
    for k in range(4):
        sc.add(box((0, y + 0.11, 0), (D * 0.86, 0.06, D * 0.36), '#ffcf4a', parent=base @ M4((0, 0, 0), rot(k * 45 + 22.5)), rl=1))
    for (dx, dz) in ((0.0, 0.0), (0.42, 0.18), (-0.38, 0.26), (0.2, -0.42), (-0.3, -0.3), (0.5, -0.12), (-0.05, 0.5)):
        sc.add(box((dx * D * 0.8, y + 0.15, dz * D * 0.8), (D * 0.16, 0.04, D * 0.16), '#b8322a', parent=base, rl=4))
        sc.add(box((dx * D * 0.8 + D * 0.05, y + 0.15, dz * D * 0.8), (D * 0.07, 0.042, D * 0.1), '#b8322a', parent=base, rl=2))
    for (dx, dz) in ((0.25, 0.35), (-0.2, 0.05), (0.1, -0.25)):
        sc.add(box((dx * D, y + 0.16, dz * D), (0.08, 0.03, 0.16), '#3a8a2a', parent=base, R=rot(dx * 400)))

def pbox_fold2(sc, pos, P, yaw=0.0, s=0.72, with_pizza=True):
    """P: dict of 0..1 for L, R, F (near), B (far), tL, tR (corner tucks), lid. Lid hinges on the far edge."""
    g = lambda k: ease(P.get(k, 0.0))
    base = M4(pos, rot(yaw))
    S = 3.0 * s; h = 0.68 * s; t = 0.06
    WALL = '#a8662e'
    sc.add(box((0, t / 2, 0), (S, t, S), CARD, parent=base))
    if with_pizza: pizza(sc, base, t, S * 0.82)
    # left/right walls hinged on x edges
    lm = base @ M4((-S / 2, 0, 0), rot(0, 0, -90 * g('L')))
    sc.add(box((-h / 2, t / 2, 0), (h, t, S), WALL, parent=lm))
    rm = base @ M4((S / 2, 0, 0), rot(0, 0, 90 * g('R')))
    sc.add(box((h / 2, t / 2, 0), (h, t, S), WALL, parent=rm))
    # near (F, -z) and far (B, +z) walls
    fm = base @ M4((0, 0, -S / 2), rot(0, 90 * g('F'), 0))
    sc.add(box((0, t / 2, -h / 2), (S, t, h), WALL, parent=fm))
    bm = base @ M4((0, 0, S / 2), rot(0, -90 * g('B'), 0))
    sc.add(box((0, t / 2, h / 2), (S, t, h), WALL, parent=bm))
    # corner tucks on the near corners
    for sx, key in ((-1, 'tL'), (1, 'tR')):
        a2 = 90 * g(key)
        tm = base @ M4((sx * S / 2, h * 0.5 * max(g('L'), g('R')), -S / 2 + 0.05), rot(sx * (90 - a2), 0, 0))
        sc.add(box((-sx * 0.3 * s / 0.72, t / 2, 0), (0.6 * s / 0.72, t * 0.9, h * 0.9), '#9a6a36', parent=tm))
    # lid hinged on the far top edge, flips over toward the kid
    a3 = 180 - 180 * g('lid')
    lidb = base @ M4((0, h * g('B'), S / 2), rot(0, a3, 0))
    lid = box((0, t / 2, -S / 2), (S, t, S), CARD, parent=lidb)
    if 'logo180' not in _tx: _tx['logo180'] = logo_img().rotate(180)
    lid.tex['py'] = (_tx['logo180'], False)
    sc.add(lid)
    # tuck flap on the lid's free edge: folds down over the front wall
    ltm = lidb @ M4((0, 0, -S - 0.02), rot(0, -92 * g('lt'), 0))
    sc.add(box((0, -t / 2, -h * 0.42), (S * 0.96, t, h * 0.84), WALL, parent=ltm))

def pbox_fold(sc, pos, f1, f2, f3, yaw=0.0, s=0.72):
    pbox_fold2(sc, pos, dict(L=f1, R=f1, F=f1, B=f1, tL=f2, tR=f2, lid=f3), yaw=0.0, s=s)

# ================= fancy Slice Town interior =================
def neon_img(text, col):
    k = ('neon', text, col)
    if k in _tx: return _tx[k]
    im = Image.new('RGBA', (1024, 300), (16, 8, 14, 255)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_ANTON, 190)
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.text((512, 150), text, font=f, fill=col + (255,), anchor='mm', stroke_width=18, stroke_fill=col + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    im = Image.alpha_composite(im, glow); d = ImageDraw.Draw(im)
    d.text((512, 150), text, font=f, fill=(255, 245, 250), anchor='mm', stroke_width=5, stroke_fill=col)
    _tx[k] = im; return im

def menu_img():
    if 'menu' in _tx: return _tx['menu']
    im = Image.new('RGBA', (600, 760), (30, 34, 30, 255)); d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 592, 752), outline=(150, 100, 60), width=14)
    fa = ImageFont.truetype(FONT_ANTON, 64); fb = ImageFont.truetype(FONT_POPPINS, 38)
    d.text((300, 70), 'MENU', font=fa, fill=(255, 220, 120), anchor='mm')
    for i, (n, pr) in enumerate((('Cheese', '$8'), ('Pepperoni', '$10'), ('Supreme', '$12'), ('Hawaiian', '$11'), ('Meat Lovers', '$13'), ('HUSS Special', '$99'))):
        y = 170 + i * 92
        d.text((50, y), n, font=fb, fill=(240, 240, 230)); d.text((550, y), pr, font=fb, fill=(255, 200, 90), anchor='ra')
    _tx['menu'] = im; return im

def shop_fancy(sc, t):
    # checkered floor over the wood
    sc.add(box((0, 0.015, 0), (18, 0.03, 16), '#ffffff', bg=True, mat='checker'))
    # neon sign on the back wall (left of window)
    nz = box((-5.6, 6.7, -7.65), (5.0, 1.5, 0.08), '#ff3a8a', nocast=True)
    nz.tex['pz'] = (neon_img('SLICE TOWN', (255, 50, 140)), True); sc.add(nz)
    sc.lights.append(dict(pos=(-5.6, 6.6, -6.4), col='#ff3a8a', I=0.55, r=3.5))
    # chalkboard menu on the right side wall
    mb = box((8.85, 6.2, -1.2), (0.12, 3.0, 2.4), '#2a2a2a', nocast=True)
    mb.tex['nx'] = (menu_img(), False); sc.add(mb)
    sc.add(box((8.9, 6.2, -1.2), (0.12, 3.3, 2.7), '#6a4428'))
    # italian flag bunting across the ceiling
    cols = ['#2a9a3a', '#ffffff', '#d42a2a']
    for row, zz in enumerate((-4.5, 2.5)):
        for k in range(18):
            x = -8.5 + k; y = 8.5 - 0.6 * math.sin(k / 17 * math.pi)
            sc.add(box((x, y, zz), (0.55, 0.6, 0.04), cols[k % 3], nocast=True, R=rot(0, 0, 180)))
    # pendant lamps over the prep table
    for x in (-2.5, 0, 2.5):
        sc.add(box((x, 7.9, 0.0), (0.05, 2.2, 0.05), '#222', nocast=True),
               box((x, 6.7, 0.0), (1.1, 0.5, 1.1), '#1f6a4a', rl=3, nocast=True),
               box((x, 6.42, 0.0), (0.5, 0.2, 0.5), '#fff2c8', emit=2.5, shade=False, rl=4, nocast=True))
    sc.lights.append(dict(pos=(0, 6.0, 0.2), col='#ffe2b0', I=0.4, r=4))
    # glass display case with pizzas (left side)
    sc.add(box((7.6, 1.3, 2.2), (2.2, 2.6, 4.0), '#7a4a2a', mat='wood'), box((7.6, 2.65, 2.2), (2.3, 0.1, 4.1), '#d8c8a8'))
    sc.add(box((7.6, 3.35, 2.2), (2.0, 1.3, 3.8), '#bfe6ff', emit=0.15, shade=False, nocast=True))
    for k, z in enumerate((1.1, 3.3)):
        pizza(sc, M4((7.6, 2.72, z)), 0.0, 1.5)
    # shelves with tomato cans and olive oil
    for y in (5.0, 6.2):
        sc.add(box((8.6, y, -4.8), (0.6, 0.12, 3.0), '#6a4428'))
        for k in range(5):
            sc.add(box((8.6, y + 0.32, -6.0 + k * 0.6), (0.4, 0.5, 0.4), ['#d42a2a', '#2a8a3a', '#ffd24a'][k % 3], rl=2))
    # plants
    for (px, pz) in ((-8.0, -6.8), (8.0, 6.5)):
        plant(sc, (px, 0, pz), 1.3)
    # framed pizza photos
    for k, z in enumerate((-2.5, 3.0)):
        fr = box((-8.9, 5.4, z), (0.1, 1.6, 1.6), '#ffffff', nocast=True); fr.tex['px'] = (poster_img(['NY', 'ROMA'][k], k + 2), False); sc.add(fr)
        sc.add(box((-8.95, 5.4, z), (0.12, 1.85, 1.85), '#c8a050'))

_shop_interior_v2 = shop_interior
def shop_interior(sc, t, window_party=True, stack_h=0, flying=0.0, ceiling_hole=False):
    _shop_interior_v2(sc, t, stack_h=stack_h)
    shop_fancy(sc, t)

_shop_exterior_v2 = shop_exterior
def shop_exterior(sc, t, through_roof=0.0, bird=0.0):
    _shop_exterior_v2(sc, t, through_roof, bird)
    nz = box((0, 11.6, 1.2), (8, 1.6, 0.2), '#ff3a8a', nocast=True); nz.tex['pz'] = (neon_img('OPEN 24/7', (255, 60, 140)), True); sc.add(nz)
    for x in (-7, 7):
        sc.add(box((x, 1.5, 5.0), (2.4, 0.15, 2.4), '#ffffff', rl=2), box((x, 0.75, 5.0), (0.2, 1.5, 0.2), '#333'))
        sc.add(box((x, 2.2, 5.0), (0.1, 3.0, 0.1), '#eee'), box((x, 3.8, 5.0), (3.2, 0.3, 3.2), '#d42a2a', rl=4), box((x, 4.0, 5.0), (2.0, 0.25, 2.0), '#ffffff', rl=4))
    for x in (-9.5, 9.5):
        plant(sc, (x, 0.24, 2.2), 1.2)
