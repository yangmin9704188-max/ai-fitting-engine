# test_hip_v0_validation_contract.py
# Validation Contract Test for HIP v0
# Purpose: Verify contract compliance (determinism, degenerate cases, return structure)
# No PASS/FAIL quality judgment - contract compliance only

import numpy as np
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import HIP measurement function (assume it exists)
try:
    from core.measurements.hip_v0 import measure_hip_v0, HipResult
except ImportError:
    # If not implemented yet, skip tests
    print("[SKIP] core.measurements.hip_v0 not implemented yet")
    sys.exit(0)


def test_determinism():
    """Test: Same input should produce same section_id and method_tag."""
    
    # Fixed input
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.5 - 0.25
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts[i] = [x, y, z]
    
    # Call twice
    result1 = measure_hip_v0(verts=verts, measurement_key="HIP")
    result2 = measure_hip_v0(verts=verts, measurement_key="HIP")
    
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
    
    result = measure_hip_v0(verts=verts, measurement_key="HIP")
    
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
    
    result = measure_hip_v0(verts=verts, measurement_key="HIP")
    
    # Check return type
    assert isinstance(result, HipResult), \
        "Result must be HipResult instance"
    
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
    
    # Check measurement_key is HIP
    assert result.measurement_key == "HIP", \
        f"measurement_key must be HIP, got {result.measurement_key}"
    
    print("[PASS] Return structure: all required fields present and correct types")


if __name__ == "__main__":
    print("Running HIP v0 Validation Contract Tests...")
    print("=" * 60)
    
    try:
        test_determinism()
        test_degenerate_case_fallback()
        test_return_structure()
        
        print("=" * 60)
        print("[PASS] All validation contract tests passed")
        print("(No quality judgment - contract compliance only)")
    except ImportError as e:
        print(f"[SKIP] HIP v0 not implemented yet: {e}")
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        raise
