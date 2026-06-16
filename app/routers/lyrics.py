from fastapi import APIRouter
from app.services.ytmusic_service import get_lyrics

router = APIRouter(tags=["Lyrics"])

@router.get("/lyrics/{browse_id}")
def lyrics(browse_id: str):
    return get_lyrics(browse_id)
