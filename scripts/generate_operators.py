"""
generate_operators.py

Purpose:
    Generates the operators dimension table with 20 operators.
    Experience levels, hire dates, certifications, and shift
    assignments are generated probabilistically with a fixed seed
    for reproducibility.

Inputs:
    None — fully self-contained generation

Outputs:
    data/synthetic/operators.csv
    scripts/generation_log.txt (appended)

Dependencies:
    None — can be run independently of other scripts

Assumptions:
    - 20 operators total
    - Experience tiers: Junior (40%), Mid (40%), Senior (20%)
    - Certification skews toward CNC_Programming for Senior operators
    - Reference date: 2022-01-03
    - Hire dates derived from experience level ranges
    - Primary shift assigned per operator
"""


import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────
OUTPUT_PATH = "data/synthetic/operators.csv"
LOG_PATH    = "scripts/generation_log.txt"

RANDOM_SEED    = 42
OPERATOR_COUNT = 20
REFERENCE_DATE = datetime(2022, 1, 3)

EXPERIENCE_LEVELS = ["Junior", "Mid", "Senior"]
EXPERIENCE_WEIGHTS = [0.40, 0.40, 0.20]

HIRE_YEAR_RANGES = {
    "Junior": (2020, 2022),
    "Mid":    (2015, 2019),
    "Senior": (2010, 2014),
}

CERTIFICATION_WEIGHTS = {
    "Junior": {"CNC_Operation": 0.90, "CNC_Programming": 0.10},
    "Mid":    {"CNC_Operation": 0.70, "CNC_Programming": 0.30},
    "Senior": {"CNC_Operation": 0.40, "CNC_Programming": 0.60},
}

SHIFT_NAMES = ["Morning", "Afternoon", "Night"]
SHIFT_WEIGHTS = [0.40, 0.35, 0.25]


def generate_operators():
    np.random.seed(RANDOM_SEED)

    rows = []

    for i in range(OPERATOR_COUNT):
        operator_id = f"OPR-{str(i+1).zfill(3)}"

        experience_level = np.random.choice(
            EXPERIENCE_LEVELS,
            p=EXPERIENCE_WEIGHTS
        )

        min_year, max_year = HIRE_YEAR_RANGES[experience_level]
        hire_year  = np.random.randint(min_year, max_year + 1)
        hire_month = np.random.randint(1, 13)
        hire_day   = np.random.randint(1, 29)
        hire_date  = datetime(int(hire_year), int(hire_month), int(hire_day))

        cert_options = list(CERTIFICATION_WEIGHTS[experience_level].keys())
        cert_weights = list(CERTIFICATION_WEIGHTS[experience_level].values())
        certification = np.random.choice(cert_options, p=cert_weights)

        primary_shift = np.random.choice(SHIFT_NAMES, p=SHIFT_WEIGHTS)

        rows.append({
            'operator_id':       operator_id,
            'experience_level':  experience_level,
            'hire_date':         hire_date.strftime('%Y-%m-%d'),
            'certification_type': certification,
            'primary_shift':     primary_shift
        })

    df = pd.DataFrame(rows)
    print(f"Generated {len(df)} operators")
    assert len(df) == OPERATOR_COUNT, f"Expected {OPERATOR_COUNT} operators, got {len(df)}"
    return df


def validate_operators(df):
    """
    Checks that hire dates are consistent with experience levels.
    A Senior operator hired after 2015 would be internally inconsistent.
    """
    df['hire_year'] = pd.to_datetime(df['hire_date']).dt.year

    for _, row in df.iterrows():
        level = row['experience_level']
        year  = row['hire_year']
        min_year, max_year = HIRE_YEAR_RANGES[level]
        assert min_year <= year <= max_year, (
            f"Operator {row['operator_id']}: hire year {year} "
            f"outside expected range {min_year}-{max_year} "
            f"for {level} level"
        )

    df = df.drop(columns=['hire_year'])
    print("Internal consistency validation passed")
    return df


def write_output(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")
    assert len(df) == OPERATOR_COUNT, f"Output row count mismatch: {len(df)}"


def write_log(df):
    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_operators.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total operators: {len(df)}\n")
        f.write(f"Random seed: {RANDOM_SEED}\n")
        f.write(f"Experience distribution:\n")
        for level, count in df['experience_level'].value_counts().items():
            f.write(f"  {level}: {count}\n")
        f.write(f"Certification distribution:\n")
        for cert, count in df['certification_type'].value_counts().items():
            f.write(f"  {cert}: {count}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting operators table generation...")

    df_operators = generate_operators()
    df_operators = validate_operators(df_operators)

    write_output(df_operators, OUTPUT_PATH)
    write_log(df_operators)

    print("\nExperience level distribution:")
    print(df_operators['experience_level'].value_counts().to_string())
    print("\nCertification distribution:")
    print(df_operators['certification_type'].value_counts().to_string())
    print("\nPrimary shift distribution:")
    print(df_operators['primary_shift'].value_counts().to_string())
    print("\nOperators generation complete.")


if __name__ == "__main__":
    main()