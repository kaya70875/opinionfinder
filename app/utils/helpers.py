import httpx
from app.types.youtube import ChannelData
import logging
from app.lib.timeout import TIMEOUT

logger = logging.getLogger(__name__)

import httpx
import traceback

async def get_channel_id(channel_name: str, api_key: str) -> str:
    try:
        print(f"🌐 Preparing request for @{channel_name}")
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
            print(f"📥 Response status: {response.status_code}")
            response.raise_for_status()

            print(f"📄 Raw response: {response.text}")
            res = response.json()

            if 'items' in res and res['items']:
                return res['items'][0]['id']
            else:
                raise ValueError(f"Channel '{channel_name}' not found.")
    
    except httpx.ConnectTimeout as e:
        print("❌ Connect timeout:", e)
    except httpx.ReadTimeout as e:
        print("❌ Read timeout:", e)
    except httpx.RequestError as e:
        print("❌ Request error:", e)
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP status error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print("❌ Unexpected error:", e)
        traceback.print_exc()



async def fetch_with_playlist_id(uploads_playlist_id, api_key: str, max_results: int) -> ChannelData:
    try:
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
                    print(f"Fetched video ID: {video_id}")

                next_page_token = res.get('nextPageToken')
                if not next_page_token:
                    break
            print('data', data)
            return ChannelData(**data)
    except AttributeError as attr_err:
        logger.error('Error fetching vide IDs:',attr_err)
        print('Error fetching video IDs:', attr_err)
        return []