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
