# PR: Round36 - 둘레 계산 디버그 계측

## 목적

Round35에서 KPI 분포(p50/p95) 와이어링은 완료되었으나, 둘레 값(WAIST_CIRC_M~19.72m, BUST_CIRC_M~134.75m)이 물리적으로 불가능한 값으로 관측되었습니다.

이번 라운드는 **정답 튜닝이 아니라, 둘레 계산 로직의 원인을 facts-only로 분해하기 위한 "디버그 계측"**을 추가합니다.

## 변경 사항

### 1. `core/measurements/core_measurements_v0.py`

#### `_compute_perimeter` 함수에 디버그 모드 추가
- `return_debug` 파라미터 추가
- 디버그 모드 시 반환값: `(perimeter, debug_info)` 튜플
- 디버그 정보 수집:
  - `n_points`: 둘레 포인트 수
  - `bbox_before`: 정렬 전 bbox (min/max/max_abs)
  - `bbox_after`: 정렬 후 bbox
  - `segment_len_stats`: min/mean/max/p95 (연속 점 거리)
  - `jump_count`: segment_len > mean*10 같은 outlier 개수
  - `perimeter_raw`: 합산 길이
  - `perimeter_final`: 리턴 값
  - `points_sorted`: True (polar angle sorting)
  - `notes`: 감지된 이슈 (jump_detected, large_bbox_before 등)

#### `_compute_circumference_at_height` 함수에 디버그 모드 추가
- `return_debug` 파라미터 추가
- 선택된 candidate에 대해 디버그 정보 수집

#### `measure_circumference_v0_with_metadata` 함수에 circ_debug 생성
- 선택된 candidate에 대해 `_compute_circumference_at_height`를 `return_debug=True`로 재호출
- `circ_debug` 정보 생성:
  - `schema_version`: "circ_debug@1"
  - `key`: standard_key (WAIST_CIRC_M 등)
  - `n_points`, `axis`, `plane`, `scale_applied`, `bbox_before/after`
  - `segment_len_stats`, `jump_count`, `perimeter_raw/final`, `notes`
  - `reason`: SCALE_SUSPECTED, ORDERING_SUSPECTED, PROJECTION_SUSPECTED, OTHER
- `circ_debug`를 metadata의 `debug_info.circ_debug`에 포함

### 2. `verification/runners/run_geo_v0_s1_facts.py`

#### circ_debug 정보 수집 및 facts_summary.json 기록
- `circ_debug_by_key` 딕셔너리로 각 둘레 키별 디버그 정보 수집
- `facts_summary.json`에 `circ_debug` 섹션 추가:
  - 각 키별로 첫 번째 processed case의 circ_debug 정보 저장
  - `sample_count` 필드로 총 수집된 케이스 수 기록

### 3. `docs/ops/INDEX.md`
- Round36 엔트리 추가

### 4. `reports/validation/INDEX.md`
- Round36 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round36_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. 둘레 값 확인
```bash
# facts_summary.json에서 둘레 값 확인
cat verification/runs/facts/geo_v0_s1/round36_*/facts_summary.json | python -m json.tool | grep -A 2 -E "(WAIST_CIRC_M|BUST_CIRC_M|HIP_CIRC_M)" | grep "value_m"
```

**예상 결과**: 둘레 값이 기록됨 (예: WAIST_CIRC_M~19.72m, BUST_CIRC_M~134.75m 등)

### 2. circ_debug 출력 일부 확인
```bash
# facts_summary.json에서 circ_debug 확인
cat verification/runs/facts/geo_v0_s1/round36_*/facts_summary.json | python -m json.tool | grep -A 20 "circ_debug"
```

**예상 결과**: 
- `circ_debug` 섹션 존재
- 각 둘레 키(WAIST_CIRC_M, BUST_CIRC_M, HIP_CIRC_M)별 circ_debug 정보
- 필수 필드: `schema_version`, `key`, `n_points`, `bbox_before`, `bbox_after`, `segment_len_stats`, `jump_count`, `perimeter_raw`, `perimeter_final`, `reason`

### 3. circ_debug 필드 상세 확인
```bash
# WAIST_CIRC_M circ_debug 상세 확인
cat verification/runs/facts/geo_v0_s1/round36_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); print(json.dumps(data.get('circ_debug', {}).get('WAIST_CIRC_M', {}), indent=2))"
```

**예상 결과**:
- `n_points`: 숫자 (둘레 포인트 수)
- `bbox_before.max_abs`: 숫자 (스케일 의심 여부 판단)
- `scale_applied`: true/false
- `segment_len_stats`: min/mean/max/p95 통계
- `jump_count`: 숫자 (outlier 개수)
- `reason`: SCALE_SUSPECTED, ORDERING_SUSPECTED, PROJECTION_SUSPECTED, OTHER 중 하나

### 4. postprocess 산출물 생성 확인
```bash
# KPI, KPI_DIFF, LINEAGE 존재 확인
ls -la verification/runs/facts/geo_v0_s1/round36_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round36_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round36_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

### 5. 원인 분류 reason 확인
```bash
# 모든 둘레 키의 reason 확인
cat verification/runs/facts/geo_v0_s1/round36_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); circ_debug = data.get('circ_debug', {}); print('\n'.join([f'{k}: {v.get(\"reason\", \"N/A\")}' for k, v in circ_debug.items()]))"
```

**예상 결과**: 
- 각 키별 reason 코드 출력 (SCALE_SUSPECTED, ORDERING_SUSPECTED, PROJECTION_SUSPECTED, OTHER)

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ 클램프/보정(정답 맞추기) 금지
- ✅ Semantic 재해석/단위 재논의 금지 (단, 스케일 적용 여부/값은 로그로 기록)
- ✅ 측정 알고리즘 정답 튜닝 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
- ✅ 정답 보정 금지: 계측으로 원인을 "사실"로 남기는 라운드
