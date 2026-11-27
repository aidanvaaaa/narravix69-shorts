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


if __name__ == "__main__":
    {"refs": refs, "make": make}[sys.argv[1]]()
