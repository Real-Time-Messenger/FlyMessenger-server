from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.common.object_id import PyObjectId

class DialogInDeleteResponseModel(MongoModel):
    """ Response model for delete dialog (it returns `dialog_id` to client). """

    dialog_id: PyObjectId = Field(..., alias="dialogId")