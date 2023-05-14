import re
from datetime import datetime, timedelta
from typing import Optional

from aiocache import cached
from aiocache.serializers import PickleSerializer
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from app.common.constants import USERS_COLLECTION
from app.common.frontend.pages import ACTIVATION_PAGE
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInResponseModel, UserInDialogResponseModel
from app.models.user.user import UserModel, UserInSignUpModel, UserInResponseModel
from app.services.hash.hash import HashService
from app.services.image.image import ImageService
from app.services.mail.mail import EmailService
from app.services.token.token import TokenService


class UserService:
    """
    Service for user.

    This class is responsible for performing tasks for CRUD requests.
    """

    @staticmethod
    @cached(ttl=30, serializer=PickleSerializer())
    async def get_by_id(
            user_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Optional[UserModel]:
        """
        Get user by id.

        :param user_id: User ID.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"_id": user_id})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def get_by_id__uncached(
            user_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Optional[UserModel]:
        """
        Get user by id.

        :param user_id: User ID.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"_id": user_id})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def authenticate(username: str, password: str, db: AsyncIOMotorClient) -> UserModel:
        """
        Authenticate a user with username/email and password.

        :param username: Username or email.
        :param password: Password.
        :param db: Database connection object.

        :return: User object.
        """

        user = await UserService.get_by_username(username, db) or await UserService.get_by_email(username, db)
        if not user:
            raise APIException.not_found(
                "We couldn't find an account with that username or email. Please check your credentials and try again.",
                translation_key="userNotFound"
            )

        if not HashService.verify_password(password, user.password):
            raise APIException.unauthorized(
                "Wrong password. Check your credentials and try again.",
                translation_key="incorrectPassword"
            )

        if not user.is_active:
            token_expiration = TokenService.get_token_expiration(user.activation_token) or None
            if token_expiration is None or token_expiration.timestamp() < datetime.now(tz=None).timestamp():
                user.activation_token = TokenService.generate_custom_token(timedelta(hours=1), type="activation",
                                                                           id=user.id)

                await EmailService.send_email(
                    user.email,
                    "Activate your account",
                    "activation",
                    username=user.username,
                    url=f"{ACTIVATION_PAGE}/{user.activation_token}"
                )

                await UserService.update(user, db)

            raise APIException.forbidden("Your account is not active. Please check your email for an activation link.",
                                         translation_key="userNotActiveCheckEmail")

        return user

    @staticmethod
    async def create(body: UserInSignUpModel, db: AsyncIOMotorClient) -> UserModel:
        """
        Create a new user.

        :param body: User object.
        :param db: Database connection object.

        :return: New user object.
        """

        try:
            image = await ImageService.generate_mock_image(body.username)
            user = UserModel(first_name=body.username, photo_url=image, **body.dict())

            new_user = await db[USERS_COLLECTION].insert_one(user.mongo())

            return await UserService.get_by_id__uncached(new_user.inserted_id, db)
        except DuplicateKeyError:
            raise APIException.bad_request("The username or email is already taken.",
                                           translation_key="usernameOrEmailIsTaken")

    @staticmethod
    async def update(user: UserModel, db: AsyncIOMotorClient) -> UserModel:
        """
        Update a user model.

        :param user: User object.
        :param db: Database connection object.

        :return: Updated user object.
        """

        try:
            await db[USERS_COLLECTION].update_one({"_id": user.id}, {"$set": user.mongo()})

            return user
        except DuplicateKeyError as e:

            # Get the field that is duplicated.
            key = e.details.get("errmsg").split("index: ")[1].split("_1")[0]

            raise APIException.bad_request(f"The '{key}' is already taken.")

    @staticmethod
    async def update_avatar(file: UploadFile, user: UserModel, db: AsyncIOMotorClient) -> UserModel:
        """
        Update user avatar.

        :param file: Image file.
        :param user: User object.
        :param db: Database connection object.

        :return: Updated user object.
        """

        filename = await ImageService.upload_image(file, "avatars")

        user.photo_url = filename
        await UserService.update(user, db)

        return user

    @staticmethod
    async def build_user_response(current_user: UserModel, db: AsyncIOMotorClient) -> UserInResponseModel:
        """
        Convert user to response model.

        :param current_user: User object.
        :param db: Database connection object.

        :return: User response object.
        """

        blacklist = []
        for blacklist_model in current_user.blacklist:
            blacklisted_user = await UserService.get_by_id__uncached(blacklist_model.blacklisted_user_id, db)

            if blacklist_model is None:
                continue

            blacklist.append(UserInResponseModel(**blacklisted_user.dict()))

        current_user.blacklist = blacklist

        return UserInResponseModel(**current_user.dict())

    @staticmethod
    async def search(
            query: str,
            current_user: UserModel,
            db: AsyncIOMotorClient
    ) -> list[DialogInResponseModel]:
        """
        Search for users.

        :param query: Search query.
        :param current_user: User object.
        :param db: Database connection object.

        :return: List of users.
        """

        query = re.sub(r"[^\w\s.]", "", query)

        users = await db[USERS_COLLECTION].find(
            {
                "$and": [
                    {
                        "$or": [
                            {"firstName": {"$regex": query, "$options": "i"}},
                            {"lastName": {"$regex": query, "$options": "i"}},
                            {"username": {"$regex": query, "$options": "i"}},
                            {"email": {"$regex": query, "$options": "i"}}
                        ]
                    },
                    {
                        "isTest": False,
                        "_id": {"$ne": current_user.id},
                        "isActive": True,
                    }
                ]
            }
        ).to_list(length=100)
        if not users:
            return []

        result = []

        for raw_user in users:
            user = UserModel.from_mongo(raw_user)

            is_me_blocked = current_user.id in [blacklist.blacklisted_user_id for blacklist in user.blacklist]
            pseudo_dialog = DialogInResponseModel(
                id=user.id,
                user=UserInDialogResponseModel(**user.dict()),
                images=[],
                unread_messages=0,
                is_pinned=False,
                is_notifications_enabled=True,
                is_sound_enabled=True,
                last_message=None,
                messages=[],
                is_me_blocked=is_me_blocked,
            )

            result.append(pseudo_dialog)

        return result

    @staticmethod
    async def get_by_username(username: str, db: AsyncIOMotorClient) -> Optional[UserModel]:
        """
        Get user by username.

        :param username: Username.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"username": username})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def get_by_email(email: str, db: AsyncIOMotorClient) -> Optional[UserModel]:
        """
        Get user by email.

        :param email: Email.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"email": email})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def get_by_two_factor_code(code: str, db: AsyncIOMotorClient) -> Optional[UserModel]:
        """
        Get user by two-factor code.

        :param code: Two-factor code.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"twoFactorCode": code})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def get_by_new_device_code(code: str, db: AsyncIOMotorClient) -> Optional[UserModel]:
        """
        Get user by new device confirmation code.

        :param code: New device confirmation code.
        :param db: Database connection object.

        :return: User object if found, None otherwise.
        """

        user = await db[USERS_COLLECTION].find_one({"newDeviceCode": code})
        if not user:
            return None

        return UserModel.from_mongo(user)

    @staticmethod
    async def delete(current_user: UserModel, db: AsyncIOMotorClient):
        """
        Delete user.

        :param current_user: User object.
        :param db: Database connection object.
        """

        await db[USERS_COLLECTION].delete_one({"_id": current_user.id})
