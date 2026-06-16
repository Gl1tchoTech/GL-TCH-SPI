from fastapi import APIRouter
from app.services.ytmusic_service import get_album

router = APIRouter(tags=["Albums"])

@router.get("/album/{browse_id}")
def album(browse_id: str):
    return get_album(browse_id)
