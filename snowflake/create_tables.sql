-- create_tables.sql
-- Creates all raw layer tables for the Manufacturing Quality Platform
-- Run once after setup.sql
-- Schemas: MANUFACTURING_QUALITY.RAW and MANUFACTURING_QUALITY.RAW_SYNTHETIC


-- Source dataset
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW.ai4i_sensor_readings
(
    udi INT PRIMARY KEY,
    product_id VARCHAR,
    type VARCHAR,
    air_temperature FLOAT,
    process_temperature FLOAT,
    rotational_speed INT,
    torque FLOAT,
    tool_wear INT,
    machine_failure INT,
    twf INT,
    hdf INT,
    pwf INT,
    osf INT,
    rnf INT
);


-- Machine assignments
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW.machine_assignments
(
    udi INT PRIMARY KEY,
    machine_id VARCHAR,
    tool_wear INT,
    is_reset_point BOOLEAN,
    tool_life_number INT
);


-- Operator assignments
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW.operator_assignments
(
    udi INT PRIMARY KEY,
    machine_id VARCHAR,
    operator_id VARCHAR
);


-- Machines dimension
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW_SYNTHETIC.machines
(
    machine_id VARCHAR PRIMARY KEY,
    machine_type VARCHAR,
    manufacturer VARCHAR,
    installation_date TIMESTAMP_NTZ,
    rated_tool_life_min INT,
    location_in_plant VARCHAR,
    is_active BOOLEAN
);


-- Maintenance log
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW_SYNTHETIC.maintenance_log
(
    maintenance_id VARCHAR PRIMARY KEY,
    machine_id VARCHAR,
    udi INT,
    maintenance_date TIMESTAMP_NTZ,
    maintenance_type VARCHAR,
    tool_replaced_flag BOOLEAN,
    duration_min INT
);


-- Operators dimension
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW_SYNTHETIC.operators
(
    operator_id VARCHAR PRIMARY KEY,
    experience_level VARCHAR,
    hire_date DATE,
    certification_type VARCHAR,
    primary_shift VARCHAR
);


-- Shifts dimension
CREATE TABLE IF NOT EXISTS MANUFACTURING_QUALITY.RAW_SYNTHETIC.shifts
(
    shift_id VARCHAR PRIMARY KEY,
    shift_name VARCHAR,
    shift_date DATE,
    shift_start TIMESTAMP_NTZ,
    shift_end TIMESTAMP_NTZ,
    supervisor_id VARCHAR
);