from app.common.swagger.examples.dialog import DIALOG_EXAMPLE
from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

GET_DIALOG_MESSAGES_RESPONSES = {
    200: {
        'description': 'Dialog messages fetched successfully.',
        'content': {
            'application/json': {
                'example': [DIALOG_EXAMPLE],
                # TODO: Implement `DIALOG_EXAMPLE_SCHEMA`
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
    422: {
        'description': 'Invalid JSON body.',
        'content': {
            'application/json': {
                'examples': {
                    'Incorrect dialog ID': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect Dialog ID.",
                                    location="query",
                                    field="dialogId",
                                    translation="incorrectDialogId"
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