from datetime import datetime

from ..common.schemas import OrmBaseModel


class GpsSampleSchema(OrmBaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float
    pos_accuracy: float
    heading: float
    velocity: float
    vel_accuracy: float


class ImuSampleSchema(OrmBaseModel):
    timestamp: datetime
    acceleration_x_ms2: float
    acceleration_y_ms2: float
    acceleration_z_ms2: float
    angular_velocity_x_rads: float
    angular_velocity_y_rads: float
    angular_velocity_z_rads: float
    pitch_rad: float
    yaw_rad: float
    roll_rad: float
