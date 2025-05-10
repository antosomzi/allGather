from datetime import datetime

from pydantic_geojson import FeatureModel, LineStringModel

from ..common.schemas import OrmBaseModel


class RunSchema(OrmBaseModel):
    run_id: str
    driver_id: int
    start_time: datetime
    # TODO: Add end_time later
    # end_timestamp: datetime


class DriverScorePropertiesSchema(OrmBaseModel):
    driver_id: int
    timestamps: list[datetime]
    scores: list[float]
    lrs: list[float | None]


class DriverScoreOutSchema(FeatureModel):
    properties: DriverScorePropertiesSchema
    geometry: LineStringModel


class RunBasedRCSchema(OrmBaseModel):
    run_id: str
    timestamp: datetime
    dissolved_id: str
    gps_lrs: float
    driving_direction: str
    curvature: float
    superelevation: float | None = None
    grade: float | None = None
    intersection: str | None = None
    u_turn: bool | None = None
