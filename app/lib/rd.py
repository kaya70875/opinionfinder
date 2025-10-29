from redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "localhost")

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_PORT = 10918

r = Redis(
    host=REDIS_HOST if ENVIRONMENT == 'prod' else 'localhost',
    port=REDIS_PORT if ENVIRONMENT == 'prod' else 6379,
    password=REDIS_PASSWORD if ENVIRONMENT == 'prod' else None,
    username="default" if ENVIRONMENT == 'prod' else None,
    decode_responses=True
)