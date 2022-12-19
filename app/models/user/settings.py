from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class ThemesEnum(str, Enum):
    LIGHT = "light"
    DARK = "dark"


class LanguagesEnum(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    ESTONIAN = "et"


class NotificationsPositionsEnum(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class LastActivityModesEnum(str, Enum):
    ALL = "all"
    FRIENDS = "friends"
    NOBODY = "nobody"


class UserSettingsModel(MongoModel):
    two_factor_enabled: bool = Field(default=False, alias="twoFactorEnabled")

    theme: ThemesEnum = Field(default=ThemesEnum.LIGHT)

    language: LanguagesEnum = Field(default=LanguagesEnum.ESTONIAN)

    chats_notifications_enabled: bool = Field(default=False, alias="chatsNotificationsEnabled")
    conversations_notifications_enabled: bool = Field(default=False, alias="conversationsNotificationsEnabled")
    groups_notifications_enabled: bool = Field(default=False, alias="groupsNotificationsEnabled")

    chats_sound_enabled: bool = Field(default=False, alias="chatsSoundEnabled")
    conversations_sound_enabled: bool = Field(default=False, alias="conversationsSoundEnabled")
    groups_sound_enabled: bool = Field(default=False, alias="groupsSoundEnabled")

    notification_position: NotificationsPositionsEnum = Field(default=NotificationsPositionsEnum.BOTTOM_RIGHT, alias="notificationPosition")

    is_display_name_visible: bool = Field(default=True, alias="isDisplayNameVisible")
    is_email_visible: bool = Field(default=True, alias="isEmailVisible")

    last_activity_mode: bool = Field(default=True, alias="lastActivityMode")

    allow_message_forwards: bool = Field(default=True, alias="allowMessageForwards")
    allow_invites: bool = Field(default=True, alias="allowInvites")
    allow_run_on_startup: bool = Field(default=True, alias="allowRunOnStartup")


class UserSettingsUpdateModel(MongoModel):
    two_factor_enabled: bool | None = Field(alias="twoFactorEnabled")

    theme: ThemesEnum | None = Field()

    language: LanguagesEnum | None = Field()

    chats_notifications_enabled: bool | None = Field(alias="chatsNotificationsEnabled")
    conversations_notifications_enabled: bool | None = Field(alias="conversationsNotificationsEnabled")
    groups_notifications_enabled: bool | None = Field(alias="groupsNotificationsEnabled")

    chats_sound_enabled: bool | None = Field(alias="chatsSoundEnabled")
    conversations_sound_enabled: bool | None = Field(alias="conversationsSoundEnabled")
    groups_sound_enabled: bool | None = Field(alias="groupsSoundEnabled")

    notification_position: NotificationsPositionsEnum | None = Field(alias="notificationPosition")

    is_display_name_visible: bool | None = Field(alias="isDisplayNameVisible")
    is_email_visible: bool | None = Field(alias="isEmailVisible")

    last_activity_mode: bool | None = Field(alias="lastActivityMode")

    allow_message_forwards: bool | None = Field(alias="allowMessageForwards")
    allow_invites: bool | None = Field(alias="allowInvites")

    allow_run_on_startup: bool | None = Field(alias="allowRunOnStartup")