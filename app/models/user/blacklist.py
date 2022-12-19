from datetime import datetime

from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class BlacklistedUserModel(MongoModel):
    """ Base model for blacklisted users. """

    blacklisted_user_id: PyObjectId = Field(..., alias="blacklistedUserId")
    blocked_at: datetime = Field(default=datetime.utcnow(), alias="blockedAt")


class BlacklistInCreateModel(MongoModel):
    """ Create model for blacklisted users. """

    blacklisted_user_id: PyObjectId = Field(..., alias="blacklistedUserId")


class BlacklistedUserInResponseModel(MongoModel):
    """ Response model for blacklisted users. """

    id: PyObjectId = Field(...)
    username: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    photo_url: str | None = Field(alias="photoURL")