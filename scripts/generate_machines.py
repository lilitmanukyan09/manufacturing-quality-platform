"""
generate_machines.py

Purpose:
    Generates the machines dimension table with one row per machine.
    Installation dates are derived programmatically from block start
    UDIs in machine_assignments.csv and the cycle duration assumption.

Inputs:
    data/raw/machine_assignments.csv

Outputs:
    data/synthetic/machines.csv
    scripts/generation_log.txt (appended)

Dependencies:
    generate_machine_assignments.py must be run first.

Assumptions:
    - One cycle = one hour of operating time
    - UDI 1 starts on 2022-01-03 00:00:00
    - M001, M002 are Milling machines
    - M003, M004 are Turning machines
    - Each machine operates as an independent production cell
"""


import pandas as pd
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────
INPUT_PATH = "data/raw/machine_assignments.csv"
OUTPUT_PATH = "data/synthetic/machines.csv"
LOG_PATH = "scripts/generation_log.txt"

CYCLE_DURATION_HOURS = 1
REFERENCE_DATE = datetime(2022, 1, 3, 0, 0, 0)

MACHINE_TYPES = {
    "M001": "Milling",
    "M002": "Milling",
    "M003": "Turning",
    "M004": "Turning"
}

MANUFACTURERS = {
    "Milling": "Mazak",
    "Turning": "DMG Mori"
}

RATED_TOOL_LIFE_MIN = 220


def load_machine_assignments(path):
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    assert len(df) == 10000, f"Expected 10000 rows, got {len(df)}"
    return df


def derive_installation_dates(df):
    """
    For each machine, finds the first UDI in its block.
    Converts that UDI to a datetime by offsetting from the reference date.
    Returns a dictionary mapping machine_id to installation_datetime.
    """
    installation_dates = {}

    for machine_id in ["M001", "M002", "M003", "M004"]:
        first_udi = df[df['machine_id'] == machine_id]['UDI'].min()
        hours_offset = int((first_udi - 1) * CYCLE_DURATION_HOURS)
        installation_date = REFERENCE_DATE + timedelta(hours=hours_offset)
        installation_dates[machine_id] = installation_date
        print(f"{machine_id}: first UDI {first_udi} → installation date {installation_date.date()}")

    return installation_dates


def build_machines_table(installation_dates):
    rows = []

    for machine_id in ["M001", "M002", "M003", "M004"]:
        machine_type = MACHINE_TYPES[machine_id]
        manufacturer = MANUFACTURERS[machine_type]
        installation_date = installation_dates[machine_id]

        rows.append({
            'machine_id': machine_id,
            'machine_type': machine_type,
            'manufacturer': manufacturer,
            'installation_date': installation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'rated_tool_life_min': RATED_TOOL_LIFE_MIN,
            'location_in_plant': f"Cell_{machine_id[-1]}",
            'is_active': True
        })

    df = pd.DataFrame(rows)
    print(f"Built machines table with {len(df)} rows")
    assert len(df) == 4, f"Expected 4 machines, got {len(df)}"
    return df


def write_output(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")
    assert len(df) == 4, f"Output row count mismatch: {len(df)}"


def write_log(installation_dates):
    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_machines.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Cycle duration assumption: {CYCLE_DURATION_HOURS} hour(s)\n")
        f.write(f"Reference date: {REFERENCE_DATE.date()}\n")
        f.write(f"Rated tool life: {RATED_TOOL_LIFE_MIN} min\n")
        f.write(f"Installation dates derived:\n")
        for machine_id, date in installation_dates.items():
            f.write(f"  {machine_id}: {date.date()}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting machines table generation...")

    df_assignments = load_machine_assignments(INPUT_PATH)
    installation_dates = derive_installation_dates(df_assignments)
    df_machines = build_machines_table(installation_dates)
    write_output(df_machines, OUTPUT_PATH)
    write_log(installation_dates)

    print("\nMachines table:")
    print(df_machines.to_string(index=False))
    print("\nMachines generation complete.")


if __name__ == "__main__":
    main()