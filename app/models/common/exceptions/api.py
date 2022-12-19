from pydantic import BaseModel


class APIExceptionModel(BaseModel):
    message: str
    code: int
