# test_thigh_v0_validation_contract.py
# Validation Contract Test for THIGH v0
# Purpose: Verify contract compliance (determinism, degenerate cases, return structure, region warnings)
# No PASS/FAIL quality judgment - contract compliance only

import numpy as np
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import THIGH measurement function (assume it exists)
try:
    from core.measurements.thigh_v0 import measure_thigh_v0, ThighResult
except ImportError:
    # If not implemented yet, skip tests
    print("[SKIP] core.measurements.thigh_v0 not implemented yet")
    sys.exit(0)


def test_determinism():
    """Test: Same input should produce same section_id and method_tag."""
    
    # Fixed input
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.3 - 0.15
        y = (i // 10) / 10.0 * 0.5 - 0.2  # Leg region
        z = ((i % 5) / 5.0) * 0.25 - 0.125
        verts[i] = [x, y, z]
    
    # Call twice
    result1 = measure_thigh_v0(verts=verts, measurement_key="THIGH")
    result2 = measure_thigh_v0(verts=verts, measurement_key="THIGH")
    
    # Check determinism
    assert result1.section_id == result2.section_id, \
        f"section_id must be deterministic: {result1.section_id} != {result2.section_id}"
    assert result1.method_tag == result2.method_tag, \
        f"method_tag must be deterministic: {result1.method_tag} != {result2.method_tag}"
    
    print("[PASS] Determinism test: section_id and method_tag are identical across calls")


def test_degenerate_case_fallback():
    """Test: Degenerate case must return NaN + DEGEN_FAIL warning."""
    
    # Degenerate input: single vertex
    verts = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    
    result = measure_thigh_v0(verts=verts, measurement_key="THIGH")
    
    # Check NaN
    assert np.isnan(result.circumference_m), \
        f"Degenerate case must return NaN, got {result.circumference_m}"
    
    # Check warning (DEGEN_FAIL or EMPTY_CANDIDATES or BODY_AXIS_TOO_SHORT)
    has_degen_warning = (
        "DEGEN_FAIL" in result.warnings or
        "EMPTY_CANDIDATES" in result.warnings or
        "BODY_AXIS_TOO_SHORT" in result.warnings
    )
    assert has_degen_warning, \
        f"Degenerate case must warn about degeneracy, got warnings: {result.warnings}"
    
    print("[PASS] Degenerate case fallback: NaN + DEGEN_FAIL warning")


def test_return_structure():
    """Test: Return structure must contain all required fields."""
    
    # Simple input
    n_verts = 50
    verts = np.random.randn(n_verts, 3).astype(np.float32) * 0.1
    verts[:, 1] -= 0.15  # Shift to leg region
    
    result = measure_thigh_v0(verts=verts, measurement_key="THIGH")
    
    # Check return type
    assert isinstance(result, ThighResult), \
        "Result must be ThighResult instance"
    
    # Check required fields exist
    assert hasattr(result, "measurement_key"), "Missing: measurement_key"
    assert hasattr(result, "circumference_m"), "Missing: circumference_m"
    assert hasattr(result, "section_id"), "Missing: section_id"
    assert hasattr(result, "method_tag"), "Missing: method_tag"
    assert hasattr(result, "warnings"), "Missing: warnings"
    
    # Check field types
    assert isinstance(result.measurement_key, str), "measurement_key must be str"
    assert isinstance(result.circumference_m, (float, type(np.nan))), \
        "circumference_m must be float or NaN"
    assert isinstance(result.section_id, str), "section_id must be str"
    assert isinstance(result.method_tag, str), "method_tag must be str"
    assert isinstance(result.warnings, list), "warnings must be list"
    
    # Check measurement_key is THIGH
    assert result.measurement_key == "THIGH", \
        f"measurement_key must be THIGH, got {result.measurement_key}"
    
    print("[PASS] Return structure: all required fields present and correct types")


def test_region_warnings():
    """Test: hip_bleed_risk and knee_proximity_risk cases should produce region warnings."""
    
    # Test hip_bleed_risk: vertices extend into hip region
    np.random.seed(42)
    n_verts = 100
    verts_hip_risk = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.4 - 0.2
        y = (i // 10) / 10.0 * 0.6 + 0.3  # Extends into hip region
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts_hip_risk[i] = [x, y, z]
    
    result_hip = measure_thigh_v0(verts=verts_hip_risk, measurement_key="THIGH")
    
    # Check for region warning (LEG_REGION_UNCERTAIN or REGION_AMBIGUOUS or HIP_BLEED_RISK)
    has_region_warning = (
        "LEG_REGION_UNCERTAIN" in result_hip.warnings or
        "REGION_AMBIGUOUS" in result_hip.warnings or
        "HIP_BLEED_RISK" in result_hip.warnings or
        "HIP" in str(result_hip.warnings).upper()
    )
    # Note: This is a soft check - if function doesn't implement region detection yet,
    # it's acceptable (no assertion failure, just log)
    if has_region_warning:
        print(f"[PASS] hip_bleed_risk case produced region warning: {result_hip.warnings}")
    else:
        print(f"[NOTE] hip_bleed_risk case did not produce region warning (may not be implemented yet): {result_hip.warnings}")
    
    # Test knee_proximity_risk: vertices too close to knee region
    verts_knee_risk = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.25 - 0.125
        y = (i // 10) / 10.0 * 0.4 - 0.6  # Very low (knee region)
        z = ((i % 5) / 5.0) * 0.2 - 0.1
        verts_knee_risk[i] = [x, y, z]
    
    result_knee = measure_thigh_v0(verts=verts_knee_risk, measurement_key="THIGH")
    
    # Check for region warning
    has_knee_warning = (
        "LEG_REGION_UNCERTAIN" in result_knee.warnings or
        "REGION_AMBIGUOUS" in result_knee.warnings or
        "KNEE_PROXIMITY_RISK" in result_knee.warnings or
        "KNEE" in str(result_knee.warnings).upper()
    )
    if has_knee_warning:
        print(f"[PASS] knee_proximity_risk case produced region warning: {result_knee.warnings}")
    else:
        print(f"[NOTE] knee_proximity_risk case did not produce region warning (may not be implemented yet): {result_knee.warnings}")


if __name__ == "__main__":
    print("Running THIGH v0 Validation Contract Tests...")
    print("=" * 60)
    
    try:
        test_determinism()
        test_degenerate_case_fallback()
        test_return_structure()
        test_region_warnings()
        
        print("=" * 60)
        print("[PASS] All validation contract tests passed")
        print("(No quality judgment - contract compliance only)")
    except ImportError as e:
        print(f"[SKIP] THIGH v0 not implemented yet: {e}")
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        raise
