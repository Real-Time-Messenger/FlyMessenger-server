from typing import Union

from fastapi import APIRouter, Depends, UploadFile, File, Cookie
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.ouath.main import get_current_user
from app.database.main import get_database
from app.models.common.responses.blacklist import BlockOrUnblockUserResponseModel
from app.models.sockets.utils import SendBlockedMessageToClient
from app.models.user.blacklist import BlacklistInCreateModel, BlacklistedUserInResponseModel
from app.models.user.sessions import UserSessionInResponseModel
from app.models.user.user import UserModel, UserInUpdateModel, UserInResponseModel
from app.services.user.blacklist import BlacklistService
from app.services.user.user import UserService
from app.services.websocket.socket import socket_service, SocketSendTypesEnum

router = APIRouter()


@router.get(
    path="/me"
)
async def get_me(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInResponseModel:
    user = await UserService.build_user_response(current_user, db)

    return user


@router.get(
    path="/me/sessions"
)
async def get_me(
        current_user: UserModel = Depends(get_current_user)
):
    return [UserSessionInResponseModel(**session.dict()) for session in current_user.sessions]


@router.get(
    path="/me/blocked-users"
)
async def get_me(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> Union[list[BlacklistedUserInResponseModel], list]:
    return [await BlacklistService.build_blacklisted_user(blacklist_model, db) for blacklist_model in current_user.blacklist]


@router.put(
    path="/me",
)
async def update_me(
        body: UserInUpdateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInResponseModel:
    # Find key in body that exist in the UserModel
    for key, value in body.dict(exclude_unset=True).items():

        # Find key in UserModel
        if hasattr(current_user, key):
            setattr(current_user, key, value)

        # Find key in UserSettingsModel
        elif hasattr(current_user.settings, key):
            setattr(current_user.settings, key, value)

    updated_user = await UserService.update(current_user, db)
    return await UserService.build_user_response(updated_user, db)


@router.put(
    path="/me/avatar",
)
async def update_avatar(
        file: UploadFile = File(...),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    updated_user = await UserService.update_avatar(file, current_user, db)
    return updated_user


@router.post("/blacklist")
async def block_or_unblock_user(
        body: BlacklistInCreateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> BlockOrUnblockUserResponseModel:
    blocked_state = await BlacklistService.block_or_unblock_user(body, current_user, db)

    user = await UserService.build_user_response(current_user, db)

    payload = SendBlockedMessageToClient(
        user_id=current_user.id,
        is_blocked=blocked_state,
    )

    await socket_service.emit_to_user(
        SocketSendTypesEnum.USER_BLOCKED,
        body.blacklisted_user_id,
        jsonable_encoder(payload)
    )

    return BlockOrUnblockUserResponseModel(
        is_blocked=blocked_state,
        blacklist=user.blacklist,
        user_id=body.blacklisted_user_id
    )


@router.delete(
    path="/me/blacklist/{blacklisted_user_id}"
)
async def unblock_user(
        blacklisted_user_id: str,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> Union[list[BlacklistedUserInResponseModel], list]:
    await BlacklistService.unblock_user(blacklisted_user_id, current_user, db)

    return [await BlacklistService.build_blacklisted_user(blacklist_model, db) for blacklist_model in current_user.blacklist]