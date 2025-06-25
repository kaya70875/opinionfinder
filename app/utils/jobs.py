from app.lib.database import db
from app.types.youtube import FetchAndMetaResponse
from typing import List
from app.lib.rd import r
from fastapi import HTTPException
import json

collection = db.get_collection("jobs")

REDIS_EXPIRY = 60 * 60 * 2

def save_job_to_redis(user_id: str, job_id: str, queries: dict, results: List[FetchAndMetaResponse]):
    """
    Saves job informations to redis and expires after 24h.
    """

    if not job_id:
        raise HTTPException(status_code=400, detail='Job id is missing for saving job to redis.')

    converted = json.dumps([result.model_dump() for result in results])

    r.hset(f"job:{job_id}", mapping={
        "job_id": job_id,
        "channel_name": queries['channel_name'],
        "total_fetched": queries['max_results'],
        "export_type": queries['export_type'],
        "allowed_metadata": queries['allowed_metadata'],
        "include_timing": queries['include_timing'],
        "results": converted
    })

    # Set job TTL
    r.expire(f"job:{job_id}", REDIS_EXPIRY)

    # Track the job under the user key using a Redis set
    r.sadd(f"user:{user_id}:jobs", job_id)
    r.expire(f"user:{user_id}:jobs", REDIS_EXPIRY)

def get_job_from_redis(job_id: str) -> dict:
    data = r.hgetall(f"job:{job_id}")
    if not data:
        return None

    return {
        "job_id": data["job_id"],
        "channel_name": data["channel_name"],
        "total_fetched": data["total_fetched"],
        "export_type": data["export_type"],
        "allowed_metadata": data["allowed_metadata"],
        "include_timing": data["include_timing"],
        "results": json.loads(data["results"])
    }

def get_user_jobs_from_redis(user_id:str) -> list:
    job_ids = r.smembers(f"user:{user_id}:jobs")
    print('job ids', job_ids)
    jobs = []

    for job_id in job_ids:
        job = get_job_from_redis(job_id)
        if job:
            jobs.append(job)
    
    return jobs