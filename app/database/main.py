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
    Database Connection Model.
    """

    client: AsyncIOMotorClient = None


db = DatabaseConnection()
test_db = DatabaseConnection()


def get_database() -> AsyncIOMotorClient:
    """
    Get the Database Connection.

    :return: Database Connection.
    """

    if db.client is None:
        db.client = AsyncIOMotorClient(DATABASE_URL)

    return db.client[DATABASE_NAME]


def get_test_database() -> AsyncIOMotorClient:
    """
    Get the Test Database Connection.

    :return: Test Database Connection.
    """

    if test_db.client is None:
        test_db.client = AsyncIOMotorClient(DATABASE_URL)

    return test_db.client["test_" + DATABASE_NAME]
