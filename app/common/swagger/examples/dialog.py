from datetime import datetime

from fastapi.encoders import jsonable_encoder

from app.common.swagger.examples.user import USER_EXAMPLE
from app.models.common.object_id import PyObjectId
from app.models.dialog.dialog import DialogInResponseModel, LastMessageInDialogModel
from app.models.dialog.messages import DialogMessageInResponseModel

# Messages example model (for swagger).
MESSAGES_EXAMPLE = [
    DialogMessageInResponseModel(
        id=PyObjectId("60f1b1b1b1b1b1b1b1b1b1b1"),
        dialog_id=PyObjectId("5f9f1b9b9b9b9b9b9b9b9b9b"),
        sender=USER_EXAMPLE,
        text="Hello, world!",
        file=None,
        is_read=True,
        sent_at=datetime.now(tz=None)
    ),
    DialogMessageInResponseModel(
        id=PyObjectId("60f1b1b1b1b1b1b1b1b1b1b2"),
        dialog_id=PyObjectId("5f9f1b9b9b9b9b9b9b9b9b9b"),
        sender=USER_EXAMPLE,
        text="Hello, world!",
        file=None,
        is_read=False,
        sent_at=datetime.now(tz=None)
    ),
]

# Dialog example model (for swagger).
DIALOG_EXAMPLE = DialogInResponseModel(
    id=PyObjectId("5f9f1b9b9b9b9b9b9b9b9b9b"),
    label="Dialog example",
    user=USER_EXAMPLE,
    images=[],
    unread_messages=1,
    is_pinned=False,
    is_notifications_enabled=True,
    is_sound_enabled=True,
    messages=MESSAGES_EXAMPLE,
    last_message=LastMessageInDialogModel(**MESSAGES_EXAMPLE[-1].dict()),
    is_me_blocked=False,
)

"""
Convert out example to JSON (convert all incompatible JSON types to compatible).
"""
DIALOG_EXAMPLE = jsonable_encoder(DIALOG_EXAMPLE)

"""
Schemas for our dialog example model
"""
DIALOG_EXAMPLE_SCHEMA = DialogInResponseModel.schema()
