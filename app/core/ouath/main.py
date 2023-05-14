from typing import Union

from fastapi import Depends, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.swagger.responses.exceptions import USER_NOT_AUTHORIZED, USER_NOT_ACTIVATED
from app.database.main import get_database
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserModel
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    Implementation of the OAuth2PasswordBearer.
    This class allows us to use the OAuth2 scheme in out app with the headers and cookies.

    More info: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    """

    def __init__(
            self,
            token_url: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Union[str, None]:
        cookie_authorization: str = request.cookies.get("Authorization")
        header_authorization: str = request.headers.get("Authorization")

        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )
        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )

        if cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param
        elif header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param
        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise USER_NOT_AUTHORIZED

            return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(token_url="/api/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserModel:
    """ Decode the token and get the user from the database. """

    token = token.replace("Bearer ", "")
    payload = TokenService.decode(token)

    if not payload:
        raise APIException.unauthorized("Invalid token.", translation_key="invalidToken")

    user = await UserService.get_by_id__uncached(PyObjectId(payload["payload"]["id"]), db)
    if not user:
        raise APIException.unauthorized("Cannot find user with this token.", translation_key="userNotFound")

    if not user.is_active:
        raise USER_NOT_ACTIVATED

    is_token_exist = await UserSessionService.get_by_token(token, db)
    if not is_token_exist:
        raise USER_NOT_AUTHORIZED

    return user
