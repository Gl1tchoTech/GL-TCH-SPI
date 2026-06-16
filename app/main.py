from fastapi import FastAPI

from app.routers import (
    search,
    albums,
    artists,
    playlists,
    lyrics,
    stream,
    song
)

app = FastAPI(
    title="YouTube Music API",
    version="1.0.0"
)

app.include_router(search.router)
app.include_router(albums.router)
app.include_router(artists.router)
app.include_router(playlists.router)
app.include_router(lyrics.router)
app.include_router(stream.router)


@app.get("/")
def root():
    return {
        "name": "YouTube Music API",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
