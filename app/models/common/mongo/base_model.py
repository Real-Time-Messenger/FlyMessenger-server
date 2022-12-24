from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, BaseConfig


class MongoModel(BaseModel):
    """
    Base model for all our Mongo models.

    This class is designed to convert a Pydantic model into a model ready to be
    populated into a database, as well as convert from data to a Pydantic model.

    Also, this class solves a popular problem like this:
        MongoDB has a field called "_id" as its unique key.

        In Python, we cannot use an underscore as a variable name or class attribute.

        We can only set the attribute - "id" in our Pydantic model, but at the same time,
        we must recreate our model dictionary (in the `from_mongo()` method)
        and overwrite the value from "_id" to "id".
    """

    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: str,
            ObjectId: str,
        }

    @classmethod
    def from_mongo(cls, data: dict):
        """ We must convert "_id" into "id". """

        if not data:
            return data
        id = data.pop('_id', None)

        if id:
            data['id'] = id
        return cls(**data)

    def mongo(self, **kwargs):
        """ Convert our model into a dictionary that can be populated into a database. """

        exclude_unset = kwargs.pop('exclude_unset', False)
        by_alias = kwargs.pop('by_alias', True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = parsed.pop('id')

        return parsed
