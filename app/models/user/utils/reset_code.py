from pydantic import Field

from app.models.common.mongo.base_model import MongoModel

class ValidateResetPasswordTokenModel(MongoModel):
    """ Model for validate user reset password token. """

    token: str = Field(...)
