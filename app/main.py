from fastapi import FastAPI

from app.routers import (
    search,
    albums,
    artists,
    playlists,
    lyrics,
    stream,
    song,
    download,
    debug
)

app = FastAPI(
    title="GL$TCH-SPI",
    version="1.0.0"
)

app.include_router(search.router)
app.include_router(albums.router)
app.include_router(artists.router)
app.include_router(playlists.router)
app.include_router(lyrics.router)
app.include_router(stream.router)
app.include_router(song.router)
app.include_router(download.router)
app.include_router(debug.router)

@app.get("/")
def root():
    return {
        "name": "GL$TCH-SPI",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {
        "status": "Working"
    }
