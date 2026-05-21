import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# ------------------------------
# Load environment variables from .env file
# ------------------------------
load_dotenv()

# ------------------------------
# Get Spotify API credentials
# ------------------------------
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8501")

# Ensure credentials exist
if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise Exception("Spotify API credentials not found. Please set them in .env file.")

# ------------------------------
# Initialize Spotify client with OAuth
# ------------------------------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private"  # Permission to read private playlists
))

# ------------------------------
# Function to fetch playlists for a mood
# ------------------------------
def get_playlists_for_mood(mood: str):
    query = f"{mood} music"
    
    try:
        results = sp.search(q=query, limit=5, type="playlist")
    except Exception as e:
        print(f"Error fetching playlists from Spotify: {e}")
        return []

    playlists = []
    for playlist in results.get("playlists", {}).get("items", []):
        if playlist: 
            playlists.append({
                "name": playlist.get("name", "No Name"),
                "url": playlist.get("external_urls", {}).get("spotify", "#"),
                "id": playlist.get("id"),  # <--- CRITICAL: We need this ID for the player!
                "image": playlist["images"][0]["url"] if playlist.get("images") else None
            })

    return playlists