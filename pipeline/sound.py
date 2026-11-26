"""Original procedural music bed + soft sound effects, mixed under the narration."""
import subprocess
import wave

import numpy as np

SR = 44100


def _read_wav(path):
    with wave.open(str(path)) as w:
        sr, n = w.getframerate(), w.getnframes()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    if sr != SR:
        x = np.linspace(0, len(a) - 1, int(len(a) * SR / sr))
        a = np.interp(x, np.arange(len(a)), a)
    return a


def _write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def _lowpass(x, k):
    if k <= 1:
        return x
    c = np.cumsum(np.insert(x, 0, 0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.zeros(len(x) - len(y))])


def music_bed(dur, mood="what_if", seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    bpm = 100 if mood == "what_if" else 90
    beat = 60 / bpm
    roots = [57, 53, 60, 55] if mood == "what_if" else [50, 46, 48, 45]  # A F C G / D Bb C A
    out = np.zeros(n)
    bar = beat * 4
    for b in range(int(dur / bar) + 1):
        root = roots[b % 4]
        s, e = int(b * bar * SR), min(n, int((b + 1) * bar * SR))
        if s >= n:
            break
        tt = t[s:e] - b * bar
        env = np.minimum(1, tt / 0.3) * np.exp(-tt / (bar * 1.4))
        for semi in (0, 3 if mood != "what_if" else 4, 7, 12):
            f = 440 * 2 ** ((root + semi - 69) / 12)
            out[s:e] += 0.05 * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt))
        fb = 440 * 2 ** ((root - 12 - 69) / 12)
        for q in range(4):  # plucky bass on each beat
            qs = int(q * beat * SR)
            seg = tt[qs:qs + int(beat * SR)] - q * beat
            if len(seg):
                out[s + qs:s + qs + len(seg)] += 0.12 * np.exp(-seg * 7) * np.sin(2 * np.pi * fb * seg)
        for q in range(8):  # soft shaker
            qs = s + int(q * beat / 2 * SR)
            ln = int(0.05 * SR)
            if qs + ln < n:
                out[qs:qs + ln] += 0.02 * rng.standard_normal(ln) * np.exp(-np.arange(ln) / SR * 60)
        for q in (0, 2):  # gentle kick
            qs = s + int(q * beat * SR)
            ln = int(0.18 * SR)
            if qs + ln < n:
                kt = np.arange(ln) / SR
                out[qs:qs + ln] += 0.25 * np.exp(-kt * 18) * np.sin(2 * np.pi * (50 + 80 * np.exp(-kt * 30)) * kt)
    return out


def whoosh(rng, length=0.35):
    ln = int(length * SR)
    noise = rng.standard_normal(ln)
    env = np.sin(np.linspace(0, np.pi, ln)) ** 2
    return _lowpass(noise, 6) * env * 0.5


def pop(length=0.08):
    ln = int(length * SR)
    tt = np.arange(ln) / SR
    return np.sin(2 * np.pi * (900 - 5000 * tt) * tt) * np.exp(-tt * 45) * 0.6


def impact(rng):
    ln = int(0.5 * SR)
    tt = np.arange(ln) / SR
    return (np.sin(2 * np.pi * (60 + 120 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 7) +
            0.3 * _lowpass(rng.standard_normal(ln), 4) * np.exp(-tt * 14)) * 0.7


def mix(voice_wav, scenes, duration, out_wav, music=True, mood="what_if", seed=0):
    rng = np.random.default_rng(seed)
    voice = _read_wav(voice_wav)
    n = int(duration * SR) + SR // 2
    v = np.zeros(n)
    v[:min(n, len(voice))] = voice[:n]
    fx = np.zeros(n)

    def add(sig, at, gain):
        s = int(at * SR)
        e = min(n, s + len(sig))
        if s < n:
            fx[s:e] += sig[:e - s] * gain

    add(impact(rng), 0.0, 0.5)
    add(pop(), 0.05, 0.4)
    for sc in scenes[1:]:
        add(whoosh(rng), max(0, sc["start"] - 0.12), 0.18)
        if "shake" in (sc.get("fx") or []) or "fire" in (sc.get("fx") or []):
            add(impact(rng), sc["start"] + 0.05, 0.45)
        if set(sc.get("fx") or []) & {"confetti", "sparkles", "fireworks", "money"}:
            add(pop(), sc["start"] + 0.1, 0.3)
    out = v * 1.0 + fx
    if music:
        m = music_bed(n / SR, mood, seed)[:n]
        env = _lowpass(np.abs(v), int(0.25 * SR))
        duck = 1 - 0.65 * np.clip(env / (env.max() + 1e-6) * 4, 0, 1)
        if len(scenes) > 2:  # drop the music out just before the punchline
            ps = scenes[-1]["start"]
            a, b = int((ps - 0.9) * SR), int((ps + 0.2) * SR)
            g = np.ones(n)
            g[max(0, a):max(0, b)] = 0.0
            g = _lowpass(g, int(0.15 * SR))
            m *= g[:len(m)]
        out += m * duck * 0.35
    _write_wav(out_wav, out * 0.8)


def mux(video, audio_wav, out_mp4):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio_wav),
           "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)
