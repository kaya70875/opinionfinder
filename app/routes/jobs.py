from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.user.extract_jwt_token import get_user_id
from arq.connections import RedisSettings
from app.lib.rd import r
from app.utils.jobs import get_user_jobs_from_redis, save_job_to_redis
from pydantic import BaseModel
from typing import List, Annotated
from app.types.youtube import FetchAndMetaResponse
from arq.jobs import Job
from arq import create_pool
import json
import asyncio

class Jobs(BaseModel):
    job_id: str
    channel_name: str
    total_fetched: int
    results: List[FetchAndMetaResponse]

class JobResults(BaseModel):
    data: List[FetchAndMetaResponse]

router = APIRouter()

@router.get("/jobs/{user_id}", response_model=List[Jobs], response_description="Get all jobs for a specific user.")
async def get_jobs(user_id: str):
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='User id is required.')

        results = get_user_jobs_from_redis(user_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

@router.get("/stream/job-progress/{progress_id}")
async def get_job_progress(progress_id: str):
    async def event_generator():
        last_progress = -1
        while True:
            await asyncio.sleep(0.5)
            progress = int(r.get(f"progress:{progress_id}:percentage") or 0)
            if progress != last_progress:
                yield f"data: {progress}\n\n"
                last_progress = progress
            if progress >= 100:
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/job/{job_id}")
async def get_job_status(job_id: str, user_id: Annotated[str, Depends(get_user_id)]):
    redis = await create_pool(RedisSettings())
    job = Job(job_id=job_id, redis=redis)

    # Get necessarry fields from redis
    queries = r.hgetall(f'query:{job_id}')

    # Get job results
    job_results = await job.result()
    results: list[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(result) for result in job_results.get("data")]

    # Save job informations to database 
    save_job_to_redis(user_id, job.job_id, queries['channel_name'], queries['max_results'], results)

    return {"data" : results}
