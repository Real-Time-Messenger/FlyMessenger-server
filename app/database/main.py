import os

from dotenv import load_dotenv, find_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(find_dotenv(".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL is not None, "DATABASE_URL is not set. Please set it in your .env file."

DATABASE_NAME = os.getenv("DATABASE_NAME", "messenger")
assert DATABASE_NAME is not None, "DATABASE_NAME is not set. Please set it in your .env file."


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

    return db.client[DATABASE_NAME]
