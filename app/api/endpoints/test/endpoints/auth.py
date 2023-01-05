from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.database.main import get_database
from app.models.user.user import UserInLoginModel, UserInAuthResponseModel
from app.services.token.token import TokenService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService

router = APIRouter()


@router.post("/login")
async def test_login(
        body: UserInLoginModel,
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInAuthResponseModel:
    """
    Authenticate user.

    **NOTE**: This endpoint is for testing purposes only.
    """

    user = await UserService.authenticate(body.username, body.password.get_secret_value(), db)

    if len(user.sessions) > 0:
        session = user.sessions[-1]
    else:
        token = TokenService.generate_access_token(id=user.id)
        session = await UserSessionService.create_fake(user, token, db)

    return UserInAuthResponseModel(token=session.token)
