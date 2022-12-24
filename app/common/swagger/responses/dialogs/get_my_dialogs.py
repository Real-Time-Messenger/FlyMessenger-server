from app.common.swagger.examples.dialog import DIALOG_EXAMPLE
from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE

GET_MY_DIALOGS_RESPONSES = {
    200: {
        'description': 'Dialogs fetched successfully.',
        'content': {
            'application/json': {
                'example': [DIALOG_EXAMPLE],
                # TODO: Implement `DIALOG_EXAMPLE_SCHEMA`
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE
}
