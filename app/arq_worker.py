# app/arq_worker.py
import logging
from arq import cron
from app.fetch import fetch_all_transcripts_with_metadata
from app.youtube_v3.v3_requests import fetch_channel
from app.user.utils import get_user_plan
from app.user.user_limits import USER_LIMITS
from app.user.limits import check_request_limits, update_user_limits
from app.utils.data_processing import clean_transcripts, calculate_estimated_token
from app.utils.writes import write_as_csv, write_as_text, write_as_json
import asyncio
import io

logger = logging.getLogger(__name__)

async def fetch_transcripts_task(ctx, channel_name: str, export_type: str, max_results: int, allowed_metadata: list[str], include_timing: bool, user_id: str):
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

        allowed_metadata_list = allowed_metadata
        cleaned_data = clean_transcripts(channel_data)
        estimated_token = calculate_estimated_token(cleaned_data)

        loop = asyncio.get_running_loop()

        if export_type == 'txt':
            output = await loop.run_in_executor(None, write_as_text, cleaned_data, allowed_metadata_list, include_timing)
            content = output.getvalue()
            return {"data": content, "type": "text/plain", "tokens": estimated_token}

        elif export_type == 'csv':
            output = await loop.run_in_executor(None, write_as_csv, cleaned_data, allowed_metadata_list, include_timing)
            content = output.getvalue()
            return {"data": content, "type": "text/csv", "tokens": estimated_token}

        elif export_type == 'json':
            output = await loop.run_in_executor(None, write_as_json, cleaned_data, allowed_metadata_list, include_timing)
            content = output.getvalue()
            return {"data": content, "type": "application/json", "tokens": estimated_token}
    except Exception as e:
        print('error',e)


class WorkerSettings:
    functions = [fetch_transcripts_task]
