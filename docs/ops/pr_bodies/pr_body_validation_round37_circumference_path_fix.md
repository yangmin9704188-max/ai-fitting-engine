# PR: Round37 - 둘레 계산 경로 안정화

## 목적

Round36 facts에 따르면 WIDTH/DEPTH는 타당하나 CIRC(둘레)만 19m~134m로 폭증합니다. 따라서 단면 추출이 아니라 **"추출된 점들을 연결해 perimeter를 계산하는 경로/순서 알고리즘"**이 원인입니다.

이번 라운드는 정답 클램프 금지, 최소 변경으로 **'폐곡선 경로'를 안정적으로 구성하여 폭증을 제거**합니다.

## 변경 사항

### 1. `core/measurements/core_measurements_v0.py`

#### `_compute_perimeter` 함수 개선 (Round37)

**문제점**: 점들의 순서가 랜덤/불안정하여 "점프" 세그먼트가 생기고 perimeter가 폭증

**해결책**: 옵션 A (권장, 단순/안정) - 2D 투영 후 각도 정렬(Polar sort) + 폐곡선

1. **중복점 제거 (Deduplication)**:
   - epsilon = 1e-6 (1 micron) tolerance로 near-duplicate 제거
   - `n_points_deduped` 필드로 제거 후 점 수 기록

2. **안정적인 Polar Angle Sorting**:
   - 중심점 계산: `center = mean(vertices_2d)`
   - 각도 계산: `angles = atan2(y-cy, x-cx)`
   - 동일각 처리: 같은 각도를 가진 점들은 중심으로부터의 거리로 정렬 후 작은 perturbation 추가

3. **폐곡선 경로 구성**:
   - 정렬된 점들을 순서대로 연결: `perimeter = sum(||p[i+1]-p[i]||)`
   - Closing edge: 마지막 점이 첫 번째 점과 연결 (`(i + 1) % n`)

4. **Round36 계측 유지/확장**:
   - `perimeter_raw`: 이전 방식 (또는 첫 실행 시 현재 값)
   - `perimeter_new`: 새 방식 (dedupe + stable sort)
   - `perimeter_final`: 최종 값 (Round36 호환성)
   - `dedupe_applied`: 중복점 제거 적용 여부
   - `dedupe_count`: 제거 후 점 수
   - `segment_len_stats`, `jump_count` 유지

#### `measure_circumference_v0_with_metadata` 함수 수정

- 선택된 candidate에 대해 `_compute_circumference_at_height`를 `return_debug=True`로 재호출하여 새 perimeter 계산
- `circ_debug`에 `perimeter_raw`와 `perimeter_new` 비교 정보 포함

### 2. `docs/ops/INDEX.md`
- Round37 엔트리 추가

### 3. `reports/validation/INDEX.md`
- Round37 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round37_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. 둘레 값 개선 확인 (Round36 대비)

```bash
# Round36과 Round37의 BUST_CIRC_M p50 비교
# Round36
cat verification/runs/facts/geo_v0_s1/round36_*/KPI.md | grep -A 5 "BUST_CIRC_M" | grep "p50"

# Round37
cat verification/runs/facts/geo_v0_s1/round37_*/KPI.md | grep -A 5 "BUST_CIRC_M" | grep "p50"
```

**예상 결과**: 
- Round36: BUST_CIRC_M p50 ~134.75m (또는 비정상적으로 큰 값)
- Round37: BUST_CIRC_M p50 < 1.5m (목표 지표, 미달이어도 원인/계측 수치가 남아야 함)

### 2. KPI.md에서 둘레 값 확인

```bash
# BUST_CIRC_M, WAIST_CIRC_M, HIP_CIRC_M p50 확인
cat verification/runs/facts/geo_v0_s1/round37_*/KPI.md | grep -E "(BUST_CIRC_M|WAIST_CIRC_M|HIP_CIRC_M)" | grep "p50"
```

**예상 결과**: 
- p50이 N/A가 아님
- Round36 대비 비정상적으로 큰 값이 감소
- 목표: BUST_CIRC_M p50 < 1.5m 진입 여부를 사실로 기록

### 3. circ_debug에서 perimeter_raw vs perimeter_new 비교

```bash
# WAIST_CIRC_M circ_debug 상세 확인
cat verification/runs/facts/geo_v0_s1/round37_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); circ_debug = data.get('circ_debug', {}).get('WAIST_CIRC_M', {}); print(f\"perimeter_raw: {circ_debug.get('perimeter_raw', 'N/A')}\"); print(f\"perimeter_new: {circ_debug.get('perimeter_new', 'N/A')}\"); print(f\"dedupe_applied: {circ_debug.get('dedupe_applied', False)}\"); print(f\"dedupe_count: {circ_debug.get('dedupe_count', 0)}\")"
```

**예상 결과**:
- `perimeter_raw`: 이전 방식 값 (또는 첫 실행 시 현재 값)
- `perimeter_new`: 새 방식 값 (dedupe + stable sort)
- `dedupe_applied`: true/false
- `dedupe_count`: 제거 후 점 수
- `perimeter_new`가 `perimeter_raw`보다 현저히 작아야 함 (폭증 제거)

### 4. PERIMETER_LARGE 경고 감소 확인

```bash
# postprocess 출력에서 PERIMETER_LARGE 경고 확인
cat verification/runs/facts/geo_v0_s1/round37_*/KPI.md | grep -i "PERIMETER_LARGE"
cat verification/runs/facts/geo_v0_s1/round37_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); summary = data.get('summary', {}); circ_keys = ['WAIST_CIRC_M', 'BUST_CIRC_M', 'HIP_CIRC_M']; [print(f\"{k}: {summary.get(k, {}).get('warnings', {})}\") for k in circ_keys]"
```

**예상 결과**: 
- PERIMETER_LARGE 경고가 사라졌거나 급감 (사실로 기록)
- 또는 jump_count가 급감

### 5. jump_count 감소 확인

```bash
# circ_debug에서 jump_count 확인
cat verification/runs/facts/geo_v0_s1/round37_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); circ_debug = data.get('circ_debug', {}); [print(f\"{k}: jump_count={v.get('jump_count', 0)}\") for k, v in circ_debug.items()]"
```

**예상 결과**: 
- jump_count가 Round36 대비 급감 (사실로 기록)

### 6. postprocess 산출물 생성 확인

```bash
# KPI, KPI_DIFF, LINEAGE 존재 확인
ls -la verification/runs/facts/geo_v0_s1/round37_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round37_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round37_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ 둘레 값 클램프/하드코딩 상한선 금지
- ✅ Semantic 재해석/단위 재논의 금지 (단, 스케일 경고는 facts로 유지)
- ✅ 측정 알고리즘 정답 튜닝 금지 (경로 안정화만)
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
- ✅ 정답 클램프 금지: 최소 변경으로 경로 안정화만 수행
