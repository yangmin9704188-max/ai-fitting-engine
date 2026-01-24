# Geometric v0 Facts-Only Summary (Round 13 - FAST MODE normal_1 Runner Success)

## 0. 실행 정보

- **Run Directory**: `verification/runs/facts/geo_v0/round13_fastmode_normal1_runner`
- **NPZ Absolute Path**: `verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz`
- **Valid Cases**: 1 (normal_1)
- **Expected Fail Cases**: 5 (degenerate_y_range, minimal_vertices, scale_error_suspected, random_noise_seed123, tall_thin)
- **Total Cases**: 6
- **Note**: FAST MODE (ONLY_CASE=normal_1)로 실행되어 valid case는 1개만 포함됨

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

**Valid Cases**: normal_1 (1개)

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
| (모든 키) | 0 | N/A |

### 4.2 Band Scan 사용

| Key | Band Scan Used Count | Band Scan Limits |
|-----|----------------------|------------------|
| (모든 키) | 0 | N/A |

### 4.3 Canonical Side 기록

| Key | Canonical Sides |
|-----|-----------------|
| THIGH_CIRC_M | right: 1 |
| MIN_CALF_CIRC_M | right: 1 |
| KNEE_HEIGHT_M | right: 1 |
| ARM_LEN_M | right: 1 |

### 4.4 Pose Unknown 비율

| Key | Breath State Unknown | Arms Down Unknown | Strict Standing Unknown | Knee Flexion Unknown |
|-----|----------------------|-------------------|------------------------|----------------------|
| (모든 키) | 0.00% | 0.00% | 0.00% | 0.00% |

## 5. Slice Sharing 통계 (Valid Cases)

| Key | Slice Shared Count | Slice Shared Rate | Slicer Independent False | Shared From |
|-----|-------------------|-------------------|--------------------------|-------------|
| WAIST_WIDTH_M | 1 | 100.00% | 1 | WAIST_CIRC_M:1 |
| WAIST_DEPTH_M | 1 | 100.00% | 1 | WAIST_CIRC_M:1 |
| HIP_WIDTH_M | 1 | 100.00% | 1 | HIP_CIRC_M:1 |
| HIP_DEPTH_M | 1 | 100.00% | 1 | HIP_CIRC_M:1 |

## 6. S0 Scale Normalization 통계 (Valid Cases)

### 6.1 HEIGHT_M 및 Bbox Span 통계

| Statistic | Round 8 (Before) | Round 13 (After FAST MODE) |
|-----------|------------------|---------------------------|
| HEIGHT_M Median | 0.8625m | 1.7101m |
| HEIGHT_M Min | 0.765m | 1.7101m |
| HEIGHT_M Max | 0.960m | 1.7101m |

**Bbox Longest Span (m)**: 
min=1.7101, 
median=1.7101, 
max=1.7101

**Bbox Span Y (m)**: 
min=1.7101, 
median=1.7101, 
max=1.7101

**Scale Factor (raw->post)**: 
min=1.0000, 
median=1.0000, 
max=1.0000

(정상: scale_factor=1.0, mesh 좌표가 이미 정규화됨)

### 6.2 둘레/키 비율 (Valid Cases)

| Ratio | Min | Median | Max |
|-------|-----|--------|-----|
| bust/height | 1.535 | 1.535 | 1.535 |
| waist/height | 1.371 | 1.371 | 1.371 |
| hip/height | 1.590 | 1.590 | 1.590 |

## 7. Round 7 Slice-Sharing 회귀 체크 (Valid Cases 기준)

### 7.1 Waist/Hip NaN율 (회귀 확인)

| Key | Round 7 NaN율 | Round 13 NaN율 | 변화 |
|-----|---------------|----------------|------|
| WAIST_CIRC_M | (Round 7) | 0.00% | - |
| WAIST_WIDTH_M | (Round 7) | 0.00% | - |
| WAIST_DEPTH_M | (Round 7) | 0.00% | - |
| HIP_CIRC_M | (Round 7) | 0.00% | - |
| HIP_WIDTH_M | (Round 7) | 0.00% | - |
| HIP_DEPTH_M | (Round 7) | 0.00% | - |

### 7.2 Slice Sharing 유지 확인 (Valid Cases)

| Key | Slice Shared Rate | Slicer Independent False Rate |
|-----|-------------------|-------------------------------|
| WAIST_WIDTH_M | 100.00% | 100.00% |
| WAIST_DEPTH_M | 100.00% | 100.00% |
| HIP_WIDTH_M | 100.00% | 100.00% |
| HIP_DEPTH_M | 100.00% | 100.00% |

## 8. 이슈 분류

### GEO_BUG

- (없음)

### POSE/PROXY

- (없음)

### COVERAGE/UNKNOWN

- (없음)

## 9. FAST MODE 특이사항

- **Warning**: `n_samples=20` 요청했으나 실제 케이스는 6개만 존재 (FAST MODE로 normal_1만 생성됨)
- **Valid Cases**: 1개 (normal_1) - FAST MODE로 인해 다른 valid cases (normal_2~5, varied_1~5)는 생성되지 않음
- **Expected Fail Cases**: 5개 - 정상적으로 포함됨
- **NPZ 생성 성공**: FAST MODE로 생성된 NPZ가 정상적으로 로드되고 처리됨
- **Slice Sharing**: WAIST/HIP width/depth에서 slice sharing이 100% 작동 (WAIST_CIRC_M/HIP_CIRC_M에서 공유)
