"""3D render step: scene plan + word timings -> 1080x1920 silent mp4 (WebGL engine, headless Chromium)."""
import os
import pathlib
import shutil
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine3d"


def render_video(plan, words, duration, out_mp4, seed=0, progress=print, workdir=None):
    work = pathlib.Path(workdir or (ROOT / "out" / "work3d"))
    if work.exists():
        shutil.rmtree(work)
    (work / "tex").mkdir(parents=True)
    os.environ["TEX_DIR"] = str(work / "tex")
    from engine3d import director  # imported late so TEX_DIR is set first
    director.engine.TEXDIR = str(work / "tex")

    hud = None  # no corner overlays
    progress("exporting 3D shots")
    names, shots = director.export_all(plan, words, duration, str(work / "data"), seed=seed, hud=hud,
                                       title_lines=plan.get("title_lines"), end_text="FOLLOW FOR MORE")
    w, h = int(os.environ.get("RENDER_W", 720)), int(os.environ.get("RENDER_H", 1280))
    nproc = max(1, min(3, (os.cpu_count() or 2) // 2))
    groups = [names[i::nproc] for i in range(nproc)]
    progress(f"rendering {len(names)} shots at {w}x{h} with {nproc} worker(s)")
    procs = [subprocess.Popen(["node", str(ENGINE / "drive.js"), str(work), ",".join(g), "--w", str(w), "--h", str(h)])
             for g in groups if g]
    for p in procs:
        if p.wait() != 0:
            raise RuntimeError("3D renderer failed")
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{work / 'vid' / (n + '.mp4')}'\n" for n in names))
    joined = work / "joined.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    tmp = pathlib.Path(str(out_mp4) + ".tmp.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-vf", "scale=1080:1920:flags=lanczos",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                    str(tmp)], check=True)
    tmp.rename(out_mp4)

    samples = {}
    for t in (1.0, duration / 2, duration - 1.0):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(out_mp4), "-frames:v", "1",
                              "-vf", "scale=108:192", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        samples[round(t, 1)] = np.frombuffer(raw, np.uint8)
    # cut points for sound effects: one whoosh per sentence change (not every camera cut)
    scenes, seen = [], set()
    for s in shots:
        if s["sentence"] not in seen:
            seen.add(s["sentence"])
            scenes.append(dict(start=s["start"], idx=s["sentence"], fx=s.get("fx", [])))
    return scenes, samples
