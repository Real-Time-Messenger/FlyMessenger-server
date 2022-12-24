from pydantic import Field, BaseModel


class SkipAndLimitModel(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)