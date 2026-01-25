# KPI Diff Contract v0

## Purpose

KPI_DIFF.md는 facts-only diff입니다.
판정 문구 없이 사실 비교만 수행합니다.

## File Location

- `<current_run_dir>/KPI_DIFF.md`

## Structure

KPI_DIFF.md는 반드시 2 섹션을 포함합니다:

1. **Diff vs Prev**
2. **Diff vs Baseline**

## Prev 결정 규칙

- `round_registry.json`의 해당 lane에서 `current round_num`보다 작은 round 중 가장 큰 round를 prev로 선택
- prev가 없으면 "Prev: N/A"로 표기하고 baseline 섹션만 생성

## Baseline 결정 규칙

- `round_registry.json`의 `lanes.<lane>.baseline.run_dir` 사용
- baseline이 없으면 baseline 섹션을 N/A로 표기

## 포함 항목 (최소)

각 diff 섹션은 다음을 포함합니다:

1. **Total cases**: current vs ref
2. **HEIGHT_M p50/p95**: current vs ref
3. **BUST/WAIST/HIP p50**: current vs ref (존재할 때만)
4. **NaN Rate Top5 변화**:
   - current top5와 ref top5를 각각 뽑고, 교집합/차집합을 표기
   - 예: "Common keys: 3", "New in current top5: KEY1, KEY2", "Dropped from top5: KEY3"
5. **Failure Reason Top5 변화**:
   - current top5와 ref top5를 각각 뽑고, 교집합/차집합을 표기
   - 예: "Common reasons: 2", "New in current top5: REASON1", "Dropped from top5: REASON2"

## 표현 규칙

- "사실 비교"만 표기:
  - 예: "+0.012m", "-3 keys", "moved rank", "new in top5"
- "좋아졌다/나빠졌다" 같은 판정 문구 금지
- "increased", "decreased", "same" 같은 상태 표기는 허용 (사실 기술)

## Notes

- 모든 값은 가능하면 상대 변화량(Δ)으로 표기
- N/A는 missing 데이터를 의미하며, 크래시 없이 처리
- ref 데이터가 없으면 해당 섹션은 "N/A"로 표기
