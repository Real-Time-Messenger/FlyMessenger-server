from fastapi.encoders import jsonable_encoder

from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.examples.user import SESSIONS_EXAMPLE, SESSIONS_EXAMPLE_SCHEMA

GET_MY_SESSIONS_RESPONSES = {
    200: {
        'description': 'Current user sessions fetched successfully.',
        'content': {
            'application/json': {
                'example': SESSIONS_EXAMPLE,
                'schema': SESSIONS_EXAMPLE_SCHEMA
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE
}
