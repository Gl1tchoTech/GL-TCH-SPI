import yt_dlp
import os
import tempfile
import base64


def _load_cookies():
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64")

    if not cookies_b64:
        return None

    try:
        cookie_data = base64.b64decode(cookies_b64)

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode="wb"
        )

        temp_file.write(cookie_data)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        print(f"[cookies] decode failed: {repr(e)}")
        return None


def download_mp3(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    cookie_file = _load_cookies()

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(
        temp_dir,
        "%(id)s.%(ext)s"
    )

    options = {
        "quiet": True,
        "noplaylist": True,
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    }

    if cookie_file:
        options["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                url,
                download=True
            )

        mp3_path = os.path.join(
            temp_dir,
            f"{video_id}.mp3"
        )

        return {
            "video_id": video_id,
            "title": info.get("title"),
            "path": mp3_path
        }

    finally:
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass
