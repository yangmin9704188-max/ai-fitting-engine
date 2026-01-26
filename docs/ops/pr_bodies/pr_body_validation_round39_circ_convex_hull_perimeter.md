# PR: Round39 - 둘레 계산을 2D Convex Hull 기반으로 교체

## 목적

Round38b에서 NaN 0%/다양성/스케일 자동변환은 성공했으나, **polar sort 기반 perimeter가 내부/오목 점들을 포함해 경로가 과도하게 길어지는 문제**가 남아있습니다.

따라서 `_compute_perimeter`를 **2D convex hull 기반**으로 교체하여 둘레(CIRC) 값 폭증(수십~수백 m)을 "클램프 없이" 기하학적으로 해결합니다.

## 변경 사항

### 1. `core/measurements/core_measurements_v0.py`

#### `_convex_hull_2d_monotone_chain` 함수 추가 (Round39)
- **알고리즘**: Andrew's monotone chain (numpy-only, SciPy 의존성 없음)
- **시간 복잡도**: O(N log N)
- **동작**:
  1. 점들을 x 좌표로 정렬 (x가 같으면 y로 정렬)
  2. 아래쪽 hull (lower hull) 계산
  3. 위쪽 hull (upper hull) 계산
  4. 두 hull을 합쳐서 convex hull 완성
- **반환**: Convex hull 점들 (counter-clockwise 순서) 또는 None (degenerate case)

#### `_compute_perimeter` 함수 수정 (Round39)
- **기존**: Polar angle sorting 기반 perimeter 계산
- **변경**: 2D convex hull 기반 perimeter 계산
- **Fallback**: Convex hull이 실패하면 (degenerate/collinear) polar sort로 fallback
- **Deduplication**: 기존 quantization-based deduplication 유지

#### debug_info 확장 (Round39)
- `perimeter_method`: "convex_hull_v1"
- `n_points_hull`: Convex hull 점 수
- `fallback_used`: Fallback 사용 여부 (bool)
- `fallback_reason`: Fallback 사유 (str, if any)
- `points_sorted`: True (convex hull) 또는 False (polar sort fallback)

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round39_$(date +%Y%m%d_%H%M%S)" && \
python verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
python tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. KPI.md에서 둘레 값 확인

```bash
# BUST_CIRC_M, WAIST_CIRC_M, HIP_CIRC_M p50 확인
cat verification/runs/facts/geo_v0_s1/round39_*/KPI.md | grep -E "(BUST_CIRC_M|WAIST_CIRC_M|HIP_CIRC_M)" | grep "p50"
```

**예상 결과**: 
- p50이 N/A가 아님
- **p50 < 1.5m** (목표 지표, 미달이어도 원인/계측 수치 기록)

### 2. 둘레값 폭증 제거 확인

```bash
# 둘레 값 분포 확인 (50m/100m급이 없어졌는지)
cat verification/runs/facts/geo_v0_s1/round39_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); summary = data.get('summary', {}); circ_keys = ['WAIST_CIRC_M', 'BUST_CIRC_M', 'HIP_CIRC_M']; [print(f\"{k}: max={summary.get(k, {}).get('value_stats', {}).get('max', 'N/A')}, p95={summary.get(k, {}).get('value_stats', {}).get('max', 'N/A')}\") for k in circ_keys]"
```

**예상 결과**: 
- 둘레값 폭증이 사라짐 (예: 50m/100m급이 없어짐)
- 최대값이 합리적 범위 (예: < 3.0m)

### 3. skip_reasons.jsonl 라인 수 확인

```bash
wc -l verification/runs/facts/geo_v0_s1/round39_*/artifacts/skip_reasons.jsonl
```

**예상 결과**: 200 lines

### 4. PERIMETER_LARGE 경고 확인

```bash
# PERIMETER_LARGE 경고 확인
cat verification/runs/facts/geo_v0_s1/round39_*/KPI.md | grep -i "PERIMETER_LARGE"
cat verification/runs/facts/geo_v0_s1/round39_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); summary = data.get('summary', {}); circ_keys = ['WAIST_CIRC_M', 'BUST_CIRC_M', 'HIP_CIRC_M']; [print(f\"{k}: {summary.get(k, {}).get('warnings', {})}\") for k in circ_keys]"
```

**예상 결과**: 
- PERIMETER_LARGE 경고가 없거나, 있으면 debug_info의 `n_hull`/`fallback_reason` 근거를 PR에 기록

### 5. circ_debug에서 convex hull 정보 확인

```bash
# circ_debug에서 perimeter_method, n_hull, fallback_used 확인
cat verification/runs/facts/geo_v0_s1/round39_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); circ_debug = data.get('circ_debug', {}); [print(f\"{k}: method={v.get('perimeter_method', 'N/A')}, n_hull={v.get('n_points_hull', 'N/A')}, fallback={v.get('fallback_used', False)}\") for k, v in circ_debug.items()]"
```

**예상 결과**: 
- `perimeter_method`: "convex_hull_v1"
- `n_points_hull`: 숫자 (hull 점 수)
- `fallback_used`: false (또는 true인 경우 `fallback_reason` 기록)

### 6. postprocess 산출물 생성 확인

```bash
ls -la verification/runs/facts/geo_v0_s1/round39_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round39_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round39_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

## 준수 사항

- ✅ 상수 클램프 금지 (정답 맞추기 금지)
- ✅ Semantic/단위 재논의 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ PASS/FAIL 판정 금지 (사실만 기록)
- ✅ SciPy 사용 금지 (numpy-only)
- ✅ 라운드 완료는 postprocess 마감까지
- ✅ 기하학적 해결: 클램프 없이 convex hull로 내부/오목 점 제거
