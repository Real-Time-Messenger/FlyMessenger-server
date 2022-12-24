from fastapi.encoders import jsonable_encoder

from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.examples.user import USER_EXAMPLE

GET_ME_RESPONSES = {
    200: {
        'description': 'Current user fetched successfully.',
        'content': {
            'application/json': {
                'example': USER_EXAMPLE,
                # TODO: Fix this
                # 'schema': USER_EXAMPLE_SCHEMA
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE
}
