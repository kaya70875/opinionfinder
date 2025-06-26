from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.user.extract_jwt_token import get_user_id
from arq.connections import RedisSettings
from app.lib.rd import r
from app.utils.jobs import *
from pydantic import BaseModel
from typing import List, Annotated
from app.types.youtube import FetchAndMetaResponse
from arq.jobs import Job
from arq import create_pool
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class Jobs(BaseModel):
    job_id: str
    channel_name: str
    total_fetched: int
    export_type: str
    allowed_metadata: str
    include_timing: str
    results: List[FetchAndMetaResponse]

class JobResults(BaseModel):
    data: List[FetchAndMetaResponse]

router = APIRouter()

@router.get("/jobs", response_model=List[Jobs], response_description="Get all jobs for a specific user.")
async def get_jobs(user_id: Annotated[str, Depends(get_user_id)]):
    try:
        results = get_user_jobs_from_redis(user_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

@router.get("/jobs-in-queue")
async def get_queued_jobs(user_id: Annotated[str, Depends(get_user_id)]):
    try:
        all_members = r.smembers(f"user:{user_id}:in-queue")
        queue_list = []

        # Return empty array no members found. 
        if not all_members:
            return []
        
        for member in all_members:
            data = json.loads(member)
            queue_list.append(data)
        return queue_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

@router.get("/stream/job-progress/{progress_id}/{user_id}")
async def get_job_progress(user_id: str, progress_id: str):
    async def event_generator():
        last_progress = -1
        while True:
            await asyncio.sleep(0.5)
            progress_key = r.get(f"progress:{progress_id}:percentage") or 0
            progress = int(progress_key or 0)
            if progress != last_progress:
                yield f"data: {progress}\n\n"
                last_progress = progress
            if progress >= 100:
                # Remove all progress keys and informations after it completes
                remove_progress_info(progress_id, user_id)
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/job/save/{job_id}")
async def save_job(user_id: Annotated[str, Depends(get_user_id)], job_id: str):
    try:
        redis = await create_pool(RedisSettings())
        job = Job(job_id=job_id, redis=redis)
        
        # Get necessarry fields from redis
        queries = r.hgetall(f'query:{job_id}')

        if not queries:
            logger.error('Missing queries in save_job.')
            return False

        # Get job results
        job_results = await job.result()
        results: list[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(result) for result in job_results.get("data")]

        if not results:
            logger.error('No results for saving job informations.')
            return False

        # Save job informations to database 
        save_job_to_redis(user_id, job.job_id, queries, results)

        return True
    except Exception as e:
        logger.error(f'Error while saving job informations to redis: ', e)

@router.get("/job/{job_id}", response_model=JobResults)
async def get_job_status(job_id: str):
    # Get job results from redis
    transcript_data = get_job_from_redis(job_id).get("results")

    return {"data" : transcript_data}