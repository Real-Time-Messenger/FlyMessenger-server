from fastapi.encoders import jsonable_encoder

from app.common.swagger.examples.dialog import MESSAGES_EXAMPLE as DIALOG_MESSAGES_EXAMPLE, DIALOG_EXAMPLE, USER_EXAMPLE as DIALOG_USER_EXAMPLE
from app.common.swagger.examples.user import USER_EXAMPLE
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInResponseModel, UserInDialogResponseModel
from app.models.search.search import SearchResultModel

# Messages example model (for swagger).
MESSAGES_EXAMPLE = [
    DialogInResponseModel(
        id=PyObjectId("5f9f1b9b9b9b9b9b9b9b9b9b"),
        label="Search example 1",
        user=UserInDialogResponseModel(**USER_EXAMPLE),
        images=[],
        unread_messages=1,
        is_pinned=False,
        is_notifications_enabled=True,
        is_sound_enabled=True,
        last_message=DIALOG_MESSAGES_EXAMPLE[0],
        messages=[],
        is_me_blocked=False,
    ),
    DialogInResponseModel(
        id=PyObjectId("5f9f1b9b9b9b9b9b9b9b9b9c"),
        label="Search example 2",
        user=UserInDialogResponseModel(**USER_EXAMPLE),
        images=[],
        unread_messages=1,
        is_pinned=False,
        is_notifications_enabled=True,
        is_sound_enabled=True,
        last_message=DIALOG_MESSAGES_EXAMPLE[1],
        messages=[],
        is_me_blocked=False,
    ),
]

# Search example model (for swagger).
SEARCH_EXAMPLE = SearchResultModel(
    dialogs=[DIALOG_EXAMPLE],
    messages=MESSAGES_EXAMPLE,
    users=[DIALOG_USER_EXAMPLE],
)

# Search example model (for swagger).
SEARCH_IN_DIALOG_EXAMPLE = SearchResultModel(
    dialogs=[],
    messages=MESSAGES_EXAMPLE,
    users=[]
)

"""
Convert out example to JSON (convert all incompatible JSON types to compatible).
"""
SEARCH_EXAMPLE = jsonable_encoder(SEARCH_EXAMPLE)
SEARCH_IN_DIALOG_EXAMPLE = jsonable_encoder(SEARCH_IN_DIALOG_EXAMPLE)

"""
Schemas for our search in dialog example model.
"""
SEARCH_EXAMPLE_SCHEMA = SearchResultModel.schema()
SEARCH_IN_DIALOG_EXAMPLE_SCHEMA = SearchResultModel.schema()
