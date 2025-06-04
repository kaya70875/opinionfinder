from fastapi.routing import APIRouter
from fastapi import HTTPException
from app.lib.database import db
from bson import ObjectId
from pydantic import BaseModel
from app.utils.helpers import serialize_mongo_doc
from typing import List
from app.types.youtube import FetchAndMetaResponse

class Jobs(BaseModel):
    _id: str
    userId: str
    jobId: str
    channelName: str
    totalFetched: int
    results: List[FetchAndMetaResponse]

class JobResults(BaseModel):
    data: List[FetchAndMetaResponse]

router = APIRouter()

collection = db.get_collection("jobs")

@router.get("/jobs/{user_id}", response_model=List[Jobs], response_description="Get all jobs for a specific user.")
async def get_jobs(user_id: str) -> list:
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='User id is required.')

        cursor = collection.find({"userId": ObjectId(user_id)})
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

        job = await collection.find_one({"jobId": job_id}) # This will raise an error check what is it.
        data = job.get("results")
        print('results from job route : ', data)

        if not data:
            raise HTTPException(status_code=404, detail='Not found any results or document for current job.')
        
        # Validate the data.
        results: List[FetchAndMetaResponse] = [FetchAndMetaResponse.model_validate(item) for item in data]
        return {"data" : results}
    except Exception as e:
        print('Error while getting job results from db', e)
