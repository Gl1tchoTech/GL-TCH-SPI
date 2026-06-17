from fastapi import APIRouter, HTTPException, Query
import subprocess
import tempfile
import base64
import os

router = APIRouter(tags=["Debug"])

ADMIN_KEY = os.getenv("ADMIN_KEY")


def load_cookie_file():
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64")

    if not cookies_b64:
        return None

    try:
        cookie_data = base64.b64decode(cookies_b64)

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode="wb"
        )

        temp_file.write(cookie_data)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        print(f"Cookie decode failed: {e}")
        return None


@router.get("/debug/formats")
def list_formats(
    url: str = Query(...),
    key: str = Query(...)
):
    if key != ADMIN_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid key"
        )

    cookie_file = load_cookie_file()

    try:
        command = [
            "yt-dlp",
            "--list-formats",
            url
        ]

        if cookie_file:
            command.extend([
                "--cookies",
                cookie_file
            ])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    finally:
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass
