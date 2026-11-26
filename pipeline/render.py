"""Turns the plan + word timings into a 1080x1920 30fps video (no audio)."""
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from . import art, config
from .script import split_sentences

W, H, FPS = config.W, config.H, config.FPS


def build_timeline(plan, words, duration):
    sents = split_sentences(plan["script"])
    counts = [len(s.split()) for s in sents]
    total = sum(counts)
    n = len(words)
    starts, cum = [], 0
    for c in counts:
        i = min(n - 1, int(round(cum * n / total))) if n else 0
        starts.append(max(0.0, words[i]["start"] - 0.12) if n else cum / total * duration)
        cum += c
    starts[0] = 0.0
    scenes = []
    for k, sc in enumerate(plan["scenes"][:len(sents)]):
        st = starts[k]
        en = starts[k + 1] if k + 1 < len(starts) else duration
        scenes.append(dict(sc, start=st, end=max(en, st + 0.3), idx=k))
    return scenes


def _scene_at(scenes, t):
    for s in scenes:
        if s["start"] <= t < s["end"]:
            return s
    return scenes[-1]


def _caption_at(words, t):
    for i, w in enumerate(words):
        nxt = words[i + 1]["start"] if i + 1 < len(words) else w["end"] + 0.4
        if w["start"] <= t < max(nxt, w["start"] + 0.12):
            return w, t - w["start"]
    return None, 0


def _text_center(d, y, text, size, fill, stroke=10, maxw=1000):
    f = art.font(size)
    while f.getlength(text) > maxw and size > 40:
        size -= 6
        f = art.font(size)
    x = (W - f.getlength(text)) / 2
    d.text((x, y - size / 2), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def render_video(plan, words, duration, out_path, seed=1, progress=None):
    scenes = build_timeline(plan, words, duration)
    bgs = {}
    nframes = int(math.ceil(duration * FPS))
    samples = {}
    sample_at = {int(nframes * f) for f in (0.02, 0.2, 0.4, 0.6, 0.8, 0.97)}
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "20", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    title_lines = art.wrap(plan["title"].upper(), art.font(86), 920)[:3]

    for fi in range(nframes):
        t = fi / FPS
        sc = _scene_at(scenes, t)
        k = sc["idx"]
        if k not in bgs:
            bgs[k] = art.paint_background(sc["background"], seed * 100 + k)
            for old in [j for j in bgs if j < k - 1]:
                del bgs[old]
        bg = bgs[k]
        lt, dur = t - sc["start"], sc["end"] - sc["start"]
        p = lt / max(dur, 0.01)
        # camera: slow push in/out, gentle drift, punch-in on the very first frames
        z = 1.0 + (0.07 * p if k % 2 == 0 else 0.07 * (1 - p))
        if t < 0.45:
            z += 0.28 * (1 - t / 0.45) ** 2
        cw, ch = art.BW / z, art.BH / z
        cx = art.BW / 2 + math.sin(t * 0.35 + k) * (art.BW - cw) / 2 * 0.8
        cy = art.BH / 2 + (art.BH - ch) / 2 * 0.25
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        frame = bg.resize((W, H), Image.BILINEAR, box=box)
        d = ImageDraw.Draw(frame)
        art.draw_particles(d, sc["background"], t, seed * 7 + k)
        ground_y = (art.GROUND - box[1]) / ch * H
        zoom_px = H / ch * (art.BH / H)

        chars = sc["characters"]
        n = len(chars)
        xs = {1: [540], 2: [370, 710], 3: [250, 540, 830]}[n]
        size = {1: 600, 2: 500, 3: 420}[n] * zoom_px
        bubble_head = None
        talking_now = bool(sc.get("dialogue")) and 0.15 < lt < dur - 0.05
        for i, c in enumerate(chars):
            pal = art.char_palette(c["role"], i, seed + k * (c["role"] != "hero"))
            talking = (i == 0 and talking_now) or c["action"] == "talk"
            layer, ax, ay, head = art.draw_character(c, pal, t, lt, dur, size, talking, seed=i * 1.7 + k)
            x = xs[i]
            if c["action"] in ("walk", "run"):
                x += (p - 0.5) * (260 if c["action"] == "run" else 140)
            px, py = int(x - ax), int(ground_y - ay)
            frame.paste(layer, (px, py), layer)
            if i == 0:
                bubble_head = (px + head[0], py + head[1])
        if talking_now and bubble_head:
            pop = min(1.0, 0.6 + (lt - 0.15) * 4)
            min_y = 270 + 100 * len(title_lines) if t < 2.4 else 260
            art.draw_bubble(frame, sc["dialogue"], bubble_head[0], bubble_head[1], pop, min_y)

        d = ImageDraw.Draw(frame)
        w, age = _caption_at(words, t)
        if w:
            pop = 1.0 + max(0.0, 0.25 * (1 - age / 0.09))
            txt = w["word"].upper().strip(",.;:")
            _text_center(d, 1560, txt, int(118 * pop), (255, 230, 0), stroke=11)
        if t < 2.4:
            slide = min(1.0, t / 0.25)
            y0 = int(-260 + (230 + 260) * slide)
            bh = 30 + 100 * len(title_lines)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rounded_rectangle((40, y0 - 20, W - 40, y0 + bh), 40, fill=(0, 0, 0, 150))
            frame.paste(ov, (0, 0), ov)
            d = ImageDraw.Draw(frame)
            for li, line in enumerate(title_lines):
                _text_center(d, y0 + 55 + li * 100, line, 86, (255, 255, 255), stroke=8)
        if duration - t < 1.8:
            _text_center(d, 250, "FOLLOW FOR MORE!", 80, (255, 230, 0), stroke=9)

        arr = np.asarray(frame)
        if k > 0 and lt < 4 / FPS:  # flash on every cut
            a = [0.35, 0.2, 0.1, 0.05][min(3, int(lt * FPS))]
            arr = (arr * (1 - a) + 255 * a).astype(np.uint8)
        if fi in sample_at:
            samples[fi] = arr.copy()
        proc.stdin.write(arr.tobytes())
        if progress and fi % 150 == 0:
            progress(fi, nframes)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed while encoding frames")
    return scenes, samples
