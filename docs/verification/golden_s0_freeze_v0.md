# Golden S0 Freeze v0

**Purpose**: S0 golden generator frozen at Round17. Valid ≥10, expected_fail 5, no clamp.

**Tag**: `golden-s0-v0.1`  
**Commit**: `cc15544bc26b244d28463568d1d32660679979d3`  
**Date**: 2026-01-25

---

## How to reproduce

```bash
rm -f verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz
py verification/datasets/golden/core_measurements_v0/create_s0_dataset.py
py verification/runners/run_geo_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz \
  --n_samples 20 \
  --out_dir verification/runs/facts/geo_v0/round17_valid10_expanded
```

---

## Outputs

- `verification/runs/facts/geo_v0/round17_valid10_expanded/facts_summary.json`
- `reports/validation/geo_v0_facts_round17_valid10_expanded.md`

---

## Freeze rule

**이후 발생하는 모든 Geometric/Validation 이슈는 S0 generator를 수정하는 것이 아니라 metadata/provenance/validation으로 해결한다.**

---

## Report filenames (by round)

| Round | Report |
|-------|--------|
| 13 | `geo_v0_facts_round13_fastmode_normal1_runner.md` |
| 15 | `geo_v0_facts_round15_bust_verts_aligned_normal1.md` |
| 16 | `geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md` |
| **17** | **`geo_v0_facts_round17_valid10_expanded.md`** (현재 기준선) |

All under `reports/validation/`.
