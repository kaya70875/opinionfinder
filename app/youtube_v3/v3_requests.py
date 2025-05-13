import httpx
from app.utils.helpers import get_channel_id, fetch_with_playlist_id, ChannelData
import os
from fastapi import HTTPException
from app.lib.timeout import TIMEOUT

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the YOUTUBE_API_KEY environment variable.")


async def fetch_channel(channel_name: str, max_results: int) -> ChannelData:
    """
    Get all channel snippets from a YouTube channel using the YouTube Data API v3.
    """
    try:
        print(f"Fetching video IDs for channel: {channel_name}...")
        channel_id = await get_channel_id(channel_name, API_KEY)
        if not channel_id:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found.")
        
        print(f"Channel ID: {channel_id}")
        
        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': API_KEY
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)
            res = response.json()
            uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            print('upload_pid', uploads_playlist_id)
            return await fetch_with_playlist_id(uploads_playlist_id, API_KEY, max_results)
    except httpx.HTTPError as e:
        print(f"Error fetching video IDs from channel: {e}")
        return []