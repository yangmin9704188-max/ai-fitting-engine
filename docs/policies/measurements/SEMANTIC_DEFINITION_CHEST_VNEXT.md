아래는 CHEST Measurement의 Semantic Definition vNext 초안입니다. (구현·계약·검증·판정 제외)

**⚠️ Deprecated**: CHEST 단일 정의는 Deprecated이며, 표준 가슴 계열 측정은 UNDERBUST/BUST 이원화로 전환되었습니다. 신규 구현은 SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md 및 SEMANTIC_DEFINITION_BUST_VNEXT.md를 참조하세요.

**CHEST v0 meaning**: CHEST v0 was defined as "Upper Torso Circumference, Non-bust" (흉곽 기반 둘레, 유방 볼륨 배제). The semantic intent was closer to UNDERBUST (structural) than BUST (volume), but the distinction was not explicitly codified.

**Relation to new standard**: No direct inheritance. CHEST v0 meaning is ambiguous in legacy context; treat as reference-only. New implementations must use UNDERBUST/BUST binary system.

SEMANTIC_DEFINITION_CHEST_VNEXT.md

Semantic Layer — Final Draft (vNext)

0. Scope & Authority

Layer: Semantic (Definition)

Measurement: CHEST (Upper Torso Circumference, Non-bust)

Relation: Circumference Family (Sibling of BUST/WAIST/HIP)

Non-Goals:

계산 로직 ❌

단면 선택 알고리즘 ❌

임계값/판정 ❌

본 문서는 CHEST가 무엇을 의미하는지를 정의한다.
이후 Layer는 이 정의를 전제로만 동작한다.

1. Core Semantic Statement

CHEST는 상체(Upper Torso) 영역에서,
유방(bust) 볼륨의 국소적 극값에 의존하지 않는
흉곽(thoracic cage) 기반 둘레 측정이다.

즉, CHEST는 의복 사이즈 및 구조 설계에 유의미한 흉곽 둘레를 의미하며,
성별·체형에 따라 크게 변하는 bust 극값을 의도적으로 배제한다.

2. Distinction from BUST (의도적 분리)

BUST: 유방 볼륨의 최대 둘레(soft-tissue dominant)

CHEST: 흉곽 구조 중심 둘레(bone-structure dominant)

CHEST는 “가장 큰 둘레”가 아니다.
CHEST는 “의미적으로 안정적인 흉곽 둘레”다.

이 분리는:

해부학적 의미 혼합을 방지하고

기하학적 극값 탐색의 부작용을 줄이기 위함이다.

3. Defined Region (의미론적 영역)

CHEST는 다음 의미론적 영역에서만 정의된다.

상체 영역(Upper Torso) 내

어깨 하부 ~ 유방 상부 사이

복부/허리 영역 포함 금지

정확한 y-좌표, 비율, 해부학적 landmark는
Semantic Layer에서 의도적으로 고정하지 않는다.

이는 Geometry Layer에서 다양한 구현을 허용하기 위함이다.

4. Undefined Semantics (NaN = Undefined)

CHEST는 다음 경우 정의되지 않음(Undefined) 으로 간주한다.

흉곽에 해당하는 폐곡선 단면이 형성되지 않는 경우

상체 영역에서 의미 있는 단면 후보가 존재하지 않는 경우

입력 형상이 흉곽 구조를 표현하기에 불충분한 경우

NaN은 실패가 아니라, CHEST가 성립하지 않는다는 의미론적 표현이다.

5. Unit Assumption

CHEST의 의미론은 입력 좌표가 meters 단위임을 전제로 한다.

단위 위반 시 결과는 의미론적으로 해석 불가

보정·추론 책임은 Semantic/Contract Layer에 귀속

6. Semantic Boundary Statement

본 Semantic Definition은 다음을 의도적으로 포함하지 않는다.

흉곽 위치 추정 방식

단면 선택 기준

bust 제거 알고리즘

검증 기준 및 임계값

Semantic Layer는 오직 다음 질문에만 답한다.

“CHEST란 무엇을 측정한다고 말하는가?”

7. Status

CHEST Semantic Definition vNext: Draft (검토 대상)

다음 단계: Contract Layer v0 (CHEST)