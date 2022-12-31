from fastapi import APIRouter, Depends, Path
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.swagger.responses.dialogs import CREATE_DIALOG_RESPONSES, GET_MY_DIALOGS_RESPONSES, \
    UPDATE_DIALOG_RESPONSES, DELETE_DIALOG_RESPONSES
from app.common.swagger.responses.dialogs.messages.get_dialog_messages import GET_DIALOG_MESSAGES_RESPONSES
from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.models.common.object_id import PyObjectId
from app.models.common.search.skip_and_limit import SkipAndLimitModel
from app.models.dialog.dialog import DialogInCreateModel, DialogInResponseModel, DialogInUpdateModel
from app.models.dialog.messages import DialogMessageInResponseModel
from app.models.user.user import UserModel
from app.services.dialog.dialog import DialogService
from app.services.dialog.message import DialogMessageService

router = APIRouter()


@router.post(
    path="",
    responses=CREATE_DIALOG_RESPONSES
)
async def create_dialog(
        body: DialogInCreateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> DialogInResponseModel:
    """
    Create dialog with user

    * **toUserId**: User ID to create dialog with

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """
    new_dialog = await DialogService.create(body, current_user, db)
    new_dialog = await DialogService.build_dialog(new_dialog, current_user, db)

    return DialogInResponseModel(**new_dialog.dict())


@router.get(
    path="/me",
    responses=GET_MY_DIALOGS_RESPONSES
)
async def get_dialogs(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> list[DialogInResponseModel]:
    """
    Get current user dialogs

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await DialogService.get_dialogs(current_user, db)


@router.get(
    path="/{dialogId}/messages",
    status_code=200,
    responses=GET_DIALOG_MESSAGES_RESPONSES
)
async def get_dialog_messages(
        dialog_id: PyObjectId = Path(..., alias="dialogId"),
        body: SkipAndLimitModel = Depends(),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> list[DialogMessageInResponseModel]:
    """
    Get messages for dialog

    * **dialogId**: Dialog ID
    * **skip**: Messages count that will be skipped **(number)**
    * **limit**: Messages count that will be returned **(number)**

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await DialogMessageService.get_dialog_messages(dialog_id, body.skip, body.limit, db)


@router.put(
    path="/{dialogId}",
    responses=UPDATE_DIALOG_RESPONSES
)
async def update_dialog(
        body: DialogInUpdateModel,
        dialog_id: PyObjectId = Path(alias="dialogId"),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> DialogInResponseModel:
    """
    Update dialog

    * **dialogId**: Dialog ID

    **Field which can be updated:**
    * **isPinned**: Dialog pinned status (boolean)
    * **isSoundEnabled**: Dialog sound status (boolean)
    * **isNotificationsEnabled**: Dialog notifications status (boolean)

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await DialogService.update(dialog_id, body, current_user, db)


@router.delete(
    path="/{dialogId}",
    status_code=204,
    responses=DELETE_DIALOG_RESPONSES
)
async def delete_dialog(
        dialog_id: PyObjectId = Path(alias="dialogId"),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Delete dialog by ID

    * **dialogId**: Dialog ID

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    await DialogService.delete(PyObjectId(dialog_id), current_user, db)
