import random
import string

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr

from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.user.user import UserModel
from app.services.mail.mail import EmailService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService


class NewDeviceService:
    """
    Service for new device.

    This class is responsible for performing tasks when a user first logs into an account.
    """

    @staticmethod
    async def generate_secret(user: UserModel, db: AsyncIOMotorClient) -> str:
        """
        Generate secret and send it to user email.

        :param user: User Instance.
        :param db: Database connection.

        :return: New device secret.
        """

        secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        await EmailService.send_email(
            user.email,
            "Authentication on a new device",
            "new_device",
            username=user.username,
            secret=secret
        )

        user.new_device_code = secret
        await UserService.update(user, db)

        return secret

    @staticmethod
    async def validate(body, request: Request, db: AsyncIOMotorClient) -> UserModel:
        """
        Validate incoming new device authentication request.

        :param body: Request body.
        :param request: Request object.
        :param db: Database object.

        :return: User object.
        """

        user = await UserService.get_by_new_device_code(body.code, db)
        if not user:
            raise APIException.not_found("The new device confirmation code is incorrect.",
                                         translation_key="newDeviceCodeIsNotValid")

        is_foreign = await UserSessionService.is_foreign_user(user, request)
        if not is_foreign:
            raise APIException.bad_request("The new device confirmation code is incorrect.",
                                           translation_key="newDeviceCodeIsNotValid")

        if body.code != user.new_device_code:
            raise APIException.forbidden("The new device confirmation code is incorrect.",
                                         translation_key="newDeviceCodeIsNotValid")

        if not user.is_active:
            raise USER_NOT_ACTIVATED

        user.new_device_code = None
        await UserService.update(user, db)

        return user
