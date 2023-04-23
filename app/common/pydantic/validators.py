from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr

from app.models.common.exceptions.body import NotCorrectLength, EmailIsNotValidType, PasswordsDoNotMatch, \
    NotCorrectToken, NotCorrectLengthWithoutMinLength, InvalidCharacters


def email_validator(email: EmailStr) -> EmailStr:
    """ Validate email for valid domain and length. """

    if not len(email) >= 3 and len(email) <= 255:
        raise NotCorrectLength(min_length=3, max_length=255, translation_key="emailHasIncorrectLength")

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise EmailIsNotValidType(translation_key="emailIsNotValid")

    return email


def username_validator(cls, username: str) -> str:
    """ Validate username for length. """

    if not len(username) >= 3 and len(username) <= 50:
        raise NotCorrectLength(min_length=3, max_length=50, translation_key="usernameHasIncorrectLength")

    if not username.isalnum() and not username.replace(".", "").isalnum() and not username.replace("_", "").isalnum():
        raise InvalidCharacters(translation_key="usernameHasInvalidCharacters")

    return username


def first_name_validator(cls, first_name: str) -> str:
    """ Validate first name for length. """

    if not len(first_name) >= 3 and len(first_name) <= 25:
        raise NotCorrectLength(min_length=3, max_length=25, translation_key="firstNameHasIncorrectLength")

    return first_name


def last_name_validator(cls, last_name: str) -> str:
    """ Validate last name for length. """

    if len(last_name) > 25:
        raise NotCorrectLengthWithoutMinLength(max_length=25, translation_key="lastNameHasIncorrectLength")

    return last_name


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


def passwords_match_validator(cls, values: dict) -> dict:
    """ Validate passwords match. """

    password = values.get("password")
    password_confirm = values.get("password_confirm")

    if password != password_confirm:
        raise PasswordsDoNotMatch(translation_key="passwordsDoNotMatch")

    return values


def token_validator(cls, token: str) -> str:
    """ Validate token for length. """

    if not len(token) >= 10 and len(token) <= 1000:
        raise NotCorrectToken(translation_key="tokenIsNotCorrect")

    return token
