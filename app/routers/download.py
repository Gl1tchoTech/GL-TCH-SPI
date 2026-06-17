from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.download_service import download_mp3

router = APIRouter(tags=["Download"])


@router.get("/download/{video_id}")
def download(video_id: str):
    try:
        result = download_mp3(video_id)

        return FileResponse(
            result["path"],
            media_type="audio/mpeg",
            filename=f"{video_id}.mp3"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download: {str(e)}"
        )
