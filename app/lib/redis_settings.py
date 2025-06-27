from arq.connections import RedisSettings
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

REDIS_CONF = RedisSettings(
    host=REDIS_HOST,
    port=15382,
    password=REDIS_PASSWORD,
    username="default",
    conn_timeout=60
)
