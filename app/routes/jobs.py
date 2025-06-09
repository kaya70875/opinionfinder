from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from app.user.extract_jwt_token import get_user_id
from arq.connections import RedisSettings
from app.lib.rd import r
from app.utils.jobs import save_job_to_redis, get_job_from_redis, get_user_jobs_from_redis
from pydantic import BaseModel
from typing import List, Annotated
from app.types.youtube import FetchAndMetaResponse
from arq.jobs import JobStatus
from arq.jobs import Job
from arq.jobs import JobStatus
from arq import create_pool
import json

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

@router.get("/job/{job_id}", response_model=JobResults, response_description="Get job results from job_id")
async def get_job(job_id: str):
    try:
        if not job_id:
            raise HTTPException(status_code=403, detail='Job id is required.')
        
        job = get_job_from_redis(job_id)
        data = job['results']

        if not data:
            raise HTTPException(status_code=404, detail='Not found any results or document for current job.')
        
        # Validate the data.
        results: List[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(item) for item in data]
        return {"data" : results}
    except Exception as e:
        print('Error while getting job results from db', e)

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str, user_id: Annotated[str, Depends(get_user_id)]):
    redis = await create_pool(RedisSettings())
    job = Job(job_id=job_id, redis=redis)

    status = await job.status()
    
    match status:
        case JobStatus.in_progress:
            return {"status": "in_progress"}
        case JobStatus.queued:
            return {"status": "queued"}
        case JobStatus.not_found:
            return {"status": "not_found"}
        case JobStatus.complete:
            # Get necessarry fields from redis
            channel_name = r.get('channel_name')
            max_results = int(r.get('max_results'))

            # Get job results
            job_results = await job.result()
            results: list[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(result) for result in job_results.get("data")]

            # Save job informations to database 
            save_job_to_redis(user_id, job.job_id, channel_name, max_results, results)

            return {"status" : "done"}


    return {"status": "unknown"}
