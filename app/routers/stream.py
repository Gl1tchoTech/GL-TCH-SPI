from fastapi import APIRouter, HTTPException

from app.services.ytdlp_service import get_stream

router = APIRouter(
    tags=["Streaming"]
)


@router.get("/stream/{video_id}")
def stream(video_id: str):
    try:
        return get_stream(video_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stream: {str(e)}"
        )
