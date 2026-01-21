[Interface Contract] Semantic → Geometric Minimal Rules v1.0
0. Scope

본 규약은 Geometric Layer 구현체가 반드시 준수해야 하는 최소 제약이다.

본 규약은 측정 정확도/우열 판단을 포함하지 않는다.

1. 입력 계약 (Inputs)
1.1 Required Inputs

Geometric Layer는 다음 입력만을 전제로 한다.

Body Surface Representation: 인체 표면을 나타내는 3D 표현(메시/implicit/sdf 등 어떤 형태든 가능)

Measurement Key: {BUST, WAIST, HIP} 중 하나

Units Metadata: 입력 스칼라/텐서/객체는 반드시 unit 메타를 포함해야 하며, Geometric 진입 시점의 단위는 m 이어야 한다.

1.2 Forbidden Assumptions (금지 가정)

특정 메시 토폴로지/정점 인덱스가 “항상 존재한다”는 가정 금지

특정 모델 파라미터(예: β)가 “항상 있다”는 가정 금지

A-pose/T-pose를 “항상 강제한다”는 가정 금지
(자세는 입력으로 주어질 수 있으나, 의미를 바꾸는 근거가 될 수 없음)

2. 출력 계약 (Outputs)
2.1 Required Output

Geometric Layer는 아래 구조의 결과를 반환해야 한다.

measurement_key: {BUST|WAIST|HIP}

circumference_m: float (meters)

정의: 선택된 단면에서의 폐곡선 길이

section_id 또는 section_param: 구현체 내부에서 “어떤 단면을 선택했는지”를 재현 가능하게 식별하는 식별자(형식 자유)

method_tag: 단면 및 폐곡선 산출 방법을 나타내는 태그(예: "plane_intersection", "geodesic_loop", "ring_sampling" 등)

단, 태그는 의미를 바꾸지 않고, 단지 방법을 기록한다.

2.2 Optional Output (권장)

debug_geometry: 선택된 단면/폐곡선의 최소 표현(예: 포인트 샘플, 폴리라인, 파라메트릭 표현 중 택1)

warnings: 경계/모호성 처리 발생 시 코드가 남기는 경고 문자열 리스트

3. 의미 보존 규칙 (Semantic Preservation)

Geometric 구현체는 반드시 아래 Semantic 규칙을 구현 결과로 만족시켜야 한다.

3.1 공통 형태 규칙

모든 {BUST, WAIST, HIP} 결과는 단면 상의 폐곡선 길이여야 한다.

“단면”은 Semantic에서 인체 장축에 직교한다.

‘수평/수직’ 좌표계 해석은 구현체 책임이며, 어떤 해석을 선택했는지 method_tag/section_id로 재현 가능해야 한다.

3.2 선택 규칙 (Selection Rule)

Geometric Layer는 Semantic의 선택 규칙을 반드시 준수해야 한다.

BUST: 정의된 가슴 영역에서 최대 둘레(Max) 선택

WAIST: 늑골 하단–장골능 사이 영역에서 최소 둘레(Min) 선택

HIP: 정의된 둔부/골반 영역에서 최대 둘레(Max) 선택

“영역(region)”을 어떻게 탐색/샘플링하는지는 구현 자유.
단, 결과가 위의 Max/Min 선택 규칙을 만족해야 한다.

3.3 모호성 처리 (Ambiguity Handling)

후보 단면이 다수인 경우, 구현체는 반드시 결정 규칙을 고정해야 하며,
해당 규칙을 warnings 또는 method_tag에 기록해야 한다.

결정 규칙은 “정점 번호”나 “특정 모델 전용 규칙”에 의존하면 안 된다.

4. 단위 규칙 (Unit Rules)
4.1 Unit Invariance

Geometric Layer는 cm 입력을 절대 받지 않는다.
(cm → m 변환은 DataLoader 책임)

Geometric Layer는 내부에서 단위를 변환하지 않는다.

출력 circumference_m는 항상 m이다.

4.2 Range Sanity (권장 강제)

모델 진입 전 또는 측정 직후, 구현체는 최소한의 물리적 범위 검사를 수행해야 한다.

예: 키/둘레가 비현실적 범위를 벗어나면 warnings에 기록(실패 처리 여부는 Geometric 내부 정책)

5. 금지 사항 (Hard Prohibitions)

결과 값에 대해 PASS/FAIL, “정확하다/부정확하다” 같은 판단(Judgment) 출력 금지

“이 방법이 더 좋다” 식의 우열 논리 금지

Regressor, 학습, Re-PCA 등 다음 단계 언급 금지(Geometric 계약 범위 외)

6. 최소 수용 기준 (Acceptance)

Geometric 구현체는 아래를 만족하면 Semantic 계약을 준수한 것으로 간주한다.

(A) {BUST, WAIST, HIP} 각각에 대해 circumference_m을 산출한다.

(B) 산출 값이 “단면 상 폐곡선 길이”라는 형태를 만족한다.

(C) 선택 규칙(Max/Min)을 만족한다.

(D) 단위 규칙(m only)을 위반하지 않는다.

(E) 어떤 단면을 선택했는지 section_id/param으로 재현 가능하게 남긴다.