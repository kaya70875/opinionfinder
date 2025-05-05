import requests

API_KEY = 'AIzaSyD-5wZEH3NK86gcxW-MJLfZLsqwRk-7bLw'

def get_channel_id(channel_name: str) -> str:
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
            'key': API_KEY
        }
    )

    res = res.json()
    if 'items' in res and len(res['items']) > 0:
        return res['items'][0]['id']['channelId']
    else:
        raise ValueError(f"Channel '{channel_name}' not found.")


def get_all_video_ids(uploads_playlist_id, api_key):
    video_ids = []
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

        res = requests.get(base_url, params=params).json()
        for item in res['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)

        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids


url = 'https://www.googleapis.com/youtube/v3/channels'
params = {
    'part': 'contentDetails',
    'id': get_channel_id('RickBeato'),
    'key': API_KEY
}

res = requests.get(url, params=params).json()
uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

video_ids = get_all_video_ids(uploads_playlist_id, API_KEY)
print(f"Found {len(video_ids)} videos.")

import json
with open("rick_beato_videos.json", "w") as f:
    json.dump(video_ids, f, indent=2)


