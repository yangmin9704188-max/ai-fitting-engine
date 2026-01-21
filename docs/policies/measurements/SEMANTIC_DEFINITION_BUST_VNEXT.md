아래는 BUST Measurement의 Semantic Definition vNext 초안입니다. (구현·계약·검증·판정 제외)

SEMANTIC_DEFINITION_BUST_VNEXT.md

Semantic Layer — Final Draft (vNext)

0. Scope & Authority

Layer: Semantic (Definition)

Measurement: BUST (Breast Volume Maximum Circumference)

Relation: Chest Family (Sibling of UNDERBUST, Volume counterpart)

Non-Goals:

계산 로직 ❌

단면 선택 알고리즘 ❌

임계값/판정 ❌

본 문서는 BUST가 무엇을 의미하는지를 정의한다.
이후 Layer는 이 정의를 전제로만 동작한다.

1. Core Semantic Statement

BUST는 상체(Upper Torso) 영역에서,
유방(breast) 볼륨의 최대 돌출 지점을 포함하는
볼륨 기반(Volume-based) 둘레 측정이다.

즉, BUST는 의복 사이즈 및 피팅에 유의미한 유방 볼륨의 최대 둘레를 의미하며,
구조적 흉곽 둘레(UNDERBUST)와 의도적으로 구분된다.

2. Distinction from UNDERBUST (의도적 분리)

UNDERBUST: 하부 흉곽 구조 중심 둘레(bone-structure dominant, structural-based)

BUST: 유방 볼륨의 최대 둘레(soft-tissue dominant, volume-based)

BUST는 "구조적 둘레"가 아니다.
BUST는 "볼륨 극값 둘레"다.

이 분리는:

해부학적 의미 혼합을 방지하고

의복 피팅 및 사이즈 선택의 정확도를 높이기 위함이다.

3. Defined Region (의미론적 영역)

BUST는 다음 의미론적 영역에서만 정의된다.

상체 영역(Upper Torso) 내

유방 볼륨이 존재하는 영역

복부/허리 영역 포함 금지

정확한 y-좌표, 비율, 해부학적 landmark는
Semantic Layer에서 의도적으로 고정하지 않는다.

이는 Geometry Layer에서 다양한 구현을 허용하기 위함이다.

4. Undefined Semantics (NaN = Undefined)

BUST는 다음 경우 정의되지 않음(Undefined) 으로 간주한다.

유방 볼륨에 해당하는 폐곡선 단면이 형성되지 않는 경우

상체 영역에서 의미 있는 단면 후보가 존재하지 않는 경우

입력 형상이 유방 볼륨을 표현하기에 불충분한 경우

NaN은 실패가 아니라, BUST가 성립하지 않는다는 의미론적 표현이다.

5. Unit Assumption

BUST의 의미론은 입력 좌표가 meters 단위임을 전제로 한다.

단위 위반 시 결과는 의미론적으로 해석 불가

보정·추론 책임은 Semantic/Contract Layer에 귀속

6. Male-Specific Interpretation (해석 전제, 보정 아님)

남성의 경우, Δ = (BUST - UNDERBUST) ≈ 0을 기대할 수 있다.

이는 자동 보정의 근거가 아니라, 해석 전제(interpretation premise)로만 사용된다.

큰 Δ(예: Δ > 5cm)는:

자동 보정 금지

자동 정상화 금지

Warning 기록만 수행 (예: "LARGE_BUST_UNDERBUST_DELTA")

해석 책임은 Judgment Layer에 귀속

7. Bra Size Input Integration (의도만, 파싱/계산식은 L2)

BUST 측정은 브라 사이즈 입력(예: "75A")과 연동될 수 있다.

이는 Semantic Layer에서 "의도"만 명시한다.

구체적 파싱 규칙, 계산식, 범위 검증은 Contract Layer(L2)에서 정의된다.

8. Semantic Boundary Statement

본 Semantic Definition은 다음을 의도적으로 포함하지 않는다.

유방 볼륨 위치 추정 방식

단면 선택 기준

브라 사이즈 파싱 알고리즘

검증 기준 및 임계값

Semantic Layer는 오직 다음 질문에만 답한다.

"BUST란 무엇을 측정한다고 말하는가?"

9. Status

BUST Semantic Definition vNext: Draft (검토 대상)

다음 단계: Contract Layer v0 (BUST/UNDERBUST)
