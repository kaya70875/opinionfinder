import requests
from app.utils.helpers import get_channel_id, get_video_ids
import os

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the YOUTUBE_API_KEY environment variable.")


def get_video_ids_from_channel(channel_name: str) -> list[str]:
    """
    Get all video IDs from a YouTube channel using the YouTube Data API v3.
    """
    try:
        print(f"Fetching video IDs for channel: {channel_name}...")
        channel_id = get_channel_id(channel_name, API_KEY)
        print(f"Channel ID: {channel_id}")
        if not channel_id:
            raise ValueError(f"Channel '{channel_name}' not found.")
        
        print(f"Channel ID: {channel_id}")
        
        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': API_KEY
        }

        res = requests.get(url, params=params).json()
        uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        return get_video_ids(uploads_playlist_id, API_KEY, 50)
    except Exception as e:
        print(f"Error fetching video IDs from channel: {e}")
        return []