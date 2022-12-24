from fastapi.encoders import jsonable_encoder

from app.common.swagger.responses.common.not_authorized import USER_NOT_AUTHORIZED_RESPONSE
from app.common.swagger.examples.user import USER_EXAMPLE
from app.models.common.exceptions.body import RequestValidationDetails, APIRequestValidationModel

UPDATE_MY_AVATAR_RESPONSES = {
    200: {
        'description': 'Avatar updated successfully.',
        'content': {
            'application/json': {
                'example': USER_EXAMPLE,
                # TODO: Implement schema
                # 'schema': USER_EXAMPLE_SCHEMA
            }
        }
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
    422: {
        'description': 'Invalid avatar.',
        'content': {
            'application/json': {
                'examples': {
                    'Invalid file type': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="Invalid file type.",
                                    location="body",
                                    field="file",
                                    translation="invalidFileType"
                                ),
                            ],
                        )
                    },
                    'File too large': {
                        'value': APIRequestValidationModel(
                            details=[
                                RequestValidationDetails(
                                    message="File too large.",
                                    location="body",
                                    field="file",
                                    translation="fileTooLarge"
                                ),
                            ],
                        )
                    }
                },
                'schema': RequestValidationDetails.schema()
            }
        }
    }
}
