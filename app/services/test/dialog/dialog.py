from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import DIALOGS_COLLECTION, USERS_COLLECTION
from app.models.dialog.dialog import DialogInResponseModel, DialogModel, UserInDialogModel, UserInDialogResponseModel
from app.models.user.user import UserInResponseModel, UserModel
from app.services.test.user.user import TestUserService


class TestDialogService:
    """ Implementation of the `TestDialogService`. """

    @staticmethod
    async def clear(db: AsyncIOMotorClient) -> None:
        """ Clear all Dialogs. """

        await db[DIALOGS_COLLECTION].delete_many({})

    @staticmethod
    async def create_fake(db: AsyncIOMotorClient) -> DialogModel:
        """ Create fake dialog. """

        from_user = await TestUserService.create_fake(db)
        to_user = await TestUserService.create_fake(db)

        dialog = DialogModel(
            from_user=UserInDialogModel(
                id=from_user.id,
            ),
            to_user=UserInDialogModel(
                id=to_user.id,
            ),
        )

        await db[DIALOGS_COLLECTION].insert_one(dialog.mongo())

        return dialog


    @staticmethod
    async def build(dialog: DialogModel, db: AsyncIOMotorClient) -> DialogInResponseModel:
        """ Build dialog. """

        to_user = await db[USERS_COLLECTION].find_one({"_id": dialog.to_user.id})

        user = UserModel.from_mongo(to_user)

        return DialogInResponseModel(
            last_message=None,
            images=[],
            unread_messages=0,
            messages=[],
            user=UserInDialogResponseModel(**user.dict()),
            is_me_blocked=False,
            id=dialog.id,
            **dialog.from_user.dict(exclude={"id"}),
        )


