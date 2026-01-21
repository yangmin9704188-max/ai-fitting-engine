---
title: "Validation Frame: Circumference v0"
version: "v0.1"
status: "draft"
created_date: "2026-01-21"
author: "Yang"
---

# Validation Frame: Circumference v0

> Doc Type: Contract  
> Layer: Validation

---

## 1. Purpose

본 계약은 `core/measurements/circumference_v0.py::measure_circumference_v0`에 대한 검증 프로토콜을 정의합니다.

검증의 목적:
- 측정 함수의 실행 가능성 확인
- 출력 형식 계약 준수 확인
- 재현 가능성(결정성) 확인
- 실패 케이스 분류 및 기록

**Non-Goals:**
- 정확도 판정 (PASS/FAIL 임계값 기반)
- 품질 게이트 (delta, delta_pct, fail_rate)
- 성능 최적화 평가
- 시스템 아키텍처 재설계

---

## 2. Inputs

### 2.1 Dataset Tiers

**Tier S0: Synthetic Cases**
- 목적: 기본 실행 가능성 및 계약 준수 확인
- 형식: NPZ 파일 (`verification/datasets/golden/circumference_v0/s0_synthetic_cases.npz`)
- 포함 케이스:
  - 정상 케이스 (박스/원통 유사) 2개
  - 퇴화 케이스 (y-range 매우 작음) 1개
  - 극소 N (정점 1~2개) 1개
  - 스케일 오류 의심 (cm 스케일처럼 큰 값) 1개
  - 랜덤 노이즈 케이스 (결정성 체크용, seed 고정) 1개

### 2.2 Input Format

**verts** (required):
- Shape: `(N, 3)` where N >= 1
- Dtype: `float32`
- Units: **meters** (정상 케이스)
- Coordinate system: 3D Cartesian (x, y, z)
- y-axis: Body long axis (vertical)

**measurement_key** (required):
- Type: `Literal["BUST", "WAIST", "HIP"]`

**units_metadata** (optional):
- Type: `Dict[str, Any]` or `None`
- Default: meters assumed if not provided

---

## 3. Execution Protocol

### 3.1 Runner Script

**File**: `verification/runners/verify_circumference_v0.py`

**Execution**:
```bash
python verification/runners/verify_circumference_v0.py [--npz <path>] [--out_dir <path>]
```

**Process**:
1. Load NPZ dataset
2. For each case_id:
   - For each measurement_key in ["BUST", "WAIST", "HIP"]:
     - Call `measure_circumference_v0(verts, measurement_key)`
     - Record output to CSV
     - Handle exceptions (record failure_type)
3. Generate summary JSON

### 3.2 Exception Handling

- **INPUT_CONTRACT_FAIL**: Input shape/type validation failure
- **EXEC_FAIL**: Function execution exception (non-input related)
- **UNIT_FAIL**: Suspected unit error (e.g., cm instead of meters) - 표식만, 중단 금지
- **DEGEN_FAIL**: Degenerate geometry (too few vertices, zero range)
- **NONDETERMINISTIC**: Determinism violation (repeated calls produce different section_id/method_tag)

---

## 4. Output Metrics

### 4.1 Per-Case Output (CSV)

**File**: `verification/reports/circumference_v0/validation_results.csv`

**Columns**:
- `case_id`: str
- `measurement_key`: str ("BUST" | "WAIST" | "HIP")
- `circumference_m`: float or "NaN" (meters)
- `section_id`: str (JSON string)
- `method_tag`: str
- `warnings_json`: str (JSON array of warning strings)
- `failure_type`: str or empty (if execution failed)

### 4.2 Summary Output (JSON)

**File**: `verification/reports/circumference_v0/validation_summary.json`

**Fields**:
- `git_sha`: str (if available)
- `dataset_id`: str (e.g., "s0_synthetic_cases")
- `nan_rate_by_key`: Dict[str, float] (BUST/WAIST/HIP별 NaN 비율)
- `warning_histogram`: Dict[str, int] (warning 타입별 발생 횟수)
- `determinism_mismatch_count`: int (반복 실행 2회 비교 시 불일치 횟수)
- `nonfinite_count`: int (circumference_m이 NaN/Inf인 케이스 수)
- `failure_count_by_type`: Dict[str, int] (failure_type별 발생 횟수)

**Units**:
- 모든 길이/둘레 값은 **meters** 단위
- `circumference_m`은 float 또는 NaN

---

## 5. Failure Taxonomy

### 5.1 INPUT_CONTRACT_FAIL

**Definition**: Input validation 실패

**Examples**:
- `verts.shape[1] != 3`
- `verts.ndim != 2`
- `measurement_key not in ["BUST", "WAIST", "HIP"]`

**Recording**:
- `failure_type = "INPUT_CONTRACT_FAIL"`
- `warnings_json`에 stacktrace 요약 포함 (너무 길면 잘라서)

### 5.2 EXEC_FAIL

**Definition**: Function execution 중 예외 발생 (input validation 통과 후)

**Examples**:
- IndexError, ValueError (non-input)
- MemoryError
- 기타 런타임 예외

**Recording**:
- `failure_type = "EXEC_FAIL"`
- `warnings_json`에 stacktrace 요약 포함

### 5.3 UNIT_FAIL

**Definition**: 스케일 오류 의심 (예: cm 단위로 입력됨)

**Examples**:
- `circumference_m > 10.0` (10m 이상은 비정상)
- `warnings`에 "PERIMETER_LARGE" 포함

**Recording**:
- `failure_type = "UNIT_FAIL"` (표식만)
- **중단 금지**: 계속 실행하여 전체 데이터셋 검증 완료

### 5.4 DEGEN_FAIL

**Definition**: 퇴화 기하학 (degenerate geometry)

**Examples**:
- `y_range < 1e-6` (body axis too short)
- `N < 3` (too few vertices)
- `warnings`에 "BODY_AXIS_TOO_SHORT", "EMPTY_CANDIDATES" 포함

**Recording**:
- `failure_type = "DEGEN_FAIL"` (선택적, warnings로도 충분)
- `circumference_m = NaN` (정상 fallback)

### 5.5 NONDETERMINISTIC

**Definition**: 결정성 위반 (determinism violation)

**Detection**:
- 동일 입력으로 2회 호출
- `section_id` 또는 `method_tag` 불일치

**Recording**:
- `failure_type = "NONDETERMINISTIC"`
- `determinism_mismatch_count` 증가

---

## 6. Validation Artifacts

### 6.1 Required Files

1. **Dataset**: `verification/datasets/golden/circumference_v0/s0_synthetic_cases.npz`
2. **Runner**: `verification/runners/verify_circumference_v0.py`
3. **Test**: `tests/test_circumference_v0_validation_contract.py`
4. **Output CSV**: `verification/reports/circumference_v0/validation_results.csv`
5. **Output JSON**: `verification/reports/circumference_v0/validation_summary.json`

### 6.2 Artifact Structure

**NPZ Dataset**:
- `verts`: `(N_cases, N_verts, 3)` or list of `(N_verts, 3)` arrays, `float32`
- `case_id`: `(N_cases,)` array of str or int

**CSV Output**:
- One row per `(case_id, measurement_key)` combination
- UTF-8 encoding

**JSON Output**:
- UTF-8 encoding
- Pretty-printed (indent=2)

---

## 7. Change Notes

v0.1 (2026-01-21):
- Initial validation frame definition
- S0 synthetic dataset specification
- Failure taxonomy establishment
- No PASS/FAIL thresholds (factual recording only)
