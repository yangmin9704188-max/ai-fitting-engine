# Geometric v0 Facts-Only Summary

## 1. 실행 조건

- **샘플 수**: 6
- **입력 데이터셋**: `verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz`
- **Git SHA**: `6b0f83c0e312fb94bd28251a34835e29a06cebc6`
- **실행 일시**: 2026-01-25T05:13:06.315619

### 1.1 S0 Dataset Scale Statistics

- **HEIGHT_M**: min=1.710m, median=1.710m, max=1.710m
- **BUST_CIRC_M**: median=2.626m, BUST/height ratio=1.535
- **WAIST_CIRC_M**: median=2.344m, WAIST/height ratio=1.371
- **HIP_CIRC_M**: median=2.719m, HIP/height ratio=1.590

## 2. Key별 요약 (Valid Cases Only - DoD 평가 기준)

**Valid Cases**: normal_* + varied_* (10개)

| Key | Valid Total | Valid NaN | Valid NaN Rate | Min | Median | Max | DoD (<=40%) |
|-----|-------------|-----------|----------------|-----|--------|-----|-------------|
| NECK_CIRC_M | 1 | 0 | 0.00% | 2.7194 | 2.7194 | 2.7194 | N/A |
| BUST_CIRC_M | 1 | 0 | 0.00% | 2.6257 | 2.6257 | 2.6257 | N/A |
| UNDERBUST_CIRC_M | 1 | 0 | 0.00% | 2.3440 | 2.3440 | 2.3440 | N/A |
| WAIST_CIRC_M | 1 | 0 | 0.00% | 2.3440 | 2.3440 | 2.3440 | N/A |
| HIP_CIRC_M | 1 | 0 | 0.00% | 2.7194 | 2.7194 | 2.7194 | N/A |
| THIGH_CIRC_M | 1 | 0 | 0.00% | 2.3871 | 2.3871 | 2.3871 | N/A |
| MIN_CALF_CIRC_M | 1 | 0 | 0.00% | 1.6216 | 1.6216 | 1.6216 | N/A |
| CHEST_WIDTH_M | 1 | 0 | 0.00% | 0.4501 | 0.4501 | 0.4501 | N/A |
| CHEST_DEPTH_M | 1 | 0 | 0.00% | 0.4321 | 0.4321 | 0.4321 | N/A |
| WAIST_WIDTH_M | 1 | 0 | 0.00% | 0.7278 | 0.7278 | 0.7278 | ✅ PASS |
| WAIST_DEPTH_M | 1 | 0 | 0.00% | 0.7287 | 0.7287 | 0.7287 | ✅ PASS |
| HIP_WIDTH_M | 1 | 0 | 0.00% | 0.8584 | 0.8584 | 0.8584 | ✅ PASS |
| HIP_DEPTH_M | 1 | 0 | 0.00% | 0.8975 | 0.8975 | 0.8975 | ✅ PASS |
| HEIGHT_M | 1 | 0 | 0.00% | 1.7101 | 1.7101 | 1.7101 | N/A |
| CROTCH_HEIGHT_M | 1 | 0 | 0.00% | 0.7696 | 0.7696 | 0.7696 | N/A |
| KNEE_HEIGHT_M | 1 | 0 | 0.00% | 0.4275 | 0.4275 | 0.4275 | N/A |
| ARM_LEN_M | 1 | 1 | 100.00% | N/A | N/A | N/A | N/A |

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
| MIN_SEARCH_USED | 1 |
| CROTCH_ESTIMATED | 1 |
| KNEE_ESTIMATED | 1 |
| LANDMARK_REGIONS_NOT_FOUND | 1 |

### 3.2 Key별 Warnings Top 5

**MIN_CALF_CIRC_M**:
- `MIN_SEARCH_USED`: 1

**CROTCH_HEIGHT_M**:
- `CROTCH_ESTIMATED`: 1

**KNEE_HEIGHT_M**:
- `KNEE_ESTIMATED`: 1

**ARM_LEN_M**:
- `LANDMARK_REGIONS_NOT_FOUND`: 1

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
| THIGH_CIRC_M | right: 1 |
| MIN_CALF_CIRC_M | right: 1 |
| CHEST_WIDTH_M | N/A |
| CHEST_DEPTH_M | N/A |
| WAIST_WIDTH_M | N/A |
| WAIST_DEPTH_M | N/A |
| HIP_WIDTH_M | N/A |
| HIP_DEPTH_M | N/A |
| HEIGHT_M | N/A |
| CROTCH_HEIGHT_M | N/A |
| KNEE_HEIGHT_M | right: 1 |
| ARM_LEN_M | right: 1 |

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
| WAIST_CIRC_M | 20 | 20.0 | 20 | 0 |
| HIP_CIRC_M | 20 | 20.0 | 20 | 0 |
| THIGH_CIRC_M | 2 | 2.0 | 2 | 0 |
| MIN_CALF_CIRC_M | 1 | 1.0 | 1 | 0 |
| CHEST_WIDTH_M | 20 | 20.0 | 20 | 0 |
| CHEST_DEPTH_M | 20 | 20.0 | 20 | 0 |
| WAIST_WIDTH_M | 20 | 20.0 | 20 | 0 |
| WAIST_DEPTH_M | 20 | 20.0 | 20 | 0 |
| HIP_WIDTH_M | 20 | 20.0 | 20 | 0 |
| HIP_DEPTH_M | 20 | 20.0 | 20 | 0 |

#### 4.5.3 BODY_AXIS_TOO_SHORT 원인 분포

| Key | Reason | Count |
|-----|--------|-------|

#### 4.5.4 LANDMARK_REGIONS_NOT_FOUND 원인 분포

| Key | Reason | Count |
|-----|--------|-------|
| ARM_LEN_M | no_vertices_in_region | 1 |

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
| WAIST_WIDTH_M | 1 | 100.00% | 1 | WAIST_CIRC_M:1 |
| WAIST_DEPTH_M | 1 | 100.00% | 1 | WAIST_CIRC_M:1 |
| HIP_WIDTH_M | 1 | 100.00% | 1 | HIP_CIRC_M:1 |
| HIP_DEPTH_M | 1 | 100.00% | 1 | HIP_CIRC_M:1 |

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
| y | 1 | 100.0% |

**Bbox Longest Span**: 
min=1.7101m, 
median=1.7101m, 
max=1.7101m

| Axis | Span Min (m) | Span Median (m) | Span Max (m) |
|------|--------------|-----------------|--------------|
| x | 0.8842 | 0.8842 | 0.8842 |
| y | 1.7101 | 1.7101 | 1.7101 |
| z | 0.9091 | 0.9091 | 0.9091 |

#### 5.3.2 HEIGHT_M 계산 통계

| Axis Used | Count | Percentage |
|-----------|-------|------------|
| y | 1 | 100.0% |

**Raw Span (m)**: 
min=1.7101, 
median=1.7101, 
max=1.7101

**Post-Transform Span (m)**: 
min=1.7101, 
median=1.7101, 
max=1.7101

**Scale Factor (raw->post)**: 
min=1.0000, 
median=1.0000, 
max=1.0000

**의심 배율 카운트**: 
near 1.0: 1, 
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
