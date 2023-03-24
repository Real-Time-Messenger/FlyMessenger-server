from datetime import datetime
from typing import Optional

from pydantic import Field

from app.common.types.str_enum import StrEnumBase
from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class UserSessionTypesEnum(StrEnumBase):
    """ User session types enum. """

    WEB = "web"
    DESKTOP = "desktop",
    TEST = "test"
    UNKNOWN = "unknown"


class UserSessionModel(MongoModel):
    """ Base model for user sessions. """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    token: str = Field(...)
    ip_address: str = Field(alias="ipAddress")
    label: str = Field(...)
    type: UserSessionTypesEnum = Field(...)
    location: str = Field(...)
    created_at: datetime = Field(default=datetime.utcnow(), alias="createdAt")


class UserSessionInResponseModel(MongoModel):
    """ Response model for user sessions. """

    id: PyObjectId = Field(...)
    ip_address: str = Field(alias="ipAddress")
    label: str = Field(...)
    type: UserSessionTypesEnum = Field(...)
    location: str = Field(...)
    current: Optional[bool] = Field(False)
    created_at: datetime = Field(..., alias="createdAt")