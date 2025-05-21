import asyncio
from concurrent.futures import ThreadPoolExecutor
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled, IpBlocked
from tenacity import retry, wait_fixed, retry_if_exception_type, stop_after_attempt
from app.types.youtube import Snippet, FetchAndMetaResponse
import requests
import time

class CustomHTTPClient(requests.Session):
    def __init__(self, timeout=5):
        super().__init__()
        self.timeout = timeout

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return super().get(url, **kwargs)

# Global API and thread pool
executor = ThreadPoolExecutor(max_workers=30)

@retry(
    retry=retry_if_exception_type(IpBlocked),
    wait=wait_fixed(1),
    stop=stop_after_attempt(2)
)
def fetch_transcript_with_snippet(video_id: str, snippet: Snippet) -> dict | None:
    try:
        ytt_api = YouTubeTranscriptApi()        
        transcript = ytt_api.fetch(video_id).to_raw_data()
        print(f"✅ {video_id} done")
        return {
            "video_id": video_id,
            "transcript": transcript,
            "snippet": snippet.model_dump()
        }
    except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled):
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return None


async def fetch_all_transcripts_with_metadata(video_ids: list[str], snippets: list[Snippet]) -> list[FetchAndMetaResponse]:
    start = time.perf_counter()
    async def run_in_thread(vid, snip):
        return await asyncio.to_thread(fetch_transcript_with_snippet, vid, snip)

    tasks = [run_in_thread(vid, snip) for vid, snip in zip(video_ids, snippets)]
    results = await asyncio.gather(*tasks)
    end = time.perf_counter()

    print(f"Took {end-start} seconds to fetch all transcripts.")
    return [
        FetchAndMetaResponse(
            video_id=result["video_id"],
            transcript=result["transcript"],
            snippet=Snippet(**result["snippet"])
        )
        for result in results if result
    ]