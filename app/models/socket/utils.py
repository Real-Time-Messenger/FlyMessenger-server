from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class SendBlockedMessageToClient(MongoModel):
    """ Model for send blocked message to client. """

    user_id: PyObjectId = Field(..., alias="userId")
    is_blocked: bool = Field(..., alias="isBlocked")
