from copy import deepcopy
from typing import Callable

from email_validator import EmailNotValidError, validate_email
from pydantic import validator, EmailStr
from pydantic.typing import AnyCallable

from app.exception.api import APIException
from app.models.common.exceptions.body import NotCorrectLength, EmailIsNotValidType, PasswordsDoNotMatch

def email_validator(email: EmailStr) -> EmailStr:
    """ Validate email for valid domain and length. """

    if not len(email) >= 3 and len(email) <= 255:
        raise NotCorrectLength(min_length=3, max_length=255, translation_key="emailHasIncorrectLength")

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise EmailIsNotValidType(translation_key="emailHasIncorrectDomain")

    return email

def username_validator(cls, username: str) -> str:
    """ Validate username for length. """

    if not len(username) >= 3 and len(username) <= 50:
        raise NotCorrectLength(min_length=3, max_length=50, translation_key="usernameHasIncorrectLength")

    return username

def password_validator(cls, password: str) -> str:
    """ Validate password for length. """

    if not len(password) >= 8 and len(password) <= 32:
        raise NotCorrectLength(min_length=8, max_length=32, translation_key="passwordHasIncorrectLength")

    return password

def password_confirm_validator(cls, password: str) -> str:
    """ Validate password for length. """

    if not len(password) >= 8 and len(password) <= 32:
        raise NotCorrectLength(min_length=8, max_length=32, translation_key="passwordConfirmHasIncorrectLength")

    return password


# make pydantic validator for passwords match
def passwords_match_validator(cls, values: dict) -> dict:
    """ Validate passwords match. """

    password = values.get("password")
    password_confirm = values.get("password_confirm")

    if password != password_confirm:
        raise PasswordsDoNotMatch(translation_key="passwordsDoNotMatch")

    return values

# example of usage
# _passwords_match_validator = validator("password", "password_confirm", pre=True)(passwords_match_validator)