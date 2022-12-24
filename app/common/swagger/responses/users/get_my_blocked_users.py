from fastapi.encoders import jsonable_encoder

from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.examples.user import BLACKLIST_EXAMPLE, BLACKLIST_EXAMPLE_SCHEMA

GET_MY_BLOCKED_USERS_RESPONSES = {
    200: {
        'description': 'Current user blocked users fetched successfully.',
        'content': {
            'application/json': {
                'example': BLACKLIST_EXAMPLE,
                'schema': BLACKLIST_EXAMPLE_SCHEMA
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
}