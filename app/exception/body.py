from app.models.common.exceptions.body import RequestValidationDetails


class APIRequestValidationException(Exception):
    """ Base class for all API request validation exceptions. """

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

    @staticmethod
    def from_pydantic_error(error):
        return APIRequestValidationException.from_details(
            errors=[RequestValidationDetails(
                location=error['loc'][0],
                field=error['loc'][1] if len(error['loc']) > 1 else None,
                message=error['msg'],
                translation=error['type'],
            ) for error in error.errors()],
            code=422,
        )