"""
Smoke test for ingestion unit canonicalization.

Tests the canonicalize_units_to_m function to ensure:
- Correct unit conversion (mm/cm/m -> m)
- 0.001m quantization with round-half-up
- NaN + warnings[] policy for invalid inputs
- No exceptions raised
"""

import numpy as np
import pytest
from data.ingestion import canonicalize_units_to_m, get_provenance_dict


def test_canonicalize_mm_to_m():
    """Test: mm to m conversion with quantization."""
    warnings = []
    values_mm = np.array([1000.0, 500.0, 100.0, 50.0])
    result = canonicalize_units_to_m(values_mm, "mm", warnings)
    
    assert isinstance(result, np.ndarray)
    assert len(warnings) == 0 or "PROVENANCE" in warnings[0]
    # 1000mm = 1.0m, 500mm = 0.5m, 100mm = 0.1m, 50mm = 0.05m
    expected = np.array([1.0, 0.5, 0.1, 0.05])
    np.testing.assert_allclose(result, expected, rtol=1e-3)


def test_canonicalize_cm_to_m():
    """Test: cm to m conversion with quantization."""
    warnings = []
    values_cm = np.array([100.0, 75.0, 50.0])
    result = canonicalize_units_to_m(values_cm, "cm", warnings)
    
    assert isinstance(result, np.ndarray)
    # 100cm = 1.0m, 75cm = 0.75m, 50cm = 0.5m
    expected = np.array([1.0, 0.75, 0.5])
    np.testing.assert_allclose(result, expected, rtol=1e-3)


def test_canonicalize_m_to_m():
    """Test: m to m (no conversion, quantization only)."""
    warnings = []
    values_m = np.array([1.0, 0.75, 0.5, 0.001])
    result = canonicalize_units_to_m(values_m, "m", warnings)
    
    assert isinstance(result, np.ndarray)
    # Should be quantized but essentially unchanged
    expected = np.array([1.0, 0.75, 0.5, 0.001])
    np.testing.assert_allclose(result, expected, rtol=1e-3)


def test_quantization_round_half_up():
    """Test: 0.001m quantization with round-half-up."""
    warnings = []
    # Test round-half-up: 0.0005m should round to 0.001m
    values = np.array([0.0005, 0.0004, 0.0006, 0.0015])
    result = canonicalize_units_to_m(values, "m", warnings)
    
    assert isinstance(result, np.ndarray)
    # 0.0005 -> 0.001 (round-half-up), 0.0004 -> 0.000, 0.0006 -> 0.001, 0.0015 -> 0.002
    expected = np.array([0.001, 0.000, 0.001, 0.002])
    np.testing.assert_allclose(result, expected, rtol=1e-3)


def test_invalid_source_unit():
    """Test: Invalid source_unit results in NaN + UNIT_FAIL warning, no exception."""
    warnings = []
    values = np.array([100.0, 200.0])
    result = canonicalize_units_to_m(values, "invalid_unit", warnings)
    
    assert isinstance(result, np.ndarray)
    assert np.all(np.isnan(result))
    assert any("UNIT_FAIL" in w for w in warnings)
    assert any("Invalid source_unit" in w for w in warnings)


def test_invalid_values_inf():
    """Test: inf/-inf values become NaN + UNIT_FAIL warning, no exception."""
    warnings = []
    values = np.array([100.0, np.inf, -np.inf, 200.0])
    result = canonicalize_units_to_m(values, "cm", warnings)
    
    assert isinstance(result, np.ndarray)
    assert np.isnan(result[1])  # inf -> NaN
    assert np.isnan(result[2])  # -inf -> NaN
    assert np.isfinite(result[0])  # 100.0cm -> 1.0m
    assert np.isfinite(result[3])  # 200.0cm -> 2.0m
    assert any("UNIT_FAIL" in w for w in warnings)
    assert any("invalid value" in w.lower() for w in warnings)


def test_scalar_input():
    """Test: Scalar input returns scalar output."""
    warnings = []
    result = canonicalize_units_to_m(100.0, "cm", warnings)
    
    assert isinstance(result, float)
    assert result == 1.0
    assert np.isfinite(result)


def test_list_input():
    """Test: List input returns numpy array."""
    warnings = []
    values = [100.0, 200.0, 300.0]
    result = canonicalize_units_to_m(values, "cm", warnings)
    
    assert isinstance(result, np.ndarray)
    expected = np.array([1.0, 2.0, 3.0])
    np.testing.assert_allclose(result, expected, rtol=1e-3)


def test_provenance_dict():
    """Test: Provenance dictionary generation."""
    prov_mm = get_provenance_dict("mm")
    assert prov_mm["source_unit"] == "mm"
    assert prov_mm["conversion_applied"] == "mm_to_m"
    assert prov_mm["canonical_unit"] == "m"
    assert prov_mm["quantization"] == "0.001m"
    
    prov_cm = get_provenance_dict("cm")
    assert prov_cm["conversion_applied"] == "cm_to_m"
    
    prov_m = get_provenance_dict("m")
    assert prov_m["conversion_applied"] == "m_to_m"
