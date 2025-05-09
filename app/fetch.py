from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from app.types.youtube import Snippet

ytt_api = YouTubeTranscriptApi()
write_lock = Lock()

all_transcripts = []

def fetch_transcript_with_snippet(video_id: str, snippet: Snippet):
    try:
        print(f"Fetching transcript for {video_id}...")
        transcript = ytt_api.fetch(video_id).to_raw_data()
        with write_lock:
            data = {
                "video_id": video_id,
                "transcript": transcript,
                "snippet": {
                    "title": snippet.title,
                    "description": snippet.description,
                    "publishedAt": snippet.publishedAt 
                }
            }
            
        print(f"✅ Transcript for {video_id} saved.")
        return all_transcripts.append(data)
                
    except NoTranscriptFound:
        print(f"❌ No transcript for {video_id}")
    except VideoUnavailable:
        print(f"❌ Video unavailable: {video_id}")
    except TranscriptsDisabled:
        print(f"❌ Transcripts disabled: {video_id}")
    except Exception as e:
        print(f"⚠️ Error for {video_id}: {e}")

async def fetch_all_transcripts_with_metadata(video_ids: list[str], snippets: list[Snippet], max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_transcript_with_snippet, vid, snippet) for vid, snippet in zip(video_ids, snippets)]
        for _ in as_completed(futures):
            pass

    return all_transcripts
