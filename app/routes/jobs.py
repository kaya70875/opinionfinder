from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from app.lib.database import db
from app.user.extract_jwt_token import get_user_id
from arq.connections import RedisSettings
from app.lib.rd import r
from app.utils.jobs import save_job
from bson import ObjectId
from pydantic import BaseModel
from app.utils.helpers import serialize_mongo_doc
from typing import List, Annotated
from app.types.youtube import FetchAndMetaResponse
from app.utils.data_processing import decompress_job
from arq.jobs import JobStatus
from arq.jobs import Job
from arq.jobs import JobStatus
from arq import create_pool
import time


class Jobs(BaseModel):
    _id: str
    userId: str
    jobId: str
    channelName: str
    totalFetched: int

class JobResults(BaseModel):
    data: List[FetchAndMetaResponse]

router = APIRouter()

collection = db.get_collection("jobs")

@router.get("/jobs/{user_id}", response_model=List[Jobs], response_description="Get all jobs for a specific user.")
async def get_jobs(user_id: str) -> list:
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='User id is required.')

        cursor = collection.find({"userId": ObjectId(user_id)}, {"results" : 0})
        results = await cursor.to_list(length=None) # Get list of all jobs for current user.

        if not results:
            return []
        
        serialized = [serialize_mongo_doc(doc) for doc in results]
        return serialized
    except Exception as e:
        print('err', e)

@router.get("/job/{job_id}", response_model=JobResults, response_description="Get job results from job_id")
async def get_job(job_id: str):
    try:
        if not job_id:
            raise HTTPException(status_code=403, detail='Job id is required.')

        start = time.perf_counter()
        doc = await collection.find_one({"jobId": job_id}, {"results": 1}) # This will raise an error check what is it.

        # Decompress data
        data = decompress_job(doc)
        end = time.perf_counter()
        print(f'Took {end - start} seconds to get results from db.')

        if not data:
            raise HTTPException(status_code=404, detail='Not found any results or document for current job.')
        
        # Validate the data.
        results: List[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(item) for item in data]
        return {"data" : results}
    except Exception as e:
        print('Error while getting job results from db', e)

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str, user_id: Annotated[str, Depends(get_user_id)]):
    redis = await create_pool(RedisSettings())  # make sure you're using the right pool here
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
            max_results = r.get('max_results')

            # Get job results
            job_results = await job.result(timeout=0)
            results: list[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(result) for result in job_results.get("data")]

            # Save job informations to database 
            await save_job(user_id, channel_name, job.job_id, max_results, results)

            return {"status" : "done"}


    return {"status": "unknown"}
