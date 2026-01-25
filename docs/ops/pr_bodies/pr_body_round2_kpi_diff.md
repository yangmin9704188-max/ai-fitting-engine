# ops: add KPI_DIFF vs prev and baseline (round2)

## 목적
postprocess_round.py가 KPI.md 생성에 더해, KPI_DIFF.md를 자동 생성하도록 확장.
KPI_DIFF는 "vs prev"와 "vs baseline"을 모두 포함.

## 구현 범위

### 1. tools/summarize_facts_kpi.py 확장
- `generate_kpi_diff()` 함수 추가
- 입력:
  - current facts_summary.json
  - prev facts_summary.json (없으면 None)
  - baseline facts_summary.json (없으면 None)
- 출력: KPI_DIFF.md (Markdown)
- 표준 포맷:
  - A) Header: current_run_dir, prev_run_dir, baseline_run_dir, 생성 시각
  - B) NaN Rate Top5 변화: current/prev/baseline 및 delta (%p)
  - C) Failure Reason Top5 변화: current/prev/baseline 및 delta
  - D) Core Distributions: HEIGHT_M p50/p95, BUST/WAIST/HIP p50
  - E) Notes: prev fallback 상태, missing 데이터 처리

### 2. tools/postprocess_round.py 업데이트
- KPI.md 생성 이후에 KPI_DIFF.md 생성 추가
- 동작:
  - prev_run_dir 및 baseline_run_dir에서 facts_summary.json 탐색
  - 우선순위: 직접 경로 → 하위 디렉토리
  - 없으면 warning 출력 후 N/A 처리 (크래시 금지)
  - 출력: `<current_run_dir>/KPI_DIFF.md`

## 변경 파일 목록

- `tools/postprocess_round.py` (업데이트: KPI_DIFF 생성 로직 추가)
- `tools/summarize_facts_kpi.py` (확장: generate_kpi_diff 함수 추가)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 스모크 테스트

### 실행 명령
```bash
py tools/postprocess_round.py \
  --current_run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

### 기대 결과
- ✅ KPI.md가 유지/갱신
- ✅ KPI_DIFF.md 생성
- ✅ prev/baseline fallback 상태가 Notes에 표시

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (2 entries)

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- KPI.md 유지/갱신 확인
- KPI_DIFF.md 생성 확인
- Notes에 "Prev run dir fell back to baseline" 표시 확인
- 모든 섹션 (Header, NaN Rate, Failure Reason, Core Distributions, Notes) 포함 확인

## KPI_DIFF.md 샘플 구조

생성된 KPI_DIFF.md는 다음 섹션을 포함:
- Header: current/prev/baseline run dir 및 생성 시각
- NaN Rate Top5 Changes: 테이블 형식으로 current/prev/baseline 및 delta 표시
- Failure Reason Top5 Changes: 테이블 형식으로 current/prev/baseline 및 delta 표시
- Core Distributions: HEIGHT_M p50/p95, BUST/WAIST/HIP p50 비교
- Notes: prev fallback 상태 및 missing 데이터 처리 정보

## 참고
- 이번 PR에서는 coverage_backlog/lineage/visual은 구현하지 않음 (다음 rounds 예정)
- Python 3.10 기준, 크래시 없이 N/A 처리 우선
