from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
import json

ytt_api = YouTubeTranscriptApi()

def fetch_transcript(video_ids: list[str]):
    """
    Fetches the transcript for a given YouTube video ID.
    """
    for video_id in video_ids:
        try:
            transcript = ytt_api.fetch(video_id)
            with open('transcripts.json', 'w') as file:
                for snippets in transcript:
                    file.write(f"{snippets.text}\n")
            print(f"Transcript for {video_id} saved successfully.")
            
        except NoTranscriptFound:
            print(f"No transcript found for video ID: {video_id}")
        except VideoUnavailable:
            print(f"Video unavailable for video ID: {video_id}")
        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video ID: {video_id}")


with open('./rick_beato_videos.json', 'r') as file:
    data = list(json.load(file))
    fetch_transcript(data)