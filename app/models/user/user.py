from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel, Field, EmailStr, validator, root_validator, SecretStr, constr

from app.common.pydantic.validators import username_validator, password_validator, passwords_match_validator, \
    email_validator, password_confirm_validator, first_name_validator, last_name_validator
from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId
from app.models.user.blacklist import BlacklistedUserModel, BlacklistedUserInResponseModel
from app.models.user.sessions import UserSessionModel, UserSessionInResponseModel
from app.models.user.settings import UserSettingsModel, UserSettingsUpdateModel
from app.services.hash.hash import HashService


class UserModel(MongoModel):
    """ Base model for user. """

    id: PyObjectId = Field(default_factory=PyObjectId)
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., min_length=3, max_length=25, alias="firstName")
    last_name: Optional[str] = Field(default=None, max_length=25, alias="lastName")
    is_active: bool = Field(default=False, alias="isActive")
    photo_url: Optional[str] = Field(alias="photoURL")
    is_online: Optional[bool] = Field(default=True, alias="isOnline")
    last_activity: Optional[datetime] = Field(default=None, alias="lastActivity")
    created_at: datetime = Field(default=datetime.utcnow(), alias="createdAt")

    reset_password_token: Optional[str] = Field(default=None, alias="resetPasswordToken")
    activation_token: Optional[str] = Field(default=None, alias="activationToken")
    two_factor_code: Optional[str] = Field(default=None, alias="twoFactorCode")
    new_device_code: Optional[str] = Field(default=None, alias="newDeviceCode")

    settings: UserSettingsModel = Field(default_factory=UserSettingsModel)
    sessions: list[UserSessionModel] = Field(default_factory=list)
    blacklist: list[BlacklistedUserModel] = Field(default_factory=list)

    @validator("password", pre=True)
    def hash_password(cls, pw: str) -> str:
        """ Hash password before save to database (if password is not hashed yet). """

        if HashService.is_hashed(pw):
            return pw

        return HashService.get_hash(pw)


class UserInSignUpModel(MongoModel):
    """ Model for sign up user. """

    username: constr(to_lower=True) = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    password_confirm: str = Field(..., alias="passwordConfirm")

    # Validators
    _username_validator = validator("username", allow_reuse=True)(username_validator)
    _password_validator = validator("password", allow_reuse=True)(password_validator)
    _email_validator = validator("email", allow_reuse=True)(email_validator)
    _password_confirm_validator = validator("password_confirm", allow_reuse=True)(password_confirm_validator)
    _passwords_match_validator = root_validator(allow_reuse=True)(passwords_match_validator)


class UserInLoginModel(BaseModel):
    """ Model for login user. """

    username: Union[constr(to_lower=True), EmailStr] = Field(..., example="username")
    password: SecretStr = Field(..., example="password")

    # Validators
    _username_validator = validator("username", allow_reuse=True)(username_validator)
    _password_validator = validator("password", allow_reuse=True)(password_validator)


class UserInAuthResponseModel(BaseModel):
    """ Model for auth response. """

    token: str = Field(...)


class UserInEventResponseModel(BaseModel):
    """ Model for user event response. """

    event: str = Field(...)


class UserInResponseModel(MongoModel):
    """ Response model for user. """

    id: PyObjectId = Field(...)
    username: str = Field(...)
    email: Optional[EmailStr] = Field(None)
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    is_active: bool = Field(..., alias="isActive")
    photo_url: Optional[str] = Field(alias="photoURL")
    is_online: Optional[bool] = Field(default=True, alias="isOnline")
    last_activity: Optional[datetime] = Field(default=None, alias="lastActivity")
    created_at: datetime = Field(..., alias="createdAt")

    settings: UserSettingsModel = Field(default_factory=UserSettingsModel)
    sessions: list[UserSessionInResponseModel] = Field(default_factory=list)
    blacklist: list[BlacklistedUserInResponseModel] = Field(default_factory=list)


class UserInUpdateModel(UserSettingsUpdateModel):
    """ Model for update user. """

    email: Optional[EmailStr] = Field()
    first_name: Optional[str] = Field(alias="firstName")
    last_name: Optional[str] = Field(alias="lastName")

    # Validators
    _email_validator = validator("email", allow_reuse=True)(email_validator)
    _first_name_validator = validator("first_name", allow_reuse=True)(first_name_validator)
    _last_name_validator = validator("last_name", allow_reuse=True)(last_name_validator)


class UserInSearchModel(MongoModel):
    """ Model for search user. """

    id: PyObjectId = Field(...)
    username: str = Field(...)
    photo_url: str = Field(..., alias="photoURL")
    email: EmailStr = Field(...)
    first_name: str = Field(..., alias="firstName")
    last_name: Optional[str] = Field(..., alias="lastName")


class UserInCallResetPasswordModel(BaseModel):
    """ Model for call reset password. """

    email: EmailStr = Field(...)

    # Validators
    _email_validator = validator("email", allow_reuse=True)(email_validator)


class UserInResetPasswordModel(BaseModel):
    """ Model for reset password. """

    token: str = Field(...)
    password: str = Field(...)
    password_confirm: str = Field(..., alias="passwordConfirm")

    # Validators
    _password_validator = validator("password", allow_reuse=True)(password_validator)
    _passwords_match_validator = root_validator(allow_reuse=True)(passwords_match_validator)


class UserInActivationModel(BaseModel):
    """ User activation model. """

    token: str = Field(...)


class UserInTwoFactorAuthenticationModel(BaseModel):
    """ User two-factor authentication model. """
    code: str = Field(...)


class UserInNewDeviceConfirmationModel(BaseModel):
    """ User new device confirmation model. """
    code: str = Field(...)
