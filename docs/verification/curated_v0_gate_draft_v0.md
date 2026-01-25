# curated_v0 Gate Draft v0

**목적**: PASS/FAIL이 아니라 "facts 신호 → 다음 행동" 맵핑 초안을 정의합니다.

## Soft validity ranges (센서용, 판정 아님)

측정값의 합리적 범위를 정의합니다. 이는 경고용 센서이며, 자동 판정에는 사용하지 않습니다.

- HEIGHT_M: [placeholder_min, placeholder_max] m
- BUST_CIRC_M: [placeholder_min, placeholder_max] m
- WAIST_CIRC_M: [placeholder_min, placeholder_max] m
- HIP_CIRC_M: [placeholder_min, placeholder_max] m

**주의**: 이 범위는 "의심 신호"만 제공하며, 자동 FAIL 판정에는 사용하지 않습니다.

## Missing policy (all-null은 coverage backlog로만)

모든 키가 null인 경우는 coverage backlog로만 기록합니다. 자동 실패 처리하지 않습니다.

- all-null 케이스는 `coverage_backlog`에 기록
- 측정 로직 수정 대상으로 분류하지 않음

## Suspicious scale triggers (10x/100x 패턴 등)

스케일 오류 의심 패턴을 감지합니다.

- 10x 패턴: 측정값이 예상 범위의 10배
- 100x 패턴: 측정값이 예상 범위의 100배
- 단위 오류 의심 시 `unit_investigation` 태그 부여

## Action mapping table

facts 신호에 따른 다음 행동을 정의합니다.

| 신호 패턴 | 다음 행동 |
|---------|---------|
| NaN>80% & reason=EMPTY_SLICE | slicer instrumentation 먼저 |
| NaN>50% & reason=UNIT_FAIL | 단위 검증 로직 점검 |
| Suspicious scale (10x/100x) | 단위 메타데이터 검증 |
| all-null 케이스 | coverage backlog 기록만 |

## How to use KPI summarizer

facts_summary.json에서 KPI 헤더를 생성합니다:

```bash
py tools/summarize_facts_kpi.py \
  verification/runs/facts/.../facts_summary.json \
  > KPI.md
```

bash 줄바꿈 컨벤션 예시:
```bash
py tools/summarize_facts_kpi.py \
  verification/runs/facts/curated_v0/round20_20260125_120000/facts_summary.json \
  > KPI.md
```
