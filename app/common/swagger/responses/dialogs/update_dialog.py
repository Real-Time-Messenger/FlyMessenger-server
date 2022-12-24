from app.common.swagger.examples.dialog import DIALOG_EXAMPLE
from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

UPDATE_DIALOG_RESPONSES = {
    200: {
        'description': 'Dialog updated successfully.',
        'content': {
            'application/json': {
                'example': DIALOG_EXAMPLE,
                # TODO: Implement `DIALOG_EXAMPLE_SCHEMA`
            }
        }
    },
    400: {
        'description': 'Bad request.',
        'content': {
            'application/json': {
                'examples': {
                    'Dialog pin limit reached': {
                        'value': APIException.bad_request("You can't pin more than 10 dialogs.",
                                                          translation_key="cantPinMoreThan10Dialogs")
                    }
                },
                'schema': APIExceptionModel.schema()
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
    404: {
        'description': 'Dialog not found.',
        'content': {
            'application/json': {
                'example': APIException.not_found("Dialog not found.", translation_key="dialogNotFound"),
                'schema': APIExceptionModel.schema()
            }
        }
    },
    422: {
        'description': 'Incorrect JSON body.',
        'content': {
            'application/json': {
                'examples': {
                    'Incorrect dialog ID': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect ID.",
                                    location="path",
                                    field="dialogId",
                                    translation="incorrectId"
                                ),
                            ]
                        )
                    }
                },
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
