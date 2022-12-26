import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL is not None

DATABASE_NAME = os.getenv("DATABASE_NAME")
assert DATABASE_NAME is not None

class DatabaseConnection:
    """
    Database connection model.

    Need only at the connection to the database.
    """

    client: AsyncIOMotorClient = None


db = DatabaseConnection()


def get_database() -> AsyncIOMotorClient:
    """
    Get the database connection.

    :return: Database connection
    """

    if db.client is None:
        db.client = AsyncIOMotorClient(DATABASE_URL)

    return db.client[DATABASE_NAME]
