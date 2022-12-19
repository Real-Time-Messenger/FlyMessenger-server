from datetime import datetime

from pydantic import Field, constr
from pydantic.validators import max_str_int

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class DialogMessageInCreateModel(MongoModel):
    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender_id: PyObjectId = Field(..., alias="senderId")
    text: str | None = Field()
    file: str | None = Field()

    class Config:
        anystr_strip_whitespace = True


class SenderInDialogMessageModel(MongoModel):
    id: PyObjectId = Field(...)
    username: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    photo_url: str | None = Field(alias="photoURL")


class DialogMessageModel(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender_id: PyObjectId = Field(..., alias="senderId")
    text: str | None = Field(None)
    file: str | None = Field(None)
    is_read: bool = Field(default=False, alias="isRead")
    sent_at: datetime = Field(default=str(datetime.now(tz=None).isoformat()), alias="sentAt")


class DialogMessageInResponseModel(MongoModel):
    id: PyObjectId = Field(...)
    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender: SenderInDialogMessageModel = Field(...)
    text: constr(curtail_length=1000) | None = Field()
    file: str | None = Field()
    is_read: bool = Field(default=False, alias="isRead")
    sent_at: datetime = Field(..., alias="sentAt")