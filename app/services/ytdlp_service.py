import yt_dlp
import os
import tempfile
import base64


def _load_cookies():
    """
    Optional cookie loader from base64 env var.
    Safe fallback if not provided.
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
        print(f"[cookies] decode failed: {repr(e)}")
        return None


def get_stream(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    cookie_file = _load_cookies()

    options = {
        "quiet": True,
        "noplaylist": True,

        # let yt-dlp decide best available format
        "format": "best",

        # improves compatibility on some environments
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

        formats = info.get("formats") or []

        # Debug info (safe to remove later)
        print(f"[yt-dlp] formats found: {len(formats)}")

        stream_url = None

        # Try best available format first
        if formats:
            for f in reversed(formats):
                if f.get("url"):
                    stream_url = f["url"]
                    break

        # fallback (sometimes yt-dlp provides direct url)
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
            "available": stream_url is not None
        }

    except Exception as e:
        print(f"[yt-dlp ERROR] {repr(e)}")

        return {
            "video_id": video_id,
            "error": str(e),
            "stream_url": None,
            "available": False
        }

    finally:
        # cleanup temp cookie file
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass