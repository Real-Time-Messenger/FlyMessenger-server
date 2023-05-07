import asyncio
import json
from typing import Optional

from aiocache import cached
from aiocache.serializers import PickleSerializer
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.websockets import WebSocket

from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInCreateModel
from app.models.dialog.messages import DialogMessageInCreateModel
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
        recipient_id = PyObjectId(json_data.get("recipientId"))
        dialog_id = PyObjectId(json_data.get("dialogId"))

        if user_type == SocketReceiveTypesEnum.SEND_MESSAGE:
            text = json_data.get("text")
            file = json_data.get("file")

            if not text and not file: return

            await self._handle_send_message(user_id, dialog_id, recipient_id, text, file, db)

        elif user_type == SocketReceiveTypesEnum.READ_MESSAGE:
            message_id = PyObjectId(json_data.get("messageId"))

            await self._handle_read_message(message_id, user_id, recipient_id, dialog_id, db)

        elif user_type == SocketReceiveTypesEnum.TOGGLE_ONLINE_STATUS:
            status = json_data.get("status")

            await self._handle_toggle_online_status(user_id, status, db)

        elif user_type == SocketReceiveTypesEnum.TYPING:
            await self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.TYPING,
                "dialogId": str(dialog_id),
            }, recipient_id)

        elif user_type == SocketReceiveTypesEnum.UNTYPING:
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

            user = await UserService.get_by_id__uncached(user_id, db)
            user.sessions.remove(session)

            connection = self.find_connection_by_token(session.token)
            if not connection:
                await UserSessionService.delete(user, session.token, db)
                return

            await UserService.update(user, db)

            # Send message to user about destroying session.
            await connection.websocket.send_json({
                "type": SocketSendTypesEnum.USER_LOGOUT,
                "currentSessionId": str(connection.token),
                "sessionId": str(session.token),
            })

            sessions = await UserSessionService.build_sessions(user_id, token, db)

            # Send message to websocket user about successful destroying session.
            await self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.USER_LOGOUT,
                "success": True,
                "sessions": sessions
            }, user_id)

    @cached(ttl=30, serializer=PickleSerializer())
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
            recipient_id: PyObjectId,
            text: str,
            file: dict,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle send message event.

        :param user_id: User ID.
        :param dialog_id: Dialog ID.
        :param recipient_id: Recipient ID.
        :param text: Message text.
        :param file: Message file.
        :param db: Database connection.
        """

        is_dialog_exist = await DialogService.get_by_id(dialog_id, db)

        if is_dialog_exist is None:
            body = DialogInCreateModel(to_user_id=recipient_id)
            current_user = await UserService.get_by_id__uncached(user_id, db)
            new_dialog = await DialogService.create(body, current_user, db)
            dialog_id = new_dialog.id

        can_send_message = await self.check_if_user_can_send_message(user_id, recipient_id, db)
        if not can_send_message:
            return

        filename = None
        if file:
            filename = await ImageService.upload_base64_image(file, "uploads")

        new_message_payload = DialogMessageInCreateModel(
            sender_id=user_id,
            dialog_id=dialog_id,
            text=text,
            file=filename,
        )
        new_message = await DialogMessageService.create(new_message_payload, db)

        current_user, recipient = await asyncio.gather(
            UserService.get_by_id(user_id, db),
            UserService.get_by_id(recipient_id, db)
        )

        dialog, recipient_dialog = await asyncio.gather(
            DialogService.get_by_id(dialog_id, db),
            DialogService.get_by_id(dialog_id, db)
        )

        dialog, recipient_dialog = await asyncio.gather(
            DialogService.build_dialog(dialog, current_user, db),
            DialogService.build_dialog(recipient_dialog, recipient, db)
        )

        dialog.messages = []
        recipient_dialog.messages = []

        dialog_data = {
            "isNotificationsEnabled": dialog.is_notifications_enabled,
            "isSoundEnabled": dialog.is_sound_enabled
        }

        recipient_dialog_data = {
            "isNotificationsEnabled": recipient_dialog.is_notifications_enabled,
            "isSoundEnabled": recipient_dialog.is_sound_enabled
        }

        await asyncio.gather(
            self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.RECEIVE_MESSAGE,
                "message": await DialogMessageService.build_message(new_message, db),
                "dialog": dialog,
                "dialogData": dialog_data,
                "userId": str(user_id),
            }, user_id),
            self._send_personal_message_by_user_id({
                "type": SocketSendTypesEnum.RECEIVE_MESSAGE,
                "message": await DialogMessageService.build_message(new_message, db),
                "dialog": recipient_dialog,
                "dialogData": recipient_dialog_data,
                "userId": str(user_id),
            }, recipient_id)
        )

    async def _handle_read_message(
            self,
            message_id: PyObjectId,
            user_id: PyObjectId,
            recipient_id: PyObjectId,
            dialog_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> None:
        """
        Handle read message event.

        :param message_id: Message ID.
        :param user_id: User ID.
        :param recipient_id: Recipient ID.
        :param dialog_id: Dialog ID.
        :param db: Database connection.
        """

        message = await DialogMessageService.read_message(message_id, dialog_id, db)
        if not message:
            return

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
