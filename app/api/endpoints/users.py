from typing import Union

from fastapi import APIRouter, Depends, UploadFile, File, Response
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.swagger.responses.users import GET_ME_RESPONSES, GET_MY_SESSIONS_RESPONSES, \
    GET_MY_BLOCKED_USERS_RESPONSES, UPDATE_ME_RESPONSES, UPDATE_MY_AVATAR_RESPONSES, BLACKLIST_USER_RESPONSES
from app.common.swagger.responses.users.delete_me import DELETE_ME_RESPONSES
from app.core.ouath.main import get_current_user, oauth2_scheme
from app.database.main import get_database
from app.exception.body import APIRequestValidationException
from app.models.common.exceptions.body import RequestValidationDetails
from app.models.common.responses.blacklist import BlockOrUnblockUserResponseModel
from app.models.dialog.dialog import DialogModel
from app.models.socket.utils import SendBlockedMessageToClient
from app.models.user.blacklist import BlacklistInCreateModel, BlacklistedUserInResponseModel
from app.models.user.sessions import UserSessionInResponseModel, UserSessionTypesEnum
from app.models.user.user import UserModel, UserInUpdateModel, UserInResponseModel
from app.services.dialog.dialog import DialogService
from app.services.dialog.message import DialogMessageService
from app.services.image.image import ImageService
from app.services.user.blacklist import BlacklistService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService
from app.services.websocket.socket import socket_service, SocketSendTypesEnum

router = APIRouter()


@router.get(
    path="/me",
    responses=GET_ME_RESPONSES
)
async def get_me(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> UserInResponseModel:
    """
    Returns current user.

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    return await UserService.build_user_response(current_user, db)


@router.get(
    path="/me/sessions",
    responses=GET_MY_SESSIONS_RESPONSES
)
async def get_my_sessions(
        current_user: UserModel = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),
) -> list[UserSessionInResponseModel]:
    """
    Returns current user sessions.

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    # sessions = [session for session in current_user.sessions if session.type != UserSessionTypesEnum.TEST]
    sessions = []
    for session in current_user.sessions:
        if session.type != UserSessionTypesEnum.TEST:
            session_model = UserSessionInResponseModel(current=session.token == token, **session.dict())
            sessions.append(session_model)

    return sessions


@router.get(
    path="/me/blacklist",
    responses=GET_MY_BLOCKED_USERS_RESPONSES
)
async def get_my_blocked_users(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> list[BlacklistedUserInResponseModel]:
    result = []

    for blacklist_model in current_user.blacklist:
        blacklisted_user = await BlacklistService.build_blacklisted_user(blacklist_model.blacklisted_user_id, db)

        if blacklisted_user is None:
            continue

        result.append(blacklisted_user)

    return result


@router.put(
    path="/me",
    responses=UPDATE_ME_RESPONSES
)
async def update_me(
        body: UserInUpdateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> object:
    """
    Update current user.

    **User fields that can be updated:**
    * **email**: Email (string, min length: 3, max length: 25)
    * **firstName**: First name (string, min length: 3, max length: 25)
    * **lastName**: Last name (string, max length: 25)

    **Settings fields that can be updated:**
    * **twoFactorEnabled**: Two factor authentication enabled (boolean)
    * **theme**: Theme (string "light" or "dark")
    * **language**: Language (string "et", "en" or "ru")
    * **chatsNotificationsEnabled**: Chats notifications enabled (boolean)
    * **conversationsNotificationsEnabled**: Conversations notifications enabled (boolean)
    * **groupsNotificationsEnabled**: Groups notifications enabled (boolean)
    * **chatsSoundEnabled**: Chats sound enabled (boolean)
    * **conversationsSoundEnabled**: Conversations sound enabled (boolean)
    * **groupsSoundEnabled**: Groups sound enabled (boolean)
    * **lastActivityMode**: Last activity mode (boolean)

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    # Find key in body that exist in the UserModel
    for key, value in body.dict(exclude_unset=True).items():

        # Find key in UserModel
        if hasattr(current_user, key):
            setattr(current_user, key, value)

        # Find key in UserSettingsModel
        elif hasattr(current_user.settings, key):
            setattr(current_user.settings, key, value)

    await UserService.update(current_user, db)

    return body.dict(exclude_unset=True, by_alias=True)


@router.put(
    path="/me/avatar",
    responses=UPDATE_MY_AVATAR_RESPONSES
)
async def update_avatar(
        file: Union[UploadFile, bytes] = File(..., content_type="image/png, image/jpeg, image/jpg"),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> object:
    """
    Update current user avatar.

    * Allowed file types: **jpg, jpeg, png**
    * Max file size: **5MB**

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    max_file_size = 1024 * 1024 * 5  # 5 MB
    allowed_extensions = ["jpg", "jpeg", "png"]

    # Allow to add image from bytes array.
    if isinstance(file, bytes):
        filename = await ImageService.upload_bytes_image(file, "avatars")

        current_user.photo_url = filename
        await ImageService.delete_image(current_user.photo_url, "avatars")
        await UserService.update(current_user, db)

        return {"photoURL": filename}

    error = None
    if file.filename.split(".")[-1] not in allowed_extensions:
        error = RequestValidationDetails(
            location="file",
            message="Invalid file type.",
            translation="invalidFileType",
            field="file"
        )

    if len(await file.read()) > max_file_size:
        error = RequestValidationDetails(
            location="file",
            message="File is too large.",
            translation="fileIsTooLarge",
            field="file"
        )

    if error:
        raise APIRequestValidationException.from_details([error])

    await ImageService.delete_image(current_user.photo_url, "avatars")
    await UserService.update_avatar(file, current_user, db)

    return {"photoURL": current_user.photo_url}


@router.post(
    path="/blacklist",
    responses=BLACKLIST_USER_RESPONSES
)
async def block_or_unblock_user(
        body: BlacklistInCreateModel,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> BlockOrUnblockUserResponseModel:
    """
    Block or unblock user.

    * **blacklistedUserId**: Blacklisted user ID

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

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
    path="/me",
    responses=DELETE_ME_RESPONSES
)
async def delete_me(
        response: Response,
        token: str = Depends(oauth2_scheme),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
) -> None:
    """
    Delete current user.

    **Note**: This endpoint is protected by OAuth2 scheme. It requires a valid access token to be sent in the **Authorization** header or cookie.
    """

    token = token.replace("Bearer ", "")
    await UserSessionService.delete(current_user, token, db)

    dialogs = await DialogService.get_by_user_id(current_user.id, db)

    response.delete_cookie(key="Authorization")

    for dialog in dialogs:
        recipient = dialog.from_user if dialog.from_user.id != current_user.id else dialog.to_user
        socket_service.emit_to_user(SocketSendTypesEnum.DELETE_DIALOG, recipient.id, {"dialogId": dialog.id})

    socket_service.emit_to_user(SocketSendTypesEnum.DELETE_USER, current_user.id, {})

    connections = socket_service.find_connections_by_user_id(current_user.id)
    if not connections:
        return None

    for connection in connections:
        socket_service.disconnect(connection.websocket)

    await DialogService.delete_all_dialogs(current_user.id, db)
    await DialogMessageService.delete_all_messages(current_user.id, db)

    await UserService.delete(current_user, db)

    return None
