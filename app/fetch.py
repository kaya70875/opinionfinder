from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from app.types.youtube import Snippet
from app.types.youtube import FetchAndMetaResponse

ytt_api = YouTubeTranscriptApi()
write_lock = Lock()

def fetch_transcript_with_snippet(video_id: str, snippet: Snippet) -> dict | None:
    try:
        print(f"Fetching transcript for {video_id}...")
        transcript = ytt_api.fetch(video_id).to_raw_data()
        print(f"✅ Transcript for {video_id} saved.")
        return {
            "video_id": video_id,
            "transcript": transcript,
            "snippet": {
                "title": snippet.title,
                "description": snippet.description,
                "publishedAt": snippet.publishedAt,
                "channelId": snippet.channelId
            }
        }
    except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled) as e:
        print(f"❌ Error for {video_id}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error for {video_id}: {e}")
        return None

async def fetch_all_transcripts_with_metadata(video_ids: list[str], snippets: list[Snippet], max_workers=10) -> list[FetchAndMetaResponse]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_transcript_with_snippet, vid, snip) for vid, snip in zip(video_ids, snippets)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(FetchAndMetaResponse(
                    video_id=result["video_id"],
                    transcript=result["transcript"],
                    snippet=Snippet(**result["snippet"])
                ))
    return results

