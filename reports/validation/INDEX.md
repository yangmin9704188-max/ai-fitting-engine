# Validation Reports Index

Round-specific facts reports (fixed filenames). **Baseline**: Round 17.

| Round | Filename |
|-------|----------|
| 13 | `geo_v0_facts_round13_fastmode_normal1_runner.md` |
| 15 | `geo_v0_facts_round15_bust_verts_aligned_normal1.md` |
| 16 | `geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md` |
| **17** | **`geo_v0_facts_round17_valid10_expanded.md`** (현재 기준선) |
| 20 | `curated_v0_facts_round1.md` |
| 21 | `curated_v0_facts_round21.md` (Gate: [docs/policies/validation/curated_v0_realdata_gate_v0.md](../policies/validation/curated_v0_realdata_gate_v0.md)) |
| 22 | `curated_v0_facts_round22.md` (Freeze: [docs/verification/golden_real_data_freeze_v0.1.md](../../verification/golden_real_data_freeze_v0.1.md)) |

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

## Round 21 (Curated v0 Real Data Golden - Gate v0)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz` (Round20과 동일)
- **Report**: `reports/validation/curated_v0_facts_round21.md`
- **Gate Document**: [`docs/policies/validation/curated_v0_realdata_gate_v0.md`](../policies/validation/curated_v0_realdata_gate_v0.md)
- **Facts summary**: `verification/runs/facts/curated_v0/round21_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/curated_v0/round21_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

## Round 22 (Curated v0 Real Data Golden - Freeze v0.1)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz` (manifest 기반 재생성)
- **Manifest**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json` (SSoT)
- **Report**: `reports/validation/curated_v0_facts_round22.md`
- **Freeze Document**: [`docs/verification/golden_real_data_freeze_v0.1.md`](../../verification/golden_real_data_freeze_v0.1.md)
- **Facts summary**: `verification/runs/facts/curated_v0/round22_<timestamp>/facts_summary.json`

### Run commands

```bash
# 1) Recreate NPZ from manifest (SSoT mode - bypasses sampling)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --case_ids_json verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

# 2) Facts runner
RUN_DIR="verification/runs/facts/curated_v0/round22_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

**주의**: Round22는 동일 케이스 재실행이므로 원칙상 KPI_DIFF는 0에 수렴하는 것이 정상입니다.
0이 아니면 "재생성 로직의 결정성(Determinism) 문제 가능성"이라는 강력 경고 신호입니다.
