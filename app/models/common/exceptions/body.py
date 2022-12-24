from typing import Optional

from pydantic import BaseModel, PydanticValueError


class RequestValidationDetails(BaseModel):
    """
    Request validation details model.

    Attributes:
        location (str): Location of the error (body, query, path, header).
        message (str): Error message.
        field (str): Field name (username, password, etc.).
        translation (str): Translation key.
    """

    location: str
    message: str
    field: Optional[str] = None
    translation: Optional[str] = None


class APIRequestValidationModel(BaseModel):
    """ API request validation model. """

    details: list[RequestValidationDetails]
    code: int = 422


class InvalidObjectId(PydanticValueError):
    """ `Invalid ObjectId` custom exception. """

    code = 'invalid_object_id'
    msg_template = 'Invalid ID'


class NotCorrectLength(PydanticValueError):
    """ `Not correct length` custom exception. """

    code = 'not_correct_length'
    msg_template = 'Field should be at least {min_length} and at most {max_length} characters long'


class NotCorrectLengthWithoutMinLength(PydanticValueError):
    """ `Not correct length without min length` custom exception. """

    code = 'not_correct_length'
    msg_template = 'Field should be at most {max_length} characters long'


class NotCorrectToken(PydanticValueError):
    """ `Not correct token` custom exception. """

    code = 'not_correct_token'
    msg_template = 'Token is not correct'


class EmailIsNotValidType(PydanticValueError):
    """ `Email is not valid type` custom exception. """

    code = 'email_is_not_valid_type'
    msg_template = 'Value is not a valid email type'


class PasswordsDoNotMatch(PydanticValueError):
    """ `Passwords do not match` custom exception. """

    code = 'passwords_do_not_match'
    msg_template = 'Passwords do not match'
