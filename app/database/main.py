import os

<<<<<<< HEAD
from dotenv import load_dotenv, find_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(find_dotenv(".env"))
=======
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
>>>>>>> bf408307fa526b662852f593cb02d28c002b7da7

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL is not None, "DATABASE_URL is not set. Please set it in your .env file."

DATABASE_NAME = os.getenv("DATABASE_NAME", "messenger")
assert DATABASE_NAME is not None, "DATABASE_NAME is not set. Please set it in your .env file."


class DatabaseConnection:
    client: AsyncIOMotorClient


db = DatabaseConnection()


def get_database() -> AsyncIOMotorClient:
    return db.client[DATABASE_NAME]
