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

def check_request_limits(user_id: str, user_limits: dict[str, int]):
    """
    Checks request limits for a specific user based on current plan.
    """

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

        if updated_metrics[channel] >= user_limits['max_channels'] or updated_metrics[video] >= user_limits['max_videos']:
            raise HTTPException(status_code=402, detail=f'Request limit exceed. Payment Required.')

    except WriteError as write_err:
        logger.error(f'Error while writing the database {write_err}')
        raise WriteError(f'Error while writing the database {write_err}')
    except ValueError as v_err:
        logger.error(f'Error while getting current plan or request type {v_err}')
        raise HTTPException(status_code=400, detail=f'Error while getting current plan or request type {v_err}')
    except AttributeError as attr_err:
        logger.error(f'Error while accessing attr in reqeust limit ${attr_err}')
        raise HTTPException(status_code=400, detail=f'Error while accessing attr in request limit ${attr_err}')
    
def update_user_limits(user_id: str, transcripts):
    """
    Updates user limit based on fetched transcripts end of the script.
    """

    #Calculate total videos that fetched end of the script
    total_videos = len(list(transcripts))

    # Update the metrics for the user
    metrics_collection.update_one({'_id' : ObjectId(user_id) }, {"$inc" : {channel : 1, video: total_videos}})
        
