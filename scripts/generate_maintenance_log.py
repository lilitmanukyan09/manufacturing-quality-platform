"""
generate_maintenance_log.py

Purpose:
    Generates the maintenance log table with one row per tool wear
    reset point. Maintenance type is determined by whether a failure
    preceded the reset. Dates are derived from machine installation
    dates and cycle duration assumption.

Inputs:
    data/raw/ai4i2020.csv
    data/raw/machine_assignments.csv
    data/synthetic/machines.csv

Outputs:
    data/synthetic/maintenance_log.csv
    scripts/generation_log.txt (appended)

Dependencies:
    generate_machine_assignments.py must be run first.
    generate_machines.py must be run first.

Assumptions:
    - One cycle = one hour of operating time
    - Unscheduled maintenance follows any failure event
    - Scheduled resets are split 60% Tool Replacement,
      40% Preventive Maintenance (fixed seed)
    - All resets result in tool replacement (tool_replaced_flag = True)
"""


import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────
AI4I_PATH = "data/raw/ai4i2020.csv"
ASSIGNMENTS_PATH = "data/raw/machine_assignments.csv"
MACHINES_PATH = "data/synthetic/machines.csv"
OUTPUT_PATH = "data/synthetic/maintenance_log.csv"
LOG_PATH = "scripts/generation_log.txt"

CYCLE_DURATION_HOURS = 1
RANDOM_SEED = 42

DURATION_RANGES = {
    "Tool Replacement":       (15, 30),
    "Preventive Maintenance": (45, 90),
    "Unscheduled Maintenance":(60, 120)
}

SCHEDULED_TYPE_WEIGHTS = {
    "Tool Replacement":       0.60,
    "Preventive Maintenance": 0.40
}


def load_inputs(ai4i_path, assignments_path, machines_path):
    df_ai4i = pd.read_csv(ai4i_path)
    df_assignments = pd.read_csv(assignments_path)
    df_machines = pd.read_csv(machines_path)

    assert len(df_ai4i) == 10000, f"Expected 10000 rows in ai4i, got {len(df_ai4i)}"
    assert len(df_assignments) == 10000, f"Expected 10000 rows in assignments, got {len(df_assignments)}"
    assert len(df_machines) == 4, f"Expected 4 machines, got {len(df_machines)}"

    print(f"Loaded ai4i: {len(df_ai4i)} rows")
    print(f"Loaded assignments: {len(df_assignments)} rows")
    print(f"Loaded machines: {len(df_machines)} rows")

    return df_ai4i, df_assignments, df_machines


def build_reset_spine(df_ai4i, df_assignments):
    """
    Joins ai4i source data to machine assignments on UDI.
    Filters to reset points only.
    Carries forward the machine_failure flag from the preceding row
    to determine scheduled vs unscheduled maintenance.
    """
    df_joined = df_assignments.merge(
        df_ai4i[['UDI', 'Machine failure']],
        on='UDI',
        how='left'
    )

    df_joined = df_joined.sort_values('UDI').reset_index(drop=True)
    df_joined['prev_machine_failure'] = df_joined['Machine failure'].shift(1)
    df_resets = df_joined[df_joined['is_reset_point'] == True].copy()

    assert len(df_resets) == 119, f"Expected 119 reset points, got {len(df_resets)}"
    print(f"Reset spine built: {len(df_resets)} reset points")

    return df_resets


def build_installation_lookup(df_machines):
    """
    Creates a dictionary mapping machine_id to installation_date datetime.
    """
    lookup = {}
    for _, row in df_machines.iterrows():
        lookup[row['machine_id']] = datetime.strptime(
            row['installation_date'],
            '%Y-%m-%d %H:%M:%S'
        )
    print(f"Installation date lookup built for {len(lookup)} machines")
    return lookup


def assign_maintenance_attributes(df_resets):
    """
    Assigns maintenance type based on whether a failure preceded the reset.
    Assigns duration randomly within type-specific ranges.
    All assignments use a fixed seed for reproducibility.
    """
    np.random.seed(RANDOM_SEED)

    maintenance_types = []
    durations = []

    scheduled_types = list(SCHEDULED_TYPE_WEIGHTS.keys())
    scheduled_weights = list(SCHEDULED_TYPE_WEIGHTS.values())

    for _, row in df_resets.iterrows():
        if row['prev_machine_failure'] == 1:
            mtype = "Unscheduled Maintenance"
        else:
            mtype = np.random.choice(scheduled_types, p=scheduled_weights)

        min_dur, max_dur = DURATION_RANGES[mtype]
        duration = np.random.randint(min_dur, max_dur + 1)

        maintenance_types.append(mtype)
        durations.append(int(duration))

    df_resets = df_resets.copy()
    df_resets['maintenance_type'] = maintenance_types
    df_resets['duration_min'] = durations

    return df_resets


def calculate_maintenance_dates(df_resets, installation_lookup):
    """
    Derives maintenance datetime from machine installation date
    and UDI position within the machine's block.
    """
    maintenance_dates = []

    for _, row in df_resets.iterrows():
        machine_id = row['machine_id']
        udi = int(row['UDI'])

        installation_date = installation_lookup[machine_id]
        first_udi = int(
            df_resets[df_resets['machine_id'] == machine_id]['UDI'].min()
        )

        hours_since_install = (udi - first_udi) * CYCLE_DURATION_HOURS
        maintenance_date = installation_date + timedelta(hours=int(hours_since_install))
        maintenance_dates.append(maintenance_date.strftime('%Y-%m-%d %H:%M:%S'))

    df_resets = df_resets.copy()
    df_resets['maintenance_date'] = maintenance_dates
    return df_resets


def assemble_output(df_resets):
    df_resets = df_resets.copy()
    df_resets['maintenance_id'] = [
        f"MNT-{str(i+1).zfill(4)}" for i in range(len(df_resets))
    ]
    df_resets['tool_replaced_flag'] = True

    output_cols = [
        'maintenance_id',
        'machine_id',
        'UDI',
        'maintenance_date',
        'maintenance_type',
        'tool_replaced_flag',
        'duration_min'
    ]

    df_output = df_resets[output_cols].copy()
    df_output = df_output.sort_values('UDI').reset_index(drop=True)

    assert len(df_output) == 119, f"Expected 119 rows, got {len(df_output)}"
    print(f"Assembled output: {len(df_output)} maintenance records")
    return df_output


def write_output(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")
    assert len(df) == 119, f"Output row count mismatch: {len(df)}"


def write_log(df_output):
    scheduled = len(df_output[df_output['maintenance_type'] != 'Unscheduled Maintenance'])
    unscheduled = len(df_output[df_output['maintenance_type'] == 'Unscheduled Maintenance'])

    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_maintenance_log.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total maintenance events: {len(df_output)}\n")
        f.write(f"Scheduled: {scheduled}\n")
        f.write(f"Unscheduled: {unscheduled}\n")
        f.write(f"Random seed: {RANDOM_SEED}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting maintenance log generation...")

    df_ai4i, df_assignments, df_machines = load_inputs(
        AI4I_PATH, ASSIGNMENTS_PATH, MACHINES_PATH
    )

    df_resets = build_reset_spine(df_ai4i, df_assignments)
    installation_lookup = build_installation_lookup(df_machines)
    df_resets = assign_maintenance_attributes(df_resets)
    df_resets = calculate_maintenance_dates(df_resets, installation_lookup)
    df_output = assemble_output(df_resets)

    write_output(df_output, OUTPUT_PATH)
    write_log(df_output)

    print("\nMaintenance type distribution:")
    print(df_output['maintenance_type'].value_counts().to_string())
    print("\nMaintenance log generation complete.")


if __name__ == "__main__":
    main()