# narravix69 auto-shorts

Makes and posts one vertical short per run, 4 times a day, for free:

1. **Script**: Google Gemini (free tier) writes a "What if…" or "Why it sucks to be…" short and a scene plan.
2. **Voice**: Kokoro (free, open source), voice `am_michael` by default; word timings drive captions.
3. **Animation**: painted backgrounds, blocky characters with faces, cloud speech bubbles, yellow word captions.
4. **Sound**: original procedural music (ducked under the voice) + soft whooshes; loudness -14 LUFS.
5. **Checks**: length, resolution, audio, blank frames.
6. **Posts**: YouTube Shorts, Instagram Reels, TikTok (when connected). Discord gets a message every run.

## Run it by hand
Actions → **Post a short** → **Run workflow**. Leave *Don't post* ticked for a test; the video appears under
the run's **Artifacts**. Untick it to post for real.

## Settings (Settings → Secrets and variables → Actions → Variables)
- `VOICE` – Kokoro voice, e.g. `am_michael`, `am_onyx`, `bm_george`
- `POSTS_PER_DAY` – `4` (default) or `3`
- `GEMINI_MODEL` – default `gemini-flash-latest`

## Secrets
`GEMINI_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `IG_USER_ID`, `IG_ACCESS_TOKEN`,
`TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REFRESH_TOKEN`, `NOTIFY_WEBHOOK`.

## Platform limits to know
- YouTube uploads stay **private** until the Google project passes YouTube's API audit
  (form: https://support.google.com/youtube/contact/yt_api_form).
- TikTok posts are **private** until the TikTok app passes its Content Posting audit.
- The Instagram token lasts 60 days; Discord will warn you 10 days before it expires.

## Local test (no keys needed)
`python -m pipeline.main --sample --fake-voice --dry-run` → `out/*.mp4`
