from app.lib.database import db
from bson import ObjectId
from app.lib.rd import r

async def get_user_plan(user_id: str) -> str:
    """
    Retrieve user plan (free, premium, premium_plus) from the users collection.
    """

    try:
        user_plan_key = f"user:{user_id}:plan"
        cached_plan = r.get(user_plan_key)
        # First try to get user plan from cache.
        if cached_plan is not None:
            return cached_plan

        user = await db['users'].find_one({"_id": ObjectId(user_id)})
        user_plan = user.get("plan", "free")
        if user:
            r.set(user_plan_key, user_plan, 60 * 60 * 2)
            return user_plan
        else:
            raise ValueError(f"User with ID {user_id} not found.")
    except Exception as e:
        print(f"Error fetching user plan: {e}")
        return "free"