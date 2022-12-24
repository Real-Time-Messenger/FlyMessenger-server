from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

CALL_RESET_PASSWORD_RESPONSES = {
    200: {
        'description': 'Reset password link sent.',
        'content': {
            'application/json': {
                'example': "null",
                'schema': None
            }
        }
    },
    403: {
        'description': 'User is not active.',
        'content': {
            'application/json': {
                'example': USER_NOT_ACTIVATED,
                'schema': APIExceptionModel.schema()
            }
        }
    },
    404: {
        'description': 'User with this email does not exist.',
        'content': {
            'application/json': {
                'example': APIException.not_found("User with this email does not exist.", translation_key="userDoesNotExist"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                'example': APIRequestValidationModel(
                    details=[
                        RequestValidationDetails(
                            message="Field should be at least 3 and at most 255 characters long.",
                            location="body",
                            field="email",
                            translation="emailHasIncorrectLength"
                        ),
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}