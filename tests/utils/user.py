from random import random

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from app.common.constants import SELF_URL, USERS_COLLECTION
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserModel
from tests.utils.utils import random_lower_string, random_email


def user_authentication_headers(
        *, client: TestClient
) -> dict[str, str]:
    """ Get user authentication headers. """

    data = {"username": "test", "password": "123123123"}

    request = client.post(f"{SELF_URL}/api/test/auth/login", json=data)

    response = request.json()
    auth_token = response["token"]

    return {"Authorization": f"Bearer {auth_token}"}


def create_fake_user(db: AsyncIOMotorClient) -> UserModel:
    """ Create fake user. """

    random_username = random

    user = UserModel(
        username=random_lower_string(),
        email=random_email(),
        first_name="test",
        last_name="user",
        photo_url="https://avatars.githubusercontent.com/u/45159366?v=4",
        blacklist=[],
        password="9328490289304829385902385902838435345234",
        is_test=True
    )

    db[USERS_COLLECTION].insert_one(UserModel.mongo(user))

    return jsonable_encoder(user)
