from geoalchemy2.types import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from driver_score.core.database import Base
metadata = Base.metadata


class DissolvedRoute(Base):
    __tablename__ = "dissolved_route"

    dissolved_id = Column(Text, primary_key=True)
    geometry = Column(Geometry("LINESTRINGZ", 4326, spatial_index=False))


class CurveInventory(Base):
    __tablename__ = "curve_inventory"

    curve_id = Column(BigInteger, primary_key=True, autoincrement=True)
    dissolved_id = Column(ForeignKey("dissolved_route.dissolved_id"))
    c_type = Column(Text)
    c_radius = Column(Float)
    c_devangle = Column(Float)
    c_length = Column(Float)
    c_pc_x = Column(Float)
    c_pc_y = Column(Float)
    c_pt_x = Column(Float)
    c_pt_y = Column(Float)
    pc_lrs = Column(Float)
    pt_lrs = Column(Float)
    geometry = Column(Geometry("LINESTRING", 4326, dimension=3, spatial_index=False))

    dissolved_route = relationship("DissolvedRoute")


class Driver(Base):
    __tablename__ = "driver"

    driver_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text)
    age = Column(Integer)
    gender = Column(Text)
    driving_history = Column(Text)
    num_previous_accidents = Column(Text)
    mental_health_issues = Column(Text)


class Run(Base):
    __tablename__ = "run"

    run_id = Column(Text, primary_key=True)
    driver_id = Column(Integer, ForeignKey("driver.driver_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    driver = relationship("Driver")


class GpsSample(Base):
    __tablename__ = "gps_sample"

    run_id = Column(Text, ForeignKey("run.run_id"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    pos_accuracy = Column(Float)
    heading = Column(Float)
    velocity = Column(Float)
    vel_accuracy = Column(Float)
    geometry = Column(Geometry("POINT", 4326, spatial_index=False))

    run = relationship("Run")


class ImuSample(Base):
    __tablename__ = "imu_sample"

    run_id = Column(Text, ForeignKey("run.run_id"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    acceleration_x_ms2 = Column(Float)
    acceleration_y_ms2 = Column(Float)
    acceleration_z_ms2 = Column(Float)
    angular_velocity_x_rads = Column(Float)
    angular_velocity_y_rads = Column(Float)
    angular_velocity_z_rads = Column(Float)
    rotation_x_sin_theta_by_2 = Column(Float)
    rotation_y_sin_theta_by_2 = Column(Float)
    rotation_z_sin_theta_by_2 = Column(Float)
    pitch_rad = Column(Float)
    roll_rad = Column(Float)
    yaw_rad = Column(Float)

    run = relationship("Run")


class RoadCharacteristic(Base):
    __tablename__ = "road_characteristic"
    __table_args__ = (
        ForeignKeyConstraint(
            ["run_id", "timestamp"], ["gps_sample.run_id", "gps_sample.timestamp"]
        ),
    )

    run_id = Column(Text, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    dissolved_id = Column(Text, ForeignKey("dissolved_route.dissolved_id"))
    gps_lrs = Column(Float)
    driving_direction = Column(Text)
    curvature = Column(Float)
    superelevation = Column(Float)
    grade = Column(Float)
    intersection = Column(Boolean)
    u_turn = Column(Boolean)

    dissolved_route = relationship("DissolvedRoute")
    gps_sample = relationship("GpsSample")


class Score(Base):
    __tablename__ = "score"
    __table_args__ = (
        ForeignKeyConstraint(
            ["run_id", "timestamp"], ["gps_sample.run_id", "gps_sample.timestamp"]
        ),
    )

    run_id = Column(Text, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    score = Column(Float)

    gps_sample = relationship("GpsSample")


class UploadLog(Base):
    __tablename__ = "upload_log"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    uploaded_by = Column(BigInteger, ForeignKey("driver.driver_id"), nullable=False)
    uploaded_on = Column(DateTime)
    upload_status = Column(Text)
    log_message = Column(Text)
    file_name = Column(Text)

    driver = relationship("Driver")


class CollectedDataFile(Base):
    __tablename__ = "collected_data_file"

    file_id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    file_name = Column(Text)
    collected_by = Column(BigInteger, ForeignKey("driver.driver_id"), nullable=False)
    collected_on = Column(DateTime)

    driver = relationship("Driver")