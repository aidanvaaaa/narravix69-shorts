"""Picks a topic and writes the script + scene plan with the free Gemini API."""
import json
import random
import re
import time

import requests

from . import config

STAGES = ["bedroom", "livingroom", "school_hall", "gym", "garage", "kitchen", "shop", "cafeteria", "diner",
          "party_room", "city_day", "city_night", "suburb_night", "suburb_day", "schoolyard", "festival",
          "highway", "red_room", "void"]
OUTFITS = ["hero", "friend", "girl", "villain", "parent", "mom", "teacher", "grandma", "athlete", "worker", "cop", "kid"]
ACTIONS = ["idle", "talk", "walk", "run", "point", "cheer", "shock", "scared", "think", "sad", "phone",
           "jump", "punch", "dance", "fall", "lie", "float", "wave", "sit"]
MOODS = ["happy", "excited", "laugh", "neutral", "sad", "crying", "worried", "scared", "terrified", "shocked",
         "angry", "shouting", "smug", "determined", "powerful", "tired", "blank", "panic"]
SHOTS = ["wide", "medium", "close", "low", "ots", "pov", "drone", "track", "dutch", "reveal", "ecu", "detail"]
FX = ["rain", "snow", "fire", "smoke", "confetti", "fireworks", "sparkles", "money", "shake"]
PROPS = ["car", "dog", "cash", "box", "jar", "trophy", "tv"]
LOOKS = ["normal", "gray", "night", "red", "warm", "cold", "dream"]

SYSTEM = f"""You write AND direct viral 35-55 second vertical 3D animated shorts for the channel narravix69,
in a blocky game-style world. Return ONLY JSON matching this shape:
{{"format": "what_if" | "why_it_sucks",
  "topic": "short topic label",
  "title": "under 60 characters, curiosity-driven, no hashtags",
  "title_lines": ["2 short lines for the on-screen hook title, max 18 characters each, UPPERCASE"],
  "description": "1-2 sentence post caption that teases the story and asks a question",
  "script": "100-140 words, ONE paragraph, narrated in second person or as a story",
  "hashtags": ["6 to 10 hashtags without #, mix of broad (shorts, animation) and topic tags"],
  "keywords": ["4-8 single words from the script to highlight in the captions"],
  "hud": {{"tag": "short status like ● LIVE or DAY 1", "sub": "short status line, max 18 chars",
           "label": "what the counter measures, max 22 chars"}},
  "hud_values": ["one counter value per sentence that escalates, max 8 characters, written with DIGITS and symbols, e.g. 100%, 75%, DAY 3, $40, 0:30, 2 HRS"],
  "scenes": [{{"sentence": 0, "stage": one of {STAGES},
              "shots": [1-2 camera shots from {SHOTS}],
              "characters": [{{"role": "hero"|"other"|"crowd", "outfit": one of {OUTFITS},
                               "mood": one of {MOODS}, "action": one of {ACTIONS}}}],
              "fx": [0-2 effects from {FX}],
              "look": one of {LOOKS} (colour grade; "normal" unless the story calls for it),
              "props": [0-2 props from {PROPS}]}}]}}

Story rules:
- The FIRST sentence is the hook and must grab attention in the first second. No intro, no "in this video".
- Short punchy sentences (6-14 words). A concrete surprising detail every 2-3 sentences. Escalate.
- what_if: a dramatic "What if..." premise in a modern blocky world, escalating stakes, a twist ending.
- why_it_sucks: "Why it sucks to be ..." about a relatable modern role or situation (the youngest sibling,
  the new kid, the last one picked, a night-shift worker, the kid whose birthday is on a holiday...), dark-funny.
- End with a punchline or a question that makes people comment.
- Write numbers as words in the script (the voice reads them). Only hud_values use digits. No real people, no brand names, no trademarked game names, no copyrighted characters.

Directing rules (you are the camera operator too):
- Exactly one scene object per sentence of the script, in order, "sentence" = 0-based index.
- The world is a shiny, gold, rich downtown like New York and San Francisco: use "city_day" (golden hour) or
  "city_night" for at least half of the scenes. Other stages are for moments that clearly happen indoors.
- The hero is a confident, rich, stylish guy (all black fit, gold chains, iced-out watch); write him that way.
- Pick the stage that best fits each sentence; stay in a location for 2-3 sentences, then move on.
- Open on a "close" or "low" shot of the hero; use "reveal" when the scale of something is shown,
  "drone" for big events, "dutch" for chaos, "ots"/"pov" only when another character is present, "wide" to set a place,
  "ecu" (extreme close-up on the face) for big emotions and reactions, "detail" (close on the chains and watch) once per video.
- Vary shots: never use the same shot twice in a row.
- The hero (outfit "hero") appears in every scene. Up to 3 more characters; use "crowd" for groups.
- Mood and action must match what the sentence says. Use "shake" for impacts and "fx" sparingly.
- Use "look" to show the story visually: "gray" when colour is gone or for a sad memory, "night" for night-time,
  "red" for danger or rage, "warm" for happy moments, "cold" for winter or loneliness, "dream" for dreams.
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


_NUMS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                       "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_NUMS.update({w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())})
_SCALE = {"hundred": 100, "thousand": 1000, "million": 1000000, "billion": 1000000000}
_SHORT = {1000: "K", 1000000: "M", 1000000000: "B"}


def digits(text):
    """'ninety percent' -> '90%', 'one million' -> '1M', 'day one' -> 'DAY 1' (counter values must be short digits)."""
    out, num, cur, big = [], None, 0, 0
    def flush():
        nonlocal num, cur, big
        if num is not None:
            v = big + cur
            for k in (1000000000, 1000000, 1000):
                if v >= k and v % k == 0:
                    out.append(f"{v // k}{_SHORT[k]}"); break
            else:
                out.append(str(v))
        num, cur, big = None, 0, 0
    for w in re.findall(r"[A-Za-z]+|[^A-Za-z\s]+", str(text)):
        lw = w.lower()
        if lw in _NUMS:
            num = True; cur += _NUMS[lw]
        elif lw in _SCALE and num is not None:
            if lw == "hundred":
                cur = (cur or 1) * 100
            else:
                big += (cur or 1) * _SCALE[lw]; cur = 0
        elif lw == "and" and num is not None:
            continue
        else:
            flush()
            out.append("%" if lw in ("percent", "pct") else w)
    flush()
    txt = " ".join(out).replace(" %", "%").replace("$ ", "$")
    return re.sub(r"\s+", " ", txt).strip()


def _pick(v, allowed, default):
    return v if v in allowed else default


def _clean(plan):
    n = len(split_sentences(plan["script"]))
    scenes = {s.get("sentence", i): s for i, s in enumerate(plan.get("scenes", []))}
    fixed, last = [], None
    for i in range(n):
        s = dict(scenes.get(i) or last or {})
        s["sentence"] = i
        s["stage"] = _pick(s.get("stage"), STAGES, (last or {}).get("stage", "city_day"))
        s["shots"] = [x for x in (s.get("shots") or []) if x in SHOTS][:2] or ["medium"]
        chars = []
        for c in (s.get("characters") or [{"role": "hero"}])[:4]:
            chars.append({"role": _pick(c.get("role"), ["hero", "other", "crowd"], "other"),
                          "outfit": _pick(c.get("outfit"), OUTFITS, "friend"),
                          "mood": _pick(c.get("mood"), MOODS, "neutral"),
                          "action": _pick(c.get("action"), ACTIONS, "idle")})
        if not any(c["role"] == "hero" for c in chars):
            chars.insert(0, {"role": "hero", "outfit": "hero", "mood": "neutral", "action": "talk"})
        for c in chars:
            if c["role"] == "hero":
                c["outfit"] = "hero"
        s["characters"] = chars
        s["fx"] = [x for x in (s.get("fx") or []) if x in FX][:2]
        s["props"] = [x for x in (s.get("props") or []) if x in PROPS][:2]
        s["look"] = _pick(s.get("look"), LOOKS, "normal")
        fixed.append(s)
        last = s
    plan["scenes"] = fixed
    plan["hashtags"] = [h.lstrip("#").replace(" ", "") for h in plan.get("hashtags", []) if h][:10]
    plan["title"] = plan.get("title", "")[:90]
    tl = [str(x).upper()[:22] for x in (plan.get("title_lines") or []) if x][:2]
    plan["title_lines"] = tl or [plan["title"].upper()[:22]]
    plan["keywords"] = [str(k) for k in plan.get("keywords", [])][:8]
    hud = plan.get("hud") if isinstance(plan.get("hud"), dict) else {}
    plan["hud"] = {k: digits(hud.get(k, ""))[:24] for k in ("tag", "sub", "label")}
    plan["hud_values"] = [digits(v).upper()[:9] for v in plan.get("hud_values", [])][:n]
    plan["description"] = str(plan.get("description", ""))[:300]
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
            if not 90 <= words <= 165:
                err = f"script length {words} words"
                continue
            plan["format"] = fmt
            return _clean(plan)
        except Exception as e:  # noqa: BLE001
            err = repr(e)
            time.sleep(5)
    raise RuntimeError(f"Could not get a valid script from Gemini: {err}")


def sample_plan():
    import pathlib
    p = json.loads((pathlib.Path(__file__).parent / "sample_plan.json").read_text())
    return _clean(p)
