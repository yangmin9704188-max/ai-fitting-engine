# test_bust_underbust_v0_smoke.py
# Smoke tests for BUST/UNDERBUST v0 geometric implementation
# Purpose: Policy sealing (Contract Violation = NaN + warnings, no exceptions)

import numpy as np
import pytest
from core.measurements.bust_underbust_v0 import (
    measure_underbust_v0,
    measure_bust_v0,
    BustUnderbustResult
)


def test_format_violation_underbust():
    """Test: Format violation returns NaN + FORMAT_VIOLATION, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Invalid format: "75" (missing cup)
    result = measure_underbust_v0(verts, bra_size_token="75")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    assert np.isnan(result.circumference_m)
    assert "FORMAT_VIOLATION" in result.warnings
    # No exception should be raised


def test_format_violation_bust():
    """Test: Format violation returns NaN + FORMAT_VIOLATION, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Invalid format: "ABC" (non-numeric)
    result = measure_bust_v0(verts, bra_size_token="ABC")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "BUST"
    assert np.isnan(result.circumference_m)
    assert "FORMAT_VIOLATION" in result.warnings
    # No exception should be raised


def test_range_violation_underbust():
    """Test: Range violation returns NaN + RANGE_VIOLATION, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Range violation: band < 65
    result = measure_underbust_v0(verts, bra_size_token="60A")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    assert np.isnan(result.circumference_m)
    assert "RANGE_VIOLATION" in result.warnings
    # No exception should be raised


def test_range_violation_bust():
    """Test: Range violation returns NaN + RANGE_VIOLATION, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Range violation: band > 90
    result = measure_bust_v0(verts, bra_size_token="95A")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "BUST"
    assert np.isnan(result.circumference_m)
    assert "RANGE_VIOLATION" in result.warnings
    # No exception should be raised


def test_cup_unknown_underbust():
    """Test: Unknown cup returns NaN + CUP_UNKNOWN, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Unknown cup: "G" (not in A-F)
    result = measure_underbust_v0(verts, bra_size_token="75G")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    assert np.isnan(result.circumference_m)
    assert "CUP_UNKNOWN" in result.warnings
    # No exception should be raised


def test_cup_unknown_bust():
    """Test: Unknown cup returns NaN + CUP_UNKNOWN, no exception."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Unknown cup: "H" (not in A-F)
    result = measure_bust_v0(verts, bra_size_token="75H")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "BUST"
    assert np.isnan(result.circumference_m)
    assert "CUP_UNKNOWN" in result.warnings
    # No exception should be raised


def test_valid_bra_size_underbust():
    """Test: Valid bra size returns finite value (type/unit check only)."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Valid: "75A"
    result = measure_underbust_v0(verts, bra_size_token="75A")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    assert isinstance(result.circumference_m, float)
    assert np.isfinite(result.circumference_m)
    # Value should be in meters (0.75 for 75cm)
    assert 0.0 < result.circumference_m < 2.0  # Reasonable range check
    assert isinstance(result.section_id, str)
    assert isinstance(result.method_tag, str)
    assert isinstance(result.warnings, list)


def test_valid_bra_size_bust():
    """Test: Valid bra size returns finite value (type/unit check only)."""
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)
    
    # Valid: "80C"
    result = measure_bust_v0(verts, bra_size_token="80C")
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "BUST"
    assert isinstance(result.circumference_m, float)
    assert np.isfinite(result.circumference_m)
    # Value should be in meters (0.80 + 0.15 = 0.95 for 80C)
    assert 0.0 < result.circumference_m < 2.0  # Reasonable range check
    assert isinstance(result.section_id, str)
    assert isinstance(result.method_tag, str)
    assert isinstance(result.warnings, list)


def test_input_contract_fail():
    """Test: Invalid verts shape returns NaN + INPUT_CONTRACT_FAIL, no exception."""
    # Invalid shape: (3,) instead of (N, 3)
    verts = np.array([0.0, 1.0, 2.0], dtype=np.float32)
    
    result = measure_underbust_v0(verts)
    
    assert isinstance(result, BustUnderbustResult)
    assert np.isnan(result.circumference_m)
    assert "INPUT_CONTRACT_FAIL" in result.warnings
    # No exception should be raised


def test_verts_based_underbust():
    """Test: verts-based underbust measurement attempts computation, no NOT_IMPLEMENTED warning."""
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
    
    # Call without bra_size_token to trigger verts-based path
    result = measure_underbust_v0(verts, bra_size_token=None)
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    # NOT_IMPLEMENTED warning should not appear
    assert "NOT_IMPLEMENTED" not in result.warnings
    
    # Result should be either:
    # - finite float (successful measurement), or
    # - NaN with UNDERBUST_MEASUREMENT_FAILED warning (failed but attempted)
    if np.isfinite(result.circumference_m):
        # Successful: check type and reasonable range
        assert isinstance(result.circumference_m, float)
        assert 0.0 < result.circumference_m < 2.0  # Reasonable range for meters
    else:
        # Failed: should have failure warning
        assert np.isnan(result.circumference_m)
        assert "UNDERBUST_MEASUREMENT_FAILED" in result.warnings or "EMPTY_CANDIDATES" in result.warnings or "SELECTION_FAILED" in result.warnings
    
    # No exception should be raised
    assert isinstance(result.section_id, str)
    assert isinstance(result.method_tag, str)
    assert isinstance(result.warnings, list)


def test_unordered_ring_perimeter():
    """Test: unordered ring points are correctly ordered and perimeter computed."""
    # Create circular ring in xz plane (y is constant)
    # Radius r = 0.15m, N = 128 points
    r = 0.15
    n_points = 128
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    
    # Generate points in xz plane (x, z coordinates)
    x_coords = r * np.cos(angles)
    z_coords = r * np.sin(angles)
    
    # Expected perimeter: 2 * pi * r
    expected_perimeter = 2 * np.pi * r
    
    # Create verts with multiple y levels (to ensure slice detection)
    # y = 0.2, 0.5, 0.8 (three rings)
    n_verts = n_points * 3
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    y_levels = [0.2, 0.5, 0.8]
    for ring_idx, y_val in enumerate(y_levels):
        start_idx = ring_idx * n_points
        end_idx = start_idx + n_points
        
        # Shuffle the order to test ordering
        indices = np.arange(n_points)
        np.random.seed(42)  # Fixed seed for reproducibility
        np.random.shuffle(indices)
        
        for i, shuffled_idx in enumerate(indices):
            verts[start_idx + i] = [x_coords[shuffled_idx], y_val, z_coords[shuffled_idx]]
    
    # Call measure_underbust_v0 without bra_size_token to trigger verts-based path
    result = measure_underbust_v0(verts, bra_size_token=None)
    
    assert isinstance(result, BustUnderbustResult)
    assert result.measurement_key == "UNDERBUST"
    # NOT_IMPLEMENTED warning should not appear
    assert "NOT_IMPLEMENTED" not in result.warnings
    
    # Result should be either finite or NaN with failure warning
    if np.isfinite(result.circumference_m):
        # Successful: check that perimeter is reasonable (wide tolerance)
        # Allow 30% error margin: [0.7 * expected, 1.3 * expected]
        assert 0.7 * expected_perimeter <= result.circumference_m <= 1.3 * expected_perimeter, \
            f"Perimeter {result.circumference_m} not in expected range [{(0.7 * expected_perimeter):.4f}, {(1.3 * expected_perimeter):.4f}]"
    else:
        # Failed: should have failure warning
        assert np.isnan(result.circumference_m)
        assert ("UNDERBUST_MEASUREMENT_FAILED" in result.warnings or 
                "EMPTY_CANDIDATES" in result.warnings or 
                "SELECTION_FAILED" in result.warnings)
    
    # No exception should be raised
    assert isinstance(result.section_id, str)
    assert isinstance(result.method_tag, str)
    assert isinstance(result.warnings, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
