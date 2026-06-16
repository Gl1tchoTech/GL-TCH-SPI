from fastapi import APIRouter
from app.services.ytmusic_service import get_artist

router = APIRouter(tags=["Artists"])

@router.get("/artist/{browse_id}")
def artist(browse_id: str):
    return get_artist(browse_id)
