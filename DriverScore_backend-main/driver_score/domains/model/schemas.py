from datetime import datetime

from ..common.schemas import OrmBaseModel


class DriverScoreInSchema(OrmBaseModel):
    timestamp: datetime
    score: float
