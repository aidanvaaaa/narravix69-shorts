"""Gold-and-glass downtown (New York canyon meets San Francisco) plus wall decor for indoor sets.

lux_city: a street running along z, lined with colourful storefronts (deli, bodega, jewelry, sneakers...),
neon signs, posters, gold street lamps and yellow taxis, with gold/blue glass towers behind and a red
suspension bridge on the horizon. decorate(): posters and LED strips for the indoor rooms.
"""
import math
import random

import numpy as np

from .engine import box, rot, C
from .sets import poster, plant, car
from .hsets import neon_img

GOLD = '#d8b04a'
SHOPS = [('DELI', (255, 200, 60)), ('BODEGA', (255, 90, 90)), ('JEWELRY', (255, 215, 90)), ('SNEAKERS', (90, 220, 255)),
         ('PIZZA', (255, 140, 60)), ('CAFE', (255, 120, 200)), ('NAILS', (255, 120, 220)), ('BARBER', (120, 200, 255)),
         ('24K GOLD', (255, 210, 80)), ('LUXE', (200, 160, 255)), ('BAGELS', (255, 190, 90)), ('DRIP', (120, 255, 200))]
FACADES = ['#b8423a', '#e8dcc4', '#2f7f86', '#d9a43a', '#e889a8', '#2c3a66', '#7a3a5a', '#f2f0ea', '#4a7a4a', '#c86a3a']
WORDS = ['STAY GOLD', 'DRIP', 'NYC', 'LEGEND', 'NO DAYS OFF', 'BOSS', 'DREAM BIG', '24K', 'HUSTLE', 'FLY', 'ICON', 'LUXE']


def lux_city(sc, t, night=False):
    rr = random.Random(77)
    if night:
        sc.sky = (C('#070b1c'), C('#24305a')); sc.ambient = C((0.3, 0.3, 0.42)); sc.suncol = C((0.12, 0.13, 0.2))
        sc.fog = C((0.14, 0.14, 0.26)); sc.fogd = 0.007; sc.stars = 0.25
    else:  # golden hour
        sc.sky = (C('#ff9d4a'), C('#ffe7b8')); sc.ambient = C((0.62, 0.52, 0.42)); sc.suncol = C((0.85, 0.6, 0.32))
        sc.fog = C((1.0, 0.82, 0.6)); sc.fogd = 0.005
    sc.sun = np.array([0.55, -0.45, -0.7])
    lw = 1.6 if night else 0.35  # how strongly windows/signs glow
    # ground, road, sidewalks
    sc.add(box((0, -0.5, 0), (240, 1, 240), '#8a8580', bg=True, mat='concrete'))
    sc.add(box((0, -0.45, -20), (10, 1, 240), '#2c2c32', bg=True, mat='asphalt'))
    for z in np.arange(-110, 40, 5):
        sc.add(box((0, 0.06, z), (0.22, 0.02, 2.4), '#f2c230', nocast=True))
    for k in range(7):  # crosswalk
        sc.add(box((-3.6 + k * 1.2, 0.06, 15), (0.7, 0.02, 3.2), '#f2f2f2', nocast=True))
    for sx in (-1, 1):
        sc.add(box((sx * 6.5, 0.13, -20), (3.0, 0.26, 240), '#cfc8bc', mat='concrete'))
        sc.add(box((sx * 5.05, 0.16, -20), (0.12, 0.3, 240), GOLD, emit=0.1))
    # storefront blocks on both sides
    shop_i = 0
    for sx in (-1, 1):
        for zi, z in enumerate(np.arange(-64, 26, 9.0)):
            name, ncol = SHOPS[shop_i % len(SHOPS)]; shop_i += 1
            fac = FACADES[(shop_i * 3 + zi) % len(FACADES)]
            h = rr.uniform(9, 13); cx = sx * 12
            sc.add(box((cx, h / 2, z), (8, h, 8.6), fac, mat='brick' if zi % 3 == 0 else 'facade'))
            sc.add(box((cx, h + 0.2, z), (8.5, 0.4, 9.0), GOLD, emit=0.12, rl=4))
            fx = sx * 7.98
            glow = '#ffd9a0' if zi % 2 else '#fff1d8'
            sc.add(box((fx, 2.4, z - 0.8), (0.1, 3.0, 5.2), glow, emit=0.5 + lw * 0.5, shade=False))
            sc.add(box((fx, 1.75, z + 3.1), (0.12, 3.5, 1.6), '#3a2418'))
            sc.add(box((fx - sx * 0.05, 1.8, z + 3.6), (0.06, 0.3, 0.12), GOLD, emit=0.3))
            for k in range(6):  # striped awning
                col = fac if k % 2 else '#ffffff'
                sc.add(box((sx * 7.2, 4.3, z - 3.4 + k * 1.1), (1.7, 0.12, 1.1), col, R=rot(0, 0, sx * 18), nocast=True))
            sg = box((sx * 7.9, 5.6, z), (0.14, 1.5, 6.8), '#120a0e', nocast=True)
            sg.tex['px' if sx < 0 else 'nx'] = (neon_img(name, ncol), True)
            sc.add(sg)
            for k in range(2):  # upper windows
                for j in range(int((h - 7) // 2.2) + 1):
                    sc.add(box((sx * 7.97, 7.4 + j * 2.2, z - 2.2 + k * 4.4), (0.08, 1.4, 1.6),
                               '#ffe2a0' if rr.random() < 0.5 else '#9fc4ff', emit=lw * rr.uniform(0.3, 1.0), shade=False, nocast=True))
            if zi % 2 == 0:  # posters between shops
                poster(sc, (sx * 7.93, 2.6, z - 4.3), rot(90 if sx < 0 else -90), 1.6, 2.2, WORDS[(shop_i + zi) % len(WORDS)], seed=shop_i)
            if night and abs(z) < 30:
                sc.lights.append(dict(pos=(sx * 6.5, 3, z), col='#ffc880', I=0.8, r=7))
    # gold and blue glass towers
    for sx in (-1, 1):
        for k, z in enumerate(np.arange(-110, 30, 13.0)):
            x = sx * rr.uniform(21, 30); h = rr.uniform(32, 85); w = rr.uniform(9, 13)
            gold = (k + (sx > 0)) % 2 == 0
            body = '#b9934a' if gold else '#34466e'
            sc.add(box((x, h / 2, z), (w, h, w), body, bg=True, emit=0.06 if gold else 0.03))
            face_x = x - sx * (w / 2 + 0.05)
            strip = '#ffd27a' if gold else '#a8c8ff'
            for j in range(int(w // 1.6)):
                sc.add(box((face_x, h / 2, z - w / 2 + 0.8 + j * 1.6), (0.06, h * 0.96, 0.18), strip,
                           emit=(0.25 + lw * 0.5), shade=False, nocast=True, bg=True))
            sc.add(box((x, h + 1.2, z), (w * 0.7, 2.4, w * 0.7), GOLD, emit=0.3 + lw * 0.4, bg=True))
            if k % 3 == 0:
                sc.add(box((x, h + 5, z), (0.4, 6, 0.4), '#e8e0d0', bg=True), box((x, h + 8.2, z), (0.6, 0.6, 0.6), '#ff4a3a', emit=2.0, shade=False, bg=True))
    for k in range(18):  # far skyline
        x = rr.uniform(-70, 70); z = rr.uniform(-170, -130); h = rr.uniform(30, 90); w = rr.uniform(8, 14)
        sc.add(box((x, h / 2, z), (w, h, w), rr.choice(['#9a7a46', '#4a5a7e', '#6a6a86']), bg=True, emit=0.05))
    # red suspension bridge on the horizon (San Francisco)
    bz = -190; red = '#c4372c'
    sc.add(box((0, 9, bz), (160, 1.6, 4), red, bg=True))
    for tx in (-40, 40):
        sc.add(box((tx, 28, bz), (3, 56, 3), red, bg=True), box((tx, 50, bz), (8, 2, 3.4), red, bg=True), box((tx, 36, bz), (8, 1.6, 3.4), red, bg=True))
    for k in range(41):
        x = -80 + k * 4
        y = 12 + 40 * (x / 40) ** 2 if abs(x) <= 40 else 52 - 42 * ((abs(x) - 40) / 40)
        sc.add(box((x, y, bz), (4.2, 0.5, 0.5), red, bg=True))
    # gold street lamps, planters, hydrants, taxis
    for z in np.arange(-60, 30, 12):
        for sx in (-1, 1):
            x = sx * 5.5
            sc.add(box((x, 4, z), (0.3, 8, 0.3), GOLD, emit=0.15, rl=4), box((x - sx * 0.9, 8.0, z), (1.9, 0.22, 0.3), GOLD, emit=0.15))
            sc.add(box((x - sx * 1.6, 7.75, z), (0.8, 0.35, 0.6), '#fff1c8', emit=2.2 if night else 0.6, shade=False))
            if night and abs(z) < 26:
                sc.lights.append(dict(pos=(x - sx * 1.6, 7, z), col='#ffd890', I=0.9, r=8))
        plant(sc, (-6.8, 0.26, z + 6), 1.0); plant(sc, (6.8, 0.26, z + 6), 1.0)
    sc.add(box((6.2, 0.75, 9), (0.5, 1.0, 0.5), '#d42a2a', rl=3), box((-6.2, 0.75, -9), (0.5, 1.0, 0.5), '#d42a2a', rl=3))
    for z, x, yaw in ((-22, 2.4, 0), (-34, -2.4, 180), (26, -2.4, 180), (-48, 2.4, 0)):
        car(sc, (x, 0, z), yaw=yaw, color='#f5c518', lights=night)


def decorate(sc, stage, t, seed=0):
    """Posters and coloured LED strips so indoor sets never look bare."""
    rooms = {  # stage: (width, depth, height) of its room() call
        'bedroom': (16, 16, 8), 'livingroom': (18, 16, 8), 'kitchen': (18, 14, 8.5), 'garage': (14, 12, 7),
        'shop': (18, 16, 9), 'cafeteria': (26, 22, 9), 'diner': (20, 16, 8), 'party_room': (20, 18, 8.5), 'gym': (30, 26, 10),
    }
    if stage not in rooms:
        return
    w, d, h = rooms[stage]
    rr = random.Random(sum(map(ord, stage)) + seed)
    words = WORDS[:]; rr.shuffle(words)
    py = h * 0.58
    spots = [((-w / 4, py, -d / 2 + 0.06), None), ((w / 4 + 1.0, py + 0.3, -d / 2 + 0.06), None),
             ((-w / 2 + 0.06, py, d / 6), rot(90)), ((w / 2 - 0.06, py, -d / 6), rot(-90))]
    for i, (p, R) in enumerate(spots):
        poster(sc, p, R, 2.0, 2.8, words[i], seed=seed + i * 3 + 1)
    led = ['#b04aff', '#3ad0ff', '#ff3a8a', '#ffb02a'][rr.randrange(4)]
    for (p, size) in (((0, h - 0.25, -d / 2 + 0.1), (w - 0.4, 0.12, 0.12)), ((-w / 2 + 0.1, h - 0.25, 0), (0.12, 0.12, d - 0.4)),
                      ((w / 2 - 0.1, h - 0.25, 0), (0.12, 0.12, d - 0.4))):
        sc.add(box(p, size, led, emit=2.5, shade=False, nocast=True))
    sc.lights.append(dict(pos=(0, h - 1, 0), col=led, I=0.22, r=max(w, d) * 0.5))
