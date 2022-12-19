from datetime import datetime

from pydantic import Field

from app.models.common.mongo.base_model import MongoModel


class UserResetCodeModel(MongoModel):
    reset_password_token: str | None = Field(default=None, alias="resetPasswordToken")
    reset_password_token_expiration: datetime | None = Field(default=None, alias="resetPasswordExpires")

class ValidateResetPasswordTokenModel(MongoModel):
    token: str = Field(...)
