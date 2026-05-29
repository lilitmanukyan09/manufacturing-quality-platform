"""
generate_operator_assignments.py

Purpose:
    Assigns an operator to each UDI based on machine group,
    shift coverage, hire date eligibility, and weekly rotation.
    Produces a lightweight assignment table joining UDIs to operators.

Inputs:
    data/raw/machine_assignments.csv
    data/synthetic/machines.csv
    data/synthetic/operators.csv

Outputs:
    data/raw/operator_assignments.csv
    scripts/generation_log.txt (appended)

Dependencies:
    generate_machine_assignments.py must be run first.
    generate_machines.py must be run first.
    generate_operators.py must be run first.

Assumptions:
    - One cycle = one hour of operating time
    - Operators are divided into fixed groups of 5 per machine
    - Assignment respects primary shift preference and hire date
    - Weekly rotation using week_number % eligible operator count
    - If no shift-matching operator is eligible, falls back to
      any eligible operator in the group
"""


import pandas as pd
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────
ASSIGNMENTS_PATH = "data/raw/machine_assignments.csv"
MACHINES_PATH    = "data/synthetic/machines.csv"
OPERATORS_PATH   = "data/synthetic/operators.csv"
OUTPUT_PATH      = "data/raw/operator_assignments.csv"
LOG_PATH         = "scripts/generation_log.txt"

CYCLE_DURATION_HOURS = 1

MACHINE_OPERATOR_GROUPS = {
    "M001": ["OPR-001", "OPR-002", "OPR-003", "OPR-004", "OPR-005"],
    "M002": ["OPR-006", "OPR-007", "OPR-008", "OPR-009", "OPR-010"],
    "M003": ["OPR-011", "OPR-012", "OPR-013", "OPR-014", "OPR-015"],
    "M004": ["OPR-016", "OPR-017", "OPR-018", "OPR-019", "OPR-020"],
}

SHIFT_HOURS = {
    "Morning":   (6, 14),
    "Afternoon": (14, 22),
    "Night":     (22, 6),
}


def load_inputs(assignments_path, machines_path, operators_path):
    df_assignments = pd.read_csv(assignments_path)
    df_machines    = pd.read_csv(machines_path)
    df_operators   = pd.read_csv(operators_path)

    assert len(df_assignments) == 10000, f"Expected 10000 rows, got {len(df_assignments)}"
    assert len(df_machines)    == 4,     f"Expected 4 machines, got {len(df_machines)}"
    assert len(df_operators)   == 20,    f"Expected 20 operators, got {len(df_operators)}"

    print(f"Loaded assignments: {len(df_assignments)} rows")
    print(f"Loaded machines:    {len(df_machines)} rows")
    print(f"Loaded operators:   {len(df_operators)} rows")

    return df_assignments, df_machines, df_operators


def build_lookups(df_machines, df_operators):
    """
    Builds two lookups:
    - installation_lookup: machine_id → installation datetime
    - operator_lookup: operator_id → {hire_date, primary_shift}
    """
    installation_lookup = {}
    for _, row in df_machines.iterrows():
        installation_lookup[row['machine_id']] = datetime.strptime(
            row['installation_date'], '%Y-%m-%d %H:%M:%S'
        )

    operator_lookup = {}
    for _, row in df_operators.iterrows():
        operator_lookup[row['operator_id']] = {
            'hire_date':    datetime.strptime(row['hire_date'], '%Y-%m-%d'),
            'primary_shift': row['primary_shift']
        }

    print(f"Built installation lookup for {len(installation_lookup)} machines")
    print(f"Built operator lookup for {len(operator_lookup)} operators")

    return installation_lookup, operator_lookup


def get_shift_for_hour(hour):
    """
    Returns shift name based on the hour of the cycle datetime.
    Night shift crosses midnight — hour 22 or later, or before 6.
    """
    if 6 <= hour < 14:
        return "Morning"
    elif 14 <= hour < 22:
        return "Afternoon"
    else:
        return "Night"
    

def assign_operators(df_assignments, installation_lookup, operator_lookup):
    """
    For each UDI:
    1. Derives cycle datetime from machine installation date and UDI offset
    2. Determines shift from cycle datetime hour
    3. Filters machine operator group by shift preference and hire date
    4. Assigns operator using week_number % eligible count
    5. Falls back to any eligible operator if no shift match found
    """
    operator_ids = []
    fallback_count = 0

    for _, row in df_assignments.iterrows():
        machine_id = row['machine_id']
        udi        = int(row['UDI'])

        # Derive cycle datetime
        first_udi = int(df_assignments[
            df_assignments['machine_id'] == machine_id
        ]['UDI'].min())

        hours_offset  = (udi - first_udi) * CYCLE_DURATION_HOURS
        install_date  = installation_lookup[machine_id]
        cycle_datetime = install_date + timedelta(hours=int(hours_offset))

        # Derive shift and week number
        shift       = get_shift_for_hour(cycle_datetime.hour)
        week_number = (cycle_datetime - install_date).days // 7

        # Get operator group for this machine
        group = MACHINE_OPERATOR_GROUPS[machine_id]

        # Filter by shift preference and hire date eligibility
        eligible = [
            op_id for op_id in group
            if operator_lookup[op_id]['primary_shift'] == shift
            and operator_lookup[op_id]['hire_date'] <= cycle_datetime
        ]

        # Fallback — any eligible operator regardless of shift preference
        if not eligible:
            eligible = [
                op_id for op_id in group
                if operator_lookup[op_id]['hire_date'] <= cycle_datetime
            ]
            fallback_count += 1

        # Assign using weekly rotation
        assigned = eligible[week_number % len(eligible)]
        operator_ids.append(assigned)

    print(f"Operator assignment complete")
    print(f"Fallback assignments used: {fallback_count}")

    df_assignments = df_assignments.copy()
    df_assignments['operator_id'] = operator_ids
    return df_assignments


def assemble_output(df):
    output_cols = [
        'UDI',
        'machine_id',
        'operator_id'
    ]
    df_output = df[output_cols].copy()
    df_output = df_output.sort_values('UDI').reset_index(drop=True)

    assert len(df_output) == 10000, f"Expected 10000 rows, got {len(df_output)}"
    print(f"Assembled output: {len(df_output)} rows")
    return df_output


def write_output(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")


def write_log(df, fallback_count):
    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_operator_assignments.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total assignments: {len(df)}\n")
        f.write(f"Fallback assignments: {fallback_count}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting operator assignment generation...")

    df_assignments, df_machines, df_operators = load_inputs(
        ASSIGNMENTS_PATH, MACHINES_PATH, OPERATORS_PATH
    )

    installation_lookup, operator_lookup = build_lookups(
        df_machines, df_operators
    )

    df_assigned = assign_operators(
        df_assignments, installation_lookup, operator_lookup
    )

    df_output = assemble_output(df_assigned)

    write_output(df_output, OUTPUT_PATH)
    write_log(df_output, 0)

    print("\nOperator distribution per machine:")
    print(df_assigned.groupby(['machine_id', 'operator_id']).size().to_string())
    print("\nOperator assignment complete.")


if __name__ == "__main__":
    main()