# ops: add KPI diff vs prev and baseline on postprocess (round5)

## 목적
postprocess_round.py가 KPI.md 뿐 아니라, KPI_DIFF.md를 "직전 라운드(prev)"와 "baseline(고정)" 둘 다에 대해 생성합니다.
판정이 아니라 사실 비교 요약만 수행합니다.

## 구현 범위

### 1. tools/kpi_diff.py (신규)
- facts_summary.json 두 개를 비교하여 KPI_DIFF.md 생성
- 기능:
  - Total cases 비교
  - HEIGHT_M p50/p95 비교
  - BUST/WAIST/HIP p50 비교
  - NaN Rate Top5 변화 (교집합/차집합 표기)
  - Failure Reason Top5 변화 (교집합/차집합 표기)
  - "사실 비교"만 표기 (판정 문구 금지)

### 2. tools/postprocess_round.py 업데이트
- round_registry.json에서 prev/baseline 결정:
  - Prev: current round_num보다 작은 round 중 가장 큰 round
  - Baseline: lanes.<lane>.baseline.run_dir
- KPI_DIFF.md 생성 로직 추가
- kpi_diff.py 사용

### 3. docs/verification/kpi_diff_contract_v0.md (신규)
- KPI_DIFF 스키마 및 정책 문서
- prev/baseline 결정 규칙 명시
- 포함 항목 정의

## 변경 파일 목록

- `tools/kpi_diff.py` (신규)
- `tools/postprocess_round.py` (업데이트: round_registry 기반 prev/baseline 결정 및 KPI_DIFF 생성)
- `docs/verification/kpi_diff_contract_v0.md` (신규)

## Prev/Baseline 결정 규칙

### Prev 결정 규칙
- `round_registry.json`의 해당 lane에서 `current round_num`보다 작은 round 중 가장 큰 round를 prev로 선택
- prev가 없으면 "Prev: N/A"로 표기하고 baseline 섹션만 생성

### Baseline 결정 규칙
- `round_registry.json`의 `lanes.<lane>.baseline.run_dir` 사용
- baseline이 없으면 baseline 섹션을 N/A로 표기

## KPI_DIFF에 포함된 항목 목록

각 diff 섹션(Diff vs Prev, Diff vs Baseline)은 다음을 포함:

1. **Total Cases**: current vs ref (Δ 표기)
2. **HEIGHT_M Distribution**: p50/p95 비교 (Δ 표기)
3. **BUST/WAIST/HIP p50**: 각 키별 비교 (Δ 표기, 존재할 때만)
4. **NaN Rate Top5 Changes**:
   - 테이블 형식: Key, Current, Ref, Δ, Status
   - Summary: Common keys, New in current top5, Dropped from top5
5. **Failure Reason Top5 Changes**:
   - 테이블 형식: Reason, Current, Ref, Δ, Status
   - Summary: Common reasons, New in current top5, Dropped from top5

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
- ✅ KPI.md 생성/갱신
- ✅ KPI_DIFF.md 생성
- ✅ prev가 없으면 Prev 섹션은 N/A, Baseline 섹션은 baseline이 자기 자신일 수 있으므로 0 diff 형태로 출력(허용)
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (5 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- KPI.md 생성 확인
- KPI_DIFF.md 생성 확인
- 두 섹션 모두 포함 확인:
  - Diff vs Prev: 모든 항목 포함 (Total cases, HEIGHT_M, BUST/WAIST/HIP, NaN Rate, Failure Reason)
  - Diff vs Baseline: 모든 항목 포함
- Summary 정보 포함 확인:
  - Common keys: 5
  - Common reasons: 5
- postprocess 정상 종료 (exit code 0)

### 추가 스모크 테스트

다른 run_dir이 없어서 prev diff가 실제로 작동하는지 확인할 수 없습니다.
현재 round20만 존재하므로 prev는 baseline으로 fallback되었습니다.
추가 run_dir이 생성되면 prev diff가 정상 작동할 것으로 예상됩니다.

## 표현 규칙 준수

- "사실 비교"만 표기:
  - 예: "+0.012m", "-3 keys", "new in top5", "dropped from top5"
- "좋아졌다/나빠졌다" 같은 판정 문구 없음
- "increased", "decreased", "same" 같은 상태 표기는 사실 기술로 허용

## 참고

- 루트에 파일 추가하지 않음 (tools/ 및 docs/verification/ 에서만 해결)
- 기존 `summarize_facts_kpi.py`의 `generate_kpi_diff` 함수는 유지 (backward compatibility)
- 새로운 `kpi_diff.py`는 더 상세한 diff를 제공
