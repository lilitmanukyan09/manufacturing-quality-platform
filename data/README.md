# Data Documentation

## Source Dataset
AI4I 2020 Predictive Maintenance Dataset — UCI Machine Learning Repository

### Features
[Paste your completed variable description table here]

### Key observations from exploration
- Source dataset represents a single machine implicitly — no machine ID 
  column present. Machine IDs are assigned programmatically by partitioning 
  the 10,000 cycles into four sequential blocks, with boundaries snapped to 
  the nearest tool wear reset point. See Machine Assignment Methodology 
  section for full details.
- 10,000 sequential cycles with continuous tool wear accumulation
- 119 tool wear reset points identified
- RNF excluded from precursor analysis — no process-parameter cause
- Derived metrics required: temperature differential, operating power,
  wear-torque product

## Synthetic Companion Tables
[To be completed in Phase 0]

## Machine Assignment Methodology
[To be completed in Phase 0]

## Cycle Duration Assumption
[To be decided and documented in Phase 0]

## Known Limitations
[To be completed]