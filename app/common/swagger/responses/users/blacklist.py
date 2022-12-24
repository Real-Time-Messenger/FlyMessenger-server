from fastapi.encoders import jsonable_encoder

from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.examples.user import BLACKLIST_EXAMPLE, USER_EXAMPLE
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails
from app.models.common.responses.blacklist import BlockOrUnblockUserResponseModel

blocked = BlockOrUnblockUserResponseModel(
    is_blocked=True,
    blacklist=BLACKLIST_EXAMPLE,
    user_id=USER_EXAMPLE.get("id")
)

unblocked = BlockOrUnblockUserResponseModel(
    is_blocked=False,
    blacklist=BLACKLIST_EXAMPLE,
    user_id=USER_EXAMPLE.get("id")
)

BLACKLIST_USER_RESPONSES = {
    200: {
        'description': 'Blacklist action performed successfully.',
        'content': {
            'application/json': {
                'examples': {
                    'Blocked': {
                        'value': jsonable_encoder(blocked)
                    },
                    'Unblocked': {
                        'value': jsonable_encoder(unblocked)
                    }
                },
                'schema': BlockOrUnblockUserResponseModel.schema()
            }
        }
    },
    400: {
        'description': 'Bad request.',
        'content': {
            'application/json': {
                'example': APIException.bad_request("You can't block yourself.", translation_key="cantBlockYourself"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
    422: {
        'description': 'Incorrect ID.',
        'content': {
            'application/json': {
                'example': APIRequestValidationModel(
                    details=[
                        RequestValidationDetails(
                            message="Incorrect user ID.",
                            location="body",
                            field="blacklistedUserId",
                            translation="incorrectUserId"
                        ),
                    ],
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
