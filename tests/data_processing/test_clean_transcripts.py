from app.types.youtube import FetchAndMetaResponse, Snippet
from app.utils.data_processing import clean_transcripts

def test_clean_transcripts():

    test_response = FetchAndMetaResponse(
        video_id="testid123",
        transcript=[
            {
                "start": 0,
                "duration": 0,
                "text": "[Music]"
            }
        ],
        snippet=Snippet(
            title="Test",
            description="desc",
            publishedAt="datetime",
            channelId="123"
            )
    )

    cleaned_response = clean_transcripts([test_response])

    assert cleaned_response[0].transcript[0]['text'] == ''

def test_clean_transcripts_with_multiple_text():
    test_response = FetchAndMetaResponse(
        video_id="testid123",
        transcript=[
            {
                "start": 0,
                "duration": 0,
                "text": "[Music][Applause] and that happened!"
            }
        ],
        snippet=Snippet(
            title="Test",
            description="desc",
            publishedAt="datetime",
            channelId="123"
        )
    )

    cleaned_response = clean_transcripts([test_response])
    
    assert cleaned_response[0].transcript[0]['text'] == 'and that happened!'
