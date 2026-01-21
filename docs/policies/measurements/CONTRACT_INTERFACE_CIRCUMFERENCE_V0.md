아래는 Semantic vNext를 정확히 반영하여 최초로 봉인하는 Contract Layer 정식 문서입니다.
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

이후 변경은 Semantic 변경이 선행되어야만 가능