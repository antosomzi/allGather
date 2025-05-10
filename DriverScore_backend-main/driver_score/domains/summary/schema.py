from ..common.schemas import OrmBaseModel


class PivotTableByRCRangeSchema(OrmBaseModel):
    driver_name: str
    run_id: str
    # route: str
    RC_range: str
    score: int


class PivotTableByRCTypeSchema(OrmBaseModel):
    driver_id: int
    route: str
    RC_type: str
    RC_id: str
    score: int
