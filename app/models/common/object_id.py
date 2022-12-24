from bson import ObjectId

from app.models.common.exceptions.body import InvalidObjectId


class PyObjectId(ObjectId):
    """ Custom ObjectId type for Pydantic models. """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise InvalidObjectId(translation_key="idIsNotCorrect")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")