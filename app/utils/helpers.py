import requests
from typing import Optional

def get_channel_id(channel_name: str, api_key: str) -> str:
    """
    Get the channel ID from the channel name using YouTube Data API v3.
    """

    res = requests.get(
        'https://www.googleapis.com/youtube/v3/search',
        params={
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
    )

    res = res.json()
    if 'items' in res and len(res['items']) > 0:
        return res['items'][0]['id']['channelId']
    else:
        raise ValueError(f"Channel '{channel_name}' not found.")


def get_video_ids(uploads_playlist_id, api_key: str, limit: Optional[int] = 50) -> list[str]:
    video_ids = []
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    next_page_token = None

    print(f"Fetching video IDs from playlist: {uploads_playlist_id}...")

    while True:
        print(f"Fetching page with token: {next_page_token}...")
        params = {
            'part': 'snippet',
            'playlistId': uploads_playlist_id,
            'maxResults': limit,
            'pageToken': next_page_token,
            'key': api_key
        }

        res = requests.get(base_url, params=params).json()
        for item in res['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)
            print(f"Fetched video ID: {video_id}")

            with open('video_ids.txt', 'a') as f:
                f.write(video_id + '\n')

        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids