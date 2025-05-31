import httpx
from app.types.youtube import ChannelData
import logging
from app.lib.timeout import TIMEOUT
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
import time
from fastapi import HTTPException

logger = logging.getLogger(__name__)
logging.basicConfig()
@retry(
        retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout)),
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        reraise=True
)
async def get_channel_id(channel_name: str, api_key: str) -> str:
    #print(f"🌐 Preparing request for @{channel_name}")
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print(f"📤 Sending request...")
        response = await client.get(
            'https://www.googleapis.com/youtube/v3/channels',
            params={
                'part': 'id',
                'forHandle': f'@{channel_name}',
                'key': api_key
            }
        )
        response.raise_for_status()
        res = response.json()

        if 'items' in res and res['items']:
            end = time.perf_counter()
            print(f"Took {end - start:.2f} seconds to get channel id")
            return res['items'][0]['id']
        else:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found.")

async def fetch_with_playlist_id(uploads_playlist_id, api_key: str, max_results: int) -> ChannelData:
    try:
        start = time.perf_counter()
        data = {
            'video_ids' : [],
            'metadata' : []
        }
        base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        next_page_token = None

        while True:
            params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': 50,
                'pageToken': next_page_token,
                'key': api_key
            }

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(base_url, params=params)
                res = response.json()
                for item in res['items']:
                    if len(data['video_ids']) >= max_results: break
                    video_id = item['snippet']['resourceId']['videoId']
                    snippet = item['snippet']

                    data['video_ids'].append(video_id)
                    data['metadata'].append(snippet)

                next_page_token = res.get('nextPageToken')
                if not next_page_token:
                    break
        print('total videos fetched: ',len(data['video_ids']))
        end = time.perf_counter()
        print(f"Took {end - start:.2f} seconds for fetch_with_playlist_id")
        return ChannelData(**data)
    except AttributeError as attr_err:
        logger.error('Error fetching vide IDs:',attr_err)
        print('Error fetching video IDs:', attr_err)
        return []