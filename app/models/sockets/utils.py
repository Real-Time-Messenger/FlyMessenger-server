from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserInResponseModel


class SendBlockedMessageToClient(BaseModel):
    user_id: PyObjectId = Field(..., alias="userId")
    is_blocked: bool = Field(..., alias="isBlocked")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }