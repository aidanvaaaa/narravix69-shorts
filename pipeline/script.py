"""Picks a topic and writes the script + scene plan with the free Gemini API."""
import json
import random
import re
import time

import requests

from . import config

BACKGROUNDS = ["grass_plains", "blocky_city", "night_city", "space", "ocean", "beach",
               "desert", "forest", "snow", "lava", "castle", "village", "arena",
               "classroom", "house", "sky", "pyramids", "battlefield", "ship_deck", "factory"]
OUTFITS = ["none", "hoodie", "knight", "viking", "pharaoh", "samurai", "astronaut",
           "peasant", "king", "soldier", "worker", "scientist", "pirate", "gladiator", "chef"]
ACTIONS = ["idle", "talk", "walk", "run", "jump", "shock", "fall", "grow", "shrink",
           "float", "fight", "think", "celebrate", "sad", "sleep", "work"]
MOODS = ["happy", "sad", "angry", "scared", "shocked", "smug", "tired", "neutral"]

SYSTEM = f"""You write viral 45-60 second vertical short videos for the channel narravix69.
Return ONLY JSON matching this shape:
{{"format": "what_if" | "why_it_sucks",
  "topic": "short topic label",
  "title": "under 60 characters, curiosity-driven, no hashtags",
  "script": "130-160 words, ONE paragraph",
  "hashtags": ["5 to 8 hashtags without #"],
  "scenes": [{{"sentence": 0, "background": one of {BACKGROUNDS},
              "characters": [{{"role": "hero"|"other"|"villain", "outfit": one of {OUTFITS},
                               "mood": one of {MOODS}, "action": one of {ACTIONS}}}],
              "dialogue": "optional, under 6 words, said by the first character",
              "caption_keyword": "one key word from that sentence"}}]}}

Rules:
- The FIRST sentence is the hook and must grab attention in the first second. No intro, no "in this video".
- Short punchy sentences. A concrete surprising detail every 2-3 sentences.
- what_if: a dramatic "What if..." premise in a blocky game-like world, escalating stakes, a twist ending.
- why_it_sucks: second person ("You're born in..."), dark-funny, ONLY real, widely documented history.
  Hedge legends ("reportedly"). Never invent numbers, names or quotes.
- End with a punchline or a question that makes people comment.
- Write numbers as words. No real living people, no brand names or trademarked game names, no copyrighted characters.
- Exactly one scene object per sentence of the script, in order, "sentence" = 0-based index.
- 1 to 3 characters per scene; the hero appears in most scenes. Faces always toward the viewer.
"""


def _call_gemini(prompt):
    body = {"systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 1.0}}
    models = [m for m in dict.fromkeys([config.GEMINI_MODEL, "gemini-flash-latest", "gemini-flash-lite-latest"]) if m]
    last = None
    for attempt in range(4):
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            try:
                r = requests.post(url, params={"key": config.GEMINI_API_KEY}, json=body, timeout=120)
            except requests.RequestException as e:
                last = f"{model}: {type(e).__name__}"
                continue
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            last = f"{model}: HTTP {r.status_code} {r.text[:200]}"
            if r.status_code in (401, 403):
                raise RuntimeError(last)
        time.sleep(20 * (attempt + 1))
    raise RuntimeError(last)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def _clean(plan):
    n = len(split_sentences(plan["script"]))
    scenes = {s.get("sentence", i): s for i, s in enumerate(plan.get("scenes", []))}
    fixed = []
    last = None
    for i in range(n):
        s = scenes.get(i) or last or {}
        s = dict(s)
        s["sentence"] = i
        if s.get("background") not in BACKGROUNDS:
            s["background"] = (last or {}).get("background", random.choice(BACKGROUNDS))
        chars = []
        for c in (s.get("characters") or [{"role": "hero"}])[:3]:
            chars.append({"role": c.get("role", "hero"),
                          "outfit": c.get("outfit") if c.get("outfit") in OUTFITS else "none",
                          "mood": c.get("mood") if c.get("mood") in MOODS else "neutral",
                          "action": c.get("action") if c.get("action") in ACTIONS else "idle"})
        s["characters"] = chars
        d = (s.get("dialogue") or "").strip()
        s["dialogue"] = " ".join(d.split()[:6])
        fixed.append(s)
        last = s
    plan["scenes"] = fixed
    plan["hashtags"] = [h.lstrip("#").replace(" ", "") for h in plan.get("hashtags", [])][:8]
    plan["title"] = plan.get("title", "")[:90]
    return plan


def write_plan(used_topics, fmt=None):
    fmt = fmt or random.choice(["what_if", "why_it_sucks"])
    recent = "\n".join(f"- {t}" for t in used_topics[-200:]) or "(none yet)"
    prompt = (f"Format: {fmt}\nPick a fresh, interesting topic. Do NOT repeat or closely "
              f"resemble any of these past topics:\n{recent}\n\nWrite the video now.")
    err = None
    for _ in range(3):
        try:
            plan = _call_gemini(prompt)
            words = len(plan.get("script", "").split())
            if not 110 <= words <= 180:
                err = f"script length {words} words"
                continue
            plan["format"] = fmt
            return _clean(plan)
        except Exception as e:  # noqa: BLE001
            err = repr(e)
            time.sleep(5)
    raise RuntimeError(f"Could not get a valid script from Gemini: {err}")


SAMPLE = {
    "format": "what_if", "topic": "what if gravity turned off for ten seconds",
    "title": "What If Gravity Turned Off For 10 Seconds?",
    "script": ("What if gravity switched off for exactly ten seconds? At second one, you lift off "
               "your bed like a balloon. Your cat is floating past the window, very confused. "
               "Second three, every car on the highway drifts up like a toy. Oceans start rising "
               "into giant wobbling blobs. At second five, the air itself begins to leak away into "
               "space. You grab a lamp post and hold on for your life. Second eight, your best "
               "friend floats by eating a sandwich, totally calm. Then gravity snaps back on. "
               "Everything falls at once, and the loudest crash in history shakes the whole world. "
               "Somehow, you land right back in bed. And the cat lands on its feet, of course. "
               "Would you have grabbed the lamp post, or the sandwich?"),
    "hashtags": ["whatif", "gravity", "animation", "shorts", "blocky", "story"],
    "scenes": [],
}


def sample_plan():
    bgs = ["sky", "house", "house", "blocky_city", "ocean", "space", "night_city", "sky",
           "blocky_city", "battlefield", "house", "house", "grass_plains"]
    acts = ["shock", "float", "float", "float", "shock", "float", "fight", "float", "fall",
            "fall", "sleep", "celebrate", "talk"]
    dlg = ["Uh oh!", "", "", "My car!", "", "I can't breathe!", "Hold on!", "Want some?",
           "", "AAAH!", "", "", ""]
    p = dict(SAMPLE)
    n = len(split_sentences(p["script"]))
    p["scenes"] = [{"sentence": i, "background": bgs[i % len(bgs)],
                    "characters": [{"role": "hero", "outfit": "hoodie", "mood": "shocked",
                                    "action": acts[i % len(acts)]}] +
                                  ([{"role": "other", "outfit": "none", "mood": "happy",
                                     "action": "float"}] if i in (7, 12) else []),
                    "dialogue": dlg[i % len(dlg)], "caption_keyword": ""} for i in range(n)]
    return _clean(p)
