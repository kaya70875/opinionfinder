from app.lib.database import db
from app.types.youtube import FetchAndMetaResponse
from typing import List
from bson import ObjectId
from app.lib.rd import r
from fastapi import HTTPException
import gzip
import json

collection = db.get_collection("jobs")

REDIS_EXPIRY = 60 * 60 * 2

async def save_job(user_id: str, channel_name: str, job_id: str, max_results: int, results: List[FetchAndMetaResponse]):
    """
    Saves job informations to MongoDB database.
    """

    try:
        # Check if there is same records or not.

        # Compress results for reducing json size for optimization.
        compressed = gzip.compress(json.dumps([result.model_dump() for result in results]).encode())

        await collection.insert_one({
            "userId": ObjectId(user_id),
            "jobId": job_id,
            "channelName": channel_name,
            "totalFetched": max_results,
            "results": compressed
        })
    except Exception as e:
        print('Error while inserting job information to db : ', e)

def save_job_to_redis(user_id: str, job_id: str, channel_name: str, max_results: int, results: List[FetchAndMetaResponse]):
    """
    Saves job informations to redis and expires after 24h.
    """

    if not job_id:
        raise HTTPException(status_code=400, detail='Job id is missing for saving job to redis.')

    converted = json.dumps([result.model_dump() for result in results])

    # Save the actual job (compressed)
    r.hset(f"job:{job_id}", mapping={
        "job_id": job_id,
        "channel_name": channel_name,
        "total_fetched": max_results,
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