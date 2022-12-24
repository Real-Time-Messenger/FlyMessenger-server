from app.exception.api import APIException
from app.models.common.exceptions.api import APIExceptionModel
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails

"""
API exception shorthands

We can use these shorthands in any place where we need to return an API exception.
"""

USER_NOT_ACTIVATED = APIException.forbidden("Your account is not activated. Please activate your account.", translation_key="accountNotActivated")

USER_NOT_AUTHORIZED = APIException.unauthorized("You are not logged in. Please log in.", translation_key="userNotLoggedIn")
USER_NOT_AUTHORIZED_SCHEMA = APIExceptionModel.schema()