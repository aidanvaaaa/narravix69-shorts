"""Narration with the free open-source Kokoro voice, plus word timings for captions."""
import re
import wave

import numpy as np

from . import config

SR = 24000


def _write_wav(path, audio, sr=SR):
    a = np.clip(audio, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def _clean_word(t):
    return re.sub(r"[^\w'’-]", "", t)


def kokoro_tts(text, path):
    """Returns list of {word, start, end} in seconds and writes a 24 kHz wav."""
    from kokoro import KPipeline  # heavy import, only on the runner

    pipe = KPipeline(lang_code="a")
    chunks, words, offset = [], [], 0.0
    for res in pipe(text, voice=config.VOICE, speed=config.VOICE_SPEED, split_pattern=r"\n+"):
        audio = res.audio.detach().cpu().numpy() if hasattr(res.audio, "detach") else np.asarray(res.audio)
        for tok in (getattr(res, "tokens", None) or []):
            w = _clean_word(getattr(tok, "text", ""))
            st, en = getattr(tok, "start_ts", None), getattr(tok, "end_ts", None)
            if w and st is not None and en is not None:
                words.append({"word": tok.text.strip(), "start": offset + float(st),
                              "end": offset + float(en)})
        chunks.append(audio)
        offset += len(audio) / SR
    audio = np.concatenate(chunks) if chunks else np.zeros(SR)
    _write_wav(path, audio)
    return words, len(audio) / SR


def whisper_words(path):
    """Fallback word timings with faster-whisper (CPU)."""
    from faster_whisper import WhisperModel

    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(path), word_timestamps=True)
    out = []
    for s in segs:
        for w in s.words or []:
            out.append({"word": w.word.strip(), "start": float(w.start), "end": float(w.end)})
    return out


def fake_tts(text, path):
    """Offline stand-in used only for local testing: a quiet hum with estimated timings."""
    words, t = [], 0.3
    for raw in text.split():
        syl = max(1, len(re.findall(r"[aeiouy]+", raw.lower())))
        d = 0.12 + 0.13 * syl
        words.append({"word": raw, "start": t, "end": t + d})
        t += d + (0.35 if raw[-1] in ".!?" else 0.12 if raw[-1] == "," else 0.04)
    dur = t + 0.4
    n = int(dur * SR)
    tt = np.arange(n) / SR
    audio = np.zeros(n)
    for w in words:
        a, b = int(w["start"] * SR), int(w["end"] * SR)
        seg = tt[a:b]
        env = np.sin(np.linspace(0, np.pi, b - a))
        audio[a:b] += 0.25 * env * np.sin(2 * np.pi * 140 * seg) * (1 + 0.3 * np.sin(2 * np.pi * 6 * seg))
    _write_wav(path, audio)
    return words, dur


def narrate(text, path, fake=False):
    if fake:
        return fake_tts(text, path)
    words, dur = kokoro_tts(text, path)
    if len(words) < len(text.split()) * 0.6:  # timings missing -> align with whisper
        words = whisper_words(path)
    return words, dur
