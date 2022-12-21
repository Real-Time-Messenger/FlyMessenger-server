from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInCreateModel, DialogInResponseModel, DialogInUpdateModel
from app.models.dialog.messages import DialogMessageInAppendModel
from app.models.user.user import UserModel
from app.services.dialog.dialog import DialogService
from app.services.dialog.message import DialogMessageService

router = APIRouter()


@router.post(
    path="",
    response_model=DialogInResponseModel
)
async def create_dialog(
        body: DialogInCreateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    new_dialog = await DialogService.create(body, current_user, db)
    new_dialog = await DialogService.build_dialog(new_dialog, current_user, db)

    return DialogInResponseModel(**new_dialog.dict())


@router.get(
    path="/me",
    response_model=list[DialogInResponseModel]
)
async def get_dialogs(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    return await DialogService.get_dialogs(current_user, db)


@router.get(
    path="/{dialog_id}/messages",
)
async def get_dialog_messages(
        dialog_id: PyObjectId,
        body: DialogMessageInAppendModel = Depends(),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    return await DialogMessageService.get_dialog_messages(dialog_id, body.skip, body.limit, db)


@router.put(
    path="/{dialog_id}"
)
async def update_dialog(
        dialog_id: str,
        body: DialogInUpdateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    updated_dialog_field = await DialogService.update(PyObjectId(dialog_id), body, current_user, db)

    return updated_dialog_field


@router.delete(
    path="/{dialog_id}"
)
async def delete_dialog(
        dialog_id: str,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    await DialogService.delete(PyObjectId(dialog_id), current_user, db)