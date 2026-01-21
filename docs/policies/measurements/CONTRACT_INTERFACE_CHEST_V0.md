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

다음 단계: Geometric Layer v0 (CHEST)