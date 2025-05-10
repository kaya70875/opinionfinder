from app.types.youtube import FetchAndMetaResponse, Snippet
from app.utils.writes import write_as_json
import json

def test_write_as_json():
    metadata = ['title', 'description']

    test_response = FetchAndMetaResponse(
        video_id="testid123",
        transcript=[
            {
                "start": 0,
                "duration": 0,
                "text": "testing text"
            },
            {
                "start": 1,
                "duration": 1.5,
                "text" : "second text"
            }
        ],
        snippet=Snippet(
            title="Test",
            description="desc",
            publishedAt="datetime",
            channelId="123"
            )
    )

    expected_file_structure = [
    {
        "video_id": "testid123",
        "title": "Test",
        "description": "desc",
        "transcript": [
        {
            "start": 0,
            "duration": 0,
            "text": "testing text"
        },
        {
            "start": 1,
            "duration": 1.5,
            "text": "second text"
        }
        ]
    }
    ]

    output = write_as_json([test_response], metadata)
    lines = json.loads(output.read())
    assert lines == expected_file_structure

def test_write_as_json_with_different_metadata():
    metadata = ['title']

    test_response = FetchAndMetaResponse(
        video_id="testid123",
        transcript=[
            {
                "start": 0,
                "duration": 0,
                "text": "testing text"
            },
            {
                "start": 1,
                "duration": 1.5,
                "text" : "second text"
            }
        ],
        snippet=Snippet(
            title="Test",
            description="desc",
            publishedAt="datetime",
            channelId="123"
            )
    )

    expected_file_structure = [
    {
        "video_id": "testid123",
        "title": "Test",
        "transcript": [
        {
            "start": 0,
            "duration": 0,
            "text": "testing text"
        },
        {
            "start": 1,
            "duration": 1.5,
            "text": "second text"
        }
        ]
    }
    ]

    output = write_as_json([test_response], metadata)
    lines = json.loads(output.read())
    assert lines == expected_file_structure

