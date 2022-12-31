from datetime import datetime
from typing import Union, Optional

from pydantic import Field, constr, BaseModel

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class DialogMessageInCreateModel(MongoModel):
    """ Model for create dialog message. """

    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender_id: PyObjectId = Field(..., alias="senderId")
    text: Optional[str] = Field()
    file: Optional[str] = Field()

    # TODO: Test it
    # class Config:
    #     anystr_strip_whitespace = True


class SenderInDialogMessageModel(MongoModel):
    """ Model for sender in dialog message. """

    id: PyObjectId = Field(...)
    username: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    photo_url: Optional[str] = Field(alias="photoURL")


class DialogMessageModel(MongoModel):
    """ Base model for dialog message. """

    id: PyObjectId = Field(default_factory=PyObjectId)
    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender_id: PyObjectId = Field(..., alias="senderId")
    text: Optional[str] = Field(None)
    file: Optional[str] = Field(None)
    is_read: bool = Field(default=False, alias="isRead")
    sent_at: datetime = Field(default=str(datetime.now(tz=None).isoformat()), alias="sentAt")


class DialogMessageInResponseModel(MongoModel):
    """ Response model for dialog message. """

    id: PyObjectId = Field(...)
    dialog_id: PyObjectId = Field(..., alias="dialogId")
    sender: SenderInDialogMessageModel = Field(...)
    text: Optional[constr(curtail_length=1000, strip_whitespace=False)] = Field()
    file: Optional[str] = Field()
    is_read: bool = Field(default=False, alias="isRead")
    sent_at: datetime = Field(..., alias="sentAt")
