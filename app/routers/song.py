from fastapi import APIRouter, HTTPException

from app.services.ytmusic_service import ytmusic

router = APIRouter(
    tags=["Songs"]
)


@router.get("/song/{video_id}")
def song(video_id: str):
    try:
        return ytmusic.get_watch_playlist(
            videoId=video_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
