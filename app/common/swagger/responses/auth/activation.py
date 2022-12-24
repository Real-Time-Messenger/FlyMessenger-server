from app.exception.api import APIException
from app.models.common.exceptions.body import RequestValidationDetails, APIRequestValidationModel

ACTIVATION_RESPONSES = {
    200: {
        'description': 'Activation successful.',
        'content': {
            'application/json': {
                'example': "null",
                'schema': None
            }
        }
    },
    400: {
        'description': 'Activation code is invalid.',
        'content': {
            'application/json': {
                'examples': {
                    'Invalid activation code': {
                        'value': APIException.bad_request("Invalid activation code.", translation_key="invalidActivationCode"),
                    },
                    'Activation code is expired': {
                        'value': APIException.bad_request("Activation code is expired.", translation_key="activationCodeIsExpired"),
                    },
                    'Account is already activated': {
                        'value': APIException.bad_request("Account is already activated.", translation_key="accountIsAlreadyActivated"),
                    },
                }
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
                            message="Token is not correct.",
                            location="body",
                            field="token",
                            translation="tokenIsNotCorrect"
                        )
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}