from datetime import datetime
from typing import Union

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import USERS_COLLECTION
from app.models.common.object_id import PyObjectId
from app.models.user.sessions import UserSessionModel
from app.models.user.user import UserModel
from app.services.location.location import LocationService
from app.services.token.token import TokenService
from app.services.user.user import UserService


class UserSessionService:

    @staticmethod
    async def create(
            user: UserModel,
            token: str,
            request: Request,
            session: AsyncIOMotorClient
    ) -> UserSessionModel:
        """ Create new session for user. """

        ip_address = await LocationService.get_ip_address(request)
        user_location = await LocationService.get_location(ip_address)

        user_session = UserSessionModel(
            token=token,
            ip_address=ip_address,
            type=request.headers.get("X-Client-Type") or "unknown",
            label=f'Fly Messenger {request.headers.get("X-Client-Type") or "unknown"} {request.headers.get("X-Client-Version") or "unknown"}',
            location=f"{user_location.get('city')}, {user_location.get('region')}, {user_location.get('country')}",
            created_at=datetime.now(tz=None)
        )

        user.sessions.append(user_session.mongo())

        await UserService.update(user, session)

        return user_session

    @staticmethod
    async def validate_session(
            session: UserSessionModel,
            request: Request
    ) -> bool:
        """
        Validate session.

        Check if:
        - Session is valid (if token is not expired).
        - Session is from the same device.
        - Session is from the same location.
        """

        token = TokenService.decode(session.token)
        if not token:
            return False

        expires_at = datetime.fromtimestamp(token.get("exp"))
        if expires_at < datetime.now():
            return False

        if session.type != request.headers.get("X-Client-Type"):
            return False

        ip_address = await LocationService.get_ip_address(request)
        user_location = await LocationService.get_location(ip_address)
        if session.ip_address != ip_address:
            return False

        location = f"{user_location.get('city')}, {user_location.get('region')}, {user_location.get('country')}"
        if session.location != location:
            return False

        return True

    @staticmethod
    async def get_current_by_user(
            user: UserModel,
            request: Request,
            db: AsyncIOMotorClient
    ) -> Union[UserSessionModel, None]:
        """ Get current session by user. """

        for session in user.sessions:
            is_valid_session = await UserSessionService.validate_session(session, request)

            if is_valid_session:
                return session
            else:
                await UserSessionService.delete(user, session.token, db)

        return None

    @staticmethod
    async def delete(
            user: UserModel,
            token: str,
            db: AsyncIOMotorClient
    ) -> None:
        """ Delete session. """

        user.sessions = [session for session in user.sessions if session.token != token]

        await UserService.update(user, db)

    @staticmethod
    async def get_by_id(session_id: PyObjectId, db: AsyncIOMotorClient):
        """ Get session by id. """

        # get session by id in user array of sessions and return session
        user = await db[USERS_COLLECTION].find_one({"sessions._id": session_id})
        if user:
            for session in user.get("sessions"):
                if session.get("_id") == session_id:
                    return UserSessionModel(**session)

        return None

    @staticmethod
    async def get_by_token(token: str, db: AsyncIOMotorClient) -> Union[UserSessionModel, None]:
        """ Get session by token. """

        # get session by token in user array of sessions and return session
        user = await db[USERS_COLLECTION].find_one({"sessions.token": token})
        if user:
            for session in user.get("sessions"):
                if session.get("token") == token:
                    return UserSessionModel(**session)

        return None

    @staticmethod
    async def is_alien_user(user: UserModel, request: Request):
        """
        Check if user is alien.

        Algorithm:
            - If user IP address not found in sessions, then we assume that user is alien.

        :return: bool
        """

        ip_address = await LocationService.get_ip_address(request)
        for session in user.sessions:
            if session.ip_address == ip_address:
                return False

        return True
