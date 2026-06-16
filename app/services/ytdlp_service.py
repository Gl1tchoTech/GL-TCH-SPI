import yt_dlp


def get_stream(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    options = {
        "quiet": True,
        "noplaylist": True,
        "format": "bestaudio/best"
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=False
        )

    return {
        "video_id": video_id,
        "title": info.get("title"),
        "artist": info.get("uploader"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "stream_url": info.get("url")
    }
