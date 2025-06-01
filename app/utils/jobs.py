from app.lib.database import db

collection = db.get_collection("jobs")

async def save_job(user_id: str, channel_name: str, job_id: str, max_results: int):
    """
    Saves job informations to MongoDB database.
    """

    # Check if there is same records or not.

    await collection.insert_one({
        "userId": user_id,
        "jobId": job_id,
        "channelName": channel_name,
        "totalFetched": max_results
    })

async def remove_job(job_id: str):
    pass