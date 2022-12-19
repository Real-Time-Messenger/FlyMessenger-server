from enum import Enum
from typing import Union

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from starlette.websockets import WebSocket

from app.models.common.object_id import PyObjectId
from app.services.token.token import TokenService
from app.services.user.blacklist import BlacklistService
from app.services.user.user import UserService


class SocketReceiveTypesEnum(str, Enum):
    SEND_MESSAGE = "SEND_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    TOGGLE_ONLINE_STATUS = "TOGGLE_ONLINE_STATUS",
    TYPING = "TYPING"
    UNTYPING = "UNTYPING",
    DESTROY_SESSION = "DESTROY_SESSION"


class SocketSendTypesEnum(str, Enum):
    RECEIVE_MESSAGE = "RECEIVE_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    TOGGLE_ONLINE_STATUS = "TOGGLE_ONLINE_STATUS"
    TYPING = "TYPING"
    UNTYPING = "UNTYPING"
    USER_BLOCKED = "USER_BLOCKED"
    USER_LOGOUT = "USER_LOGOUT"


class ConnectionModel(BaseModel):
    """ Model for connected websocket. """

    token: str
    user_id: PyObjectId
    websocket: WebSocket

    class Config:
        arbitrary_types_allowed = True


class SocketBase:
    """ Base class service for websocket worker. """

    connections: list[ConnectionModel] = []

    async def accept(self, websocket: WebSocket, authorization: str) -> None:
        """
        Accept a new websocket connection.

        :param websocket: Websocket to accept.
        :param authorization: Authorization header.
        """

        await websocket.accept()

        token = authorization.replace("Bearer ", "")
        user_id = TokenService.decode(token).get("payload").get("id")

        if not user_id: return

        self.connections.append(ConnectionModel(token=token, websocket=websocket, user_id=user_id))

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnect the websocket.

        :param websocket: Websocket to disconnect.
        :return: None
        """

        for connection in self.connections:
            if connection.websocket == websocket:
                self.connections.remove(connection)
                break

    def find_connection(self, user_id: PyObjectId) -> Union[ConnectionModel, None]:
        """
        Find connection by user id.

        :param user_id: User id.
        :return: ConnectionModel or None (if connection not found).
        """

        for connection in self.connections:
            if connection.user_id == user_id:
                return connection

        return None

    def find_connections_by_user_id(self, user_id: PyObjectId) -> Union[list[ConnectionModel], list]:
        """
        Find connection by user id.

        :param user_id: User id.
        :return: ConnectionModel or None (if connection not found).
        """

        connections = []

        for connection in self.connections:
            if connection.user_id == user_id:
                connections.append(connection)

        return connections

    async def _send_global_message(self, message: dict) -> None:
        """
        Send message to all connected users.

        :param message: Message to send.
        :return: None
        """

        for connection in self.connections:

            # Try to send message to user.
            try:
                await connection.websocket.send_json(jsonable_encoder(message))
            except Exception:

                # If an error occurred, disconnect the user.
                await self.disconnect(connection.websocket)

    async def _send_personal_message(self, user_ids: list[PyObjectId], message: dict) -> None:
        """
        Send message to specific users.

        :param message: Message to send.
        :param user_ids: The list of user IDs to send the message to.
        :return: None
        """

        for user_id in user_ids:
            await self._send_message(message, user_id=user_id)

    async def _send_message(self, message: dict, **kwargs) -> None:
        user_id = kwargs.get("user_id")

        connections = self.find_connections_by_user_id(user_id)
        for connection in connections:
            try:
                await connection.websocket.send_json(jsonable_encoder(message))
            except Exception:
                await self.disconnect(connection.websocket)

    async def send_message_by_websocket(self, websocket: WebSocket, message: dict) -> None:
        """
        Send message to specific websocket.

        :param websocket: Websocket to send message.
        :param message: Message to send.
        :return: None
        """

        await websocket.send_json(jsonable_encoder(message))

    async def _send_message_to_user_id(self, message: dict, user_id: PyObjectId) -> None:
        """
        Send message to specific user.

        :param message: Message to send.
        :param user_id: User ID to send the message to.
        :return: None
        """
        connections = self.find_connections_by_user_id(user_id)

        for connection in connections:
            try:
                await connection.websocket.send_json(jsonable_encoder(message))

            except Exception:
                await self.disconnect(connection.websocket)

    async def emit_to_user(self, event_type: SocketSendTypesEnum, user_ids: Union[list[PyObjectId], PyObjectId], message: dict) -> None:
        """
        Send message to specific user.

        :param event_type: Type of event message.
        :param user_ids: The list of user IDs to send the message to.
        :param message: Message to send.
        :return: None
        """

        if not isinstance(user_ids, list):
            user_ids = [user_ids]

        await self._send_personal_message(user_ids, {
            "type": event_type,
            **message
        })

    async def check_if_user_can_send_message(self, user_id: PyObjectId, recipient_id: PyObjectId,
                                             db: AsyncIOMotorClient) -> bool:
        current_user = await UserService.get_by_id(user_id, db)
        is_user_blocked_from_current_user = await BlacklistService.get_user_in_blacklist(recipient_id, current_user)
        if is_user_blocked_from_current_user:
            return False

        recipient = await UserService.get_by_id(recipient_id, db)
        is_user_blocked_from_recipient = await BlacklistService.get_user_in_blacklist(user_id, recipient)
        if is_user_blocked_from_recipient:
            return False

        return True