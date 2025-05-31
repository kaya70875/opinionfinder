import httpx
import logging
from fastapi import HTTPException
from app.lib.database import db
from json import JSONDecodeError

logger = logging.getLogger(__name__)

async def extract_id_from_email(token: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=45.0
            )
            

        if res.status_code != 200:
            logger.error(f"Error fetching user info: {res.status_code} - {res.text}")
            raise HTTPException(status_code=res.status_code, detail="Failed to fetch user info")

        response = res.json()
        email = response['email']
        
        currentUser = await db['users'].find_one({'email': email})

        if not currentUser:
            raise HTTPException(status_code=404, detail="User not found in DB")
        user_id = currentUser.get('_id')

        return user_id
    except httpx.HTTPStatusError as http_err:
        logger.error(f'HTTP error: {http_err}')
        raise HTTPException(status_code=http_err.response.status_code, detail=str(http_err))
    except JSONDecodeError as json_err:
        logger.error(f'Invalid json structure from request object: {json_err}')
        raise HTTPException(status_code=400, detail=f'Invalid json structure from request object: {json_err}')
    except ValueError as v_err:
        logger.error(f'Value error: {v_err}')
        raise HTTPException(status_code=400, detail=f'Value error: {v_err}')