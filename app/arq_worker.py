# app/arq_worker.py
import logging
from app.fetch import fetch_all_transcripts_with_metadata
from app.youtube_v3.v3_requests import fetch_channel
from app.user.user_limits import USER_LIMITS
from app.user.limits import update_user_limits
from app.utils.data_processing import clean_transcripts, calculate_estimated_token

logger = logging.getLogger(__name__)

async def fetch_transcripts_task(ctx:str, progress_id: str, channel_id: str, max_results: int, user_id: str):
    try:
        channel = await fetch_channel(channel_id, max_results)
        if not channel or not channel.video_ids:
            return {"error": "No videos found"}

        video_ids = channel.video_ids
        snippets = channel.metadata

        channel_data = await fetch_all_transcripts_with_metadata(video_ids, snippets, progress_id)
        await update_user_limits(user_id, (data.transcript for data in channel_data))

        cleaned_data = clean_transcripts(channel_data)
        estimated_token = calculate_estimated_token(cleaned_data)

        return {
            "data": cleaned_data,
            "token": estimated_token
        }

    except Exception as e:
        print('error',e)


class WorkerSettings:
    functions = [fetch_transcripts_task]
    keep_result = 3000
