# app/arq_worker.py
import logging
from app.fetch import fetch_all_transcripts_with_metadata
from app.youtube_v3.v3_requests import fetch_channel
from app.user.utils import get_user_plan
from app.user.user_limits import USER_LIMITS
from app.user.limits import check_request_limits, update_user_limits
from app.utils.data_processing import clean_transcripts, calculate_estimated_token

logger = logging.getLogger(__name__)

async def fetch_transcripts_task(ctx:str, channel_name: str, max_results: int, user_id: str):
    try:
        user_plan = await get_user_plan(user_id)
        user_plan = user_plan.lower().replace(' ', '_')
        user_limits = USER_LIMITS.get(user_plan, USER_LIMITS['free'])
        max_allowed = int(user_limits['max_videos'])

        if max_results is None:
            max_results = max_allowed
        if max_results > max_allowed:
            logger.error("Limit exceeds user plan")
            return {"error": f"Max {max_allowed} videos allowed for {user_plan} plan."}

        await check_request_limits(user_id, user_limits=user_limits)

        channel = await fetch_channel(channel_name, max_results)
        if not channel or not channel.video_ids:
            return {"error": "No videos found"}

        video_ids = channel.video_ids
        snippets = channel.metadata

        channel_data = await fetch_all_transcripts_with_metadata(video_ids, snippets)
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
    keep_result = 86400
