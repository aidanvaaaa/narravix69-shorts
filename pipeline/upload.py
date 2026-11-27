"""Posting to YouTube Shorts, Instagram Reels and TikTok through their official APIs."""
import os
import time

import requests

from . import config


def caption_text(plan):
    tags = " ".join("#" + h for h in plan["hashtags"])
    desc = plan.get("description") or ""
    return f"{plan['title']}\n\n{desc}\n\nFollow @narravix69 for more.\n\n{tags} #shorts".replace("\n\n\n\n", "\n\n")


# ---------------------------------------------------------------- YouTube
def youtube(path, plan):
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET and config.YT_REFRESH_TOKEN):
        return {"ok": False, "skipped": True, "msg": "YouTube secrets missing"}
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(None, refresh_token=config.YT_REFRESH_TOKEN, client_id=config.YT_CLIENT_ID,
                        client_secret=config.YT_CLIENT_SECRET, token_uri="https://oauth2.googleapis.com/token",
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    body = {"snippet": {"title": (plan["title"] + " #Shorts")[:100], "description": caption_text(plan),
                        "tags": plan["hashtags"], "categoryId": "24"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(path), mimetype="video/mp4", resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    status = resp.get("status", {}).get("privacyStatus")
    note = "" if status == "public" else " (YouTube set it to PRIVATE: the Google project needs the API audit before uploads can be public)"
    return {"ok": True, "url": f"https://youtube.com/shorts/{vid}", "msg": f"YouTube: {status}{note}"}


# --------------------------------------------------------------- Instagram
def instagram(path, plan):
    if not (config.IG_USER_ID and config.IG_ACCESS_TOKEN):
        return {"ok": False, "skipped": True, "msg": "Instagram secrets missing"}
    g = f"https://graph.facebook.com/{config.GRAPH_VERSION}"
    tok = config.IG_ACCESS_TOKEN
    r = requests.post(f"{g}/{config.IG_USER_ID}/media", data={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption_text(plan),
        "share_to_feed": "true", "access_token": tok}, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Instagram {r.status_code}: {r.text[:400]}")
    cid = r.json()["id"]
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        up = requests.post(f"https://rupload.facebook.com/ig-api-upload/{config.GRAPH_VERSION}/{cid}",
                           headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)},
                           data=f, timeout=600)
    up.raise_for_status()
    for _ in range(60):
        st = requests.get(f"{g}/{cid}", params={"fields": "status_code,status", "access_token": tok}, timeout=30).json()
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram processing failed: {st}")
        time.sleep(10)
    pub = requests.post(f"{g}/{config.IG_USER_ID}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    if not pub.ok:
        raise RuntimeError(f"Instagram publish {pub.status_code}: {pub.text[:400]}")
    mid = pub.json()["id"]
    link = requests.get(f"{g}/{mid}", params={"fields": "permalink", "access_token": tok}, timeout=30).json().get("permalink", "")
    return {"ok": True, "url": link, "msg": "Instagram: published"}


def instagram_token_days_left():
    """Warn before the 60-day token expires."""
    try:
        r = requests.get(f"https://graph.facebook.com/{config.GRAPH_VERSION}/debug_token",
                         params={"input_token": config.IG_ACCESS_TOKEN, "access_token": config.IG_ACCESS_TOKEN}, timeout=30).json()
        exp = r.get("data", {}).get("expires_at", 0)
        return None if not exp else (exp - time.time()) / 86400
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------ TikTok
def tiktok(path, plan):
    if not (config.TIKTOK_CLIENT_KEY and config.TIKTOK_CLIENT_SECRET and config.TIKTOK_REFRESH_TOKEN):
        return {"ok": False, "skipped": True, "msg": "TikTok not connected yet (skipped)"}
    base = "https://open.tiktokapis.com/v2"
    tr = requests.post(f"{base}/oauth/token/", data={
        "client_key": config.TIKTOK_CLIENT_KEY, "client_secret": config.TIKTOK_CLIENT_SECRET,
        "grant_type": "refresh_token", "refresh_token": config.TIKTOK_REFRESH_TOKEN}, timeout=30).json()
    access = tr.get("access_token")
    if not access:
        raise RuntimeError(f"TikTok token refresh failed: {tr}")
    hdr = {"Authorization": f"Bearer {access}", "Content-Type": "application/json; charset=UTF-8"}
    info = requests.post(f"{base}/post/publish/creator_info/query/", headers=hdr, timeout=30).json().get("data", {})
    opts = info.get("privacy_level_options", ["SELF_ONLY"])
    privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opts else opts[0]
    size = os.path.getsize(path)
    init = requests.post(f"{base}/post/publish/video/init/", headers=hdr, json={
        "post_info": {"title": caption_text(plan)[:2000], "privacy_level": privacy, "disable_duet": False,
                      "disable_comment": False, "disable_stitch": False, "is_aigc": True},
        "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}},
        timeout=30).json()
    data = init.get("data") or {}
    if "upload_url" not in data:
        raise RuntimeError(f"TikTok init failed: {init}")
    with open(path, "rb") as f:
        put = requests.put(data["upload_url"], data=f, timeout=600, headers={
            "Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}"})
    put.raise_for_status()
    note = "" if privacy == "PUBLIC_TO_EVERYONE" else " (posted as private until the TikTok app passes audit)"
    return {"ok": True, "url": "", "msg": f"TikTok: uploaded, privacy {privacy}{note}"}


def notify(text):
    if not config.NOTIFY_WEBHOOK:
        print(text)
        return
    try:
        requests.post(config.NOTIFY_WEBHOOK, json={"content": text[:1900], "username": "Narravix69 Pipeline"}, timeout=20)
    except Exception as e:  # noqa: BLE001
        print("notify failed", e)
