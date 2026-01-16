# Frozen Policy Verification Scripts

This directory contains verification scripts for the two frozen policies:
1. **A-Pose Normalization v1.1**
2. **Shoulder Width v1.1.2**

## ⚠️ Important: Execution Requirements

**All verification scripts MUST be run from the project root directory.**

The project root is the directory containing `core/`, `verification/`, `pipelines/`, etc.

### Windows PowerShell Example:
```powershell
# Navigate to project root first
cd "C:\Users\caino\Desktop\ai model"

# Then run verification scripts (either method works):
# Method A: python -m (recommended)
py -m verification.runners.verify_apose_v11 --n_cases 20

# Method B: Direct script execution (also works)
py verification/runners/verify_apose_v11.py --n_cases 20
```

### Why?
- `core/` is a top-level package in the project root
- Python needs the project root in `sys.path` to resolve `core.*` imports
- Bootstrap code in scripts automatically adds the project root to `sys.path`
- `python -m` mode automatically adds the project root to `sys.path`

## Overview

Each verification script:
- Runs with a single command (from project root)
- Generates `results.csv` and `summary.json` in the output directory
- Records `cfg_used` / policy tag / version in `summary.json` (Policy-to-Run wiring proof)
- Saves `case_*_debug.json` for failed cases

---

## (A) A-Pose Normalization v1.1

### Script
`verification/runners/verify_apose_v11.py`

### Verification Criteria
- ✅ dtype float32 maintained
- ✅ axis convention (y-axis only)
- ✅ A-Pose angle range (30-45 deg, tol ±5) → [25, 50] deg violation rate = 0
- ✅ exceptions = 0

### Usage
```bash
py verification/runners/verify_apose_v11.py [--model_path ./models] [--data_dir ./data/processed/step1_output] [--out_dir verification/reports/apose_v11] [--n_cases 20]
```

### Output Files
- `verification/reports/apose_v11/verification_results.csv`
- `verification/reports/apose_v11/verification_summary.json`
- `verification/reports/apose_v11/case_*_debug.json` (for failures)

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.verify_apose_v11 --n_cases 20

# Method B: Direct script
py verification/runners/verify_apose_v11.py --n_cases 20
```

### Summary JSON Structure
```json
{
  "policy_version": "A-Pose Normalization v1.1",
  "policy_tag": "pose_apose_v11_frozen_2026-01-16",
  "cfg_used": {
    "angle_deg": 30.0,
    "axis": "y",
    "l_idx": 16,
    "r_idx": 17,
    "sign_l": 1.0,
    "sign_r": -1.0
  },
  "verification_criteria": {...},
  "results": {...},
  "compliance": {...}
}
```

---

## (B) Shoulder Width v1.1.2

### Script
`verification/runners/verify_shoulder_width_v112.py`

### Verification Criteria
- ✅ cfg_used == cfg_frozen (policy-to-run wiring proof)
- ✅ ratio = measured_sw / joint_sw in [1.0, 1.3] range
- ✅ ||lm - shoulder_joint|| < 0.20m (L/R)
- ✅ fallback/exceptions = 0
- ✅ worst-case 1 debug JSON saved

### Usage

**⚠️ Run from project root:**
```powershell
# Method A: python -m (recommended)
py -m verification.runners.verify_shoulder_width_v112 --npz <path_to_npz> [--out_dir verification/reports/shoulder_width_v112]

# Method B: Direct script execution
py verification/runners/verify_shoulder_width_v112.py --npz <path_to_npz> [--out_dir verification/reports/shoulder_width_v112]
```

### Input NPZ Format
NPZ file must contain:
- `verts`: (T, N, 3) or (N, 3) - vertices
- `lbs_weights`: (T, N, J) or (N, J) - LBS weights
- `joints_xyz`: (T, J, 3) or (J, 3) - joint positions

### Output Files
- `verification/reports/shoulder_width_v112/verification_results.csv`
- `verification/reports/shoulder_width_v112/verification_summary.json`
- `verification/reports/shoulder_width_v112/case_*_debug.json` (for failures/worst-case)

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.verify_shoulder_width_v112 --npz verification/datasets/golden_shoulder_batched.npz

# Method B: Direct script
py verification/runners/verify_shoulder_width_v112.py --npz verification/datasets/golden_shoulder_batched.npz
```

### Summary JSON Structure
```json
{
  "policy_version": "Shoulder Width v1.1.2",
  "policy_tag": "shoulder_width_v112_frozen_2026-01-16",
  "cfg_used": {
    "r0_ratio": 0.26,
    "r1_ratio": 0.18,
    "cap_quantile": 0.94,
    ...
  },
  "cfg_expected": {
    "r0_ratio": 0.26,
    "r1_ratio": 0.18,
    "cap_quantile": 0.94
  },
  "verification_criteria": {...},
  "results": {...},
  "compliance": {...}
}
```

---

## (C) Golden Set Export

### Script
`verification/datasets/export_golden_shoulder_npz.py`

### Purpose
Generate NPZ files containing `verts`/`lbs_weights`/`joints_xyz`/`joint_ids` for shoulder width verification.

### Usage

**⚠️ Run from project root:**
```powershell
# Method A: python -m (recommended)
py -m verification.datasets.export_golden_shoulder_npz [--model_path ./models] [--data_dir ./data/processed/step1_output] [--out_dir verification/datasets] [--n_cases 10] [--format batched|individual]

# Method B: Direct script execution
py verification/datasets/export_golden_shoulder_npz.py [--model_path ./models] [--data_dir ./data/processed/step1_output] [--out_dir verification/datasets] [--n_cases 10] [--format batched|individual]
```

### Output Files
- **Batched format**: `verification/datasets/golden_shoulder_batched.npz` (single file with all cases)
- **Individual format**: `verification/datasets/golden_shoulder_001.npz`, `golden_shoulder_002.npz`, ... (one file per case)

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.datasets.export_golden_shoulder_npz --n_cases 10 --format batched
py -m verification.datasets.export_golden_shoulder_npz --n_cases 10 --format individual

# Method B: Direct script
py verification/datasets/export_golden_shoulder_npz.py --n_cases 10 --format batched
py verification/datasets/export_golden_shoulder_npz.py --n_cases 10 --format individual
```

### NPZ Contents
- `verts`: (T, N, 3) or (N, 3) - vertices in float32
- `lbs_weights`: (T, N, J) or (N, J) - LBS weights in float32
- `joints_xyz`: (T, J, 3) or (J, 3) - joint positions in float32 (first 55 joints)
- `joint_ids`: dict with keys "L_shoulder", "R_shoulder", "L_elbow", "R_elbow", "L_wrist", "R_wrist"

---

## Quick Start

### 1. Generate Golden Set

**⚠️ Run from project root:**
```powershell
# Method A: python -m
py -m verification.datasets.export_golden_shoulder_npz --n_cases 10 --format batched

# Method B: Direct script
py verification/datasets/export_golden_shoulder_npz.py --n_cases 10 --format batched
```

### 2. Verify A-Pose

**⚠️ Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.verify_apose_v11 --n_cases 20

# Method B: Direct script
py verification/runners/verify_apose_v11.py --n_cases 20
```

### 3. Verify Shoulder Width

**⚠️ Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.verify_shoulder_width_v112 --npz verification/datasets/golden_shoulder_batched.npz

# Method B: Direct script
py verification/runners/verify_shoulder_width_v112.py --npz verification/datasets/golden_shoulder_batched.npz
```

---

## (D) Shoulder Width v1.2 Extended Golden Set Export

### Script
`verification/tools/export_golden_shoulder_v12_npz.py`

### Purpose
Generate extended golden dataset (>= 200 frames) for v1.2 regression verification.
Includes variation in body shapes to test measurement robustness.

### Usage

**⚠️ Run from project root:**
```powershell
# Method A: python -m (recommended)
py -m verification.tools.export_golden_shoulder_v12_npz [--model_path ./models] [--data_dir ./data/processed/step1_output] [--out_dir verification/datasets/golden/shoulder_width] [--n_frames 200]

# Method B: Direct script execution
py verification/tools/export_golden_shoulder_v12_npz.py [--model_path ./models] [--data_dir ./data/processed/step1_output] [--out_dir verification/datasets/golden/shoulder_width] [--n_frames 200]
```

### Output Files
- **Extended dataset**: `verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz`

### NPZ Contents
- `verts`: (T, N, 3) - vertices in float32 (T >= 200 frames)
- `lbs_weights`: (T, N, J) - LBS weights in float32
- `joints_xyz`: (T, J, 3) - joint positions in float32 (first 55 joints)
- `joint_ids`: dict with keys "L_shoulder", "R_shoulder", "L_elbow", "R_elbow", "L_wrist", "R_wrist"
- `provenance`: JSON string with dataset generation metadata

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.tools.export_golden_shoulder_v12_npz --n_frames 200

# Method B: Direct script
py verification/tools/export_golden_shoulder_v12_npz.py --n_frames 200
```

---

## (E) Shoulder Width v1.2 Regression Verification (Frozen Gate)

### Script
`verification/runners/shoulder_width/verify_shoulder_width_v12_regression.py`

### Purpose
Verify v1.2 measurement on extended golden set using fixed default config.
This is the Candidate -> Frozen verification gate.

### Fixed Default Config
- `plane_height_tolerance`: 0.08
- `arm_distance_threshold`: 0.12
- `arm_alignment_cosine_threshold`: 0.50
- `lateral_quantile`: 0.90

### Verification Criteria
- ✅ fallback = 0
- ✅ exception = 0
- ✅ wiring proof hash stable and unique for the cfg
- ✅ arm_excluded_count non-trivial across frames (not zeroing out)
- ✅ no obvious "arm leakage" signatures (ratio spikes, delta spikes, cross_section_count anomalies)

### Usage

**⚠️ Run from project root:**
```powershell
# Method A: python -m (recommended)
py -m verification.runners.shoulder_width.verify_shoulder_width_v12_regression [--npz verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz] [--out_dir artifacts/shoulder_width/v1.2/regression/YYYYMMDD_<STATUS>]

# Method B: Direct script execution
py verification/runners/shoulder_width/verify_shoulder_width_v12_regression.py [--npz verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz] [--out_dir artifacts/shoulder_width/v1.2/regression/YYYYMMDD_<STATUS>]
```

### Input NPZ Format
NPZ file must contain:
- `verts`: (T, N, 3) - vertices (T >= 200 frames)
- `lbs_weights`: (T, N, J) - LBS weights
- `joints_xyz`: (T, J, 3) - joint positions
- `joint_ids`: dict with joint name mappings

### Output Files
All artifacts are saved under:
`artifacts/shoulder_width/v1.2/regression/YYYYMMDD_<PASS|PARTIAL|FAIL>/`

- `wiring_proof.json` - Single cfg + hash (includes git_head_sha if available)
- `regression_results.csv` - Per-frame results (all frames)
- `regression_summary.json` - Overall statistics and success criteria
- `worst_cases.json` - Top N frames with largest deltas or suspicious counts

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.shoulder_width.verify_shoulder_width_v12_regression --npz verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz

# Method B: Direct script
py verification/runners/shoulder_width/verify_shoulder_width_v12_regression.py --npz verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz
```

### Summary JSON Structure
```json
{
  "timestamp": "2026-01-17T...",
  "status": "PASS|PARTIAL|FAIL",
  "git_head_sha": "abc12345",
  "golden_set": "verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz",
  "n_frames": 200,
  "config": {
    "plane_height_tolerance": 0.08,
    "arm_direction_exclusion_threshold": 0.50,
    "arm_distance_threshold": 0.12,
    "lateral_quantile": 0.90
  },
  "cfg_hash": "...",
  "overall_statistics": {...},
  "statistics": {...},
  "pose_perturbation": {...},
  "worst_cases_count": N,
  "success_criteria": {...}
}
```

---

## (F) Smart Mapper Sanity Check with Shoulder Width v1.2 (Optional)

### Script
`verification/runners/smart_mapper/verify_smart_mapper_with_sw_v12.py`

### Purpose
Minimal sanity check to ensure Smart Mapper works with v1.2 shoulder width.
Tests a small batch (10-20 samples) to confirm:
- Loss is finite
- Gradients/optimization do not explode
- v1.2 measurement integration works

### Note
This check is optional and can be skipped if Smart Mapper module is not available in the repository.

### Usage

**⚠️ Run from project root:**
```powershell
# Method A: python -m (recommended)
py -m verification.runners.smart_mapper.verify_smart_mapper_with_sw_v12 [--model_path ./models] [--data_dir ./data/processed/step1_output] [--n_samples 10] [--out_dir artifacts/verification/smart_mapper_sw_v12]

# Method B: Direct script execution
py verification/runners/smart_mapper/verify_smart_mapper_with_sw_v12.py [--model_path ./models] [--data_dir ./data/processed/step1_output] [--n_samples 10] [--out_dir artifacts/verification/smart_mapper_sw_v12]
```

### Output Files
- `artifacts/verification/smart_mapper_sw_v12/sanity_check_results.csv` - Per-case results
- `artifacts/verification/smart_mapper_sw_v12/sanity_check_summary.json` - Summary statistics

### Example

**Run from project root:**
```powershell
# Method A: python -m
py -m verification.runners.smart_mapper.verify_smart_mapper_with_sw_v12 --n_samples 10

# Method B: Direct script
py verification/runners/smart_mapper/verify_smart_mapper_with_sw_v12.py --n_samples 10
```

---

## File Structure

```
verification/
├── runners/
│   ├── verify_apose_v11.py                    # A-Pose v1.1 verification
│   ├── verify_shoulder_width_v112.py          # Shoulder Width v1.1.2 verification
│   ├── verify_smart_mapper_v001.py            # Smart Mapper v0.1 verification
│   ├── sweep_shoulder_width_v112.py           # Shoulder width parameter sweep
│   ├── step2_verify_pose.py                   # Pose verification
│   ├── verify_policy.py                       # Policy verification
│   └── shoulder_width/
│       └── verify_shoulder_width_v113_sweep.py # v1.1.3 candidate sweep
├── datasets/
│   ├── export_golden_shoulder_npz.py          # Golden set export
│   ├── golden_shoulder_batched.npz            # Generated golden set (batched)
│   └── dummy_data.npz                         # Dummy test data
├── tools/
│   ├── check_smplx_weights.py                 # SMPL-X weights checker
│   ├── inspect_smplx_joints.py                # SMPL-X joints inspector
│   ├── step0_make_dummy.py                    # Dummy data generator
│   └── summarize_sanity_checks.py             # Sanity check summarizer
├── debug/
│   ├── debug_shoulder_width_case2.py          # Shoulder width debug script
│   └── debug_output/                          # Debug output files
├── reports/
│   ├── apose_v11/
│   │   ├── verification_results.csv
│   │   ├── verification_summary.json
│   │   └── case_*_debug.json (if failures)
│   └── shoulder_width_v112/
│       ├── verification_results.csv
│       ├── verification_summary.json
│       └── case_*_debug.json (if failures/worst-case)
└── README_VERIFICATION.md                     # This file
```

---

## Notes

1. **Policy-to-Run Wiring Proof**: Both verification scripts record `cfg_used` in `summary.json` to prove that the correct frozen policy configuration is being used.

2. **Debug Files**: Failed cases automatically save debug JSON files. For shoulder width, the worst-case (last frame) is also saved.

3. **Exit Codes**: Scripts exit with code 0 if all checks pass, 1 otherwise.

4. **Dependencies**: All scripts require:
   - SMPL-X models in `./models/`
   - Beta means from step1 output in `./data/processed/step1_output/`
   - Python packages: torch, smplx, numpy, pandas
