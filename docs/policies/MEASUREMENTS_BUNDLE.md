CONTRACT_INTERFACE_CHEST_V0.md

Contract Layer — Interface Definition

0. Scope & Authority

Layer: Contract (Interface)

Measurement: CHEST (Upper Torso Circumference, Non-bust)

Semantic Anchor: SEMANTIC_DEFINITION_CHEST_VNEXT.md

Applies To:

chest_v0 (초기 구현)

CHEST 계열 이후 버전

본 문서는 CHEST의 의미론을 코드 인터페이스로 봉인한다.
계산 방법, 단면 선택, 검증 기준, 판단 로직은 포함하지 않는다.

1. Contract Role Statement

Contract Layer의 역할은 다음 하나다.

Semantic Definition에서 규정한 CHEST의 의미가
코드 입·출력에서 어떻게 표현되어야 하는지를 명시한다.

Contract는:

의미를 해석하지 않는다 (Judgment 아님)

계산을 설명하지 않는다 (Geometric 아님)

결과를 평가하지 않는다 (Validation 아님)

2. Input Contract (입력 계약)
2.1 Required Inputs
항목	타입	의미
verts	float32[N, 3]	3D 인체 메시 정점 좌표
measurement_key	Enum	CHEST

measurement_key는 CHEST 단일 값만 허용된다.

2.2 Unit Assumption (필수 전제)

입력 좌표는 meters 단위여야 한다.

단위는 검증 대상이 아니라 계약 전제다.

위반 시:

Geometry는 단위 추론·보정을 수행하지 않는다

반환 결과는 의미론적으로 해석 불가가 될 수 있다

단위 위반은:

❌ Geometry Error 아님

❌ Validation Fail 아님

✅ Semantic / Contract 위반

3. Output Contract (출력 계약)
3.1 Primary Output Fields
필드	타입	의미
circumference_m	float | NaN	CHEST 둘레 (meters) 또는 Undefined
section_id	string	선택된 단면 식별자
method_tag	string	측정 방법 식별 태그
warnings	list[string]	주의 신호 목록
4. Undefined vs Error vs Warning (핵심 계약)
4.1 Undefined (NaN)

NaN은 Error가 아니다.

NaN은 다음을 의미한다.

CHEST 측정이 정의되지 않음

흉곽 기반 폐곡선 단면이 성립하지 않음

Geometry가 의미 없는 수치를 반환하지 않기로 선택함

NaN 반환이 허용되는 대표적 경우

상체 영역에서 흉곽에 해당하는 단면 후보가 존재하지 않는 경우

흉곽 구조를 표현하기에 입력 형상이 불충분한 경우

→ 이는 Semantic Definition의 경계 표현이다.

4.2 Error (Exception)

Error는 계약 또는 시스템 위반을 의미한다.

상황	처리
verts shape 불일치	Exception 허용
필수 입력 누락	Exception 허용
내부 계산 불가능 상태	Exception 허용

Error는:

질문이 잘못되었거나

시스템이 계산을 수행할 수 없음을 의미한다.

4.3 Warning

Warning은 결과를 부정하지 않는다.

Warning은:

결과는 반환되었으나

해석 시 주의가 필요함을 의미한다.

대표적 Warning 예

UNIT_FAIL

DEGEN_FAIL

REGION_AMBIGUOUS

Warning은:

결과 사용을 차단하지 않는다

Judgment Layer의 해석 입력으로 사용된다

5. section_id Contract
5.1 성격

section_id는 내부 디버그 값이 아니라
재현성을 보장하기 위한 계약 식별자다.

5.2 요구사항

동일 입력 → 동일 section_id

단면 선택 기준을 식별할 수 있어야 함

문자열 형식(JSON 직렬화 허용)

6. Geometry Layer: Allowed & Forbidden
6.1 Geometry가 허용받는 행위

NaN 반환

Warning 추가

내부 계산 방식 변경 (계약 유지 조건 하)

6.2 Geometry가 금지되는 행위

bust 볼륨을 추론·보정하려는 시도

단위 자동 보정

Undefined를 Error로 승격

Warning 은닉

의미론적 판단 수행

7. Contract Stability Declaration

본 문서는 CHEST Contract v0로 봉인된다.

Semantic Definition이 변경되지 않는 한:

Contract는 유지된다

Geometry 구현 변경은 허용된다

8. Boundary Statement

본 문서는 다음을 의도적으로 포함하지 않는다.

단면 생성 알고리즘

흉곽 위치 추정 방식

Validation 메트릭

품질 판정 기준

Contract는 오직 다음 질문에만 답한다.

“CHEST의 의미가 코드 인터페이스에서 어떻게 나타나야 하는가?”

9. Status Declaration

CHEST Contract Layer v0: Draft 완료

다음 단계: Geometric Layer v0 (CHEST)아래는 Semantic vNext를 정확히 반영하여 최초로 봉인하는 Contract Layer 정식 문서입니다.
이 문서는 새 규칙을 만들지 않고, 지금까지 암묵적으로 지켜온 계약을 인터페이스 수준에서 명문화합니다.

CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md

Contract Layer — Interface Definition

0. Scope & Authority

Layer: Contract (Interface)

Measurement Family: Circumference

Semantic Anchor: SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md

Applies To:

circumference_v0 (current)

이후 Circumference 계열 측정 전반

본 문서는 Semantic Definition을 기계적으로 전달하는 계약 문서다.
계산 방법, 검증 기준, 판단 로직은 포함하지 않는다.

1. Contract Role Statement

Contract Layer의 역할은 다음 하나다.

“Semantic Definition이 코드 인터페이스에서
어떻게 표현되어야 하는가를 명확히 규정한다.”

따라서 Contract는:

의미를 해석하지 않는다 (Judgment 아님)

계산을 설명하지 않는다 (Geometric 아님)

결과를 평가하지 않는다 (Validation 아님)

2. Input Contract (입력 계약)
2.1 Required Inputs
항목	타입	의미
verts	float32[N, 3]	3D 인체 메시 정점 좌표
measurement_key	Enum	BUST, WAIST, HIP 중 하나
2.2 Unit Assumption (필수 전제)

모든 좌표는 meters 단위여야 한다.

이 전제는 검증 대상이 아니라 계약 전제다.

위반 시:

Geometry는 보정하지 않는다

결과는 의미론적으로 해석 불가가 될 수 있다

단위 오류는:

❌ Geometry Error 아님

❌ Validation Fail 아님

✅ Contract Violation (Semantic 수준)

3. Output Contract (출력 계약)
3.1 Primary Output
필드	타입	의미
circumference_m	float | NaN	둘레 값 (meters) 또는 Undefined
section_id	string	측정에 사용된 단면 식별자
method_tag	string	측정 방법 식별 태그
warnings	list[string]	주의 신호 목록
4. Undefined vs Error vs Warning (핵심 계약)
4.1 Undefined (NaN)

NaN은 Error가 아니다.

NaN은 다음 의미를 가진다.

측정 대상이 정의되지 않음

질문 자체가 성립하지 않음

Geometry가 침묵을 선택한 결과

NaN 반환이 허용되는 대표적 경우

유효한 폐곡선 단면이 형성되지 않는 경우

후보 단면이 정의 영역 밖에만 존재하는 경우

→ 이는 Semantic Definition의 경계 표현이다.

4.2 Error (Exception)

Error는 계약 위반 또는 시스템 실패를 의미한다.

Error가 허용되는 경우는 매우 제한적이다.

상황	처리
verts shape 불일치	Exception 허용
필수 입력 누락	Exception 허용
내부 연산 불가능 상태	Exception 허용

Error는:

“질문이 잘못되었다” 또는

“시스템이 계산할 수 없다”를 의미한다.

4.3 Warning

Warning은 결과를 부정하지 않는다.

Warning은 다음을 의미한다.

결과는 반환되었으나

해석 시 주의가 필요함

대표적 Warning 예

UNIT_FAIL

DEGEN_FAIL

NUMERIC_INSTABILITY

Warning은:

결과 해석을 막지 않는다

Judgment Layer의 입력 신호가 된다

5. section_id 계약
5.1 성격 정의

section_id는 구현 내부 디버그 값이 아니라
계약의 일부인 재현 식별자다.

5.2 계약 요구사항

동일 입력 → 동일 section_id

section_id는 재현 가능해야 한다

포맷은 문자열(JSON 직렬화 허용)

6. Geometry Layer의 자유와 금지
6.1 Geometry가 자유롭게 할 수 있는 것

NaN 반환

Warning 추가

내부 계산 방식 변경 (계약 유지 조건 하)

6.2 Geometry가 해서는 안 되는 것

단위 추론 또는 자동 보정

Undefined를 Error로 승격

Warning을 숨김

의미론적 판단 수행

7. Contract Stability Declaration

본 Contract는 v0로 봉인된다.

Semantic Definition이 변경되지 않는 한:

Contract는 유지된다

Geometry 변경은 허용된다

8. Boundary Statement

본 문서는 다음을 의도적으로 포함하지 않는다.

계산 알고리즘

단면 선택 규칙

Validation 메트릭

품질 판정 기준

Contract는 오직 다음 질문에만 답한다.

“Semantic Definition이
코드 인터페이스에서 어떻게 나타나야 하는가?”

9. Status Declaration

Contract Layer v0: ✅ 최초 봉인

이후 변경은 Semantic 변경이 선행되어야만 가능---
title: "Measurement Semantic + Interface Freeze"
version: "v1.0.0"
status: "frozen"
created_date: "2026-01-21"
frozen_commit_sha: "9731aa4"
author: "Yang"
---

# Measurement Semantic + Interface Freeze v1.0.0

> Doc Type: Contract  
> Layer: Meta

---

## 1. Summary

본 선언은 측정 관련 Semantic 및 Interface 문서들이 정의/계약의 단일 진실원이며, 이 시점 이후에는 "무엇을 재는가"와 "단위/인터페이스"를 다시 의심하지 않음을 의미한다.

---

## 2. Scope

### In Scope

- 측정 의미(Semantic) 정의 고정
- 인터페이스 규약 고정
- 변경 제어 규칙

### Out of Scope

- Geometric 구현(알고리즘), 성능, 정확도, 품질 판단
- PASS/FAIL 판단 (Report에서만 수행)

---

## 3. Invariants (Normative)

### 3.1 MUST (필수)

- 아래 Frozen Artifacts는 변경 제어 규칙에 따라만 수정 가능
- 변경 시 새 버전 문서 + 새 Freeze + 새 Tag 필수

### 3.2 MUST NOT (금지)

- 기존 Freeze 선언의 무단 변경 금지
- 의미/계약 변경 시 기존 Freeze 무시 금지

---

## 4. Frozen Artifacts

1. `docs/policies/measurements/README.md`  
   - Body Measurement Meta-Policy (Semantic Invariants)

2. `docs/policies/measurements/BUST.md`  
3. `docs/policies/measurements/WAIST.md`  
4. `docs/policies/measurements/HIP.md`  
   - Item Contracts (Selection Rules only)

5. `docs/policies/measurements/INTERFACE_TO_GEOMETRIC.md`  
   - Semantic → Geometric Minimal Interface Contract

---

## 5. Prohibitions (Explicit)

- Geometric 구현(알고리즘), 성능, 정확도, 품질 판단
- PASS/FAIL 판단 (Report에서만 수행)

---

## 6. Change Notes

v1.0.0:
- Measurement Semantic + Interface Freeze 초기 선언

---

## 7. Freeze Notes

**Frozen Artifacts:**
- `docs/policies/measurements/README.md`
- `docs/policies/measurements/BUST.md`
- `docs/policies/measurements/WAIST.md`
- `docs/policies/measurements/HIP.md`
- `docs/policies/measurements/INTERFACE_TO_GEOMETRIC.md`

**Change Control:**
- 위 문서들의 변경은 "의미/계약 변경"에 해당한다
- 변경이 필요할 경우:
  - 기존 Freeze는 유지하며,
  - **새 버전 문서 + 새 Freeze + 새 Tag**로만 진행한다

**Approved by:** Project Owner (Human)  
**Date:** 2026-01-21 (KST)
GEOMETRIC_DESIGN_CHEST_V0.md

Geometric Layer — Design Specification

0. Scope & Authority

Layer: Geometric (Implementation Design)

Measurement: CHEST

Semantic Anchor: SEMANTIC_DEFINITION_CHEST_VNEXT.md

Contract Anchor: CONTRACT_INTERFACE_CHEST_V0.md

Non-Goals:

해부학적 추론 ❌

bust 제거 로직 ❌

정확도 최적화 ❌

PASS/FAIL 판정 ❌

본 문서는 CHEST를 계산 “어떻게 할 것인가”에 대한 최소 구현 설계다.
의미 판단은 절대 포함하지 않는다.

1. Design Principle (핵심 원칙)

CHEST Geometric Layer v0는 다음 원칙을 따른다.

Circumference v0 패턴 최대 재사용

해부학적 추론 금지

기하학적 극값 탐색 금지

정의되지 않은 경우 NaN 반환 허용

즉,

“CHEST를 ‘잘’ 재는 것”이 아니라
“CHEST를 Semantic/Contract 위반 없이 계산하는 가장 단순한 방법”

을 목표로 한다.

2. Input / Output (계약 재확인)

입력:

verts: float32[N,3] (meters)

measurement_key = CHEST

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

3.2 CHEST-specific Region Gating (최소 제약)

CHEST v0는 아주 약한 영역 제약만 적용한다.

허용 영역:

상체(Upper Torso) 추정 범위

금지 영역:

복부 하단

명백한 하체 영역

⚠️ 주의

정확한 비율, landmark, skeleton 정보 사용 금지

이 단계에서는 “대략적인 상체 범위”만 필요

이 gating은 의미를 보장하기 위함이 아니라
의미를 훼손할 가능성을 줄이기 위한 최소 안전장치다.

3.3 Section Selection Rule (v0)

CHEST v0에서는 다음 규칙만 허용한다.

선택 규칙:

허용 영역 내에서

중앙값(median)에 가장 가까운 단면

금지:

max (BUST 혼동 위험)

min (WAIST 혼동 위험)

의미

극값을 피함으로써

CHEST의 “구조적 안정성”만 확보

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

상체 영역 내 후보가 다수 존재

UNIT_FAIL

수치 스케일 이상 감지 시

Warning은:

결과를 차단하지 않음

Judgment Layer로 전달됨

6. section_id & method_tag 규칙
section_id

포함 정보:

axis (y)

slice_index

region_gate (upper_torso)

JSON 직렬화 문자열 권장

method_tag
chest_v0_y_slice_median

7. Failure Handling
상황	처리
후보 단면 없음	NaN + DEGEN_FAIL
폐곡선 불성립	NaN
입력 오류	Exception (Contract 위반)

NaN은 정상 결과다.

8. Geometric Boundary Statement

본 Geometric Layer는 다음을 의도적으로 하지 않는다.

해부학적 landmark 추론

bust 제거 알고리즘

Skeleton / pose 활용

최적화 기반 탐색

9. Status

CHEST Geometric Layer v0: 설계 완료

다음 단계: Validation Layer v0 (CHEST)---
title: "Body Measurement Meta-Policy"
version: "v1.3"
status: "frozen"
created_date: "2026-01-16"
frozen_commit_sha: "9731aa4"
author: "Yang"
---

# Body Measurement Meta-Policy v1.3

> Doc Type: Contract  
> Layer: Semantic

---

## 1. Summary

본 계약은 모든 신체 둘레 측정의 의미(Semantic) 정의를 고정한다.  
이 계약이 깨질 경우 측정 결과의 일관성과 재현성이 보장되지 않으며, Semantic Layer와 Geometric Layer 간 인터페이스 혼란이 발생한다.

---

## 2. Scope

### In Scope

- 측정 의미(Semantic) 정의
- 둘레 측정의 개념적 정의
- 측정 의미의 자세 독립성
- 좌표계 해석 위임 규칙

### Out of Scope

- 구현 세부 (특정 알고리즘, 정점 인덱스, 파라미터)
- 정확도 비교
- 성능
- Gate, PASS/FAIL 판단
- 서비스 레이어

---

## 3. Invariants (Normative)

### 3.1 MUST (필수)

- **둘레의 정의**: 모든 둘레 측정은 인체 장축에 직교하는 단면상의 폐곡선(Closed curve) 길이로 정의한다.
- **의미 독립성**: 측정의 의미는 인체의 자세(A-pose, T-pose 등)나 특정 메시의 토폴로지에 의존하지 않는다.

### 3.2 MUST NOT (금지)

- 특정 정점 인덱스(Vertex Index) 언급 금지
- SMPL-X 파라미터($\beta$) 언급 금지
- 특정 기하학 알고리즘 언급 금지

### 3.3 SHOULD (권장)

- **좌표계 위임**: "수평" 및 "수직"에 대한 물리적 좌표계 해석은 Geometric Layer의 구현체로 위임한다.

---

## 4. Interface / Schema (If Applicable)

N/A (Semantic-only 계약)

---

## 5. Terminology

- **Cross-section**: 인체 장축에 수직인 절단면
- **Closed Curve**: 단면 상에서 인체 표면을 따라 형성되는 닫힌 경로

---

## 6. Change Notes

v1.3:
- Semantic Layer 정의 명확화
- 좌표계 위임 규칙 추가

---

## 7. Freeze Notes

**Frozen Artifacts:**
- 본 문서 (Body Measurement Meta-Policy v1.3)
- 관련 측정 항목 계약 (BUST, WAIST, HIP)

**Change Control:**
- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능
아래는 CHEST Measurement의 Semantic Definition vNext 초안입니다. (구현·계약·검증·판정 제외)

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

다음 단계: Contract Layer v0 (CHEST)Semantic Layer — Final Definition (vNext)

0. Scope & Authority

Layer: Semantic (Definition)

Measurement Family: Circumference

Supersedes: Implicit semantic assumptions in circumference_v0

Non-Goals:

구현 방식 정의 ❌

단면 선택 알고리즘 ❌

검증 기준 / 임계값 ❌

PASS / FAIL 판정 ❌

본 문서는 **“우리가 무엇을 측정한다고 말하는가”**에 대해서만 답한다.
이 정의는 이후 Contract, Geometric, Validation, Judgment Layer의 해석 기준(anchor) 이 된다.

1. Core Semantic Statement

Circumference란,
3차원 인체 형상에서 특정 해부학적 의미를 갖는 횡단면이 형성될 때에만 정의되는 측정값이다.

이 정의는 항상 성립하지 않는다.
정의가 성립하지 않는 경우, 결과는 실패가 아니라 정의되지 않음(Undefined) 이다.

2. Undefined의 의미론 (NaN = Undefined)
2.1 정의 선언

Circumference는 유효한 폐곡선 단면이 존재할 때만 정의된다.
다음 조건 중 하나라도 충족되지 않을 경우, 해당 측정은 정의되지 않음(Undefined) 으로 간주한다.

횡단면이 기하학적으로 형성되지 않는 경우

폐곡선을 구성할 수 없는 경우

단면 후보가 정의상 허용된 영역에 존재하지 않는 경우

2.2 NaN의 의미

NaN은 계산 실패(Error)가 아니다.
NaN은 질문 자체가 성립하지 않음을 나타내는 의미론적 값이다.

이는 다음을 의미한다.

구현체는 “억지로 답을 낼 의무가 없다”

Geometry Layer는 침묵할 권리가 있다

Judgment Layer는 이를 결함이 아닌 정의 경계 신호로 해석한다

3. WAIST의 의미론적 정의 (의도적 유보)
3.1 현재 정의 (vNext에서도 유지)

WAIST는 몸통 영역에서 상대적으로 가장 좁은 둘레로 정의된다.

3.2 의도적 유보 선언

여기서 “가장 좁다”는 개념은
기하학적 최소값인지, 해부학적 위치 제약을 동반한 최소값인지는 아직 정의되지 않았다.

3.3 의미

현재 정의는 기하학적으로는 유효하나

생물학적·해부학적 의미를 완전히 보장하지는 않는다

이 유보는 다음을 허용한다.

vNext 이후에서 해부학적 지식(Semantic Prior)을 도입할 가능성

기하학적 단순화와 의미론적 정확성 사이의 공식적인 긴장 관계 인정

4. Unit Assumption & Responsibility (Meters 전제)
4.1 정의 선언

Circumference의 의미론은 입력 좌표가 meters 단위임을 전제로 한다.

4.2 위반 시 해석

이 전제가 충족되지 않을 경우,

결과는 의미론적으로 해석 불가

이는 계산 오류가 아니라 정의 위반

4.3 책임 귀속

단위 해석은 Semantic / Contract Layer의 책임

Geometry Layer는 단위 추론, 보정, 추측을 수행하지 않는다

이는 명시적인 GIGO(Garbage In, Garbage Out) 원칙의 선언이다.

5. Measurement Failure의 재정의

본 프로젝트에서 다음 구분을 명확히 한다.

구분	의미
Error	시스템 또는 구현의 실패
Undefined (NaN)	질문이 정의되지 않음
Warning	해석 시 주의가 필요한 신호

Circumference에서 NaN은 결함이 아니라 정의의 경계 표현이다.

6. Semantic Boundary Statement

본 Semantic Definition은 다음을 의도적으로 포함하지 않는다.

단면 생성 방식

후보 선택 규칙(max/min 등)의 구현

퇴화 판단 로직

검증 메트릭

결과 해석 규칙

Semantic Layer는 오직 다음 질문에만 답한다.

“우리는 무엇을 측정한다고 주장하는가?”

7. Status Declaration

Semantic Definition vNext: ✅ 확정

본 정의는 이후 모든 Layer의 해석 기준(anchor) 로 사용된다.

구현 변경은 요구하지 않으며,
차기 사이클에서만 설계 선택이 발생할 수 있다.---
title: "Validation Frame: CHEST v0"
version: "v0.1"
status: "draft"
created_date: "2026-01-21"
author: "Yang"
---

# Validation Frame: CHEST v0

> Doc Type: Contract  
> Layer: Validation

---

## 1. Purpose

본 계약은 `core/measurements/chest_v0.py::measure_chest_v0`에 대한 검증 프로토콜을 정의합니다.

검증의 목적:
- 측정 함수의 실행 가능성 확인
- 출력 형식 계약 준수 확인
- 재현 가능성(결정성) 확인
- 실패 케이스 분류 및 기록

**Non-Goals:**
- 정확도 판정 (PASS/FAIL 임계값 기반)
- 품질 게이트 (delta, delta_pct, fail_rate)
- 성능 최적화 평가
- 시스템 아키텍처 재설계

---

## 2. Inputs

### 2.1 Dataset Tiers

**Tier S0: Synthetic Cases**
- 목적: 기본 실행 가능성 및 계약 준수 확인
- 형식: NPZ 파일 (`verification/datasets/golden/chest_v0/s0_synthetic_cases.npz`)
- 포함 케이스:
  - 정상 케이스 (박스/원통 유사) 2개
  - 퇴화 케이스 (y-range 매우 작음) 1개
  - 극소 N (정점 1~2개) 1개
  - 스케일 오류 의심 (cm 스케일처럼 큰 값) 1개
  - 랜덤 노이즈 케이스 (결정성 체크용, seed 고정) 1개

### 2.2 Input Format

**verts** (required):
- Shape: `(N, 3)` where N >= 1
- Dtype: `float32`
- Units: **meters** (정상 케이스)
- Coordinate system: 3D Cartesian (x, y, z)
- y-axis: Body long axis (vertical)

**measurement_key** (required):
- Type: `Literal["CHEST"]` (단일 값만 허용)

**units_metadata** (optional):
- Type: `Dict[str, Any]` or `None`
- Default: meters assumed if not provided

---

## 3. Execution Protocol

### 3.1 Runner Script

**File**: `verification/runners/verify_chest_v0.py`

**Execution**:
```bash
python verification/runners/verify_chest_v0.py [--npz <path>] [--out_dir <path>]
```

**Process**:
1. Load NPZ dataset
2. For each case_id:
   - Call `measure_chest_v0(verts, measurement_key="CHEST")`
   - Record output to CSV
   - Handle exceptions (record failure_type)
   - Check determinism (2회 호출 비교)
3. Generate summary JSON

### 3.2 Exception Handling

- **INPUT_CONTRACT_FAIL**: Input shape/type validation failure
- **EXEC_FAIL**: Function execution exception (non-input related)
- **UNIT_FAIL**: Suspected unit error (e.g., cm instead of meters) - 표식만, 중단 금지
- **DEGEN_FAIL**: Degenerate geometry (too few vertices, zero range)
- **NONDETERMINISTIC**: Determinism violation (repeated calls produce different section_id/method_tag)

---

## 4. Output Metrics

### 4.1 Per-Case Output (CSV)

**File**: `verification/reports/chest_v0/validation_results.csv`

**Columns**:
- `case_id`: str
- `measurement_key`: str ("CHEST")
- `circumference_m`: float or "NaN" (meters)
- `section_id`: str (JSON string)
- `method_tag`: str
- `warnings_json`: str (JSON array of warning strings)
- `failure_type`: str or empty (if execution failed)

### 4.2 Summary Output (JSON)

**File**: `verification/reports/chest_v0/validation_summary.json`

**Fields**:
- `git_sha`: str (if available)
- `dataset_id`: str (e.g., "s0_synthetic_cases")
- `nan_rate`: float (NaN 비율)
- `warning_histogram`: Dict[str, int] (warning 타입별 발생 횟수)
- `determinism_mismatch_count`: int (반복 실행 2회 비교 시 불일치 횟수)
- `nonfinite_count`: int (circumference_m이 NaN/Inf인 케이스 수)
- `failure_count_by_type`: Dict[str, int] (failure_type별 발생 횟수)

**Units**:
- 모든 길이/둘레 값은 **meters** 단위
- `circumference_m`은 float 또는 NaN

---

## 5. Failure Taxonomy

### 5.1 INPUT_CONTRACT_FAIL

**Definition**: Input validation 실패

**Examples**:
- `verts.shape[1] != 3`
- `verts.ndim != 2`
- `measurement_key != "CHEST"`

**Recording**:
- `failure_type = "INPUT_CONTRACT_FAIL"`
- `warnings_json`에 stacktrace 요약 포함 (너무 길면 잘라서)

### 5.2 EXEC_FAIL

**Definition**: Function execution 중 예외 발생 (input validation 통과 후)

**Examples**:
- IndexError, ValueError (non-input)
- MemoryError
- 기타 런타임 예외

**Recording**:
- `failure_type = "EXEC_FAIL"`
- `warnings_json`에 stacktrace 요약 포함

### 5.3 UNIT_FAIL

**Definition**: 스케일 오류 의심 (예: cm 단위로 입력됨)

**Examples**:
- `circumference_m > 10.0` (10m 이상은 비정상)
- `warnings`에 "PERIMETER_LARGE" 포함

**Recording**:
- `failure_type = "UNIT_FAIL"` (표식만)
- **중단 금지**: 계속 실행하여 전체 데이터셋 검증 완료

### 5.4 DEGEN_FAIL

**Definition**: 퇴화 기하학 (degenerate geometry)

**Examples**:
- `y_range < 1e-6` (body axis too short)
- `N < 3` (too few vertices)
- `warnings`에 "BODY_AXIS_TOO_SHORT", "EMPTY_CANDIDATES", "DEGEN_FAIL" 포함

**Recording**:
- `failure_type = "DEGEN_FAIL"` (선택적, warnings로도 충분)
- `circumference_m = NaN` (정상 fallback)

### 5.5 NONDETERMINISTIC

**Definition**: 결정성 위반 (determinism violation)

**Detection**:
- 동일 입력으로 2회 호출
- `section_id` 또는 `method_tag` 불일치

**Recording**:
- `failure_type = "NONDETERMINISTIC"`
- `determinism_mismatch_count` 증가

---

## 6. Validation Artifacts

### 6.1 Required Files

1. **Dataset**: `verification/datasets/golden/chest_v0/s0_synthetic_cases.npz`
2. **Runner**: `verification/runners/verify_chest_v0.py`
3. **Test**: `tests/test_chest_v0_validation_contract.py`
4. **Output CSV**: `verification/reports/chest_v0/validation_results.csv`
5. **Output JSON**: `verification/reports/chest_v0/validation_summary.json`

### 6.2 Artifact Structure

**NPZ Dataset**:
- `verts`: `(N_cases, N_verts, 3)` or list of `(N_verts, 3)` arrays, `float32`
- `case_id`: `(N_cases,)` array of str or int

**CSV Output**:
- One row per `case_id`
- UTF-8 encoding

**JSON Output**:
- UTF-8 encoding
- Pretty-printed (indent=2)

---

## 7. Change Notes

v0.1 (2026-01-21):
- Initial validation frame definition
- S0 synthetic dataset specification
- Failure taxonomy establishment
- No PASS/FAIL thresholds (factual recording only)
---
title: "Validation Frame: Circumference v0"
version: "v0.1"
status: "draft"
created_date: "2026-01-21"
author: "Yang"
---

# Validation Frame: Circumference v0

> Doc Type: Contract  
> Layer: Validation

---

## 1. Purpose

본 계약은 `core/measurements/circumference_v0.py::measure_circumference_v0`에 대한 검증 프로토콜을 정의합니다.

검증의 목적:
- 측정 함수의 실행 가능성 확인
- 출력 형식 계약 준수 확인
- 재현 가능성(결정성) 확인
- 실패 케이스 분류 및 기록

**Non-Goals:**
- 정확도 판정 (PASS/FAIL 임계값 기반)
- 품질 게이트 (delta, delta_pct, fail_rate)
- 성능 최적화 평가
- 시스템 아키텍처 재설계

---

## 2. Inputs

### 2.1 Dataset Tiers

**Tier S0: Synthetic Cases**
- 목적: 기본 실행 가능성 및 계약 준수 확인
- 형식: NPZ 파일 (`verification/datasets/golden/circumference_v0/s0_synthetic_cases.npz`)
- 포함 케이스:
  - 정상 케이스 (박스/원통 유사) 2개
  - 퇴화 케이스 (y-range 매우 작음) 1개
  - 극소 N (정점 1~2개) 1개
  - 스케일 오류 의심 (cm 스케일처럼 큰 값) 1개
  - 랜덤 노이즈 케이스 (결정성 체크용, seed 고정) 1개

### 2.2 Input Format

**verts** (required):
- Shape: `(N, 3)` where N >= 1
- Dtype: `float32`
- Units: **meters** (정상 케이스)
- Coordinate system: 3D Cartesian (x, y, z)
- y-axis: Body long axis (vertical)

**measurement_key** (required):
- Type: `Literal["BUST", "WAIST", "HIP"]`

**units_metadata** (optional):
- Type: `Dict[str, Any]` or `None`
- Default: meters assumed if not provided

---

## 3. Execution Protocol

### 3.1 Runner Script

**File**: `verification/runners/verify_circumference_v0.py`

**Execution**:
```bash
python verification/runners/verify_circumference_v0.py [--npz <path>] [--out_dir <path>]
```

**Process**:
1. Load NPZ dataset
2. For each case_id:
   - For each measurement_key in ["BUST", "WAIST", "HIP"]:
     - Call `measure_circumference_v0(verts, measurement_key)`
     - Record output to CSV
     - Handle exceptions (record failure_type)
3. Generate summary JSON

### 3.2 Exception Handling

- **INPUT_CONTRACT_FAIL**: Input shape/type validation failure
- **EXEC_FAIL**: Function execution exception (non-input related)
- **UNIT_FAIL**: Suspected unit error (e.g., cm instead of meters) - 표식만, 중단 금지
- **DEGEN_FAIL**: Degenerate geometry (too few vertices, zero range)
- **NONDETERMINISTIC**: Determinism violation (repeated calls produce different section_id/method_tag)

---

## 4. Output Metrics

### 4.1 Per-Case Output (CSV)

**File**: `verification/reports/circumference_v0/validation_results.csv`

**Columns**:
- `case_id`: str
- `measurement_key`: str ("BUST" | "WAIST" | "HIP")
- `circumference_m`: float or "NaN" (meters)
- `section_id`: str (JSON string)
- `method_tag`: str
- `warnings_json`: str (JSON array of warning strings)
- `failure_type`: str or empty (if execution failed)

### 4.2 Summary Output (JSON)

**File**: `verification/reports/circumference_v0/validation_summary.json`

**Fields**:
- `git_sha`: str (if available)
- `dataset_id`: str (e.g., "s0_synthetic_cases")
- `nan_rate_by_key`: Dict[str, float] (BUST/WAIST/HIP별 NaN 비율)
- `warning_histogram`: Dict[str, int] (warning 타입별 발생 횟수)
- `determinism_mismatch_count`: int (반복 실행 2회 비교 시 불일치 횟수)
- `nonfinite_count`: int (circumference_m이 NaN/Inf인 케이스 수)
- `failure_count_by_type`: Dict[str, int] (failure_type별 발생 횟수)

**Units**:
- 모든 길이/둘레 값은 **meters** 단위
- `circumference_m`은 float 또는 NaN

---

## 5. Failure Taxonomy

### 5.1 INPUT_CONTRACT_FAIL

**Definition**: Input validation 실패

**Examples**:
- `verts.shape[1] != 3`
- `verts.ndim != 2`
- `measurement_key not in ["BUST", "WAIST", "HIP"]`

**Recording**:
- `failure_type = "INPUT_CONTRACT_FAIL"`
- `warnings_json`에 stacktrace 요약 포함 (너무 길면 잘라서)

### 5.2 EXEC_FAIL

**Definition**: Function execution 중 예외 발생 (input validation 통과 후)

**Examples**:
- IndexError, ValueError (non-input)
- MemoryError
- 기타 런타임 예외

**Recording**:
- `failure_type = "EXEC_FAIL"`
- `warnings_json`에 stacktrace 요약 포함

### 5.3 UNIT_FAIL

**Definition**: 스케일 오류 의심 (예: cm 단위로 입력됨)

**Examples**:
- `circumference_m > 10.0` (10m 이상은 비정상)
- `warnings`에 "PERIMETER_LARGE" 포함

**Recording**:
- `failure_type = "UNIT_FAIL"` (표식만)
- **중단 금지**: 계속 실행하여 전체 데이터셋 검증 완료

### 5.4 DEGEN_FAIL

**Definition**: 퇴화 기하학 (degenerate geometry)

**Examples**:
- `y_range < 1e-6` (body axis too short)
- `N < 3` (too few vertices)
- `warnings`에 "BODY_AXIS_TOO_SHORT", "EMPTY_CANDIDATES" 포함

**Recording**:
- `failure_type = "DEGEN_FAIL"` (선택적, warnings로도 충분)
- `circumference_m = NaN` (정상 fallback)

### 5.5 NONDETERMINISTIC

**Definition**: 결정성 위반 (determinism violation)

**Detection**:
- 동일 입력으로 2회 호출
- `section_id` 또는 `method_tag` 불일치

**Recording**:
- `failure_type = "NONDETERMINISTIC"`
- `determinism_mismatch_count` 증가

---

## 6. Validation Artifacts

### 6.1 Required Files

1. **Dataset**: `verification/datasets/golden/circumference_v0/s0_synthetic_cases.npz`
2. **Runner**: `verification/runners/verify_circumference_v0.py`
3. **Test**: `tests/test_circumference_v0_validation_contract.py`
4. **Output CSV**: `verification/reports/circumference_v0/validation_results.csv`
5. **Output JSON**: `verification/reports/circumference_v0/validation_summary.json`

### 6.2 Artifact Structure

**NPZ Dataset**:
- `verts`: `(N_cases, N_verts, 3)` or list of `(N_verts, 3)` arrays, `float32`
- `case_id`: `(N_cases,)` array of str or int

**CSV Output**:
- One row per `(case_id, measurement_key)` combination
- UTF-8 encoding

**JSON Output**:
- UTF-8 encoding
- Pretty-printed (indent=2)

---

## 7. Change Notes

v0.1 (2026-01-21):
- Initial validation frame definition
- S0 synthetic dataset specification
- Failure taxonomy establishment
- No PASS/FAIL thresholds (factual recording only)
---
title: "Validation Frame: HIP v0"
version: "v0.1"
status: "draft"
created_date: "2026-01-21"
author: "Yang"
---

# Validation Frame: HIP v0

> Doc Type: Contract  
> Layer: Validation

---

## 1. Purpose

본 계약은 `core/measurements/hip_v0.py::measure_hip_v0`에 대한 검증 프로토콜을 정의합니다.

검증의 목적:
- 측정 함수의 실행 가능성 확인
- 출력 형식 계약 준수 확인
- 재현 가능성(결정성) 확인
- 실패 케이스 분류 및 기록

**Non-Goals:**
- 정확도 판정 (PASS/FAIL 임계값 기반)
- 품질 게이트 (delta, delta_pct, fail_rate)
- 성능 최적화 평가
- 시스템 아키텍처 재설계

---

## 2. Inputs

### 2.1 Dataset Tiers

**Tier S0: Synthetic Cases**
- 목적: 기본 실행 가능성 및 계약 준수 확인
- 형식: NPZ 파일 (`verification/datasets/golden/hip_v0/s0_synthetic_cases.npz`)
- 포함 케이스:
  - 정상 케이스 (박스/원통 유사) 2개
  - 퇴화 케이스 (y-range 매우 작음) 1개
  - 극소 N (정점 1~2개) 1개
  - 스케일 오류 의심 (cm 스케일처럼 큰 값) 1개
  - 랜덤 노이즈 케이스 (결정성 체크용, seed 고정) 1개
  - 상위 quantile 모호성 케이스 (upper_quantile_ambiguous) 1개

### 2.2 Input Format

**verts** (required):
- Shape: `(N, 3)` where N >= 1
- Dtype: `float32`
- Units: **meters** (정상 케이스)
- Coordinate system: 3D Cartesian (x, y, z)
- y-axis: Body long axis (vertical)

**measurement_key** (required):
- Type: `Literal["HIP"]` (단일 값만 허용)

**units_metadata** (optional):
- Type: `Dict[str, Any]` or `None`
- Default: meters assumed if not provided

---

## 3. Execution Protocol

### 3.1 Runner Script

**File**: `verification/runners/verify_hip_v0.py`

**Execution**:
```bash
python verification/runners/verify_hip_v0.py [--npz <path>] [--out_dir <path>]
```

**Process**:
1. Load NPZ dataset
2. For each case_id:
   - Call `measure_hip_v0(verts, measurement_key="HIP")`
   - Record output to CSV
   - Handle exceptions (record failure_type)
   - Check determinism (2회 호출 비교)
3. Generate summary JSON

### 3.2 Exception Handling

- **INPUT_CONTRACT_FAIL**: Input shape/type validation failure
- **EXEC_FAIL**: Function execution exception (non-input related)
- **UNIT_FAIL**: Suspected unit error (e.g., cm instead of meters) - 표식만, 중단 금지
- **DEGEN_FAIL**: Degenerate geometry (too few vertices, zero range)
- **NONDETERMINISTIC**: Determinism violation (repeated calls produce different section_id/method_tag)

---

## 4. Output Metrics

### 4.1 Per-Case Output (CSV)

**File**: `verification/reports/hip_v0/validation_results.csv`

**Columns**:
- `case_id`: str
- `measurement_key`: str ("HIP")
- `circumference_m`: float or "NaN" (meters)
- `section_id`: str (JSON string)
- `method_tag`: str
- `warnings_json`: str (JSON array of warning strings)
- `failure_type`: str or empty (if execution failed)

### 4.2 Summary Output (JSON)

**File**: `verification/reports/hip_v0/validation_summary.json`

**Fields**:
- `git_sha`: str (if available)
- `dataset_id`: str (e.g., "s0_synthetic_cases")
- `nan_rate`: float (NaN 비율)
- `warning_histogram`: Dict[str, int] (warning 타입별 발생 횟수)
- `determinism_mismatch_count`: int (반복 실행 2회 비교 시 불일치 횟수)
- `nonfinite_count`: int (circumference_m이 NaN/Inf인 케이스 수)
- `failure_count_by_type`: Dict[str, int] (failure_type별 발생 횟수)

**Units**:
- 모든 길이/둘레 값은 **meters** 단위
- `circumference_m`은 float 또는 NaN

---

## 5. Failure Taxonomy

### 5.1 INPUT_CONTRACT_FAIL

**Definition**: Input validation 실패

**Examples**:
- `verts.shape[1] != 3`
- `verts.ndim != 2`
- `measurement_key != "HIP"`

**Recording**:
- `failure_type = "INPUT_CONTRACT_FAIL"`
- `warnings_json`에 stacktrace 요약 포함 (너무 길면 잘라서)

### 5.2 EXEC_FAIL

**Definition**: Function execution 중 예외 발생 (input validation 통과 후)

**Examples**:
- IndexError, ValueError (non-input)
- MemoryError
- 기타 런타임 예외

**Recording**:
- `failure_type = "EXEC_FAIL"`
- `warnings_json`에 stacktrace 요약 포함

### 5.3 UNIT_FAIL

**Definition**: 스케일 오류 의심 (예: cm 단위로 입력됨)

**Examples**:
- `circumference_m > 10.0` (10m 이상은 비정상)
- `warnings`에 "PERIMETER_LARGE" 포함

**Recording**:
- `failure_type = "UNIT_FAIL"` (표식만)
- **중단 금지**: 계속 실행하여 전체 데이터셋 검증 완료

### 5.4 DEGEN_FAIL

**Definition**: 퇴화 기하학 (degenerate geometry)

**Examples**:
- `y_range < 1e-6` (body axis too short)
- `N < 3` (too few vertices)
- `warnings`에 "BODY_AXIS_TOO_SHORT", "EMPTY_CANDIDATES", "DEGEN_FAIL" 포함

**Recording**:
- `failure_type = "DEGEN_FAIL"` (선택적, warnings로도 충분)
- `circumference_m = NaN` (정상 fallback)

### 5.5 NONDETERMINISTIC

**Definition**: 결정성 위반 (determinism violation)

**Detection**:
- 동일 입력으로 2회 호출
- `section_id` 또는 `method_tag` 불일치

**Recording**:
- `failure_type = "NONDETERMINISTIC"`
- `determinism_mismatch_count` 증가

---

## 6. Validation Artifacts

### 6.1 Required Files

1. **Dataset**: `verification/datasets/golden/hip_v0/s0_synthetic_cases.npz`
2. **Runner**: `verification/runners/verify_hip_v0.py`
3. **Test**: `tests/test_hip_v0_validation_contract.py`
4. **Output CSV**: `verification/reports/hip_v0/validation_results.csv`
5. **Output JSON**: `verification/reports/hip_v0/validation_summary.json`

### 6.2 Artifact Structure

**NPZ Dataset**:
- `verts`: `(N_cases, N_verts, 3)` or list of `(N_verts, 3)` arrays, `float32`
- `case_id`: `(N_cases,)` array of str or int

**CSV Output**:
- One row per `case_id`
- UTF-8 encoding

**JSON Output**:
- UTF-8 encoding
- Pretty-printed (indent=2)

---

## 7. Change Notes

v0.1 (2026-01-21):
- Initial validation frame definition
- S0 synthetic dataset specification (7 cases including upper_quantile_ambiguous)
- Failure taxonomy establishment
- No PASS/FAIL thresholds (factual recording only)
---
title: "Validation Frame: THIGH v0"
version: "v0.1"
status: "draft"
created_date: "2026-01-21"
author: "Yang"
---

# Validation Frame: THIGH v0

> Doc Type: Contract  
> Layer: Validation

---

## 1. Purpose

본 계약은 `core/measurements/thigh_v0.py::measure_thigh_v0`에 대한 검증 프로토콜을 정의합니다.

검증의 목적:
- 측정 함수의 실행 가능성 확인
- 출력 형식 계약 준수 확인
- 재현 가능성(결정성) 확인
- 실패 케이스 분류 및 기록

**Non-Goals:**
- 정확도 판정 (PASS/FAIL 임계값 기반)
- 품질 게이트 (delta, delta_pct, fail_rate)
- 성능 최적화 평가
- 시스템 아키텍처 재설계

---

## 2. Inputs

### 2.1 Dataset Tiers

**Tier S0: Synthetic Cases**
- 목적: 기본 실행 가능성 및 계약 준수 확인
- 형식: NPZ 파일 (`verification/datasets/golden/thigh_v0/s0_synthetic_cases.npz`)
- 포함 케이스:
  - 정상 케이스 (박스/원통 유사) 2개
  - 퇴화 케이스 (y-range 매우 작음) 1개
  - 극소 N (정점 1~2개) 1개
  - 스케일 오류 의심 (cm 스케일처럼 큰 값) 1개
  - 랜덤 노이즈 케이스 (결정성 체크용, seed 고정) 1개
  - HIP 영역 침범 위험 (hip_bleed_risk) 1개
  - 무릎 근접 위험 (knee_proximity_risk) 1개

### 2.2 Input Format

**verts** (required):
- Shape: `(N, 3)` where N >= 1
- Dtype: `float32`
- Units: **meters** (정상 케이스)
- Coordinate system: 3D Cartesian (x, y, z)
- y-axis: Body long axis (vertical)

**measurement_key** (required):
- Type: `Literal["THIGH"]` (단일 값만 허용)

**units_metadata** (optional):
- Type: `Dict[str, Any]` or `None`
- Default: meters assumed if not provided

---

## 3. Execution Protocol

### 3.1 Runner Script

**File**: `verification/runners/verify_thigh_v0.py`

**Execution**:
```bash
python verification/runners/verify_thigh_v0.py [--npz <path>] [--out_dir <path>]
```

**Process**:
1. Load NPZ dataset
2. For each case_id:
   - Call `measure_thigh_v0(verts, measurement_key="THIGH")`
   - Record output to CSV
   - Handle exceptions (record failure_type)
   - Check determinism (2회 호출 비교)
3. Generate summary JSON

### 3.2 Exception Handling

- **INPUT_CONTRACT_FAIL**: Input shape/type validation failure
- **EXEC_FAIL**: Function execution exception (non-input related)
- **UNIT_FAIL**: Suspected unit error (e.g., cm instead of meters) - 표식만, 중단 금지
- **DEGEN_FAIL**: Degenerate geometry (too few vertices, zero range)
- **NONDETERMINISTIC**: Determinism violation (repeated calls produce different section_id/method_tag)

---

## 4. Output Metrics

### 4.1 Per-Case Output (CSV)

**File**: `verification/reports/thigh_v0/validation_results.csv`

**Columns**:
- `case_id`: str
- `measurement_key`: str ("THIGH")
- `circumference_m`: float or "NaN" (meters)
- `section_id`: str (JSON string)
- `method_tag`: str
- `warnings_json`: str (JSON array of warning strings)
- `failure_type`: str or empty (if execution failed)

### 4.2 Summary Output (JSON)

**File**: `verification/reports/thigh_v0/validation_summary.json`

**Fields**:
- `git_sha`: str (if available)
- `dataset_id`: str (e.g., "s0_synthetic_cases")
- `nan_rate`: float (NaN 비율)
- `warning_histogram`: Dict[str, int] (warning 타입별 발생 횟수)
- `determinism_mismatch_count`: int (반복 실행 2회 비교 시 불일치 횟수)
- `nonfinite_count`: int (circumference_m이 NaN/Inf인 케이스 수)
- `failure_count_by_type`: Dict[str, int] (failure_type별 발생 횟수)

**Units**:
- 모든 길이/둘레 값은 **meters** 단위
- `circumference_m`은 float 또는 NaN

---

## 5. Failure Taxonomy

### 5.1 INPUT_CONTRACT_FAIL

**Definition**: Input validation 실패

**Examples**:
- `verts.shape[1] != 3`
- `verts.ndim != 2`
- `measurement_key != "THIGH"`

**Recording**:
- `failure_type = "INPUT_CONTRACT_FAIL"`
- `warnings_json`에 stacktrace 요약 포함 (너무 길면 잘라서)

### 5.2 EXEC_FAIL

**Definition**: Function execution 중 예외 발생 (input validation 통과 후)

**Examples**:
- IndexError, ValueError (non-input)
- MemoryError
- 기타 런타임 예외

**Recording**:
- `failure_type = "EXEC_FAIL"`
- `warnings_json`에 stacktrace 요약 포함

### 5.3 UNIT_FAIL

**Definition**: 스케일 오류 의심 (예: cm 단위로 입력됨)

**Examples**:
- `circumference_m > 10.0` (10m 이상은 비정상)
- `warnings`에 "PERIMETER_LARGE" 포함

**Recording**:
- `failure_type = "UNIT_FAIL"` (표식만)
- **중단 금지**: 계속 실행하여 전체 데이터셋 검증 완료

### 5.4 DEGEN_FAIL

**Definition**: 퇴화 기하학 (degenerate geometry)

**Examples**:
- `y_range < 1e-6` (body axis too short)
- `N < 3` (too few vertices)
- `warnings`에 "BODY_AXIS_TOO_SHORT", "EMPTY_CANDIDATES", "DEGEN_FAIL" 포함

**Recording**:
- `failure_type = "DEGEN_FAIL"` (선택적, warnings로도 충분)
- `circumference_m = NaN` (정상 fallback)

### 5.5 NONDETERMINISTIC

**Definition**: 결정성 위반 (determinism violation)

**Detection**:
- 동일 입력으로 2회 호출
- `section_id` 또는 `method_tag` 불일치

**Recording**:
- `failure_type = "NONDETERMINISTIC"`
- `determinism_mismatch_count` 증가

---

## 6. Validation Artifacts

### 6.1 Required Files

1. **Dataset**: `verification/datasets/golden/thigh_v0/s0_synthetic_cases.npz`
2. **Runner**: `verification/runners/verify_thigh_v0.py`
3. **Test**: `tests/test_thigh_v0_validation_contract.py`
4. **Output CSV**: `verification/reports/thigh_v0/validation_results.csv`
5. **Output JSON**: `verification/reports/thigh_v0/validation_summary.json`

### 6.2 Artifact Structure

**NPZ Dataset**:
- `verts`: `(N_cases, N_verts, 3)` or list of `(N_verts, 3)` arrays, `float32`
- `case_id`: `(N_cases,)` array of str or int

**CSV Output**:
- One row per `case_id`
- UTF-8 encoding

**JSON Output**:
- UTF-8 encoding
- Pretty-printed (indent=2)

---

## 7. Change Notes

v0.1 (2026-01-21):
- Initial validation frame definition
- S0 synthetic dataset specification (8 cases including hip_bleed_risk and knee_proximity_risk)
- Failure taxonomy establishment
- No PASS/FAIL thresholds (factual recording only)
---
title: "Bust Circumference"
version: "v1.0"
status: "frozen"
created_date: "2026-01-16"
frozen_commit_sha: "9731aa4"
author: "Yang"
---

# Bust Circumference v1.0

> Doc Type: Contract  
> Layer: Semantic

---

## 1. Summary

본 계약은 BUST(가슴둘레) 측정의 의미를 고정한다.  
이 계약이 깨질 경우 가슴둘레 측정의 일관성이 보장되지 않으며, 의류 제작 및 피팅에 혼란이 발생한다.

---

## 2. Scope

### In Scope

- BUST 측정의 의미 정의
- 선택 규칙 (Selection Rule)
- 모호성 처리 규칙

### Out of Scope

- 구현 세부 (Plane 방정식, 정점 루프, 특정 축 좌표값)
- 정확도 비교
- Gate, PASS/FAIL 판단
- Geometric Layer 구현

---

## 3. Invariants (Normative)

### 3.1 MUST (필수)

- **Key**: BUST
- **Definition**: 상반신 가슴 볼륨의 최대 돌출 지점을 포함하는 단면의 둘레
- **Selection Rule**: 해당 영역 내 둘레값의 최대값(Max) 채택

### 3.2 MUST NOT (금지)

- Plane 방정식 기재 금지
- 정점 루프 기재 금지
- 특정 축(Axis) 좌표값 기재 금지
- (이러한 내용은 Geometric Layer에서 다룸)

### 3.3 SHOULD (권장)

- **Ambiguity Handling**: 만약 최대 돌출 지점이 모호하거나 다수가 존재할 경우, 해부학적 기준에 따라 일관되게 식별 가능한 단면 하나를 선택한다.

---

## 4. Interface / Schema (If Applicable)

N/A (Semantic-only 계약)

---

## 5. Prohibitions (Explicit)

- Gate 정의
- Acceptance / PASS / FAIL
- 품질 평가
- 모델 학습, 회귀, Re-PCA 등

---

## 6. Change Notes

v1.0:
- BUST 측정 의미 정의 초기화

---

## 7. Freeze Notes

**Frozen Artifacts:**
- 본 문서 (Bust Circumference v1.0)

**Change Control:**
- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능
---
title: "..."            # DB: policies.name
version: "vX.Y"         # DB: policies.version
status: "draft|candidate|frozen|archived|deprecated"
created_date: "YYYY-MM-DD"
frozen_commit_sha: "abcdef0"   # status=frozen일 때 필수, 그 외 생략 가능

author: "Yang"
latest_report: "..."            # (옵션) Contract 문서에서는 보통 비워둔다
---

# <Contract Title> <version>

> Doc Type: Contract  
> Layer: Semantic | Data | Interface (중 하나만 선택)

---

## 1. Summary
- 이 문서가 **무엇을 고정(Freeze)하는 계약인지**를 1~3줄로 명시한다.
- 이 계약이 깨질 경우 발생하는 혼란의 종류를 간단히 적는다.

---

## 2. Scope
### In Scope
- 본 계약이 책임지는 레이어와 대상
  - 예: 측정 의미(Semantic), 단위 규약(Data), 인터페이스 형태(Interface)

### Out of Scope
- 명시적으로 다루지 않는 것
  - 구현 세부, 정확도 비교, 성능, Gate, PASS/FAIL 판단, 서비스 레이어 등

---

## 3. Invariants (Normative)
> 이 섹션만이 **강제 규칙**이다.  
> MUST / MUST NOT / SHOULD 를 명확히 구분한다.

### 3.1 MUST (필수)
- 반드시 지켜야 하는 불변 조건을 나열한다.

### 3.2 MUST NOT (금지)
- 이 계약 하에서 절대 발생해서는 안 되는 행위를 나열한다.

### 3.3 SHOULD (권장)
- 강제는 아니지만, 일관성과 추적성을 위해 권장되는 규칙을 나열한다.

---

## 4. Interface / Schema (If Applicable)
> Data / Interface 계약일 때만 사용한다.  
> Semantic-only 계약이면 `N/A`로 둔다.

### Inputs
- 입력 형태, 필수 메타데이터, 단위 요구사항 등

### Outputs
- 출력 값의 의미, 단위, 필수 필드

### Schema (Optional)
```json
{
  "example_field": "type"
}

5. Prohibitions (Explicit)

이 계약 문서에서 의도적으로 다루지 않는 것을 다시 한 번 명시한다.

Gate 정의

Acceptance / PASS / FAIL

품질 평가

모델 학습, 회귀, Re-PCA 등

6. Change Notes

vX.Y:

왜 이 버전이 생겼는지

무엇이 바뀌었는지

의미(Semantic)가 바뀌었는지 여부를 명확히 적는다.

7. Freeze Notes (When status = candidate | frozen)

Draft 단계에서는 생략 가능

Frozen Artifacts:

이 계약과 함께 봉인되는 파일 목록

Change Control:

변경은 새 버전 + 새 Freeze + 새 Tag로만 가능함을 명시
title: "Hip Circumference"

version: "v1.0"

status: "frozen"

created\_date: "2026-01-16"

frozen\_commit\_sha: "9731aa4"

author: "Yang"

---



\# Hip Circumference v1.0



> Doc Type: Contract  

> Layer: Semantic



---



\## 1. Summary



본 계약은 HIP(엉덩이둘레) 측정의 의미를 고정한다.  

이 계약이 깨질 경우 엉덩이둘레 측정의 일관성이 보장되지 않으며, 의류 제작 및 피팅에 혼란이 발생한다.



---



\## 2. Scope



\### In Scope



\- HIP 측정의 의미 정의

\- 선택 규칙 (Selection Rule)

\- 모호성 처리 규칙



\### Out of Scope



\- 구현 세부 (Plane 방정식, 정점 루프, 특정 축 좌표값)

\- 정확도 비교

\- Gate, PASS/FAIL 판단

\- Geometric Layer 구현



---



\## 3. Invariants (Normative)



\### 3.1 MUST (필수)



\- \*\*Key\*\*: HIP

\- \*\*Definition\*\*: 둔부 및 골반 최대 돌출 지점을 지나는 단면의 둘레

\- \*\*Selection Rule\*\*: 해당 영역 내 둘레값의 최대값(Max) 채택



\### 3.2 MUST NOT (금지)



\- Plane 방정식 기재 금지

\- 정점 루프 기재 금지

\- 특정 축(Axis) 좌표값 기재 금지

\- (이러한 내용은 Geometric Layer에서 다룸)



\### 3.3 SHOULD (권장)



\- \*\*Ambiguity Handling\*\*: 만약 최대 돌출 지점이 모호하거나 다수가 존재할 경우, 해부학적 기준에 따라 일관되게 식별 가능한 단면 하나를 선택한다.



---



\## 4. Interface / Schema (If Applicable)



N/A (Semantic-only 계약)



---



\## 5. Prohibitions (Explicit)



\- Gate 정의

\- Acceptance / PASS / FAIL

\- 품질 평가

\- 모델 학습, 회귀, Re-PCA 등



---



\## 6. Change Notes



v1.0:

\- HIP 측정 의미 정의 초기화



---



\## 7. Freeze Notes



\*\*Frozen Artifacts:\*\*

\- 본 문서 (Hip Circumference v1.0)



\*\*Change Control:\*\*

\- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능

---

title: "Waist Circumference"

version: "v1.0"

status: "frozen"

created\_date: "2026-01-16"

frozen\_commit\_sha: "9731aa4"

author: "Yang"

---



\# Waist Circumference v1.0



> Doc Type: Contract  

> Layer: Semantic



---



\## 1. Summary



본 계약은 WAIST(허리둘레) 측정의 의미를 고정한다.  

이 계약이 깨질 경우 허리둘레 측정의 일관성이 보장되지 않으며, 의류 제작 및 피팅에 혼란이 발생한다.



---



\## 2. Scope



\### In Scope



\- WAIST 측정의 의미 정의

\- 선택 규칙 (Selection Rule)

\- 모호성 처리 규칙



\### Out of Scope



\- 구현 세부 (Plane 방정식, 정점 루프, 특정 축 좌표값)

\- 정확도 비교

\- Gate, PASS/FAIL 판단

\- Geometric Layer 구현



---



\## 3. Invariants (Normative)



\### 3.1 MUST (필수)



\- \*\*Key\*\*: WAIST

\- \*\*Definition\*\*: 늑골 하단과 장골능 사이 구간에서 형성되는 단면의 둘레

\- \*\*Selection Rule\*\*: 해당 영역 내 둘레값의 최소값(Min) 채택



\### 3.2 MUST NOT (금지)



\- Plane 방정식 기재 금지

\- 정점 루프 기재 금지

\- 특정 축(Axis) 좌표값 기재 금지

\- (이러한 내용은 Geometric Layer에서 다룸)



\### 3.3 SHOULD (권장)



\- \*\*Ambiguity Handling\*\*: 만약 측정 기준 지점이 모호하거나 다수가 존재할 경우, 해부학적 기준에 따라 일관되게 식별 가능한 단면 하나를 선택한다.



---



\## 4. Interface / Schema (If Applicable)



N/A (Semantic-only 계약)



---



\## 5. Prohibitions (Explicit)



\- Gate 정의

\- Acceptance / PASS / FAIL

\- 품질 평가

\- 모델 학습, 회귀, Re-PCA 등



---



\## 6. Change Notes



v1.0:

\- WAIST 측정 의미 정의 초기화



---



\## 7. Freeze Notes



\*\*Frozen Artifacts:\*\*

\- 본 문서 (Waist Circumference v1.0)



\*\*Change Control:\*\*

\- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능



---

policy\_id: measurements-interface-to-geometric

policy\_name: Semantic → Geometric Minimal Interface Contract

version: 1.1.0

layer: interface

scope: semantic\_to\_geometric

status: active

keys: \[BUST, WAIST, HIP]

unit\_in: m

unit\_out: m

---



\# \[Interface Contract] Semantic → Geometric Minimal Rules



본 문서는 \*\*Semantic Layer에서 확정된 인체 측정 정의\*\*를  

Geometric Layer 구현체로 전달하기 위한 \*\*최소 인터페이스 규약\*\*이다.



본 규약의 목적은 다음과 같다.



\- 측정의 \*\*의미(Semantic)\*\* 를 구현으로부터 보호한다

\- Geometric Layer의 \*\*구현 자유도\*\*를 최대화한다

\- 단위·형태·선택 규칙에 대한 \*\*불변 조건\*\*을 명확히 한다



본 문서는 \*\*정확도, 우열, 품질 판단을 다루지 않는다.\*\*



---



\## 0. Scope



\- 적용 대상: Geometric Layer 구현체

\- 제외 범위:

&nbsp; - 측정 정확도 비교

&nbsp; - PASS / FAIL 판단

&nbsp; - 모델 학습, 회귀, Re-PCA

&nbsp; - 서비스/렌더링/비용



---



\## 1. Normative Requirements (MUST)



\### 1.1 Required Inputs



Geometric Layer는 아래 입력만을 전제로 한다.



\- \*\*Body Surface Representation\*\*

&nbsp; - 인체 표면을 나타내는 3D 표현

&nbsp; - 메시, implicit surface, SDF 등 형태는 자유



\- \*\*Measurement Key\*\*

&nbsp; - `{BUST, WAIST, HIP}` 중 하나



\- \*\*Units Metadata\*\*

&nbsp; - 모든 수치 입력은 `m` 단위여야 한다

&nbsp; - 단위 변환(cm → m)은 DataLoader 책임이며,

&nbsp;   Geometric Layer는 cm 입력을 받아서는 안 된다



---



\### 1.2 Forbidden Assumptions



Geometric Layer는 다음을 가정해서는 안 된다.



\- 특정 메시 토폴로지 또는 정점 인덱스의 존재

\- 특정 바디 모델(SMPL-X 등)의 사용

\- 특정 파라미터(예: β)가 항상 존재한다는 가정

\- A-pose / T-pose 강제

&nbsp; - 자세는 입력 조건일 수 있으나,

&nbsp;   \*\*측정의 의미를 바꾸는 근거가 될 수 없다\*\*



---



\## 2. Required Outputs



\### 2.1 Normative Output Schema



```json

{

&nbsp; "measurement\_key": "BUST | WAIST | HIP",

&nbsp; "circumference\_m": "number",

&nbsp; "section\_id": "string",

&nbsp; "method\_tag": "string",

&nbsp; "warnings": \["string"]

}

2.2 Output Field Semantics

measurement\_key

입력으로 받은 측정 항목 키



circumference\_m

선택된 단면에서의 폐곡선 길이

단위: meters (m)



section\_id

구현체 내부에서 선택된 단면을

재현 가능하게 식별할 수 있는 식별자



권장 구성 (SHOULD):



사용된 알고리즘 또는 전략 식별자



알고리즘 버전



핵심 파라미터 힌트



예시 (Informative):



plane\_v1\_height\_0.85



geodesic\_v2\_seed\_auto



method\_tag

단면/폐곡선 산출 방법 및

선택·결정 규칙을 기록하기 위한 태그



warnings

모호성 처리, 범위 이탈 등

주의가 필요한 상황을 기록하는 로그



3\. Semantic Preservation Rules

3.1 Common Shape Rule

모든 측정 결과는

인체 장축에 직교하는 단면 상의 폐곡선 길이여야 한다



“수평 / 수직” 좌표계 해석은

Geometric Layer 구현체에 위임된다



3.2 Selection Rules (MANDATORY)

BUST

가슴 영역 내 둘레값 최대(Max) 단면



WAIST

늑골 하단–장골능 사이 둘레값 최소(Min) 단면



HIP

둔부 및 골반 영역 내 둘레값 최대(Max) 단면



3.3 Ambiguity Handling (MUST)

후보 단면이 다수인 경우,

구현체는 결정 규칙을 반드시 고정해야 한다



해당 결정 규칙은

method\_tag 또는 warnings에 반드시 기록되어야 한다



기록에는 다음 정보가 포함되어야 한다:



어떤 기준으로 단면이 선택되었는지



왜 다른 후보가 제외되었는지(요약 수준)



결정 규칙은 특정 정점 번호나

모델 전용 규칙에 의존해서는 안 된다



4\. Unit Rules

4.1 Unit Invariance

Geometric Layer는 내부에서 단위를 변환하지 않는다



출력 circumference\_m는 항상 m 단위이다



4.2 Range Sanity (MUST WITH WARNING)

Geometric Layer는 측정 결과에 대해

물리적 범위 검사를 반드시 수행해야 한다



결과가 비현실적 범위를 벗어나는 경우:



FAIL 또는 중단 판단을 내려서는 안 된다



대신 warnings에 반드시 기록해야 한다



예시 범위 (Informative):



둘레 < 0.1 m



둘레 > 3.0 m



5\. Hard Prohibitions (MUST NOT)

PASS / FAIL 판단 출력



정확도·품질 평가



구현 간 우열 비교



Regressor, 학습, Re-PCA 언급



6\. Acceptance Criteria

Geometric Layer 구현체는 아래를 만족하면

Semantic 계약을 준수한 것으로 간주한다.



(A) {BUST, WAIST, HIP} 결과를 반환한다



(B) 결과는 단면 상 폐곡선 길이다



(C) 선택 규칙(Max / Min)을 만족한다



(D) 단위 규칙(m only)을 위반하지 않는다



(E) 선택된 단면을 재현 가능하게 식별할 수 있다



7\. Versioning Policy

MAJOR: 측정 의미 변경



MINOR: 인터페이스 확장(하위 호환)



PATCH: 문구 수정, 명확화

