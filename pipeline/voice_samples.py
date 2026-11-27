"""Records the same short narration in many free Kokoro voices so you can pick one (python -m pipeline.voice_samples)."""
import pathlib
import subprocess

import numpy as np

from . import config, voice

LINE = ("{name}. The Moon just broke. You have about two years to live. "
        "At first, the sky looks beautiful. Then the pieces start falling.")
VOICES = [  # (kokoro voice id, label)
    ("am_michael", "Michael, the current voice"),
    ("am_onyx", "Onyx"),
    ("am_fenrir", "Fenrir"),
    ("am_adam", "Adam"),
    ("am_eric", "Eric"),
    ("am_liam", "Liam"),
    ("am_echo", "Echo"),
    ("am_puck", "Puck"),
    ("bm_george", "George, British"),
    ("bm_lewis", "Lewis, British"),
    ("bm_daniel", "Daniel, British"),
    ("bm_fable", "Fable, British"),
    ("af_heart", "Heart, female"),
    ("bf_emma", "Emma, British female"),
]


def main():
    from kokoro import KPipeline
    out = pathlib.Path("out/voices")
    out.mkdir(parents=True, exist_ok=True)
    pipes = {}
    files = []
    for i, (vid, label) in enumerate(VOICES, 1):
        lang = vid[0]
        pipe = pipes.setdefault(lang, KPipeline(lang_code=lang))
        chunks = []
        for res in pipe(LINE.format(name=label.split(",")[0]), voice=vid, speed=config.VOICE_SPEED):
            a = res.audio.detach().cpu().numpy() if hasattr(res.audio, "detach") else np.asarray(res.audio)
            chunks.append(a)
        wav = out / f"{i:02d}_{vid}.wav"
        voice._write_wav(wav, np.concatenate(chunks))
        voice.deepen(wav)  # same speed and deeper pitch the videos use
        mp3 = out / f"{i:02d}_{label.split(',')[0].lower()}_{vid}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-b:a", "128k", str(mp3)], check=True)
        files.append(wav)
        print("made", mp3.name)
    lst = out / "list.txt"
    gap = out / "gap.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.8", str(gap)], check=True)
    lst.write_text("".join(f"file '{f.resolve()}'\nfile '{gap.resolve()}'\n" for f in files))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-b:a", "128k",
                    str(out / "00_ALL_VOICES.mp3")], check=True)
    for f in files + [gap, lst]:
        f.unlink()


if __name__ == "__main__":
    main()
