from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from fastapi import Depends

from pydantic import BaseModel, Field, EmailStr, validator, root_validator, SecretStr

from app.common.pydantic.validators import username_validator, password_validator, passwords_match_validator, \
    email_validator, password_confirm_validator
from app.exception.api import APIException
from app.models.common.exceptions.body import NotCorrectLength, EmailIsNotValidType
from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserModel, BlacklistedUserInResponseModel
from app.models.user.sessions import UserSessionModel, UserSessionInResponseModel
from app.models.user.settings import UserSettingsModel, UserSettingsUpdateModel
from app.services.hash.hash import HashService
from app.services.token.token import TokenService


class UserModel(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., min_length=3, max_length=25, alias="firstName")
    last_name: str | None = Field(default=None, max_length=25, alias="lastName")
    is_active: bool = Field(default=False ,alias="isActive")
    photo_url: str | None = Field(alias="photoURL")
    is_online: bool | None = Field(default=True, alias="isOnline")
    last_activity: datetime | None = Field(default=None, alias="lastActivity")
    created_at: datetime = Field(default=datetime.utcnow(), alias="createdAt")

    reset_password_token: str | None = Field(default=None, alias="resetPasswordToken")
    reset_password_token_expiration: datetime | None = Field(default=None, alias="resetPasswordExpires")

    activation_token: str | None = Field(default=None, alias="activationToken")

    settings: UserSettingsModel = Field(default_factory=UserSettingsModel)
    sessions: list[UserSessionModel] = Field(default_factory=list)
    blacklist: list[BlacklistedUserModel] = Field(default_factory=list)

    @validator("password", pre=True)
    def hash_password(cls, pw: str) -> str:
        if HashService.is_hashed(pw):
            return pw

        return HashService.get_hash(pw)


class UserInSignUpModel(MongoModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    password_confirm: str = Field(..., alias="passwordConfirm")

    _username_validator = validator("username", allow_reuse=True)(username_validator)
    _password_validator = validator("password", allow_reuse=True)(password_validator)
    _email_validator = validator("email", allow_reuse=True)(email_validator)
    _password_confirm_validator = validator("password_confirm", allow_reuse=True)(password_confirm_validator)
    _passwords_match_validator = root_validator(allow_reuse=True)(passwords_match_validator)

    # @validator("username", pre=True)
    # def username_validator(cls, username: str) -> str:
    #     if not len(username) >= 3 and len(username) <= 50:
    #         raise NotCorrectLength(min_length=3, max_length=50, translation_key="usernameHasIncorrectLength")
    #
    #     return username
    #
    # @validator("email", pre=True)
    # def email_validator(cls, email: EmailStr) -> EmailStr:
    #     if not len(email) >= 3 and len(email) <= 255:
    #         raise NotCorrectLength(min_length=3, max_length=255, translation_key="emailHasIncorrectLength")
    #
    #     try:
    #         validate_email(email)
    #     except EmailNotValidError as e:
    #         raise EmailIsNotValidType(translation_key="emailHasIncorrectDomain")
    #
    #     return email
    #
    # @validator("password", pre=True)
    # def password_validator(cls, password: str) -> str:
    #     if not len(password) >= 8 and len(password) <= 32:
    #         raise NotCorrectLength(min_length=8, max_length=32, translation_key="passwordHasIncorrectLength")
    #
    #     return password
    #
    # @validator("password_confirm", pre=True)
    # def password_confirm_validator(cls, password_confirm: str) -> str:
    #     if not len(password_confirm) >= 8 and len(password_confirm) <= 32:
    #         raise NotCorrectLength(min_length=8, max_length=32, translation_key="passwordConfirmHasIncorrectLength")
    #
    #     return password_confirm
    #
    # @root_validator
    # def passwords_match(cls, values: dict) -> dict:
    #     password = values.get("password")
    #     password_confirm = values.get("password_confirm")
    #
    #     if password != password_confirm:
    #         raise PasswordsDoNotMatch(translation_key="passwordsDoNotMatch")
    #
    #     return values

class UserInLoginModel(BaseModel):
    username: str | EmailStr = Field(..., example="username")
    password: SecretStr = Field(..., example="password")

    _username_validator = validator("username", allow_reuse=True)(username_validator)
    _password_validator = validator("password", allow_reuse=True)(password_validator)

class UserInAuthResponseModel(BaseModel):
    token: str = Field(...)


class UserInResponseModel(MongoModel):
    id: PyObjectId = Field(...)
    username: str = Field(...)
    email: EmailStr | None = Field(None)
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    is_active: bool = Field(..., alias="isActive")
    photo_url: str | None = Field(alias="photoURL")
    is_online: bool | None = Field(default=True, alias="isOnline")
    last_activity: datetime | None = Field(default=None, alias="lastActivity")
    created_at: datetime = Field(..., alias="createdAt")

    settings: UserSettingsModel = Field(default_factory=UserSettingsModel)
    sessions: list[UserSessionInResponseModel] = Field(default_factory=list)
    blacklist: list[BlacklistedUserInResponseModel] = Field(default_factory=list)


class UserInUpdateModel(UserSettingsUpdateModel):
    username: str | None = Field()
    email: EmailStr | None = Field()
    first_name: str | None = Field(min_length=3, max_length=25, alias="firstName")
    last_name: str | None = Field(max_length=25, alias="lastName")


class UserInSearchModel(MongoModel):
    id: PyObjectId = Field(...)
    username: str = Field(...)
    photo_url: str = Field(..., alias="photoURL")
    email: EmailStr = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: str | None = Field(..., alias="lastName")


class UserInCallResetPasswordModel(BaseModel):
    email: EmailStr = Field(...)

    @validator("email")
    def email_is_correct(cls, email: EmailStr) -> EmailStr:
        if not len(email) >= 3 and len(email) <= 255:
            raise NotCorrectLength(min_length=3, max_length=255, translation_key="emailHasIncorrectLength")

        try:
            validate_email(email)
        except EmailNotValidError as e:
            raise EmailIsNotValidType(translation_key="emailHasIncorrectDomain")

        return email

class UserInResetPasswordModel(BaseModel):
    token: str = Field(...)
    password: str = Field(..., min_length=8, max_length=32)
    password_confirm: str = Field(..., min_length=8, max_length=32, alias="passwordConfirm")

    @root_validator
    def check_passwords_match(cls, values: dict) -> dict:
        pw1, pw2 = values.get('password'), values.get('password_confirm')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise APIException.bad_request("Passwords do not match.")
        return values


class UserInActivationModel(BaseModel):
    token: str = Field(...)