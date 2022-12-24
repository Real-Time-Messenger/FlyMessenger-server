from bson import ObjectId
from pydantic import BaseModel, Field


class TokenInCreateModel(BaseModel):
    """ Model for token in create. """

    exp: float = Field(...)
    iat: float = Field(...)
    payload: dict = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }