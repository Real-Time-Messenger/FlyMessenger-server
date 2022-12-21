from datetime import datetime, timedelta
from typing import Union

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from app.common.constants import USERS_COLLECTION
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserModel, UserInSignUpModel, UserInResponseModel, UserInSearchModel
from app.services.hash.hash import HashService
from app.services.image.image import ImageService
from app.services.token.token import TokenService


class UserService:
    @staticmethod
    async def get_by_id(user_id: PyObjectId, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Get user by id. """

        user = await db[USERS_COLLECTION].find_one({"_id": user_id})
        return UserModel.from_mongo(user) if user else None

    @staticmethod
    async def authenticate(username: str, password: str, db: AsyncIOMotorClient) -> UserModel:
        """ Authenticate a user with username/email and password. """

        user = await UserService.get_by_username(username, db) or await UserService.get_by_email(username, db)
        if not user:
            raise APIException.not_found(
                "We couldn't find an account with that username or email. Please check your credentials and try again.")

        if not HashService.verify_password(password, user.password):
            raise APIException.unauthorized("Incorrect password. Please try again.")

        if not user.is_active:
            token_expiration = TokenService.get_token_expiration(user.activation_token)
            if token_expiration.timestamp() < datetime.now(tz=None).timestamp():
                user.activation_token = TokenService.generate_custom_token(timedelta(hours=1), type="activation",
                                                                           id=user.id)
                await UserService.update(user, db)

                raise APIException.forbidden("Your activation token has expired. We have sent you a new one.",
                                             translation_key="tokenExpiredCheckEmail")

            raise APIException.forbidden("Your account is not active. Please check your email for an activation link.",
                                         translation_key="userNotActiveCheckEmail")

        return user

    @staticmethod
    async def create(body: UserInSignUpModel, db: AsyncIOMotorClient) -> UserModel:
        """ Create a new user model. """

        try:
            user = UserModel(first_name=body.username, photo_url="https://i.imgur.com/1Q1Z1Zm.png", **body.dict())
            new_user = await db[USERS_COLLECTION].insert_one(user.mongo())

            created_user = await UserService.get_by_id(new_user.inserted_id, db)

            return created_user
        except DuplicateKeyError:
            raise APIException.bad_request("The username or email is already taken.",
                                           translation_key="usernameOrEmailIsTaken")

    @staticmethod
    async def update(user: UserModel, db: AsyncIOMotorClient) -> UserModel:
        """ Update a user model. """

        try:
            await db[USERS_COLLECTION].update_one({"_id": user.id}, {"$set": user.mongo()})

            return user
        except DuplicateKeyError as e:

            # Get the field that is duplicated.
            key = e.details.get("errmsg").split("index: ")[1].split("_1")[0]

            raise APIException.bad_request(f"The {key} is already taken.")

    @staticmethod
    async def update_avatar(file: UploadFile, user: UserModel, db: AsyncIOMotorClient) -> UserModel:
        """ Update user avatar. """

        filename = await ImageService.upload_image(file)

        user.photo_url = filename
        await UserService.update(user, db)

        return user

    @staticmethod
    async def build_user_response(current_user: UserModel, db: AsyncIOMotorClient) -> UserInResponseModel:
        """ Convert user to response model. """

        blacklist = []
        for blacklist_model in current_user.blacklist:
            blacklisted_user = await UserService.get_by_id(blacklist_model.blacklisted_user_id, db)
            blacklist.append(UserInResponseModel(**blacklisted_user.dict()))

        current_user.blacklist = blacklist

        return UserInResponseModel(**current_user.dict())

    @staticmethod
    async def search(query: str, current_user: UserModel, db: AsyncIOMotorClient) -> list[UserInSearchModel]:
        """ Search for users. """

        users = await db[USERS_COLLECTION].find(
            {
                "$or": [
                    {"firstName": {"$regex": query, "$options": "i"}},
                    {"lastName": {"$regex": query, "$options": "i"}},
                    {"username": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                ],
                "_id": {"$ne": current_user.id},
            }
        ).to_list(length=100)

        return [UserInSearchModel(**UserModel.from_mongo(user).dict()) for user in users]

    @staticmethod
    async def get_by_username(username: str, db: AsyncIOMotorClient):
        """ Get user by username. """

        user = await db[USERS_COLLECTION].find_one({"username": username})
        return UserModel.from_mongo(user) if user else None

    @staticmethod
    async def get_by_email(email: str, db: AsyncIOMotorClient):
        """ Get user by email. """

        user = await db[USERS_COLLECTION].find_one({"email": email})
        return UserModel.from_mongo(user) if user else None

    @staticmethod
    async def activate(current_user: UserModel, db: AsyncIOMotorClient) -> None:
        """ Activate user account. """

        current_user.is_active = True

        await UserService.update(current_user, db)

    @staticmethod
    async def get_by_reset_password_token(token: str, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Get user by reset password token. """

        user = await db[USERS_COLLECTION].find_one({"resetPasswordToken": token})
        return UserModel.from_mongo(user) if user else None

    @staticmethod
    async def get_by_two_factor_code(code: str, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Get user by two-factor code. """

        user = await db[USERS_COLLECTION].find_one({"twoFactorCode": code})
        return UserModel.from_mongo(user) if user else None

    @staticmethod
    async def get_by_new_device_code(code: str, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Get user by new device confirmation code. """

        user = await db[USERS_COLLECTION].find_one({"newDeviceCode": code})
        return UserModel.from_mongo(user) if user else None
