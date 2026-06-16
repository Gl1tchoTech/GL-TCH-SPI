from fastapi import APIRouter
from app.services.ytmusic_service import search

router = APIRouter(tags=["Search"])

@router.get("/search")
def search_music(q: str):
    return search(q)
