from app.user.user_limits import USER_LIMITS
from app.user.utils import get_user_plan
from app.lib.database import db
from bson import ObjectId
from datetime import datetime, timedelta
from pymongo.errors import WriteError
from pymongo import ReturnDocument
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

metrics_collection = db['metrics']
channel = 'channels_scraped'
video = 'videos_scraped'

def check_request_limit(user_id: str, videos: int):
    """
    Checks request limits for a specific user based on current plan.
    """

    user_plan = get_user_plan(user_id).lower().replace(" ", "_")
    now = datetime.now()

    try:
        metrics = metrics_collection.find_one({"_id": ObjectId(user_id)})
        if not metrics or metrics.get("reset_time", now) <= now:
            #if no record found or reset time is in the past, create a new record
            updated_metrics = metrics_collection.find_one_and_update(
                {"_id" : ObjectId(user_id)},
                {
                    "$set": {
                        channel: 0,
                        video: 0,
                        "reset_time": now + timedelta(days=1)
                    }
                },
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
        else:
            updated_metrics = metrics
        
        limits = USER_LIMITS.get(user_plan, USER_LIMITS["free"])

        if updated_metrics[channel] >= limits['max_channels'] or updated_metrics[video] >= limits['max_videos']:
            raise HTTPException(status_code=402, detail=f'Request limit exceed. Payment Required.')
        
        # Update the metrics for the user
        metrics_collection.update_one({'_id' : ObjectId(user_id) }, {"$inc" : {channel : 1, video: videos}})

    except WriteError as write_err:
        logger.error(f'Error while writing the database {write_err}')
        raise WriteError(f'Error while writing the database {write_err}')
    except ValueError as v_err:
        logger.error(f'Error while getting current plan or request type {v_err}')
        raise HTTPException(status_code=400, detail=f'Error while getting current plan or request type {v_err}')
    except AttributeError as attr_err:
        logger.error(f'Error while accessing attr in reqeust limit ${attr_err}')
        raise HTTPException(status_code=400, detail=f'Error while accessing attr in request limit ${attr_err}')
        
