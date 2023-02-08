from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr

from app.common.constants import USERS_COLLECTION
from app.common.utils.string.main import random_string
from app.models.user.user import UserInResponseModel, UserModel


class TestUserService:
    """ User Service Test Case. """

    @staticmethod
    async def create_fake(db: AsyncIOMotorClient) -> UserInResponseModel:
        """ Create Fake User. """

        username = f"test_{random_string(10)}"
        email = f"test_{random_string(10)}@test.com"

        user = UserModel(
            username=username,
            email=EmailStr(email),
            password=random_string(16),
            first_name=random_string(16),
            last_name=random_string(16),
        )

        await db[USERS_COLLECTION].insert_one(user.mongo())

        return UserInResponseModel(**user.dict())
