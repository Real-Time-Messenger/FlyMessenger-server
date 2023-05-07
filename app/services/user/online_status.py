from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.models.common.object_id import PyObjectId
from app.models.user.user import UserModel
from app.services.user.user import UserService


class UserOnlineStatusService:

    @staticmethod
    async def toggle_online_status(user_id: PyObjectId, status: bool, db: AsyncIOMotorClient) -> Optional[UserModel]:
        """ Toggle online status. """

        user = await UserService.get_by_id__uncached(user_id, db)
        if not user: return None

        if not user.settings.last_activity_mode:
            user.is_online = None
            await UserService.update(user, db)
            return user

        user.is_online = status
        if not status:
            user.last_activity = datetime.now(tz=None)

        await UserService.update(user, db)

        return user
