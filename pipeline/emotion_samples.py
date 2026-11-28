"""Emotional voice samples with Chatterbox (MIT licensed, free). Run after `pip install chatterbox-tts`.

Step 1 (python -m pipeline.emotion_samples refs): make short reference voices with Kokoro (synthetic, owned by nobody).
Step 2 (python -m pipeline.emotion_samples make): Chatterbox reads the same dramatic passage in several voices and
emotion levels, sentence by sentence, with natural pauses.
"""
import pathlib
import re
import subprocess
import sys

import numpy as np

OUT = pathlib.Path("out/emotion")
REF_TEXT = ("Listen carefully. What happens next will change everything. "
            "The sky goes quiet. Then the light breaks apart, piece by piece.")
PASSAGE = ("The Moon just broke. You have about two years to live. "
           "At first... it's beautiful. Seven glowing pieces drift across the night sky, and the whole world stops to watch. "
           "But gravity doesn't care how beautiful it is. The pieces grind into each other. They start to fall. "
           "And when the first one hits... the sky catches fire.")
KOKORO_REFS = {"onyx": "am_onyx", "fenrir": "am_fenrir", "george": "bm_george"}
SAMPLES = [  # (file label, reference or None for the built-in voice, exaggeration, cfg)
    ("1_default_natural", None, 0.5, 0.5),
    ("2_default_dramatic", None, 0.85, 0.3),
    ("3_deep_onyx_dramatic", "onyx", 0.8, 0.3),
    ("4_gritty_fenrir_dramatic", "fenrir", 0.8, 0.3),
    ("5_british_documentary", "george", 0.7, 0.35),
]


def refs():
    from kokoro import KPipeline
    OUT.mkdir(parents=True, exist_ok=True)
    pipes = {}
    for name, vid in KOKORO_REFS.items():
        p = pipes.setdefault(vid[0], KPipeline(lang_code=vid[0]))
        a = np.concatenate([np.asarray(r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else r.audio)
                            for r in p(REF_TEXT, voice=vid, speed=0.95)])
        import wave
        with wave.open(str(OUT / f"ref_{name}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
            w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
        print("ref", name)


def make():
    import torch
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    torch.set_num_threads(4)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    sents = [s for s in re.split(r"(?<=[.!?])\s+", PASSAGE) if s.strip()]
    for label, ref, ex, cfg in SAMPLES:
        parts = []
        for s in sents:
            kw = dict(exaggeration=ex, cfg_weight=cfg)
            if ref:
                kw["audio_prompt_path"] = str(OUT / f"ref_{ref}.wav")
            wav = model.generate(s, **kw)
            parts.append(wav)
            pause = 0.45 if s.endswith("...") or s.endswith(".") else 0.25
            parts.append(torch.zeros(1, int(model.sr * pause)))
        full = torch.cat(parts, dim=1)
        wavp = OUT / f"{label}.wav"
        ta.save(str(wavp), full, model.sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wavp), "-af", "loudnorm=I=-16:TP=-1.5",
                        "-b:a", "160k", str(OUT / f"{label}.mp3")], check=True)
        wavp.unlink()
        print("made", label, flush=True)


def _trim(w, sr, thr=0.012, keep=0.04):
    """Cut silence at both ends of a clip (keeps a few ms so words aren't clipped)."""
    import torch
    a = w.abs().squeeze(0)
    idx = torch.nonzero(a > thr).squeeze(-1)
    if len(idx) == 0:
        return w
    k = int(sr * keep)
    return w[:, max(0, int(idx[0]) - k): min(w.shape[1], int(idx[-1]) + k)]


def _join(parts, sr, pauses):
    """Join chunks with short natural pauses and 30 ms crossfades (no hard cuts)."""
    import torch
    out = parts[0]
    fade = int(sr * 0.03)
    for p, gap in zip(parts[1:], pauses):
        out = torch.cat([out, torch.zeros(1, int(sr * gap))], dim=1)
        ramp = torch.linspace(0, 1, fade).unsqueeze(0)
        p = p.clone(); p[:, :fade] *= ramp
        out = torch.cat([out, p], dim=1)
    return out


def _chunks(text, max_chars=230):
    """2-3 sentences per chunk so the intonation flows across sentences."""
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    out, cur = [], ""
    for s in sents:
        if cur and len(cur) + len(s) > max_chars:
            out.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return out


POLISH = "highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=6500:t=q:w=1.5:g=-2,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,aecho=0.85:0.4:28:0.12,loudnorm=I=-16:TP=-1.5"


def british():
    """Smoother British documentary narration: natural reference, sentence groups, soft pauses, warm polish."""
    import torch
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    torch.set_num_threads(4)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    sr = model.sr
    # 1) a natural-sounding British reference made by Chatterbox itself (flows better than the synthetic one)
    nat = OUT / "ref_george_natural.wav"
    ref_line = ("You know, most people never think about the Moon. It's just there, every night, quietly watching. "
                "But tonight... something is different.")
    w = model.generate(ref_line, audio_prompt_path=str(OUT / "ref_george.wav"), exaggeration=0.45, cfg_weight=0.5)
    ta.save(str(nat), _trim(w, sr), sr)
    variants = [
        ("A_british_flow", str(OUT / "ref_george.wav"), 0.5, 0.5, 230),
        ("B_british_natural", str(nat), 0.5, 0.5, 230),
        ("C_british_natural_emotional", str(nat), 0.65, 0.4, 230),
        ("D_british_one_take", str(nat), 0.55, 0.45, 1000),
    ]
    for label, ref, ex, cfg, mx in variants:
        chunks = _chunks(PASSAGE, mx)
        parts, pauses = [], []
        for c in chunks:
            parts.append(_trim(model.generate(c, audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg), sr))
            pauses.append(0.42 if c.rstrip().endswith("...") else 0.28)
        full = _join(parts, sr, pauses[:-1])
        wavp = OUT / f"{label}.wav"
        ta.save(str(wavp), full, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wavp), "-af", POLISH, "-b:a", "160k",
                        str(OUT / f"{label}.mp3")], check=True)
        wavp.unlink()
        print("made", label, flush=True)


def story():
    """Reads STORY_TEXT in the chosen narrator voice (British, natural, emotional) -> out/emotion/story.mp3"""
    import os
    import torch
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    torch.set_num_threads(4)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    sr = model.sr
    nat = pathlib.Path(os.environ.get("NARRATOR_REF", "assets/narrator_ref.ogg"))  # fixed narrator clip, so every video sounds the same
    ex, cfg = float(os.environ.get("NARRATOR_EX", "0.65")), float(os.environ.get("NARRATOR_CFG", "0.4"))
    text = os.environ["STORY_TEXT"]
    parts, pauses = [], []
    for c in _chunks(text, 230):
        parts.append(_trim(model.generate(c, audio_prompt_path=str(nat), exaggeration=ex, cfg_weight=cfg), sr))
        pauses.append(0.42 if c.rstrip().endswith("...") else 0.3)
    full = _join(parts, sr, pauses[:-1])
    wavp = OUT / "story.wav"
    ta.save(str(wavp), full, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wavp), "-af", POLISH, "-b:a", "192k", str(OUT / "story.mp3")], check=True)
    print("made story", flush=True)


VOICE_TEXT = ("This prisoner has a plan, and it starts with a single breadcrumb. Every morning, he saves one crumb from "
              "breakfast and leaves it on his window. The next day, a pigeon shows up. Then two. Then forty.")
VOICE_REFS = [  # (label, Kokoro voice used only as a synthetic starting point, exaggeration, cfg)
    ("01_current_narrator", None, 0.65, 0.4),
    ("02_british_lewis_deep", "bm_lewis", 0.6, 0.4),
    ("03_british_daniel_calm", "bm_daniel", 0.55, 0.45),
    ("04_british_fable_storyteller", "bm_fable", 0.65, 0.4),
    ("05_american_michael_warm", "am_michael", 0.6, 0.4),
    ("06_american_adam_deep", "am_adam", 0.6, 0.4),
    ("07_american_eric_documentary", "am_eric", 0.55, 0.45),
    ("08_american_onyx_gravel", "am_onyx", 0.6, 0.4),
    ("09_chatterbox_builtin", "builtin", 0.6, 0.4),
]


def voices():
    """Same Pigeon Escape passage in several storytelling voices (all synthetic, owned by nobody)."""
    import wave
    import torch
    import torchaudio as ta
    from kokoro import KPipeline
    from chatterbox.tts import ChatterboxTTS
    OUT.mkdir(parents=True, exist_ok=True)
    pipes = {}
    for label, vid, _, _ in VOICE_REFS:
        if vid in (None, "builtin"):
            continue
        p = pipes.setdefault(vid[0], KPipeline(lang_code=vid[0]))
        a = np.concatenate([np.asarray(r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else r.audio)
                            for r in p(REF_TEXT, voice=vid, speed=0.95)])
        with wave.open(str(OUT / f"ref_{vid}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
            w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    torch.set_num_threads(4)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    sr = model.sr
    ref_line = ("You know, most people never think about it. It's just there, every night, quietly waiting. "
                "But tonight... something is different.")
    for label, vid, ex, cfg in VOICE_REFS:
        kw = {}
        if vid is None:
            kw["audio_prompt_path"] = "assets/narrator_ref.ogg"
        elif vid != "builtin":
            nat = OUT / f"nat_{vid}.wav"  # let Chatterbox re-voice it first so it flows naturally (same recipe as the current narrator)
            w = model.generate(ref_line, audio_prompt_path=str(OUT / f"ref_{vid}.wav"), exaggeration=0.45, cfg_weight=0.5)
            ta.save(str(nat), _trim(w, sr), sr)
            kw["audio_prompt_path"] = str(nat)
        parts, pauses = [], []
        for c in _chunks(VOICE_TEXT, 230):
            parts.append(_trim(model.generate(c, exaggeration=ex, cfg_weight=cfg, **kw), sr))
            pauses.append(0.3)
        full = _join(parts, sr, pauses[:-1])
        wavp = OUT / f"{label}.wav"
        ta.save(str(wavp), full, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wavp), "-af", POLISH, "-b:a", "160k", str(OUT / f"{label}.mp3")], check=True)
        wavp.unlink()
        print("made", label, flush=True)


def story_daniel():
    """Story narration in the chosen calm British voice (Daniel)."""
    import os
    os.environ["NARRATOR_REF"] = "assets/narrator_daniel.ogg"
    os.environ["NARRATOR_EX"] = "0.55"
    os.environ["NARRATOR_CFG"] = "0.45"
    story()


if __name__ == "__main__":
    {"refs": refs, "make": make, "british": british, "story": story, "voices": voices, "story_daniel": story_daniel}[sys.argv[1]]()
