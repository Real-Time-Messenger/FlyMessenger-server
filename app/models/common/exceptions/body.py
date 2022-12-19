from pydantic import BaseModel, PydanticValueError


class RequestValidationDetails(BaseModel):
    location: str
    message: str
    field: str | None = None
    translation: str | None = None


class APIRequestValidationModel(BaseModel):
    details: list[RequestValidationDetails]
    code: int


class NotCorrectLength(PydanticValueError):
    code = 'not_correct_length'
    msg_template = 'Field should be at least {min_length} and at most {max_length} characters long'

class EmailIsNotValidType(PydanticValueError):
    code = 'email_is_not_valid_type'
    msg_template = 'Value is not a valid email type'

class PasswordsDoNotMatch(PydanticValueError):
    code = 'passwords_do_not_match'
    msg_template = 'Passwords do not match'