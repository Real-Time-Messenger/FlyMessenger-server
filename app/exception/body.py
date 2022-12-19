from app.models.common.exceptions.body import RequestValidationDetails


class APIRequestValidationException(Exception):
    def __init__(self, details: list, code: int):
        self.details = details
        self.code = code

    def __str__(self):
        return 'APIRequestValidationError(details={}, code={})'.format(self.details, self.code)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_details(errors: list[RequestValidationDetails], code: int = 422):
        return APIRequestValidationException(details=errors, code=code)