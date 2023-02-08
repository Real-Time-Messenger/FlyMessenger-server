import json
from typing import Optional

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.websockets import WebSocket

from app.models.common.object_id import PyObjectId
from app.models.dialog.messages import DialogMessageInCreateModel
from app.models.user.user import UserInResponseModel
from app.services.dialog.dialog import DialogService
from app.services.dialog.message import DialogMessageService
from app.services.image.image import ImageService
from app.services.token.token import TokenService
from app.services.user.online_status import UserOnlineStatusService
from app.services.user.sessions import UserSessionService
from app.services.user.user import UserService
from app.services.websocket.base import SocketBase, SocketReceiveTypesEnum, SocketSendTypesEnum


class SocketService(SocketBase):
    """
    Websocket service.

    This service is responsible for handling websocket connections and sending messages to users.
    """

    async def handle_connection(
            self,
            websocket: WebSocket,
            message: str,
            token: str,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle websocket connection and socket events.

        :param websocket: Websocket connection.
        :param message: Message from client.
        :param token: Token from client.
        :param db: Database connection.
        """

        if not token:
            await websocket.close()
            return

        json_data = json.loads(message)
        user_type = json_data.get("type", "Type")
        user_id = PyObjectId(TokenService.decode(token).get("payload").get("id"))
        dialog_id = PyObjectId(json_data.get("dialogId"))

        if user_type == SocketReceiveTypesEnum.SEND_MESSAGE:
            text = json_data.get("text")
            file = json_data.get("file")

            if not text and not file: return

            await self._handle_send_message(user_id, dialog_id, text, file, db)

        elif user_type == SocketReceiveTypesEnum.READ_MESSAGE:
            message_id = json_data.get("messageId")

            await self._handle_read_message(PyObjectId(message_id), user_id, dialog_id, db)

        elif user_type == SocketReceiveTypesEnum.TOGGLE_ONLINE_STATUS:
            status = json_data.get("status")

            await self._handle_toggle_online_status(user_id, status, db)

        elif user_type == SocketReceiveTypesEnum.TYPING:
            recipient_id = await self._get_recipient_id(user_id, dialog_id, db)

            await self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.TYPING,
                "dialogId": str(dialog_id),
            }, recipient_id)

        elif user_type == SocketReceiveTypesEnum.UNTYPING:
            recipient_id = await self._get_recipient_id(user_id, dialog_id, db)

            await self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.UNTYPING,
                "dialogId": str(dialog_id),
            }, recipient_id)

        elif user_type == SocketReceiveTypesEnum.DESTROY_SESSION:
            current_session = await UserSessionService.get_by_token(token, db)
            if not current_session: return

            session_id = json_data.get("sessionId")
            session = await UserSessionService.get_by_id(PyObjectId(session_id), db)
            if not session: return

            user = await UserService.get_by_id(user_id, db)
            user.sessions.remove(session)

            built_user = await UserService.build_user_response(user, db)

            connection = self.find_connection_by_token(session.token)
            if not connection:
                await UserSessionService.delete(user, session.token, db)
                return

            # Send message to user about destroying session.
            await connection.websocket.send_json({
                "type": SocketSendTypesEnum.USER_LOGOUT,
                "currentSessionId": str(connection.token),
                "sessionId": str(session.token),
            })

            # Send message to websocket user about successful destroying session.
            await websocket.send_json({
                "type": SocketSendTypesEnum.USER_LOGOUT,
                "success": True,
                "user": jsonable_encoder(UserInResponseModel(**built_user.dict()))
            })

            await UserService.update(user, db)

    async def _get_recipient_id(
            self,
            user_id: PyObjectId,
            dialog_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> Optional[PyObjectId]:
        """
        Get recipient id.

        :param user_id: User id.
        :param dialog_id: Dialog id.
        :param db: Database connection.

        :return: Recipient id.
        """

        dialog = await DialogService.get_by_id(dialog_id, db)

        if not dialog:
            return None

        return dialog.from_user.id if dialog.from_user.id != user_id else dialog.to_user.id

    async def _handle_send_message(
            self,
            user_id: PyObjectId,
            dialog_id: PyObjectId,
            text: str,
            file: dict,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle send message event.

        :param user_id: User id.
        :param dialog_id: Dialog id.
        :param text: Message text.
        :param file: Message file.
        :param db: Database connection.
        """

        recipient_id = await self._get_recipient_id(user_id, dialog_id, db)

        is_user_can_send_message = await self.check_if_user_can_send_message(user_id, recipient_id, db)
        if not is_user_can_send_message:
            return

        filename = await ImageService.upload_base64_image(file, "uploads") if file else None

        new_message_payload = DialogMessageInCreateModel(
            sender_id=user_id,
            dialog_id=dialog_id,
            text=text,
            file=filename,
        )

        new_message = await DialogMessageService.create(new_message_payload, db)

        current_user = await UserService.get_by_id(user_id, db)

        dialog = await DialogService.get_by_id(dialog_id, db)
        dialog = await DialogService.build_dialog(dialog, current_user, db)
        dialog.messages = []

        dialog_data = {
            "isNotificationsEnabled": dialog.is_notifications_enabled,
            "isSoundEnabled": dialog.is_sound_enabled,
        }

        await self._send_personal_message_by_user_id({
            "type": SocketSendTypesEnum.RECEIVE_MESSAGE,
            "message": await DialogMessageService.build_message(new_message, db),
            "dialog": dialog,
            "dialogData": dialog_data,
            "userId": str(user_id),
        }, user_id, recipient_id)

    async def _handle_read_message(
            self,
            message_id: PyObjectId,
            user_id: PyObjectId,
            dialog_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle read message event.

        :param message_id: Message id.
        :param user_id: User id.
        :param dialog_id: Dialog id.
        :param db: Database connection.
        """

        message = await DialogMessageService.read_message(message_id, dialog_id, db)

        recipient_id = await self._get_recipient_id(user_id, dialog_id, db)

        await self._send_personal_message_by_user_id({
            "type": SocketSendTypesEnum.READ_MESSAGE,
            "messageId": str(message.id),
            "dialogId": str(dialog_id),
        }, user_id, recipient_id)

    async def _handle_toggle_online_status(
            self,
            user_id: PyObjectId,
            status: bool,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle toggle online status event.

        :param user_id: User id.
        :param status: Online status.
        :param db: Database connection.
        """

        user = await UserOnlineStatusService.toggle_online_status(user_id, status, db)
        if not user.settings.last_activity_mode:
            status = None

        await self._send_global_message({
            "type": SocketSendTypesEnum.TOGGLE_ONLINE_STATUS.value,
            "userId": str(user_id),
            "status": status,
            "lastActivity": user.last_activity,
        })


socket_service = SocketService()
