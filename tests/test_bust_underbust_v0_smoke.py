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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
