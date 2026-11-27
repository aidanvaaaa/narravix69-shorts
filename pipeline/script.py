"""Picks a topic and writes the script + scene plan with the free Gemini API."""
import json
import random
import re
import time

import requests

from . import config

STAGES = ["bedroom", "livingroom", "school_hall", "gym", "garage", "kitchen", "shop", "cafeteria", "diner",
          "party_room", "city_day", "city_night", "suburb_night", "suburb_day", "schoolyard", "festival",
          "highway", "red_room", "void",
          "space", "moon_breaks", "earth_ring", "black_hole", "sun_dark", "asteroid", "meteor_city", "tsunami_city",
          "flood_city", "ash_city", "frozen_city", "ring_sky", "blackout_city", "volcano", "deep_ocean", "whale",
          "earth_core", "ocean_impact", "wasteland"]
WORLD_HELP = """Science stages (use these for the big moments, the hero watches or survives them):
space (Earth + Moon seen from an orbital deck), moon_breaks (the Moon cracking into chunks), earth_ring (Earth with a
rock/debris ring), black_hole (glowing swirling disk pulling things in), sun_dark (Sun gone black, frozen dark Earth),
asteroid (fiery rock flying at Earth), meteor_city (orange sky, meteors raining on the city), tsunami_city (giant wave
rolling down the street), flood_city (city streets under water), ash_city (gray ash falling, volcano on the horizon),
frozen_city (dark frozen city, snow), ring_sky (huge planetary ring arching over the city), blackout_city (whole city
dark, no power), volcano (erupting supervolcano close up), deep_ocean (sinking into the dark deep sea with glowing
creatures), whale (deep sea with a giant blue whale), earth_core (cut-away of Earth's layers, falling through the core),
ocean_impact (asteroid impact ring spreading across the ocean), wasteland (dead trees, wilted flowers, piles of trash)."""
TOPICS = [
    ("The Moon shatters", "The Moon just broke. You have about two years to live.",
     "0 sec flash, Moon cracks into 7 chunks; days: glowing pieces fill the night sky, people think it is beautiful; months: pieces grind into a Saturn-like ring; ~2 years: White Sky, trillions of fragments rain down, sky on fire, oceans boil.",
     "moon_breaks, space, earth_ring, meteor_city"),
    ("Earth stops spinning for one second", "Everything not bolted to the bedrock keeps moving at one thousand miles per hour.",
     "people, cars, trees, buildings, oceans flung east at bullet speed; winds faster than any tornado; oceans slosh into continents as mega-tsunamis.",
     "space, city_day, tsunami_city, flood_city"),
    ("A coin-sized black hole appears on your desk", "It's tiny. It weighs as much as Earth. And it's hungry.",
     "desk, room, house pulled in and spaghettified; Earth crushed inward around a marble; twist: the Moon now orbits a black hole the size of a coin.",
     "bedroom, black_hole, space"),
    ("Every insect disappears overnight", "You'd be happy for exactly one week.",
     "week 1: no mosquitoes, then birds starve; months: fruit, coffee and chocolate vanish, nothing pollinates; years: dead things stop rotting, the world piles up with waste.",
     "suburb_day, shop, wasteland"),
    ("The Sun turns into a black hole", "Earth's orbit wouldn't change at all. That's the scary part.",
     "8 minutes nothing happens (light travel time); then the sky goes black; plants die within weeks; oceans freeze from the top down; survivors huddle by deep-sea volcanic vents.",
     "city_day, sun_dark, frozen_city, deep_ocean"),
    ("Falling into the Mariana Trench without a sub", "At the bottom, the water pressure is like fifty jumbo jets sitting on you.",
     "depth ticks down; anglerfish, giant isopods, ghost sharks appear by layer; ears pop, lungs compress.",
     "deep_ocean"),
    ("A 10 km asteroid hits the middle of the Atlantic", "Same size as the one that killed the dinosaurs. Here's what happens to New York.",
     "impact: a mile-tall tsunami ring; minutes: molten rock rains back down, forests burn worldwide; months: ash blocks the sun, impact winter.",
     "asteroid, ocean_impact, tsunami_city, meteor_city, frozen_city"),
    ("Humans can breathe underwater", "We'd colonize seventy percent of the planet within a century.",
     "underwater cities, ocean wars over territory, new kinds of humans; dark turn: we overfish everything and sharks start treating us as prey.",
     "deep_ocean, whale, flood_city"),
    ("Earth's gravity doubles for 10 seconds", "You'd feel like you were carrying a second you on your back.",
     "bridges sag, planes drop, tall buildings buckle; people collapse, weakest structures crumble first.",
     "city_day, city_night, space"),
    ("Yellowstone erupts tomorrow", "This isn't fiction. It's overdue... sort of.",
     "blast radius spreads, ash covers half the country; crops fail worldwide; the Year Without Summer.",
     "volcano, ash_city, frozen_city, wasteland"),
    ("Surviving being swallowed by a blue whale", "Spoiler: it's impossible, and here's every reason why.",
     "its throat is the size of a dinner plate so you'd be spat out; if you did fit: stomach chambers, acid, no oxygen.",
     "whale, deep_ocean"),
    ("All the ice on Earth melts", "Say goodbye to Florida, London and Shanghai.",
     "sea level rises seventy meters; the map is redrawn city by city; mass migration, new coastlines, cities become underwater ruins.",
     "space, flood_city, tsunami_city, deep_ocean"),
    ("Earth has rings like Saturn", "Every sunset would look like this.",
     "gorgeous visuals, but the rings cast shadows that create permanent winter zones; satellites become impossible; ring debris rains down as meteors.",
     "ring_sky, earth_ring, frozen_city, meteor_city"),
    ("Jumping into a hole through the entire Earth", "It takes exactly forty two minutes. Here's what you'd see.",
     "crust, then the mantle getting hotter, then the outer core of liquid iron; you'd fall back and forth forever like a pendulum unless air drag stops you in the middle.",
     "city_day, earth_core"),
    ("The internet disappears forever", "Day one is annoying. Day thirty is chaos.",
     "day 1: no phones, banks freeze, GPS fails; week 1: supply chains collapse, stores empty; months: paper maps, landlines and letters come back.",
     "city_night, blackout_city, shop, city_day"),
]
OUTFITS = ["hero", "friend", "girl", "villain", "parent", "mom", "teacher", "grandma", "athlete", "worker", "cop", "kid"]
ACTIONS = ["idle", "talk", "walk", "run", "point", "cheer", "shock", "scared", "think", "sad", "phone",
           "jump", "punch", "dance", "fall", "lie", "float", "wave", "sit"]
MOODS = ["happy", "excited", "laugh", "neutral", "sad", "crying", "worried", "scared", "terrified", "shocked",
         "angry", "shouting", "smug", "determined", "powerful", "tired", "blank", "panic"]
SHOTS = ["event", "wide", "medium", "close", "low", "ots", "pov", "drone", "track", "dutch", "reveal", "ecu", "detail"]
FX = ["rain", "snow", "fire", "smoke", "confetti", "fireworks", "sparkles", "money", "shake"]
PROPS = ["car", "dog", "cash", "box", "jar", "trophy", "tv"]
LOOKS = ["normal", "gray", "night", "red", "warm", "cold", "dream"]

SYSTEM = f"""You write AND direct gripping, high-retention 65-90 second vertical 3D animated "what if" science shorts
for the channel narravix69, in a blocky game-style world. Return ONLY JSON matching this shape:
{{"format": "what_if",
  "topic": "short topic label",
  "title": "under 60 characters, curiosity-driven, no hashtags",
  "title_lines": ["2 short lines for the on-screen hook title, max 18 characters each, UPPERCASE"],
  "description": "1-2 sentence post caption that teases the story and asks a question",
  "script": "170-230 words, ONE paragraph, present tense, second person (You...)",
  "hashtags": ["6 to 10 hashtags without #, mix of broad (shorts, science, whatif) and topic tags"],
  "keywords": ["4-8 single words from the script to highlight in the captions"],
  "stamps": ["one short timeline label per sentence with DIGITS, max 14 characters, e.g. 0 SEC, 8 MIN, DAY 3, 2 YEARS, -4000 M, or an empty string when the time does not change"],
  "scenes": [{{"sentence": 0, "stage": one of {STAGES},
              "shots": [2 camera shots from {SHOTS}],
              "characters": [{{"role": "hero"|"other"|"crowd", "outfit": one of {OUTFITS},
                               "mood": one of {MOODS}, "action": one of {ACTIONS}}}],
              "fx": [0-2 effects from {FX}],
              "look": one of {LOOKS} (colour grade; "normal" unless the story calls for it),
              "props": [0-2 props from {PROPS}]}}]}}

{WORLD_HELP}

Story rules:
- Quality gate: before writing, reject any idea that is generic, slow or obvious. Pick the most gripping,
  most visual version. Every video needs an instant hook, escalating tension, and a memorable ending.
- The FIRST sentence (first 3 seconds) drops the viewer straight into danger, a shocking fact, an impossible
  choice or an absurd visual. Bad: "Today we look at what happens when...". Good: "Your pilot just collapsed,
  the plane is diving, and you are the only one awake." No intro, no filler, no "in this video".
- Present tense, second person, short rhythmic sentences (5-12 words). Every sentence must escalate: a new
  danger, a hard number, a ticking deadline, a reversal. Concrete, vivid, physical details.
- Follow the topic brief you are given: use its hook (you may sharpen it) and its beats, in order, as a ticking
  timeline (seconds -> minutes -> days -> years, or a depth / distance counting down). Keep the science accurate
  and explain cause and effect clearly so every sentence makes sense to a 13-year-old. One clear idea per sentence.
- END ON A CLIFFHANGER: the LAST sentence leaves the viewer desperate to know what happens next. Build to the
  biggest moment, then cut right before the answer: a new threat appears, a shocking reveal, or a question left
  hanging ("But that's not even the worst part.", "And then the ground starts shaking."). Do NOT resolve it and
  do NOT say "follow" or "part 2" in the script; the end screen says that.
- Write numbers as words in the script (the voice reads them). Only stamps use digits. No real people, no brand names, no trademarked game names, no copyrighted characters.

Directing rules (you are the camera operator too):
- Exactly one scene object per sentence of the script, in order, "sentence" = 0-based index. Count your sentences: the number of scenes MUST equal the number of sentences.
- SHOW what the sentence says: pick the science stage that matches it (the Moon breaking -> moon_breaks, waves ->
  tsunami_city, deep sea -> deep_ocean...). Use the stages suggested in the topic brief. Use city_day / city_night
  only for normal everyday moments before or after the disaster.
- The hero ("you") is a confident stylish guy who witnesses and survives it all; he reacts to what happens.
- Pick the stage that best fits each sentence; stay in a location for 2-3 sentences, then move on.
- Open on a "close" or "low" shot of the hero; use "event" to show the spectacle itself (the planet, the wave,
  the volcano, the creatures) in at least half of the sentences, "reveal" when the scale of something is shown,
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
        if scenes.get(i):
            s = dict(scenes[i])
        else:  # missing scene: reuse the last place but with a fresh camera and a standing hero
            s = dict(last or {})
            s["shots"] = ["event", "close"] if i % 2 else ["close", "event"]
            s["characters"] = [dict(c, action="idle" if c.get("action") in ("lie", "fall") else c.get("action"))
                               for c in (s.get("characters") or [])]
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
    plan["stamps"] = [digits(v).upper()[:16] for v in (plan.get("stamps") or [])][:n]
    plan.pop("hud", None); plan.pop("hud_values", None)
    plan["description"] = str(plan.get("description", ""))[:300]
    return plan


def next_topic(used_topics):
    used = {str(u).strip().lower() for u in used_topics}
    for t in TOPICS:
        if t[0].lower() not in used:
            return t
    return None


def write_plan(used_topics, fmt=None):
    fmt = "what_if"
    t = next_topic(used_topics)
    if t:
        name, hook, beats, stages = t
        prompt = (f"Topic: What if... {name}?\nHook to open with (first sentence): {hook}\nBeats, in order: {beats}\n"
                  f"Suggested stages: {stages}\nWrite the video now.")
    else:
        recent = "\n".join(f"- {x}" for x in used_topics[-200:])
        prompt = ("Pick a fresh science / space / nature-disaster \"what if\" topic in the same style as these "
                  f"(a shocking number in the hook, a ticking timeline, a cliffhanger at the end). Do NOT repeat any of these:\n{recent}\n"
                  "Write the video now.")
    err = None
    for _ in range(3):
        try:
            plan = _call_gemini(prompt)
            words = len(plan.get("script", "").split())
            if not 150 <= words <= 260:
                err = f"script length {words} words"
                continue
            nsent = len(split_sentences(plan["script"]))
            if len(plan.get("scenes") or []) < nsent - 1:
                err = f"{len(plan.get('scenes') or [])} scenes for {nsent} sentences"
                continue
            plan["format"] = fmt
            if t:
                plan["topic"] = t[0]
            return _clean(plan)
        except Exception as e:  # noqa: BLE001
            err = repr(e)
            time.sleep(5)
    raise RuntimeError(f"Could not get a valid script from Gemini: {err}")


def sample_plan():
    import pathlib
    p = json.loads((pathlib.Path(__file__).parent / "sample_plan.json").read_text())
    return _clean(p)
