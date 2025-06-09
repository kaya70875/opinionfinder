from app.types.youtube import FetchAndMetaResponse
import re
import gzip
import json

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

def calculate_estimated_token(channel_data: list[FetchAndMetaResponse]) -> int:
    """
    Calculates total token count estimation for AI and ML actions.
    """

    total = 0

    for data in channel_data:
        transcripts = data.transcript
        snippet = data.snippet

        for entry in transcripts:
            total += len(entry['text'])
        
        total += len(snippet.description)
        total += len(snippet.title)
        total += len(snippet.publishedAt)
    
    return total

def decompress_job(doc) -> list:
    """
    Decompress gzip and return list of JSON data.
    @Parameters:
        doc: MongoDB document
    """
    results_compressed: bytes = doc['results']
    decompressed = gzip.decompress(results_compressed)
    data = json.loads(decompressed.decode())

    return data
