from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import RequestValidationDetails, APIRequestValidationModel
from app.models.user.user import UserInEventResponseModel
from app.models.user.utils.response_types import AuthResponseType

SIGNUP_RESPONSES = {
    200: {
        'description': 'Signup successful.',
        'content': {
            'application/json': {
                'example': UserInEventResponseModel(event=AuthResponseType.ACTIVATION_REQUIRED),
                'schema': UserInEventResponseModel.schema()
            }
        }
    },
    400: {
        'description': 'User already exists.',
        'content': {
            'application/json': {
                'example': APIException.bad_request("User already exists.", translation_key="userAlreadyExists"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                'examples': {
                    'Validation failed': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Field should be at least 3 and at most 50 characters long.",
                                    location="body",
                                    field="username",
                                    translation="usernameHasIncorrectLength"
                                ),
                                RequestValidationDetails(
                                    message="Field should be at least 3 and at most 255 characters long.",
                                    location="body",
                                    field="email",
                                    translation="emailHasIncorrectLength"
                                ),
                                RequestValidationDetails(
                                    message="Field should be at least 8 and at most 32 characters long.",
                                    location="body",
                                    field="password",
                                    translation="passwordHasIncorrectLength"
                                ),
                                RequestValidationDetails(
                                    message="Field should be at least 8 and at most 32 characters long.",
                                    location="body",
                                    field="passwordConfirm",
                                    translation="passwordConfirmHasIncorrectLength"
                                )
                            ],
                            code=422
                        ),
                    },
                    'Username already exist': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="The username is already taken.",
                                    location="body",
                                    field="username",
                                    translation="usernameAlreadyTaken"
                                )
                            ],
                            code=422
                        ),
                    },
                    'Email already exist': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="The email is already taken.",
                                    location="body",
                                    field="email",
                                    translation="emailAlreadyTaken"
                                )
                            ],
                            code=422
                        ),
                    }
                },
                'schema': RequestValidationDetails.schema(),
            },
        }
    }
}
