from typing import Any, Union

from motor.motor_asyncio import AsyncIOMotorClient

from app.common.constants import DIALOGS_COLLECTION
from app.exception.api import APIException
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInCreateModel, DialogModel, DialogInResponseModel, DialogInUpdateModel, \
    UserInDialogResponseModel, UserInDialogCreateModel
from app.models.user.user import UserModel
from app.services.dialog.message import DialogMessageService
from app.services.user.blacklist import BlacklistService
from app.services.user.user import UserService


class DialogService:

    @staticmethod
    async def get_by_id(
            dialog_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Union[DialogModel, None]:
        """
        Get dialog by id

        :param dialog_id: Dialog ID
        :param db: Database connection object
        :return: Dialog object
        """

        dialog = await db[DIALOGS_COLLECTION].find_one({"_id": dialog_id})
        return DialogModel.from_mongo(dialog)

    @staticmethod
    async def get_by_user_id(
            user_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Union[list[DialogModel], list]:
        """
        Get dialog by user id

        :param user_id: User ID
        :param db: Database connection object
        :return: Dialog object
        """

        dialog = db[DIALOGS_COLLECTION].find({"$or": [{"fromUser._id": user_id}, {"toUser._id": user_id}]}).limit(100)
        return [DialogModel.from_mongo(dialog) async for dialog in dialog]

    @staticmethod
    async def get_by_user_and_receiver_id(
            user_id: PyObjectId,
            receiver_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Union[DialogModel, None]:
        """
        Get dialog by user id and receiver id

        :param user_id: User ID
        :param receiver_id: Receiver ID
        :param db: Database connection object
        :return: Dialog object
        """

        dialog = await db[DIALOGS_COLLECTION].find_one(
            {"$or": [{"fromUser._id": user_id, "toUser._id": receiver_id},
                     {"fromUser._id": receiver_id, "toUser._id": user_id}]})
        return DialogModel.from_mongo(dialog) if dialog else None

    @staticmethod
    async def create(body: DialogInCreateModel, current_user: UserModel, db: AsyncIOMotorClient) -> DialogModel:
        """ Create a new dialog. """

        is_dialog_exist = await DialogService.get_by_user_and_receiver_id(current_user.id, body.to_user_id, db)
        if is_dialog_exist:
            raise APIException.bad_request("Dialog already exist")

        is_adding_self = body.to_user_id == current_user.id
        if is_adding_self:
            raise APIException.bad_request("You can't add yourself to dialog.")

        from_user_payload = UserInDialogCreateModel(
            id=current_user.id,
        )
        to_user_payload = UserInDialogCreateModel(
            id=body.to_user_id,
        )

        dialog_body = DialogModel(from_user=from_user_payload, to_user=to_user_payload)

        new_dialog = await db.dialogs.insert_one(dialog_body.mongo())
        return await DialogService.get_by_id(new_dialog.inserted_id, db)

    @staticmethod
    async def get_dialogs(current_user: UserModel, db: AsyncIOMotorClient) -> Union[list[DialogInResponseModel], list]:
        """ Get all dialogs. """

        result = []
        dialogs = await DialogService.get_by_user_id(current_user.id, db)
        if not dialogs:
            return []

        for dialog in dialogs:
            dialog = await DialogService.build_dialog(dialog, current_user, db)
            result.append(dialog)

        return result

    @staticmethod
    async def build_dialog(new_dialog: DialogModel, current_user: UserModel, db: AsyncIOMotorClient,
                           last_message: Union[DialogInResponseModel, None] = None) -> DialogInResponseModel:
        """ Build dialog instance for response. """

        if new_dialog.from_user.id == current_user.id:
            user = await UserService.get_by_id(new_dialog.to_user.id, db)
        else:
            user = await UserService.get_by_id(new_dialog.from_user.id, db)

        user_in_dialog = UserInDialogResponseModel(**user.dict())

        label = ' '.join(filter(None, (user_in_dialog.first_name, user_in_dialog.last_name)))

        messages = await DialogMessageService.get_by_dialog_id_and_build(new_dialog.id, db)
        unread_messages = await DialogMessageService.get_unread_messages_count(new_dialog.id, current_user.id, db)
        last_message = last_message or messages[-1] if messages else None

        is_user_blocked = await BlacklistService.get_user_in_blacklist(user.id, current_user)
        user_in_dialog.is_blocked = is_user_blocked is not None

        is_me_blocked = await BlacklistService.get_user_in_blacklist(current_user.id, user)

        images = [message.file for message in messages if message.file]

        return DialogInResponseModel(
            label=label,
            last_message=last_message,
            images=images,
            unread_messages=unread_messages,
            messages=messages,
            user=user_in_dialog,
            is_me_blocked=bool(is_me_blocked),
            id=new_dialog.id,
            **new_dialog.from_user.dict(exclude={"id"}),
        )

    @staticmethod
    async def search(query: str, current_user: UserModel, db: AsyncIOMotorClient) -> list[DialogInResponseModel]:
        """ Search dialogs by query. """

        dialogs = await DialogService.get_dialogs(current_user, db)
        result = []

        for dialog in dialogs:
            # if query.lower() in dialog.label.lower() or dialog.user is not None and \
            #         (query.lower() in dialog.user.first_name.lower() or
            #         query.lower() in dialog.user.last_name.lower() or
            #         query.lower() in dialog.user.username.lower()):
            #     result.append(dialog)

            print(dialog)

            if query.lower() in dialog.label.lower() or (
                    dialog.user is not None and
                    (query.lower() in dialog.user.first_name.lower() or
                     dialog.user.last_name is not None and query.lower() in dialog.user.last_name.lower() or
                        query.lower() in dialog.user.username.lower())

            ):
                result.append(dialog)

        return result

    @staticmethod
    async def update(dialog_id: PyObjectId, body: DialogInUpdateModel, current_user: UserModel,
                     db: AsyncIOMotorClient) -> DialogInResponseModel:
        """ Update dialog by id. """

        dialog = await DialogService.get_by_id(dialog_id, db)
        if not dialog:
            raise APIException.not_found("Dialog not found.")

        dialog_user = dialog.from_user if dialog.from_user.id == current_user.id else dialog.to_user

        for key, value in body.dict(exclude_unset=True).items():

            # If user try to update isPinned state for dialog
            if key == DialogInUpdateModel.__fields__[key].name and value is not None:
                pinned_dialogs_count = await DialogService.get_pinned_dialogs_count(current_user.id, db)

                # Throw error if user already pinned 10 dialogs
                if pinned_dialogs_count >= 10:
                    raise APIException.bad_request("You can't pin more than 10 dialogs.")

                setattr(dialog_user, key, value)

        dialog = DialogModel(**dialog.dict())

        await db[DIALOGS_COLLECTION].find_one_and_update({"_id": dialog.id}, {"$set": dialog.mongo()})

        return await DialogService.build_dialog(dialog, current_user, db)

    @staticmethod
    async def get_pinned_dialogs_count(user_id: PyObjectId, db: AsyncIOMotorClient) -> int:
        """ Get all pinned dialogs. """

        return await db[DIALOGS_COLLECTION].count_documents(
            {"$or": [{"fromUserId": user_id}, {"toUserId": user_id}], "isPinned": True})

    @staticmethod
    async def delete(dialog_id: PyObjectId, current_user: UserModel, db: AsyncIOMotorClient) -> None:
        """ Delete dialog by id. """

        dialog = await DialogService.get_by_id(dialog_id, db)
        if not dialog:
            raise APIException.not_found("Dialog not found.")

        is_dialog_owner = dialog.from_user.id == current_user.id or dialog.to_user.id == current_user.id
        if not is_dialog_owner:
            raise APIException.bad_request("You can't delete dialog.")

        await db[DIALOGS_COLLECTION].delete_one({"_id": dialog_id})

        await DialogMessageService.delete_by_dialog_id(dialog_id, db)
