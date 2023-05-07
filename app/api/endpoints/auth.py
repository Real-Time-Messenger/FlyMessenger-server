from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, Request, Response
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import cookie_options
from app.common.swagger.responses.auth import LOGIN_RESPONSES, SIGNUP_RESPONSES, LOGOUT_RESPONSES, ACTIVATION_RESPONSES, \
    CALL_RESET_PASSWORD_RESPONSES, VALIDATE_RESET_PASSWORD_TOKEN_RESPONSES, RESET_PASSWORD_RESPONSES, \
    TWO_FACTOR_RESPONSES, NEW_DEVICE_RESPONSES
from app.core.ouath.main import get_current_user, oauth2_scheme
from app.database.main import get_database
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserInAuthResponseModel, UserInSignUpModel, UserModel, UserInCallResetPasswordModel, \
    UserInResetPasswordModel, UserInActivationModel, UserInLoginModel, UserInEventResponseModel, \
    UserInTwoFactorAuthenticationModel, UserInNewDeviceConfirmationModel
from app.models.user.utils.reset_code import ValidateResetPasswordTokenModel
from app.services.auth.auth import AuthService
from app.services.auth.new_device import NewDeviceService
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService
from app.services.websocket.base import SocketSendTypesEnum
from app.services.websocket.socket import socket_service

router = APIRouter()


@router.post(
    path="/login",
    responses=LOGIN_RESPONSES,
)
async def login(
        request: Request,
        response: Response,
        body: UserInLoginModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> Union[UserInAuthResponseModel, UserInEventResponseModel]:
    """
    Authenticate user and return token **(if user doesn't have 2FA enabled)**

    - **username**: Username of the user
    - **password**: Password of the user
    """

    return await AuthService.login(body, request, response, db)


@router.post(
    path="/signup",
    responses=SIGNUP_RESPONSES
)
async def signup(
        body: UserInSignUpModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInEventResponseModel:
    """
    Create a new user and send activation mail.

    - **username**: Username of the user
    - **email**: Email of the user
    - **password**: Password of the user
    - **passwordConfirm**: Password confirmation of the user
    """

    return await AuthService.signup(body, db)


@router.post(
    path="/logout",
    responses=LOGOUT_RESPONSES
)
async def logout(
        response: Response,
        current_user: UserModel = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Logout a current user.

    After successful logout, the token (from cookies or headers) will be invalidated.

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    token = token.replace("Bearer ", "")
    await UserSessionService.delete(current_user, token, db)

    body = {
        "userId": str(current_user.id),
        "status": False,
        "lastActivity": datetime.now()
    }

    await socket_service.emit_for_all(
        SocketSendTypesEnum.TOGGLE_ONLINE_STATUS,
        jsonable_encoder(body)
    )

    response.delete_cookie(key="Authorization")


@router.post(
    path="/activate",
    responses=ACTIVATION_RESPONSES
)
async def activate(
        body: UserInActivationModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Activate a user account.

    - **token**: Activation code
    """

    await AuthService.activate(body, db)


@router.post(
    path="/call-reset-password",
    responses=CALL_RESET_PASSWORD_RESPONSES
)
async def call_reset_password(
        body: UserInCallResetPasswordModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Sends an email message to the user with a link to reset their password

    * **email**: Email of the user
    """

    await AuthService.call_reset_password(body, db)


@router.post(
    path="/validate-reset-password-token",
    responses=VALIDATE_RESET_PASSWORD_TOKEN_RESPONSES
)
async def validate_reset_password_token(
        body: ValidateResetPasswordTokenModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Validate reset password token.

    * **token**: Reset password token
    """

    token = TokenService.decode(body.token)
    if token is None:
        raise APIException.bad_request("The reset password token is incorrect",
                                       translation_key="resetPasswordTokenIsNotValid")

    user_id = token.get("payload").get("id")
    if user_id is None:
        raise APIException.bad_request("The reset password token is incorrect",
                                       translation_key="resetPasswordTokenIsNotValid")

    user = await UserService.get_by_id__uncached(PyObjectId(user_id), db)
    if not user:
        raise APIException.not_found("The reset password token is incorrect.",
                                     translation_key="resetPasswordTokenIsNotValid")

    token_expiration = TokenService.get_token_expiration(body.token)
    if token_expiration < datetime.now():
        raise APIException.forbidden("The reset password token is expired.",
                                     translation_key="resetPasswordTokenIsExpired")


@router.post(
    path="/reset-password",
    responses=RESET_PASSWORD_RESPONSES
)
async def reset_password(
        body: UserInResetPasswordModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Reset password.

    * **token**: Reset password token
    * **password**: New password
    * **passwordConfirm**: New password confirmation
    """

    await AuthService.reset_password(body, db)


@router.post(
    path="/two-factor",
    responses=TWO_FACTOR_RESPONSES
)
async def two_factor_authentication(
        body: UserInTwoFactorAuthenticationModel,
        response: Response,
        request: Request,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInAuthResponseModel:
    """
    Two-factor authentication.

    * **code**: Two-factor authentication code
    """

    return await AuthService.two_factor(body, request, response, db)


@router.post(
    path="/new-device",
    responses=NEW_DEVICE_RESPONSES
)
async def new_device_confirmation(
        body: UserInNewDeviceConfirmationModel,
        response: Response,
        request: Request,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInAuthResponseModel:
    """
    New device confirmation.

    * **code**: New device confirmation code
    """

    user = await NewDeviceService.validate(body, request, db)

    token = TokenService.generate_access_token(id=user.id)
    await UserSessionService.create(user, token, request, db)

    response.set_cookie(key="Authorization", value=f"Bearer {token}", **cookie_options)

    return UserInAuthResponseModel(token=token)
