from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserInResponseModel


class BlockOrUnblockUserResponseModel(MongoModel):
    """ Response model for block or unblock user. """

    user_id: PyObjectId = Field(..., alias="userId")
    is_blocked: bool = Field(..., alias="isBlocked")
    blacklist: list[BlacklistedUserInResponseModel] = Field(..., alias="blacklist")