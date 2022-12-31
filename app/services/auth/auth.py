from datetime import timedelta, datetime
from typing import Union

from fastapi import Request, Response
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import cookie_options
from app.common.frontend.pages import ACTIVATION_PAGE, RESET_PASSWORD
from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.exception.body import APIRequestValidationException
from app.models.common.exceptions.body import RequestValidationDetails
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserInSignUpModel, UserInEventResponseModel, UserInLoginModel, UserInAuthResponseModel, \
    UserInActivationModel, UserInCallResetPasswordModel, UserInResetPasswordModel, UserInTwoFactorAuthenticationModel
from app.models.user.utils.response_types import AuthResponseType
from app.services.auth.new_device import NewDeviceService
from app.services.auth.two_factor import TwoFactorService
from app.services.hash.hash import HashService
from app.services.mail.mail import EmailService
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService


class AuthService:
    """
    Authentication service.

    This service is responsible for user authentication and authorization.
    """

    @staticmethod
    def setup_token(token: str, response: Response) -> None:
        """
        Setup base authentication token.

        :param token: Token to be set.
        :param response: Response object.
        """

        response.set_cookie(
            key="Authorization",
            value=f"Bearer {token}",
            **cookie_options
        )

        response.headers["Authorization"] = token

    @staticmethod
    async def login(
            body: UserInLoginModel,
            request: Request,
            response: Response,
            db: AsyncIOMotorClient
    ) -> Union[UserInAuthResponseModel, UserInEventResponseModel]:
        """
        Authenticate user and return token **(if user doesn't have 2FA enabled)**.

        Also, we check the user's account on someone else's device (the one that authenticates for the first time),
        whether the user has activated his account, and also for the presence of two-factor authentication.

        :param body: User login body.
        :param request: Request object.
        :param response: Response object.
        :param db: Database object.

        :return: **Token** (if the login success) or **UserInEventResponseModel(event=Union[AuthResponseType.NEW_DEVICE, AuthResponseType.TWO_FACTOR, AuthResponseType.ACTIVATION_REQUIRED])** (if the login was successful, but confirmation is required).
        """

        user = await UserService.authenticate(body.username, body.password.get_secret_value(), db)

        is_user_foreign = await UserSessionService.is_foreign_user(user, request)
        if is_user_foreign:
            await NewDeviceService.generate_secret(user, db)

            return UserInEventResponseModel(event=AuthResponseType.NEW_DEVICE)

        if user.settings.two_factor_enabled:
            await TwoFactorService.generate_secret(user, db)

            return UserInEventResponseModel(event=AuthResponseType.TWO_FACTOR)

        token = TokenService.generate_access_token(id=user.id)
        await UserSessionService.create(user, token, request, db)

        AuthService.setup_token(token, response)

        return UserInAuthResponseModel(token=token)

    @staticmethod
    async def signup(
            body: UserInSignUpModel,
            db: AsyncIOMotorClient
    ) -> UserInEventResponseModel:
        """
        Registration of a new user in the system.

        Upon successful registration, a token is sent to the user in the body of the response from the server,
        which serves to identify the user when sending requests to the server.

        :param body: User signup body.
        :param db: Database object.

        :return: Message that user was successfully registered and should activate his account.
        """

        is_username_exist = await UserService.get_by_username(body.username, db)
        if is_username_exist:
            error = RequestValidationDetails(
                message="The username is already taken.",
                location="body",
                field="username",
                translation="usernameAlreadyTaken"
            )

            raise APIRequestValidationException.from_details([error])

        is_email_exist = await UserService.get_by_email(body.email, db)
        if is_email_exist:
            error = RequestValidationDetails(
                message="The email is already taken.",
                location="body",
                field="email",
                translation="emailAlreadyTaken"
            )

            raise APIRequestValidationException.from_details([error])

        user = await UserService.create(body, db)

        user.activation_token = TokenService.generate_custom_token(
            timedelta(hours=1),
            id=user.id,
            type="activation"
        )
        await UserService.update(user, db)

        await EmailService.send_email(
            email=user.email,
            subject="Activate your account",
            template="activation",
            username=user.username,
            url=f"{ACTIVATION_PAGE}/{user.activation_token}",
        )

        return UserInEventResponseModel(event=AuthResponseType.ACTIVATION_REQUIRED)

    @staticmethod
    async def activate(body: UserInActivationModel, db: AsyncIOMotorClient) -> None:
        """
        User activation for further use of the API.

        :param body: User activation body.
        :param db: Database object.
        """

        decoded_token = TokenService.decode(body.token)
        if not decoded_token:
            raise APIException.bad_request(
                "Invalid activation code.",
                translation_key="invalidActivationCode"
            )

        decoded_token = decoded_token.get("payload")
        if decoded_token.get("type") != "activation":
            raise APIException.bad_request(
                "Invalid activation code.",
                translation_key="invalidActivationCode"
            )

        expiration_time = TokenService.get_token_expiration(body.token)
        if expiration_time < datetime.now():
            raise APIException.bad_request(
                "Activation code is expired.",
                translation_key="activationCodeIsExpired"
            )

        user_id = PyObjectId(decoded_token.get("id"))
        user = await UserService.get_by_id(user_id, db)
        if not user:
            raise APIException.bad_request(
                "Invalid activation code.",
                translation_key="invalidActivationCode"
            )

        if user.is_active:
            raise APIException.bad_request(
                "Account is already activated.",
                translation_key="accountIsAlreadyActivated"
            )

        user.activation_token = None
        user.is_active = True

        await UserService.update(user, db)

    @staticmethod
    async def call_reset_password(body: UserInCallResetPasswordModel, db: AsyncIOMotorClient) -> None:
        """
        Sending an email with a link to reset your password.

        :param body: User call reset password body.
        :param db: Database object.
        """

        user = await UserService.get_by_email(body.email, db)
        if not user:
            raise APIException.not_found(
                "User with this email does not exist.",
                translation_key="userDoesNotExist"
            )

        if not user.is_active:
            raise USER_NOT_ACTIVATED

        token = TokenService.generate_custom_token(
            timedelta(hours=1),
            type="reset_password",
            id=user.id
        )

        user.reset_password_token = token
        await UserService.update(user, db)

        await EmailService.send_email(
            user.email,
            "Password recovery request",
            "reset_password",
            url=f"{RESET_PASSWORD}?token={token}",
            username=user.username
        )

    @staticmethod
    async def reset_password(body: UserInResetPasswordModel, db: AsyncIOMotorClient) -> None:
        """
        Resetting the user's password.

        After successfully changing the password, the user must log in again.

        :param body: User reset password body.
        :param db: Database object.
        """

        token_payload = TokenService.decode(body.token)
        if not token_payload:
            raise APIException.bad_request(
                "The reset password token is incorrect.",
                translation_key="resetPasswordTokenIsNotValid"
            )

        user_id = token_payload.get("payload").get("id")
        if not user_id:
            raise APIException.bad_request(
                "The reset password token is incorrect.",
                translation_key="resetPasswordTokenIsNotValid"
            )

        user = await UserService.get_by_id(PyObjectId(user_id), db)
        if not user:
            raise APIException.not_found(
                "The reset password token is incorrect.",
                translation_key="resetPasswordTokenIsNotValid"
            )

        token_expiration = TokenService.get_token_expiration(body.token)
        if token_expiration < datetime.utcnow():
            raise APIException.forbidden(
                "The reset password token is expired.",
                translation_key="resetPasswordTokenIsExpired"
            )

        if HashService.verify_password(body.password, user.password):
            raise APIException.bad_request(
                "You cannot use the same password as before.",
                translation_key="cannotUseSamePassword"
            )

        user.password = HashService.get_hash(body.password)
        # user.reset_password_token = None

        await UserService.update(user, db)

    @staticmethod
    async def two_factor(
            body: UserInTwoFactorAuthenticationModel,
            request: Request,
            response: Response,
            db: AsyncIOMotorClient
    ) -> UserInAuthResponseModel:
        """
        User authentication using two-factor authentication.

        :param body: User two-factor authentication body.
        :param request: Request object.
        :param response: Response object.
        :param db: Database object.

        :return: User authentication token.
        """

        user = await TwoFactorService.validate(body, db)

        token = TokenService.generate_access_token(id=user.id)
        await UserSessionService.create(user, token, request, db)

        AuthService.setup_token(token, response)

        return UserInAuthResponseModel(token=token)
