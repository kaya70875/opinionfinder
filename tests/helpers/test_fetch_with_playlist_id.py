from app.utils.helpers import fetch_with_playlist_id
from app.types.youtube import ChannelData, Snippet
import responses

@responses.activate
def test_fetch_with_playlist_id_multiple_pages():
    first_page = {
        "items": [
            {
                "snippet": {
                    "resourceId": {
                        "videoId": "video123"
                    },
                    "title": "Test Video 1",
                    "description": "Desc 1",
                    "publishedAt": "2021-01-01T00:00:00Z",
                    "channelId": "channel123"
                }
            }
        ],
        "nextPageToken": "PAGE2"
    }

    second_page = {
        "items": [
            {
                "snippet": {
                    "resourceId": {
                        "videoId": "video456"
                    },
                    "title": "Test Video 2",
                    "description": "Desc 2",
                    "publishedAt": "2021-01-02T00:00:00Z",
                    "channelId": "channel456"
                }
            }
        ]
        # no nextPageToken means it's the last page
    }

    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'

    # Add two mock responses to simulate pagination
    responses.add(responses.GET, base_url, json=first_page, status=200)
    responses.add(responses.GET, base_url, json=second_page, status=200)

    res = fetch_with_playlist_id(
        uploads_playlist_id="fake_playlist_id",
        api_key="fake_api_key",
        max_results=2
    )

    # Assertions
    assert isinstance(res, ChannelData)
    assert len(res.video_ids) == 2
    assert res.video_ids == ["video123", "video456"]
    assert isinstance(res.metadata[0], Snippet)
    assert res.metadata[0].title == "Test Video 1"
    assert res.metadata[1].title == "Test Video 2"
