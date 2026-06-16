from fastapi import APIRouter
from app.services.ytdlp_service import get_stream

router = APIRouter(tags=["Streaming"])

@router.get("/stream/{video_id}")
def stream(video_id: str):
    return get_stream(video_id)
