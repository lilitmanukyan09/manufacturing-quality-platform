"""
generate_machine_assignments.py

Purpose:
    Reads ai4i2020.csv and assigns each UDI to one of four machines
    by snapping block boundaries to the nearest tool wear reset point
    at approximately UDI 2500, 5000, and 7500.

Inputs:
    data/raw/ai4i2020.csv

Outputs:
    data/raw/machine_assignments.csv
    scripts/generation_log.txt (appended)

Dependencies:
    None — must be run before any other generation script

Reproducibility:
    Fully deterministic — no randomness. Running twice produces
    identical output.
"""


import pandas as pd
from datetime import datetime
import os

# ── Configuration ─────────────────────────────────────────
INPUT_PATH = "data/raw/ai4i2020.csv"
OUTPUT_PATH = "data/raw/machine_assignments.csv"
LOG_PATH = "scripts/generation_log.txt"

APPROXIMATE_BOUNDARIES = [2500, 5000, 7500]
MACHINE_IDS = ["M001", "M002", "M003", "M004"]


def load_data(path):
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    assert len(df) == 10000, f"Expected 10000 rows, got {len(df)}"
    return df


def detect_resets(df):
    reset_udis = []
    for i in range(1, len(df)):
        prev_wear = df.loc[i-1, 'Tool wear [min]']
        curr_wear = df.loc[i, 'Tool wear [min]']
        if curr_wear < prev_wear:
            reset_udis.append(int(df.loc[i, 'UDI']))
    
    print(f"Detected {len(reset_udis)} reset points")
    assert len(reset_udis) == 119, f"Expected 119 resets, got {len(reset_udis)}"
    return reset_udis


def snap_boundaries(approximate_boundaries, reset_udis):
    actual_boundaries = []
    for target in approximate_boundaries:
        snapped = next(
            (udi for udi in reset_udis if udi >= target),
            None
        )
        if snapped is None:
            raise ValueError(f"No reset point found at or after UDI {target}")
        actual_boundaries.append(snapped)
        print(f"Boundary target UDI {target} → snapped to reset at UDI {snapped}")
    
    return actual_boundaries


def assign_machines(df, actual_boundaries, machine_ids):
    def get_machine_id(udi):
        if udi < actual_boundaries[0]:
            return machine_ids[0]
        elif udi < actual_boundaries[1]:
            return machine_ids[1]
        elif udi < actual_boundaries[2]:
            return machine_ids[2]
        else:
            return machine_ids[3]
    
    df['machine_id'] = df['UDI'].apply(get_machine_id)
    return df


def assign_tool_life_numbers(df):
    df = df.copy()
    df['tool_life_number'] = 0
    
    for machine_id in df['machine_id'].unique():
        mask = df['machine_id'] == machine_id
        machine_df = df[mask].copy()
        
        tool_life = 1
        tool_life_numbers = []
        
        for i in range(len(machine_df)):
            tool_life_numbers.append(tool_life)
            if i < len(machine_df) - 1:
                curr_wear = machine_df.iloc[i]['Tool wear [min]']
                next_wear = machine_df.iloc[i+1]['Tool wear [min]']
                if next_wear < curr_wear:
                    tool_life += 1
        
        df.loc[mask, 'tool_life_number'] = tool_life_numbers
    
    return df


def flag_resets(df, reset_udis):
    df['is_reset_point'] = df['UDI'].isin(reset_udis)
    return df


def write_output(df, output_path):
    output_cols = [
        'UDI',
        'machine_id',
        'Tool wear [min]',
        'is_reset_point',
        'tool_life_number'
    ]
    df[output_cols].to_csv(output_path, index=False)
    print(f"Written {len(df)} rows to {output_path}")
    assert len(df) == 10000, f"Output row count mismatch: {len(df)}"


def write_log(actual_boundaries, machine_ids, reset_count):
    with open(LOG_PATH, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"generate_machine_assignments.py\n")
        f.write(f"Run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Reset points detected: {reset_count}\n")
        f.write(f"Actual block boundaries chosen:\n")
        for i, (boundary, machine) in enumerate(
            zip([1] + actual_boundaries, machine_ids)
        ):
            f.write(f"  {machine}: starts at UDI {boundary}\n")
        f.write(f"Output: {OUTPUT_PATH}\n")


def main():
    print("Starting machine assignment generation...")
    
    df = load_data(INPUT_PATH)
    reset_udis = detect_resets(df)
    actual_boundaries = snap_boundaries(APPROXIMATE_BOUNDARIES, reset_udis)
    df = assign_machines(df, actual_boundaries, MACHINE_IDS)
    df = assign_tool_life_numbers(df)
    df = flag_resets(df, reset_udis)
    write_output(df, OUTPUT_PATH)
    write_log(actual_boundaries, MACHINE_IDS, len(reset_udis))
    
    print("Machine assignment complete.")
    print(f"Log written to {LOG_PATH}")
    
    print("\nMachine distribution:")
    print(df.groupby('machine_id')['UDI'].count().to_string())
    print("\nTool life counts per machine:")
    print(df.groupby('machine_id')['tool_life_number'].max().to_string())

if __name__ == "__main__":
    main()