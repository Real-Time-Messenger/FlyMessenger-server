from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import DIALOG_MESSAGES_COLLECTION
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInResponseModel, LastMessageInDialogModel
from app.models.dialog.messages import DialogMessageInCreateModel, DialogMessageModel, DialogMessageInResponseModel, \
    SenderInDialogMessageModel
from app.services.user.user import UserService


class DialogMessageService:

    @staticmethod
    async def get_by_id(
            message_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> DialogMessageModel | None:
        """
        Get dialog message by id

        :param message_id: Dialog message ID
        :param db: Database connection object
        :return: Dialog message object
        """

        message = await db[DIALOG_MESSAGES_COLLECTION].find_one({"_id": message_id})
        return DialogMessageModel.from_mongo(message) if message else None

    @staticmethod
    async def create(
            body: DialogMessageInCreateModel,
            db: AsyncIOMotorClient
    ) -> DialogMessageModel:
        """
        Create a new dialog message.

        :param body: Dialog message body
        :param db: Database connection object
        :return: Dialog message object
        """

        new_message_body = DialogMessageModel(**body.dict(), sent_at=datetime.now(tz=None))

        new_dialog_message = await db[DIALOG_MESSAGES_COLLECTION].insert_one(new_message_body.mongo())
        return await DialogMessageService.get_by_id(new_dialog_message.inserted_id, db)

    @staticmethod
    async def build_message(new_message: DialogMessageModel, db: AsyncIOMotorClient) -> DialogMessageInResponseModel | None:
        """
        Build dialog message.

        :param new_message: Dialog message object
        :return: Dialog message object
        """

        user = await UserService.get_by_id(new_message.sender_id, db)

        if not user:
            return None

        return DialogMessageInResponseModel(
            sender=user, **new_message.dict()
        )

    @staticmethod
    async def get_by_dialog_id(dialog_id: PyObjectId, db: AsyncIOMotorClient) -> list[DialogMessageModel] | list:
        """
        Get dialog message by dialog id

        :param dialog_id: Dialog ID
        :param db: Database connection object
        :return: Dialog message object
        """

        dialogs = db[DIALOG_MESSAGES_COLLECTION].find({"dialogId": dialog_id}).limit(100)
        return [DialogMessageModel.from_mongo(dialog) async for dialog in dialogs]

    @staticmethod
    async def get_by_dialog_id_and_build(dialog_id: PyObjectId, db: AsyncIOMotorClient) -> list[
        DialogMessageInResponseModel]:
        """
        Get dialog message by dialog id and build

        :param dialog_id: Dialog ID
        :param db: Database connection object
        :return: Dialog message object
        """

        result = []
        messages = await DialogMessageService.get_by_dialog_id(dialog_id, db)

        for message in messages:
            sender = await UserService.get_by_id(message.sender_id, db)

            # TODO: remove it.
            if not sender:
                continue

            result.append(
                DialogMessageInResponseModel(
                    sender=SenderInDialogMessageModel(**sender.dict()),
                    sent_at=message.sent_at,
                    **message.dict(exclude={"sent_at"})
                )
            )

        return result

    @staticmethod
    async def read_message(message_id: PyObjectId, dialog_id: PyObjectId, db: AsyncIOMotorClient):
        """ Set message as read """

        await db[DIALOG_MESSAGES_COLLECTION].update_one(
            {"_id": message_id, "dialogId": dialog_id},
            {"$set": {"isRead": True}}
        )

        return await DialogMessageService.get_by_id(message_id, db)

    @staticmethod
    async def get_unread_messages_count(dialog_id: PyObjectId, user_id: PyObjectId, db: AsyncIOMotorClient) -> int:
        """ Get unread messages count """

        return await db[DIALOG_MESSAGES_COLLECTION].count_documents(
            {"dialogId": dialog_id, "senderId": {"$ne": user_id}, "isRead": False}
        )

    @staticmethod
    async def get_by_text(query: str, dialog_id: PyObjectId, db: AsyncIOMotorClient):
        """ Get messages by text """

        messages = db[DIALOG_MESSAGES_COLLECTION].find(
            {
                "text": {"$regex": query, "$options": "i"},
                "dialogId": dialog_id,
            }
        ).limit(100)

        return [DialogMessageModel.from_mongo(message) async for message in messages]

    @staticmethod
    async def search(query: str, dialogs: list[DialogInResponseModel], db: AsyncIOMotorClient) -> list[DialogInResponseModel]:
        """ Search messages """

        result = []
        for dialog in dialogs:
            messages = await DialogMessageService.get_by_text(query, dialog.id, db)

            for message in messages:
                sender = await UserService.get_by_id(message.sender_id, db)

                result.append(
                    DialogInResponseModel(
                        **dialog.dict(exclude={"last_message"}),
                        last_message=LastMessageInDialogModel(
                            sender=sender,
                            sent_at=message.sent_at,
                            **message.dict(exclude={"sent_at"})
                        )
                    )
                )

        return result

    @staticmethod
    async def delete_by_dialog_id(dialog_id: PyObjectId, db: AsyncIOMotorClient):
        """ Delete messages by dialog id """

        await db[DIALOG_MESSAGES_COLLECTION].delete_many({"dialogId": dialog_id})
