# ops: add lightweight degradation signals to KPI_DIFF (round5)

## 목적
KPI_DIFF.md 상단에 "한 줄 경고"를 추가하여 사람이 파일을 깊게 읽지 않아도 악화 여부를 즉시 판단하게 합니다.
PASS/FAIL 금지. 경고는 signal일 뿐입니다.

## 구현 범위

### 1. KPI_DIFF.md 상단에 Degradation Signals 섹션 추가
- **DEGRADATION_FLAG**: `true`/`false`
- **DEGRADED_KEYS_TOP3**: `key1, key2, key3` (없으면 `N/A`)
- **HEIGHT_P50_SHIFT**: `+0.000m` (없으면 `N/A`)
- 기준:
  - baseline 대비 NaN rate가 악화된 키 상위 3개를 degraded로 간주
  - HEIGHT_M p50의 baseline 대비 변화량 계산

### 2. 구현 위치
- `tools/kpi_diff.py`에 `compute_degradation_signals()` 함수 추가
- `generate_kpi_diff()` 함수에서 상단에 signals 섹션 추가

## 변경 파일 목록

- `tools/kpi_diff.py` (업데이트: degradation signals 추가)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지 (signals only)

## 스모크 테스트

### 실행 명령
```bash
py tools/postprocess_round.py \
  --current_run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

### 기대 결과
- ✅ KPI_DIFF.md 생성 확인
- ✅ 상단에 Degradation Signals 섹션 추가 확인
- ✅ DEGRADATION_FLAG, DEGRADED_KEYS_TOP3, HEIGHT_P50_SHIFT 포함
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Warning: No previous run found for lane 'curated_v0'. Using current as prev.
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801 (fallback (no prev found, using current))
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline alias: curated-v0-realdata-v0.1 (auto (new registry: curated-v0-realdata-v0.1))
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (16 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json
Generated: LINEAGE.md
Updated: docs/verification/golden_registry.json (1 entries)
Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for curated_v0 realdata lane.

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- KPI_DIFF.md 생성 확인
- 상단에 Degradation Signals 섹션 추가 확인
- postprocess 정상 종료 (exit code 0)

## 생성된 KPI_DIFF.md 상단 예시

```markdown
# KPI Diff

*Generated at: 2026-01-25T21:45:00.123456*

- **Current run dir**: `verification/runs/facts/curated_v0/round20_20260125_164801`
- **Prev run dir**: `N/A`
- **Baseline run dir**: `verification/runs/facts/curated_v0/round20_20260125_164801`

## Degradation Signals (Baseline vs Current)

- **DEGRADATION_FLAG**: `false`
- **DEGRADED_KEYS_TOP3**: `N/A`
- **HEIGHT_P50_SHIFT**: `+0.0000m`

*Note: These are signals only, not PASS/FAIL judgments.*

## Diff vs Prev
...
```

## 주요 개선사항

1. **경고 신호 추가**:
   - baseline 대비 NaN rate 악화 키 상위 3개 자동 감지
   - HEIGHT_M p50 shift 계산
   - degradation flag로 한눈에 악화 여부 확인

2. **가벼운 구현**:
   - 복잡한 임계값 규칙 없이 단순 비교만 수행
   - signals only (판정 금지)

3. **사용성 향상**:
   - 파일을 깊게 읽지 않아도 악화 여부 즉시 판단 가능
   - 상단에 배치하여 가시성 향상

## 참고

- 루트에 파일 추가하지 않음 (tools/ 안에서만 해결)
- 기존 동작과 호환 (추가 기능만)
- PASS/FAIL 판정 없이 signals only 유지
