from app.common.swagger.responses.exceptions import USER_NOT_ACTIVATED
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails
from app.models.user.user import UserInAuthResponseModel, UserInEventResponseModel
from app.models.user.utils.response_types import AuthResponseType

LOGIN_RESPONSES = {
    200: {
        'description': 'Login successful.',
        'content': {
            'application/json': {
                'examples': {
                    'Return user token': {
                        'value': UserInAuthResponseModel(token='token'),
                    },
                    'Need to confirm new device': {
                        'value': UserInEventResponseModel(event=AuthResponseType.NEW_DEVICE),
                        'schema': UserInAuthResponseModel.schema()
                    },
                    'Need to confirm two-factor authentication': {
                        'value': UserInEventResponseModel(event=AuthResponseType.TWO_FACTOR),
                    },
                    'Need to activate account': {
                        'value': UserInEventResponseModel(event=AuthResponseType.ACTIVATION_REQUIRED),
                    },
                },
                'schema': UserInAuthResponseModel.schema()
            }
        }
    },
    403: {
        'description': 'Account is not activated.',
        'content': {
            'application/json': {
                'example': USER_NOT_ACTIVATED,
                'schema': APIExceptionModel.schema()
            }
        }
    },
    404: {
        'description': 'The username or password is incorrect.',
        'content': {
            'application/json': {
                'example': APIException.not_found("The username or password is incorrect.",
                                                  translation_key="userNotFound"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                'examples': {
                    'Incorrect username': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect username.",
                                    location="body",
                                    field="username",
                                    translation="incorrectUsername"
                                ),
                            ]
                        )
                    },
                    'Incorrect password': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect password.",
                                    location="body",
                                    field="password",
                                    translation="incorrectPassword"
                                ),
                            ]
                        )
                    },
                },
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
