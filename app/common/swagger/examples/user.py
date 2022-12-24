from datetime import datetime

from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr

from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserInResponseModel
from app.models.user.sessions import UserSessionInResponseModel, UserSessionTypesEnum
from app.models.user.settings import UserSettingsModel, ThemesEnum, LanguagesEnum
from app.models.user.user import UserInResponseModel

# Sessions example model (for swagger).
SESSIONS_EXAMPLE = [
    UserSessionInResponseModel(
        id=PyObjectId("5f9b1b5b9b9b9b9b9b9b9b9b"),
        ip_address="127.0.0.1",
        label="Fly Messenger Web 0.1.0",
        location="Tallinn, Harjumaa, Estonia",
        type=UserSessionTypesEnum.WEB,
        created_at=datetime.now(tz=None)
    ),
    UserSessionInResponseModel(
        id=PyObjectId("5f9b1b5b9b9b9b9b9b9b9b9c"),
        ip_address="127.0.0.1",
        label="Fly Messenger Desktop 0.1.0",
        location="Narva, Ida-Virumaa, Estonia",
        type=UserSessionTypesEnum.DESKTOP,
        created_at=datetime.now(tz=None)
    ),
]

# Blacklist example model (for swagger).
BLACKLIST_EXAMPLE = [
    BlacklistedUserInResponseModel(
        id=PyObjectId("5f9b1b5b9b9b9b9b9b9b9b9d"),
        username="test",
        first_name="Test",
        last_name="Test",
        photo_url="https://example.com/photo.jpg"
    )
]

# Settings example model (for swagger).
SETTINGS_EXAMPLE = UserSettingsModel(
    two_factor_enabled=False,
    theme=ThemesEnum.LIGHT,
    language=LanguagesEnum.ENGLISH,
    chats_notifications_enabled=True,
    conversations_notifications_enabled=True,
    groups_notifications_enabled=True,
    chats_sound_enabled=True,
    conversations_sound_enabled=True,
    groups_sound_enabled=True,
    allow_run_on_startup=True,
    last_activity_mode=True
)

# User example model (for swagger).
USER_EXAMPLE = UserInResponseModel(
    id=PyObjectId("5f9f1b9b9c9d1b0b8c8b4567"),
    username="test",
    email=EmailStr("test@mail.ru"),
    first_name="Test",
    last_name="Test",
    photo_url="https://i.imgur.com/1Q1Z1Zm.png",
    is_active=True,
    settings=SETTINGS_EXAMPLE,
    sessions=SESSIONS_EXAMPLE,
    blacklist=BLACKLIST_EXAMPLE,
    created_at=datetime.now(tz=None)
)

"""
Convert out example to JSON (convert all incompatible JSON types to compatible).
"""
USER_EXAMPLE = jsonable_encoder(USER_EXAMPLE)
SESSIONS_EXAMPLE = jsonable_encoder(SESSIONS_EXAMPLE)
BLACKLIST_EXAMPLE = jsonable_encoder(BLACKLIST_EXAMPLE)

""" 
Schemas for our user example model.
"""

# !!! WARNING !!!
# All comments below are for testing purposes only.
# Because I can't create a schema for the main user model

SETTINGS_EXAMPLE_SCHEMA = UserSettingsModel.schema()
# SETTINGS_EXAMPLE_SCHEMA["properties"]["theme"] = ThemesEnum.schema()
# SETTINGS_EXAMPLE_SCHEMA["properties"]["language"] = LanguagesEnum.schema()

SESSIONS_EXAMPLE_SCHEMA = UserSessionInResponseModel.schema()
# SESSIONS_EXAMPLE_SCHEMA["definitions"]["UserSessionInResponseModel"]["properties"]["type"] = UserSessionTypesEnum.schema()
# SESSIONS_EXAMPLE_SCHEMA["properties"]["type"] = UserSessionTypesEnum.schema()

BLACKLIST_EXAMPLE_SCHEMA = BlacklistedUserInResponseModel.schema()

"""
Replace the default schema with the actual schema.

This is a workaround for an issue where models that inherit from model `UserInResponseModel` cannot be found
when generating the schema. This is because the schema is generated before the models are defined.
"""

USER_EXAMPLE_SCHEMA = UserInResponseModel.schema()
# USER_EXAMPLE_SCHEMA["properties"]["settings"] = SETTINGS_EXAMPLE_SCHEMA
# USER_EXAMPLE_SCHEMA["definitions"]["UserSessionInResponseModel"]["properties"]["type"] = UserSessionTypesEnum.schema()
# USER_EXAMPLE_SCHEMA["properties"]["sessions"]["items"] = SESSIONS_EXAMPLE_SCHEMA
# USER_EXAMPLE_SCHEMA["properties"]["blacklist"]["items"] = BLACKLIST_EXAMPLE_SCHEMA

# USER_EXAMPLE_SCHEMA["properties"]["settings"] = SETTINGS_EXAMPLE_SCHEMA
# USER_EXAMPLE_SCHEMA["definitions"]["UserSettingsModel"]["properties"]["theme"] = ThemesEnum.schema()
# USER_EXAMPLE_SCHEMA["definitions"]["UserSettingsModel"]["properties"]["language"] = LanguagesEnum.schema()
# USER_EXAMPLE_SCHEMA["properties"]["sessions"]["items"] = SESSIONS_EXAMPLE_SCHEMA
# USER_EXAMPLE_SCHEMA["properties"]["blacklist"]["items"] = BLACKLIST_EXAMPLE_SCHEMA
