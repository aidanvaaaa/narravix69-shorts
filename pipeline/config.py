"""Settings, read from environment (GitHub secrets / variables)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data"
FONT = str(ROOT / "assets" / "ComicRelief-Bold.ttf")

W, H, FPS = 1080, 1920, 30


def env(name, default=""):
    v = os.environ.get(name, "")
    return v if v.strip() else default


GEMINI_API_KEY = env("GEMINI_API_KEY")
GEMINI_MODEL = env("GEMINI_MODEL", "gemini-flash-latest")
VOICE = env("VOICE", "am_michael")
VOICE_SPEED = float(env("VOICE_SPEED", "1.0"))
POSTS_PER_DAY = int(env("POSTS_PER_DAY", "4"))
DRY_RUN = env("DRY_RUN", "false").lower() in ("1", "true", "yes")

YT_CLIENT_ID = env("YT_CLIENT_ID")
YT_CLIENT_SECRET = env("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = env("YT_REFRESH_TOKEN")

IG_USER_ID = env("IG_USER_ID")
IG_ACCESS_TOKEN = env("IG_ACCESS_TOKEN")
GRAPH_VERSION = env("GRAPH_VERSION", "v25.0")

TIKTOK_CLIENT_KEY = env("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = env("TIKTOK_CLIENT_SECRET")
TIKTOK_REFRESH_TOKEN = env("TIKTOK_REFRESH_TOKEN")

NOTIFY_WEBHOOK = env("NOTIFY_WEBHOOK")
