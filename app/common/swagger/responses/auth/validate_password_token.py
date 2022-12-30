from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

VALIDATE_RESET_PASSWORD_TOKEN_RESPONSES = {
    200: {
        'description': 'Reset password token is valid.',
        'content': {
            'application/json': {
                'example': "null",
                'schema': None
            }
        }
    },
    403: {
        'description': 'Reset password token is expired.',
        'content': {
            'application/json': {
                'example': APIException.forbidden("The reset password token is expired.",
                                                  translation_key="resetPasswordTokenIsExpired"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    404: {
        'description': 'The reset password token is incorrect.',
        'content': {
            'application/json': {
                'example': APIException.not_found("The reset password token is incorrect.",
                                                  translation_key="resetPasswordTokenIsNotValid"),
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
                            message="Field required.",
                            location="body",
                            field="code",
                            translation="validateResetPasswordCodeRequired"
                        ),
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
