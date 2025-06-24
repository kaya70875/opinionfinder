import logging
import httpx
import os
from app.utils.helpers import fetch_with_playlist_id, ChannelData
from app.lib.timeout import TIMEOUT
from tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt
logging.basicConfig()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the YOUTUBE_API_KEY environment variable.")

@retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        reraise=True
)
async def fetch_channel(channel_id: str, max_results: int) -> ChannelData:
    """
    Get all channel snippets from a YouTube channel using the YouTube Data API v3.
    """    
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
        return await fetch_with_playlist_id(uploads_playlist_id, API_KEY, max_results)