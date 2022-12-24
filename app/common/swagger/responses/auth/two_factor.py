from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails
from app.models.user.user import UserInAuthResponseModel

TWO_FACTOR_RESPONSES = {
    200: {
        'description': 'Two factor authentication successful',
        'content': {
            'application/json': {
                'example': UserInAuthResponseModel(token="token"),
                'schema': UserInAuthResponseModel.schema()
            }
        }
    },
    403: {
        'description': 'Two-factor authentication failed.',
        'content': {
            'application/json': {
                'examples': {
                    'Two-factor authentication is not enabled': {
                        'value': APIException.forbidden("Two-factor authentication is not enabled.",
                                                        translation_key="twoFactorIsNotEnabled"),
                    },
                    'Two-factor authentication code is incorrect': {
                        'value': APIException.forbidden("Two-factor authentication code is incorrect.",
                                                        translation_key="twoFactorCodeIsNotValid"),
                    },
                    'User is not activated': {
                        'value': USER_NOT_ACTIVATED
                    }
                },
                'schema': APIExceptionModel.schema()
            }
        }
    },
    404: {
        'description': 'User with this two-factor code does not exist.',
        'content': {
            'application/json': {
                'example': APIException.not_found("The two-factor code is incorrect.",
                                                  translation_key="twoFactorCodeIsNotValid"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body',
        'content': {
            'application/json': {
                'example': APIRequestValidationModel(
                    details=[
                        RequestValidationDetails(
                            message="Field required.",
                            location="body",
                            field="code",
                            translation="twoFactorCodeIsRequired"
                        ),
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
