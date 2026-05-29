# Data Documentation

## Source Dataset
AI4I 2020 Predictive Maintenance Dataset — UCI Machine Learning Repository  
URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

A synthetic dataset of 10,000 CNC machining process cycles containing 
sensor readings, product variant information, and five labeled failure 
modes. Generated to simulate predictive maintenance scenarios in a 
manufacturing environment.

### Features
[Paste your completed variable description table here]

### Key Observations from Exploration
- No machine ID column present — dataset implicitly represents a single 
  continuous process
- 10,000 sequential cycles with continuous tool wear accumulation 
  across mixed product types
- 119 tool wear reset points identified — each represents a tool replacement
- RNF failure type has only 5 occurrences and no process-parameter cause
- Three failure modes depend on derived metrics not present in the 
  raw data: temperature differential (HDF), operating power (PWF), 
  and wear-torque product (OSF)


## Machine Assignment Methodology
The dataset is partitioned into four sequential blocks, each representing 
one machine's operational history. Block boundaries are snapped to the 
nearest tool wear reset point rather than arbitrary row numbers — ensuring 
each machine starts with a complete tool life with no inherited tool wear 
from a previous block.

Approximate boundary targets of UDI 2500, 5000, and 7500 are scanned 
forward to the nearest reset point at or after each target, producing 
the actual boundaries used for assignment.

Variant-based assignment — grouping all L cycles to one machine, M to 
another, H to a third — was considered and rejected. Tool wear accumulates 
continuously across product types in sequential UDI order, making 
variant-based splits analytically inconsistent with the source data structure.

The assignment is fully deterministic — no randomness is involved and 
running the script twice produces identical output. All timestamps across 
synthetic tables derive from a single cycle duration assumption of one 
hour per cycle, anchored to a reference start date of 2022-01-03 for UDI 1.

## Synthetic Companion Tables
Four synthetic tables were generated to introduce the operational context 
absent from the source dataset, enabling dimensional analysis across 
machines, maintenance history, shift patterns, and operator experience. 
All tables except operators derive directly or indirectly from the source 
dataset. Timestamps in all tables are derived from machine block start UDIs 
and the cycle duration assumption documented in the Machine Assignment 
Methodology section.

- **Machines** — four machines across two types: Milling (M001, M002) and 
  Turning (M003, M004), each operating as an independent production cell. 
  Installation dates are derived programmatically from block start UDIs.
- **Maintenance Log** — 119 records derived from tool wear reset points. 
  Resets preceded by a failure event are logged as Unscheduled Maintenance. 
  Scheduled resets are split into Tool Replacement (60%) and Preventive 
  Maintenance (40%).
- **Shifts** — facility-level schedule of three shifts per day, 7 days per 
  week, covering the full operating period. Six supervisors rotate weekly 
  within each shift type.
- **Operators** — 20 operators with deterministic distribution across 
  experience tiers (Junior 40%, Mid 40%, Senior 20%), certification types, 
  and primary shift assignments. Fully self-generated — no dependency on 
  source data.

## Known Limitations

### Source Dataset
The AI4I 2020 dataset is synthetically generated and was not collected 
from a real manufacturing facility. Failure modes are deterministic by 
construction — failure precursors are guaranteed to exist rather than 
being statistically discovered. This is the most significant limitation 
of the project.
- RNF failure type is excluded from precursor analysis — with no 
  process-parameter cause, including it would contaminate deviation 
  scoring without adding analytical value

### Synthetic Data Generation
Several simplifications were made to limit complexity:

- Operators are assigned a primary shift column rather than linked 
  through a junction table
- Maintenance durations are randomly generated within realistic ranges 
  rather than derived from actual repair data
- Shift supervisor rotation follows a simple weekly pattern rather than 
  reflecting real scheduling complexity

### Analytical Limitations
The business question is answered on a dataset with guaranteed signal 
by construction. In real manufacturing data, failure precursors may be 
weaker, noisier, or absent for certain failure modes. The transformation 
architecture demonstrated here is designed to surface signal where it 
exists — its effectiveness on genuinely uncertain real-world data would 
require separate validation.