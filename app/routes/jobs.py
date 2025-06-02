from fastapi.routing import APIRouter
from fastapi import HTTPException
from app.lib.database import db
from bson import ObjectId
from pydantic import BaseModel
from app.utils.helpers import serialize_mongo_doc
from typing import List

class Jobs(BaseModel):
    _id: str
    userId: str
    jobId: str
    channelName: str
    totalFetched: int

router = APIRouter()

collection = db.get_collection("jobs")

@router.get("/jobs/{user_id}", response_model=List[Jobs], response_description="Get all jobs for a specific user.")
async def get_jobs(user_id: str) -> list:
    try:
        if not user_id:
            return HTTPException(status_code=403, detail='User id is required.')

        cursor = collection.find({"userId": ObjectId(user_id)})
        results = await cursor.to_list(length=None) # Get list of all jobs for current user.
        print('res', results)

        if not results:
            return HTTPException(status_code=404, detail='Cannot found any jobs for user.')
        
        serialized = [serialize_mongo_doc(doc) for doc in results]
        return serialized
    except Exception as e:
        print('err', e)
