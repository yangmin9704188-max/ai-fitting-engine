# Round Operations v0

라운드 실행 표준 프로세스 및 후처리 가이드입니다.

## 표준 실행 커맨드 템플릿

### 1. Runner 실행

```bash
# 예: curated_v0 facts runner
py verification/runners/run_curated_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_dir verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)
```

### 2. 후처리 (필수)

```bash
# Runner 실행 후 반드시 postprocess 실행
py tools/postprocess_round.py \
  --run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

**후처리 도구가 생성하는 파일:**
- `KPI.md`: KPI 헤더 (markdown)
- `kpi.json`: KPI 데이터 (JSON)
- `KPI_DIFF.md`: Prev/Baseline 대비 diff
- `ROUND_CHARTER.md`: 라운드 헌장 (템플릿 기반, 없을 때만 생성)

## Baseline 설정

Baseline은 고정 기준선으로, 모든 라운드와 비교할 수 있습니다.

### Baseline 설정 방법

```bash
# 1. 먼저 해당 run_dir에 대해 postprocess 실행
py tools/postprocess_round.py --run_dir <run_dir>

# 2. Baseline으로 설정
py tools/set_baseline_run.py \
  --run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

Baseline은 `verification/runs/facts/_baseline.json`에 기록됩니다.

### Baseline 변경

Baseline을 변경하려면 `set_baseline_run.py`를 다시 실행하면 됩니다.

## Coverage Backlog

`docs/verification/coverage_backlog.md`는 자동으로 업데이트됩니다:
- NaN 100% 키
- VALUE_MISSING 100% 키

이 파일은 facts-only 기록이며, 판정/추측 없이 누적됩니다.

## KPI Diff 구조

`KPI_DIFF.md`는 두 섹션을 포함합니다:

1. **Diff vs Prev**: 이전 라운드와의 비교
2. **Diff vs Baseline**: 고정 기준선과의 비교

각 섹션은 다음을 포함합니다:
- NaN rate 변화 (Top 5)
- Failure reason 변화 (Top 5)
- HEIGHT/BUST/WAIST/HIP p50 변화
