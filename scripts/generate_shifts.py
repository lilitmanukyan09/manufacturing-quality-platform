"""
generate_shifts.py

Purpose:
    Generates the shifts dimension table covering the full operating
    period from M001 installation date to the last cycle of M004.
    Three shifts per day, 7 days a week, facility-level schedule.

Inputs:
    data/raw/machine_assignments.csv
    data/synthetic/machines.csv

Outputs:
    data/synthetic/shifts.csv
    scripts/generation_log.txt (appended)

Dependencies:
    generate_machine_assignments.py must be run first.
    generate_machines.py must be run first.

Assumptions:
    - Morning shift:   06:00 - 14:00
    - Afternoon shift: 14:00 - 22:00
    - Night shift:     22:00 - 06:00 (next day)
    - 7 days per week operation
    - 6 supervisors rotating weekly within shift type
    - One cycle = one hour
"""


import pandas as pd
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────
ASSIGNMENTS_PATH = "data/raw/machine_assignments.csv"
MACHINES_PATH    = "data/synthetic/machines.csv"
OUTPUT_PATH      = "data/synthetic/shifts.csv"
LOG_PATH         = "scripts/generation_log.txt"

CYCLE_DURATION_HOURS = 1

SHIFT_DEFINITIONS = [
    {"shift_name": "Morning",   "start_hour": 6,  "end_hour": 14},
    {"shift_name": "Afternoon", "start_hour": 14, "end_hour": 22},
    {"shift_name": "Night",     "start_hour": 22, "end_hour": 6},
]

SUPERVISORS = {
    "Morning":   ["SUP-001", "SUP-002"],
    "Afternoon": ["SUP-003", "SUP-004"],
    "Night":     ["SUP-005", "SUP-006"],
}


def load_inputs(assignments_path, machines_path):
    df_assignments = pd.read_csv(assignments_path)
    df_machines = pd.read_csv(machines_path)

    assert len(df_assignments) == 10000, f"Expected 10000 rows, got {len(df_assignments)}"
    assert len(df_machines) == 4, f"Expected 4 machines, got {len(df_machines)}"

    print(f"Loaded assignments: {len(df_assignments)} rows")
    print(f"Loaded machines: {len(df_machines)} rows")

    return df_assignments, df_machines


def get_operating_period(df_assignments, df_machines):
    """
    Start: M001 installation date (earliest installation)
    End:   derived from last UDI and its machine's installation date
    """
    installation_lookup = {}
    for _, row in df_machines.iterrows():
        installation_lookup[row['machine_id']] = datetime.strptime(
            row['installation_date'], '%Y-%m-%d %H:%M:%S'
        )

    last_row = df_assignments.sort_values('UDI').iloc[-1]
    last_machine = last_row['machine_id']
    last_udi = int(last_row['UDI'])

    first_udi_for_last_machine = int(
        df_assignments[df_assignments['machine_id'] == last_machine]['UDI'].min()
    )

    hours_to_last = (last_udi - first_udi_for_last_machine) * CYCLE_DURATION_HOURS
    end_datetime = installation_lookup[last_machine] + timedelta(hours=int(hours_to_last))

    start_datetime = min(installation_lookup.values())

    print(f"Operating period: {start_datetime.date()} to {end_datetime.date()}")
    return start_datetime, end_datetime


def generate_shifts(start_datetime, end_datetime):
    """
    Iterates day by day across the operating period.
    For each day generates three shift slots.
    Assigns supervisors by weekly rotation within shift type.
    """
    rows = []
    shift_counter = 1

    current_date = start_datetime.date()
    end_date = end_datetime.date()

    while current_date <= end_date:
        week_number = (current_date - start_datetime.date()).days // 7

        for shift_def in SHIFT_DEFINITIONS:
            shift_name = shift_def['shift_name']
            start_hour = shift_def['start_hour']
            end_hour   = shift_def['end_hour']

            shift_start = datetime.combine(current_date, 
                         datetime.min.time().replace(hour=start_hour))

            if shift_name == "Night":
                shift_end = datetime.combine(current_date + timedelta(days=1),
                           datetime.min.time().replace(hour=end_hour))
            else:
                shift_end = datetime.combine(current_date,
                           datetime.min.time().replace(hour=end_hour))

            supervisors = SUPERVISORS[shift_name]
            supervisor  = supervisors[week_number % len(supervisors)]

            rows.append({
                'shift_id':         f"SHF-{str(shift_counter).zfill(5)}",
                'shift_name':       shift_name,
                'shift_date':       current_date.strftime('%Y-%m-%d'),
                'shift_start':      shift_start.strftime('%Y-%m-%d %H:%M:%S'),
                'shift_end':        shift_end.strftime('%Y-%m-%d %H:%M:%S'),
                'supervisor_id':    supervisor
            })

            shift_counter += 1

        current_date += timedelta(days=1)

    df = pd.DataFrame(rows)
    print(f"Generated {len(df)} shift slots")
    return df


def write_output(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")


def write_log(df):
    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_shifts.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total shift slots generated: {len(df)}\n")
        f.write(f"Shift distribution:\n")
        for shift_name, count in df['shift_name'].value_counts().items():
            f.write(f"  {shift_name}: {count}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting shifts table generation...")

    df_assignments, df_machines = load_inputs(
        ASSIGNMENTS_PATH, MACHINES_PATH
    )

    start_datetime, end_datetime = get_operating_period(
        df_assignments, df_machines
    )

    df_shifts = generate_shifts(start_datetime, end_datetime)

    write_output(df_shifts, OUTPUT_PATH)
    write_log(df_shifts)

    print("\nShift distribution:")
    print(df_shifts['shift_name'].value_counts().to_string())
    print(f"\nDate range: {df_shifts['shift_date'].min()} "
          f"to {df_shifts['shift_date'].max()}")
    print("\nShifts generation complete.")


if __name__ == "__main__":
    main()