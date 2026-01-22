GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md

Geometric Layer — Design Specification

0. Scope & Authority

Layer: Geometric (Implementation Design)

Measurement: BUST / UNDERBUST

Semantic Anchor: 
- SEMANTIC_DEFINITION_BUST_VNEXT.md
- SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md

Contract Anchor: CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md

Non-Goals:

해부학적 추론 ❌

자동 보정 ❌

정확도 최적화 ❌

PASS/FAIL 판정 ❌

본 문서는 BUST/UNDERBUST를 계산 "어떻게 할 것인가"에 대한 최소 구현 설계다.
의미 판단은 절대 포함하지 않는다.

1. Design Principle (핵심 원칙)

BUST/UNDERBUST Geometric Layer v0는 다음 원칙을 따른다.

Circumference v0 패턴 최대 재사용

해부학적 추론 금지

기하학적 극값 탐색 금지 (UNDERBUST는 구조적 안정성, BUST는 볼륨 극값)

정의되지 않은 경우 NaN 반환 허용

자동 보정 금지 (Contract 위반)

즉,

"BUST/UNDERBUST를 '잘' 재는 것"이 아니라
"BUST/UNDERBUST를 Semantic/Contract 위반 없이 계산하는 가장 단순한 방법"

을 목표로 한다.

2. Input / Output (계약 재확인)

입력:

verts: float32[N,3] (meters)

measurement_key = "UNDERBUST" 또는 "BUST"

출력:

circumference_m: float | NaN

section_id: string

method_tag: string

warnings: list[string]

출력 필드는 Contract Layer와 1:1 대응해야 한다.

3. Geometric Strategy v0 (개념적)
3.1 Candidate Section Generation

기준 축: y-axis

방식:

Circumference v0와 동일하게

y축을 일정 간격으로 슬라이싱

각 slice에서 단면 후보 생성

이유:

구현 안정성 확보

재현성 보장

기존 Validation/Smoke 패턴 재사용 가능

3.2 UNDERBUST-specific Region Gating (최소 제약)

UNDERBUST v0는 하부 흉곽(thoracic cage) 영역에 대한 약한 제약만 적용한다.

허용 영역:

하부 흉곽 추정 범위 (상체 하단)

금지 영역:

복부 하단

명백한 하체 영역

⚠️ 주의

정확한 비율, landmark, skeleton 정보 사용 금지

이 단계에서는 "대략적인 하부 흉곽 범위"만 필요

이 gating은 의미를 보장하기 위함이 아니라
의미를 훼손할 가능성을 줄이기 위한 최소 안전장치다.

3.3 BUST-specific Region Gating (최소 제약)

BUST v0는 유방 볼륨 영역에 대한 약한 제약만 적용한다.

허용 영역:

상체 중상단 (유방 볼륨 추정 범위)

금지 영역:

복부 하단

명백한 하체 영역

⚠️ 주의

정확한 비율, landmark, skeleton 정보 사용 금지

이 단계에서는 "대략적인 유방 볼륨 범위"만 필요

이 gating은 의미를 보장하기 위함이 아니라
의미를 훼손할 가능성을 줄이기 위한 최소 안전장치다.

3.4 Section Selection Rule (v0)

UNDERBUST v0:

선택 규칙:

허용 영역 내에서

중앙값(median)에 가장 가까운 단면

금지:

max (BUST 혼동 위험)

min (WAIST 혼동 위험)

의미:

극값을 피함으로써

UNDERBUST의 "구조적 안정성"만 확보

BUST v0:

선택 규칙:

허용 영역 내에서

최대값(max)에 가장 가까운 단면

금지:

median (UNDERBUST 혼동 위험)

의미:

볼륨 극값을 선택함으로써

BUST의 "볼륨 특성"만 확보

⚠️ TBD: 실제 단면 선택 알고리즘은 구현 단계에서 명시적으로 정의됨

4. Circumference Computation

선택된 단면에서:

폐곡선 여부 검사

폐곡선 성립 시 길이 계산

불성립 시 NaN

계산 방식 자체는 Circumference v0와 동일

5. Warning Policy (Geometric 관점)

Geometry는 판단하지 않고 신호만 남긴다.

허용 Warning

DEGEN_FAIL

단면 후보 부족

REGION_AMBIGUOUS

허용 영역 내 후보가 다수 존재

UNIT_FAIL

수치 스케일 이상 감지 시

LARGE_BUST_UNDERBUST_DELTA

남성 케이스에서 큰 Δ 감지 시 (Contract 위반 아님, 신호만)

INPUT_CONTRACT_FAIL

입력 계약 위반 (형식/타입/범위)

MEASUREMENT_KEY_MISMATCH

measurement_key 불일치

Warning은:

결과를 차단하지 않음

Judgment Layer로 전달됨

6. section_id & method_tag 규칙
section_id

포함 정보 (초안):

axis (y)

slice_index

region_gate (underbust_region 또는 bust_region)

measurement_key (UNDERBUST 또는 BUST)

JSON 직렬화 문자열 권장

⚠️ TBD: 실제 형식은 구현 단계에서 artifacts.extra_json에 저장될 형식으로 명시적으로 정의됨

method_tag

초안 값:

underbust_v0_y_slice_median

bust_v0_y_slice_max

⚠️ TBD: 실제 태그는 구현 단계에서 명시적으로 정의됨

7. Failure Handling

상황	처리
후보 단면 없음	NaN + DEGEN_FAIL
폐곡선 불성립	NaN
입력 오류	NaN + warnings["INPUT_CONTRACT_FAIL"] (예외 금지)
measurement_key 불일치	NaN + warnings["MEASUREMENT_KEY_MISMATCH"] (예외 금지)

NaN은 정상 결과다.

8. Geometric Boundary Statement

본 Geometric Layer는 다음을 의도적으로 하지 않는다.

해부학적 landmark 추론

Skeleton / pose 활용

최적화 기반 탐색

자동 보정 (Contract 위반)

9. Status

BUST/UNDERBUST Geometric Layer v0: 설계 완료

다음 단계: Validation Layer v0 (BUST/UNDERBUST)
