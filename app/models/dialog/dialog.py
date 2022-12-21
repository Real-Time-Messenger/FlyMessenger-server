from datetime import datetime
from typing import Union

from pydantic import Field, BaseModel

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId
from app.models.dialog.messages import DialogMessageInResponseModel


class DialogInCreateModel(MongoModel):
    to_user_id: PyObjectId = Field(..., alias="toUserId")


class UserInDialogCreateModel(MongoModel):
    id: PyObjectId = Field(..., alias="_id")
    is_notifications_enabled: bool = Field(default=True, alias="isNotificationsEnabled")
    is_sound_enabled: bool = Field(default=True, alias="isSoundEnabled")
    is_pinned: bool = Field(default=False, alias="isPinned")


class DialogModel(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    from_user: UserInDialogCreateModel = Field(..., alias="fromUser")
    to_user: UserInDialogCreateModel = Field(..., alias="toUser")


class UserInDialogResponseModel(MongoModel):
    id: PyObjectId = Field(...)
    username: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: Union[str, None] = Field(default=None, alias="lastName")
    photo_url: Union[str, None] = Field(alias="photoURL")
    is_blocked: bool = Field(default=False, alias="isBlocked")
    last_activity: Union[datetime, None] = Field(default=None, alias="lastActivity")

class UserInLastMessageModel(MongoModel):
    id: PyObjectId = Field(...)


class LastMessageInDialogModel(MongoModel):
    id: PyObjectId = Field(...)
    text: Union[str, None] = Field()
    file: Union[str, None] = Field()
    sent_at: datetime = Field(alias="sentAt")
    is_read: bool = Field(default=False, alias="isRead")
    sender: UserInLastMessageModel = Field(...)

class DialogInResponseModel(MongoModel):
    id: PyObjectId = Field(...)
    label: str = Field(...)
    user: UserInDialogResponseModel = Field(...)
    images: list[str] = Field(default_factory=list)
    unread_messages: int = Field(default=0, alias="unreadMessages")
    is_pinned: bool = Field(default=False, alias="isPinned")
    is_notifications_enabled: bool = Field(default=True, alias="isNotificationsEnabled")
    is_sound_enabled: bool = Field(default=True, alias="isSoundEnabled")
    last_message: Union[LastMessageInDialogModel, None] = Field(None, alias="lastMessage")
    messages: Union[list[DialogMessageInResponseModel], None] = Field(None)
    is_me_blocked: bool = Field(default=False, alias="isMeBlocked")


class DialogInUpdateModel(MongoModel):
    is_pinned: Union[bool, None] = Field(alias="isPinned")
    is_sound_enabled: Union[bool, None] = Field(alias="isSoundEnabled")
    is_notifications_enabled: Union[bool, None] = Field(alias="isNotificationsEnabled")

    class Config:
        allow_population_by_field_name = True