from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

ytt_api = YouTubeTranscriptApi()
write_lock = Lock()

all_transcripts = {}

def fetch_single_transcript(video_id: str):
    try:
        print(f"Fetching transcript for {video_id}...")
        transcript = ytt_api.fetch(video_id).to_raw_data()
        with write_lock:
            all_transcripts[video_id] = transcript
            
        print(f"✅ Transcript for {video_id} saved.")
                
    except NoTranscriptFound:
        print(f"❌ No transcript for {video_id}")
    except VideoUnavailable:
        print(f"❌ Video unavailable: {video_id}")
    except TranscriptsDisabled:
        print(f"❌ Transcripts disabled: {video_id}")
    except Exception as e:
        print(f"⚠️ Error for {video_id}: {e}")

async def fetch_all_transcripts(video_ids: list[str], max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_single_transcript, vid) for vid in video_ids]
        for _ in as_completed(futures):
            pass
        
    return all_transcripts
