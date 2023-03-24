from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId
from app.models.dialog.messages import DialogMessageInResponseModel


class DialogInCreateModel(MongoModel):
    """ Model for create dialog. """

    to_user_id: PyObjectId = Field(..., alias="toUserId")


class UserInDialogModel(MongoModel):
    """ Model for user in dialog. """

    id: PyObjectId = Field(..., alias="_id")
    is_notifications_enabled: bool = Field(default=True, alias="isNotificationsEnabled")
    is_sound_enabled: bool = Field(default=True, alias="isSoundEnabled")
    is_pinned: bool = Field(default=False, alias="isPinned")


class DialogModel(MongoModel):
    """ Base model for dialog. """

    id: PyObjectId = Field(default_factory=PyObjectId)
    from_user: UserInDialogModel = Field(..., alias="fromUser")
    to_user: UserInDialogModel = Field(..., alias="toUser")


class UserInDialogResponseModel(MongoModel):
    """ Response model for user in dialog. """

    id: PyObjectId = Field(...)
    username: str = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    photo_url: Optional[str] = Field(alias="photoURL")
    is_blocked: bool = Field(default=False, alias="isBlocked")
    is_online: Optional[bool] = Field(default=False, alias="isOnline")
    last_activity: Optional[datetime] = Field(default=None, alias="lastActivity")


class UserInLastMessageModel(MongoModel):
    """ Model for user in last message. """

    id: PyObjectId = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    photo_url: Optional[str] = Field(alias="photoURL")


class LastMessageInDialogModel(MongoModel):
    """ Model for last message in dialog. """

    id: PyObjectId = Field(...)
    text: Optional[str] = Field()
    file: Optional[str] = Field()
    sent_at: datetime = Field(alias="sentAt")
    is_read: bool = Field(default=False, alias="isRead")
    sender: UserInLastMessageModel = Field(...)


class DialogInResponseModel(MongoModel):
    """ Response model for dialog. """

    id: PyObjectId = Field(...)
    user: UserInDialogResponseModel = Field(...)
    images: list[str] = Field(default_factory=list)
    unread_messages: int = Field(default=0, alias="unreadMessages")
    is_pinned: bool = Field(default=False, alias="isPinned")
    is_notifications_enabled: bool = Field(default=True, alias="isNotificationsEnabled")
    is_sound_enabled: bool = Field(default=True, alias="isSoundEnabled")
    last_message: Optional[LastMessageInDialogModel] = Field(None, alias="lastMessage")
    messages: Optional[list[DialogMessageInResponseModel]] = Field(None)
    is_me_blocked: bool = Field(default=False, alias="isMeBlocked")


class DialogInUpdateModel(MongoModel):
    """ Model for update dialog. """

    is_pinned: Optional[bool] = Field(alias="isPinned")
    is_sound_enabled: Optional[bool] = Field(alias="isSoundEnabled")
    is_notifications_enabled: Optional[bool] = Field(alias="isNotificationsEnabled")
