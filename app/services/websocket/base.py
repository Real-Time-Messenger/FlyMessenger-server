from enum import Enum
from typing import Union, Optional

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from starlette.websockets import WebSocket

from app.database.main import get_database
from app.models.common.exceptions.body import InvalidObjectId
from app.models.common.object_id import PyObjectId
from app.services.token.token import TokenService
from app.services.user.blacklist import BlacklistService
from app.services.user.online_status import UserOnlineStatusService
from app.services.user.user import UserService


class SocketReceiveTypesEnum(str, Enum):
    """ Types of received messages. """

    SEND_MESSAGE = "SEND_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    TOGGLE_ONLINE_STATUS = "TOGGLE_ONLINE_STATUS",
    TYPING = "TYPING"
    UNTYPING = "UNTYPING",
    DESTROY_SESSION = "DESTROY_SESSION"


class SocketSendTypesEnum(str, Enum):
    """ Types of sent messages. """

    RECEIVE_MESSAGE = "RECEIVE_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    TOGGLE_ONLINE_STATUS = "TOGGLE_ONLINE_STATUS"
    TYPING = "TYPING"
    UNTYPING = "UNTYPING"
    USER_BLOCKED = "USER_BLOCKED"
    USER_LOGOUT = "USER_LOGOUT"
    DELETE_DIALOG = "DELETE_DIALOG"


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

    async def accept(self, websocket: WebSocket, authorization: str) -> Optional[bool]:
        """
        Accept a new websocket connection.

        :param websocket: Websocket to accept.
        :param authorization: Authorization header.
        """

        await websocket.accept()
        # await websocket.send_json({"ping": "pong"})

        token = TokenService.decode(authorization)
        if token is None:
            return False

        user_id = token.get("payload", {}).get("id", "")
        if not user_id:
            return False

        try:
            user_id = PyObjectId.validate(user_id)
        except InvalidObjectId:
            return False

        connection = self.find_connection(user_id)
        if connection is None:
            self.connections.append(ConnectionModel(token=authorization, websocket=websocket, user_id=user_id))

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnect the websocket.

        :param websocket: Websocket to disconnect.
        :return: None
        """

        db = get_database()

        for connection in self.connections:
            if connection.websocket == websocket:
                self.connections.remove(connection)
                try:
                    await UserOnlineStatusService.toggle_online_status(connection.user_id, False, db)
                    await websocket.close()
                except Exception:
                    pass
                break

    def find_connection(self, user_id: PyObjectId) -> Optional[ConnectionModel]:
        """
        Find connection by user ID.

        :param user_id: User ID.
        :return: ConnectionModel or None (if connection not found).
        """

        for connection in self.connections:
            if connection.user_id == user_id:
                return connection

        return None

    def find_connections_by_user_id(self, user_id: PyObjectId) -> list[ConnectionModel]:
        """
        Find connection by user ID.

        :param user_id: User ID.

        :return: List of connections by user ID, or an empty list if no connections were found.
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
        """

        for connection in self.connections:

            # Try to send message to user.
            try:
                await connection.websocket.send_json(jsonable_encoder(message))
            except Exception:

                # If an error occurred, disconnect the user.
                await self.disconnect(connection.websocket)

    async def _send_personal_message_by_websocket(self, message: dict, *websockets) -> None:
        """
        Send message to specific users.

        :param message: Message to send.
        :param websockets: The list of websocket's to send the message to.
        """

        for websocket in websockets:
            await self._send_message(message, websocket=websocket)

    async def _send_personal_message_by_user_id(self, message: dict, *user_ids: PyObjectId) -> None:
        """
        Send message to specific users (all connections with the same user ID).

        :param message: Message to send.
        :param user_ids: The list of user ID's to send the message to.
        """

        for user_id in user_ids:
            await self._send_message_to_user_id(message, user_id=user_id)

    async def _send_message(self, message: dict, **kwargs) -> None:
        """
        Send message to specific user.

        :param message: Message to send.
        :param kwargs: Keyword arguments.
        """

        user_id = kwargs.get("user_id")
        websocket = kwargs.get("websocket")

        if user_id:
            connections = self.find_connection(user_id)
            for connection in connections:
                try:
                    await connection.websocket.send_json(jsonable_encoder(message))
                except Exception:
                    await self.disconnect(connection.websocket)
        elif websocket:
            try:
                await websocket.send_json(jsonable_encoder(message))
            except Exception:
                await self.disconnect(websocket)

    async def _send_message_to_user_id(self, message: dict, **kwargs) -> None:
        """
        Send message to specific user.

        :param message: Message to send.
        :param kwargs: Keyword arguments.
        """

        user_id = kwargs.get("user_id")

        connections = self.find_connections_by_user_id(user_id)
        for connection in connections:
            try:
                pass
                await connection.websocket.send_json(jsonable_encoder(message))
            except Exception:
                await self.disconnect(connection.websocket)

    async def emit_to_user(
            self,
            event_type: SocketSendTypesEnum,
            user_ids: Union[list[PyObjectId], PyObjectId],
            message: dict
    ) -> None:
        """
        Send message to specific user.

        :param event_type: Type of event message.
        :param user_ids: The list of user IDs to send the message to.
        :param message: Message to send.
        """

        if not isinstance(user_ids, list):
            user_ids = [user_ids]

        await self._send_personal_message_by_user_id({
            "type": event_type,
            **message
        }, *user_ids)

    async def check_if_user_can_send_message(
            self,
            user_id: PyObjectId,
            recipient_id: PyObjectId,
            db: AsyncIOMotorClient
    ) -> bool:
        """
        Check if the user can send a message to the recipient (if the recipient is not blocked).

        :param user_id: User ID.
        :param recipient_id: Recipient ID.
        :param db: Database connection.

        :return: True if the user can send a message to the recipient, False otherwise.
        """

        current_user = await UserService.get_by_id(user_id, db)
        if not current_user:
            return False

        is_user_blocked_from_current_user = await BlacklistService.get_user_in_blacklist(recipient_id, current_user)
        if is_user_blocked_from_current_user:
            return False

        recipient = await UserService.get_by_id(recipient_id, db)
        if not recipient:
            return False

        is_user_blocked_from_recipient = await BlacklistService.get_user_in_blacklist(user_id, recipient)
        if is_user_blocked_from_recipient:
            return False

        return True

    def find_connection_by_token(self, token: str) -> Optional[ConnectionModel]:
        """
        Find connection by token.

        :param token: Token.
        :return: ConnectionModel or None (if connection not found).
        """

        for connection in self.connections:
            if connection.token == token:
                return connection

        return None
