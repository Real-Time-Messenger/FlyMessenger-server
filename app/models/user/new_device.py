import random
import string
from typing import Union

from fastapi import Request

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr

from app.exception.api import APIException
from app.models.user.user import UserModel
from app.services.mail.mail import EmailService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService


class NewDeviceService:

    @staticmethod
    async def generate_secret(email: EmailStr) -> str:
        """
        Generate secret and send it to user email.

        :param email: User email.
        :return: str
        """

        # Generate 8 digit random digit
        secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Send email with secret
        await EmailService.send_email(
            email=email,
            subject="New device authentication",
            template="new_device",
            secret=secret
        )

        return secret

    @staticmethod
    async def validate(body, request: Request, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Validate incoming new device authentication request. """

        if not body.code:
            raise APIException.bad_request("The ew device confirmation code is required.", translation_key="newDeviceCodeIsEmpty")

        user = await UserService.get_by_new_device_code(body.code, db)
        if not user:
            raise APIException.not_found("The new device confirmation code is incorrect.",
                                         translation_key="newDeviceCodeIsNotValid")

        is_alien = await UserSessionService.is_alien_user(user, request)
        if not is_alien:
            raise APIException.bad_request("The new device confirmation code is incorrect.",
                                           translation_key="newDeviceCodeIsNotValid")

        if body.code != user.new_device_code:
            raise APIException.forbidden("The new device confirmation code is incorrect.",
                                         translation_key="newDeviceCodeIsNotValid")

        if not user.is_active:
            raise APIException.forbidden("The account is not active.", translation_key="userNotActive")

        user.new_device_code = None
        await UserService.update(user, db)

        return user