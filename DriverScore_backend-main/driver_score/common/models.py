from geoalchemy2.types import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.orm import relationship


from driver_score.core.database import Base
metadata = Base.metadata

class DissolvedRoute(Base):
    __tablename__ = "dissolved_route"

    dissolved_id = Column(Text, primary_key=True)
    geometry = Column(Geometry("LINESTRINGZ", 4326, 3, from_text="ST_GeomFromEWKT", name="geometry"), index=True)


class Driver(Base):
    __tablename__ = "driver"

    driver_id = Column(BigInteger, primary_key=True, server_default=text("nextval('driver_driver_id_seq'::regclass)"))
    name = Column(Text)
    age = Column(Integer)
    gender = Column(Text)
    driving_history = Column(Text)
    num_previous_accidents = Column(Text)
    mental_health_issues = Column(Text)


t_geography_columns = Table(
    "geography_columns",
    metadata,
    Column("f_table_catalog", String),
    Column("f_table_schema", String),
    Column("f_table_name", String),
    Column("f_geography_column", String),
    Column("coord_dimension", Integer),
    Column("srid", Integer),
    Column("type", Text),
)


t_geometry_columns = Table(
    "geometry_columns",
    metadata,
    Column("f_table_catalog", String(256)),
    Column("f_table_schema", String),
    Column("f_table_name", String),
    Column("f_geometry_column", String),
    Column("coord_dimension", Integer),
    Column("srid", Integer),
    Column("type", String(30)),
)


class SpatialRefSy(Base):
    __tablename__ = "spatial_ref_sys"
    __table_args__ = (CheckConstraint("(srid > 0) AND (srid <= 998999)"),)

    srid = Column(Integer, primary_key=True)
    auth_name = Column(String(256))
    auth_srid = Column(Integer)
    srtext = Column(String(2048))
    proj4text = Column(String(2048))


class CollectedDataFile(Base):
    __tablename__ = "collected_data_file"

    file_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        server_default=text("nextval('collected_data_file_file_id_seq'::regclass)"),
    )
    file_name = Column(Text)
    collected_by = Column(
        ForeignKey("driver.driver_id"),
        nullable=False,
        server_default=text("nextval('collected_data_file_collected_by_seq'::regclass)"),
    )
    collected_on = Column(DateTime)

    driver = relationship("Driver")


class CurveInventory(Base):
    __tablename__ = "curve_inventory"

    curve_id = Column(
        BigInteger, primary_key=True, server_default=text("nextval('curve_inventory_curve_id_seq'::regclass)")
    )
    dissolved_id = Column(ForeignKey("dissolved_route.dissolved_id"))
    c_type = Column(Text)
    c_radius = Column(Float(53))
    c_devangle = Column(Float(53))
    c_length = Column(Float(53))
    c_pc_x = Column(Float(53))
    c_pc_y = Column(Float(53))
    c_pt_x = Column(Float(53))
    c_pt_y = Column(Float(53))
    pc_lrs = Column(Float(53))
    pt_lrs = Column(Float(53))
    geometry = Column(Geometry("LINESTRING", 4326, from_text="ST_GeomFromEWKT", name="geometry"), index=True)

    dissolved = relationship("DissolvedRoute")


class Run(Base):
    __tablename__ = "run"

    run_id = Column(Text, primary_key=True)
    driver_id = Column(ForeignKey("driver.driver_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    driver = relationship("Driver")


class UploadLog(Base):
    __tablename__ = "upload_log"

    log_id = Column(BigInteger, primary_key=True, server_default=text("nextval('upload_log_log_id_seq'::regclass)"))
    uploaded_by = Column(
        ForeignKey("driver.driver_id"),
        nullable=False,
        server_default=text("nextval('upload_log_uploaded_by_seq'::regclass)"),
    )
    uploaded_on = Column(DateTime)
    upload_status = Column(Text)
    log_message = Column(Text)
    file_name = Column(Text)

    driver = relationship("Driver")


class GpsSample(Base):
    __tablename__ = "gps_sample"

    run_id = Column(ForeignKey("run.run_id"), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    latitude = Column(Float(53))
    longitude = Column(Float(53))
    altitude = Column(Float(53))
    pos_accuracy = Column(Float(53))
    heading = Column(Float(53))
    velocity = Column(Float(53))
    vel_accuracy = Column(Float(53))
    geometry = Column(Geometry("POINT", 4326, spatial_index=False, from_text="ST_GeomFromEWKT", name="geometry"))

    run = relationship("Run")


class RoadCharacteristic(Base):
    __tablename__ = "road_characteristic"
    __table_args__ = (ForeignKeyConstraint(["run_id", "timestamp"], ["gps_sample.run_id", "gps_sample.timestamp"]),)

    run_id = Column(Text, primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    dissolved_id = Column(ForeignKey("dissolved_route.dissolved_id"))
    gps_lrs = Column(Float(53))
    driving_direction = Column(Text)
    curvature = Column(Float(53))
    superelevation = Column(Float(53))
    grade = Column(Float(53))
    intersection = Column(Boolean)
    u_turn = Column(Boolean)

    dissolved = relationship("DissolvedRoute")
    gps_samples = relationship("GpsSample")


class Score(Base):
    __tablename__ = "score"
    __table_args__ = (ForeignKeyConstraint(["run_id", "timestamp"], ["gps_sample.run_id", "gps_sample.timestamp"]),)

    run_id = Column(Text, primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    score = Column(Float(53))

    gps_samples = relationship("GpsSample")


class ImuSample(Base):
    __tablename__ = "imu_sample"

    run_id = Column(ForeignKey("run.run_id"), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    acceleration_x_ms2 = Column(Float(53))
    acceleration_y_ms2 = Column(Float(53))
    acceleration_z_ms2 = Column(Float(53))
    angular_velocity_x_rads = Column(Float(53))
    angular_velocity_y_rads = Column(Float(53))
    angular_velocity_z_rads = Column(Float(53))
    rotation_x_sin_theta_by_2 = Column(Float(53))
    rotation_y_sin_theta_by_2 = Column(Float(53))
    rotation_z_sin_theta_by_2 = Column(Float(53))
    pitch_rad = Column(Float(53))
    roll_rad = Column(Float(53))
    yaw_rad = Column(Float(53))

    run = relationship("Run")
