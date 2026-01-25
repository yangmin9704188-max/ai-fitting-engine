# Geometric v0 Facts-Only Summary (Round 17 - Valid 10 Expanded)

## 1. 실행 조건

- **샘플 수**: 15
- **입력 데이터셋**: `verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz`
- **Git SHA**: `4c1d4493ea6dcd2217a6b2ae773e6a09b5b51e04`
- **실행 일시**: 2026-01-25T16:10:58.521945

### 1.1 S0 Dataset Scale Statistics

- **HEIGHT_M**: min=1.655m, median=1.758m, max=1.841m
- **BUST_CIRC_M**: median=0.720m, BUST/height ratio=0.409
- **WAIST_CIRC_M**: median=0.464m, WAIST/height ratio=0.264
- **HIP_CIRC_M**: median=0.598m, HIP/height ratio=0.340

## 2. Key별 요약 (Valid Cases Only - DoD 평가 기준)

**Valid Cases**: normal_* + varied_* (10개)

| Key | Valid Total | Valid NaN | Valid NaN Rate | Min | Median | Max | DoD (<=40%) |
|-----|-------------|-----------|----------------|-----|--------|-----|-------------|
| NECK_CIRC_M | 10 | 0 | 0.00% | 0.2936 | 0.3864 | 0.5759 | N/A |
| BUST_CIRC_M | 10 | 0 | 0.00% | 0.5493 | 0.7200 | 1.1632 | N/A |
| UNDERBUST_CIRC_M | 10 | 0 | 0.00% | 0.5493 | 0.7200 | 1.1632 | N/A |
| WAIST_CIRC_M | 10 | 0 | 0.00% | 0.4017 | 0.4638 | 0.7767 | N/A |
| HIP_CIRC_M | 10 | 0 | 0.00% | 0.4899 | 0.5980 | 0.9605 | N/A |
| THIGH_CIRC_M | 10 | 0 | 0.00% | 0.6044 | 0.7903 | 1.1750 | N/A |
| MIN_CALF_CIRC_M | 10 | 0 | 0.00% | 0.4617 | 0.7269 | 0.8275 | N/A |
| CHEST_WIDTH_M | 10 | 0 | 0.00% | 0.1889 | 0.2486 | 0.3653 | N/A |
| CHEST_DEPTH_M | 10 | 0 | 0.00% | 0.1893 | 0.2544 | 0.3747 | N/A |
| WAIST_WIDTH_M | 10 | 0 | 0.00% | 0.1282 | 0.1462 | 0.2434 | ✅ PASS |
| WAIST_DEPTH_M | 10 | 0 | 0.00% | 0.1311 | 0.1482 | 0.2437 | ✅ PASS |
| HIP_WIDTH_M | 10 | 0 | 0.00% | 0.1569 | 0.1912 | 0.3107 | ✅ PASS |
| HIP_DEPTH_M | 10 | 0 | 0.00% | 0.1619 | 0.1900 | 0.3071 | ✅ PASS |
| HEIGHT_M | 10 | 0 | 0.00% | 1.6554 | 1.7582 | 1.8407 | N/A |
| CROTCH_HEIGHT_M | 10 | 0 | 0.00% | 0.7449 | 0.7912 | 0.8283 | N/A |
| KNEE_HEIGHT_M | 10 | 0 | 0.00% | 0.4139 | 0.4395 | 0.4602 | N/A |
| ARM_LEN_M | 10 | 10 | 100.00% | N/A | N/A | N/A | N/A |

## 2.1 Expected Fail Cases (사실 기록)

**Expected Fail Cases**: degenerate_y_range, minimal_vertices, scale_error_suspected, random_noise_seed123, tall_thin (5개)

| Key | Expected Fail Total | Expected Fail NaN | Expected Fail NaN Rate |
|-----|---------------------|-------------------|------------------------|
| NECK_CIRC_M | 5 | 4 | 80.00% |
| BUST_CIRC_M | 5 | 3 | 60.00% |
| UNDERBUST_CIRC_M | 5 | 3 | 60.00% |
| WAIST_CIRC_M | 5 | 3 | 60.00% |
| HIP_CIRC_M | 5 | 4 | 80.00% |
| THIGH_CIRC_M | 5 | 4 | 80.00% |
| MIN_CALF_CIRC_M | 5 | 4 | 80.00% |
| CHEST_WIDTH_M | 5 | 2 | 40.00% |
| CHEST_DEPTH_M | 5 | 2 | 40.00% |
| WAIST_WIDTH_M | 5 | 3 | 60.00% |
| WAIST_DEPTH_M | 5 | 3 | 60.00% |
| HIP_WIDTH_M | 5 | 4 | 80.00% |
| HIP_DEPTH_M | 5 | 4 | 80.00% |
| HEIGHT_M | 5 | 0 | 0.00% |
| CROTCH_HEIGHT_M | 5 | 0 | 0.00% |
| KNEE_HEIGHT_M | 5 | 0 | 0.00% |
| ARM_LEN_M | 5 | 3 | 60.00% |

## 3. Warnings Top 리스트

### 3.1 전체 Warnings Top 10

| Warning Type | Count |
|--------------|-------|
| MIN_SEARCH_USED | 10 |
| CROTCH_ESTIMATED | 10 |
| KNEE_ESTIMATED | 10 |
| LANDMARK_REGIONS_NOT_FOUND | 10 |

### 3.2 Key별 Warnings Top 5

**MIN_CALF_CIRC_M**:
- `MIN_SEARCH_USED`: 10

**CROTCH_HEIGHT_M**:
- `CROTCH_ESTIMATED`: 10

**KNEE_HEIGHT_M**:
- `KNEE_ESTIMATED`: 10

**ARM_LEN_M**:
- `LANDMARK_REGIONS_NOT_FOUND`: 10

## 4. Proxy/Band Scan/Side 기록 통계

### 4.1 Proxy 사용

| Key | Proxy Used Count | Proxy Types |
|-----|------------------|-------------|
| NECK_CIRC_M | 0 | N/A |
| BUST_CIRC_M | 0 | N/A |
| UNDERBUST_CIRC_M | 0 | N/A |
| WAIST_CIRC_M | 0 | N/A |
| HIP_CIRC_M | 0 | N/A |
| THIGH_CIRC_M | 0 | N/A |
| MIN_CALF_CIRC_M | 0 | N/A |
| CHEST_WIDTH_M | 0 | N/A |
| CHEST_DEPTH_M | 0 | N/A |
| WAIST_WIDTH_M | 0 | N/A |
| WAIST_DEPTH_M | 0 | N/A |
| HIP_WIDTH_M | 0 | N/A |
| HIP_DEPTH_M | 0 | N/A |
| HEIGHT_M | 0 | N/A |
| CROTCH_HEIGHT_M | 0 | N/A |
| KNEE_HEIGHT_M | 0 | N/A |
| ARM_LEN_M | 0 | N/A |

### 4.2 Band Scan 사용

| Key | Band Scan Used Count | Band Scan Limits |
|-----|----------------------|------------------|
| NECK_CIRC_M | 0 | N/A |
| BUST_CIRC_M | 0 | N/A |
| UNDERBUST_CIRC_M | 0 | N/A |
| WAIST_CIRC_M | 0 | N/A |
| HIP_CIRC_M | 0 | N/A |
| THIGH_CIRC_M | 0 | N/A |
| MIN_CALF_CIRC_M | 0 | N/A |
| CHEST_WIDTH_M | 0 | N/A |
| CHEST_DEPTH_M | 0 | N/A |
| WAIST_WIDTH_M | 0 | N/A |
| WAIST_DEPTH_M | 0 | N/A |
| HIP_WIDTH_M | 0 | N/A |
| HIP_DEPTH_M | 0 | N/A |
| HEIGHT_M | 0 | N/A |
| CROTCH_HEIGHT_M | 0 | N/A |
| KNEE_HEIGHT_M | 0 | N/A |
| ARM_LEN_M | 0 | N/A |

### 4.3 Canonical Side 기록

| Key | Canonical Sides |
|-----|-----------------|
| NECK_CIRC_M | N/A |
| BUST_CIRC_M | N/A |
| UNDERBUST_CIRC_M | N/A |
| WAIST_CIRC_M | N/A |
| HIP_CIRC_M | N/A |
| THIGH_CIRC_M | right: 10 |
| MIN_CALF_CIRC_M | right: 10 |
| CHEST_WIDTH_M | N/A |
| CHEST_DEPTH_M | N/A |
| WAIST_WIDTH_M | N/A |
| WAIST_DEPTH_M | N/A |
| HIP_WIDTH_M | N/A |
| HIP_DEPTH_M | N/A |
| HEIGHT_M | N/A |
| CROTCH_HEIGHT_M | N/A |
| KNEE_HEIGHT_M | right: 10 |
| ARM_LEN_M | right: 10 |

### 4.4 Pose Unknown 비율

| Key | Breath State Unknown | Arms Down Unknown | Strict Standing Unknown | Knee Flexion Unknown |
|-----|----------------------|-------------------|------------------------|----------------------|
| NECK_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| BUST_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| UNDERBUST_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| WAIST_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| HIP_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| THIGH_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| MIN_CALF_CIRC_M | 0.00% | 0.00% | 0.00% | 0.00% |
| CHEST_WIDTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| CHEST_DEPTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| WAIST_WIDTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| WAIST_DEPTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| HIP_WIDTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| HIP_DEPTH_M | 0.00% | 0.00% | 0.00% | 0.00% |
| HEIGHT_M | 0.00% | 0.00% | 0.00% | 0.00% |
| CROTCH_HEIGHT_M | 0.00% | 0.00% | 0.00% | 0.00% |
| KNEE_HEIGHT_M | 0.00% | 0.00% | 0.00% | 0.00% |
| ARM_LEN_M | 0.00% | 0.00% | 0.00% | 0.00% |

### 4.5 Debug 정보 (실패 원인 분해)

#### 4.5.1 CROSS_SECTION_NOT_FOUND 원인 분포

| Key | Reason | Count | Percentage |
|-----|--------|-------|------------|

#### 4.5.2 Cross-section Candidates Count 통계

| Key | Min | Median | Max | Zero Count |
|-----|-----|--------|-----|-----------|
| NECK_CIRC_M | 2 | 2.0 | 2 | 0 |
| BUST_CIRC_M | 3 | 3.0 | 3 | 0 |
| UNDERBUST_CIRC_M | 3 | 3.0 | 3 | 0 |
| WAIST_CIRC_M | 15 | 17.5 | 20 | 0 |
| HIP_CIRC_M | 15 | 17.5 | 20 | 0 |
| THIGH_CIRC_M | 2 | 2.0 | 2 | 0 |
| MIN_CALF_CIRC_M | 1 | 1.0 | 1 | 0 |
| CHEST_WIDTH_M | 15 | 17.5 | 20 | 0 |
| CHEST_DEPTH_M | 15 | 17.5 | 20 | 0 |
| WAIST_WIDTH_M | 15 | 17.5 | 20 | 0 |
| WAIST_DEPTH_M | 15 | 17.5 | 20 | 0 |
| HIP_WIDTH_M | 15 | 17.5 | 20 | 0 |
| HIP_DEPTH_M | 15 | 17.5 | 20 | 0 |

#### 4.5.3 BODY_AXIS_TOO_SHORT 원인 분포

| Key | Reason | Count |
|-----|--------|-------|

#### 4.5.4 LANDMARK_REGIONS_NOT_FOUND 원인 분포

| Key | Reason | Count |
|-----|--------|-------|
| ARM_LEN_M | no_vertices_in_region | 10 |

## 5. Nearest Valid Plane Fallback 통계 (Valid Cases)

| Key | Used Count | Used Rate | Shift Min (mm) | Shift Median (mm) | Shift Max (mm) |
|-----|------------|-----------|----------------|------------------|----------------|
| WAIST_WIDTH_M | 0 | 0.00% | N/A | N/A | N/A |
| WAIST_DEPTH_M | 0 | 0.00% | N/A | N/A | N/A |
| HIP_WIDTH_M | 0 | 0.00% | N/A | N/A | N/A |
| HIP_DEPTH_M | 0 | 0.00% | N/A | N/A | N/A |

### 5.1 Slice Sharing 통계 (Valid Cases)

| Key | Slice Shared Count | Slice Shared Rate | Slicer Independent False | Shared From |
|-----|-------------------|-------------------|--------------------------|-------------|
| WAIST_WIDTH_M | 10 | 100.00% | 10 | WAIST_CIRC_M:10 |
| WAIST_DEPTH_M | 10 | 100.00% | 10 | WAIST_CIRC_M:10 |
| HIP_WIDTH_M | 10 | 100.00% | 10 | HIP_CIRC_M:10 |
| HIP_DEPTH_M | 10 | 100.00% | 10 | HIP_CIRC_M:10 |

### 5.2 Target/Bbox Debug 통계 (Valid Cases)

| Key | Target Out of Bounds Count | Out of Bounds Rate | Initial Candidates (Zero Count) | Fallback Candidates (Median) |
|-----|---------------------------|-------------------|--------------------------------|------------------------------|
| WAIST_WIDTH_M | 0 | 0.00% | 0 | N/A |
| WAIST_DEPTH_M | 0 | 0.00% | 0 | N/A |
| HIP_WIDTH_M | 0 | 0.00% | 0 | N/A |
| HIP_DEPTH_M | 0 | 0.00% | 0 | N/A |

### 5.3 HEIGHT_M Debug 통계 (Valid Cases)

#### 5.3.1 Bbox 최장축 비교

| Longest Axis | Count | Percentage |
|--------------|-------|------------|
| y | 10 | 100.0% |

**Bbox Longest Span**: 
min=1.6554m, 
median=1.7582m, 
max=1.8407m

| Axis | Span Min (m) | Span Median (m) | Span Max (m) |
|------|--------------|-----------------|--------------|
| x | 0.1959 | 0.2575 | 0.3824 |
| y | 1.6554 | 1.7582 | 1.8407 |
| z | 0.1973 | 0.2555 | 0.3826 |

#### 5.3.2 HEIGHT_M 계산 통계

| Axis Used | Count | Percentage |
|-----------|-------|------------|
| y | 10 | 100.0% |

**Raw Span (m)**: 
min=1.6554, 
median=1.7582, 
max=1.8407

**Post-Transform Span (m)**: 
min=1.6554, 
median=1.7582, 
max=1.8407

**Scale Factor (raw->post)**: 
min=1.0000, 
median=1.0000, 
max=1.0000

**의심 배율 카운트**: 
near 1.0: 10, 
near 0.5: 0, 
near 0.1: 0, 
near 0.01: 0, 
near 10: 0, 
near 100: 0

#### 5.3.3 원인 분류 (Facts 기반)

| Case | Evidence |
|------|----------|
| (원인 분류 불가 - 추가 분석 필요) | |


## 6. Round Comparison

(Round comparison data not available)

## 8. 이슈 분류

### GEO_BUG

- (없음)

### POSE/PROXY

- (없음)

### COVERAGE/UNKNOWN

- (없음)
