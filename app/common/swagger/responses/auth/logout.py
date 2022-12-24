from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.responses.exceptions import USER_NOT_AUTHORIZED
from app.models.common.exceptions.api import APIExceptionModel

LOGOUT_RESPONSES = {
    200: {
        'description': 'Logout successful.',
        'content': {
            'application/json': {
                'example': "null",
                'schema': None
            }
        }
    },
    401:USER_NOT_AUTHORIZED_RESPONSE
}
