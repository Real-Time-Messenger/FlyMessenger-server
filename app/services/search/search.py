from motor.motor_asyncio import AsyncIOMotorClient

from app.models.common.object_id import PyObjectId
from app.models.search.search import SearchResultModel
from app.models.user.user import UserModel
from app.services.dialog.dialog import DialogService
from app.services.dialog.message import DialogMessageService
from app.services.user.user import UserService


class SearchService:
    """
    Service for search.

    This class is responsible for performing search-related tasks.
    """

    @staticmethod
    async def search(
            query: str,
            current_user: UserModel,
            db: AsyncIOMotorClient
    ) -> SearchResultModel:
        """
        Search by query.

        :param query: Search query.
        :param current_user: Current user.
        :param db: Database connection object.

        :return: Search result object.
        """

        dialogs = await DialogService.search(query, current_user, db)

        user_dialogs = await DialogService.get_dialogs(current_user, db)
        messages = await DialogMessageService.search(query, user_dialogs, db)

        users = await UserService.search(query, current_user, db)

        return SearchResultModel(dialogs=dialogs, messages=messages, users=users)

    @staticmethod
    async def search_by_dialog(
            query: str,
            dialog_id: PyObjectId,
            current_user: UserModel,
            db: AsyncIOMotorClient
    ) -> SearchResultModel:
        """
        Search by dialog.

        :param query: Search query.
        :param dialog_id: Dialog ID.
        :param current_user: Current user.
        :param db: Database connection object.

        :return: Search result object.
        """

        dialog = await DialogService.get_by_id(dialog_id, db)
        dialog = await DialogService.build_dialog(dialog, current_user, db)
        messages = await DialogMessageService.search(query, [dialog], db)

        return SearchResultModel(dialogs=[], messages=messages)
