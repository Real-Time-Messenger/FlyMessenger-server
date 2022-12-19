from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.dialog.dialog import DialogInResponseModel
from app.models.user.user import UserInSearchModel


class SearchResultModel(BaseModel):
    dialogs: list[DialogInResponseModel] = Field(default_factory=list)
    messages: list[DialogInResponseModel] = Field(default_factory=list)
    users: list[UserInSearchModel] = Field(default_factory=list)

    class Config:
        json_encoders = {
            ObjectId: str
        }