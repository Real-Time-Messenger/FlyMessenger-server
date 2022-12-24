from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

RESET_PASSWORD_RESPONSES = {
    200: {
        'description': 'Password reset successful.',
        'content': {
            'application/json': {
                'example': "null",
                'schema': None
            }
        }
    },
    400: {
        'description': 'Reset password token is invalid.',
        'content': {
            'application/json': {
                'example': APIException.bad_request("The reset password token is incorrect.",
                                                    translation_key="resetPasswordTokenIsNotValid"),
                'schema': APIExceptionModel.schema()
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
        'description': 'Reset password token does not exist.',
        'content': {
            'application/json': {
                'example': APIException.not_found("The reset password token does not exist.",
                                                  translation_key="resetPasswordTokenDoesNotExist"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                # 'example': APIRequestValidationModel(
                #     details=[
                #         RequestValidationDetails(
                #             message="Field should be at least 8 and at most 32 characters long.",
                #             location="body",
                #             field="password",
                #             translation="passwordHasIncorrectLength"
                #         ),
                #         RequestValidationDetails(
                #             message="Passwords do not match.",
                #             location="__root__ (because we use root validator)",
                #             field="password",
                #             translation="passwordsDoNotMatch"
                #         ),
                #     ],
                #     code=422
                # ),
                # 'schema': RequestValidationDetails.schema()
                'examples': {
                    'Token is empty': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Field required.",
                                    location="body",
                                    field="token",
                                    translation="tokenIsRequired"
                                ),
                            ],
                        )
                    },
                    'Password has incorrect length': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Field should be at least 8 and at most 32 characters long.",
                                    location="body",
                                    field="password",
                                    translation="passwordHasIncorrectLength"
                                ),
                            ],
                        )
                    },
                    'Passwords do not match': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Passwords do not match.",
                                    location="__root__",
                                    field="password",
                                    translation="passwordsDoNotMatch"
                                ),
                            ],
                        )
                    }
                }
            }
        }
    }
}
