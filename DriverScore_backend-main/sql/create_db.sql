CREATE EXTENSION postgis;

-- CREATE TABLE route_inventory (
--     dissolved_id TEXT PRIMARY KEY,
--     fid BIGSERIAL,
--     rcd TEXT,
--     speed_limit INTEGER,
--     fmeas DOUBLE PRECISION,
--     tmeas DOUBLE PRECISION,
--     geometry GEOMETRY(MULTILINESTRING, 4326)
-- );
-- CREATE TABLE dissolved_route (
--     dissolved_id TEXT PRIMARY KEY,
--     geometry GEOMETRY(MULTILINESTRING, 4326)
-- );
-- We use POINT instead of LINESTRING because:
-- 1. Point is more granular to control over
-- 2. A Point can be referred to different RCs, such as uphill/downhill/intersection.
--	  Cannot do the same to Linestrings.
--
-- Whenever we have a new RC, we create a new table and add foreign key in route.
CREATE TABLE dissolved_route (
	dissolved_id TEXT PRIMARY KEY,
	geometry GEOMETRY(LINESTRINGZ, 4326)
);

CREATE INDEX idx_dissolved_route_geometry ON dissolved_route USING GIST (geometry);

CREATE TABLE curve_inventory (
	curve_id BIGSERIAL PRIMARY KEY,
	dissolved_id TEXT REFERENCES dissolved_route(dissolved_id),
	c_type TEXT,
	c_radius DOUBLE PRECISION,
	c_devangle DOUBLE PRECISION,
	c_length DOUBLE PRECISION,
	c_pc_x DOUBLE PRECISION,
	c_pc_y DOUBLE PRECISION,
	c_pt_x DOUBLE PRECISION,
	c_pt_y DOUBLE PRECISION,
	pc_lrs DOUBLE PRECISION,
	pt_lrs DOUBLE PRECISION,
	geometry GEOMETRY(LINESTRING, 4326, 3)
);

CREATE INDEX idx_curve_inventory_geometry ON curve_inventory USING GIST (geometry);

CREATE TABLE driver (
	driver_id BIGSERIAL PRIMARY KEY,
	name TEXT,
	age INTEGER,
	gender TEXT,
	driving_history TEXT,
	num_previous_accidents TEXT,
	mental_health_issues TEXT
);

CREATE TABLE run (
	run_id TEXT PRIMARY KEY,
	driver_id INTEGER REFERENCES driver(driver_id),
	start_time TIMESTAMP,
	end_time TIMESTAMP
);

CREATE TABLE gps_sample (
	-- file_id BIGSERIAL REFERENCES collected_data_file(file_id),
	run_id TEXT REFERENCES run(run_id),
	timestamp TIMESTAMP,
	latitude DOUBLE PRECISION,
	longitude DOUBLE PRECISION,
	altitude DOUBLE PRECISION,
	pos_accuracy DOUBLE PRECISION,
	heading DOUBLE PRECISION,
	velocity DOUBLE PRECISION,
	vel_accuracy DOUBLE PRECISION,
	geometry GEOMETRY(POINT, 4326),
	PRIMARY KEY (run_id, timestamp)
);

CREATE TABLE imu_sample (
	run_id TEXT REFERENCES run(run_id),
	-- file_id BIGSERIAL REFERENCES collected_data_file(file_id),
	timestamp TIMESTAMP,
	acceleration_x_ms2 DOUBLE PRECISION,
	acceleration_y_ms2 DOUBLE PRECISION,
	acceleration_z_ms2 DOUBLE PRECISION,
	angular_velocity_x_rads DOUBLE PRECISION,
	angular_velocity_y_rads DOUBLE PRECISION,
	angular_velocity_z_rads DOUBLE PRECISION,
	rotation_x_sin_theta_by_2 DOUBLE PRECISION,
	rotation_y_sin_theta_by_2 DOUBLE PRECISION,
	rotation_z_sin_theta_by_2 DOUBLE PRECISION,
	pitch_rad DOUBLE PRECISION,
	roll_rad DOUBLE PRECISION,
	yaw_rad DOUBLE PRECISION,
	PRIMARY KEY (run_id, timestamp)
);

CREATE TABLE road_characteristic (
	run_id TEXT,
	timestamp timestamp,
	dissolved_id TEXT REFERENCES dissolved_route(dissolved_id),
	gps_lrs float,
	driving_direction TEXT,
	curvature float,
	superelevation float,
	grade float,
	intersection boolean,
	u_turn boolean,
	FOREIGN KEY (run_id, timestamp) REFERENCES gps_sample(run_id, timestamp),
	PRIMARY KEY (run_id, timestamp)
);

CREATE TABLE score (
	run_id TEXT,
	timestamp timestamp,
	score float,
	PRIMARY KEY (run_id, timestamp),
	FOREIGN KEY (run_id, timestamp) REFERENCES gps_sample(run_id, timestamp)
);

CREATE TABLE upload_log (
	log_id BIGSERIAL PRIMARY KEY,
	uploaded_by BIGSERIAL REFERENCES driver(driver_id),
	uploaded_on TIMESTAMP,
	upload_status TEXT,
	log_message TEXT,
	file_name TEXT
);

CREATE TABLE collected_data_file (
	file_id BIGSERIAL PRIMARY KEY,
	file_name TEXT,
	collected_by BIGSERIAL REFERENCES driver(driver_id),
	collected_on TIMESTAMP -- TODO: Synchronize these fields later
	--    ploaded_by INTEGER REFERENCES userprofile(id),
	--    uploaded_on TIMESTAMP,
	--    proc_status TEXT
);

CREATE INDEX idx_file_id ON collected_data_file(file_id);
