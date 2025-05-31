from fastapi import APIRouter, Depends
from fastapi import Query, Path, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.utils.writes import write_as_csv, write_as_text, write_as_json
from app.fetch import fetch_all_transcripts_with_metadata
from app.youtube_v3.v3_requests import fetch_channel
from app.user.limits import check_request_limits, update_user_limits
from app.user.utils import get_user_plan
from app.user.user_limits import USER_LIMITS
from app.utils.data_processing import clean_transcripts, calculate_estimated_token
from app.user.extract_jwt_token import get_user_id
import asyncio
import logging
from typing import Annotated
from arq import create_pool
from arq.connections import RedisSettings
import io
from app.lib.rd import r
import json
from app.types.youtube import FetchAndMetaResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/transcripts/download")
async def download():
    
    export_type = str(r.get("export_type"))
    allowed_metadata_list = json.loads(r.get("allowed_metadata_list"))
    include_timing = bool(r.get("include_timing"))
    cached_cleaned_data = json.loads(r.get("transcripts"))

    cleaned_data: list[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate_json(item) for item in cached_cleaned_data]

    loop = asyncio.get_running_loop()

    if export_type == "txt":
        output = await loop.run_in_executor(
            None, write_as_text, cleaned_data, allowed_metadata_list, include_timing
        )
        return StreamingResponse(output, media_type="text/txt", headers={
            "Content-Disposition": "attachment; filename=transcripts.txt",
        })

    elif export_type == 'csv':
        output = await loop.run_in_executor(
            None, write_as_csv, cleaned_data, allowed_metadata_list, include_timing
        )
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=transcripts.csv",
        })

    elif export_type == 'json':
        output = await loop.run_in_executor(
            None, write_as_json, cleaned_data, allowed_metadata_list, include_timing
        )
        return StreamingResponse(output, media_type="application/json", headers={
            "Content-Disposition": "attachment; filename=transcripts.json",
        })

@router.get("/transcripts/{channel_name}")
async def fetch_transcripts(
        user_id: Annotated[str, Depends(get_user_id)],
        channel_name : str = Path(description="Channel name to fetch transcripts from.", min_length=1, max_length=70),
        export_type: str = Query(default="json", description="Export type for transcripts. Options: 'json', 'txt', 'csv'"),
        max_results: int = Query(default=None, description="Limit the number of transcripts to fetch."),
        allowed_metadata: str = Query(default='title', description="Allowed metadata values. Options : 'title | description | publishedAt'"),
        include_timing: bool = Query(default=True, description="Whether the include start and duration parameters or not.")
        ):
    """
    Fetch transcripts for all videos from a channel.
    """
    if export_type not in ["json", "txt", "csv"]:
        raise HTTPException(status_code=400, detail="Invalid export type. Options: 'json', 'txt', 'csv'")
    
    # Set maximum allowed videos to fetch as default.
    user_plan = await get_user_plan(user_id)
    user_plan = user_plan.lower().replace(' ', '_')
    user_limits = USER_LIMITS.get(user_plan, USER_LIMITS['free'])
    max_allowed = int(user_limits['max_videos'])
    if max_results is None:
        max_results = max_allowed
    if max_results > max_allowed:
        logger.error(f"Limit exceeds plan allowance ({max_allowed} max for {user_plan} users).")
        raise HTTPException(status_code=403, detail=f"Limit exceeds plan allowance ({max_allowed} max for {user_plan} users).")

    # Check request limits for the user
    await check_request_limits(user_id, user_limits=user_limits)
    
    channel = await fetch_channel(channel_name, max_results)
    video_ids = channel.video_ids if channel else []
    snippets = channel.metadata if channel else []
    if not video_ids:
        logger.error("No video IDs found for the specified channel.")
        raise HTTPException(status_code=404, detail="No video IDs found for the specified channel.")

    # Call the fetch function from fetch.py
    channel_data = await fetch_all_transcripts_with_metadata(video_ids, snippets)
    #channel_data = await fetch_all_transcripts_with_metadata(video_ids, snippets)
    if not channel_data:
        logger.error("No channel_data found for the current channel")
        #raise HTTPException(status_code=404, detail="No channel_data found for the current channel")

    #Update user metrics
    await update_user_limits(user_id, (data.transcript for data in channel_data))

    # Convert metadata to a list
    allowed_metadata_list = allowed_metadata.split(',')

    #Clean transcripts for final writing format.
    cleaned_data = clean_transcripts(channel_data)

    #Calculate estimated token
    estimated_token = calculate_estimated_token(cleaned_data)

    r.set("transcripts", json.dumps([data.model_dump_json() for data in cleaned_data]))
    r.set("export_type", export_type)
    r.set("allowed_metadata_list", json.dumps(allowed_metadata_list))
    r.set("include_timing", str(include_timing))

    return {
        "data" : cleaned_data,
        "token": estimated_token
    }
    

@router.get("/transcripts/background/{channel_name}")
async def start_background_fetching_job(
    channel_name: str,
    export_type: str = Query("json"),
    max_results: int = Query(None),
    allowed_metadata: str = Query("title"),
    include_timing: bool = Query(True)
):
    user_id = "681b72683e6372ca59e05893"
    redis = await create_pool(RedisSettings())

    job = await redis.enqueue_job(
        "fetch_transcripts_task",
        channel_name,
        export_type,
        max_results,
        allowed_metadata.split(","),
        include_timing,
        user_id
    )

    result = await job.result()  # or poll periodically

    if "error" in result:
        return JSONResponse(status_code=400, content={"detail": result["error"]})

    return StreamingResponse(io.BytesIO(result["data"].encode()), media_type=result["type"], headers={
        "Content-Disposition": f"attachment; filename=transcripts.{export_type}",
        "X-Estimated-Tokens": str(result["tokens"])
    })