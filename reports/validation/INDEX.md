# Validation Reports Index

Round-specific facts reports (fixed filenames). **Baseline**: Round 17.

| Round | Filename |
|-------|----------|
| 13 | `geo_v0_facts_round13_fastmode_normal1_runner.md` |
| 15 | `geo_v0_facts_round15_bust_verts_aligned_normal1.md` |
| 16 | `geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md` |
| **17** | **`geo_v0_facts_round17_valid10_expanded.md`** (현재 기준선) |
| 20 | `curated_v0_facts_round1.md` |

See `docs/verification/golden_s0_freeze_v0.md` for S0 reproduce commands and freeze rule.

## Round 20 (Curated v0 Real Data Golden)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz`
- **Report**: `reports/validation/curated_v0_facts_round1.md`
- **Facts summary**: `verification/runs/facts/curated_v0/round20_<timestamp>/facts_summary.json`

### Run commands

```bash
# 1) Create real-data golden NPZ (smoke: --n_cases 30)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --n_cases 200 \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

# 2) Facts runner (out_dir default: round20_<timestamp>)
py verification/runners/run_curated_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_dir verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)
```
