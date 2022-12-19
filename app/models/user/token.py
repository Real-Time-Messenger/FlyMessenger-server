from datetime import datetime, timedelta

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common.object_id import PyObjectId


class TokenModel(BaseModel):
    token: str = Field(...)


class TokenInCreateModel(BaseModel):
    exp: float = Field(...)
    iat: float = Field(...)
    payload: dict = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }