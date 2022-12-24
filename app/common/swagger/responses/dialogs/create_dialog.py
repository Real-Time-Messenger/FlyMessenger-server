from app.common.swagger.examples.dialog import DIALOG_EXAMPLE
from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.exception.api import APIException
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

CREATE_DIALOG_RESPONSES = {
    200: {
        'description': 'Dialog created successfully.',
        'content': {
            'application/json': {
                'example': DIALOG_EXAMPLE,
                # TODO: Fix this
                # 'schema': DIALOG_EXAMPLE_SCHEMA
            }
        }
    },
    400: {
        'description': 'Bad request.',
        'content': {
            'application/json': {
                'examples:': {
                    'Dialog already exists': {
                        'value': APIException.bad_request("Dialog already exist.", translation_key="dialogAlreadyExist")
                    },
                    'Cannot add yourself': {
                        'value': APIException.bad_request("You can't add yourself to dialog.", translation_key="cantAddYourselfToDialog")
                    }
                }
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                'examples': {
                    'Incorrect user ID': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect user ID.",
                                    location="body",
                                    field="userId",
                                    translation="incorrectUserId"
                                ),
                            ],
                        )
                    },
                }
            }
        }
    }
}
