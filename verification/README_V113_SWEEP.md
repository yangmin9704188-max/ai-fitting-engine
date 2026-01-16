# Shoulder Width v1.1.3 (Candidate) Parameter Sweep Verification

## Overview

This verification runner evaluates candidate parameter configurations for Shoulder Width v1.1.3 with comprehensive semantic validity gates, wiring proof, and regression analysis.

## Features

### 1. Semantic Validity Gates
- **Upper Arm Leakage Detection**: Checks for landmarks placed too far from shoulder joints
  - `landmark_distance < 0.20m` from shoulder joint (L/R)
  - `ratio = measured_sw / joint_sw <= 1.3`
- **Fallback Detection**: Ensures no fallback to joint-based measurement
- **Exception Handling**: Tracks and reports exceptions

### 2. Wiring Proof
- **Runtime CFG Hash**: Each candidate's runtime configuration is hashed
- **Policy-to-Run Verification**: Proves that runtime cfg matches policy cfg
- **Audit Trail**: All wiring proofs saved to `wiring_proof.json`

### 3. Golden Set Regression Analysis
- **Error Statistics**: Mean, std, min, max, max deviation
- **Ratio Analysis**: Distribution of measured_sw / joint_sw ratios
- **Per-Frame Breakdown**: Detailed results for each frame in golden set

### 4. Failure Analysis
- **Worst-Case Examples**: Saves worst leakage case for each candidate
- **Best Pass Cases**: Saves successful cases for comparison
- **Top Failure Reasons**: Aggregates and ranks failure modes

## Usage

### Basic Usage (Default Parameter Sweep)

```bash
py verification/verify_shoulder_width_v113_sweep.py --npz verification/golden_shoulder_batched.npz
```

This will:
- Load the golden set from NPZ
- Run default parameter sweep (r0_ratio: [0.20, 0.22, 0.24, 0.26], r1_ratio: [0.14, 0.16, 0.18], cap_quantile: [0.92, 0.94, 0.96])
- Save results to `artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/`

### Custom Candidate Configurations

Create a JSON file with candidate configurations:

```json
{
  "description": "Custom candidate configs",
  "candidates": [
    {
      "id": "candidate_strict",
      "config": {
        "r0_ratio": 0.20,
        "r1_ratio": 0.14,
        "cap_quantile": 0.96,
        "distal_w_threshold": 0.55,
        "s_min_ratio": 0.02,
        "s_max_ratio": 0.95,
        "min_cap_points": 60
      }
    },
    {
      "id": "candidate_moderate",
      "config": {
        "r0_ratio": 0.22,
        "r1_ratio": 0.16,
        "cap_quantile": 0.94,
        ...
      }
    }
  ]
}
```

Then run:

```bash
py verification/verify_shoulder_width_v113_sweep.py --npz verification/golden_shoulder_batched.npz --configs verification/example_configs_v113.json
```

### Custom Output Directory

```bash
py verification/verify_shoulder_width_v113_sweep.py --npz verification/golden_shoulder_batched.npz --out_dir artifacts/custom_sweep
```

## Output Structure

```
artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/
├── wiring_proof.json              # Wiring proof for all candidates
├── sweep_results.csv              # Summary table (one row per candidate)
├── sweep_summary.json             # Full summary with rankings
├── candidate_001/
│   ├── per_frame_results.csv      # Detailed per-frame results
│   ├── worst_leakage_case.json    # Worst leakage example
│   └── best_pass_case.json        # Best pass example (if any)
├── candidate_002/
│   └── ...
└── ...
```

## Output Files

### 1. `sweep_results.csv`

Summary table with one row per candidate:
- `candidate_id`: Candidate identifier
- `config.*`: Configuration parameters (r0_ratio, r1_ratio, cap_quantile, etc.)
- `cfg_hash`: SHA-256 hash of configuration (first 16 chars)
- `semantic_valid`: Boolean (PASS/FAIL)
- `validity_reason`: Failure reason if invalid
- `n_total`, `n_valid`, `n_failures`, `n_fallback`, `n_leakage`: Counts
- `regression.*`: Statistics (mean_sw_m, std_sw_m, max_deviation_m, mean_ratio, etc.)
- `leakage_details.*`: Leakage case IDs and top reasons

### 2. `sweep_summary.json`

Complete summary with:
- `timestamp`: Execution timestamp
- `golden_set`: Path to input NPZ
- `n_frames`: Number of frames in golden set
- `n_candidates`: Number of candidates evaluated
- `semantic_validity_thresholds`: Validation thresholds used
- `results`: Full results array (same as CSV but structured)
- `rankings`: Top candidates by different criteria
  - `by_validity`: Sorted by semantic_valid, then by n_leakage
  - `by_stability`: Sorted by std_sw_m (lowest first)
  - `by_max_ratio`: Sorted by max_ratio (lowest first)
- `failure_analysis`: Top failure reasons and counts

### 3. `wiring_proof.json`

Wiring proof documentation:
```json
{
  "timestamp": "2026-01-17T...",
  "wiring_proofs": {
    "candidate_001": {
      "runtime_cfg": { ... },
      "cfg_hash": "a03a67b8455b9b0a"
    },
    ...
  },
  "note": "Each candidate's runtime cfg and hash are recorded for policy-to-run verification"
}
```

### 4. `candidate_*/per_frame_results.csv`

Per-frame detailed results:
- `frame_id`: Frame index (1-based)
- `measured_sw_m`: Measured shoulder width
- `joint_sw_m`: Joint-based shoulder width
- `ratio`: measured_sw / joint_sw
- `landmark_L_dist_m`, `landmark_R_dist_m`: Landmark distances from shoulder joints
- `fallback`: Boolean (was fallback used?)
- `leakage`: Boolean (was leakage detected?)
- `leakage_reason`: Leakage reason if detected
- `exception`: Exception message if any

### 5. `candidate_*/worst_leakage_case.json` / `best_pass_case.json`

Example cases for analysis:
```json
{
  "frame_id": 2,
  "config": {
    "r0_ratio": 0.2,
    "r1_ratio": 0.14,
    "cap_quantile": 0.92
  },
  "measured_sw_m": 1.5829,
  "joint_sw_m": 0.3581,
  "ratio": 4.421,
  "leakage": true,
  "leakage_reason": "L_landmark_dist=0.6355m>=0.2m; R_landmark_dist=0.6752m>=0.2m; ratio=4.421>1.3",
  ...
}
```

## Console Output

The script prints:
1. **Progress**: One line per candidate evaluation
2. **Summary**:
   - Top 5 candidates (by validity + stability)
   - Top 5 failure reasons (with counts)

Example:
```
================================================================================
Console Summary
================================================================================

Top 5 Candidates (by Validity + Stability):
--------------------------------------------------------------------------------
No valid candidates found.

Top 5 Failure Reasons:
--------------------------------------------------------------------------------
1. leakage_cases=10: 36 candidates
================================================================================
```

## Semantic Validity Criteria

A candidate **PASSES** semantic validity gates if:
- ✅ `n_failures == 0` (no exceptions)
- ✅ `n_fallback == 0` (no fallback to joint-based measurement)
- ✅ `n_leakage == 0` (no upper arm leakage detected)

Leakage is detected if **any** of the following are true:
- `landmark_L_dist >= 0.20m` OR `landmark_R_dist >= 0.20m`
- `ratio = measured_sw / joint_sw > 1.3`

## Integration with Policy Report

The output files are designed to be directly included in policy reports:

1. **`sweep_summary.json`**: Can be referenced or embedded in report
2. **`wiring_proof.json`**: Provides audit trail for policy-to-run verification
3. **`sweep_results.csv`**: Can be imported into Excel/Google Sheets for analysis
4. **`candidate_*/worst_leakage_case.json`**: Provides reproducible examples for documentation

## Notes

- **Algorithm Structure**: The measurement algorithm structure is NOT modified. Only parameters are evaluated.
- **Golden Set**: Uses the same golden set format as `verify_shoulder_width_v112.py`
- **Reproducibility**: All results include timestamps and configuration hashes for reproducibility
- **Performance**: For large parameter sweeps, consider using smaller golden sets or filtering candidates

## Example: Quick Start

```bash
# 1. Generate golden set (if not already done)
py verification/export_golden_shoulder_npz.py --n_cases 10 --format batched

# 2. Run sweep
py verification/verify_shoulder_width_v113_sweep.py --npz verification/golden_shoulder_batched.npz

# 3. Check results
# - artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/sweep_summary.json
# - artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/sweep_results.csv
```
