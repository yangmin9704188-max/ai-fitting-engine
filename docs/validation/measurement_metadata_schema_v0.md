# Measurement Metadata Schema v0

본 문서는 Geometric 구현이 산출한 각 standard_key 측정 결과에 함께 붙는 **metadata 계약(스키마)**을 정의한다.

---

## A. 목적/범위

이 스키마는 Geometric이 산출한 각 standard_key 측정 결과에 함께 붙는 metadata 계약임을 명시한다.

**핵심 원칙**: Semantic 수정 금지 원칙 하에서 문제는 metadata/provenance로 흡수한다. Geometric/Validation 이슈가 발생해도 Semantic을 수정하지 않고, 대신 metadata와 provenance를 통해 사실을 기록하고 warning으로 신호화한다.

---

## B. Top-level JSON 형태

단일 측정 레코드 예시:

```json
{
  "standard_key": "BUST_CIRC_M",
  "value_m": 0.92,
  "unit": "m",
  "precision": 0.001,
  "pose": {
    "breath_state": "neutral_mid",
    "arms_down": true,
    "strict_standing": true,
    "knee_flexion_forbidden": false
  },
  "method": {
    "path_type": "closed_curve",
    "metric_type": "circumference",
    "canonical_side": "right",
    "landmark_confidence": "high",
    "landmark_resolution": "direct",
    "fixed_height_required": true,
    "fixed_cross_section_required": false
  },
  "search": {
    "band_scan_used": false,
    "band_scan_limit_mm": 10,
    "min_max_search_used": false
  },
  "proxy": {
    "proxy_used": false,
    "proxy_type": null,
    "proxy_tool": null
  },
  "provenance": {
    "source": "sizekorea",
    "evidence_ref": "docs/semantic/evidence/sizekorea_measurement_methods_v0.md#bust_circ_m"
  },
  "warnings": [],
  "version": {
    "semantic_tag": "semantic-v0",
    "schema_version": "metadata-schema-v0"
  }
}
```

---

## C. 필수 필드(Required)와 선택 필드(Optional)

### Required Fields

다음 필드는 모든 측정 레코드에 반드시 포함되어야 한다:

- **standard_key** (string): 표준 키 이름 (예: "BUST_CIRC_M", "HEIGHT_M")
- **unit** (string): 단위. 길이/둘레/폭/두께/높이는 "m", 무게는 "kg"로 고정
- **precision** (number): 정밀도. 기본값 0.001 (1mm)
- **value** + **value_unit_key**: 값과 단위 키 중 하나로 통일
  - 예: `value_m` (number) 또는 `value_kg` (number)
- **method.path_type** (enum): 경로 타입
  - `"straight_line"`: 직선 거리
  - `"surface_path"`: 체표 경로 (예: ARM_LEN_M)
  - `"closed_curve"`: 닫힌 곡선 (둘레 계열)
- **method.metric_type** (enum): 측정 타입
  - `"circumference"`: 둘레
  - `"width"`: 폭
  - `"depth"`: 두께
  - `"height"`: 높이
  - `"length"`: 길이
  - `"mass"`: 무게
- **provenance.source** (enum): 데이터 소스
  - `"sizekorea"`: SizeKorea 데이터셋
- **warnings** (array of strings): 경고 메시지 배열 (빈 배열 허용)
- **version.semantic_tag** (string): Semantic 버전 태그 (예: "semantic-v0")
- **version.schema_version** (string): 스키마 버전 (예: "metadata-schema-v0")

### Optional Fields (강력 권장)

다음 필드는 선택이지만, 가능한 경우 반드시 포함하는 것을 강력 권장한다:

#### method
- **method.canonical_side** (enum): 측정 측면
  - `"right"`: 우측 (THIGH_CIRC_M, MIN_CALF_CIRC_M, KNEE_HEIGHT_M, ARM_LEN_M 등)
  - `"left"`: 좌측
  - `"bilateral"`: 양측
- **method.landmark_confidence** (enum): 랜드마크 신뢰도
  - `"high"`: 높음
  - `"medium"`: 중간
  - `"low"`: 낮음
- **method.landmark_resolution** (enum): 랜드마크 해결 방법
  - `"direct"`: 직접 매칭
  - `"nearest_cross_section_fallback"`: 가장 가까운 단면 폴백
- **method.fixed_height_required** (bool): 고정 높이 필수 여부
- **method.fixed_cross_section_required** (bool): 고정 단면 필수 여부

#### search
- **search.band_scan_used** (bool): band_scan 사용 여부
- **search.band_scan_limit_mm** (int): band_scan 제한 (semantic-v0 정책 상 10)
- **search.min_max_search_used** (bool): 최소/최대 탐색 사용 여부

#### proxy
- **proxy.proxy_used** (bool): proxy 사용 여부
- **proxy.proxy_type** (enum): proxy 타입
  - `"plane_clamp"`: 평면화 도구 사용
  - `"other"`: 기타
- **proxy.proxy_tool** (string): proxy 도구 (예: "acrylic_board", "caliper", "ruler")

#### pose
- **pose.breath_state** (enum): 호흡 상태
  - `"neutral_mid"`: 중간 호흡
  - `"unknown"`: 알 수 없음
- **pose.arms_down** (bool | "unknown"): 팔 내림 여부
- **pose.strict_standing** (bool | "unknown"): 엄격한 기립 자세
- **pose.knee_flexion_forbidden** (bool | "unknown"): 무릎 굴곡 금지 여부

#### debug (Optional, for failure analysis)
다음 필드는 실패 원인 분석을 위해 선택적으로 포함할 수 있다:

##### cross_section (cross-section 탐색 관련)
- **debug.cross_section.target_height_ratio** (float): 목표 높이 비율 (0.0~1.0, y_min 기준)
- **debug.cross_section.target_z_m** (float): 목표 높이 (meters, 절대값)
- **debug.cross_section.search_window_mm** (float): 탐색 윈도우 크기 (mm)
- **debug.cross_section.candidates_count** (int): 후보 단면 개수
- **debug.cross_section.reason_not_found** (enum): 단면을 찾지 못한 이유
  - `"empty_slice"`: tolerance 내 정점이 3개 미만
  - `"invalid_axis"`: body axis가 유효하지 않음
  - `"out_of_bounds"`: target_height가 범위를 벗어남
  - `"degenerate_geometry"`: 기하학적으로 퇴화된 단면

##### body_axis (body axis 유효성 관련)
- **debug.body_axis.length_m** (float): body axis 길이 (meters)
- **debug.body_axis.valid** (bool): body axis가 유효한지 여부
- **debug.body_axis.reason_invalid** (string): body axis가 유효하지 않은 이유
  - `"too_short"`: y_range < 1e-6m
  - `"degenerate"`: y_min == y_max

##### landmark_regions (landmark 영역 탐색 관련)
- **debug.landmark_regions.required** (array of strings): 필요한 landmark 영역 목록
  - 예: `["shoulder_region", "wrist_region"]`
- **debug.landmark_regions.found** (array of strings): 찾은 landmark 영역 목록
- **debug.landmark_regions.reason_not_found** (string): landmark 영역을 찾지 못한 이유
  - `"no_vertices_in_region"`: 해당 영역에 정점이 없음
  - `"region_out_of_bounds"`: 영역이 메쉬 범위를 벗어남

---

## D. 키 유형별 최소 세트 가이드

### Circumference 계열 (BUST_CIRC_M, WAIST_CIRC_M, HIP_CIRC_M 등)
- `method.path_type`: `"closed_curve"`
- `method.metric_type`: `"circumference"`
- `method.fixed_height_required`: `true`
- `search.band_scan_used`: `false` (기본)
- `search.band_scan_limit_mm`: `10` (semantic-v0 정책)
- `pose.breath_state`: `"neutral_mid"` (가능시)

### Width/Depth 계열 (CHEST_WIDTH_M, WAIST_WIDTH_M, HIP_WIDTH_M, CHEST_DEPTH_M 등)
- `method.path_type`: `"straight_line"`
- `method.metric_type`: `"width"` 또는 `"depth"`
- `method.fixed_cross_section_required`: `true`
- `proxy.proxy_used`: `true` (plane_clamp 사용시)
- `proxy.proxy_type`: `"plane_clamp"` (사용시)
- `proxy.proxy_tool`: 도구 이름 (예: "acrylic_board", "caliper")
- `pose.breath_state`: `"neutral_mid"` (가능시)

### ARM_LEN_M
- `method.path_type`: `"surface_path"`
- `method.metric_type`: `"length"`
- `method.canonical_side`: `"right"`

### Vertical Height 계열 (CROTCH_HEIGHT_M, KNEE_HEIGHT_M, HEIGHT_M)
- `method.path_type`: `"straight_line"`
- `method.metric_type`: `"height"`
- `pose.strict_standing`: `true`
- `pose.knee_flexion_forbidden`: `true`
- `method.canonical_side`: `"right"` (KNEE_HEIGHT_M의 경우)

---

## E. "금지된 자동화" 규칙 명문화

다음 자동화는 **금지**되며, 명시적으로 기록되어야 한다:

### 1. auto_substitution 금지
- 유사 키 간 자동 대체/승계 금지
- 예: WAIST_CIRC_M이 없어도 NAVEL_WAIST_CIRC_M으로 자동 대체 금지
- 필요시 warning으로만 기록

### 2. auto_pose_correction 금지
- 자세 위반 시 자동 보정 금지
- `pose_violation`은 warning으로만 기록
- `auto_pose_correction` 필드는 존재하지 않음 (금지이므로)

### 3. proxy 자동 대체 금지
- all-null 키에 대해 다른 키나 추정값으로 자동 대체 금지
- `proxy.proxy_used`는 명시적으로 `true`일 때만 설정
- proxy 사용 시 반드시 `proxy.proxy_type`, `proxy.proxy_tool`, `provenance` 기록 필수

### 4. 좌우 평균/자동 보정 금지
- `canonical_side=right`인 키에 대해 좌우 평균 계산 금지
- 필요시 warning으로만 기록

---

## F. 참조 문서

- Semantic 정의: `docs/semantic/measurement_semantics_v0.md`
- SizeKorea Evidence: `docs/semantic/evidence/sizekorea_measurement_methods_v0.md`
- Pose Normalization: `docs/semantic/pose_normalization.md`
