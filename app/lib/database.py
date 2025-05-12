from pymongo import errors
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Retrieve environment variables
mongo_uri = os.getenv('DATABASE_URI')
mongo_db = os.getenv('MONGO_DB')

# Check if environment variables are set
if not mongo_uri or not mongo_db:
    raise ValueError("Environment variables DATABASE_URI or MONGO_DB are not set.")

try:
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]  # Access the database

    print("Database connection successful")
except errors.ConnectionFailure as exc:
    logger.error(f'Database connection failed. {exc}')

