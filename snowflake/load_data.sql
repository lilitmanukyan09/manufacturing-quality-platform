-- load_data.sql
-- Stages local CSV files and loads them into Snowflake raw layer
-- Run after setup.sql and create_tables.sql
--
-- NOTE: PUT commands use absolute local file paths.
-- Update paths to match your local repository location before running.
-- All CSV files must be generated locally before running this script.
-- See README.md for script execution order.

USE DATABASE MANUFACTURING_QUALITY;
USE SCHEMA RAW;
-- ── Stage local files ────────────────────────────────────────────

PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/raw/ai4i2020.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/raw/machine_assignments.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/raw/operator_assignments.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/synthetic/machines.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/synthetic/maintenance_log.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/synthetic/operators.csv @manufacturing_raw_stage;
PUT file://C:/Users/Lilit/Lilit/Study/Projects/manufacturing-quality-platform/data/synthetic/shifts.csv @manufacturing_raw_stage;


-- ── Load staged files into raw tables ───────────────────────────

-- Source dataset
COPY INTO MANUFACTURING_QUALITY.RAW.ai4i_sensor_readings
FROM @manufacturing_raw_stage/ai4i2020.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Machine assignments
COPY INTO MANUFACTURING_QUALITY.RAW.machine_assignments
FROM @manufacturing_raw_stage/machine_assignments.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Operator assignments
COPY INTO MANUFACTURING_QUALITY.RAW.operator_assignments
FROM @manufacturing_raw_stage/operator_assignments.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Machines dimension
COPY INTO MANUFACTURING_QUALITY.RAW_SYNTHETIC.machines
FROM @manufacturing_raw_stage/machines.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Maintenance log
COPY INTO MANUFACTURING_QUALITY.RAW_SYNTHETIC.maintenance_log
FROM @manufacturing_raw_stage/maintenance_log.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Operators dimension
COPY INTO MANUFACTURING_QUALITY.RAW_SYNTHETIC.operators
FROM @manufacturing_raw_stage/operators.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');

-- Shifts dimension
COPY INTO MANUFACTURING_QUALITY.RAW_SYNTHETIC.shifts
FROM @manufacturing_raw_stage/shifts.csv
FILE_FORMAT = (FORMAT_NAME = 'MANUFACTURING_QUALITY.RAW.manufacturing_csv_format');