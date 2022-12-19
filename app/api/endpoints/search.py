from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.models.user.user import UserModel
from app.services.search.search import SearchService

router = APIRouter()

@router.get('/{dialog_id}/{query}')
async def search_by_dialog(
        query: str,
        dialog_id: str,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    result = await SearchService.search_by_dialog(query, dialog_id, current_user, db)

    return result


@router.get('/{query}')
async def search(
        query: str,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    result = await SearchService.search(query, current_user, db)

    return result