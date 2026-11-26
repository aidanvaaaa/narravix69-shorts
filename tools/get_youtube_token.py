"""Run ONCE on your own computer to connect your YouTube channel.

  pip install google-auth-oauthlib
  python tools/get_youtube_token.py

A browser window opens: sign in with the Google account that owns the narravix69
YouTube channel (aidan.l.rangel@gmail.com), allow uploads, and the script prints a
refresh token. Save it as the GitHub secret YT_REFRESH_TOKEN. Never share it.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

client_id = input("Paste your YouTube Client ID: ").strip()
client_secret = input("Paste your YouTube Client secret: ").strip()
flow = InstalledAppFlow.from_client_config(
    {"installed": {"client_id": client_id, "client_secret": client_secret,
                   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                   "token_uri": "https://oauth2.googleapis.com/token",
                   "redirect_uris": ["http://localhost"]}},
    scopes=["https://www.googleapis.com/auth/youtube.upload"])
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
print("\nYour YT_REFRESH_TOKEN (save it as a GitHub secret, keep it private):\n")
print(creds.refresh_token)
