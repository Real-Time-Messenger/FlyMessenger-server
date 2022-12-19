from datetime import datetime
from typing import Union

from pydantic import Field

from app.models.common.mongo.base_model import MongoModel


class UserResetCodeModel(MongoModel):
    reset_password_token: Union[str, None] = Field(default=None, alias="resetPasswordToken")
    reset_password_token_expiration: Union[datetime, None] = Field(default=None, alias="resetPasswordExpires")

class ValidateResetPasswordTokenModel(MongoModel):
    token: str = Field(...)
