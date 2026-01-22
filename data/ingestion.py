#!/usr/bin/env python3
"""
Ingestion layer: Unit canonicalization to meters (m).

This module provides the canonical unit conversion function for the ingestion phase.
All processed/canonical data MUST be in meters (m) with 0.001m (1mm) resolution.

Contract: UNIT_STANDARD.md
"""

from typing import Literal, Union
import numpy as np
from decimal import Decimal, ROUND_HALF_UP


def canonicalize_units_to_m(
    values: Union[float, np.ndarray, list],
    source_unit: Literal["mm", "cm", "m"],
    warnings: list[str],
) -> Union[float, np.ndarray]:
    """
    Convert values from source unit to meters (m) with 0.001m quantization.
    
    Args:
        values: Input values (scalar, array, or list)
        source_unit: Source unit ("mm", "cm", or "m")
        warnings: List to append warnings (mutated in-place)
    
    Returns:
        Values in meters (m), quantized to 0.001m resolution.
        Invalid values are converted to NaN.
    
    Provenance:
        - source_unit: Original unit
        - conversion_applied: e.g., "cm_to_m", "mm_to_m", "m_to_m"
        - canonical_unit: "m"
        - quantization: 0.001m (round-half-up)
    
    Contract Violation:
        - Invalid source_unit: values become NaN, UNIT_FAIL warning added
        - Invalid values (inf, -inf): become NaN, UNIT_FAIL warning added
        - No exceptions raised (NaN + warnings[] policy)
    """
    # Convert to numpy array for uniform handling
    is_scalar = isinstance(values, (float, int))
    if isinstance(values, (list, tuple)):
        values_arr = np.array(values, dtype=np.float64)
    elif isinstance(values, np.ndarray):
        values_arr = values.astype(np.float64)
    else:
        # Scalar
        values_arr = np.array([values], dtype=np.float64)
    
    # Check for invalid source_unit
    if source_unit not in ["mm", "cm", "m"]:
        warnings.append(f"UNIT_FAIL: Invalid source_unit '{source_unit}', expected 'mm', 'cm', or 'm'")
        result = np.full_like(values_arr, np.nan)
        return result[0] if is_scalar else result
    
    # Check for invalid values (inf, -inf)
    invalid_mask = ~np.isfinite(values_arr)
    if np.any(invalid_mask):
        warnings.append(f"UNIT_FAIL: {np.sum(invalid_mask)} invalid value(s) (inf/-inf) detected")
    
    # Convert to meters
    if source_unit == "mm":
        values_m = values_arr / 1000.0
        conversion_applied = "mm_to_m"
    elif source_unit == "cm":
        values_m = values_arr / 100.0
        conversion_applied = "cm_to_m"
    else:  # source_unit == "m"
        values_m = values_arr.copy()
        conversion_applied = "m_to_m"
    
    # Apply 0.001m quantization with round-half-up
    # Using Decimal for precise rounding
    quantized = np.array([
        float(Decimal(float(v)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))
        if np.isfinite(v) else np.nan
        for v in values_m
    ])
    
    # Replace invalid values with NaN
    quantized[invalid_mask] = np.nan
    
    # Provenance is recorded via warnings (fact recording, no judgment)
    # In practice, provenance should be stored in metadata structures
    # For now, we record the conversion in warnings for debugging
    if conversion_applied != "m_to_m":
        warnings.append(f"PROVENANCE: {conversion_applied}, quantization=0.001m")
    
    if is_scalar:
        return float(quantized[0])
    else:
        return quantized


def get_provenance_dict(
    source_unit: Literal["mm", "cm", "m"],
) -> dict[str, str]:
    """
    Generate provenance metadata for unit conversion.
    
    Args:
        source_unit: Source unit
    
    Returns:
        Dictionary with provenance fields:
        - source_unit: Original unit
        - conversion_applied: Conversion operation (e.g., "cm_to_m")
        - canonical_unit: "m"
        - quantization: "0.001m"
    """
    if source_unit == "mm":
        conversion_applied = "mm_to_m"
    elif source_unit == "cm":
        conversion_applied = "cm_to_m"
    else:  # source_unit == "m"
        conversion_applied = "m_to_m"
    
    return {
        "source_unit": source_unit,
        "conversion_applied": conversion_applied,
        "canonical_unit": "m",
        "quantization": "0.001m",
    }
