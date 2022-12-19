from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId


class DialogInDeleteResponseModel(MongoModel):
    dialog_id: PyObjectId = Field(..., alias="dialogId")