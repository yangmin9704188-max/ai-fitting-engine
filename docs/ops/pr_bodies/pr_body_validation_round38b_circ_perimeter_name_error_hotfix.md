# PR: Round38b HOTFIX - Circumference Perimeter NameError 수정

## 목적

Round38에서 모든 CIRC가 NaN 처리되었고, facts_summary.json에 `"EXEC_FAIL: name 'perimeter' is not defined"`가 기록되었습니다.

이는 알고리즘 문제가 아니라 **런타임 변수명/스코프 버그**입니다. 다양성/로더/성능은 이미 통과했으므로, 이번 라운드는 최소 수정으로 버그만 제거합니다.

## 버그 원인

**파일**: `core/measurements/core_measurements_v0.py`

**위치**: `_compute_perimeter` 함수 (207번 라인)

**문제**: 
- `return_debug=True`일 때는 `perimeter_final` 변수를 사용하여 반환
- `return_debug=False`일 때는 `return float(perimeter)`를 호출하지만, `perimeter` 변수가 정의되지 않음
- `perimeter_final`은 정의되어 있지만, `return_debug=False` 경로에서 사용되지 않음

## 변경 사항

### `core/measurements/core_measurements_v0.py`

**수정 내용**:
- 207번 라인: `return float(perimeter)` → `return float(perimeter_final)`
- 변수명 단일화: `perimeter_final`을 일관되게 사용

**최소 수정 원칙 준수**:
- 알고리즘 변경 없음
- 변수명만 수정
- 기존 로직 유지

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round38b_$(date +%Y%m%d_%H%M%S)" && \
python verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
python tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. KPI.md에서 둘레 값 확인

```bash
# BUST_CIRC_M, WAIST_CIRC_M, HIP_CIRC_M p50/p95 확인
cat verification/runs/facts/geo_v0_s1/round38b_*/KPI.md | grep -E "(BUST_CIRC_M|WAIST_CIRC_M|HIP_CIRC_M)" | grep -E "(p50|p95|median|mean)"
```

**예상 결과**: 
- p50/p95가 N/A가 아님
- 둘레 값이 정상 범위 (예: 0.5m ~ 2.0m)

### 2. facts_summary.json에서 NameError 재발 확인

```bash
# "name 'perimeter' is not defined" 재발 여부 확인
cat verification/runs/facts/geo_v0_s1/round38b_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); summary = data.get('summary', {}); circ_keys = ['WAIST_CIRC_M', 'BUST_CIRC_M', 'HIP_CIRC_M']; errors = []; [errors.extend([f'{k}: {w}' for w in summary.get(k, {}).get('warnings', {}).keys() if 'perimeter' in w.lower() or 'name' in w.lower()]) for k in circ_keys]; print('\\n'.join(errors) if errors else 'No perimeter name errors found')"
```

**예상 결과**: 
- "name 'perimeter' is not defined" 재발하지 않음
- EXEC_FAIL 경고가 없거나, 있다면 다른 원인

### 3. skip_reasons.jsonl 라인 수 확인

```bash
wc -l verification/runs/facts/geo_v0_s1/round38b_*/artifacts/skip_reasons.jsonl
```

**예상 결과**: 200 lines

### 4. postprocess 산출물 생성 확인

```bash
ls -la verification/runs/facts/geo_v0_s1/round38b_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round38b_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round38b_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

## 준수 사항

- ✅ 정답 튜닝(클램프/상한) 금지
- ✅ Semantic/단위 재논의 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ 라운드 완료는 postprocess 마감까지
- ✅ 최소 수정 원칙: 변수명만 수정, 알고리즘 변경 없음
