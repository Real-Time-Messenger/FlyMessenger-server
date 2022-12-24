from enum import Enum


class AuthResponseType(str, Enum):
    """
    Response types for auth.

    This is how we let the client know what needs to be done.

    For example, if we received `TWO_FACTOR` upon login, then we will redirect to the two-factor authentication page.
    """

    ACTIVATION_REQUIRED = "ACTIVATION_REQUIRED"
    TWO_FACTOR = "TWO_FACTOR"
    NEW_DEVICE = "NEW_DEVICE"
