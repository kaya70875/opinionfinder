from app.types.youtube import FetchAndMetaResponse
import re

def clean_transcripts(channel_data: list[FetchAndMetaResponse]) -> list[FetchAndMetaResponse]:
    """
    Cleans unnecessary text from transcripts like [Music], [Applause], etc.
    """

    for data in channel_data:
        transcripts = data.transcript
        
        for entry in transcripts:

            # Remove unnecessary text patterns like [Music], [Applause], etc.
            cleaned_text = re.sub(r'\[.*?\]', '', entry['text'])

            # Remove extra whitespace
            cleaned_text = ' '.join(cleaned_text.split())

            # Update the transcript text
            entry['text'] = cleaned_text

    return channel_data
