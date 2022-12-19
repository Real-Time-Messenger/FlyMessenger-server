import os

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(find_dotenv("config/.env", raise_error_if_not_found=True))

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL is not None, "DATABASE_URL is not set. Please set it in your .env file."

DATABASE_NAME = os.getenv("DATABASE_NAME")
assert DATABASE_NAME is not None, "DATABASE_NAME is not set. Please set it in your .env file."

class DatabaseConnection:
    client: AsyncIOMotorClient = None


db = DatabaseConnection()


async def get_database() -> AsyncIOMotorClient:
    return db.client[DATABASE_NAME]
