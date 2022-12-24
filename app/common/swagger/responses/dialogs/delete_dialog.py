from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

DELETE_DIALOG_RESPONSES = {
    204: {
        'description': 'Dialog deleted successfully.'
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
