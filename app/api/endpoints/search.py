from fastapi import APIRouter, Depends, Path, Query
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.swagger.responses.search import SEARCH_BY_DIALOG_RESPONSES, SEARCH_RESPONSES
from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.models.common.object_id import PyObjectId
from app.models.search.search import SearchResultModel
from app.models.user.user import UserModel
from app.services.search.search import SearchService

router = APIRouter()


@router.get(
    path="/{dialogId}",
    responses=SEARCH_BY_DIALOG_RESPONSES
)
async def search_by_dialog(
        query: str = Query(...),
        dialog_id: PyObjectId = Path(..., alias='dialogId'),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> SearchResultModel:
    """
    Search messages by dialog

    * **dialogId**: Dialog ID
    * **query**: search query (string)

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await SearchService.search_by_dialog(query, dialog_id, current_user, db)


@router.get(
    path="",
    responses=SEARCH_RESPONSES,
    response_model=SearchResultModel
)
async def search(
        query: str = Query(...),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> SearchResultModel:
    """
    Search dialogs, messages and users in whole app

    * **query**: search query (string)

    **Note:** This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await SearchService.search(query, current_user, db)
