from datetime import datetime
from enum import Enum

from pydantic_geojson import FeatureModel, LineStringModel

from ..common.schemas import OrmBaseModel


class RcType(str, Enum):
    CURVE = "curve"
    TANGENT = "tangent"


class RouteBasedRCSchema(FeatureModel):
    type: RcType
    id: int
    score: int
    geometry: LineStringModel
