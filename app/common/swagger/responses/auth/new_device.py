from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails
from app.models.user.user import UserInAuthResponseModel

NEW_DEVICE_RESPONSES = {
    200: {
        'description': 'New device successful.',
        'content': {
            'application/json': {
                'example': UserInAuthResponseModel(token="token"),
                'schema': UserInAuthResponseModel.schema()
            }
        }
    },
    400: {
        'description': 'New device code is incorrect.',
        'content': {
            'application/json': {
                'example': APIException.bad_request("The new device confirmation code is incorrect.",
                                                    translation_key="newDeviceCodeIsNotValid"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    403: {
        'description': 'New device authentication failed.',
        'content': {
            'application/json': {
                'examples': {
                    'New device authentication is incorrect': {
                        'value': APIException.forbidden("The new device confirmation code is incorrect.",
                                                        translation_key="newDeviceCodeIsNotValid"),
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
        'description': 'User with this new device code does not exist.',
        'content': {
            'application/json': {
                'example': APIException.not_found("The new device confirmation code is incorrect.",
                                                  translation_key="newDeviceCodeIsNotValid"),
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
                            translation="newDeviceCodeIsRequired"
                        ),
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
