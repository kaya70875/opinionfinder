import redis
import os
from dotenv import load_dotenv
load_dotenv()

host = os.getenv('REDIS_HOST')
password = os.getenv('REDIS_PASSWORD')

r = redis.Redis(
    host=host,
    port=15382,
    decode_responses=True,
    username="default",
    password=password,
)