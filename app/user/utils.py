from app.lib.database import db
from bson import ObjectId

def get_user_plan(user_id: str) -> str:
    """
    Retrieve user plan (free, premium, premium_plus) from the users collection.
    """

    try:
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        if user:
            return user.get("plan", "free")
        else:
            raise ValueError(f"User with ID {user_id} not found.")
    except Exception as e:
        print(f"Error fetching user plan: {e}")
        return "free"