from datetime import datetime
from typing import Union, Optional, List

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import USERS_COLLECTION
from app.models.common.object_id import PyObjectId
from app.models.user.sessions import UserSessionModel, UserSessionTypesEnum, UserSessionInResponseModel
from app.models.user.user import UserModel
from app.services.location.location import LocationService
from app.services.token.token import TokenService
from app.services.user.user import UserService


class UserSessionService:
    """
    Service for user sessions.

    This class is responsible for performing tasks when a user logs in and out, as well as for CRUD requests.
    """

    @staticmethod
    async def create(
            user: UserModel,
            token: str,
            request: Request,
            db: AsyncIOMotorClient
    ) -> UserSessionModel:
        """
        Create new session for user.

        :param user: User object.
        :param token: Token object.
        :param request: Request object.
        :param db: Database connection object.

        :return: User session object.
        """

        ip_address = await LocationService.get_ip_address(request)
        user_location = await LocationService.get_location(ip_address)

        client_type = request.headers.get("X-Client-Type") or "unknown"
        session_type = UserSessionTypesEnum(client_type.lower())

        user_session = UserSessionModel(
            token=token,
            ip_address=ip_address,
            type=session_type,
            label=f'Fly Messenger {request.headers.get("X-Client-Type") or "unknown"} {request.headers.get("X-Client-Version") or "unknown"}',
            location=f"{user_location.get('city')}, {user_location.get('region')}, {user_location.get('country')}",
            created_at=datetime.now(tz=None)
        )

        user.sessions.append(user_session.mongo())

        await UserService.update(user, db)
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

        :param session: User session object.
        :param request: Request object.

        :return: True if session is valid, False if session is invalid.
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
    ) -> Optional[UserSessionModel]:
        """
        Get current session by user.

        :param user: User object.
        :param request: Request object.
        :param db: Database connection object.

        :return: User session object.
        """

        for session in user.sessions:
            if session.type == UserSessionTypesEnum.TEST:
                continue

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
        """
        Delete session by token.

        :param user: User object.
        :param token: Token object.
        :param db: Database connection object.
        """

        user.sessions = [session for session in user.sessions if session.token != token]

        await UserService.update(user, db)

    @staticmethod
    async def get_by_id(
            session_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Optional[UserSessionModel]:
        """
        Get session by id.

        :param session_id: Session id.
        :param db: Database connection object.

        :return: User session object if session exists, None if session does not exist.
        """

        user = await db[USERS_COLLECTION].find_one({"sessions._id": session_id})
        if not user:
            return None

        for session in user.get("sessions"):
            if session.get("_id") == session_id and session.get("type") != UserSessionTypesEnum.TEST:
                return UserSessionModel(**session)

        return None

    @staticmethod
    async def get_by_token(
            token: str,
            db: AsyncIOMotorClient
    ) -> Optional[UserSessionModel]:
        """
        Get session by token.

        :param token: Token object.
        :param db: Database connection object.

        :return: User session object if session exists, None if session does not exist.
        """

        user = await db[USERS_COLLECTION].find_one({"sessions.token": token})
        if not user:
            return None

        for session in user.get("sessions"):
            if session.get("token") == token:
                return UserSessionModel.from_mongo(session)

        return None

    @staticmethod
    async def is_foreign_user(user: UserModel, request: Request) -> bool:
        """
        Check if user is foreign.

        Algorithm:
            - If user IP address not found in sessions, then we assume that user is foreign.

        :param user: User object.
        :param request: Request object.

        :return: True if user is foreign, False if user is not foreign.
        """

        ip_address = await LocationService.get_ip_address(request)
        for session in user.sessions:
            if session.ip_address == ip_address:
                return False

        return True

    @staticmethod
    async def create_fake(user, token, db) -> UserSessionModel:
        """
        Generate fake user session.

        :param user: User object.
        :param token: Token object.
        :param db: Database connection object.

        :return: User session object.
        """

        user_session = UserSessionModel(
            token=token,
            ip_address="TEST_IP_ADDRESS",
            type=UserSessionTypesEnum.TEST,
            label="TEST_USER",
            location="TEST_LOCATION",
            created_at=datetime.now(tz=None)
        )

        user.sessions.append(user_session.mongo())
        await UserService.update(user, db)

        return user_session

    @staticmethod
    async def build_sessions(user_id: PyObjectId, token: str, db: AsyncIOMotorClient) -> List[UserSessionModel]:
        """
        Build sessions.

        :param user_id: User id.
        :param token: Current user token.
        :param db: Database connection object.

        :return: List of user session objects.
        """

        # set the `current` field to True if the sessions token is the same as the user's current token
        user = await UserService.get_by_id(user_id, db)

        sessions = []
        for user_session in user.sessions:
            session = UserSessionInResponseModel.from_mongo(user_session.dict())

            if user_session.token == token:
                session.current = True

            sessions.append(session)

        return sessions
