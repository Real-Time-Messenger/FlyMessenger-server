import random
import string
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr

from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.user.user import UserInTwoFactorAuthenticationModel, UserModel
from app.services.mail.mail import EmailService
from app.services.user.user import UserService


class TwoFactorService:
    """
    Service for two-factor authentication.

    This class is responsible for performing tasks when two-factor authentication is enabled on the user's account.
    """

    @staticmethod
    async def generate_secret(email: EmailStr) -> str:
        """
        Generate two-factor code and send it to user email.

        :param email: User email.

        :return: Two-factor authentication secret.
        """

        secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        await EmailService.send_email(
            email=email,
            subject="Two factor authentication",
            template="two_factor",
            secret=secret
        )

        return secret

    @staticmethod
    async def validate(body: UserInTwoFactorAuthenticationModel, db: AsyncIOMotorClient) -> UserModel:
        """
        Validate incoming two-factor authentication request.

        :return: User object.
        """

        user = await UserService.get_by_two_factor_code(body.code, db)
        if not user:
            raise APIException.not_found("The two-factor code is incorrect.", translation_key="twoFactorCodeIsNotValid")

        if not user.settings.two_factor_enabled:
            raise APIException.forbidden("Two-factor authentication is not enabled.",
                                         translation_key="twoFactorIsNotEnabled")

        if not user.two_factor_code:
            raise APIException.forbidden("Two-factor authentication is not enabled.",
                                         translation_key="twoFactorIsNotEnabled")

        if body.code != user.two_factor_code:
            raise APIException.forbidden("The two-factor code is incorrect.", translation_key="twoFactorCodeIsNotValid")

        if not user.is_active:
            raise USER_NOT_ACTIVATED

        user.two_factor_code = None
        await UserService.update(user, db)

        return user
