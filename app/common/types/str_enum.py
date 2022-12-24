from pydantic.types import Enum as PydanticEnum


class StrEnumBase(str, PydanticEnum):
    """
    Base class for string enums.

    Example:
    class MyEnum(StrEnumBase):
        A = "a"
        B = "b"

    # We can call `schema` method to get JSON schema for this enum
    MyEnum.schema()

    # output:
    {
        'type': 'string',
        'enum': ['a', 'b']
    }
    """
    @classmethod
    def schema(cls):
        return {
            "type": "string",
            "enum": [value for value in cls]
        }
