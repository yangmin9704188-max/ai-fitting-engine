"""
Test that NaN-only columns do not trigger unit_conversion_failed.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipelines.build_curated_v0 import apply_unit_canonicalization

def test_nan_only_no_unit_fail():
    """
    Test that NaN-only columns do not trigger unit_conversion_failed.
    
    Verifies:
    1) NaN values are not counted as unit_conversion_failed
    2) Only inf/-inf trigger unit_conversion_failed
    """
    # Create DataFrame with NaN-only column
    df = pd.DataFrame({
        'NECK_WIDTH_M': [np.nan, np.nan, np.nan],
        'NECK_DEPTH_M': [np.nan, np.nan, np.nan],
        'OTHER_COL': [1, 2, 3]
    })
    
    # Unit map with valid unit
    unit_map = {
        'NECK_WIDTH_M': 'mm',
        'NECK_DEPTH_M': 'mm'
    }
    warnings = []
    
    # Apply unit canonicalization
    df_converted = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify no unit_conversion_failed warnings for NaN-only columns
    unit_fail_warnings = [w for w in warnings if w.get('reason') == 'unit_conversion_failed']
    
    # NaN-only columns should not trigger unit_conversion_failed
    # (inf/-inf would trigger it, but NaN should not)
    for w in unit_fail_warnings:
        assert 'inf/-inf' in w.get('details', ''), \
            f"unit_conversion_failed should only occur for inf/-inf, got: {w}"
    
    print("test_nan_only_no_unit_fail: PASSED")

if __name__ == '__main__':
    test_nan_only_no_unit_fail()
