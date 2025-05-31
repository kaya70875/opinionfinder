from fastapi.security import HTTPBearer
from fastapi import Depends
from typing import Annotated
from app.utils.users import extract_id_from_email

security = HTTPBearer(
    description='Enter your JWT token from next auth.'
)

async def get_user_id(credentials: Annotated[str, Depends(security)]):

    token = credentials.credentials
    return await extract_id_from_email(token)