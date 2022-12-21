from typing import Union

from fastapi import Depends, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from motor.motor_asyncio import AsyncIOMotorClient

from app.database.main import get_database
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.user import UserModel
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService


class OAuth2PasswordBearerCookie(OAuth2):
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
                raise APIException.unauthorized("Not authenticated. Please login.")
            
            return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie(token_url="/api/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserModel:
    """ Get the current user from the token. """

    token = token.replace("Bearer ", "")
    payload = TokenService.decode(token)

    if not payload:
        raise APIException.unauthorized("Invalid token.")

    user = await UserService.get_by_id(PyObjectId(payload["payload"]["id"]), db)
    if not user:
        raise APIException.unauthorized("Invalid authentication credentials.")

    is_token_exist = await UserSessionService.get_by_token(token, db)
    if not is_token_exist:
        raise APIException.unauthorized("Invalid authentication credentials.")

    return user
