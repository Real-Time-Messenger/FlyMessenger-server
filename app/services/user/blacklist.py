from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserModel, BlacklistedUserInResponseModel, BlacklistInCreateModel
from app.models.user.user import UserModel
from app.services.user.user import UserService


class BlacklistService:

    @staticmethod
    async def build_blacklisted_user(body: BlacklistedUserModel,
                                     db: AsyncIOMotorClient) -> BlacklistedUserInResponseModel:
        """ Convert blocked user to response model. """

        blacklisted_user = await UserService.get_by_id(body.blacklisted_user_id, db)

        return BlacklistedUserInResponseModel(**blacklisted_user.dict())

    @staticmethod
    async def block_or_unblock_user(body: BlacklistInCreateModel, current_user: UserModel,
                                    db: AsyncIOMotorClient) -> bool:
        """ Block or unblock a user. """

        is_blocked = True

        if body.blacklisted_user_id == current_user.id:
            raise APIException.bad_request("You can't block yourself.")

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
    async def get_user_in_blacklist(blacklisted_user_id: PyObjectId,
                                    current_user: UserModel) -> BlacklistedUserModel | None:
        """ Get a user in blacklist. """

        for blacklist_model in current_user.blacklist:
            if blacklist_model.blacklisted_user_id == blacklisted_user_id:
                return blacklist_model

        return None

    @staticmethod
    async def unblock_user(blacklisted_user_id: str, current_user: UserModel, db: AsyncIOMotorClient):
        """ Unblock a user. """

        blacklist_model = await BlacklistService.get_user_in_blacklist(PyObjectId(blacklisted_user_id), current_user)
        if blacklist_model:
            current_user.blacklist.remove(blacklist_model)
            await UserService.update(current_user, db)
