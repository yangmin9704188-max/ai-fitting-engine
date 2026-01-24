# Measurement Semantics v0 (Freeze Candidate)

본 문서는 AI Fitting Engine의 **Semantic Layer** 산출물이며, 45개 표준 Measurement Key의 의미론을 봉인한다.
- SoT(Standard Keys): docs/contract/standard_keys.md :contentReference[oaicite:1]{index=1}
- Data 상태(참고): curated_v0 v3 completeness / unit-fail trace는 "관측 사실"로만 사용한다. 
- 이후 Geometric/Validation 세션에서는 본 문서의 의미를 재해석/수정하지 않는다(Freeze).

---

## A. Semantic-Level Normative Rules (v0)

### A1. Canonical Unit / Precision
- Canonical unit: **meters (m)**, weight는 **kilograms (kg)**
- Export/Report precision target: **0.001 m (1 mm)**  
- 본 규칙은 Contract/ingestion에서 이미 강제된다는 전제이며, Semantic은 의미 정의만 제공한다. 

### A2. Soft Validity Range (Sensor-only, Non-blocking)
- 아래 범위는 **판정 임계값이 아니라 센서용**(RANGE_SUSPECTED류 warning) 권고치다.
- 범위 밖이면 자동 보정 금지(오직 warning). 

권고 범위(일반 성인 기준, 보수적으로 넓게):
- HEIGHT_M: 1.20–2.20
- WEIGHT_KG: 25–200
- HEAD/NECK/ARM/LEG 등 둘레: 0.08–1.60
- 상체 둘레(UNDERBUST/BUST/WAIST/HIP/ABDOMEN): 0.40–1.80
- 길이/높이(ARM_LEN/BACK_LEN/FRONT_CENTER/CROTCH_FB 등): 0.10–1.20
- 폭/두께(width/depth): 0.05–0.80

### A3. Pose Normalization (Semantic Principle)
기본 자세(기준 자세):
- Standing, upright, neutral spine
- 양발 체중 균등, 시선 정면
- 팔은 자연스럽게 내리고(상체 측정 방해 최소), 과도한 벌림/들기 금지
- 일반 호흡(과흡기/과호기 금지)
- 얇은 측정복 수준(두꺼운 의복/보정속옷 금지)

자세 규칙의 상세는 `docs/semantic/pose_normalization.md`로 분리한다.

### A4. Sex / Body-type Differences
- SEX는 "측정치 의미"를 바꾸지 않는다. (동일 key를 동일 의미로 사용)
- 단, **UNDERBUST** 등 일부 항목은 관측/수집 관행상 여성 중심으로 존재할 수 있음 → "결측/편향"은 자동 보정 금지, warning만 허용. 

### A5. Ideal vs Observed (Semantic Invariance)
- **Semantic은 Ideal 정의를 고정한다.** 데이터 관측 차이(측정 높이/위치/방법 차이)는 Semantic을 변경하지 않는다.
- 데이터셋에서 관측된 측정 높이/위치 차이는 "Observed note"로만 분리 기록하며, Semantic 정의는 불변이다.
- Validation/Warnings 레이어에서만 관측 차이를 기록/경고한다.

### A6. Data Coverage & Proxy Prohibition
- curated_v0 v3에서 all-null인 키도 의미론은 유지한다(표준키 사전에 포함된 이상 의미 정의는 불변).
- **자동 proxy/추정 대체 금지**: all-null 키에 대해 다른 키나 추정값으로 자동 대체하지 않는다.
- Proxy 사용 시(필수인 경우): provenance 기록 필수(Warning only, 자동 보정 금지).

### A7. Allowed DoF & Pose Constraints (SizeKorea Evidence-based)
- **band_scan_limit**: band_scan_limit_mm = 10 (±10mm)를 Semantic 규칙으로 확정. 기본은 forbidden이며, landmark 미해결 시에만 최소 범위로 허용. 핵심 둘레(BUST/WAIST/HIP 등)는 band_scan=forbidden, fixed_height=required, breath_state=neutral_mid를 기본으로 한다.
- **canonical_side = right**: SizeKorea의 오른쪽 측정 원칙을 normative rule로 명시. 좌우 평균/자동 보정 금지(필요 시 warning만). 적용 키: THIGH_CIRC_M, MIN_CALF_CIRC_M, KNEE_HEIGHT_M, ARM_LEN_M.
- **plane_clamp 정책**: plane_clamp는 proxy로만 허용되며 provenance 기록이 필수다. 도구(가로자/큰수평자/아크릴판) 기반 평면화 관측치를 반영한 proxy이며, canonical metric(진짜 신체 metric)으로 오인하면 안 된다. 폭/두께 키(CHEST_WIDTH/DEPTH, WAIST_WIDTH/DEPTH, HIP_WIDTH/DEPTH 등)에 공통 적용.
- **자동 보정 금지**: auto_pose_correction=forbidden / proxy 자동 대체 금지 / auto substitution 금지

**Evidence 문서 참조**: [SizeKorea Measurement Methods v0](../semantic/evidence/sizekorea_measurement_methods_v0.md)

---

## B. Critical: Multi-definition Groups (No Auto Substitution)

### B1. CHEST(legacy) vs UNDERBUST vs BUST
- 대표 표준키: **UNDERBUST_CIRC_M**, **BUST_CIRC_M**
- Deprecated/Reference-only: **CHEST_CIRC_M_REF** (legacy reference, 자동 대체 금지)
- 원칙: "CHEST = 표준 가슴" 표현 금지. CHEST는 역사적 산출물 참조(REF)로만 유지. 

### B2. WAIST vs NAVEL_WAIST
- 대표 표준키: **WAIST_CIRC_M**
- 파생/보조 키: **NAVEL_WAIST_CIRC_M**, NAVEL_WAIST_WIDTH_M, NAVEL_WAIST_DEPTH_M
- 승계 규칙: 서로 자동 대체 금지(배꼽선은 체형/복부지방에 민감)

### B3. HIP vs UPPER_HIP vs TOP_HIP
- 대표 표준키: **HIP_CIRC_M**
- 파생/보조 키: **UPPER_HIP_CIRC_M**, **TOP_HIP_CIRC_M**
- 승계 규칙: 자동 대체 금지(측정 높이/단면이 다르며 의복 사이징에서 의미가 다름)
- 데이터 관측: UPPER_HIP/TOP_HIP는 source에 따라 all-null이 관측됨(사실). 

### B4. THIGH vs MID_THIGH
- 대표 표준키: **THIGH_CIRC_M**
- 파생/보조 키: **MID_THIGH_CIRC_M**
- 승계 규칙: 자동 대체 금지("최대둘레" vs "중간높이 둘레")

### B5. CALF vs MIN_CALF
- 대표 표준키: **CALF_CIRC_M** (장딴지 일반/최대 의미에 가까움)
- 파생/보조 키: **MIN_CALF_CIRC_M**
- 승계 규칙: 자동 대체 금지(부츠/팬츠 핏 영향이 상이)

### B6. ANKLE family
- 표준키: **ANKLE_MAX_CIRC_M**
- 주의: MIN/instep 등 파생 개념이 존재 가능하나 v0 범위 밖(추가 금지)

### B7. SHOULDER_WIDTH family
- 표준키: **SHOULDER_WIDTH_M**
- 주의: "어깨끝–어깨끝" vs "어깨뼈(견봉)간" vs "목옆점 포함" 등 혼동이 흔함 → v0는 견봉(어깨끝점) 간 **직선 폭**으로 고정.

---

## C. Standard Key Semantic Cards (45 keys)

카드 템플릿:
- Measurement Type: circumference / length / height / width / depth / meta / weight
- Landmark: 해부학적 기준점(요약)
- Path/Plane: 수평 둘레 / 직선 거리 / 수직 높이 등
- Pose/Condition: 기준 자세/호흡/금지 조건
- Invariance/Sensitivity: 변형 민감도(지방/호흡/자세/근육)
- Confusions: 혼동 위험 1–2개
- SizeKorea Basis: "표준 측정항목" 준거(요약)

> 주: SizeKorea "측정 방법 원문"은 본 레포에 별도 인용문으로 포함되어 있지 않으므로, v0에서는 **표준 항목명 준거** 수준으로만 근거를 명시한다. (추가 인용은 별도 작업으로만 수행)

---

### META

#### HUMAN_ID
- Type: meta
- Meaning: 개인 식별(통합/조인용), 수치 의미 없음
- Confusions: (없음)
- Basis: SizeKorea 개인 ID 준거 :contentReference[oaicite:8]{index=8}

#### SEX
- Type: meta
- Meaning: 성별 라벨(M/F 등), 측정 의미를 바꾸지 않음
- Confusions: gender identity와 혼동 금지(데이터 라벨임)
- Basis: SizeKorea 성별 항목 준거 :contentReference[oaicite:9]{index=9}

#### AGE
- Type: meta
- Meaning: 만 나이 또는 조사 기준 나이(데이터 정의를 따름)
- Confusions: 연령대/출생연도와 혼동 금지
- Basis: SizeKorea 나이 항목 준거 :contentReference[oaicite:10]{index=10}

---

### GLOBAL BODY

#### HEIGHT_M
- Type: height
- Landmark: 정수리(vertex)–바닥
- Path/Plane: 수직 높이
- Pose: 기립, 맨발, 시선 정면
- Sensitivity: 자세/척추 신전, 측정 오차(머리카락)
- Confusions: KNEE_HEIGHT_M, CROTCH_HEIGHT_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#height_m)
- Pose Constraints: standing; vertical alignment
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; pose_violation=warn_only

#### WEIGHT_KG
- Type: weight
- Landmark: N/A
- Path: 체중계 측정
- Pose: 가벼운 복장, 측정 시간대 영향 가능
- Sensitivity: 수분/식사/시간대
- Confusions: BMI(파생값)와 혼동 금지
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#weight_kg)
- Pose Constraints: standing; weight evenly distributed
- Allowed DoF: (N/A - weight measurement)

---

### HEAD / NECK

#### HEAD_CIRC_M
- Type: circumference
- Landmark: 미간 위/후두 융기 포함 "머리 최대 둘레"에 해당
- Path/Plane: 수평 둘레(최대 둘레)
- Pose: 고개 중립
- Sensitivity: 모발/측정 위치
- Confusions: NECK_CIRC_M
- Basis: 머리둘레 표준항목 준거 :contentReference[oaicite:13]{index=13}

#### NECK_CIRC_M
- Type: circumference
- Landmark: 방패연골아래점
- Path/Plane: 수평 둘레
- Pose: 고개 중립, 어깨 긴장 완화, breath_state=neutral_mid
- Sensitivity: 자세/근육 긴장, 호흡 영향 약
- Confusions: HEAD_CIRC_M, CHEST 계열
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#neck_circ_m)
- Definition: 방패연골아래점을 지나는 둘레. 기준점: 방패연골아래점. 측정 방법: 피측정자의 앞에서 줄자로 방패연골아래점에서 목의 축에 직각으로 지나는 둘레를 측정한다.
- Uncertainty note: SMPL-X에서 정확한 해부학 포인트가 불명확하면 '가장 가까운 수평 단면'에 고정하되 band_scan은 최소화한다(band_scan_limit_mm = 10).
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### NECK_WIDTH_M
- Type: width
- Landmark: 목 단면의 좌우 폭(전면/측면 기준점은 Contract/Geometry에서 확정)
- Path/Plane: 수평 단면의 좌우 직선 폭
- Pose: 고개 중립
- Sensitivity: 자세/근육 긴장
- Confusions: NECK_DEPTH_M
- Basis: 목너비 표준항목 준거 :contentReference[oaicite:15]{index=15}
- Data Coverage: Observed: none in curated_v0 v3 (all-null). 자동 proxy/추정 대체 금지. Proxy 사용 시 provenance 기록 필수(Warning only). 

#### NECK_DEPTH_M
- Type: depth
- Landmark: 목 단면의 전후 두께
- Path/Plane: 수평 단면의 전후 직선 길이
- Pose: 고개 중립
- Sensitivity: 자세
- Confusions: NECK_WIDTH_M
- Basis: 목두께 표준항목 준거 :contentReference[oaicite:17]{index=17}
- Data Coverage: Observed: none in curated_v0 v3 (all-null). 자동 proxy/추정 대체 금지. Proxy 사용 시 provenance 기록 필수(Warning only). 

---

### SHOULDER

#### SHOULDER_WIDTH_M
- Type: width
- Landmark: 좌/우 견봉점(acromion, "어깨끝점") 간
- Path/Plane: 수평에 가까운 직선 폭(좌우)
- Pose: 기립, 팔 자연스럽게 내림(들거나 과도한 벌림 금지), 견갑 중립(과도한 말림/후인 금지) 상태가 의미 보존 전제, 위반 시 warning
- Sensitivity: 자세(어깨 말림/펴짐), 근육 긴장
- Confusions: CHEST_WIDTH_M, 등/어깨둘레(비표준)
- Basis: 어깨너비 표준항목 준거 :contentReference[oaicite:19]{index=19}

---

### CHEST / BUST / UNDERBUST

#### CHEST_CIRC_M_REF (Reference-only)
- Type: circumference
- Landmark: "가슴둘레" 레거시 참조(흉곽/가슴높이 단면)
- Path/Plane: 수평 둘레(legacy)
- Pose: 기립, 자연 호흡
- Sensitivity: 호흡/자세/유방 볼륨(개인차)
- Confusions: BUST_CIRC_M, UNDERBUST_CIRC_M
- Rule: **표준 대체 금지**. 오직 legacy 비교/연구 참조로만 사용.
- Basis: 표준키 사전의 REF 정의 :contentReference[oaicite:20]{index=20}

#### BUST_CIRC_M
- Type: circumference
- Landmark: 유방의 가장 돌출된 지점("젖가슴 최대")을 지나는 수평 단면
- Path/Plane: 수평 둘레(최대 둘레)
- Pose: 기립, 자연 호흡(과흡기/과호기 금지), breath_state=neutral_mid
- Sensitivity: 호흡/브라 착용/측정 위치, 체형·연령 영향 큼
- Confusions: CHEST_CIRC_M_REF, UNDERBUST_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#bust_circ_m)
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### UNDERBUST_CIRC_M
- Type: circumference
- Landmark: 유방 바로 아래의 흉곽 단면(밑가슴)
- Path/Plane: 수평 둘레(흉곽 anchor)
- Pose: 기립, 자연 호흡, breath_state=neutral_mid
- Sensitivity: 호흡 영향(상체 둘레 중 상대적으로 큼), 자세
- Confusions: WAIST_CIRC_M, CHEST_CIRC_M_REF
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#underbust_circ_m)
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### UNDERBUST_WIDTH_M
- Type: width
- Landmark: 밑가슴 단면의 좌우 폭
- Path/Plane: 수평 단면 좌우 직선 폭
- Pose: 기립, 팔 내림
- Sensitivity: 자세/측정 위치
- Confusions: UNDERBUST_DEPTH_M, CHEST_WIDTH_M
- Basis: 표준키 사전 준거 :contentReference[oaicite:23]{index=23}
- Data note(관측): curated_v0 v3에서 all-null 관측(사실). 

#### UNDERBUST_DEPTH_M
- Type: depth
- Landmark: 밑가슴 단면의 전후 두께
- Path/Plane: 수평 단면 전후 직선 길이
- Pose: 기립
- Sensitivity: 자세/호흡
- Confusions: UNDERBUST_WIDTH_M, CHEST_DEPTH_M
- Basis: 표준키 사전 준거 :contentReference[oaicite:25]{index=25}
- Data note(관측): curated_v0 v3에서 all-null 관측(사실). 

#### CHEST_WIDTH_M
- Type: width
- Landmark: 가슴(흉곽/가슴높이) 단면의 좌우 폭
- Path/Plane: 수평 단면 좌우 직선 폭
- Pose: 기립, 팔 내림, breath_state=neutral_mid
- Sensitivity: 자세(어깨 말림), 호흡
- Confusions: SHOULDER_WIDTH_M, UNDERBUST_WIDTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#chest_width_m)
- Pose Constraints: breath_state=neutral_mid; arms_down_required
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

#### CHEST_DEPTH_M
- Type: depth
- Landmark: 가슴 단면의 전후 두께
- Path/Plane: 수평 단면 전후 직선 길이
- Pose: 기립, breath_state=neutral_mid
- Sensitivity: 호흡/자세
- Confusions: UNDERBUST_DEPTH_M, WAIST_DEPTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#chest_depth_m)
- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

---

### WAIST / ABDOMEN

#### WAIST_CIRC_M
- Type: circumference
- Landmark: 허리 기준선(일반적으로 몸통의 가장 잘록한 부위)
- Path/Plane: 수평 둘레
- Pose: 기립, 자연 호흡, breath_state=neutral_mid
- Sensitivity: 호흡/자세/복부 힘주기
- Confusions: NAVEL_WAIST_CIRC_M, ABDOMEN_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#waist_circ_m)
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### NAVEL_WAIST_CIRC_M
- Type: circumference
- Landmark: 배꼽 높이의 몸통 단면
- Path/Plane: 수평 둘레
- Pose: 기립, breath_state=neutral_mid
- Sensitivity: 복부 지방/자세 영향 큼
- Confusions: WAIST_CIRC_M, ABDOMEN_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#navel_waist_circ_m)
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### ABDOMEN_CIRC_M
- Type: circumference
- Landmark: 복부에서 가장 돌출된 부위를 지나는 수평 둘레
- Path/Plane: 수평 둘레
- Pose: 기립, breath_state=neutral_mid
- Sensitivity: 복부 힘주기/자세/호흡
- Confusions: NAVEL_WAIST_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#abdomen_circ_m)
- Observed note: 데이터셋에서 관측된 측정 높이 차이는 Validation/Warnings로만 기록되며, Semantic 정의는 불변이다.
- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid(when specified); pose_violation=warn_only; substitution=forbidden

#### WAIST_WIDTH_M
- Type: width
- Landmark: 허리 단면 좌우 폭
- Path/Plane: 수평 단면 좌우 직선 폭
- Pose: 기립, breath_state=neutral_mid
- Sensitivity: 자세
- Confusions: WAIST_DEPTH_M, NAVEL_WAIST_WIDTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#waist_width_m)
- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

#### WAIST_DEPTH_M
- Type: depth
- Landmark: 허리 단면 전후 두께
- Path/Plane: 수평 단면 전후 직선 길이
- Pose: 기립, breath_state=neutral_mid
- Sensitivity: 자세/복부 힘주기
- Confusions: WAIST_WIDTH_M, NAVEL_WAIST_DEPTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#waist_depth_m)
- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

#### NAVEL_WAIST_WIDTH_M
- Type: width
- Landmark: 배꼽 높이 단면 좌우 폭
- Path/Plane: 수평 단면 좌우 직선 폭
- Pose: 기립
- Sensitivity: 복부/자세 영향 큼
- Confusions: NAVEL_WAIST_DEPTH_M, WAIST_WIDTH_M
- Basis: 표준키 사전 준거 :contentReference[oaicite:34]{index=34}

#### NAVEL_WAIST_DEPTH_M
- Type: depth
- Landmark: 배꼽 높이 단면 전후 두께
- Path/Plane: 수평 단면 전후 직선 길이
- Pose: 기립
- Sensitivity: 복부/자세 영향 큼
- Confusions: NAVEL_WAIST_WIDTH_M, WAIST_DEPTH_M
- Basis: 표준키 사전 준거 :contentReference[oaicite:35]{index=35}

---

### HIP

#### HIP_CIRC_M
- Type: circumference
- Landmark: 둔부의 최대 돌출부를 지나는 수평 단면("엉덩이 최대")
- Path/Plane: 수평 둘레(최대 둘레)
- Pose: 기립, 다리 과도한 벌림 금지
- Sensitivity: 자세/골반 기울기
- Confusions: UPPER_HIP_CIRC_M, TOP_HIP_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#hip_circ_m)
- Pose Constraints: standing; tape horizontal
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; pose_violation=warn_only; substitution=forbidden

#### HIP_WIDTH_M
- Type: width
- Landmark: 힙 단면 좌우 폭
- Path/Plane: 수평 단면 좌우 직선 폭
- Pose: 기립
- Sensitivity: 자세
- Confusions: HIP_DEPTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#hip_width_m)
- Pose Constraints: standing
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

#### HIP_DEPTH_M
- Type: depth
- Landmark: 힙 단면 전후 두께
- Path/Plane: 수평 단면 전후 직선 길이
- Pose: 기립
- Sensitivity: 자세
- Confusions: HIP_WIDTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#hip_depth_m)
- Pose Constraints: standing
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

#### UPPER_HIP_CIRC_M
- Type: circumference
- Landmark: HIP보다 상단(허리-힙 사이) 단면 둘레("upper-hip")
- Path/Plane: 수평 둘레
- Pose: 기립
- Sensitivity: 측정 높이 정의에 민감
- Confusions: HIP_CIRC_M, TOP_HIP_CIRC_M
- Basis: Upper-hip둘레 표준항목 준거 :contentReference[oaicite:39]{index=39}
- Data note(관측): curated_v0 v3에서 all-null이 관측됨(사실). 

#### TOP_HIP_CIRC_M
- Type: circumference
- Landmark: hip 계열 중 가장 상단/상부 기준("top-hip")
- Path/Plane: 수평 둘레
- Pose: 기립
- Sensitivity: 측정 높이 정의에 매우 민감
- Confusions: UPPER_HIP_CIRC_M, WAIST_CIRC_M
- Basis: Top-hip둘레 표준항목 준거 :contentReference[oaicite:41]{index=41}
- Data note(관측): curated_v0 v3에서 all-null이 관측됨(사실). 

---

### ARM / UPPER LIMB

#### UPPER_ARM_CIRC_M
- Type: circumference
- Landmark: 상완(위팔) 기준 위치의 둘레(보통 이두근 최대에 가까움)
- Path/Plane: 팔 축에 수직인 단면 둘레
- Pose: 팔 자연스럽게 내림(힘주기 금지)
- Sensitivity: 근육 수축/자세에 민감
- Confusions: ELBOW_CIRC_M, WRIST_CIRC_M
- Basis: 위팔둘레 표준항목 준거 :contentReference[oaicite:43]{index=43}

#### ELBOW_CIRC_M
- Type: circumference
- Landmark: 팔꿈치(주두/상완-전완 관절부) 기준 둘레
- Path/Plane: 관절부 단면 둘레
- Pose: 팔 편 상태(과굴곡 금지)
- Sensitivity: 굴곡 각도
- Confusions: FOREARM(비표준), UPPER_ARM_CIRC_M
- Basis: 팔꿈치둘레 표준항목 준거 :contentReference[oaicite:44]{index=44}

#### WRIST_CIRC_M
- Type: circumference
- Landmark: 요골경상돌기/척골경상돌기 주변 손목 최소에 가까운 둘레
- Path/Plane: 손목 단면 둘레
- Pose: 손목 중립
- Sensitivity: 측정 위치(최소/최대) 차이
- Confusions: FOREARM/hand(비표준)
- Basis: 손목둘레 표준항목 준거 :contentReference[oaicite:45]{index=45}

#### ARM_LEN_M
- Type: length
- Landmark: 어깨점(견봉)–손목점(또는 측정 표준의 손목 기준점)
- Path/Plane: 체표길이(surface path)
- Pose: 팔 자연스럽게 내림/약간 펼침(표준에 따름), right-side measurement
- Sensitivity: 팔 각도/어깨 자세
- Confusions: BACK_LEN_M, SHOULDER_WIDTH_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#arm_len_m)
- Pose Constraints: right-side measurement
- Allowed DoF: path_type=surface_path(체표길이); canonical_side=right; symmetry_avg=forbidden; pose_violation=warn_only

---

### TORSO LENGTHS

#### BACK_LEN_M
- Type: length
- Landmark: 목뒤점(경추점)–허리/등 기준점(측정 표준 준거)
- Path/Plane: 등 중심선 따라 길이(또는 직선; 표준에 따름)
- Pose: 기립, 등 펴기 과도 금지
- Sensitivity: 자세/척추 굴곡
- Confusions: FRONT_CENTER_LEN_M, HEIGHT_M
- Basis: 등길이 표준항목 준거 :contentReference[oaicite:47]{index=47}

#### FRONT_CENTER_LEN_M
- Type: length
- Landmark: 목앞점(흉골상절흔)–전면 중심선 하단 기준점(표준 준거)
- Path/Plane: 앞 중심선 길이
- Pose: 기립
- Sensitivity: 자세/가슴 형태
- Confusions: BACK_LEN_M, CROTCH_FB_LEN_M
- Basis: 앞중심길이 표준항목 준거 :contentReference[oaicite:48]{index=48}

#### CROTCH_FB_LEN_M
- Type: length
- Landmark: 앞허리 기준점–샅(회음부)–뒤허리 기준점의 앞뒤 길이("샅앞뒤길이")
- Path/Plane: 인체 표면 경로 길이(앞→샅→뒤)
- Pose: 기립, 다리 과도 벌림 금지
- Sensitivity: 골반 기울기/자세에 매우 민감
- Confusions: CROTCH_HEIGHT_M, HIP_CIRC_M
- Basis: 샅앞뒤길이 표준항목 준거 :contentReference[oaicite:49]{index=49}

---

### LOWER LIMB HEIGHTS

#### CROTCH_HEIGHT_M
- Type: height
- Landmark: 샅점(회음부 최저점 근처)–바닥
- Path/Plane: 수직 높이
- Pose: 기립, strict_standing, knee_flexion=forbidden
- Sensitivity: 다리 벌림/골반 기울기
- Confusions: KNEE_HEIGHT_M, HEIGHT_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#crotch_height_m)
- Pose Constraints: strict_standing; knee_flexion=forbidden; board_level=required(아크릴판 수평)
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; pose_violation=warn_only

#### KNEE_HEIGHT_M
- Type: height
- Landmark: 무릎 기준점–바닥
- Path/Plane: 수직 높이
- Pose: 기립, strict_standing, knee_flexion=forbidden, right-side measurement
- Sensitivity: 무릎 굴곡
- Confusions: CROTCH_HEIGHT_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#knee_height_m)
- Pose Constraints: strict_standing; knee_flexion=forbidden; right-side measurement
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; canonical_side=right; pose_violation=warn_only

---

### LOWER LIMB CIRCUMFERENCES

#### THIGH_CIRC_M
- Type: circumference
- Landmark: 허벅지 기준(대퇴) 둘레(보통 대퇴 최대에 가까움)
- Path/Plane: 대퇴 축에 수직 단면 둘레
- Pose: 기립, right-side measurement
- Sensitivity: 다리 벌림/근육 수축
- Confusions: MID_THIGH_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#thigh_circ_m)
- Pose Constraints: standing; right-side measurement
- Allowed DoF: canonical_side=right; symmetry_avg=forbidden; fixed_height=required; band_scan=forbidden; pose_violation=warn_only

#### MID_THIGH_CIRC_M
- Type: circumference
- Landmark: 대퇴 "중간 높이" 단면 둘레
- Path/Plane: 수직 위치를 정의한 단면 둘레(중간)
- Pose: 기립
- Sensitivity: "중간" 정의(높이) 민감
- Confusions: THIGH_CIRC_M
- Basis: 넙다리중간둘레 표준항목 준거 :contentReference[oaicite:53]{index=53}

#### KNEE_CIRC_M
- Type: circumference
- Landmark: 무릎 관절부 둘레
- Path/Plane: 관절부 단면 둘레
- Pose: 무릎 편 상태 권고(과굴곡 금지)
- Sensitivity: 굴곡 각도
- Confusions: BELOW_KNEE_CIRC_M
- Basis: 무릎둘레 표준항목 준거 :contentReference[oaicite:54]{index=54}

#### BELOW_KNEE_CIRC_M
- Type: circumference
- Landmark: 무릎 바로 아래(하퇴 상부) 단면 둘레
- Path/Plane: 하퇴 축에 수직 단면 둘레
- Pose: 기립
- Sensitivity: 측정 높이 정의 민감
- Confusions: KNEE_CIRC_M, CALF_CIRC_M
- Basis: 무릎아래둘레 표준항목 준거 :contentReference[oaicite:55]{index=55}

#### CALF_CIRC_M
- Type: circumference
- Landmark: 장딴지(하퇴) 둘레(일반적으로 최대에 가까움)
- Path/Plane: 하퇴 축에 수직 단면 둘레
- Pose: 기립
- Sensitivity: 근육 긴장/자세
- Confusions: MIN_CALF_CIRC_M
- Basis: 장딴지둘레 표준항목 준거 :contentReference[oaicite:56]{index=56}

#### MIN_CALF_CIRC_M
- Type: circumference
- Landmark: 복사뼈를 포함하지 않는 발목 위 종아리 최소 둘레
- Path/Plane: 하퇴 축에 수직 단면 둘레(최소, 복사뼈 제외)
- Pose: 기립, right-side measurement
- Sensitivity: 측정 위치(최소점 탐색) 민감
- Confusions: ANKLE_MAX_CIRC_M, CALF_CIRC_M
- Basis: [SizeKorea Evidence](../semantic/evidence/sizekorea_measurement_methods_v0.md#min_calf_circ_m)
- Pose Constraints: standing; right-side measurement
- Allowed DoF: canonical_side=right; symmetry_avg=forbidden; fixed_height=required; band_scan=forbidden; pose_violation=warn_only

#### ANKLE_MAX_CIRC_M
- Type: circumference
- Landmark: malleolus(복사뼈)를 포함한 발목 단면 최대 둘레
- Path/Plane: 발목 단면 둘레(최대, 복사뼈 포함)
- Pose: 기립, 발목 중립
- Sensitivity: 측정 위치(최대/최소) 혼동
- Confusions: MIN_CALF_CIRC_M, (비표준 ankle_min)
- Basis: 발목최대둘레 표준항목 준거 :contentReference[oaicite:58]{index=58}

---

## D. Non-Standard Observations (Out-of-Contract; No action in v0)
curated_v0 v3 completeness 관측 중 일부 컬럼(BICEPS_CIRC_M, FOREARM_CIRC_M 등)이 표준키 사전(45 keys)에 존재하지 않는 것으로 보일 수 있다.
- v0 봉인 범위에서는 **표준키 사전(45개)만** 의미론을 가진다.
- 비표준 컬럼은 Contract 확장 없이 "무시/비표준"으로 처리한다(자동 편입 금지). 

---

## Freeze Declaration (Semantic v0)

본 문서(Measurement Semantics v0)는 **2026-01-24 (Asia/Seoul)** 기준으로 봉인된다.
1) 본 문서는 45개 표준 Measurement Key의 **Ideal 의미론 정의**를 고정한다.  
2) 데이터 소스별 측정 관행/분포/결측(Observed)은 **Semantic 정의를 변경하지 않으며**, Validation/Warnings에서만 흡수한다.  
3) 유사 키 간 **자동 대체/승계/보정은 금지**한다(No Auto Substitution).  
4) all-null 등 데이터 커버리지가 부족한 키도 의미론은 유지하되, **자동 Proxy/추정 대체는 금지**한다(Proxy 사용 시 provenance 기록 필수).  
5) 이후 Geometric/Validation 구현에서 본 의미론을 재해석하거나 수정하는 행위는 금지하며, 변경이 필요하면 **Semantic v1**로 새 문서/새 태그로만 진행한다. 
