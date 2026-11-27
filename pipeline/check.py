"""Quick account check: confirms the YouTube and Instagram keys work, without making a video.
Prints only account names and error messages, never the keys themselves."""
import os
import requests


def yt():
    cid, sec, rt = (os.environ.get(k, "").strip() for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not (cid and sec and rt):
        return "YouTube: one or more keys are empty"
    looks = []
    if not cid.endswith(".apps.googleusercontent.com"):
        looks.append("YT_CLIENT_ID doesn't look like a client ID")
    if not sec.startswith("GOCSPX-"):
        looks.append("YT_CLIENT_SECRET doesn't look like a client secret")
    if not rt.startswith("1//"):
        looks.append("YT_REFRESH_TOKEN doesn't look like a refresh token")
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid, "client_secret": sec, "refresh_token": rt, "grant_type": "refresh_token"}, timeout=30)
    if not r.ok:
        err = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"error": r.text[:200]}
        return f"YouTube: FAILED ({err.get('error')}: {err.get('error_description', '')})" + (" | " + "; ".join(looks) if looks else "")
    tok = r.json()["access_token"]
    ch = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                      headers={"Authorization": f"Bearer {tok}"}, timeout=30).json()
    items = ch.get("items") or []
    name = items[0]["snippet"]["title"] if items else "(no channel on this Google account)"
    return f"YouTube: OK, connected to channel '{name}'"


def ig():
    uid, tok = os.environ.get("IG_USER_ID", "").strip(), os.environ.get("IG_ACCESS_TOKEN", "").strip()
    ver = os.environ.get("GRAPH_VERSION", "v25.0")
    if not (uid and tok):
        return "Instagram: one or more keys are empty"
    r = requests.get(f"https://graph.facebook.com/{ver}/{uid}", params={"fields": "username,account_type", "access_token": tok}, timeout=30)
    if not r.ok:
        e = r.json().get("error", {}) if r.headers.get("content-type", "").startswith("application/json") else {"message": r.text[:200]}
        return f"Instagram: FAILED ({e.get('type', '')} code {e.get('code', '')}: {e.get('message', '')})"
    j = r.json()
    d = requests.get(f"https://graph.facebook.com/{ver}/debug_token", params={"input_token": tok, "access_token": tok}, timeout=30).json().get("data", {})
    scopes = ", ".join(d.get("scopes", [])) or "unknown"
    return f"Instagram: OK, connected to @{j.get('username')} ({j.get('account_type', '')}); permissions: {scopes}"


if __name__ == "__main__":
    for f in (yt, ig):
        try:
            print(f())
        except Exception as e:  # noqa: BLE001
            print(f"{f.__name__}: error {type(e).__name__}: {str(e)[:200]}")
