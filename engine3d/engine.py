import os
import numpy as np, math, random, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
SS = 2
FONTS = os.environ.get('FONT_DIR', '/usr/share/fonts/truetype/google-fonts/ofl')
FONT_ANTON = os.path.join(FONTS, 'anton/Anton-Regular.ttf')
FONT_SERIF = os.path.join(FONTS, 'cardo/Cardo-Italic.ttf')
FONT_SERIF_B = os.path.join(FONTS, 'cardo/Cardo-Bold.ttf')
FONT_POPPINS = os.environ.get('FONT_POPPINS', os.path.join(os.path.dirname(FONTS), 'Poppins-Bold.ttf'))
TEXDIR = os.environ.get('TEX_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work', 'tex'))
os.makedirs(TEXDIR, exist_ok=True)
TIME = [0.0]

MAT = dict(plastic=0, wood=1, carpet=2, grass=3, concrete=4, tile=6, wall=7, locker=8, asphalt=9, checker=10, facade=11, curtain=12, brick=13)

def hexc(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(ch * 2 for ch in h)
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])

def C(c):
    if isinstance(c, str): return hexc(c)
    return np.array(c, float)

def rot(yaw=0, pitch=0, roll=0):
    y, p, r = map(math.radians, (yaw, pitch, roll))
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    Rz = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz

def M4(pos=(0, 0, 0), R=None):
    m = np.eye(4)
    if R is not None: m[:3, :3] = R
    m[:3, 3] = pos
    return m

FACE_IDX = dict(px=0, nx=1, py=2, ny=3, pz=4, nz=5)
_texcache = {}

def tex_name(img):
    k = id(img)
    if k in _texcache and _texcache[k][0] is img: return _texcache[k][1]
    im = img.convert('RGBA')
    h = hashlib.md5(im.tobytes() + str(im.size).encode()).hexdigest()[:16]
    fn = f'{TEXDIR}/{h}.png'
    if not os.path.exists(fn): im.save(fn)
    _texcache[k] = (img, h)
    return h

class Box:
    __slots__ = ('M', 'size', 'color', 'bg', 'decals', 'tex', 'emit', 'tile', 'jitter', 'faces', 'seed', 'shade', 'mat', 'rl', 'nocast')
    def __init__(self, M, size, color, bg=False, emit=0.0, tile=None, jitter=0.0, faces=None, shade=True, mat=0, rl=0, nocast=False):
        self.M = M; self.size = np.array(size, float); self.color = C(color); self.bg = bg
        self.decals = {}; self.tex = {}; self.emit = emit; self.shade = shade
        self.mat = MAT[mat] if isinstance(mat, str) else mat; self.rl = rl; self.nocast = nocast or bg

def box(pos, size, color, R=None, parent=None, **kw):
    for k in ('tile', 'jitter'): kw.pop(k, None)
    m = M4(pos, R)
    if parent is not None: m = parent @ m
    return Box(m, size, color, **kw)

class Scene:
    def __init__(self):
        self.boxes = []; self.lights = []; self.blobs = []
        self.sky = (C('#7fb8ff'), C('#dff0ff')); self.ambient = C((0.55, 0.55, 0.6))
        self.sun = np.array([-0.4, -1.0, -0.6]); self.suncol = C((0.6, 0.58, 0.5))
        self.fog = C('#000000'); self.fogd = 0.0
        self.cam = dict(pos=(0, 5, 10), target=(0, 3, 0), fov=50, roll=0)
        self.static = None; self.overlays = []; self.shadow = True; self.she = 22; self.shc = None; self.tags = []; self.stars = 0.0
    def add(self, *bs):
        for b in bs:
            if isinstance(b, (list, tuple)): self.add(*b)
            elif b is not None: self.boxes.append(b)
        return bs

_SROWS = {}
def _rows(boxes, texlist):
    rows = []
    for b in boxes:
        tl = -1; tf = 0; te = 0
        if b.tex:
            fname, (img, emissive) = next(iter(b.tex.items()))
            nm = tex_name(img)
            if nm not in texlist: texlist.append(nm)
            assert len(texlist) <= 96, 'texture overflow'
            tl = texlist.index(nm); tf = FACE_IDX[fname]; te = 1 if emissive else 0
        flags = tf | (b.rl << 3) | ((0 if b.shade else 1) << 6) | ((1 if b.nocast else 0) << 7) | (te << 8)
        rows.append(np.concatenate([b.M.T.reshape(-1), b.size, np.clip(b.color, 0, 4), [b.emit, b.mat, tl, flags]]))
    return np.array(rows, np.float32) if rows else np.zeros((0, 26), np.float32)
def export(sc, texlist):
    arr = _rows(sc.boxes, texlist)
    if sc.static is not None:
        k = (id(sc.static), id(texlist))
        if k not in _SROWS: _SROWS.clear(); _SROWS[k] = _rows(sc.static, texlist)
        arr = np.concatenate([arr, _SROWS[k]])
    amb = C(sc.ambient)
    meta = dict(cam=dict(pos=[float(x) for x in sc.cam['pos']], target=[float(x) for x in sc.cam['target']], fov=float(sc.cam['fov']), roll=float(sc.cam.get('roll', 0))),
                sun=[float(x) for x in sc.sun], sunc=[float(x) for x in C(sc.suncol)],
                amb=[[float(x) for x in amb * 1.15], [float(x) for x in amb * 0.55]],
                fog=[float(x) for x in C(sc.fog)], fogd=float(sc.fogd),
                lights=[[[float(x) for x in l['pos']], [float(x) for x in C(l['col'])], float(l.get('I', 1)), float(l.get('r', 6))] for l in sc.lights][:10],
                sky=[[float(x) for x in C(sc.sky[0])], [float(x) for x in C(sc.sky[1])]],
                shadow=bool(sc.shadow), she=float(sc.she), stars=float(sc.stars),
                tags=[dict(p=[float(x) for x in p_], t=t_) for p_, t_ in sc.tags])
    if sc.shc is not None: meta['shc'] = [float(x) for x in sc.shc]
    return arr, meta

# ---------- Roblox faces ----------
_faces = {}
def face_img(style, narr=False):
    if (style, narr) in _faces: return _faces[(style, narr)]
    S = 1024
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    K = (18, 18, 18, 255); Wt = (255, 255, 255, 255)
    def X(u): return S / 2 + u * S / 2
    def Y(v): return S / 2 - v * S / 2
    def ell(cx, cy, rx, ry, col): d.ellipse((X(cx - rx), Y(cy + ry), X(cx + rx), Y(cy - ry)), fill=col)
    def arc(cx, cy, rx, ry, a0, a1, w, col=K): d.arc((X(cx - rx), Y(cy + ry), X(cx + rx), Y(cy - ry)), a0, a1, fill=col, width=int(w * S / 2))
    def line(pts, w, col=K): d.line([(X(a), Y(b)) for a, b in pts], fill=col, width=int(w * S / 2), joint='curve')
    G = (245, 197, 66, 255)
    browed = [False]
    def brow(side, inner_up, w=0.07):
        browed[0] = True
        off = 0.14 if narr else 0.0; w = 0.085 if narr else w
        y_out = 0.5 - off; y_in = 0.5 + inner_up - off
        a = (side * 0.5, y_out); b = (side * 0.13, y_in)
        if narr and side == 1:
            m1 = (a[0] + (b[0] - a[0]) * 0.36, a[1] + (b[1] - a[1]) * 0.36); m2 = (a[0] + (b[0] - a[0]) * 0.64, a[1] + (b[1] - a[1]) * 0.64)
            line([a, m1], w); line([m2, b], w)
        else:
            line([a, b], w)
    def gold(x0, y0, x1, y1): d.rounded_rectangle((X(x0), Y(y0), X(x1), Y(y1)), radius=8, fill=G)
    if style == 'focus':
        for sx in (-0.28, 0.28):
            d.chord((X(sx - 0.13), Y(0.24), X(sx + 0.13), Y(0.0)), 180, 360, fill=K)
            ell(sx + 0.02, 0.1, 0.03, 0.03, Wt)
        line([(-0.5, 0.36), (-0.1, 0.22)], 0.09); line([(0.5, 0.36), (0.1, 0.22)], 0.09)
        line([(-0.2, -0.32), (0.2, -0.32)], 0.065)
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'power':
        for sx in (-0.28, 0.28):
            d.polygon([(X(sx - 0.17), Y(0.2)), (X(sx + 0.17), Y(0.08 if sx < 0 else 0.2)), (X(sx + 0.15), Y(-0.02)), (X(sx - 0.15), Y(-0.02))] if sx < 0 else
                      [(X(sx - 0.17), Y(0.2) if False else Y(0.08)), (X(sx + 0.17), Y(0.2)), (X(sx + 0.15), Y(-0.02)), (X(sx - 0.15), Y(-0.02))], fill=(255, 255, 255, 255))
            ell(sx, 0.07, 0.07, 0.07, (40, 200, 255, 255)); ell(sx, 0.07, 0.03, 0.03, (255, 255, 255, 255))
        line([(-0.56, 0.4), (-0.08, 0.18)], 0.11); line([(0.56, 0.4), (0.08, 0.18)], 0.11)
        d.rounded_rectangle((X(-0.32), Y(-0.24), X(0.32), Y(-0.56)), radius=20, fill=K)
        d.rectangle((X(-0.28), Y(-0.28), X(0.28), Y(-0.52)), fill=Wt)
        for xx in (-0.14, 0.0, 0.14): d.line((X(xx), Y(-0.28), X(xx), Y(-0.52)), fill=K, width=6)
        d.line((X(-0.28), Y(-0.40), X(0.28), Y(-0.40)), fill=K, width=6)
        for sx in (-0.62, 0.62): d.line((X(sx), Y(0.6), X(sx * 0.9), Y(0.3)), fill=(255, 255, 255, 0), width=1)
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'roar':
        for sx in (-0.28, 0.28):
            d.chord((X(sx - 0.14), Y(0.26), X(sx + 0.14), Y(-0.02)), 180, 360, fill=K)
        line([(-0.52, 0.4), (-0.1, 0.2)], 0.1); line([(0.52, 0.4), (0.1, 0.2)], 0.1)
        d.rounded_rectangle((X(-0.3), Y(-0.18), X(0.3), Y(-0.66)), radius=50, fill=K)
        d.rectangle((X(-0.24), Y(-0.2), X(0.24), Y(-0.28)), fill=Wt); d.rectangle((X(-0.24), Y(-0.56), X(0.24), Y(-0.64)), fill=Wt)
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'grin':
        for sx in (-0.28, 0.28):
            arc(sx, 0.08, 0.13, 0.12, 200, 340, 0.06)
        d.chord((X(-0.34), Y(-0.02), X(0.34), Y(-0.6)), 0, 180, fill=K)
        d.chord((X(-0.2), Y(-0.38), X(0.2), Y(-0.6)), 180, 360, fill=(230, 80, 90, 255))
        d.rectangle((X(-0.28), Y(-0.3), X(0.28), Y(-0.36)), fill=Wt)
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'choke':
        # bulging crossed eyes, tongue flopping out, panic sweat
        for sx, px in ((-0.3, 0.06), (0.3, -0.06)):
            ell(sx, 0.16, 0.19, 0.22, Wt); d.ellipse((X(sx - 0.19), Y(0.38), X(sx + 0.19), Y(-0.06)), outline=K, width=int(0.04 * S / 2))
            ell(sx + px, 0.12, 0.05, 0.06, K)
            line([(sx - 0.17, 0.27), (sx - 0.08, 0.31)], 0.025, (230, 60, 60, 255)); line([(sx + 0.08, 0.06), (sx + 0.16, 0.02)], 0.025, (230, 60, 60, 255))
        line([(-0.55, 0.5), (-0.14, 0.42)], 0.07); line([(0.55, 0.56), (0.14, 0.44)], 0.07)
        d.rounded_rectangle((X(-0.24), Y(-0.24), X(0.24), Y(-0.5)), radius=30, fill=K)
        d.rounded_rectangle((X(-0.1), Y(-0.36), X(0.16), Y(-0.78)), radius=40, fill=(255, 110, 140, 255))
        line([(0.03, -0.42), (0.03, -0.66)], 0.025, (200, 60, 90, 255))
        d.rounded_rectangle((X(0.6), Y(0.42), X(0.68), Y(0.1)), radius=20, fill=(110, 200, 255, 255))
        d.rounded_rectangle((X(-0.68), Y(0.3), X(-0.6), Y(0.0)), radius=20, fill=(110, 200, 255, 255))
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'smirk':
        # one eyebrow up, lopsided smug smile, half-lidded eyes
        for sx in (-0.28, 0.28):
            ell(sx, 0.1, 0.085, 0.11, K); ell(sx + 0.02, 0.15, 0.028, 0.035, Wt)
            d.rectangle((X(sx - 0.12), Y(0.27), X(sx + 0.12), Y(0.14)), fill=(0, 0, 0, 0))
            line([(sx - 0.12, 0.15), (sx + 0.12, 0.15)], 0.05)
        line([(-0.48, 0.34), (-0.12, 0.3)], 0.07); line([(0.12, 0.46), (0.48, 0.38)], 0.07)
        line([(-0.24, -0.36), (0.06, -0.36), (0.26, -0.24)], 0.06)
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'snicker':
        # squinty happy eyes, pressed grin trying not to laugh, laugh tear
        for sx in (-0.28, 0.28):
            arc(sx, 0.06, 0.13, 0.11, 200, 340, 0.065)
        d.chord((X(-0.26), Y(-0.16), X(0.26), Y(-0.46)), 0, 180, fill=K)
        d.rectangle((X(-0.22), Y(-0.29), X(0.22), Y(-0.34)), fill=Wt)
        ell(-0.5, -0.14, 0.09, 0.06, (255, 120, 130, 170)); ell(0.5, -0.14, 0.09, 0.06, (255, 120, 130, 170))
        d.rounded_rectangle((X(0.4), Y(0.04), X(0.48), Y(-0.22)), radius=20, fill=(110, 200, 255, 255))
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'holdlaugh':
        # eyes squeezed shut >  <, lips pressed in a wobbly line, puffed red cheeks
        line([(-0.44, 0.24), (-0.18, 0.12), (-0.44, 0.02)], 0.065); line([(0.44, 0.24), (0.18, 0.12), (0.44, 0.02)], 0.065)
        line([(-0.22, -0.36), (-0.11, -0.31), (0.0, -0.37), (0.11, -0.31), (0.22, -0.36)], 0.055)
        ell(-0.5, -0.18, 0.14, 0.1, (255, 110, 120, 200)); ell(0.5, -0.18, 0.14, 0.1, (255, 110, 120, 200))
        d.rounded_rectangle((X(-0.6), Y(0.0), X(-0.52), Y(-0.3)), radius=20, fill=(110, 200, 255, 255))
        im = im.resize((512, 512), Image.LANCZOS); _faces[(style, narr)] = im; return im
    if style == 'blink':
        line([(-0.42, 0.14), (-0.18, 0.14)], 0.06); line([(0.18, 0.14), (0.42, 0.14)], 0.06)
        arc(0, -0.05, 0.32, 0.28, 30, 150, 0.065)
    elif style == 'sleep':
        arc(-0.3, 0.2, 0.13, 0.1, 20, 160, 0.055); arc(0.3, 0.2, 0.13, 0.1, 20, 160, 0.055)
        arc(0, -0.25, 0.14, 0.08, 20, 160, 0.05)
    elif style in ('scared', 'terror', 'shout', 'blank'):
        if style == 'blank':
            ell(-0.3, 0.15, 0.11, 0.07, (255, 250, 220, 255)); ell(0.3, 0.15, 0.11, 0.07, (255, 250, 220, 255))
            line([(-0.2, -0.36), (0.2, -0.36)], 0.045)
        else:
            for sx in (-0.3, 0.3):
                ell(sx, 0.13, 0.16, 0.2, Wt); d.ellipse((X(sx - 0.16), Y(0.33), X(sx + 0.16), Y(-0.07)), outline=K, width=int(0.035 * S / 2))
                ell(sx, 0.1, 0.055, 0.065, K)
            if style == 'scared':
                ell(0, -0.42, 0.09, 0.12, K); brow(-1, -0.05); brow(1, -0.05)
            elif style == 'terror':
                ell(0, -0.45, 0.15, 0.19, K); brow(-1, -0.08); brow(1, -0.08)
                d.rounded_rectangle((X(0.55), Y(0.3), X(0.63), Y(-0.15)), radius=20, fill=(110, 200, 255, 255))
                d.rounded_rectangle((X(-0.63), Y(0.3), X(-0.55), Y(-0.15)), radius=20, fill=(110, 200, 255, 255))
            else:
                d.rounded_rectangle((X(-0.26), Y(-0.28), X(0.26), Y(-0.66)), radius=40, fill=K)
                d.rounded_rectangle((X(-0.2), Y(-0.31), X(0.2), Y(-0.38)), radius=10, fill=Wt)
                brow(-1, -0.12, 0.08); brow(1, -0.12, 0.08)
    else:
        for sx in (-0.28, 0.28):
            ell(sx, 0.12, 0.085, 0.15, K); ell(sx + 0.025, 0.18, 0.03, 0.045, Wt)
        if style in ('smile', 'tears_smile') and narr:
            d.chord((X(-0.32), Y(-0.08), X(0.32), Y(-0.52)), 0, 180, fill=K)
            d.rectangle((X(-0.26), Y(-0.3), X(0.26), Y(-0.37)), fill=Wt)
            gold(0.03, -0.29, 0.13, -0.4)
        elif style in ('smile', 'tears_smile'):
            arc(0, 0.02, 0.36, 0.34, 35, 145, 0.065)
        elif style == 'neutral':
            arc(0, -0.05, 0.3, 0.22, 55, 125, 0.06)
        elif style in ('sad', 'tears'):
            arc(0, -0.62, 0.25, 0.2, 215, 325, 0.06); brow(-1, 0.1); brow(1, 0.1)
        elif style == 'worried':
            line([(-0.18, -0.33), (-0.06, -0.29), (0.06, -0.33), (0.18, -0.29)], 0.05); brow(-1, 0.08); brow(1, 0.08)
            ell(0.6, 0.32, 0.05, 0.08, (140, 215, 255, 255))
        if style in ('tears', 'tears_smile'):
            d.rounded_rectangle((X(-0.34), Y(-0.05), X(-0.24), Y(-0.6)), radius=20, fill=(90, 190, 255, 255))
            d.rounded_rectangle((X(0.24), Y(-0.05), X(0.34), Y(-0.6)), radius=20, fill=(90, 190, 255, 255))
    if narr:
        if not browed[0]:
            ins = {'sleep': 0.0, 'blink': 0.0, 'smile': 0.02, 'neutral': -0.04}.get(style, 0.0)
            brow(-1, ins); brow(1, ins)
        if style in ('smile', 'tears_smile'):
            pass
        elif style == 'neutral':
            gold(0.06, -0.31, 0.15, -0.41)
        elif style in ('sad', 'tears'):
            gold(0.04, -0.47, 0.12, -0.55)
        elif style == 'worried':
            gold(0.05, -0.31, 0.13, -0.39)
        elif style == 'scared':
            gold(-0.06, -0.31, 0.04, -0.39)
        elif style == 'terror':
            gold(-0.07, -0.28, 0.05, -0.37)
        elif style == 'shout':
            gold(0.02, -0.3, 0.12, -0.39)
    im = im.resize((512, 512), Image.LANCZOS)
    _faces[(style, narr)] = im
    return im

_shirts = {}
def shirt_img(kind, col):
    key = (kind, tuple(np.round(C(col), 3)))
    if key in _shirts: return _shirts[key]
    S = 512; c = tuple(int(x * 255) for x in C(col))
    dk = tuple(int(x * 0.72) for x in c); lt = tuple(min(255, int(x * 1.15 + 10)) for x in c)
    im = Image.new('RGBA', (S, S), c + (255,)); d = ImageDraw.Draw(im)
    for y in range(0, 60): d.line((0, y, S, y), fill=tuple(int(cc * (0.85 + 0.15 * y / 60)) for cc in c) + (255,))
    if kind == 'hoodie':
        d.polygon([(150, 0), (256, 110), (362, 0)], fill=dk + (255,))
        d.polygon([(175, 0), (256, 80), (337, 0)], fill=tuple(int(x * 0.5) for x in c) + (255,))
        d.line((225, 80, 215, 250), fill=(235, 235, 235, 255), width=10); d.line((287, 80, 297, 250), fill=(235, 235, 235, 255), width=10)
        d.ellipse((205, 240, 225, 262), fill=(235, 235, 235, 255)); d.ellipse((287, 240, 307, 262), fill=(235, 235, 235, 255))
        d.rounded_rectangle((110, 330, 402, 470), radius=30, fill=dk + (255,))
        d.line((110, 400, 402, 400), fill=tuple(int(x * 0.62) for x in c) + (255,), width=4)
        d.rectangle((0, 488, S, S), fill=dk + (255,))
    elif kind in ('tee', 'tee_logo'):
        d.chord((176, -60, 336, 70), 0, 180, fill=tuple(int(x * 0.6) for x in c) + (255,))
        d.chord((186, -60, 326, 55), 0, 180, fill=(30, 30, 30, 0) if False else tuple(int(x * 0.85) for x in c) + (255,))
        if kind == 'tee_logo':
            d.rounded_rectangle((150, 170, 362, 300), radius=24, fill=(250, 250, 250, 255))
            d.text((170, 175), 'GG', font=ImageFont.truetype(FONT_ANTON, 110), fill=c + (255,))
            d.text((300, 175), '!', font=ImageFont.truetype(FONT_ANTON, 110), fill=(30, 30, 30, 255))
    elif kind == 'jersey':
        d.rectangle((0, 0, 100, S), fill=(0, 0, 0, 0)); d.rectangle((412, 0, S, S), fill=(0, 0, 0, 0))
        d.polygon([(170, 0), (256, 130), (342, 0)], fill=(0, 0, 0, 0))
        d.line((100, 0, 100, S), fill=(255, 220, 60, 255), width=16); d.line((412, 0, 412, S), fill=(255, 220, 60, 255), width=16)
        d.line((170, 0, 256, 130), fill=(255, 220, 60, 255), width=14); d.line((342, 0, 256, 130), fill=(255, 220, 60, 255), width=14)
        f = ImageFont.truetype(FONT_ANTON, 210)
        d.text((256, 330), '23', font=f, fill=(255, 255, 255, 255), anchor='mm', stroke_width=8, stroke_fill=(255, 220, 60, 255))
    elif kind == 'flannel':
        for x in range(0, S, 64):
            d.rectangle((x, 0, x + 26, S), fill=tuple(int(v * 0.55) for v in c) + (255,))
        for y in range(0, S, 64):
            d.rectangle((0, y, S, y + 26), fill=tuple(int(v * 0.55) for v in c) + (255,))
        for x in range(0, S, 64):
            d.line((x + 13, 0, x + 13, S), fill=(20, 20, 20, 255), width=4)
        d.polygon([(256, 110), (175, 0), (130, 0), (230, 140)], fill=lt + (255,)); d.polygon([(256, 110), (337, 0), (382, 0), (282, 140)], fill=lt + (255,))
        d.polygon([(190, 0), (256, 100), (322, 0)], fill=(240, 240, 240, 255))
    elif kind == 'collar':
        d.polygon([(170, 0), (256, 90), (342, 0)], fill=tuple(int(x * 0.8) for x in c) + (255,))
        d.polygon([(256, 90), (175, 0), (130, 0), (230, 120)], fill=lt + (255,)); d.polygon([(256, 90), (337, 0), (382, 0), (282, 120)], fill=lt + (255,))
        for y in (180, 280, 380): d.ellipse((248, y, 264, y + 16), fill=(200, 200, 200, 255))
    elif kind == 'tank':
        d.rectangle((0, 0, 110, S), fill=(0, 0, 0, 0)); d.rectangle((402, 0, S, S), fill=(0, 0, 0, 0))
        d.chord((150, -150, 362, 150), 0, 180, fill=(0, 0, 0, 0))
        d.line((110, 0, 110, S), fill=dk + (255,), width=8); d.line((402, 0, 402, S), fill=dk + (255,), width=8)
    elif kind == 'torn':
        d.polygon([(160, 0), (256, 100), (352, 0)], fill=(20, 20, 20, 255))
        for (x, y, r) in ((120, 260, 40), (360, 380, 30), (300, 180, 22)):
            d.polygon([(x - r, y), (x - r * 0.3, y - r), (x + r, y - r * 0.4), (x + r * 0.6, y + r), (x - r * 0.4, y + r * 0.7)], fill=(20, 10, 10, 255))
        d.line((60, 420, 200, 470), fill=(120, 20, 20, 255), width=8)
    if kind != 'tank':
        d.line((0, 0, 0, S), fill=dk + (255,), width=10); d.line((S - 1, 0, S - 1, S), fill=dk + (255,), width=10)
    _shirts[key] = im
    return im

PHONE_EAR = dict(pitch=143.3, roll=-35.2, yaw=84.2, elbow=123.6)

_LEGS = {}
def character(sc, pos, yaw=0, pose=None, skin='#8a3ff0', shirt='#8c8c94', pants='#1d1d22', cuff='#8a3ff0',
              hair='dreads', haircol='#121212', face='neutral', root_R=None, phone=None, scale=1.0, blob=True, extra=None, idle=True,
              design='tee', shoes='#1b1b1f', tag=None, chain=False, grill=False, slit=False, arms=None, skirt=None, nohead=False):
    p = dict(ll=0, rl=0, la=0, ra=0, lar=0, rar=0, lay=0, ray=0, le=8, re=8, lk=0, rk=0, hy=0, hp=0, lean=0, sit=False, y=0)
    if pose: p.update(pose)
    if p['sit'] and p['ll'] >= 80 and 'lk' not in (pose or {}): p['lk'] = p['ll']; p['rk'] = p['rl']
    ear = None
    for side in ('r', 'l'):
        if p[side + 'a'] >= 140:
            p[side + 'a'] = PHONE_EAR['pitch']; p[side + 'ar'] = -PHONE_EAR['roll'] * -1 if False else PHONE_EAR['roll']
            p[side + 'ay'] = PHONE_EAR['yaw']; p[side + 'e'] = PHONE_EAR['elbow']; ear = side
    t = TIME[0]; ph = (pos[0] * 1.7 + pos[2] * 0.9) % 6.28
    br = math.sin(t * 2.4 + ph) if idle else 0
    if ear != 'l': p['la'] += br * 2.5; p['lar'] += 3 + br * 1.5
    if ear != 'r': p['ra'] -= br * 2.5; p['rar'] += 3 + br * 1.5
    p['hp'] += br * 1.2; p['hy'] += math.sin(t * 0.9 + ph) * 3 if idle else 0
    blink = idle and ((t + ph) % 3.4) < 0.11
    R0 = rot(yaw, p['lean'], 0) if root_R is None else root_R
    base = M4((pos[0], pos[1] + p['y'], pos[2]), R0)
    if scale != 1.0:
        S = np.eye(4); S[:3, :3] *= scale; base = base @ S
    tb = base @ M4((0, br * 0.025, 0))
    out = []
    armc = arms if arms is not None else shirt
    torso = box((0, 3, 0), (2, 2, 1), skin if design == 'jersey' else shirt, parent=tb, rl=1)
    torso.tex['pz'] = (shirt_img(design, shirt), False)
    out.append(torso)
    if skirt is not None:
        out.append(box((0, 1.78, 0), (2.25, 0.85, 1.3), skirt, parent=tb, rl=1, mat='carpet'))
        out.append(box((0, 2.12, 0), (2.08, 0.2, 1.06), C(skirt) * 0.75, parent=tb, rl=1))
    else:
        out.append(box((0, 2.08, 0), (1.96, 0.2, 0.98), C(pants) * 0.8, parent=tb, rl=1))
    for side, key, kk in ((-0.5, 'll', 'lk'), (0.5, 'rl', 'rk')):
        hip = base @ M4((side, 2, 0), rot(0, -p[key], 0))
        out.append(box((0, -0.5, 0), (0.97, 1.05, 0.98), pants, parent=hip, rl=1))
        knee = hip @ M4((0, -1.0, 0), rot(0, p[kk], 0))
        out.append(box((0, -0.38, 0), (0.93, 0.8, 0.93), pants, parent=knee, rl=1))
        out.append(box((0, -0.86, 0.07), (0.97, 0.28, 1.12), shoes, parent=knee, rl=1))
        _LEGS[key] = (hip, knee)
    armboxes = {}
    armboxes['ll_hip'], armboxes['ll_knee'] = _LEGS['ll']; armboxes['rl_hip'], armboxes['rl_knee'] = _LEGS['rl']
    for side, key, rk, yk, ek in ((-1.5, 'la', 'lar', 'lay', 'le'), (1.5, 'ra', 'rar', 'ray', 're')):
        sg = -1 if side < 0 else 1
        sh = tb @ M4((side, 3.85, 0), rot(sg * p[yk], -p[key], sg * p[rk]))
        out.append(box((0, -0.45, 0), (0.95, 1.05, 0.95), armc, parent=sh, rl=1))
        el = sh @ M4((0, -0.95, 0), rot(0, -p[ek], 0))
        out.append(box((0, -0.3, 0), (0.92, 0.7, 0.92), armc, parent=el, rl=1))
        out.append(box((0, -0.78, 0), (0.86, 0.34, 0.86), cuff, parent=el, rl=2))
        armboxes[key] = el; armboxes[key + '_sh'] = sh
    hm = tb @ M4((0, 4, 0), rot(p['hy'], -p['hp'], 0))
    if nohead:
        hair = 'none'
    if not nohead: out.append(box((0, 0.05, 0), (0.6, 0.2, 0.6), skin, parent=hm))
    head = box((0, 0.66, 0), (1.3, 1.3, 1.3), skin, parent=hm, rl=3)
    if nohead: head.size = np.array([0.01, 0.01, 0.01])
    fs = face
    if blink and face in ('neutral', 'smile', 'sad', 'worried', 'tears', 'tears_smile'): fs = 'blink'
    head.tex['pz'] = (face_img(fs, narr=(grill or slit)), False)
    out.append(head)
    hc = C(haircol)
    if hair == 'dreads':
        out.append(box((0, 1.34, -0.05), (1.5, 0.45, 1.5), hc, parent=hm, rl=2))
        out.append(box((0, 0.85, -0.58), (1.48, 1.2, 0.4), hc, parent=hm, rl=2))
        for sx in (-0.7, 0.7):
            out.append(box((sx, 0.95, -0.1), (0.3, 1.0, 1.3), hc, parent=hm, rl=2))
        for sx in (-0.45, 0.0, 0.45):
            out.append(box((sx, 1.22, 0.6), (0.42, 0.42, 0.28), hc, parent=hm, rl=3))
        for k, sx in enumerate((-0.55, -0.2, 0.2, 0.55)):
            out.append(box((sx, 0.55 - 0.08 * (k % 2), -0.72), (0.26, 0.9, 0.26), hc, parent=hm, rl=4))
    elif hair == 'durag':
        out.append(box((0, 1.3, -0.04), (1.4, 0.4, 1.42), hc, parent=hm, rl=3))
        out.append(box((0, 0.95, -0.7), (0.5, 0.3, 0.2), hc, parent=hm, rl=2))
        out.append(box((0, 0.5, -0.78), (0.42, 0.9, 0.1), hc, parent=hm, rl=1))
    elif hair == 'bandana':
        out.append(box((0, 1.32, -0.05), (1.4, 0.3, 1.4), '#111', parent=hm, rl=2))
        out.append(box((0, 1.1, 0), (1.44, 0.3, 1.44), hc, parent=hm, rl=2))
        out.append(box((0, 1.1, -0.8), (0.4, 0.3, 0.25), hc, parent=hm, rl=2))
    elif hair == 'cap_back':
        out.append(box((0, 1.38, 0), (1.42, 0.45, 1.42), hc, parent=hm, rl=2))
        out.append(box((0, 1.22, -0.85), (1.3, 0.12, 0.7), hc, parent=hm, rl=1))
    elif hair in ('beanie', 'beanie_beard'):
        out.append(box((0, 1.4, -0.02), (1.42, 0.62, 1.42), hc, parent=hm, rl=3, mat='carpet'))
        out.append(box((0, 1.12, -0.02), (1.47, 0.28, 1.47), hc * 1.25 + 0.02, parent=hm, rl=2, mat='carpet'))
        out.append(box((0.42, 1.12, 0.74), (0.3, 0.2, 0.03), '#d8d8d8', parent=hm))
        if hair == 'beanie_beard':
            out.append(box((0, 0.06, 0.6), (1.0, 0.26, 0.2), '#a8a8b0', parent=hm, rl=2))
    elif hair == 'taper':
        # clean taper fade: neat waves on top, sharp line-up across the forehead, sides and back faded down to skin
        out.append(box((0, 1.4, -0.03), (1.38, 0.3, 1.36), hc, parent=hm, rl=3))
        hl = hc * 1.6 + 0.03
        for k, dz in enumerate((0.42, 0.14, -0.14, -0.42)):
            out.append(box((0, 1.555, dz), (1.2 - 0.08 * abs(k - 1.5), 0.035, 0.07), hl, parent=hm, rl=1, nocast=True))
        out.append(box((0, 1.235, 0.66), (1.1, 0.2, 0.04), hc, parent=hm, rl=1))
        fade = hc * 0.45 + C(skin) * 0.55
        for sx in (-1, 1):
            out.append(box((sx * 0.665, 1.2, -0.06), (0.035, 0.24, 1.05), hc, parent=hm, rl=1))
            out.append(box((sx * 0.66, 1.0, -0.1), (0.025, 0.17, 0.92), fade, parent=hm, rl=1))
        out.append(box((0, 1.17, -0.665), (1.3, 0.3, 0.035), hc, parent=hm, rl=1))
        out.append(box((0, 0.95, -0.66), (1.2, 0.16, 0.025), fade, parent=hm, rl=1))
    elif hair == 'short':
        out.append(box((0, 1.33, -0.05), (1.42, 0.35, 1.42), hc, parent=hm, rl=2))
        out.append(box((0, 0.95, -0.6), (1.4, 0.7, 0.25), hc, parent=hm, rl=2))
        out.append(box((0.25, 1.22, 0.62), (0.9, 0.22, 0.2), hc, parent=hm, rl=2))
    elif hair == 'long':
        out.append(box((0, 1.34, -0.05), (1.46, 0.38, 1.46), hc, parent=hm, rl=2))
        out.append(box((0, 0.3, -0.58), (1.5, 2.1, 0.4), hc, parent=hm, rl=2))
        for sx in (-0.7, 0.7):
            out.append(box((sx, 0.5, -0.05), (0.25, 1.7, 1.35), hc, parent=hm, rl=2))
        out.append(box((0, 1.17, 0.6), (1.38, 0.3, 0.2), hc, parent=hm, rl=2))
    elif hair == 'curly':
        for dx in (-0.42, 0, 0.42):
            for dz in (-0.42, 0, 0.42):
                out.append(box((dx, 1.38, dz), (0.6, 0.5, 0.6), hc, parent=hm, rl=4))
    elif hair == 'gray':
        out.append(box((0, 1.34, -0.05), (1.5, 0.42, 1.5), hc, parent=hm, rl=2))
        out.append(box((0, 0.85, -0.58), (1.48, 1.2, 0.4), hc, parent=hm, rl=2))
        for sx in (-0.7, 0.7):
            out.append(box((sx, 0.95, -0.1), (0.28, 1.0, 1.3), hc, parent=hm, rl=2))
        out.append(box((0, 0.06, 0.6), (1.0, 0.26, 0.2), '#a8a8b0', parent=hm, rl=2))
    elif hair == 'cap':
        out.append(box((0, 1.38, 0), (1.42, 0.45, 1.42), hc, parent=hm, rl=2))
        out.append(box((0, 1.22, 0.85), (1.3, 0.12, 0.7), hc, parent=hm, rl=1))
    elif hair == 'bald_beard':
        out.append(box((0, 0.15, 0.6), (1.15, 0.5, 0.22), hc, parent=hm, rl=2))
        out.append(box((0, 1.3, -0.05), (1.36, 0.14, 1.36), hc, parent=hm, rl=1))
    if chain is True:
        Gc = '#f5c542'
        for k in range(15):
            u = -1 + 2 * k / 14
            x = u * 0.62; y = 3.92 - (1 - u * u) * 1.0
            out.append(box((x, y, 0.55), (0.2, 0.16, 0.12), Gc, parent=tb, rl=2, emit=0.25, R=rot(0, 0, math.degrees(math.atan2(2 * u * 1.0, 1)) * 0.6)))
        out.append(box((0, 2.68, 0.58), (0.55, 0.6, 0.12), Gc, parent=tb, rl=2, emit=0.3))
        out.append(box((0, 2.68, 0.65), (0.3, 0.32, 0.04), '#fff2a0', parent=tb, rl=1, emit=0.6))
    elif chain == 'silver':
        for k in range(11):
            u = -1 + 2 * k / 10
            out.append(box((u * 0.5, 3.92 - (1 - u * u) * 0.6, 0.53), (0.12, 0.1, 0.08), '#d8dde4', parent=tb, rl=2, emit=0.2))
    if phone:
        side = 'ra' if phone in ('r', 'r_screen') else 'la'
        el = armboxes[side]
        if ear == side[0]:
            pm = el @ M4((0.0, -0.95, 0.15), rot(0, 90, 0))
        else:
            pm = el @ M4((0, -1.0, 0.2), rot(0, 0, 0))
        out.append(box((0, 0, 0), (0.55, 0.13, 0.95), '#111114', parent=pm, rl=1))
        if phone.endswith('screen'):
            out.append(box((0, 0.07, 0), (0.45, 0.02, 0.8), '#bfe6ff', parent=pm, emit=1.6, shade=False))
    if extra:
        extra(out, base, hm, armboxes)
    if tag:
        sc.tags.append(((hm @ np.array([0, 2.05, 0, 1]))[:3], tag))
    sc.add(out)
    return base

# ---------- environment helpers ----------
def room(sc, w, d, h, wall, floor, ceil='#f2efe6', floor_tile=1.2, floor_j=0.05, wall_j=0.02, x0=0, z0=0, walls='nsew', floor_mat='wood', holes=()):
    sc.add(box((x0, -0.25, z0), (w, 0.5, d), floor, bg=True, mat=floor_mat))
    sc.add(box((x0, h + 0.25, z0), (w, 0.5, d), ceil, bg=True, mat='wall'))
    t = 0.5
    if 'n' in walls: sc.add(box((x0, h / 2, z0 - d / 2 - t / 2), (w + 2 * t, h, t), wall, bg=True, mat='wall'))
    if 's' in walls: sc.add(box((x0, h / 2, z0 + d / 2 + t / 2), (w + 2 * t, h, t), wall, bg=True, mat='wall'))
    for side, sx in (('w', -1), ('e', 1)):
        if side not in walls: continue
        x = x0 + sx * (w / 2 + t / 2)
        hs = sorted([(hz - hw / 2, hz + hw / 2, hh) for (hs_, hz, hw, hh) in holes if hs_ == side])
        z = z0 - d / 2
        for a, b, hh in hs:
            if a > z: sc.add(box((x, h / 2, (z + a) / 2), (t, h, a - z), wall, bg=True, mat='wall'))
            sc.add(box((x, (hh + h) / 2, (a + b) / 2), (t, h - hh, b - a), wall, bg=True, mat='wall'))
            z = b
        if z0 + d / 2 > z: sc.add(box((x, h / 2, (z + z0 + d / 2) / 2), (t, h, z0 + d / 2 - z), wall, bg=True, mat='wall'))
    sc.add(box((x0, 0.25, z0 - d / 2 + 0.1), (w, 0.5, 0.2), '#f4f4f4', nocast=True))
    sc.add(box((x0 - w / 2 + 0.1, 0.25, z0), (0.2, 0.5, d), '#f4f4f4', nocast=True))
    sc.add(box((x0 + w / 2 - 0.1, 0.25, z0), (0.2, 0.5, d), '#f4f4f4', nocast=True))

def window(sc, pos, w, h, R=None, sky='#1b2a55', frame='#f4f4f4', emit=0.6, moon=False):
    out = [box(pos, (w, h, 0.12), sky, R=R, emit=emit, shade=False, nocast=True)]
    Rm = R if R is not None else np.eye(3)
    base = M4(pos, Rm)
    out.append(box((0, h / 2, 0.1), (w + 0.4, 0.25, 0.3), frame, parent=base, nocast=True))
    out.append(box((0, -h / 2, 0.15), (w + 0.6, 0.25, 0.45), frame, parent=base, nocast=True))
    out.append(box((-w / 2, 0, 0.1), (0.25, h, 0.3), frame, parent=base, nocast=True))
    out.append(box((w / 2, 0, 0.1), (0.25, h, 0.3), frame, parent=base, nocast=True))
    out.append(box((0, 0, 0.1), (0.15, h, 0.2), frame, parent=base, nocast=True))
    out.append(box((0, 0, 0.1), (w, 0.15, 0.2), frame, parent=base, nocast=True))
    sc.add(out)

def door(sc, pos, open_deg=0, R=None, color='#7a4a2a', frame='#f4f4f4', hinge_left=True, knob='#d8b45a', w=3.0, h=6.6, dark_behind=True, behind='#05050a'):
    Rm = R if R is not None else np.eye(3)
    base = M4(pos, Rm)
    out = []
    if dark_behind:
        out.append(box((0, h / 2, -4.2), (w + 0.6, h, 0.1), behind, parent=base, shade=False, nocast=True))
        out.append(box((-w / 2 - 0.3, h / 2, -2.2), (0.1, h, 4), behind, parent=base, shade=False, nocast=True))
        out.append(box((w / 2 + 0.3, h / 2, -2.2), (0.1, h, 4), behind, parent=base, shade=False, nocast=True))
        out.append(box((0, -0.05, -2.2), (w + 0.6, 0.1, 4), behind, parent=base, shade=False, nocast=True))
        out.append(box((0, h + 0.05, -2.2), (w + 0.6, 0.1, 4), behind, parent=base, shade=False, nocast=True))
    out.append(box((-w / 2 - 0.15, h / 2, 0), (0.3, h + 0.3, 0.4), frame, parent=base, nocast=True))
    out.append(box((w / 2 + 0.15, h / 2, 0), (0.3, h + 0.3, 0.4), frame, parent=base, nocast=True))
    out.append(box((0, h + 0.15, 0), (w + 0.6, 0.3, 0.4), frame, parent=base, nocast=True))
    hx = -w / 2 if hinge_left else w / 2
    sgn = 1 if hinge_left else -1
    hm = base @ M4((hx, 0, 0.05), rot(sgn * open_deg, 0, 0))
    out.append(box((sgn * w / 2, h / 2, 0), (w - 0.05, h - 0.05, 0.2), color, parent=hm, mat='wood'))
    for py in (h * 0.72, h * 0.28):
        out.append(box((sgn * w / 2, py, 0.11), (w * 0.7, h * 0.36, 0.04), C(color) * 0.85, parent=hm, mat='wood'))
        out.append(box((sgn * w / 2, py, -0.11), (w * 0.7, h * 0.36, 0.04), C(color) * 0.85, parent=hm, mat='wood'))
    out.append(box((sgn * (w - 0.35), h * 0.47, 0.2), (0.24, 0.24, 0.25), knob, parent=hm, rl=3))
    out.append(box((sgn * (w - 0.35), h * 0.47, -0.2), (0.24, 0.24, 0.25), knob, parent=hm, rl=3))
    sc.add(out)
    return hm

def bed(sc, pos, yaw=0, blanket='#3b5bb5', frame='#4a2f1e', length=7, width=4.4):
    base = M4(pos, rot(yaw))
    out = [box((0, 0.6, 0), (width, 1.2, length), frame, parent=base, mat='wood'),
           box((0, 1.5, 0.2), (width - 0.3, 0.7, length - 0.6), '#eeeeee', parent=base, rl=1, mat='carpet'),
           box((0, 1.95, 0.9), (width - 0.1, 0.25, length - 1.8), blanket, parent=base, rl=1, mat='carpet'),
           box((0, 2.0, -length / 2 + 0.9), (width * 0.6, 0.5, 1.2), '#ffffff', parent=base, rl=2, mat='carpet'),
           box((0, 2.1, -length / 2 - 0.1), (width + 0.2, 4.2, 0.4), frame, parent=base, mat='wood')]
    sc.add(out)
    return base

def nightstand(sc, pos, yaw=0):
    base = M4(pos, rot(yaw))
    sc.add([box((0, 1.1, 0), (2.0, 2.2, 1.8), '#6b4429', parent=base, mat='wood'),
            box((0, 1.35, 0.92), (1.6, 0.6, 0.05), '#5a3822', parent=base, mat='wood'),
            box((0, 1.35, 0.97), (0.3, 0.12, 0.06), '#d8b45a', parent=base, rl=1)])
    return base

def lamp(sc, pos, on=True, col='#ffe2a8'):
    sc.add([box((pos[0], pos[1] + 0.1, pos[2]), (0.7, 0.2, 0.7), '#3a3a3a', rl=1),
            box((pos[0], pos[1] + 0.8, pos[2]), (0.15, 1.3, 0.15), '#3a3a3a'),
            box((pos[0], pos[1] + 1.7, pos[2]), (0.9, 0.8, 0.9), col, emit=1.2 if on else 0, shade=not on, rl=1, nocast=True)])
    if on: sc.lights.append(dict(pos=(pos[0], pos[1] + 1.7, pos[2]), col=col, I=1.4, r=5))

def bookshelf(sc, pos, yaw=0, h=6, w=3.5):
    base = M4(pos, rot(yaw))
    out = [box((0, h / 2, -0.1), (w, h, 1.1), '#6b4429', parent=base, mat='wood')]
    for s in range(4):
        out.append(box((0, 0.15 + s * (h - 0.3) / 3, 0.2), (w, 0.2, 1.1), '#5e3b23', parent=base, mat='wood'))
    out.append(box((-w / 2 + 0.1, h / 2, 0.2), (0.2, h, 1.1), '#5e3b23', parent=base, mat='wood'))
    out.append(box((w / 2 - 0.1, h / 2, 0.2), (0.2, h, 1.1), '#5e3b23', parent=base, mat='wood'))
    cols = ['#d94f4f', '#4f7fd9', '#e6c34a', '#4fae6a', '#efefef', '#9a5fd0', '#e08a3c']
    rng = random.Random(3)
    for s in range(3):
        y = 0.25 + s * (h - 0.3) / 3
        x = -w / 2 + 0.3
        while x < w / 2 - 0.5:
            bw = 0.25 + rng.random() * 0.2; bh = 1.0 + rng.random() * 0.5
            out.append(box((x + bw / 2, y + bh / 2, 0.35), (bw, bh, 0.6), rng.choice(cols), parent=base))
            x += bw + 0.03
    sc.add(out)

def phone_tex(lines, bg=(20, 24, 34), accent=(80, 220, 120), size=(288, 512), ring=False, glitch=0.0, waveform=None, red=False):
    S2 = 2
    im = Image.new('RGBA', (size[0] * S2, size[1] * S2), bg + (255,))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT_ANTON, 36 * S2); f2 = ImageFont.truetype(FONT_ANTON, 54 * S2); f3 = ImageFont.truetype(FONT_ANTON, 26 * S2)
    # gradient bg
    for yy in range(0, im.size[1], 8):
        a = yy / im.size[1]
        d.rectangle((0, yy, im.size[0], yy + 8), fill=tuple(int(c * (1 - 0.5 * a) + (30 if not red else 60) * a * (i == 0 if red else i == 2)) for i, c in enumerate(bg)) + (255,))
    y = 90 * S2
    for i, (txt, kind) in enumerate(lines):
        f = {'big': f2, 'mid': f1, 'small': f3}[kind]
        col = (255, 255, 255) if not red else (255, 90, 90)
        if kind == 'small': col = (170, 185, 210)
        tw = d.textlength(txt, font=f)
        d.text(((im.size[0] - tw) / 2, y), txt, font=f, fill=col)
        y += f.size + 22 * S2
    if ring:
        cx = im.size[0] // 2; by = im.size[1] - 120 * S2
        d.ellipse((cx - 110 * S2, by, cx - 40 * S2, by + 70 * S2), fill=(230, 60, 60))
        d.ellipse((cx + 40 * S2, by, cx + 110 * S2, by + 70 * S2), fill=accent)
    im = im.resize(size, Image.LANCZOS)
    if glitch > 0:
        arr = np.asarray(im).copy()
        rr = np.random.default_rng(int(glitch * 1000))
        for _ in range(int(10 * glitch)):
            y0 = rr.integers(0, size[1] - 10); hh = rr.integers(2, 14); sh = rr.integers(-30, 30)
            arr[y0:y0 + hh] = np.roll(arr[y0:y0 + hh], sh, axis=1)
        noise = rr.integers(0, 255, arr.shape[:2])
        mask = rr.random(arr.shape[:2]) < 0.08 * glitch
        arr[mask, :3] = noise[mask][:, None]
        im = Image.fromarray(arr)
    return im

def text_tex(lines, size=(600, 380), bg=(232, 216, 178), fg=(30, 22, 16), font=FONT_SERIF, fs=64, border=None):
    im = Image.new('RGBA', size, bg + (255,))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(font, fs)
    total = len(lines) * (fs * 1.25)
    y = (size[1] - total) / 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((size[0] - tw) / 2, y), ln, font=f, fill=fg)
        y += fs * 1.25
    return im

_fonts = {}
def font(sz, path=FONT_ANTON):
    k = (sz, path)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, sz)
    return _fonts[k]

def lerp(a, b, t): return np.array(a, float) * (1 - t) + np.array(b, float) * t
def ease(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def eout(t): t = min(1, max(0, t)); return 1 - (1 - t) ** 3
def ein(t): t = min(1, max(0, t)); return t ** 3
def shake(t, amp, freq=11, seed=0):
    amp = amp * 0.3
    return np.array([math.sin(t * freq + seed) * amp + math.sin(t * freq * 2.3 + 1.7 + seed) * amp * 0.5,
                     math.sin(t * freq * 1.3 + 0.5 + seed) * amp + math.sin(t * freq * 2.9 + seed) * amp * 0.4, 0])
def walk(t, speed=7, amp=35):
    s = math.sin(t * speed) * amp
    c = math.cos(t * speed)
    return dict(ll=s, rl=-s, la=-s * 0.8, ra=s * 0.8, lk=max(0, c) * amp * 1.3, rk=max(0, -c) * amp * 1.3,
                le=15 + max(0, -s) * 0.6, re=15 + max(0, s) * 0.6, y=abs(c) * 0.1)
