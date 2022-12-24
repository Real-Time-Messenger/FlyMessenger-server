from fastapi.encoders import jsonable_encoder

from app.common.swagger.examples.user import USER_EXAMPLE, USER_EXAMPLE_SCHEMA
from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

UPDATE_ME_RESPONSES = {
    200: {
        'description': 'User updated successfully.',
        'content': {
            'application/json': {
                'example': USER_EXAMPLE,
                'schema': USER_EXAMPLE_SCHEMA
            }
        }
    },
    400: {
        'description': 'Duplicated field value.',
        'content': {
            'application/json': {
                'example': APIException.bad_request("The '{key}' is already taken."),
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
                            message="Field should be at least 3 and at most 255 characters long",
                            location="body",
                            field="email",
                            translation="emailHasIncorrectLength"
                        ),
                        RequestValidationDetails(
                            message="Field should be at least 3 and at most 25 characters long",
                            location="body",
                            field="firstName",
                            translation="firstNameHasIncorrectLength"
                        ),
                        RequestValidationDetails(
                            message="Field should be at most 25 characters long",
                            location="body",
                            field="lastName",
                            translation="lastNameHasIncorrectLength"
                        ),
                    ],
                    code=422
                ),
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
