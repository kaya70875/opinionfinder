from app.lib.database import db
from app.types.youtube import FetchAndMetaResponse
from typing import List
from bson import ObjectId
import gzip
import json

collection = db.get_collection("jobs")

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

async def remove_job(job_id: str):
    pass