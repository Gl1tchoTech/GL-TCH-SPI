import yt_dlp
import tempfile
import os


def download_mp3(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(temp_dir, "%(id)s.%(ext)s")

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
        ],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    mp3_path = os.path.join(temp_dir, f"{video_id}.mp3")

    return {
        "title": info.get("title"),
        "path": mp3_path,
    }
