import yt_dlp

def get_stream(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"

    options = {
        "quiet": True,
        "format": "bestaudio/best"
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=False
        )

    return {
        "id": video_id,
        "title": info.get("title"),
        "duration": info.get("duration"),
        "stream_url": info.get("url")
    }
