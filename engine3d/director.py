"""Automatic 3D director: turns a scene plan + word timings into rendered shot files.

Every sentence becomes 1-2 shots (2-3 s each). Each shot picks a stage (a detailed 3D set),
characters with poses/faces, effects, props and a camera move (wide, medium, close-up, low
angle, over-the-shoulder, POV, drone, tracking, dutch), so the camera is always telling the
story. Output: one .bin/.json pair per shot for renderer.html.
"""
import json
import math
import os
import random
import re

import numpy as np

from . import engine
from .engine import export, C, rot, M4, box, lerp, ease, eout, shake, walk
from .psets import *  # noqa: F401,F403  (all sets, props, characters)
from .luxsets import lux_city, decorate

FPS = 30

# --------------------------------------------------------------------------- stages
# builder, hero spot, camera box (xmin, xmax, zmin, zmax, ymax) the camera must stay inside
STAGES = {
    'bedroom':      (lambda sc, t: bedroom(sc, lamp_on=True, lying=False), (0, 0, -1.5), (-7.4, 7.4, -7.4, 7.4, 7.6)),
    'livingroom':   (lambda sc, t: livingroom(sc, t, mom=False), (-3, 0, 0), (-8.4, 8.4, -7.4, 7.4, 7.6), 90),
    'school_hall':  (lambda sc, t: school(sc), (0, 0, 0), (-5.4, 5.4, -30, 30, 8.6)),
    'gym':          (lambda sc, t: gym(sc, t), (0, 0, 2), (-14, 14, -12, 12, 9.5)),
    'garage':       (lambda sc, t: garage(sc, t, door=0.0), (0, 0, -1.5), (-6.4, 6.4, -5.4, 5.4, 6.6)),
    'kitchen':      (lambda sc, t: kitchen(sc, t), (0, 0, -1), (-8.4, 8.4, -6.4, 6.4, 8.0)),
    'shop':         (lambda sc, t: shop_interior(sc, t), (0, 0, 0), (-8.4, 8.4, -7.4, 7.4, 8.4)),
    'cafeteria':    (lambda sc, t: cafeteria(sc, t), (0, 0, 2), (-12, 12, -10, 10, 8.4)),
    'diner':        (lambda sc, t: diner(sc, t), (0, 0, 0), (-8.4, 8.4, -7.4, 7.4, 8.0)),
    'party_room':   (lambda sc, t: party_room(sc, t), (3, 0, 1), (-8.4, 8.4, -7.4, 7.4, 7.6)),
    'city_day':     (lambda sc, t: lux_city(sc, t, night=False), (0, 0, 4), None),
    'city_night':   (lambda sc, t: lux_city(sc, t, night=True), (0, 0, 4), None),
    'suburb_night': (lambda sc, t: street(sc), (0, 0.24, 8), None),
    'suburb_day':   (lambda sc, t: street_day(sc, t), (0, 0, 14), None),
    'schoolyard':   (lambda sc, t: schoolyard(sc, t), (0, 0, 3), None),
    'festival':     (lambda sc, t: party_street(sc, t, crowd=True), (0, 0, 6), None),
    'highway':      (lambda sc, t: highway(sc, t), (0, 0, 6), None),
    'red_room':     (lambda sc, t: redroom(sc, t), (0, 0, 0), (-6.4, 6.4, -6.4, 6.4, 7.6)),
    'void':         (lambda sc, t: void(sc, t), (0, 0, 0), None),
}
STAGE_NAMES = list(STAGES)


def stage_info(name):
    e = STAGES[name if name in STAGES else 'city_day']
    return e[0], e[1], e[2], (e[3] if len(e) > 3 else 0)


def _rot_about(p, H, yaw):
    """Rotate point p around the hero spot H by the stage yaw (degrees)."""
    if not yaw:
        return np.array(p, float)
    a = math.radians(yaw); dx, dz = p[0] - H[0], p[2] - H[2]
    return np.array([H[0] + math.cos(a) * dx + math.sin(a) * dz, p[1], H[2] - math.sin(a) * dx + math.cos(a) * dz])

# ---------------------------------------------------------------------- characters
OUTFITS = {
    'hero':     dict(design='hoodie', skin='#f0c8a0', arms='#141418', shirt='#141418', pants='#0f0f12', cuff='#f0c8a0', hair='short', haircol='#16120f', shoes='#f6f6f6', slit=True),
    'friend':   dict(design='tee_logo', skin='#c98a5a', arms='#ff7a3a', shirt='#ff7a3a', pants='#24242e', cuff='#c98a5a', hair='curly', haircol='#1a1210', shoes='#ffd24a'),
    'girl':     dict(design='tee', skin='#f0c8a0', shirt='#ff6ab0', pants='#2a2a3a', cuff='#f0c8a0', hair='long', haircol='#3a2010', skirt='#7a5aff', shoes='#ffffff'),
    'villain':  dict(design='torn', skin='#a8b0b8', arms='#2a2a30', shirt='#2a2a30', pants='#141418', cuff='#a8b0b8', hair='bandana', haircol='#c42a2a', shoes='#111111'),
    'parent':   dict(design='collar', skin='#e8b890', arms='#4a7a5a', shirt='#4a7a5a', pants='#3a3a48', cuff='#e8b890', hair='bald_beard', haircol='#5a4030', shoes='#2a2020'),
    'mom':      dict(design='collar', skin='#e8c0a0', arms='#c84a6a', shirt='#c84a6a', pants='#3a3a48', cuff='#e8c0a0', hair='long', haircol='#5a3020', skirt='#5a4a8a', shoes='#2a2020'),
    'teacher':  dict(design='collar', skin='#d8a878', arms='#6a5a4a', shirt='#e8e0d0', pants='#4a4a52', cuff='#d8a878', hair='gray', haircol='#c8c8cc', shoes='#2a2020'),
    'grandma':  dict(design='collar', skin='#e8c0a0', arms='#8a5ab0', shirt='#8a5ab0', pants='#5a4a6a', cuff='#e8c0a0', hair='gray', haircol='#d8d8de', skirt='#6a4a8a', shoes='#3a2a2a'),
    'athlete':  dict(design='jersey', skin='#c98a5a', shirt='#d42a3a', pants='#1a1a22', cuff='#c98a5a', hair='durag', haircol='#111111', shoes='#ffffff'),
    'worker':   dict(design='flannel', skin='#e8b890', arms='#a83a2a', shirt='#a83a2a', pants='#3a4a6a', cuff='#e8b890', hair='cap', haircol='#d8a020', shoes='#4a3020'),
    'cop':      dict(design='collar', skin='#d8a878', arms='#1a2a5a', shirt='#1a2a5a', pants='#141a30', cuff='#d8a878', hair='cap', haircol='#1a2a5a', shoes='#111111'),
    'kid':      dict(design='tee', skin='#f0c8a0', shirt='#4ad88a', pants='#3a3a52', cuff='#f0c8a0', hair='short', haircol='#2a1a10', shoes='#ff5a5a'),
}
CROWD_SHIRTS = ['#ff5a8a', '#5ac8ff', '#ffd24a', '#8aff6a', '#c08aff', '#ff9a3a', '#e8e8e8']
GOLDC = '#e2b23c'


def drip(out, base, hm, arms):
    """Hero jewellery: three gold chains (short, medium, long with a diamond pendant), iced watches, diamond studs."""
    t = engine.TIME[0]
    for i, (depth, w) in enumerate(((0.45, 0.48), (0.8, 0.6), (1.15, 0.7))):
        n = 13 + i * 2
        for k in range(n):
            u = -1 + 2 * k / (n - 1)
            x = u * w; y = 3.97 - (1 - u * u) * depth
            ang = math.degrees(math.atan2(2 * u * depth, 1)) * 0.55
            out.append(box((x, y, 0.55 + 0.012 * i), (0.12, 0.09, 0.08), GOLDC, parent=base, rl=2, emit=0.12, R=rot(0, 0, ang)))
    out.append(box((0, 2.75, 0.6), (0.36, 0.4, 0.08), GOLDC, parent=base, rl=2, emit=0.15))
    out.append(box((0, 2.75, 0.65), (0.2, 0.2, 0.04), '#ffffff', parent=base, R=rot(0, 0, 45), emit=1.6 + 0.8 * math.sin(t * 7), shade=False))
    for key in ('la', 'ra'):
        el = arms[key]
        out.append(box((0, -0.58, 0), (0.98, 0.22, 0.98), '#e9eef6', parent=el, rl=4, emit=0.5))
        for j, (dx, dz) in enumerate(((0, 0.5), (0.5, 0), (-0.5, 0), (0, -0.5))):
            tw = 1.2 + 1.5 * max(0.0, math.sin(t * 9 + j * 1.7 + (key == 'ra') * 2))
            out.append(box((dx, -0.58, dz), (0.16, 0.16, 0.16), '#ffffff', parent=el, emit=tw, shade=False, nocast=True))
    for sx in (-1, 1):
        out.append(box((sx * 0.67, 0.5, 0.05), (0.08, 0.14, 0.14), '#ffffff', parent=hm, emit=1.8, shade=False, nocast=True))


NICE = [  # extras dress sharp and never like the hero (no all-black)
    dict(design='collar', shirt='#f4f4f4', arms='#1f2f5a', pants='#1f2f5a', shoes='#5a3420'),          # navy suit
    dict(design='collar', shirt='#f4f4f4', arms='#6a1f2a', pants='#6a1f2a', shoes='#2a1a12'),          # burgundy suit
    dict(design='collar', shirt='#2a2a30', arms='#e8dcc0', pants='#e8dcc0', shoes='#f4f4f4'),          # cream suit
    dict(design='collar', shirt='#f4f4f4', arms='#1f5a46', pants='#1f5a46', shoes='#3a2418'),          # emerald suit
    dict(design='tee_logo', shirt='#f4efe4', arms='#f4efe4', pants='#c8a87a', shoes='#f4f4f4'),         # cream tee, khakis
    dict(design='collar', shirt='#ffffff', arms='#6a4228', pants='#2a3348', shoes='#6a4228'),          # leather jacket
    dict(design='tee', shirt='#ff8fb0', arms='#ff8fb0', pants='#f4f4f4', shoes='#ffd24a'),             # pastel fit
    dict(design='collar', shirt='#f4f4f4', arms='#8a8f98', pants='#8a8f98', shoes='#1a1a1e'),          # grey suit
    dict(design='jersey', shirt='#2a6ad8', pants='#f4f4f4', shoes='#d42a3a'),                          # jersey + whites
    dict(design='tee_logo', shirt='#7ac8ff', arms='#7ac8ff', pants='#3a4a6a', shoes='#f4f4f4'),         # sky blue fit
]
NICE_DRESS = ['#c84a7a', '#e8c24a', '#4a8ae8', '#e85a3a', '#8a5ad8', '#f4f4f4', '#3ab89a']
SKINS = ['#f0c8a0', '#c98a5a', '#8a5a3a', '#e8b890', '#a8704a', '#f4d0b0']
HAIRS = [('short', '#2a1a10'), ('curly', '#1a1210'), ('durag', '#c42a2a'), ('cap', '#1f2f5a'), ('short', '#d8b060'), ('beanie', '#e8c24a')]


def nice_outfit(c, k):
    """Pick a sharp, varied outfit for an extra, keeping role hints (girl/mom -> dress, cop stays cop, villain flashy)."""
    o = c.get('outfit', 'friend')
    if o in ('cop',):
        return dict(OUTFITS['cop'])
    h = (sum(map(ord, o)) + k * 7) % 997
    skin = SKINS[h % len(SKINS)]
    if o == 'villain':
        return dict(design='collar', skin=skin, shirt='#111', arms='#7a1fa8', pants='#7a1fa8', cuff=skin, hair='bandana', haircol='#c42a2a', shoes='#f5c542', chain=True)
    if o in ('girl', 'mom', 'grandma'):
        dress = NICE_DRESS[h % len(NICE_DRESS)]
        return dict(design='tee', skin=skin, shirt=dress, arms=skin, pants='#2a2a3a', cuff=skin, hair='gray' if o == 'grandma' else 'long',
                    haircol='#d8d8de' if o == 'grandma' else ['#3a2010', '#1a1210', '#d8a040', '#7a2a1a'][h % 4], skirt=dress, shoes='#f4f4f4', chain='silver')
    base = dict(NICE[h % len(NICE)])
    hair, hc = HAIRS[(h // 3) % len(HAIRS)]
    base.update(skin=skin, cuff=skin, hair='gray' if o in ('teacher', 'parent', 'grandma') else hair, haircol='#c8c8cc' if o == 'teacher' else hc)
    if h % 3 == 0:
        base['chain'] = 'silver'
    return base

FACE = {'happy': 'smile', 'smile': 'smile', 'excited': 'grin', 'laugh': 'snicker', 'neutral': 'neutral',
        'sad': 'sad', 'crying': 'tears', 'worried': 'worried', 'scared': 'scared', 'terrified': 'terror',
        'shocked': 'terror', 'angry': 'roar', 'shouting': 'shout', 'smug': 'smirk', 'determined': 'focus',
        'powerful': 'power', 'tired': 'sleep', 'blank': 'blank', 'panic': 'choke'}
ACTIONS = ['idle', 'talk', 'walk', 'run', 'point', 'cheer', 'shock', 'scared', 'think', 'sad', 'phone',
           'jump', 'punch', 'dance', 'fall', 'lie', 'float', 'wave', 'sit']
SHOTS = ['wide', 'medium', 'close', 'low', 'ots', 'pov', 'drone', 'track', 'dutch', 'reveal', 'ecu', 'detail']
FX = ['rain', 'snow', 'fire', 'smoke', 'confetti', 'fireworks', 'sparkles', 'money', 'shake']


def pose_for(action, t, lt, k=0):
    s = math.sin(t * 6 + k)
    if action == 'talk':
        return dict(ra=30 + 18 * abs(math.sin(t * 3.1 + k)), re=45, la=12, rar=-10)
    if action in ('walk', 'run'):
        return walk(t + k, 9 if action == 'run' else 6, 40 if action == 'run' else 28) | (dict(lean=12) if action == 'run' else {})
    if action == 'point':
        return dict(ra=92, re=0, ray=-8, la=8)
    if action == 'cheer':
        return dict(ra=134 + 4 * s, la=134 - 4 * s, re=4, le=4, y=abs(math.sin(t * 7 + k)) * 0.6)
    if action == 'shock':
        return dict(ra=128, la=128, re=55, le=55, lean=-8, hp=-6)
    if action == 'scared':
        return dict(ra=105, la=105, re=95, le=95, lean=-12, ll=-6, rl=6, hp=8)
    if action == 'think':
        return dict(ra=118, re=132, rar=12, la=12, hy=10, hp=-6)
    if action == 'sad':
        return dict(ra=4, la=4, hp=18, lean=4)
    if action == 'phone':
        return dict(ra=150)
    if action == 'jump':
        return dict(ra=120, la=120, re=10, le=10, ll=30, rl=30, lk=50, rk=50, y=abs(math.sin(t * 4.2 + k)) * 2.4)
    if action == 'punch':
        p = math.sin(t * 10 + k) > 0
        return dict(ra=92 if p else 40, re=0 if p else 100, la=40 if p else 92, le=100 if p else 0, lean=8)
    if action == 'dance':
        return dict(ra=90 + 40 * s, la=90 - 40 * s, re=30, le=30, hy=15 * s, y=abs(s) * 0.3, lean=6 * s)
    if action == 'wave':
        return dict(ra=128 + 10 * math.sin(t * 9), re=20, rar=-10 * math.sin(t * 9))
    if action == 'float':
        return dict(ra=70 + 8 * s, la=70 - 8 * s, re=20, le=20, ll=10, rl=-10, y=2.2 + 0.4 * math.sin(t * 1.8 + k))
    if action == 'sit':
        return dict(sit=True, ll=90, rl=90, y=0.45, ra=30, la=30, re=60, le=60)
    return None


def put_character(sc, c, pos, yaw, t, lt, k, scale=1.0):
    if c.get('role') == 'hero':
        out = dict(OUTFITS['hero']); out['extra'] = drip
    else:
        out = nice_outfit(c, k)
    act = c.get('action', 'idle')
    face = FACE.get(c.get('mood', 'neutral'), 'neutral')
    if act in ('fall', 'lie'):
        tilt = 90 if act == 'lie' else min(90, lt * 260)
        character(sc, (pos[0], pos[1] + 0.55 * (tilt / 90), pos[2]), yaw=yaw, face=face if act == 'fall' else 'sleep',
                  root_R=rot(yaw, -tilt, 0), scale=scale, **out)
        return
    pz = pose_for(act, t, lt, k)
    p = list(pos)
    if act == 'sit':
        chair(sc, (pos[0], pos[1], pos[2]), yaw=yaw)
    if act in ('walk', 'run'):
        sp = 2.6 if act == 'run' else 1.2
        a = math.radians(yaw)
        p[0] += math.sin(a) * sp * (lt - 1.0)
        p[2] += math.cos(a) * sp * (lt - 1.0)
    character(sc, tuple(p), yaw=yaw, pose=pz, face=face, scale=scale, phone='r' if act == 'phone' else None, **out)


# -------------------------------------------------------------------------- effects
def sparkles(sc, center, t, n=24, r=3.0, col='#fff6a0'):
    rr = random.Random(7)
    for j in range(n):
        a = rr.uniform(0, 6.28) + t * 0.6
        h = rr.uniform(0, 5)
        q = 0.5 + 0.5 * math.sin(t * 6 + j)
        sc.add(box((center[0] + math.cos(a) * r * rr.uniform(0.3, 1), center[1] + h, center[2] + math.sin(a) * r * rr.uniform(0.3, 1)),
                   (0.14 * q + 0.04,) * 3, col, emit=2.5, shade=False, nocast=True, rl=4))


def money_rain(sc, center, t, n=40):
    rr = random.Random(3)
    for j in range(n):
        x = center[0] + rr.uniform(-6, 6); z = center[2] + rr.uniform(-4, 4)
        y = 12 - ((t * rr.uniform(2, 3.5) + rr.uniform(0, 12)) % 12)
        sc.add(box((x, y, z), (0.8, 0.02, 0.4), '#5ac85a', R=rot(t * 90 + j * 40, 20 * math.sin(t * 3 + j), 0), rl=1, nocast=True))


def apply_fx(sc, fx, center, t):
    for f in fx or []:
        if f == 'rain':
            add_rain(sc, t, center, n=170)
        elif f == 'snow':
            snow(sc, t, center)
        elif f == 'fire':
            fire(sc, (center[0] - 3.5, 0, center[2] - 2.5), t, 1.3); fire(sc, (center[0] + 4, 0, center[2] - 3), t + 0.4, 1.0)
            sc.lights.append(dict(pos=(center[0], 3, center[2] - 2), col='#ff8a3a', I=1.4, r=9))
        elif f == 'smoke':
            smoke(sc, (center[0] + 2, 0, center[2] - 3), t, 1.4)
        elif f == 'confetti':
            confetti(sc, t, center)
        elif f == 'fireworks':
            fireworks(sc, t, [(center[0] - 6, 16, center[2] - 18), (center[0] + 7, 19, center[2] - 22)])
        elif f == 'sparkles':
            sparkles(sc, center, t)
        elif f == 'money':
            money_rain(sc, center, t)


PROPS = ['car', 'dog', 'cash', 'box', 'jar', 'phone_big', 'trophy', 'tv']


def apply_props(sc, props, H, t, syaw=0):
    def R(x, y, z):
        return tuple(_rot_about((x, y, z), H, syaw))
    for k, pname in enumerate(props or []):
        side = -1 if k % 2 == 0 else 1
        if pname == 'car':
            car(sc, R(H[0] + side * 6.5, 0, H[2] - 2.5), yaw=90, color=['#c42a2a', '#2a8ad8', '#f2c230'][k % 3])
        elif pname == 'dog':
            dog(sc, R(H[0] + side * 2.4, 0, H[2] + 1.0), yaw=-side * 30, t=t)
        elif pname == 'cash':
            bills(sc, R(H[0] + side * 2.2, 0.05, H[2] + 1.4), n=10)
        elif pname == 'box':
            pbox_stack(sc, R(H[0] + side * 2.6, 0, H[2] + 0.5), 3)
        elif pname == 'jar':
            jar(sc, R(H[0] + side * 2.0, 2.4, H[2] + 1.0), glow=0.6)
            sc.add(box(R(H[0] + side * 2.0, 1.2, H[2] + 1.0), (1.6, 2.4, 1.6), '#7a4a2a', rl=1))
        elif pname == 'trophy':
            sc.add(box(R(H[0] + side * 2.2, 1.2, H[2] + 1.0), (1.4, 2.4, 1.4), '#f4f4f4', rl=1))
            sc.add(box(R(H[0] + side * 2.2, 3.0, H[2] + 1.0), (0.9, 1.2, 0.9), '#f5c542', emit=0.5, rl=4))
        elif pname == 'tv':
            sc.add(box(R(H[0] + side * 3.0, 3.2, H[2] - 2.0), (3.6, 2.2, 0.3), '#111', rl=1))
            sc.add(box(R(H[0] + side * 3.0, 3.2, H[2] - 1.84), (3.3, 1.9, 0.02), '#6ab8ff', emit=1.4, shade=False))


# ------------------------------------------------------------------------- cameras
def clamp_cam(p, bounds):
    if not bounds:
        return np.array([p[0], max(0.6, p[1]), p[2]])
    xmin, xmax, zmin, zmax, ymax = bounds
    return np.array([min(max(p[0], xmin), xmax), min(max(p[1], 0.8), ymax), min(max(p[2], zmin), zmax)])


def camera(kind, H, lt, dur, seed, bounds, other=None, hero_scale=1.0):
    hx, hy, hz = H
    s = hero_scale
    head = np.array([hx, hy + 4.65 * s, hz])
    chest = np.array([hx, hy + 3.4 * s, hz])
    p = ease(lt / max(dur, 0.01))
    side = 1 if seed % 2 == 0 else -1
    if kind == 'wide':
        a = lerp((hx + side * 4 * s, hy + 6.5 * s, hz + 15 * s), (hx + side * 3 * s, hy + 5.6 * s, hz + 12.5 * s), p)
        return a, chest + (0, 0.5 * s, -2), 58, 0
    if kind == 'medium':
        ang = math.radians(side * (12 + 10 * p))
        d = 8.2 * s
        a = (hx + math.sin(ang) * d, hy + 4.3 * s, hz + math.cos(ang) * d)
        return a, chest + (0, 0.6 * s, 0), 46, 0
    if kind == 'close':
        d = lerp(5.6 * s, 4.6 * s, p)
        return (hx + side * 0.7 * s, hy + 4.9 * s, hz + d), head, 34, 0
    if kind == 'low':
        return lerp((hx + side * 1.6 * s, hy + 0.9, hz + 5.8 * s), (hx + side * 1.2 * s, hy + 0.8, hz + 5.0 * s), p), head + (0, 0.4 * s, 0), 60, side * 4
    if kind == 'ecu':  # extreme close-up: the face fills the frame
        d = lerp(3.4 * s, 2.9 * s, p)
        return (hx + side * 0.25 * s, hy + 4.75 * s, hz + d), head + (0, 0.05 * s, 0), 30, 0
    if kind == 'detail':  # drip shot: chains and watch, slow orbit
        ang = math.radians(side * (25 - 30 * p))
        d = 3.6 * s
        return (hx + math.sin(ang) * d, hy + 3.3 * s, hz + math.cos(ang) * d), np.array([hx, hy + 3.0 * s, hz]), 34, side * 3
    if kind == 'dutch':
        return lerp((hx - side * 2.2 * s, hy + 3.6 * s, hz + 6.4 * s), (hx - side * 1.8 * s, hy + 3.8 * s, hz + 5.6 * s), p), head, 48, side * (14 + 4 * p)
    if kind == 'drone':
        return lerp((hx + 2, hy + 22 * s, hz + 10 * s), (hx + 1, hy + 17 * s, hz + 7 * s), p), chest, 55, 0
    if kind == 'track':
        x = lerp(hx - side * 5 * s, hx + side * 1.0 * s, p)
        return (x, hy + 3.8 * s, hz + 7.5 * s), chest + (side * 1.2 * p, 0.5, 0), 50, 0
    if kind == 'reveal':
        # starts tight on the hero, pulls back fast to show the whole world
        d = lerp(4.5 * s, 18 * s, eout(lt / max(dur, 0.01)))
        return (hx + side * 0.5 * d * 0.25, hy + 4.4 * s + d * 0.25, hz + d), chest + (0, 0.3 * s, -d * 0.12), 52, 0
    if kind in ('ots', 'pov') and other is not None:
        ox, oy, oz = other
        if kind == 'ots':  # over the other character's shoulder, looking at the hero
            return lerp((ox + 3.0, oy + 5.6, oz + 4.4), (ox + 2.7, oy + 5.5, oz + 3.9), p), head, 44, 0
        # pov: from the hero's eyes looking at the other character
        return (hx, hy + 4.7 * s, hz + 0.9 * s) + shake(lt, 0.03, seed=seed), np.array([ox, oy + 4.3, oz]), 64, 0
    return camera('medium', H, lt, dur, seed, bounds, other, hero_scale)


# ------------------------------------------------------------------- occlusion
def _obstacles(boxes):
    """Inverse transforms + half sizes of set boxes, for camera line-of-sight tests."""
    if not boxes:
        return None
    inv = np.stack([np.linalg.inv(b.M) for b in boxes])
    half = np.stack([b.size * 0.5 for b in boxes])
    return inv, half


def _first_hit(obs, a, b):
    """Distance along a->b to the first box hit (slab test in each box's local frame), or None."""
    if obs is None:
        return None
    inv, half = obs
    d = b - a
    L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    a4 = np.append(a, 1.0)
    la = np.einsum('nij,j->ni', inv, a4)[:, :3]
    ld = np.einsum('nij,j->ni', inv[:, :3, :3], d)
    with np.errstate(divide='ignore', invalid='ignore'):
        t1 = (-half - la) / ld
        t2 = (half - la) / ld
    tmin = np.nanmax(np.minimum(t1, t2), axis=1)
    tmax = np.nanmin(np.maximum(t1, t2), axis=1)
    inside = np.all(np.abs(la) <= half, axis=1)
    hit = (tmax >= np.maximum(tmin, 0)) & (tmin <= 0.97) & ~inside
    hit |= inside
    if not hit.any():
        return None
    t = np.where(inside, 0.0, np.maximum(tmin, 0))[hit].min()
    return float(t) * L


def unblock(cam, target, obs, bounds):
    """If set geometry blocks the view, try the mirrored side of the hero, else move in front of the blocker."""
    cam = np.array(cam, float); target = np.array(target, float)
    dist = np.linalg.norm(cam - target)
    if _first_hit(obs, cam, target) is None:
        return cam
    off = cam - target
    for m in ((1, 1, -1), (-1, 1, 1), (-1, 1, -1)):
        c2 = clamp_cam(target + off * np.array(m), bounds)
        if np.linalg.norm(c2 - target) > 0.6 * dist and _first_hit(obs, c2, target) is None:
            return c2
    c = cam
    for _ in range(4):
        h = _first_hit(obs, c, target)
        if h is None:
            break
        dvec = (target - c) / max(np.linalg.norm(target - c), 1e-6)
        c = c + dvec * (h + 0.5)
        if np.linalg.norm(target - c) < 2.2:
            c = target - dvec * 2.2
            break
    return c


LOOKS = {  # colour grade per sentence (post-process)
    'normal': {},
    'gray': dict(sat=0.0, con=0.1),
    'night': dict(dark=0.3, tint=[0.55, 0.65, 1.0], tint_a=0.25, sat=0.9),
    'red': dict(tint=[1.0, 0.25, 0.2], tint_a=0.3, vig=0.6),
    'warm': dict(tint=[1.0, 0.75, 0.45], tint_a=0.15, sat=1.25),
    'cold': dict(tint=[0.55, 0.8, 1.0], tint_a=0.2, sat=0.85),
    'dream': dict(bloom=1.4, sat=0.8, tint=[1.0, 0.85, 1.0], tint_a=0.15),
}


# --------------------------------------------------------------------------- frames
def build_frame(shot, lt, gt):
    st_name = shot['stage'] if shot['stage'] in STAGES else 'city_day'
    builder, H, bounds, syaw = stage_info(st_name)
    sc = engine.Scene()
    builder(sc, gt)
    decorate(sc, st_name, gt)
    obs = _obstacles([b for b in sc.boxes if not (b.size[1] < 0.3 and b.M[1, 3] < 0.4)]) if bounds else None
    if st_name in ('void', 'red_room'):  # these sets are moody; keep the hero readable
        sc.ambient = np.maximum(np.array(sc.ambient, float), 0.22)
        sc.lights.append(dict(pos=(H[0] + 2.5, H[1] + 7, H[2] + 5), col='#ffffff', I=2.2, r=12))
    scale = float(shot.get('hero_scale', 1.0) or 1.0)
    chars = shot.get('characters') or [{'role': 'hero', 'outfit': 'hero', 'action': 'idle', 'mood': 'neutral'}]
    kind = shot['shot']
    others = [c for c in chars if c.get('role') != 'hero']
    hero = next((c for c in chars if c.get('role') == 'hero'), None)
    other_pos = None
    face_pair = kind in ('ots', 'pov') and others
    if face_pair:
        other_pos = tuple(_rot_about((H[0] + 0.9, H[1], H[2] + 4.6 * max(1.0, scale * 0.8)), H, syaw))
        others = [dict(others[0], action='talk' if others[0].get('action') in ('float', 'jump', 'run', 'walk', 'fall', 'lie') else others[0].get('action'))] + others[1:]
    k = 0
    if hero is not None and not (kind == 'pov'):
        put_character(sc, hero, H, syaw, gt, lt, 0, scale)
    spots = [(-3.4, 0.6), (3.4, 0.6), (-6.2, -1.6), (6.2, -1.6), (-1.8, -3.6), (1.8, -3.6), (-8, -3), (8, -3)]
    for j, c in enumerate(others[:8]):
        if face_pair and j == 0:
            pos = other_pos
            yaw = math.degrees(math.atan2(H[0] - pos[0], H[2] - pos[2]))
        else:
            dx, dz = spots[j % len(spots)]
            pos = tuple(_rot_about((H[0] + dx, H[1], H[2] + dz), H, syaw))
            look = _rot_about((H[0], 0, H[2] + 3), H, syaw)
            yaw = math.degrees(math.atan2(look[0] - pos[0], look[2] - pos[2]))
        put_character(sc, c, pos, yaw, gt, lt, j + 1)
        k += 1
    apply_props(sc, shot.get('props'), H, gt, syaw)
    apply_fx(sc, shot.get('fx'), H, gt)
    act = (hero or {}).get('action', 'idle')
    yo = {'float': 2.2 + 0.4 * math.sin(gt * 1.8), 'jump': 1.0, 'fall': -3.4, 'lie': -3.6, 'sit': -0.6}.get(act, 0.0)
    camH = (H[0], H[1] + yo * scale, H[2])
    if act == 'sit' and kind in ('close', 'low', 'dutch', 'track'):
        kind = 'medium' if kind != 'low' else 'wide'
    if act in ('fall', 'lie') and kind in ('close', 'low', 'dutch', 'track', 'medium'):
        kind = 'drone' if kind in ('close', 'medium') else 'wide'
        camH = (H[0], H[1] - 1.0, H[2])
    local_other = tuple(_rot_about(other_pos, H, -syaw)) if other_pos is not None else None
    cam_pos, target, fov, roll = camera(kind, camH, lt, shot['dur'], shot['seed'], None, local_other, scale)
    cam_pos = clamp_cam(_rot_about(cam_pos, H, syaw), bounds)
    target = _rot_about(np.array(target, float), H, syaw)
    if obs is not None and kind != 'pov':
        cam_pos = unblock(cam_pos, target, obs, bounds)
    if 'shake' in (shot.get('fx') or []):
        cam_pos = cam_pos + shake(lt, 0.09, seed=shot['seed'])
    # living handheld drift
    dp = np.array([math.sin(gt * 0.6) * 0.03, math.sin(gt * 0.75 + 2) * 0.02, 0])
    sc.cam = dict(pos=cam_pos + dp, target=np.array(target, float) + dp * 0.6, fov=fov, roll=roll)
    return sc


# -------------------------------------------------------------------------- timeline
def split_sentences(text):
    return [p for p in re.split(r'(?<=[.!?])\s+', text.strip()) if p.strip()]


def plan_shots(plan, words, duration, seed=1):
    """Sentence timings from word timings; each sentence -> 1+ shots of <= 2.8 s, varied camera."""
    sents = split_sentences(plan['script'])
    counts = [len(s.split()) for s in sents]
    total = max(1, sum(counts))
    n = len(words)
    starts, cum = [], 0
    for c in counts:
        i = min(n - 1, int(round(cum * n / total))) if n else 0
        starts.append(max(0.0, words[i]['start'] - 0.08) if n else cum / total * duration)
        cum += c
    starts[0] = 0.0
    shots, rr, last = [], random.Random(seed), None
    for k, sc in enumerate(plan['scenes'][:len(sents)]):
        st = starts[k]
        en = starts[k + 1] if k + 1 < len(starts) else duration
        wanted = [s for s in (sc.get('shots') or []) if s in SHOTS] or ['medium']
        pieces = max(1, int(math.ceil((en - st) / 2.8)))
        seg = (en - st) / pieces
        for j in range(pieces):
            kind = wanted[j % len(wanted)]
            if kind == last:  # never repeat the same framing back to back
                kind = rr.choice([s for s in ('medium', 'close', 'low', 'wide', 'dutch') if s != last])
            if k == 0 and j == 0:
                kind = wanted[0] if wanted[0] in ('close', 'low', 'dutch', 'pov') else 'close'
            if kind in ('ots', 'pov') and not [c for c in sc.get('characters', []) if c.get('role') != 'hero']:
                kind = 'close'
            shots.append(dict(sc, shot=kind, start=st + j * seg, dur=seg, seed=rr.randint(0, 9999), sentence=k))
            last = kind
    return shots


def caption_at(words, t, keys):
    for i, w in enumerate(words):
        nx = words[i + 1]['start'] if i + 1 < len(words) else w['end'] + 0.45
        end = min(nx, w['end'] + 0.35)
        if w['start'] - 0.02 <= t < max(end, w['start'] + 0.12):
            raw = re.sub(r'["“”]', '', w['word']).strip()
            txt = raw.rstrip(',.…?:;!')
            key = re.sub(r'[^a-z0-9]', '', txt.lower()) in keys
            return txt, t - w['start'], key
    return None, 0, False


def export_all(plan, words, duration, outdir, seed=1, hud=None, end_text='FOLLOW FOR PART 2', title_lines=None):
    os.makedirs(outdir, exist_ok=True)
    words = [w for w in words if re.search(r'[A-Za-z0-9]', w['word'])]
    shots = plan_shots(plan, words, duration, seed)
    keys = {re.sub(r'[^a-z0-9]', '', k.lower()) for k in plan.get('keywords', [])}
    hud_vals = plan.get('hud_values') or []
    names = []
    for i, shot in enumerate(shots):
        f0 = round(shot['start'] * FPS)
        f1 = round((shots[i + 1]['start'] if i + 1 < len(shots) else duration) * FPS)
        texlist, frames, blobs, off = [], [], [], 0
        for fi in range(f0, max(f0 + 1, f1)):
            gt = fi / FPS
            lt = gt - shot['start']
            engine.TIME[0] = gt
            sc = build_frame(shot, lt, gt)
            arr, meta = export(sc, texlist)
            meta['o'] = off; meta['n'] = len(arr); off += arr.size
            cut = max(0.0, 1 - lt / 0.12) if i > 0 else max(0.0, 1 - lt / 0.35)
            post = dict(exp=0.97, zb=0.35 * cut, vig=0.36, tint=[1, 1, 1], tint_a=0.0, flash=0.12 * cut, ca=0.0,
                        grain=0.025, sat=1.18, dark=0.0, bloom=0.75)
            if shot['stage'] in ('red_room', 'void'):
                post['vig'] = 0.55
            post.update(LOOKS.get(shot.get('look') or 'normal', {}))
            meta['post'] = post
            txt, age, key = caption_at(words, gt, keys)
            if txt:
                meta['cap'] = dict(t=txt.upper() if key else txt, col=[255, 140, 30] if key else [255, 216, 74],
                                   pop=1.0 + (0.55 if key else 0.3) * math.exp(-age * 16), st=1)
            if hud:
                v = hud_vals[min(shot['sentence'], len(hud_vals) - 1)] if hud_vals else ''
                prev = hud_vals[min(shot['sentence'] - 1, len(hud_vals) - 1)] if hud_vals and shot['sentence'] > 0 else v
                meta['hud'] = dict(tag=hud.get('tag', ''), sub=hud.get('sub', ''), label=hud.get('label', ''),
                                   value=str(v), col=hud.get('col', '#ff4a3a'),
                                   pulse=max(0.0, 1 - (lt / 0.4)) if v != prev and lt < 0.4 else 0.0)
            if title_lines and gt < 2.2:
                meta['title'] = dict(lines=title_lines, a=min(1.0, gt / 0.2) * min(1.0, (2.2 - gt) / 0.25), hl='#ffd84a')
            if duration - gt < 1.9 and end_text:
                meta['end'] = dict(text=end_text, a=min(1.0, (1.9 - (duration - gt)) / 0.3))
            frames.append(meta); blobs.append(arr)
        name = f's{i:03d}'
        np.concatenate([b.reshape(-1) for b in blobs]).astype(np.float32).tofile(os.path.join(outdir, name + '.bin'))
        json.dump(dict(frames=frames, textures=texlist), open(os.path.join(outdir, name + '.json'), 'w'))
        names.append(name)
    return names, shots
