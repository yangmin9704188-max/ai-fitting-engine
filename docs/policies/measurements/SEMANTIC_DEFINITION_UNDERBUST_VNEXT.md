아래는 UNDERBUST Measurement의 Semantic Definition vNext 초안입니다. (구현·계약·검증·판정 제외)

SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md

Semantic Layer — Final Draft (vNext)

0. Scope & Authority

Layer: Semantic (Definition)

Measurement: UNDERBUST (Lower Chest Circumference, Structural)

Relation: Chest Family (Sibling of BUST, Structural counterpart)

Non-Goals:

계산 로직 ❌

단면 선택 알고리즘 ❌

임계값/판정 ❌

본 문서는 UNDERBUST가 무엇을 의미하는지를 정의한다.
이후 Layer는 이 정의를 전제로만 동작한다.

1. Core Semantic Statement

UNDERBUST는 하부 흉곽(Lower Thoracic Cage) 영역에서,
유방(bust) 볼륨의 국소적 극값에 의존하지 않는
구조적(Structural) 기반 둘레 측정이다.

즉, UNDERBUST는 의복 사이즈 및 구조 설계에 유의미한 하부 흉곽 둘레를 의미하며,
성별·체형에 따라 크게 변하는 bust 극값을 의도적으로 배제한다.

2. Distinction from BUST (의도적 분리)

BUST: 유방 볼륨의 최대 둘레(soft-tissue dominant, volume-based)

UNDERBUST: 하부 흉곽 구조 중심 둘레(bone-structure dominant, structural-based)

UNDERBUST는 "가장 큰 둘레"가 아니다.
UNDERBUST는 "의미적으로 안정적인 하부 흉곽 둘레"다.

이 분리는:

해부학적 의미 혼합을 방지하고

기하학적 극값 탐색의 부작용을 줄이기 위함이다.

3. Defined Region (의미론적 영역)

UNDERBUST는 다음 의미론적 영역에서만 정의된다.

하부 흉곽 영역(Lower Thoracic Cage) 내

유방 하부 ~ 복부 상부 사이

복부/허리 영역 포함 금지

정확한 y-좌표, 비율, 해부학적 landmark는
Semantic Layer에서 의도적으로 고정하지 않는다.

이는 Geometry Layer에서 다양한 구현을 허용하기 위함이다.

4. Undefined Semantics (NaN = Undefined)

UNDERBUST는 다음 경우 정의되지 않음(Undefined) 으로 간주한다.

하부 흉곽에 해당하는 폐곡선 단면이 형성되지 않는 경우

하부 흉곽 영역에서 의미 있는 단면 후보가 존재하지 않는 경우

입력 형상이 하부 흉곽 구조를 표현하기에 불충분한 경우

NaN은 실패가 아니라, UNDERBUST가 성립하지 않는다는 의미론적 표현이다.

5. Unit Assumption

UNDERBUST의 의미론은 입력 좌표가 meters 단위임을 전제로 한다.

단위 위반 시 결과는 의미론적으로 해석 불가

보정·추론 책임은 Semantic/Contract Layer에 귀속

6. Male-Specific Interpretation (해석 전제, 보정 아님)

남성의 경우, Δ = (BUST - UNDERBUST) ≈ 0을 기대할 수 있다.

이는 자동 보정의 근거가 아니라, 해석 전제(interpretation premise)로만 사용된다.

큰 Δ(예: Δ > 5cm)는:

자동 보정 금지

Warning 기록만 수행 (예: "LARGE_BUST_UNDERBUST_DELTA")

해석 책임은 Judgment Layer에 귀속

7. Semantic Boundary Statement

본 Semantic Definition은 다음을 의도적으로 포함하지 않는다.

하부 흉곽 위치 추정 방식

단면 선택 기준

bust 제거 알고리즘

검증 기준 및 임계값

Semantic Layer는 오직 다음 질문에만 답한다.

"UNDERBUST란 무엇을 측정한다고 말하는가?"

8. Status

UNDERBUST Semantic Definition vNext: Draft (검토 대상)

다음 단계: Contract Layer v0 (UNDERBUST)
