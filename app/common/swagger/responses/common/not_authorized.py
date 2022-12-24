from app.common.swagger.responses.exceptions import USER_NOT_AUTHORIZED, USER_NOT_AUTHORIZED_SCHEMA

USER_NOT_AUTHORIZED_RESPONSE = {
    'description': 'User is not authorized.',
    'content': {
        'application/json': {
            'example': USER_NOT_AUTHORIZED,
            'schema': USER_NOT_AUTHORIZED_SCHEMA
        }
    }
}