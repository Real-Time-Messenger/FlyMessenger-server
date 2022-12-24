from pydantic import BaseModel


class APIExceptionModel(BaseModel):
    """ Base model for base API exception class. """

    message: str
    code: int
