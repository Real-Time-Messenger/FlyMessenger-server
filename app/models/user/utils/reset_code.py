from datetime import datetime
from typing import Union

from pydantic import Field

from app.models.common.mongo.base_model import MongoModel

class ValidateResetPasswordTokenModel(MongoModel):
    token: str = Field(...)
