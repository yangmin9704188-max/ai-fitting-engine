CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md

Contract Layer — Interface Definition

0. Scope & Authority

Layer: Contract (Interface)

Measurement: BUST / UNDERBUST (Breast Volume / Lower Chest Structural)

**CHEST는 Deprecated/Reference-only이며, 표준 키가 아니다.** 신규 구현은 BUST/UNDERBUST 이원화 체계를 사용한다.

Semantic Anchor: 
- SEMANTIC_DEFINITION_BUST_VNEXT.md
- SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md

Applies To:

bust_v0 / underbust_v0 (초기 구현)

BUST / UNDERBUST 계열 이후 버전

본 문서는 BUST/UNDERBUST의 의미론을 코드 인터페이스로 봉인한다.
계산 방법, 단면 선택, 검증 기준, 판단 로직은 포함하지 않는다.

1. Contract Role Statement

Contract Layer의 역할은 다음 하나다.

Semantic Definition에서 규정한 BUST/UNDERBUST의 의미가
코드 입·출력에서 어떻게 표현되어야 하는지를 명시한다.

Contract는:

의미를 해석하지 않는다 (Judgment 아님)

계산을 설명하지 않는다 (Geometric 아님)

결과를 평가하지 않는다 (Validation 아님)

2. Input Contract (입력 계약)
2.1 Required Inputs

표준 키 (Standard Keys):

UNDERBUST_CIRC_M: 하부 흉곽 둘레 (meters)

BUST_CIRC_M: 유방 볼륨 최대 둘레 (meters)

2.2 Bra Size Input Format (브라 사이즈 입력)

입력은 select 기반 정규화 토큰 전제를 따른다. 비표준 문자열 관용 파싱은 MVP 범위 밖이다.

포맷: "75A" (band_cm + cup)

구성:
- band_cm: 밴드 둘레 (cm 단위, 정수)
- cup: 컵 사이즈 (A, B, C, D, E, F)

예시:
- "75A": 밴드 75cm, 컵 A
- "80C": 밴드 80cm, 컵 C

2.3 Allowed Range (MVP)

band_cm: 65 ~ 90 (cm)

cup: A, B, C, D, E, F

2.4 Delta Table (컵별 Δ 값, cm)

Δ 테이블은 MVP 휴리스틱/대표값이다. Provenance: 이 값들은 초기 MVP 운영 범위에서 채택된 대표값이며, 향후 데이터 기반 보정이 가능하다.

컵 사이즈	Δ (cm)
A	10.0
B	12.5
C	15.0
D	17.5
E	20.0
F	22.5

2.5 Calculation Formula (meters)

UNDERBUST_CIRC_M = band_cm / 100

BUST_CIRC_M = UNDERBUST_CIRC_M + DELTA_CM[cup] / 100

예시:
- 입력: "75A"
- UNDERBUST_CIRC_M = 75 / 100 = 0.75 (meters)
- BUST_CIRC_M = 0.75 + 10.0 / 100 = 0.85 (meters)

2.6 Unit Assumption (필수 전제)

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
circumference_m	float | NaN	BUST 또는 UNDERBUST 둘레 (meters) 또는 Undefined
section_id	string	선택된 단면 식별자
method_tag	string	측정 방법 식별 태그
warnings	list[string]	주의 신호 목록

4. Error / Undefined / Warning (핵심 계약)
4.1 Contract Violation (포맷/범위 위반)

상황	처리
포맷 위반 (예: "75", "ABC")	ValueError 허용 또는 NaN + warnings["FORMAT_VIOLATION"]
범위 위반 (band < 65 또는 > 90)	ValueError 허용 또는 NaN + warnings["RANGE_VIOLATION"]
cup 미인식 (예: "G", "H")	ValueError 허용 또는 NaN + warnings["CUP_UNKNOWN"]

선택: ValueError 또는 NaN + warnings 중 하나를 선택해 문서에 고정한다.

자동 보정 금지: 포맷/범위 위반 시 자동으로 "가장 가까운 유효값"으로 보정하지 않는다.

4.2 Undefined (NaN)

NaN은 Error가 아니다.

NaN은 다음을 의미한다.

BUST/UNDERBUST 측정이 정의되지 않음

유방 볼륨 또는 하부 흉곽에 해당하는 폐곡선 단면이 성립하지 않음

Geometry가 의미 없는 수치를 반환하지 않기로 선택함

NaN 반환이 허용되는 대표적 경우

상체 영역에서 유방 볼륨 또는 하부 흉곽에 해당하는 단면 후보가 존재하지 않는 경우

입력 형상이 유방 볼륨 또는 하부 흉곽 구조를 표현하기에 불충분한 경우

→ 이는 Semantic Definition의 경계 표현이다.

4.3 Error (Exception)

Error는 계약 또는 시스템 위반을 의미한다.

상황	처리
verts shape 불일치	Exception 허용
필수 입력 누락	Exception 허용
내부 계산 불가능 상태	Exception 허용

Error는:

질문이 잘못되었거나

시스템이 계산을 수행할 수 없음을 의미한다.

4.4 Warning

Warning은 결과를 부정하지 않는다.

Warning은:

결과는 반환되었으나

해석 시 주의가 필요함을 의미한다.

대표적 Warning 예

UNIT_FAIL

DEGEN_FAIL

REGION_AMBIGUOUS

LARGE_BUST_UNDERBUST_DELTA (남성 큰 Δ)

Warning은:

결과 사용을 차단하지 않는다

Judgment Layer의 해석 입력으로 사용된다

5. Male-Specific Contract (남성 처리)

남성의 경우, 동일 키(UNDERBUST_CIRC_M, BUST_CIRC_M)를 사용한다.

큰 Δ(예: Δ = BUST_CIRC_M - UNDERBUST_CIRC_M > 0.05m)는:

자동 보정 금지

자동 정상화 금지

Warning 기록만 수행: warnings.append("LARGE_BUST_UNDERBUST_DELTA")

해석 책임은 Judgment Layer에 귀속

6. section_id Contract
6.1 성격

section_id는 내부 디버그 값이 아니라
재현성을 보장하기 위한 계약 식별자다.

6.2 요구사항

동일 입력 → 동일 section_id

단면 선택 기준을 식별할 수 있어야 함

문자열 형식(JSON 직렬화 허용)

7. Geometry Layer: Allowed & Forbidden
7.1 Geometry가 허용받는 행위

NaN 반환

Warning 추가

내부 계산 방식 변경 (계약 유지 조건 하)

7.2 Geometry가 금지되는 행위

포맷/범위 위반 시 자동 보정

단위 자동 보정

Undefined를 Error로 승격

Warning 은닉

의미론적 판단 수행

남성 큰 Δ 자동 정상화

8. Contract Stability Declaration

본 문서는 BUST/UNDERBUST Contract v0로 봉인된다.

Semantic Definition이 변경되지 않는 한:

Contract는 유지된다

Geometry 구현 변경은 허용된다

9. Boundary Statement

본 문서는 다음을 의도적으로 포함하지 않는다.

단면 생성 알고리즘

유방 볼륨 또는 하부 흉곽 위치 추정 방식

Validation 메트릭

품질 판정 기준

Contract는 오직 다음 질문에만 답한다.

"BUST/UNDERBUST의 의미가 코드 인터페이스에서 어떻게 나타나야 하는가?"

10. Status Declaration

BUST/UNDERBUST Contract Layer v0: Draft 완료

다음 단계: Geometric Layer v0 (BUST/UNDERBUST)
