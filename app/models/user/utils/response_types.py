from enum import Enum


class AuthResponseType(str, Enum):
    TWO_FACTOR = "TWO_FACTOR"
    NEW_DEVICE = "NEW_DEVICE"
