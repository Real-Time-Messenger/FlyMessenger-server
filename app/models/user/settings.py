from typing import Optional

from pydantic import Field

from app.common.types.str_enum import StrEnumBase
from app.models.common.mongo.base_model import MongoModel


class ThemesEnum(StrEnumBase):
    """ UI themes enum. """
    LIGHT = "light"
    DARK = "dark"


class LanguagesEnum(StrEnumBase):
    """ UI languages enum. """

    ENGLISH = "en"
    RUSSIAN = "ru"
    ESTONIAN = "et"


class UserSettingsModel(MongoModel):
    """ Base model for user settings. """

    two_factor_enabled: bool = Field(default=False, alias="twoFactorEnabled")

    theme: ThemesEnum = Field(default=ThemesEnum.LIGHT)

    language: LanguagesEnum = Field(default=LanguagesEnum.ENGLISH)

    chats_notifications_enabled: bool = Field(default=False, alias="chatsNotificationsEnabled")
    conversations_notifications_enabled: bool = Field(default=False, alias="conversationsNotificationsEnabled")
    groups_notifications_enabled: bool = Field(default=False, alias="groupsNotificationsEnabled")

    chats_sound_enabled: bool = Field(default=False, alias="chatsSoundEnabled")
    conversations_sound_enabled: bool = Field(default=False, alias="conversationsSoundEnabled")
    groups_sound_enabled: bool = Field(default=False, alias="groupsSoundEnabled")

    last_activity_mode: bool = Field(default=True, alias="lastActivityMode")

    allow_run_on_startup: bool = Field(default=True, alias="allowRunOnStartup")

class UserSettingsUpdateModel(MongoModel):
    """ Model for updating user settings. """

    two_factor_enabled: Optional[bool] = Field(None, alias="twoFactorEnabled")

    theme: Optional[ThemesEnum] = Field(None)

    language: Optional[LanguagesEnum] = Field(None)

    chats_notifications_enabled: Optional[bool] = Field(None, alias="chatsNotificationsEnabled")
    conversations_notifications_enabled: Optional[bool] = Field(None, alias="conversationsNotificationsEnabled")
    groups_notifications_enabled: Optional[bool] = Field(None, alias="groupsNotificationsEnabled")

    chats_sound_enabled: Optional[bool] = Field(None, alias="chatsSoundEnabled")
    conversations_sound_enabled: Optional[bool] = Field(None, alias="conversationsSoundEnabled")
    groups_sound_enabled: Optional[bool] = Field(None, alias="groupsSoundEnabled")
