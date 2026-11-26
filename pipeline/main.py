"""One run = one short: topic -> script -> voice -> animation -> sound -> checks -> post -> log."""
import argparse
import datetime as dt
import json
import random
import re
import subprocess
import sys
import time
import traceback


from . import config, render, script, sound, upload, voice


def log(msg):
    print(f"[{dt.datetime.now(dt.timezone.utc):%H:%M:%S}] {msg}", flush=True)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def quality_checks(path, samples):
    info = probe(path)
    dur = float(info["format"]["duration"])
    types = [s["codec_type"] for s in info["streams"]]
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    problems = []
    if not 25 <= dur <= 62:
        problems.append(f"duration {dur:.1f}s outside 25-62s")
    if "audio" not in types:
        problems.append("no audio")
    if (v["width"], v["height"]) != (1080, 1920):
        problems.append(f"resolution {v['width']}x{v['height']}")
    for fi, arr in samples.items():
        if arr.std() < 8:
            problems.append(f"frame {fi} looks blank")
    if path.stat().st_size > 100 * 1024 * 1024:
        problems.append("file over 100 MB")
    return problems, dur


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:50]


def should_skip_slot():
    """With POSTS_PER_DAY=3 the earliest daily run is skipped."""
    return config.POSTS_PER_DAY <= 3 and dt.datetime.now(dt.timezone.utc).hour == 16


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="make the video but do not post")
    ap.add_argument("--sample", action="store_true", help="use the built-in sample script (no Gemini)")
    ap.add_argument("--fake-voice", action="store_true", help="offline placeholder voice for local tests")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--scheduled", action="store_true")
    a = ap.parse_args()
    dry = a.dry_run or config.DRY_RUN
    if a.scheduled and should_skip_slot():
        log("POSTS_PER_DAY=3: skipping this time slot")
        return 0
    config.OUT.mkdir(exist_ok=True)
    used_path = config.DATA / "topics_used.json"
    used = json.loads(used_path.read_text()) if used_path.exists() else []
    seed = int(time.time()) % 100000
    random.seed(seed)
    try:
        log("writing script")
        last_fmts = [u.get("format") for u in used[-2:] if isinstance(u, dict)]
        fmt = None
        if len(last_fmts) == 2 and last_fmts[0] == last_fmts[1]:
            fmt = "why_it_sucks" if last_fmts[0] == "what_if" else "what_if"
        plan = script.sample_plan() if a.sample else script.write_plan(
            [u["topic"] if isinstance(u, dict) else u for u in used], fmt)
        log(f"topic: {plan['topic']} | title: {plan['title']}")
        name = f"{dt.datetime.now(dt.timezone.utc):%Y%m%d_%H%M}_{slug(plan['title'])}"
        vwav = config.OUT / f"{name}_voice.wav"
        log("recording voice")
        words, vdur = voice.narrate(plan["script"], vwav, fake=a.fake_voice)
        duration = vdur + 0.6
        log(f"voice {vdur:.1f}s, {len(words)} timed words; rendering")
        silent = config.OUT / f"{name}_silent.mp4"
        scenes, samples = render.render_video(plan, words, duration, silent, seed=seed,
                                              progress=lambda i, n: log(f"  frame {i}/{n}"))
        log("mixing sound")
        mixwav = config.OUT / f"{name}_mix.wav"
        sound.mix(vwav, scenes, duration, mixwav, music=not a.no_music, mood=plan["format"], seed=seed)
        final = config.OUT / f"{name}.mp4"
        sound.mux(silent, mixwav, final)
        for f in (silent, mixwav, vwav):
            f.unlink(missing_ok=True)
        problems, dur = quality_checks(final, samples)
        if problems:
            raise RuntimeError("quality check failed: " + "; ".join(problems))
        log(f"video ready: {final.name} ({dur:.1f}s)")
        (config.OUT / f"{name}.json").write_text(json.dumps(plan, indent=2))
        if dry:
            upload.notify(f"🧪 Test video made (not posted): **{plan['title']}** — download it from the workflow run's artifacts.")
            return 0

        results = {}
        for plat, fn in (("youtube", upload.youtube), ("instagram", upload.instagram), ("tiktok", upload.tiktok)):
            try:
                results[plat] = fn(final, plan)
            except Exception as e:  # noqa: BLE001
                results[plat] = {"ok": False, "msg": f"{plat} failed: {e}"}
            log(f"{plat}: {results[plat]['msg']}")
        used.append({"topic": plan["topic"], "format": plan["format"], "title": plan["title"],
                     "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")})
        used_path.write_text(json.dumps(used, indent=1))
        with open(config.DATA / "post_log.jsonl", "a") as f:
            f.write(json.dumps({"date": dt.datetime.now(dt.timezone.utc).isoformat(), "title": plan["title"], "results": results}) + "\n")
        lines = [f"🎬 **{plan['title']}**"]
        for plat, r in results.items():
            mark = "✅" if r.get("ok") else ("⏭️" if r.get("skipped") else "❌")
            lines.append(f"{mark} {r['msg']} {r.get('url', '')}")
        days = upload.instagram_token_days_left()
        if days is not None and days < 10:
            lines.append(f"⚠️ Instagram token expires in {days:.0f} days — make a new one and update IG_ACCESS_TOKEN.")
        if not any(r.get("ok") for r in results.values()):
            lines.append("The video is saved in this run's artifacts so you can post it by hand.")
        upload.notify("\n".join(lines))
        return 0
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        upload.notify(f"❌ Shorts pipeline run failed, nothing was posted: {e}"[:1900])
        return 1


if __name__ == "__main__":
    sys.exit(main())
