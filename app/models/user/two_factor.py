import random
import string
from typing import Union

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr

from app.exception.api import APIException
from app.models.user.user import UserInTwoFactorAuthenticationModel, UserModel
from app.services.mail.mail import EmailService
from app.services.user.user import UserService


class TwoFactorService:

    @staticmethod
    async def generate_secret(email: EmailStr) -> str:
        """
        Generate secret and send it to user email.

        :return: str
        """

        # Generate 8 digit random digit.
        secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Send email with secret.
        await EmailService.send_email(
            email=email,
            subject="Two factor authentication",
            template="two_factor",
            secret=secret
        )

        return secret

    @staticmethod
    async def validate(body: UserInTwoFactorAuthenticationModel, db: AsyncIOMotorClient) -> Union[UserModel, None]:
        """ Validate incoming two-factor authentication request. """

        user = await UserService.get_by_two_factor_code(body.code, db)
        if not user:
            raise APIException.not_found("The two-factor code is incorrect.", translation_key="twoFactorCodeIsNotValid")

        if not user.settings.two_factor_enabled:
            raise APIException.forbidden("Two factor authentication is not enabled.",
                                         translation_key="twoFactorIsNotEnabled")

        if not user.two_factor_code:
            raise APIException.forbidden("Two factor authentication is not enabled.",
                                         translation_key="twoFactorIsNotEnabled")

        if body.code != user.two_factor_code:
            raise APIException.forbidden("The two-factor code is incorrect.", translation_key="twoFactorCodeIsNotValid")

        if not user.is_active:
            raise APIException.forbidden("The account is not active.", translation_key="userNotActive")

        user.two_factor_code = None
        await UserService.update(user, db)

        return user
