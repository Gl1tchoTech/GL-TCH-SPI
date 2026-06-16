from fastapi import APIRouter, HTTPException

from app.services.ytmusic_service import ytmusic

router = APIRouter(
    tags=["Lyrics"]
)


@router.get("/lyrics/{video_id}")
def lyrics(video_id: str):
    try:
        watch_playlist = ytmusic.get_watch_playlist(
            videoId=video_id
        )

        lyrics_browse_id = watch_playlist.get("lyrics")

        if not lyrics_browse_id:
            raise HTTPException(
                status_code=404,
                detail="Lyrics not available"
            )

        return ytmusic.get_lyrics(
            lyrics_browse_id
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
