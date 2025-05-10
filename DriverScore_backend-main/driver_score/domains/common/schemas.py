from pydantic import BaseModel


class OrmBaseModel(BaseModel):
    class Config:
        from_attributes = True  # for orm
        extra = "ignore"  # ignore undefined fields
