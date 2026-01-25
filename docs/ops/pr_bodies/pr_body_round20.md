## Round20: Curated v0 실데이터 Golden NPZ + Facts Runner

### Generator freeze 준수 (수정 없음)
- **Golden S0 generator는 수정하지 않았습니다.** `create_s0_dataset.py` 및 Geometric 로직 변경 없음.
- Round20은 Validation/Metadata 작업이며, 실데이터 분포/결측/경고를 facts-only로 기록합니다.

### 변경 파일 목록 / 의도

| 파일 | 의도 |
|------|------|
| `verification/datasets/golden/core_measurements_v0/create_real_data_golden.py` | **신규.** curated_v0/m_standard 자동 탐색 → `golden_real_data_v0.npz` 생성. `meta_unit=m`, `schema_version=core_measurements_v0_real@1`, measurements/case_id/case_metadata. |
| `verification/runners/run_curated_v0_facts_round1.py` | **신규.** NPZ 로드 → 키별 count/nan/min/median/max, warnings_top5 → facts_summary.json + md. HEIGHT/BUST/WAIST/HIP/NECK 상단 배치, 절대경로 PROOF 출력. |
| `reports/validation/INDEX.md` | Round20 항목 추가. NPZ/리포트/facts_summary 경로 및 실행 커맨드. |
| `reports/validation/curated_v0_facts_round1.md` | Round20 고정 리포트 (runner가 매 실행 시 복사). |

### 실행 커맨드

```bash
# 1) Golden NPZ 생성 (smoke: --n_cases 30)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --n_cases 200 \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

# 2) Facts runner
py verification/runners/run_curated_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_dir verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)
```

### 산출물 경로
- NPZ: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz`
- Report: `reports/validation/curated_v0_facts_round1.md`
- Summary: `verification/runs/facts/curated_v0/round20_<timestamp>/facts_summary.json`
