Semantic Layer — Final Definition (vNext)

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
차기 사이클에서만 설계 선택이 발생할 수 있다.