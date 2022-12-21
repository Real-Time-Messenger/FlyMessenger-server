from datetime import datetime, timedelta
from typing import Union

from fastapi import APIRouter, Depends, Request, Response, Cookie, Body
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import cookie_options, FRONTEND_URL
from app.common.swagger.responses.exceptions import ACCOUNT_NOT_ACTIVATED
from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.exception.api import APIException
from app.exception.body import APIRequestValidationException
from app.models.common.exceptions.body import RequestValidationDetails, APIRequestValidationModel
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.object_id import PyObjectId
from app.models.user.new_device import NewDeviceService
from app.models.user.token import TokenModel
from app.models.user.two_factor import TwoFactorService
from app.models.user.user import UserInAuthResponseModel, UserInSignUpModel, UserModel, UserInCallResetPasswordModel, \
    UserInResetPasswordModel, UserInActivationModel, UserInLoginModel, UserInEventResponseModel, \
    UserInTwoFactorAuthenticationModel, UserInNewDeviceConfirmationModel
from app.models.user.utils.reset_code import ValidateResetPasswordTokenModel
from app.models.user.utils.response_types import AuthResponseType
from app.services.hash.hash import HashService
from app.services.mail.mail import EmailService
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService

router = APIRouter()


@router.post(
    path="/login",
    summary="Authenticate a user",
    response_description="A token for the new user to use for authentication.",
    responses={
        200: {
            "description": "A token for the new user to use for authentication.",
            "content": {
                "application/json": {
                    "example": TokenModel(token="generated_token")
                }
            }
        },
        403: {
            "description": "Account is not activated.",
            "content": {
                "application/json": {
                    "example": ACCOUNT_NOT_ACTIVATED
                }
            }
        },
        404: {
            "description": "The username or password is incorrect.",
            "content": {
                "application/json": {
                    "example": APIExceptionModel(message="The username or password is incorrect.", code=404)
                }
            }
        },
        422: {
            "description": "The request body is invalid.",
            "content": {
                "application/json": {
                    "example": APIRequestValidationModel(
                        details=[
                            RequestValidationDetails(
                                message="Field required",
                                location="body",
                                field="username"
                            ),
                            RequestValidationDetails(
                                message="Field required",
                                location="body",
                                field="password"
                            )
                        ],
                        code=422
                    )
                }
            }
        }
    },
)
async def login(
        request: Request,
        response: Response,
        body: UserInLoginModel = Body(...),
        db: AsyncIOMotorClient = Depends(get_database)
) -> Union[UserInAuthResponseModel, UserInEventResponseModel]:
    """
    Authenticate user and return token.

    - **username**: Username of the user
    - **password**: Password of the user
    """

    user = await UserService.authenticate(body.username, body.password.get_secret_value(), db)
    if not user:
        raise APIException.not_found("The username or password is incorrect.", translation_key="incorrectUsernameOrPassword")

    is_alien_user = await UserSessionService.is_alien_user(user, request)
    if is_alien_user:
        new_device_code = await NewDeviceService.generate_secret(user.email)

        user.new_device_code = new_device_code
        await UserService.update(user, db)

        return UserInEventResponseModel(event=AuthResponseType.NEW_DEVICE)

    if user.settings.two_factor_enabled:
        two_factor_code = await TwoFactorService.generate_secret(user.email)

        user.two_factor_code = two_factor_code
        await UserService.update(user, db)

        return UserInEventResponseModel(event=AuthResponseType.TWO_FACTOR)

    token = TokenService.generate_access_token(id=user.id)
    await UserSessionService.create(user, token, request, db)

    response.set_cookie(key="Authorization", value=f"Bearer {token}", **cookie_options)

    return UserInAuthResponseModel(token=token)


@router.post(
    path="/signup",
    summary="Create a new user",
    response_description="A token for the new user to use for authentication.",
    responses={
        200: {
            "description": "A token for the new user to use for authentication.",
            "content": {
                "application/json": {
                    "example": TokenModel(token="generated_token")
                }
            }
        },
        400: {
            "description": "The username or email is already taken.",
            "content": {
                "application/json": {
                    "example": APIExceptionModel(message="The username or email is already taken.", code=400)
                }
            }
        },
        422: {
            "description": "The request body is invalid.",
            "content": {
                "application/json": {
                    "example": APIRequestValidationModel(
                        details=[
                            RequestValidationDetails(
                                message="Field required.",
                                location="body",
                                field="username"
                            ),
                            RequestValidationDetails(
                                message="Field required.",
                                location="body",
                                field="email"
                            ),
                            RequestValidationDetails(
                                message="Field required.",
                                location="body",
                                field="password"
                            ),
                            RequestValidationDetails(
                                message="Passwords do not match.",
                                location="body",
                                field="passwordConfirm"
                            )
                        ],
                        code=422
                    )
                }
            }
        }
    },
)
async def signup(
        body: UserInSignUpModel,
        request: Request,
        response: Response,
        db: AsyncIOMotorClient = Depends(get_database)
) -> Union[RequestValidationError, UserInAuthResponseModel]:
    """
    Create a new user and return token.

    - **username**: Username of the user
    - **email**: Email of the user
    - **password**: Password of the user
    - **passwordConfirm**: Password confirmation of the user
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
    token = TokenService.generate_access_token(id=user.id)

    user.activation_token = TokenService.generate_custom_token(timedelta(hours=1), id=user.id)
    await UserSessionService.create(user, token, request, db)

    response.set_cookie(key="Authorization", value=f"Bearer {token}", **cookie_options)

    return UserInAuthResponseModel(token=token)


@router.post(
    path="/logout",
)
async def logout(
        response: Response,
        current_user: UserModel = Depends(get_current_user),
        authorization: str = Cookie(alias="Authorization"),
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Logout a user.
    """
    token = authorization.replace("Bearer ", "")

    await UserSessionService.delete(current_user, token, db)

    response.delete_cookie(key="Authorization")

# TODO: Implement stuff:
# - Request for reset password
# - Change password
# - Two factor authentication
# - New device confirmation

@router.post(path="/activate")
async def activate(
        body: UserInActivationModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Activate a user account.

    - **code**: Activation code
    """

    decoded_token = TokenService.decode(body.token)
    if not decoded_token:
        raise APIException.bad_request("Invalid activation code.", translation_key="invalidActivationCode")

    decoded_token = decoded_token.get("payload")
    if decoded_token.get("type") != "activation":
        raise APIException.bad_request("Invalid activation code.", translation_key="invalidActivationCode")

    expiration_time = TokenService.get_token_expiration(body.token)
    if expiration_time < datetime.now():
        raise APIException.bad_request("The activation code has expired.", translation_key="activationCodeExpired")

    user = await UserService.get_by_id(PyObjectId(decoded_token.get("id")), db)
    if not user or user.is_active:
        raise APIException.bad_request("Invalid activation code.", translation_key="invalidActivationCode")

    user.activation_token = None

    await UserService.activate(user, db)


@router.post(path="/call-reset-password")
async def call_reset_password(
        body: UserInCallResetPasswordModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Call reset password.
    """
    user = await UserService.get_by_email(body.email, db)
    if not user:
        raise APIException.not_found("The email is incorrect.")

    if not user.is_active:
        raise APIException.forbidden("The account is not active.")

    token = TokenService.generate_custom_token(timedelta(hours=1), type="reset_password", id=user.id)

    user.reset_password_token = token

    await UserService.update(user, db)
    await EmailService.send_email(user.email, "Reset password", "reset_password", url=f"{FRONTEND_URL}/m/reset-password?token={token}")

@router.post(path="/validate-reset-password-token")
async def validate_reset_password_token(
        body: ValidateResetPasswordTokenModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> bool:
    """
    Validate reset password token.
    """
    user = await UserService.get_by_reset_password_token(body.token, db)
    if not user:
        raise APIException.not_found("The reset password token is incorrect.", translation_key="resetPasswordTokenIsNotValid")

    token_expiration = TokenService.get_token_expiration(body.token)

    if token_expiration < datetime.now():
        raise APIException.forbidden("The reset password token is expired.", translation_key="resetPasswordTokenIsExpired")

    return True

@router.post(path="/reset-password")
async def reset_password(
        body: UserInResetPasswordModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Reset password.
    """
    token_payload = TokenService.decode(body.token)
    user_id = PyObjectId(token_payload.get("id"))

    user = await UserService.get_by_id(user_id, db)
    if not user:
        raise APIException.not_found("The reset password token is incorrect.", translation_key="resetPasswordTokenIsNotValid")

    token_expiration = TokenService.get_token_expiration(body.token)

    if token_expiration < datetime.utcnow():
        raise APIException.forbidden("The reset password token is expired.", translation_key="resetPasswordTokenIsExpired")

    user.password = HashService.get_hash(body.password)
    user.reset_password_token = None

    await UserService.update(user, db)


@router.post(path="/two-factor")
async def two_factor_authentication(
        body: UserInTwoFactorAuthenticationModel,
        response: Response,
        request: Request,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInAuthResponseModel:
    """
    Two-factor authentication.
    """
    user = await TwoFactorService.validate(body, db)

    token = TokenService.generate_access_token(id=user.id)
    await UserSessionService.create(user, token, request, db)

    response.set_cookie(key="Authorization", value=f"Bearer {token}", **cookie_options)

    return UserInAuthResponseModel(token=token)


@router.post(path="/new-device")
async def new_device_confirmation(
        body: UserInNewDeviceConfirmationModel,
        response: Response,
        request: Request,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInAuthResponseModel:
    """
    New device confirmation.
    """

    user = await NewDeviceService.validate(body, request, db)

    token = TokenService.generate_access_token(id=user.id)
    await UserSessionService.create(user, token, request, db)

    response.set_cookie(key="Authorization", value=f"Bearer {token}", **cookie_options)

    return UserInAuthResponseModel(token=token)