"""World / science sets for the "what if" shorts: space, oceans, disasters, the Earth's insides.

Every stage builds a full scene from (sc, t). LT[0] holds the time inside the current shot so big events
(a wave rolling in, the Moon cracking) play out on screen in every shot. Each stage also has an "event
camera" (EVENT_CAMS) that frames the spectacle for wide / drone / reveal shots, while close-ups stay on
the hero, who watches it happen from a spot in the scene.
"""
import math
import random

import numpy as np

from .engine import box, rot, C, character
from .luxsets import lux_city

LT = [0.0]          # shot-local time, set by the director before each frame
_CACHE = {}


def _ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ voxel planets
def _shell(R):
    """Integer voxel positions forming a hollow sphere of radius R (in voxels)."""
    k = ('shell', R)
    if k not in _CACHE:
        r = np.arange(-R, R + 1)
        g = np.stack(np.meshgrid(r, r, r, indexing='ij'), -1).reshape(-1, 3).astype(float)
        d = np.linalg.norm(g, axis=1)
        _CACHE[k] = g[(d <= R + 0.05) & (d > R - 1.05)]
    return _CACHE[k]


def _noise(p, seed):
    """Cheap smooth noise on unit directions (sum of sines)."""
    rr = random.Random(seed)
    v = np.zeros(len(p))
    for o in range(6):
        a = np.array([rr.uniform(-1, 1) for _ in range(3)])
        a = a / np.linalg.norm(a) * (1.6 + o * 1.3)
        v += np.sin(p @ a + rr.uniform(0, 6.28)) / (1 + o * 0.6)
    return v


def _palette(kind, R):
    k = ('pal', kind, R)
    if k in _CACHE:
        return _CACHE[k]
    P = _shell(R)
    u = P / np.linalg.norm(P, axis=1, keepdims=True)
    n = _noise(u, {'earth': 3, 'moon': 9, 'rock': 21, 'sun': 5, 'dark': 3}[kind])
    cols, emit = [], []
    for i in range(len(P)):
        y = u[i, 1]
        if kind in ('earth', 'dark'):
            if abs(y) > 0.93:
                c, e = '#f4f8ff', 0.0
            elif n[i] > 0.55:
                c = '#3f9a3c' if n[i] < 1.3 else ('#7c6b3c' if n[i] < 1.9 else '#a89a7a')
                if abs(y) < 0.3 and n[i] > 1.0:
                    c = '#c9a659'  # deserts near the equator
                e = 0.0
            else:
                c = '#1f63c4' if n[i] > 0.1 else '#174fa4'
                e = 0.0
            if kind == 'dark':  # frozen, sunless Earth
                c = '#cfe3f4' if abs(y) > 0.4 or n[i] > 0.55 else '#2a3f5c'
        elif kind == 'moon':
            c = '#c8c8cc' if n[i] > -0.2 else ('#9a9aa2' if n[i] > -0.9 else '#7a7a84')
            e = 0.0
        elif kind == 'rock':
            c = '#6a5a4a' if n[i] > 0 else '#4a3e34'
            e = 0.0
        else:  # sun
            c = '#fff3b0' if n[i] > 0.4 else ('#ffd24a' if n[i] > -0.4 else '#ff9a2a')
            e = 2.6
        cols.append(c); emit.append(e)
    _CACHE[k] = (P, cols, emit)
    return _CACHE[k]


def planet(sc, center, radius, kind='earth', spin=0.0, R=9, tilt=18, explode=None, glow=None):
    """A voxel planet. explode=(p, seeds) breaks it into chunks that fly apart (p 0..1)."""
    P, cols, emit = _palette(kind, R)
    g = radius / R
    rt = rot(spin, 0, tilt)
    pts = (P @ rt.T) * g
    off = np.zeros_like(pts)
    hot = np.zeros(len(P))
    if explode is not None:
        p, nchunks = explode
        k = ('chunks', R, nchunks)
        if k not in _CACHE:
            rr = random.Random(11)
            seeds = np.array([[rr.gauss(0, 1) for _ in range(3)] for _ in range(nchunks)])
            seeds /= np.linalg.norm(seeds, axis=1, keepdims=True)
            u = P / np.linalg.norm(P, axis=1, keepdims=True)
            dots = u @ seeds.T
            lab = dots.argmax(1)
            srt = np.sort(dots, 1)
            edge = (srt[:, -1] - srt[:, -2]) < 0.05
            _CACHE[k] = (seeds, lab, edge)
        seeds, lab, edge = _CACHE[k]
        drift = (seeds[lab] @ rt.T) * radius * (0.03 + 1.1 * p)
        off = drift
        hot = edge * max(0.0, 1 - p * 1.4)
    s = g * 1.32
    core = {'earth': '#174fa4', 'dark': '#2a3f5c', 'moon': '#8a8a92', 'rock': '#4a3e34', 'sun': '#ffb02a'}[kind]
    if explode is None:
        sc.add(box(tuple(center), (radius * 1.74,) * 3, core, rl=4, nocast=True, emit=2.0 if kind == 'sun' else 0.0))
    for i in range(len(P)):
        e = emit[i]
        c = cols[i]
        if hot[i] > 0:
            c = '#ff7a2a'; e = 1.1 * hot[i] + 0.2
        sc.add(box(tuple(np.array(center) + pts[i] + off[i]), (s, s, s), c, emit=e, nocast=True, shade=kind != 'sun'))
    if glow:
        sc.lights.append(dict(pos=tuple(center), col=glow, I=2.5, r=radius * 4))


def clouds(sc, center, radius, spin, R=9):
    P = _shell(R + 1)
    k = ('cloudmask', R)
    if k not in _CACHE:
        u = P / np.linalg.norm(P, axis=1, keepdims=True)
        _CACHE[k] = P[_noise(u, 44) > 1.4]
    pts = (_CACHE[k] @ rot(spin, 0, 18).T) * (radius / R)
    s = radius / R * 0.9
    for q in pts:
        sc.add(box(tuple(np.array(center) + q), (s, s * 0.85, s), '#ffffff', emit=0.25, nocast=True))


def ring(sc, center, r0, r1, t, n=220, tilt=20, cols=('#d8c8a8', '#b8a888', '#e8dcc0'), size=0.9, speed=6.0, seed=1):
    rr = random.Random(seed)
    Rt = rot(0, 0, tilt)
    for j in range(n):
        r = rr.uniform(r0, r1)
        a = rr.uniform(0, 6.283) + t * speed / r
        p = np.array([math.cos(a) * r, rr.uniform(-0.4, 0.4), math.sin(a) * r]) @ Rt.T
        s = size * rr.uniform(0.5, 1.4)
        sc.add(box(tuple(np.array(center) + p), (s, s * 0.7, s), cols[j % len(cols)], R=rot(j * 37 + t * 20, j * 13, 0),
                   emit=0.15, nocast=True))


def starfield(sc, seed=5, n=160, dist=330):
    rr = random.Random(seed)
    for j in range(n):
        th = rr.uniform(0, 6.283); ph = rr.uniform(-1.2, 1.4)
        p = (math.cos(ph) * math.sin(th) * dist, math.sin(ph) * dist, math.cos(ph) * math.cos(th) * dist)
        s = rr.uniform(0.4, 1.3)
        sc.add(box(p, (s, s, s), '#ffffff' if j % 5 else '#bcd4ff', emit=3.0, shade=False, nocast=True))


def space_base(sc):
    sc.sky = (C('#02030a'), C('#0a1030')); sc.stars = 1.0
    sc.ambient = C((0.22, 0.24, 0.34)); sc.suncol = C((1.0, 0.95, 0.85)); sc.sun = np.array([-0.8, -0.25, -0.45])
    sc.fog = C('#000000'); sc.fogd = 0.0
    starfield(sc)


def deck(sc, t):
    """Small orbital observation deck the hero stands on."""
    sc.add(box((0, -0.3, 0), (16, 0.6, 12), '#3a3f4a', mat='concrete'))
    for x in np.arange(-7, 7.5, 2):
        sc.add(box((x, 0.01, 0), (0.06, 0.02, 12), '#262a32', nocast=True))
    for sx in (-1, 1):
        sc.add(box((sx * 8, 0.0, 0), (0.25, 0.25, 12), '#5ab4ff', emit=1.6, nocast=True))
    sc.add(box((0, 0.0, -6), (16, 0.25, 0.25), '#5ab4ff', emit=1.6, nocast=True))
    for x in np.arange(-7.5, 8, 2.5):
        sc.add(box((x, 1.2, -5.8), (0.18, 2.4, 0.18), '#9aa4b4'))
    sc.add(box((0, 2.35, -5.8), (16, 0.16, 0.16), '#c8d0dc'))
    sc.add(box((-6.5, 1.0, 3.5), (2.4, 2.0, 1.6), '#2a2e38'))
    sc.add(box((-6.5, 2.05, 3.6), (2.0, 0.08, 1.2), '#3ad0ff', emit=1.2, nocast=True))
    sc.lights.append(dict(pos=(2.5, 7, 6), col='#cfe0ff', I=2.0, r=14))


EARTH = (0, 18, -170)


def st_space(sc, t):
    space_base(sc); deck(sc, t)
    planet(sc, EARTH, 46, 'earth', spin=t * 4)
    clouds(sc, EARTH, 46, t * 6)
    planet(sc, (78, 52, -150), 12, 'moon', spin=t * 2, R=7)


def st_moon_breaks(sc, t):
    space_base(sc); deck(sc, t)
    lt = LT[0]
    planet(sc, (-40, 2, -210), 40, 'earth', spin=t * 4)
    clouds(sc, (-40, 2, -210), 40, t * 6)
    p = _ease(min(1.0, (t * 0.05 + lt * 0.12)))
    planet(sc, (34, 40, -140), 22, 'moon', spin=t * 3, R=8, explode=(p, 7))
    if lt < 0.5 and t < 3:
        sc.lights.append(dict(pos=(34, 40, -120), col='#ffffff', I=6 * (1 - lt * 2), r=80))
    rr = random.Random(4)
    for j in range(60):  # small debris
        d = np.array([rr.gauss(0, 1) for _ in range(3)]); d /= np.linalg.norm(d)
        q = np.array((34, 40, -140)) + d * (22 + 30 * p * rr.uniform(0.5, 1.6))
        s = rr.uniform(0.6, 1.6)
        sc.add(box(tuple(q), (s, s, s), '#a8a8b0', R=rot(j * 40 + t * 30, j * 20, 0), nocast=True))


def st_earth_ring(sc, t):
    space_base(sc); deck(sc, t)
    planet(sc, EARTH, 40, 'earth', spin=t * 4)
    clouds(sc, EARTH, 40, t * 6)
    ring(sc, EARTH, 58, 92, t, n=420, tilt=16, size=2.2, speed=40)


def st_black_hole(sc, t):
    space_base(sc); deck(sc, t)
    c = np.array((0, 22, -140))
    rr = random.Random(2)
    for j in range(520):  # accretion disk, hotter inside
        r = 18 + rr.random() ** 1.6 * 46
        a = rr.uniform(0, 6.283) + t * 260 / (r * r) * 6
        p = np.array([math.cos(a) * r, rr.uniform(-0.6, 0.6) * (r / 40), math.sin(a) * r]) @ rot(0, 0, 14).T
        col = '#fff6d8' if r < 26 else ('#ffc04a' if r < 40 else '#ff6a1a')
        s = rr.uniform(1.0, 2.6)
        sc.add(box(tuple(c + p), (s * 2.2, s * 0.5, s), col, R=rot(-math.degrees(a), 0, 14), emit=2.6, shade=False, nocast=True))
    for j in range(90):  # photon ring
        a = j / 90 * 6.283
        p = np.array([math.cos(a) * 17, math.sin(a) * 17, 0])
        sc.add(box(tuple(c + p + (0, 0, 8)), (1.6, 1.6, 0.4), '#ffe8a8', emit=3.2, shade=False, nocast=True))
    sc.add(box(tuple(c), (30, 30, 30), '#000000', rl=4, shade=False, nocast=True))
    for j in range(24):  # things being stretched and pulled in
        a = j * 0.9 + t * 0.5
        r = 70 - ((t * 9 + j * 13) % 50)
        p = np.array([math.cos(a) * r, math.sin(j) * 6, math.sin(a) * r])
        L = 2 + (70 - r) * 0.25
        sc.add(box(tuple(c + p), (L, 0.5, 0.5), ['#7a8aa0', '#c84a3a', '#e8e8e8'][j % 3], R=rot(-math.degrees(a) + 90, 0, 0), nocast=True))
    sc.lights.append(dict(pos=tuple(c + (0, 0, 30)), col='#ffb050', I=2.5, r=120))


def st_sun_dark(sc, t):
    space_base(sc); deck(sc, t)
    sc.ambient = C((0.18, 0.2, 0.3)); sc.suncol = C((0.22, 0.24, 0.36))
    planet(sc, EARTH, 46, 'dark', spin=t * 4)
    c = np.array((120, 70, -260))
    for j in range(60):
        a = j / 60 * 6.283 + t * 0.4
        sc.add(box(tuple(c + (math.cos(a) * 12, math.sin(a) * 12, 0)), (2, 2, 0.5), '#ffcf7a', emit=2.0, shade=False, nocast=True))
    sc.add(box(tuple(c), (20, 20, 20), '#000000', rl=4, shade=False, nocast=True))


def st_asteroid(sc, t):
    space_base(sc); deck(sc, t)
    planet(sc, EARTH, 46, 'earth', spin=t * 4)
    clouds(sc, EARTH, 46, t * 6)
    lt = LT[0]
    a = np.array((70, 50, -60)); b = np.array(EARTH) + (10, 20, 30)
    q = a + (b - a) * min(1.0, 0.15 + lt * 0.12)
    planet(sc, tuple(q), 7, 'rock', spin=t * 40, R=5)
    d = (a - b) / np.linalg.norm(a - b)
    for j in range(26):
        p = q + d * (6 + j * 2.2)
        s = max(0.6, 5 - j * 0.17)
        sc.add(box(tuple(p + np.sin([j * 2.1, j * 1.3, j]) * 0.8), (s, s, s), '#ffd24a' if j < 8 else '#ff6a1a',
                   emit=3.0 - j * 0.08, shade=False, nocast=True, rl=3))
    sc.lights.append(dict(pos=tuple(q), col='#ff9a3a', I=3, r=60))


# ------------------------------------------------------------------ ground disasters
def _dim_windows(sc, k=0.04):
    for b in sc.boxes:
        if b.emit > 0.2:
            b.emit *= k
    sc.lights = []


def st_meteor_city(sc, t):
    lux_city(sc, t, night=True)
    sc.sky = (C('#3a0a04'), C('#ff6a1a')); sc.fog = C((0.6, 0.22, 0.08)); sc.fogd = 0.012; sc.stars = 0.0
    sc.ambient = C((0.55, 0.3, 0.2)); sc.suncol = C((0.9, 0.4, 0.15))
    rr = random.Random(8)
    for j in range(46):
        per = rr.uniform(1.2, 2.6)
        ph = ((t + rr.uniform(0, per)) % per) / per
        x0 = rr.uniform(-70, 70); z0 = rr.uniform(-150, -20)
        head = np.array((x0 + 40 - 60 * ph, 110 - 115 * ph, z0))
        d = np.array((0.46, 0.89, 0))
        for k in range(7):
            s = 1.8 - k * 0.2
            sc.add(box(tuple(head + d * k * 2.2), (s, s, s), '#fff2b0' if k < 2 else '#ff7a2a', emit=3.2 - k * 0.3,
                       shade=False, nocast=True, rl=3))
    for j, (x, z) in enumerate(((-16, -40), (14, -70), (-20, -95), (18, -30))):
        for k in range(6):
            h = (t * 3 + k * 0.7 + j) % 4
            s = 2.4 - h * 0.4
            sc.add(box((x + math.sin(k + t * 4) * 0.8, 12 + h * 2.2, z), (s, s, s), '#ffb02a' if h < 2 else '#ff4a1a',
                       emit=2.6, shade=False, nocast=True, rl=3))
        sc.lights.append(dict(pos=(x, 14, z), col='#ff7a2a', I=2.0, r=26))


def wave_wall(sc, z, height=34, width=120, t=0.0):
    for i, x in enumerate(np.arange(-width / 2, width / 2, 4)):
        hh = height + math.sin(x * 0.15 + t) * 3
        for k in range(10):
            f = k / 9
            y = f * hh
            zz = z + (1 - f) * 18 - math.sin(f * 2.6) * 9
            col = ['#0a2a4a', '#0e3a64', '#13507e', '#1a6a98', '#2a86b0', '#4aa4c8'][min(5, int(f * 6))]
            sc.add(box((x, y, zz), (4.3, hh / 9 + 0.6, 6), col, nocast=True))
        for k in range(3):
            sc.add(box((x + math.sin(t * 5 + i + k) * 1.2, hh + 1 + k * 0.8, z - 4 + k * 2), (3.2, 1.6, 3.0), '#f4fbff',
                       emit=0.35, rl=3, nocast=True))


def st_tsunami_city(sc, t):
    lux_city(sc, t, night=False)
    sc.sky = (C('#3a4658'), C('#8a96a6')); sc.fog = C((0.5, 0.56, 0.64)); sc.fogd = 0.006
    sc.suncol = C((0.4, 0.42, 0.45)); sc.ambient = C((0.5, 0.52, 0.58))
    lt = LT[0]
    wave_wall(sc, -95 + min(lt, 4.5) * 14, t=t)
    for x in np.arange(-60, 60, 6):  # rushing water in front of the wave
        for k in range(3):
            z = -60 + min(lt, 4.5) * 14 + k * 6
            sc.add(box((x, 0.4 + math.sin(t * 4 + x) * 0.3, z), (6.1, 1.0, 6.1), '#2a6a90', nocast=True))


def st_flood_city(sc, t):
    lux_city(sc, t, night=False)
    sc.sky = (C('#6a7a8c'), C('#c8d0d8')); sc.fog = C((0.7, 0.74, 0.8)); sc.fogd = 0.006
    lvl = 3.0
    sc.add(box((0, lvl - 1, -20), (240, 2, 260), '#2a6f8f', nocast=True))
    rr = random.Random(3)
    for j in range(120):  # ripples
        x = rr.uniform(-40, 40); z = rr.uniform(-120, 30)
        x += math.sin(t * 0.8 + j) * 1.5
        sc.add(box((x, lvl + 0.02, z), (rr.uniform(1.5, 4), 0.05, 0.25), '#8fd0e8', emit=0.2, nocast=True))
    for j in range(14):  # floating debris
        x = rr.uniform(-6, 6); z = rr.uniform(-60, 0) + t * 0.6
        sc.add(box((x, lvl + 0.15 + math.sin(t * 2 + j) * 0.1, z), (1.4, 0.3, 0.9), ['#8a5a3a', '#c42a2a', '#e8e8e8'][j % 3],
                   R=rot(j * 40 + t * 10, 0, 0), nocast=True))
    sc.add(box((0, lvl + 0.15, 4), (4.4, 0.5, 4.4), '#7a4a2a'))  # the raft the hero stands on


def volcano_shape(sc, pos, t, h=46, base=70, erupt=1.0):
    x0, y0, z0 = pos
    n = 12
    for k in range(n):
        f = k / n
        w = base * (1 - f * 0.82)
        col = '#3a2e2a' if k % 2 else '#2e2420'
        sc.add(box((x0, y0 + f * h + h / n / 2, z0), (w, h / n + 0.2, w * 0.9), col, R=rot(k * 7, 0, 0), nocast=True))
    sc.add(box((x0, y0 + h + 0.3, z0), (base * 0.16, 0.8, base * 0.14), '#ff6a1a', emit=3.0, shade=False, nocast=True))
    for s in (-1, 1):  # lava rivers
        for k in range(10):
            f = k / 10
            sc.add(box((x0 + s * base * (0.06 + f * 0.33), y0 + h * (1 - f) - 1, z0 + base * 0.3 * f + 4), (2.2, 2.2, 2.2),
                       '#ff7a1a', emit=2.6, shade=False, nocast=True))
    rr = random.Random(6)
    for j in range(int(60 * erupt)):  # fountain
        per = rr.uniform(1.0, 2.0); ph = ((t + rr.uniform(0, per)) % per)
        vx = rr.uniform(-6, 6); vy = rr.uniform(14, 24); vz = rr.uniform(-6, 6)
        p = (x0 + vx * ph, y0 + h + vy * ph - 9 * ph * ph, z0 + vz * ph)
        if p[1] > y0 + h * 0.6:
            sc.add(box(p, (1.4, 1.4, 1.4), '#ffb02a' if j % 3 else '#ff4a1a', emit=3.0, shade=False, nocast=True, rl=3))
    for j in range(int(40 * erupt)):  # ash plume
        per = 8.0; ph = ((t * 0.6 + j * 0.37) % per) / per
        r = 6 + ph * 34
        p = (x0 + math.sin(j * 2.3) * r * 0.6, y0 + h + 6 + ph * 70, z0 + math.cos(j * 1.7) * r * 0.4)
        s = 8 + ph * 18
        sc.add(box(p, (s, s * 0.8, s), '#4a4646' if j % 2 else '#5e5a58', rl=4, nocast=True))
    sc.lights.append(dict(pos=(x0, y0 + h + 6, z0), col='#ff6a1a', I=3.0, r=90))


def st_volcano(sc, t):
    sc.sky = (C('#2a1c18'), C('#a8502a')); sc.fog = C((0.35, 0.22, 0.18)); sc.fogd = 0.007
    sc.ambient = C((0.4, 0.3, 0.28)); sc.suncol = C((0.7, 0.4, 0.25)); sc.sun = np.array([0.5, -0.5, -0.6])
    sc.add(box((0, -0.5, -40), (300, 1, 300), '#2a2422', bg=True, mat='concrete'))
    rr = random.Random(9)
    for j in range(40):
        x = rr.uniform(-30, 30); z = rr.uniform(-30, 10)
        if abs(x) < 4 and z > -4:
            continue
        s = rr.uniform(0.8, 3)
        sc.add(box((x, s / 2 - 0.2, z), (s, s, s * 1.2), '#3a302c', R=rot(rr.uniform(0, 90), 0, 0)))
    volcano_shape(sc, (0, 0, -95), t)


def ash_fall(sc, t, center, n=200, col='#b8b4b0'):
    rr = random.Random(12)
    for j in range(n):
        x = center[0] + rr.uniform(-14, 14); z = center[2] + rr.uniform(-14, 8)
        y = 16 - ((t * rr.uniform(1.0, 2.0) + rr.uniform(0, 16)) % 16)
        x += math.sin(t + j) * 0.6
        sc.add(box((x, y, z), (0.14, 0.14, 0.14), col, nocast=True, shade=False, emit=0.2))


def st_ash_city(sc, t):
    lux_city(sc, t, night=False)
    _dim_windows(sc, 0.3)
    sc.sky = (C('#3a3634'), C('#7a706a')); sc.fog = C((0.42, 0.4, 0.38)); sc.fogd = 0.018
    sc.ambient = C((0.4, 0.38, 0.36)); sc.suncol = C((0.35, 0.3, 0.26))
    volcano_shape(sc, (0, 0, -150), t, h=60, base=90)
    ash_fall(sc, t, (0, 0, 4))
    for z in np.arange(-60, 20, 3):  # ash piling up on the road
        sc.add(box((0, 0.12, z), (9.6, 0.2, 3.1), '#9a9690', nocast=True))


def st_frozen_city(sc, t):
    lux_city(sc, t, night=True)
    _dim_windows(sc, 0.05)
    sc.sky = (C('#02040a'), C('#0c1426')); sc.fog = C((0.12, 0.16, 0.26)); sc.fogd = 0.012; sc.stars = 1.0
    sc.ambient = C((0.3, 0.36, 0.5)); sc.suncol = C((0.1, 0.12, 0.2))
    for z in np.arange(-80, 30, 4):
        sc.add(box((0, 0.3, z), (24, 0.5, 4.1), '#dfeaf6', nocast=True))
    rr = random.Random(5)
    for j in range(220):
        x = rr.uniform(-14, 14); z = rr.uniform(-10, 10) + 4
        y = 14 - ((t * rr.uniform(0.8, 1.6) + rr.uniform(0, 14)) % 14)
        sc.add(box((x + math.sin(t + j) * 0.8, y, z), (0.12, 0.12, 0.12), '#ffffff', emit=0.6, nocast=True, shade=False))
    sc.lights.append(dict(pos=(3, 8, 8), col='#8ab4ff', I=1.6, r=18))


def st_ring_sky(sc, t):
    lux_city(sc, t, night=False)
    c = np.array((0, -40, -300))
    for j in range(260):
        a = math.pi * (0.04 + 0.92 * j / 260)
        for b, (r, col) in enumerate(((235, '#e8d8b8'), (246, '#c8b088'), (256, '#f4ead4'))):
            p = c + (math.cos(a) * r, math.sin(a) * r * 0.55, 0)
            sc.add(box(tuple(p), (9, 7, 1), col, emit=2.2, shade=False, nocast=True))


def st_blackout(sc, t):
    lux_city(sc, t, night=True)
    _dim_windows(sc, 0.02)
    sc.sky = (C('#010206'), C('#060a16')); sc.stars = 1.0; sc.fog = C((0.03, 0.04, 0.08)); sc.fogd = 0.016
    sc.ambient = C((0.16, 0.18, 0.26)); sc.suncol = C((0.08, 0.09, 0.14))
    sc.lights.append(dict(pos=(2, 6, 8), col='#9ab0d8', I=1.2, r=14))


# ------------------------------------------------------------------ ocean
def anglerfish(sc, pos, t, s=1.0):
    x, y, z = pos
    sc.add(box((x, y, z), (2.6 * s, 2.0 * s, 1.8 * s), '#1a1e26', rl=3))
    for k in range(6):
        sc.add(box((x + (k - 2.5) * 0.4 * s, y - 0.5 * s, z + 0.95 * s), (0.18 * s, 0.4 * s, 0.1 * s), '#f4f4ec', emit=0.3))
    sc.add(box((x - 1.6 * s, y, z), (0.9 * s, 1.2 * s, 0.2 * s), '#141820', R=rot(0, 0, 20 * math.sin(t * 6))))
    for sx in (-0.6, 0.6):
        sc.add(box((x + sx * s, y + 0.5 * s, z + 0.92 * s), (0.25 * s, 0.25 * s, 0.05 * s), '#9af0ff', emit=2.0, shade=False))
    sc.add(box((x + 0.6 * s, y + 1.5 * s, z + 0.6 * s), (0.08 * s, 1.4 * s, 0.08 * s), '#2a2e36', R=rot(0, 30, 0)))
    sc.add(box((x + 0.9 * s, y + 2.2 * s, z + 1.2 * s), (0.45 * s,) * 3, '#d8ffb0', emit=4.0, shade=False, rl=4))
    sc.lights.append(dict(pos=(x + 0.9 * s, y + 2.2 * s, z + 1.4 * s), col='#c8ffa0', I=1.4, r=6 * s))


def jelly(sc, pos, t, col='#ff7ad8'):
    x, y, z = pos
    y += math.sin(t * 1.4 + x) * 0.6
    sc.add(box((x, y, z), (1.6, 1.0, 1.6), col, emit=1.6, rl=4, shade=False))
    for k in range(5):
        a = k * 1.25
        sc.add(box((x + math.cos(a) * 0.5, y - 1.3 - 0.2 * math.sin(t * 3 + k), z + math.sin(a) * 0.5), (0.08, 1.8, 0.08), col, emit=1.0, shade=False))


def isopod(sc, pos, t):
    x, y, z = pos
    for k in range(7):
        sc.add(box((x + k * 0.55, y + 0.35 * math.sin(k * 0.45), z), (0.6, 0.7 - abs(k - 3) * 0.05, 1.5), '#b8aca0' if k % 2 else '#a89a8e', rl=2))
    for k in range(6):
        for sz in (-1, 1):
            sc.add(box((x + k * 0.55 + 0.3, y - 0.45, z + sz * 0.75), (0.08, 0.5, 0.08), '#8a7c70', R=rot(0, 0, 20 * math.sin(t * 8 + k))))


def ghost_shark(sc, pos, t):
    x, y, z = pos
    x += math.sin(t * 0.4) * 3
    sc.add(box((x, y, z), (4.4, 1.1, 1.2), '#c8ccd8', rl=3))
    sc.add(box((x + 2.6, y + 0.1, z), (1.4, 0.8, 0.9), '#b8bcc8', rl=3))
    sc.add(box((x - 3.0, y, z), (2.4, 0.2, 0.2), '#a8acb8'))
    sc.add(box((x, y + 0.9, z), (1.0, 1.0, 0.1), '#b0b4c0', R=rot(0, 0, -20)))
    sc.add(box((x + 3.1, y + 0.25, z + 0.5), (0.3, 0.3, 0.05), '#6af0ff', emit=2.0, shade=False))


def whale(sc, pos, t, s=1.0):
    x, y, z = pos
    for k in range(9):
        w = (1.0 - abs(k - 3.5) / 6.5) * s
        sc.add(box((x + k * 3.2 * s, y + math.sin(t + k * 0.4) * 0.3, z), (3.4 * s, 4.2 * w + 1, 3.6 * w + 1), '#3a5a7a' if k % 2 else '#365474', rl=3))
    sc.add(box((x + 1.5 * s, y - 1.6 * s, z), (9 * s, 0.6 * s, 3.0 * s), '#a8bccc', rl=2))
    sc.add(box((x + 29 * s, y + math.sin(t * 1.2) * 1.4, z), (2 * s, 0.4 * s, 7 * s), '#30506e'))


def st_deep_ocean(sc, t):
    sc.sky = (C('#000206'), C('#021428')); sc.fog = C((0.0, 0.05, 0.12)); sc.fogd = 0.045
    sc.ambient = C((0.12, 0.2, 0.32)); sc.suncol = C((0.05, 0.1, 0.18)); sc.sun = np.array([0.1, -1, 0.1])
    sc.shadow = False
    sc.add(box((0, -6, 0), (200, 1, 200), '#1a2228', bg=True))
    rr = random.Random(14)
    for j in range(40):
        x = rr.uniform(-30, 30); z = rr.uniform(-40, 10)
        s = rr.uniform(1, 5)
        sc.add(box((x, -5.5 + s / 3, z), (s, s * 0.7, s), '#222c34', R=rot(rr.uniform(0, 90), 0, 0)))
    for j in range(240):  # marine snow drifting up past the falling hero
        x = rr.uniform(-12, 12); z = rr.uniform(-14, 10)
        y = ((t * rr.uniform(1.5, 3.0) + rr.uniform(0, 18)) % 18) - 4
        sc.add(box((x, y, z), (0.07, 0.07, 0.07), '#cfe8ff', emit=0.8, nocast=True, shade=False))
    for k in range(8):  # bubbles from the hero
        y = 5 + ((t * 2.4 + k * 0.7) % 6)
        sc.add(box((0.3 + math.sin(t * 3 + k) * 0.3, y, 0.5), (0.22, 0.22, 0.22), '#e8f6ff', emit=0.6, rl=4, nocast=True))
    anglerfish(sc, (-5.5, 3.5, -3), t, 1.3)
    jelly(sc, (6, 6, -6), t)
    jelly(sc, (-9, 8, -10), t + 2, '#7ad0ff')
    isopod(sc, (3, -4.6, -4), t)
    ghost_shark(sc, (2, 9, -14), t)
    sc.lights.append(dict(pos=(2, 8, 6), col='#5aa0ff', I=1.4, r=16))


def st_whale(sc, t):
    st_deep_ocean(sc, t)
    sc.fogd = 0.025; sc.sky = (C('#02142a'), C('#0a3a66')); sc.ambient = C((0.2, 0.32, 0.5))
    whale(sc, (-14, 10, -18), t, 1.0)


# ------------------------------------------------------------------ inside the Earth
LAYERS = [(40, '#6b4a2b', 0.0), (37.5, '#c0441c', 0.4), (22, '#ff9a1a', 1.6), (11, '#fff0b0', 2.6)]


def _core_disc():
    k = 'coredisc'
    if k not in _CACHE:
        out = []
        g = 2.0
        rr = random.Random(1)
        for x in np.arange(-40, 41, g):
            for y in np.arange(-40, 41, g):
                r = math.hypot(x, y)
                if r > 40:
                    continue
                col, e = LAYERS[0][1], 0.0
                for rad, c, em in LAYERS:
                    if r <= rad:
                        col, e = c, em
                if LAYERS[2][0] < r <= LAYERS[1][0]:  # mantle gets hotter inward
                    f = (LAYERS[1][0] - r) / (LAYERS[1][0] - LAYERS[2][0])
                    col = '#c0441c' if f < 0.5 else '#e8661a'; e = 0.4 + f * 0.8
                out.append(box((x, y + 40, -60), (g * 1.02, g * 1.02, 1.0 + rr.random() * 0.3), col, emit=e, nocast=True, shade=e < 0.5))
        _CACHE[k] = out
    return _CACHE[k]


def st_earth_core(sc, t):
    sc.sky = (C('#02030a'), C('#0a0c18')); sc.stars = 0.6; sc.fogd = 0.0; sc.shadow = False
    sc.ambient = C((0.4, 0.3, 0.26)); sc.suncol = C((0.6, 0.4, 0.3))
    sc.static = _core_disc()
    lt = LT[0]
    y = 78 - ((t * 2.2) % 76)
    sc.add(box((0, 40, -58.6), (1.4, 80, 0.4), '#05060a', nocast=True))
    sc.add(box((0, y, -58.2), (1.1, 1.1, 0.4), '#ffffff', emit=3.0, shade=False, nocast=True, rl=4))
    # tunnel around the hero (close shots): glowing rock rushing upward
    rr = random.Random(3)
    for j in range(70):
        a = rr.uniform(0, 6.283)
        yy = ((rr.uniform(0, 30) + t * 18) % 30) - 8
        r = 5.5 + rr.random()
        hot = min(1.0, max(0.0, (t % 60) / 40))
        col = '#5a3a24' if rr.random() > hot else '#ff7a1a'
        sc.add(box((math.cos(a) * r, yy, math.sin(a) * r + 0.5), (1.6, 3.2, 1.6), col, emit=1.6 if col == '#ff7a1a' else 0.0, nocast=True))
    sc.lights.append(dict(pos=(0, 5, 3), col='#ff9a4a', I=2.0, r=14))


# ------------------------------------------------------------------ the ocean surface
def st_ocean_impact(sc, t):
    sc.sky = (C('#2a3a5a'), C('#d88a5a')); sc.fog = C((0.6, 0.5, 0.45)); sc.fogd = 0.004
    sc.ambient = C((0.5, 0.45, 0.45)); sc.suncol = C((0.9, 0.6, 0.4)); sc.shadow = False
    lt = LT[0]
    rr0 = 10 + min(lt, 7.0) * 26
    c = np.array((0, 0, -140))
    for x in np.arange(-120, 121, 8):
        for z in np.arange(-260, 21, 8):
            d = math.hypot(x - c[0], z - c[2])
            h = math.sin(x * 0.08 + t) * 0.4 + math.cos(z * 0.06 + t * 1.3) * 0.4
            h += 14 * math.exp(-((d - rr0) / 8) ** 2)
            sc.add(box((x, h - 1, z), (8.1, 2, 8.1), '#1a5a8a' if h < 4 else '#cfe8f4', nocast=True))
    fb = min(1.0, 0.2 + lt * 0.4)
    for j in range(40):  # fireball and steam column
        f = j / 40
        s = (6 + f * 20) * fb
        sc.add(box(tuple(c + (math.sin(j * 2.1) * s * 0.4, f * 70 * fb, math.cos(j * 1.3) * s * 0.3)), (s, s, s),
                   '#fff2c0' if f < 0.25 else ('#ff8a2a' if f < 0.6 else '#6a5a56'), emit=3.0 * (1 - f), rl=4, nocast=True))
    sc.lights.append(dict(pos=tuple(c + (0, 20, 30)), col='#ffb060', I=4, r=200))
    sc.add(box((0, 1.5, 6), (10, 3, 22), '#e8e8ec'))  # ship deck the hero stands on
    sc.add(box((0, 3.05, 6), (9.6, 0.1, 21.6), '#8a6a4a', mat='wood'))


def st_wasteland(sc, t):
    sc.sky = (C('#7a7060'), C('#c8b898')); sc.fog = C((0.7, 0.64, 0.55)); sc.fogd = 0.012
    sc.ambient = C((0.55, 0.5, 0.45)); sc.suncol = C((0.7, 0.6, 0.45))
    sc.add(box((0, -0.5, -40), (300, 1, 300), '#6a5e48', bg=True, mat='grass'))
    rr = random.Random(10)
    for j in range(18):  # dead trees
        x = rr.choice([-1, 1]) * rr.uniform(6, 30); z = rr.uniform(-80, 10)
        h = rr.uniform(5, 9)
        sc.add(box((x, h / 2, z), (0.6, h, 0.6), '#4a3a2a'))
        for k in range(3):
            sc.add(box((x + (k - 1) * 0.9, h * 0.75 + k * 0.5, z), (0.2, 2.6, 0.2), '#4a3a2a', R=rot(0, 0, (k - 1) * 40)))
    for j in range(8):  # piles of garbage nobody can break down
        x = rr.choice([-1, 1]) * rr.uniform(5, 20); z = rr.uniform(-60, 0)
        for k in range(14):
            s = rr.uniform(0.8, 2.0)
            sc.add(box((x + rr.uniform(-2.5, 2.5), s / 2 + k * 0.18, z + rr.uniform(-2.5, 2.5)), (s, s, s),
                       rr.choice(['#5a6a3a', '#3a3a3a', '#8a5a3a', '#c8c0a8', '#3a5a8a']), R=rot(rr.uniform(0, 90), 0, 0)))
    for j in range(30):  # wilted flowers
        x = rr.uniform(-8, 8); z = rr.uniform(-12, 4)
        if abs(x) < 2 and z > -2:
            continue
        sc.add(box((x, 0.4, z), (0.08, 0.8, 0.08), '#6a6a4a'))
        sc.add(box((x + 0.15, 0.7, z), (0.3, 0.2, 0.3), '#7a6a6a', R=rot(0, 0, 50)))


# name -> (builder, hero spot, camera bounds)
WORLD_STAGES = {
    'space':         (st_space, (0, 0, 2), None),
    'moon_breaks':   (st_moon_breaks, (0, 0, 2), None),
    'earth_ring':    (st_earth_ring, (0, 0, 2), None),
    'black_hole':    (st_black_hole, (0, 0, 2), None),
    'sun_dark':      (st_sun_dark, (0, 0, 2), None),
    'asteroid':      (st_asteroid, (0, 0, 2), None),
    'meteor_city':   (st_meteor_city, (0, 0, 4), None),
    'tsunami_city':  (st_tsunami_city, (0, 0, 4), None),
    'flood_city':    (st_flood_city, (0, 3.4, 4), None),
    'ash_city':      (st_ash_city, (0, 0, 4), None),
    'frozen_city':   (st_frozen_city, (0, 0.55, 4), None),
    'ring_sky':      (st_ring_sky, (0, 0, 4), None),
    'blackout_city': (st_blackout, (0, 0, 4), None),
    'volcano':       (st_volcano, (0, 0, 6), None),
    'deep_ocean':    (st_deep_ocean, (0, 0, 0), None),
    'whale':         (st_whale, (0, 0, 0), None),
    'earth_core':    (st_earth_core, (0, -2, 0), None),
    'ocean_impact':  (st_ocean_impact, (0, 3.1, 8), None),
    'wasteland':     (st_wasteland, (0, 0, 2), None),
}


def _orbit(target, dist, h, lt, dur, seed, fov=50, sweep=14):
    side = 1 if seed % 2 == 0 else -1
    p = _ease(lt / max(dur, 0.01))
    a = math.radians(side * (sweep * (p - 0.5)))
    tx, ty, tz = target
    return (tx + math.sin(a) * dist, ty + h, tz + math.cos(a) * dist), np.array(target, float), fov, 0


def event_camera(stage, kind, lt, dur, seed):
    """Frames the spectacle from one of three angles (picked per shot) so no two shots look the same."""
    ev = _event_camera(stage, kind, lt, dur, seed)
    if ev is None:
        return None
    pos, target, fov, roll = np.array(ev[0], float), np.array(ev[1], float), ev[2], ev[3]
    v = (seed // 7) % 3
    street = stage in ('meteor_city', 'tsunami_city', 'flood_city', 'ash_city', 'frozen_city', 'ring_sky', 'blackout_city')
    if v and street:  # buildings line the street: vary height and distance, never swing sideways into a wall
        if v == 1:
            pos = np.array([3.8 if seed % 2 else -3.8, 1.3, pos[2] + 3.0]); fov = fov + 4
        else:
            pos = np.array([0.0, pos[1] + 12.0, pos[2] + 6.0]); fov = fov - 4
        return pos, target, fov, roll
    if v:
        off = pos - target
        ang = math.radians(32 if v == 1 else -28)
        c, s_ = math.cos(ang), math.sin(ang)
        off = np.array([off[0] * c + off[2] * s_, off[1], -off[0] * s_ + off[2] * c])
        if v == 1:
            off = off * 0.72 + np.array([0, abs(off[1]) * 0.15 + 2.0, 0])   # closer, a little higher
            roll = roll + 4
        else:
            off = off * 1.12; off[1] = off[1] * 0.4                          # wider and lower
            fov = fov + 4
        pos = target + off
        if stage not in ('space', 'moon_breaks', 'earth_ring', 'black_hole', 'sun_dark', 'asteroid', 'earth_core'):
            pos[1] = max(pos[1], 1.2)
    return pos, target, fov, roll


def _event_camera(stage, kind, lt, dur, seed):
    """Frames the spectacle of a world stage, or None to use the normal hero camera."""
    p = _ease(lt / max(dur, 0.01))
    if stage in ('space', 'earth_ring', 'sun_dark', 'asteroid'):
        c = EARTH if stage != 'sun_dark' else (40, 30, -200)
        d = 190 - 25 * p if kind != 'reveal' else 120 + 110 * p
        return _orbit(c, d, 10, lt, dur, seed, fov=48)
    if stage == 'moon_breaks':
        return _orbit((10, 25, -170), 150 - 20 * p, 5, lt, dur, seed, fov=50)
    if stage == 'black_hole':
        return _orbit((0, 22, -140), 120 - 25 * p, 28, lt, dur, seed, fov=52)
    if stage == 'ring_sky':
        return (0, 34 + 6 * p, 30), np.array((0, 95, -250), float), 62, 0
    if stage in ('meteor_city', 'tsunami_city', 'ash_city'):
        look = {'meteor_city': (0, 40, -60), 'tsunami_city': (0, 18, -50), 'ash_city': (0, 30, -100), 'ring_sky': (0, 60, -200)}[stage]
        return (3 * (1 if seed % 2 else -1), 2.2 + 3 * p, 14), np.array(look, float), 62, 0
    if stage in ('flood_city', 'frozen_city', 'blackout_city'):
        return (8 - 6 * p, 22 - 4 * p, 26), np.array((0, 3, -20), float), 55, 0
    if stage == 'volcano':
        return (8 * (1 if seed % 2 else -1), 6 + 4 * p, 60 - 8 * p), np.array((0, 34, -95), float), 62, 0
    if stage in ('deep_ocean', 'whale'):
        return (9 - 4 * p, 3 + 2 * p, 14), np.array((0, 4, -6), float), 60, 0
    if stage == 'earth_core':
        return (0, 40, 48 - 10 * p), np.array((0, 40, -60), float), 66, 0
    if stage == 'ocean_impact':
        return (0, 60 + 20 * p, 70), np.array((0, 0, -140), float), 58, 0
    if stage == 'wasteland':
        return (10 - 4 * p, 7, 20), np.array((0, 2, -20), float), 55, 0
    return None
