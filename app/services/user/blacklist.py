from datetime import datetime
from typing import Union, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import USERS_COLLECTION
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserModel, BlacklistedUserInResponseModel, BlacklistInCreateModel
from app.models.user.user import UserModel
from app.services.user.user import UserService


class BlacklistService:
    """
    Service for blacklist.

    This class is responsible for performing tasks when a user blocks another user and is also responsible for CRUD requests.
    """

    @staticmethod
    async def build_blacklisted_user(
            user_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Optional[BlacklistedUserInResponseModel]:
        """
        Convert blocked user to response model.

        :param user_id: User ID.
        :param db: Database connection object.

        :return: Blacklisted user object.
        """

        blacklisted_user = await UserService.get_by_id(user_id, db)
        if not blacklisted_user:
            await BlacklistService.delete(user_id, db)
            return None

        return BlacklistedUserInResponseModel(**blacklisted_user.dict())

    @staticmethod
    async def block_or_unblock_user(
            body: BlacklistInCreateModel,
            current_user: UserModel,
            db: AsyncIOMotorClient
    ) -> bool:
        """
        Block or unblock a user.

        :param body: Blacklist object.
        :param current_user: Current user object.
        :param db: Database connection object.

        :return: True if the user was blocked, False if the user was unblocked.
        """

        is_blocked = True

        if body.blacklisted_user_id == current_user.id:
            raise APIException.bad_request("You can't block yourself.", translation_key="cantBlockYourself")

        blacklist_model = await BlacklistService.get_user_in_blacklist(body.blacklisted_user_id, current_user)
        if blacklist_model:
            current_user.blacklist.remove(blacklist_model)
            is_blocked = False
        else:
            new_blacklist = BlacklistedUserModel(
                blacklisted_user_id=body.blacklisted_user_id,
                blocked_at=datetime.now(tz=None)
            )

            current_user.blacklist.append(new_blacklist)

        await UserService.update(current_user, db)

        return is_blocked

    @staticmethod
    async def get_user_in_blacklist(
            blacklisted_user_id: PyObjectId,
            current_user: UserModel
    ) -> Optional[BlacklistedUserModel]:
        """
        Get a user in blacklist.

        :param blacklisted_user_id: Blacklisted user ID.
        :param current_user: Current user object.

        :return: **Blacklisted user object** if the user is in the blacklist, **None** if the user is not in the blacklist.
        """

        for blacklist_model in current_user.blacklist:
            if blacklist_model.blacklisted_user_id == blacklisted_user_id:
                return blacklist_model

        return None

    @staticmethod
    async def unblock_user(
            blacklisted_user_id: str,
            current_user: UserModel,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Unblock a user (from list of blocked users).

        :param blacklisted_user_id: Blacklisted user ID.
        :param current_user: Current user object.
        :param db: Database connection object.
        """

        blacklist_model = await BlacklistService.get_user_in_blacklist(PyObjectId(blacklisted_user_id), current_user)
        if blacklist_model:
            current_user.blacklist.remove(blacklist_model)
            await UserService.update(current_user, db)

    @staticmethod
    async def delete(
            user_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Delete user from every blacklist.

        :param user_id: User ID.
        :param db: Database connection object.
        """

        await db[USERS_COLLECTION].update_many(
            {"blacklist.blacklisted_user_id": user_id},
            {"$pull": {"blacklist": {"blacklisted_user_id": user_id}}}
        )
