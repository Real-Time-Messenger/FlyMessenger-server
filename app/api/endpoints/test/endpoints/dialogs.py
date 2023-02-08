from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.database.main import get_test_database
from app.models.dialog.dialog import DialogInResponseModel
from app.services.test.dialog.dialog import TestDialogService

router = APIRouter()


@router.post(
    path=""
)
async def create_fake_dialog(
        db: AsyncIOMotorClient = Depends(get_test_database)
) -> DialogInResponseModel:
    """
    Create Fake Dialog

    **NOTE**: This endpoint is for testing purposes only.
    """

    await TestDialogService.clear(db)

    new_dialog = await TestDialogService.create_fake(db)
    return await TestDialogService.build(new_dialog, db)
