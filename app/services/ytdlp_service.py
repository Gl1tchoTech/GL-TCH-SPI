import yt_dlp
import os
import tempfile
import base64

def get_stream(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    options = {
    "quiet": True,
    "noplaylist": True,
    "format": "bestaudio[ext=m4a]/bestaudio/best"
    }
    
    # Handle cookies from environment variable
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64")
    temp_cookie_file = None
    
    if cookies_b64:
        try:
            # Decode base64 and write to temp file
            cookie_data = base64.b64decode(cookies_b64)
            temp_cookie_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt')
            temp_cookie_file.write(cookie_data)
            temp_cookie_file.close()
            options["cookiefile"] = temp_cookie_file.name
        except Exception as e:
            print(f"Failed to decode cookies: {e}")
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "video_id": video_id,
                "title": info.get("title"),
                "artist": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "stream_url": info.get("url")
            }
    except Exception as e:
        print(f"yt-dlp error: {repr(e)}")
        raise
    finally:
        # Cleanup temp cookie file
        if temp_cookie_file and os.path.exists(temp_cookie_file.name):
            os.unlink(temp_cookie_file.name)
