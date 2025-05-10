from app.utils.writes import write_as_text
from app.types.youtube import FetchAndMetaResponse, Snippet

def test_write_as_text():

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

    expected_file_structure = ['Transcript for testid123:\n', 'title --> Test \n', 'description --> desc \n', '0 --> 0\n', 'testing text\n', '1 --> 2.5\n', 'second text\n', '\n']

    output = write_as_text([test_response], metadata)
    lines = output.readlines()

    assert lines == expected_file_structure

def test_write_as_text_with_different_metadata():
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

    expected_file_structure = ['Transcript for testid123:\n', 'title --> Test \n', '0 --> 0\n', 'testing text\n', '1 --> 2.5\n', 'second text\n', '\n']

    output = write_as_text([test_response], metadata)
    lines = output.readlines()

    assert lines == expected_file_structure