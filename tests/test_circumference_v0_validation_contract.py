# test_circumference_v0_validation_contract.py
# Validation Contract Test for Circumference v0
# Purpose: Verify contract compliance (determinism, empty candidates, return structure)
# No PASS/FAIL quality judgment - contract compliance only

import numpy as np
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.measurements.circumference_v0 import measure_circumference_v0, CircumferenceResult


def test_determinism():
    """Test (a): Same input should produce same section_id and method_tag."""
    
    # Fixed input
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.5 - 0.25
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts[i] = [x, y, z]
    
    # Call twice
    result1 = measure_circumference_v0(verts=verts, measurement_key="BUST")
    result2 = measure_circumference_v0(verts=verts, measurement_key="BUST")
    
    # Check determinism
    assert result1.section_id == result2.section_id, \
        f"section_id must be deterministic: {result1.section_id} != {result2.section_id}"
    assert result1.method_tag == result2.method_tag, \
        f"method_tag must be deterministic: {result1.method_tag} != {result2.method_tag}"
    
    print("[PASS] Determinism test: section_id and method_tag are identical across calls")


def test_empty_candidates_fallback():
    """Test (b): Empty candidates case must return NaN + EMPTY_CANDIDATES warning."""
    
    # Degenerate input: single vertex
    verts = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    
    result = measure_circumference_v0(verts=verts, measurement_key="BUST")
    
    # Check NaN
    assert np.isnan(result.circumference_m), \
        f"Empty candidates must return NaN, got {result.circumference_m}"
    
    # Check warning
    assert "EMPTY_CANDIDATES" in result.warnings, \
        f"Empty candidates must warn 'EMPTY_CANDIDATES', got warnings: {result.warnings}"
    
    print("[PASS] Empty candidates fallback: NaN + EMPTY_CANDIDATES warning")


def test_return_structure():
    """Test (c): Return structure must contain all required fields."""
    
    # Simple input
    n_verts = 50
    verts = np.random.randn(n_verts, 3).astype(np.float32) * 0.1
    
    result = measure_circumference_v0(verts=verts, measurement_key="WAIST")
    
    # Check return type
    assert isinstance(result, CircumferenceResult), \
        "Result must be CircumferenceResult instance"
    
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
    
    print("[PASS] Return structure: all required fields present and correct types")


def test_all_measurement_keys():
    """Test that all measurement keys (BUST, WAIST, HIP) work."""
    
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.5 - 0.25
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts[i] = [x, y, z]
    
    for key in ["BUST", "WAIST", "HIP"]:
        result = measure_circumference_v0(verts=verts, measurement_key=key)
        assert result.measurement_key == key, \
            f"measurement_key mismatch: expected {key}, got {result.measurement_key}"
        assert isinstance(result, CircumferenceResult)
    
    print("[PASS] All measurement keys (BUST, WAIST, HIP) work correctly")


if __name__ == "__main__":
    print("Running Circumference v0 Validation Contract Tests...")
    print("=" * 60)
    
    test_determinism()
    test_empty_candidates_fallback()
    test_return_structure()
    test_all_measurement_keys()
    
    print("=" * 60)
    print("[PASS] All validation contract tests passed")
    print("(No quality judgment - contract compliance only)")
