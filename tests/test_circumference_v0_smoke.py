# test_circumference_v0_smoke.py
# Smoke test for Geometric Layer v0
# Purpose: Verify callability and contract structure compliance

import numpy as np
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.measurements.circumference_v0 import measure_circumference_v0, CircumferenceResult


def test_smoke_bust():
    """Smoke test: BUST measurement - callable and contract compliance."""
    
    # Fixed sample input (meters)
    # Simple box-like body shape for testing
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    # Generate vertices in a box shape (0.5m x 1.0m x 0.3m)
    # y-axis is vertical (body long axis)
    for i in range(n_verts):
        # x: -0.25 to 0.25
        # y: 0.0 to 1.0 (body height)
        # z: -0.15 to 0.15
        x = (i % 10) / 10.0 * 0.5 - 0.25
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts[i] = [x, y, z]
    
    # Test 1: Function call completes without exception
    try:
        result = measure_circumference_v0(
            verts=verts,
            measurement_key="BUST",
            units_metadata={"unit": "meters"}
        )
    except Exception as e:
        assert False, f"Function call raised exception: {e}"
    
    # Test 2: Return structure contains all Interface contract fields
    assert isinstance(result, CircumferenceResult), "Result must be CircumferenceResult"
    assert hasattr(result, "measurement_key"), "Missing: measurement_key"
    assert hasattr(result, "circumference_m"), "Missing: circumference_m"
    assert hasattr(result, "section_id"), "Missing: section_id"
    assert hasattr(result, "method_tag"), "Missing: method_tag"
    assert hasattr(result, "warnings"), "Missing: warnings"
    
    # Test 3: Output circumference_m is meters (float or NaN)
    assert isinstance(result.circumference_m, (float, type(np.nan))), \
        f"circumference_m must be float or NaN, got {type(result.circumference_m)}"
    
    # Explicit check: NaN or finite float
    if not np.isnan(result.circumference_m):
        assert np.isfinite(result.circumference_m), \
            f"circumference_m must be finite float or NaN, got {result.circumference_m}"
        # Units check: reasonable range for meters (0.1m to 3.0m for body measurements)
        # This is NOT accuracy check, just unit sanity
        assert 0.0 <= result.circumference_m <= 10.0, \
            f"circumference_m out of reasonable range: {result.circumference_m}m"
    
    # Test 4: Field types
    assert isinstance(result.measurement_key, str), "measurement_key must be str"
    assert isinstance(result.section_id, str), "section_id must be str"
    assert isinstance(result.method_tag, str), "method_tag must be str"
    assert isinstance(result.warnings, list), "warnings must be list"
    
    # Test 5: measurement_key matches input
    assert result.measurement_key == "BUST", \
        f"measurement_key mismatch: expected BUST, got {result.measurement_key}"
    
    print("[PASS] BUST smoke test passed")
    print(f"  circumference_m: {result.circumference_m}")
    print(f"  section_id: {result.section_id[:50]}...")
    print(f"  method_tag: {result.method_tag}")
    print(f"  warnings: {len(result.warnings)} warnings")


def test_smoke_waist():
    """Smoke test: WAIST measurement."""
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.4 - 0.2
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.25 - 0.125
        verts[i] = [x, y, z]
    
    result = measure_circumference_v0(verts=verts, measurement_key="WAIST")
    
    assert isinstance(result, CircumferenceResult)
    assert isinstance(result.circumference_m, (float, type(np.nan)))
    assert result.measurement_key == "WAIST"
    
    print("[PASS] WAIST smoke test passed")
    print(f"  circumference_m: {result.circumference_m}")


def test_smoke_hip():
    """Smoke test: HIP measurement."""
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    for i in range(n_verts):
        x = (i % 10) / 10.0 * 0.45 - 0.225
        y = (i // 10) / 10.0 * 1.0
        z = ((i % 5) / 5.0) * 0.3 - 0.15
        verts[i] = [x, y, z]
    
    result = measure_circumference_v0(verts=verts, measurement_key="HIP")
    
    assert isinstance(result, CircumferenceResult)
    assert isinstance(result.circumference_m, (float, type(np.nan)))
    assert result.measurement_key == "HIP"
    
    print("[PASS] HIP smoke test passed")
    print(f"  circumference_m: {result.circumference_m}")


def test_smoke_empty_candidates():
    """Smoke test: Empty candidates fallback (NaN)."""
    # Degenerate input: single vertex
    verts = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    
    result = measure_circumference_v0(verts=verts, measurement_key="BUST")
    
    assert isinstance(result, CircumferenceResult)
    assert np.isnan(result.circumference_m), "Empty candidates must return NaN"
    assert "EMPTY_CANDIDATES" in result.warnings, "Must warn about empty candidates"
    
    print("[PASS] Empty candidates fallback test passed")
    print(f"  circumference_m: {result.circumference_m} (NaN as expected)")


if __name__ == "__main__":
    print("Running Geometric Layer v0 smoke tests...")
    print("=" * 60)
    
    test_smoke_bust()
    test_smoke_waist()
    test_smoke_hip()
    test_smoke_empty_candidates()
    
    print("=" * 60)
    print("[PASS] All smoke tests passed")
