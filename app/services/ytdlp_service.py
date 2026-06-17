import yt_dlp
import os
import tempfile
import base64


def _load_cookies():
    """
    Optional: loads cookies from base64 env var (if provided)
    """
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64")
    if not cookies_b64:
        return None

    try:
        cookie_data = base64.b64decode(cookies_b64)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb")
        temp_file.write(cookie_data)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"[cookies] Failed to decode cookies: {repr(e)}")
        return None


def get_stream(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    cookie_file = _load_cookies()

    options = {
        "quiet": True,
        "noplaylist": True,

        # more stable extraction on cloud environments
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }

    if cookie_file:
        options["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        # DEBUG (safe to remove later)
        formats = info.get("formats") or []
        print(f"[yt-dlp] formats found: {len(formats)}")

        # safest stream selection logic
        stream_url = None

        for f in reversed(formats):
            if f.get("url"):
                stream_url = f["url"]
                break

        # final fallback (sometimes present)
        if not stream_url:
            stream_url = info.get("url")

        return {
            "video_id": video_id,
            "title": info.get("title"),
            "artist": info.get("uploader"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "stream_url": stream_url,
            "format_count": len(formats),
        }

    except Exception as e:
        print(f"[yt-dlp ERROR] {repr(e)}")

        return {
            "video_id": video_id,
            "error": str(e),
            "stream_url": None
        }

    finally:
        # cleanup cookie temp file
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass