-- Docker-compatible database schema
-- Generated from current_schema.sql - Cleaned for Docker PostgreSQL
-- Removed all OWNER TO references for compatibility

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Homebrew)
-- Dumped by pg_dump version 14.17 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);

--
-- Name: collected_data_file; Type: TABLE; Schema: public
--

CREATE TABLE public.collected_data_file (
    file_id bigint NOT NULL,
    file_name text,
    collected_by bigint NOT NULL,
    collected_on timestamp without time zone
);

--
-- Name: collected_data_file_file_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.collected_data_file_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: collected_data_file_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.collected_data_file_file_id_seq OWNED BY public.collected_data_file.file_id;

--
-- Name: curve_inventory; Type: TABLE; Schema: public
--

CREATE TABLE public.curve_inventory (
    curve_id bigint NOT NULL,
    dissolved_id text,
    c_type text,
    c_radius double precision,
    c_devangle double precision,
    c_length double precision,
    c_pc_x double precision,
    c_pc_y double precision,
    c_pt_x double precision,
    c_pt_y double precision,
    pc_lrs double precision,
    pt_lrs double precision,
    geometry public.geometry(LineString,4326)
);

--
-- Name: curve_inventory_curve_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.curve_inventory_curve_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: curve_inventory_curve_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.curve_inventory_curve_id_seq OWNED BY public.curve_inventory.curve_id;

--
-- Name: dissolved_route; Type: TABLE; Schema: public
--

CREATE TABLE public.dissolved_route (
    dissolved_id text NOT NULL,
    geometry public.geometry(LineStringZ,4326)
);

--
-- Name: driver; Type: TABLE; Schema: public
--

CREATE TABLE public.driver (
    driver_id bigint NOT NULL,
    name text,
    age integer,
    gender text,
    driving_history text,
    num_previous_accidents text,
    mental_health_issues text
);

--
-- Name: driver_driver_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.driver_driver_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: driver_driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.driver_driver_id_seq OWNED BY public.driver.driver_id;

--
-- Name: gps_sample; Type: TABLE; Schema: public
--

CREATE TABLE public.gps_sample (
    run_id text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    latitude double precision,
    longitude double precision,
    altitude double precision,
    pos_accuracy double precision,
    heading double precision,
    velocity double precision,
    vel_accuracy double precision,
    geometry public.geometry(Point,4326)
);

--
-- Name: imu_sample; Type: TABLE; Schema: public
--

CREATE TABLE public.imu_sample (
    run_id text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    acceleration_x_ms2 double precision,
    acceleration_y_ms2 double precision,
    acceleration_z_ms2 double precision,
    angular_velocity_x_rads double precision,
    angular_velocity_y_rads double precision,
    angular_velocity_z_rads double precision,
    rotation_x_sin_theta_by_2 double precision,
    rotation_y_sin_theta_by_2 double precision,
    rotation_z_sin_theta_by_2 double precision,
    pitch_rad double precision,
    roll_rad double precision,
    yaw_rad double precision
);

--
-- Name: road_characteristic; Type: TABLE; Schema: public
--

CREATE TABLE public.road_characteristic (
    run_id text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    dissolved_id text,
    gps_lrs double precision,
    driving_direction text,
    curvature double precision,
    superelevation double precision,
    grade double precision,
    intersection boolean,
    u_turn boolean
);

--
-- Name: run; Type: TABLE; Schema: public
--

CREATE TABLE public.run (
    run_id text NOT NULL,
    driver_id integer,
    start_time timestamp without time zone,
    end_time timestamp without time zone
);

--
-- Name: score; Type: TABLE; Schema: public
--

CREATE TABLE public.score (
    run_id text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    score double precision
);

--
-- Name: upload_log; Type: TABLE; Schema: public
--

CREATE TABLE public.upload_log (
    log_id bigint NOT NULL,
    uploaded_by bigint NOT NULL,
    uploaded_on timestamp without time zone,
    upload_status text,
    log_message text,
    file_name text
);

--
-- Name: upload_log_log_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.upload_log_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: upload_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.upload_log_log_id_seq OWNED BY public.upload_log.log_id;

--
-- Name: collected_data_file file_id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.collected_data_file ALTER COLUMN file_id SET DEFAULT nextval('public.collected_data_file_file_id_seq'::regclass);

--
-- Name: curve_inventory curve_id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.curve_inventory ALTER COLUMN curve_id SET DEFAULT nextval('public.curve_inventory_curve_id_seq'::regclass);

--
-- Name: driver driver_id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.driver ALTER COLUMN driver_id SET DEFAULT nextval('public.driver_driver_id_seq'::regclass);

--
-- Name: upload_log log_id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.upload_log ALTER COLUMN log_id SET DEFAULT nextval('public.upload_log_log_id_seq'::regclass);

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);

--
-- Name: collected_data_file collected_data_file_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.collected_data_file
    ADD CONSTRAINT collected_data_file_pkey PRIMARY KEY (file_id);

--
-- Name: curve_inventory curve_inventory_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.curve_inventory
    ADD CONSTRAINT curve_inventory_pkey PRIMARY KEY (curve_id);

--
-- Name: dissolved_route dissolved_route_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.dissolved_route
    ADD CONSTRAINT dissolved_route_pkey PRIMARY KEY (dissolved_id);

--
-- Name: driver driver_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_pkey PRIMARY KEY (driver_id);

--
-- Name: gps_sample gps_sample_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.gps_sample
    ADD CONSTRAINT gps_sample_pkey PRIMARY KEY (run_id, "timestamp");

--
-- Name: imu_sample imu_sample_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.imu_sample
    ADD CONSTRAINT imu_sample_pkey PRIMARY KEY (run_id, "timestamp");

--
-- Name: road_characteristic road_characteristic_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.road_characteristic
    ADD CONSTRAINT road_characteristic_pkey PRIMARY KEY (run_id, "timestamp");

--
-- Name: run run_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.run
    ADD CONSTRAINT run_pkey PRIMARY KEY (run_id);

--
-- Name: score score_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.score
    ADD CONSTRAINT score_pkey PRIMARY KEY (run_id, "timestamp");

--
-- Name: upload_log upload_log_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.upload_log
    ADD CONSTRAINT upload_log_pkey PRIMARY KEY (log_id);

--
-- Name: ix_collected_data_file_file_id; Type: INDEX; Schema: public
--

CREATE INDEX ix_collected_data_file_file_id ON public.collected_data_file USING btree (file_id);

--
-- Name: collected_data_file collected_data_file_collected_by_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.collected_data_file
    ADD CONSTRAINT collected_data_file_collected_by_fkey FOREIGN KEY (collected_by) REFERENCES public.driver(driver_id);

--
-- Name: curve_inventory curve_inventory_dissolved_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.curve_inventory
    ADD CONSTRAINT curve_inventory_dissolved_id_fkey FOREIGN KEY (dissolved_id) REFERENCES public.dissolved_route(dissolved_id);

--
-- Name: gps_sample gps_sample_run_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.gps_sample
    ADD CONSTRAINT gps_sample_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.run(run_id);

--
-- Name: imu_sample imu_sample_run_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.imu_sample
    ADD CONSTRAINT imu_sample_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.run(run_id);

--
-- Name: road_characteristic road_characteristic_dissolved_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.road_characteristic
    ADD CONSTRAINT road_characteristic_dissolved_id_fkey FOREIGN KEY (dissolved_id) REFERENCES public.dissolved_route(dissolved_id);

--
-- Name: road_characteristic road_characteristic_run_id_timestamp_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.road_characteristic
    ADD CONSTRAINT road_characteristic_run_id_timestamp_fkey FOREIGN KEY (run_id, "timestamp") REFERENCES public.gps_sample(run_id, "timestamp");

--
-- Name: run run_driver_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.run
    ADD CONSTRAINT run_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(driver_id);

--
-- Name: score score_run_id_timestamp_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.score
    ADD CONSTRAINT score_run_id_timestamp_fkey FOREIGN KEY (run_id, "timestamp") REFERENCES public.gps_sample(run_id, "timestamp");

--
-- Name: upload_log upload_log_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.upload_log
    ADD CONSTRAINT upload_log_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.driver(driver_id);

--
-- PostgreSQL database dump complete
--