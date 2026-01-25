## Round18 Golden S0 Freeze 패키지 봉인

### 요약
- **Tag**: `golden-s0-v0.1`
- **Commit**: `cc15544` (Round17 report) / freeze doc references this
- **원칙**: 이후 Geometric/Validation 이슈는 **S0 generator 수정 없이** metadata/provenance/validation으로 처리

### 재현 커맨드
```bash
rm -f verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz
py verification/datasets/golden/core_measurements_v0/create_s0_dataset.py
py verification/runners/run_geo_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz \
  --n_samples 20 \
  --out_dir verification/runs/facts/geo_v0/round17_valid10_expanded
```

### 산출물 경로
- `verification/runs/facts/geo_v0/round17_valid10_expanded/facts_summary.json`
- `reports/validation/geo_v0_facts_round17_valid10_expanded.md`

### 변경 사항
- `docs/verification/golden_s0_freeze_v0.md` 추가 (freeze 봉인 문서)
- `SYNC_HUB.md` 8.4 Golden S0 (Round17 Freeze) 섹션 추가
- `reports/validation/INDEX.md` 추가 (라운드별 리포트 파일명 고정, round17 기준선)
