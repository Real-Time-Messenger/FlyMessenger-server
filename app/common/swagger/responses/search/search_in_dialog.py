from app.common.swagger.examples.search import SEARCH_IN_DIALOG_EXAMPLE, SEARCH_IN_DIALOG_EXAMPLE_SCHEMA
from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

SEARCH_BY_DIALOG_RESPONSES = {
    200: {
        'description': 'Search by dialog fetched successfully.',
        'content': {
            'application/json': {
                'example': SEARCH_IN_DIALOG_EXAMPLE,
                'schema': SEARCH_IN_DIALOG_EXAMPLE_SCHEMA
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
                                    message="Incorrect ID.",
                                    location="path",
                                    field="dialogId",
                                    translation="incorrectId"
                                ),
                            ]
                        )
                    },
                    'Incorrect search query': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Incorrect search query.",
                                    location="query",
                                    field="query",
                                    translation="incorrectSearchQuery"
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
