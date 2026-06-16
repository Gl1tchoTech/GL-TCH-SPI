from fastapi import APIRouter
from app.services.ytmusic_service import get_playlist

router = APIRouter(tags=["Playlists"])

@router.get("/playlist/{playlist_id}")
def playlist(playlist_id: str):
    return get_playlist(playlist_id)
