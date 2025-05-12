from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
import asyncio
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

async def fetch_all_transcripts_with_metadata(video_ids: list[str], snippets: list[Snippet]) -> list[FetchAndMetaResponse]:
    async def run_in_thread(vid, snip):
        return await asyncio.to_thread(fetch_transcript_with_snippet, vid, snip)

    tasks = [run_in_thread(vid, snip) for vid, snip in zip(video_ids, snippets)]
    results_raw = await asyncio.gather(*tasks)

    return [
        FetchAndMetaResponse(
            video_id=result["video_id"],
            transcript=result["transcript"],
            snippet=Snippet(**result["snippet"])
        )
        for result in results_raw if result
    ]

