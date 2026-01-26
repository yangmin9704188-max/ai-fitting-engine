# PR: Round35 - KPI 분포 통계 스키마 연결

## 목적

Round34에서 Processed=5, NPZ/Visual 생성 성공, NaN Rate는 집계되었으나, KPI 분포 통계(p50/p95)와 BUST/WAIST/HIP p50이 N/A로 남아있었습니다.

이번 라운드는 **"분포 통계가 N/A가 되는 원인"**을 facts-only로 규명하고, `summarize_facts_kpi.py` ↔ `facts_summary.json` 스키마/키 연결을 최소 수정으로 바로잡습니다.

## 원인 분석 (facts-only)

### 관측된 사실
- Round34 실행 결과: `facts_summary.json`에 `summary[key]["value_stats"]["median"]` 및 `summary[key]["value_stats"]["max"]`가 존재함
- KPI.md 출력: HEIGHT_M Distribution p50/p95가 N/A, BUST/WAIST/HIP p50이 N/A

### 원인 규명
- `tools/summarize_facts_kpi.py`의 `get_value_distribution` 함수가 `summary[key]["median"]`을 직접 찾음
- 실제 `facts_summary.json` 구조는 `summary[key]["value_stats"]["median"]`에 통계값이 저장됨
- 키 경로 불일치로 인해 통계값을 찾지 못하여 N/A 반환

## 변경 사항

### 1. `tools/summarize_facts_kpi.py`

#### get_value_distribution 함수 보강
- 기존: `summary[key]["median"]`만 확인
- 변경: 다중 경로 fallback 추가
  - Path 1: `key_stats["median"]` (direct)
  - Path 2: `key_stats["value_stats"]["median"]` (geo_v0_s1 runner 구조)
  - Path 3: `key_stats["values"]` 배열에서 직접 계산 (최후 fallback)
- numpy import 추가 (median 계산용)

### 2. `docs/ops/INDEX.md`
- Round35 엔트리 추가

### 3. `reports/validation/INDEX.md`
- Round35 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round35_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. KPI.md에서 HEIGHT_M Distribution p50/p95가 N/A가 아닌지 확인
```bash
# KPI.md에서 확인
cat verification/runs/facts/geo_v0_s1/round35_*/KPI.md | grep -A 3 "HEIGHT_M Distribution"
```

**예상 결과**: 
- p50: 숫자 값 (예: 1.70 m)
- p95: 숫자 값 (예: 1.75 m)
- N/A가 아님

### 2. KPI.md에서 BUST/WAIST/HIP p50이 N/A가 아닌지 확인
```bash
# KPI.md에서 확인
cat verification/runs/facts/geo_v0_s1/round35_*/KPI.md | grep -A 5 "BUST/WAIST/HIP p50"
```

**예상 결과**: 
- BUST_CIRC_M: 숫자 값 (N/A 아님)
- WAIST_CIRC_M: 숫자 값 (N/A 아님)
- HIP_CIRC_M: 숫자 값 (N/A 아님)
- (측정된 키만 표시, 측정되지 않은 키는 N/A 가능)

### 3. postprocess 산출물 생성 확인
```bash
# KPI, KPI_DIFF, LINEAGE 존재 확인
ls -la verification/runs/facts/geo_v0_s1/round35_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round35_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round35_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

### 4. facts_summary.json 구조 확인
```bash
# value_stats 구조 확인
cat verification/runs/facts/geo_v0_s1/round35_*/facts_summary.json | python -m json.tool | grep -A 5 "value_stats" | head -20
```

**예상 결과**: 
- `summary[key]["value_stats"]["median"]` 존재
- `summary[key]["value_stats"]["max"]` 존재

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ Semantic 재해석/단위 재논의 금지
- ✅ 측정 알고리즘 정답 튜닝 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
- ✅ 최소 수정 원칙: runner는 변경하지 않고, KPI 요약기만 보강
