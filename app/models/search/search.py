from pydantic import Field

from app.models.common.mongo.base_model import MongoModel
from app.models.dialog.dialog import DialogInResponseModel
from app.models.user.user import UserInSearchModel


class SearchResultModel(MongoModel):
    """ Model for search result. """

    dialogs: list[DialogInResponseModel] = Field(default_factory=list)
    messages: list[DialogInResponseModel] = Field(default_factory=list)
    users: list[UserInSearchModel] = Field(default_factory=list)