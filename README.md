# Manufacturing Process Quality Intelligence Platform

## Overview

A dbt-based analytics engineering portfolio project modeling predictive maintenance data to identify process parameter patterns that precede quality failure events.

**Business Question:** For each recorded failure, what was the state of every process parameter in the 5, 10, and 20 operating cycles preceding it — and which parameters show the most consistent deviation from their product-variant baseline before failure occurs?

**Stack:** Python · dbt Core · Snowflake · Power BI

## Dataset

AI4I 2020 Predictive Maintenance Dataset  
Source: UCI Machine Learning Repository  
URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

Note: Synthetic dataset. Companion dimension tables are also synthetically generated — see `data/README.md` for methodology.

## Architecture

The project follows a layered dbt architecture:

- **Raw Layer (Snowflake)** — 7 raw tables loaded via COPY INTO
- **Staging Layer (dbt views)** — 7 staging models that clean and prepare raw data
- **Intermediate Layer (dbt views)** — [To be built in Stage 3]
- **Marts Layer (dbt tables)** — [To be built in Stage 4]

Data flows: Raw → Staging → Intermediate → Marts → Power BI

View the data lineage with `dbt docs serve` after running `dbt docs generate`.

## Project Structure
```
manufacturing-quality-platform/
├── dbt/                          # dbt transformation project
│   ├── models/
│   │   ├── staging/              # Raw data staging layer (7 models)
│   │   │   ├── stg_ai4i__*.sql
│   │   │   ├── stg_synthetic__*.sql
│   │   │   ├── sources.yml
│   │   │   └── schema.yml
│   │   ├── intermediate/         # Transformation logic (Phase 2)
│   │   └── marts/                # Analytical output (Phase 3)
│   ├── tests/                    # Custom singular tests
│   ├── macros/                   # Reusable SQL/Jinja functions
│   ├── dbt_project.yml
│   └── packages.yml
├── data/
│   ├── raw/                      # Source CSVs — not committed
│   ├── synthetic/                # Generated dimension tables — not committed
│   └── README.md
├── scripts/                      # Python data generation scripts
├── snowflake/                    # Snowflake SQL setup and load scripts
│   ├── setup.sql
│   ├── create_tables.sql
│   └── load_data.sql
├── docs/                         # Architecture diagrams and documentation
├── .env.example
├── .gitignore
├── profiles.yml.example          # dbt Snowflake profile template
├── requirements.txt              # Python dependencies
└── README.md
```

## Prerequisites

- Python 3.13+
- git 2.34+
- pip 26.1+
- Snowflake account

## Local Setup

### Installation

1. Clone the repository

```bash
git clone https://github.com/lilitmanukyan09/manufacturing-quality-platform.git
cd manufacturing-quality-platform
```

2. Create and activate virtual environment

```bash
py -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment

```bash
copy .env.example .env
```

Fill in your Snowflake credentials in `.env`

5. Configure dbt profile

Copy `profiles.yml.example` to `C:\Users\YOURNAME\.dbt\profiles.yml`

Replace YOURNAME with your Windows username — run `echo %USERNAME%` in your terminal to confirm it.

Fill in your Snowflake account details and credentials (using key pair authentication recommended).

## Running the Project

### Stage 1: Generate Synthetic Data

[Complete] Generate all companion dimension tables and machine assignments from the source dataset.

```bash
python scripts/generate_machine_assignments.py
python scripts/generate_machines.py
python scripts/generate_maintenance_log.py
python scripts/generate_shifts.py
python scripts/generate_operators.py
python scripts/generate_operator_assignments.py
```

Before running: place `ai4i2020.csv` in `data/raw/`

### Stage 2: Set Up dbt and Snowflake

[Complete] Snowflake environment configured, dbt project initialized, staging layer built with 7 transformation models and 35+ data quality tests.

**To reproduce or verify:**

1. Configure Snowflake infrastructure

```bash
# From Snowsight or SnowSQL
snowsql -a <account_id> -u <username> -f snowflake/setup.sql
snowsql -a <account_id> -u <username> -f snowflake/create_tables.sql
snowsql -a <account_id> -u <username> -f snowflake/load_data.sql
```

2. Verify dbt connection

```bash
cd dbt
dbt debug
```

3. Build staging models and run tests

```bash
dbt run
dbt test
```

4. Generate and view data lineage

```bash
dbt docs generate
dbt docs serve
```

Opens interactive lineage graph in browser at `http://localhost:8000`

### Stage 3: Build Intermediate Layer

[Planned] Business logic, metric calculations, and failure precursor analysis.

### Stage 4: Build Marts and Power BI Dashboard

[Planned] Analytical tables optimized for BI consumption.

## Development Workflow

```bash
# Activate environment
venv\Scripts\activate
cd dbt

# Build all models
dbt run

# Run data quality tests
dbt test

# Run specific model
dbt run --select stg_ai4i__sensor_readings

# Generate documentation
dbt docs generate
dbt docs serve
```

## Data Methodology

See `data/README.md` for:
- Dataset exploration and structure
- Synthetic data generation approach
- Machine assignment methodology
- Cycle duration assumptions
- Known limitations

## Key Technical Decisions

See `data/README.md` under "Key Technical Decisions" section for:
- Machine assignment strategy (4 independent production cells)
- Cycle duration assumption (1 hour per cycle)
- Reference start date (2022-01-03)
- Machine type categorization (Milling vs Turning)
- Maintenance logic (scheduled vs unscheduled)
- Deterministic data generation with fixed seeds

## Known Limitations

See `data/README.md` under "Known Limitations" section for:
- Source dataset limitations (synthetic, deterministic failure modes)
- Synthetic data generation simplifications
- Analytical limitations (guaranteed signal, not real-world uncertainty)

## Contact & Portfolio

This project demonstrates:
- End-to-end dbt project setup and architecture
- Professional data documentation practices
- Multi-layer analytics engineering workflow
- Data quality testing and validation
- dbt source-to-mart transformation pipeline

For questions or improvements, open an issue or submit a pull request.