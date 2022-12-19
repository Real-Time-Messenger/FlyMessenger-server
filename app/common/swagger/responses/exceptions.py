from app.exception.api import APIException


"""
Swagger response exceptions example
"""

ACCOUNT_NOT_ACTIVATED = APIException.forbidden("Your account is not activated. Please activate your account.", translation_key="accountNotActivated")