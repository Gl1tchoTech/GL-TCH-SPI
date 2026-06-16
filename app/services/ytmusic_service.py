from ytmusicapi import YTMusic

ytmusic = YTMusic()

def search(query):
    return ytmusic.search(query)

def get_artist(browse_id):
    return ytmusic.get_artist(browse_id)

def get_album(browse_id):
    return ytmusic.get_album(browse_id)

def get_playlist(playlist_id):
    return ytmusic.get_playlist(playlist_id)

def get_lyrics(browse_id):
    return ytmusic.get_lyrics(browse_id)
