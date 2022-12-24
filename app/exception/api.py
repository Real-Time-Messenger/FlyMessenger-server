from typing import Union

from fastapi import status


class APIException(Exception):
    """ Base class for all API exceptions. """

    def __init__(self, code: int, message: str, translation_key: Union[str, None] = None):
        self.code = code
        self.message = message
        self.translation_key = translation_key

    def __str__(self):
        return 'APIException(code={}, message={}, translation={})'.format(self.code, self.message, self.translation_key)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def bad_request(message: str, translation_key: Union[str, None] = None):
        return APIException(code=status.HTTP_400_BAD_REQUEST, message=message, translation_key=translation_key)

    @staticmethod
    def unauthorized(message: str, translation_key: Union[str, None] = None):
        return APIException(code=status.HTTP_401_UNAUTHORIZED, message=message, translation_key=translation_key)

    @staticmethod
    def forbidden(message: str, translation_key: Union[str, None] = None):
        return APIException(code=status.HTTP_403_FORBIDDEN, message=message, translation_key=translation_key)

    @staticmethod
    def not_found(message: str, translation_key: Union[str, None] = None):
        return APIException(code=status.HTTP_404_NOT_FOUND, message=message, translation_key=translation_key)

