# Manufacturing Process Quality Intelligence Platform

## Overview
A dbt-based analytics engineering portfolio project modeling 
predictive maintenance data to identify process parameter patterns 
that precede quality failure events.

**Business Question:** For each recorded failure, what was the state 
of every process parameter in the 5, 10, and 20 operating cycles 
preceding it — and which parameters show the most consistent 
deviation from their product-variant baseline before failure occurs?

**Stack:** Python · dbt Core · Snowflake · Power BI

## Dataset
AI4I 2020 Predictive Maintenance Dataset  
Source: UCI Machine Learning Repository  
URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset  
Note: Synthetic dataset. Companion dimension tables are also 
synthetically generated — see data/README.md for methodology.

## Architecture
[To be completed in Phase 1]

## Project Structure
\`\`\`
manufacturing-quality-platform/
├── data/
│   ├── raw/                  # Source CSVs — not committed to git
│   ├── synthetic/            # Generated dimension tables — not committed to git
│   └── README.md             # Data model decisions and generation methodology
├── scripts/                  # Python generation scripts
├── snowflake/                # COPY INTO SQL scripts for raw layer loading
├── docs/                     # Architecture diagrams and supplementary documentation
├── dbt/                      # dbt project (added Phase 1)
├── .env.example              # Required environment variable names
├── profiles.yml.example      # dbt Snowflake connection template
├── requirements.txt          # Pinned Python dependencies
└── README.md                 # This file
\`\`\`

## Prerequisites
- Python 3.13.11
- git 2.34.1
- pip 26.1.1

## Local Setup

### Steps
1. Clone the repository
\`\`\`bash
git clone https://github.com/lilitmanukyan09/manufacturing-quality-platform.git
cd manufacturing-quality-platform
\`\`\`

2. Create and activate virtual environment
\`\`\`bash
py -m venv venv
venv\Scripts\activate
\`\`\`

3. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configure credentials
\`\`\`bash
copy .env.example .env
\`\`\`
Fill in your Snowflake credentials in `.env`

5. Configure dbt profile  
Copy `profiles.yml.example` to `C:\Users\YOURNAME\.dbt\profiles.yml`  
Replace YOURNAME with your Windows username — run `echo %USERNAME%` 
in your terminal to confirm it.
Fill in your Snowflake credentials

### Running the project
[To be completed as phases are built]

## Data Generation Methodology
See `data/README.md`

## Key Technical Decisions
[To be completed as decisions are made]

## Known Limitations
[To be completed]