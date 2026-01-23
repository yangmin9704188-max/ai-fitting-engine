"""
Test that 8th unitless fallback applies to expected_unit='m' keys including _REF.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipelines.build_curated_v0 import apply_unit_canonicalization

def test_8th_fallback_chest_circ_m_ref():
    """
    Test that CHEST_CIRC_M_REF (expected_unit='m' but _REF suffix) gets 8th fallback.
    
    Verifies:
    1) CHEST_CIRC_M_REF gets mm->m fallback for 8th_direct/8th_3d
    2) Fallback applies to all _M suffix keys (expected_unit='m')
    """
    # Create DataFrame with CHEST_CIRC_M_REF in mm (unitless)
    df = pd.DataFrame({
        'CHEST_CIRC_M_REF': [900.0, 950.0, 1000.0],  # mm values
        'NECK_WIDTH_M': [100.0, 110.0, 120.0],  # mm values
        'OTHER_COL': [1, 2, 3]
    })
    
    # Unit map without CHEST_CIRC_M_REF (unitless)
    unit_map = {
        'NECK_WIDTH_M': None  # Also unitless to test fallback
    }
    warnings = []
    
    # Test with 8th_direct source
    df_converted_8th = apply_unit_canonicalization(df, unit_map, warnings, source_key='8th_direct')
    
    # Verify CHEST_CIRC_M_REF was converted (mm->m, ÷1000)
    chest_values = df_converted_8th['CHEST_CIRC_M_REF'].values
    assert not np.isnan(chest_values[0]), "CHEST_CIRC_M_REF should not be NaN after fallback"
    assert abs(chest_values[0] - 0.9) < 0.001, \
        f"CHEST_CIRC_M_REF should be ~0.9m (900mm/1000), got {chest_values[0]}"
    
    # Verify NECK_WIDTH_M was also converted
    neck_values = df_converted_8th['NECK_WIDTH_M'].values
    assert not np.isnan(neck_values[0]), "NECK_WIDTH_M should not be NaN after fallback"
    assert abs(neck_values[0] - 0.1) < 0.001, \
        f"NECK_WIDTH_M should be ~0.1m (100mm/1000), got {neck_values[0]}"
    
    # Verify UNIT_DEFAULT_MM_NO_UNIT warnings were recorded
    unit_default_warnings = [w for w in warnings if 'UNIT_DEFAULT_MM_NO_UNIT' in str(w.get('details', ''))]
    assert len(unit_default_warnings) >= 2, \
        f"Should have at least 2 UNIT_DEFAULT_MM_NO_UNIT warnings, got {len(unit_default_warnings)}"
    
    # Verify CHEST_CIRC_M_REF is in warnings
    chest_warnings = [w for w in unit_default_warnings if w.get('column') == 'CHEST_CIRC_M_REF']
    assert len(chest_warnings) > 0, "CHEST_CIRC_M_REF should have UNIT_DEFAULT_MM_NO_UNIT warning"
    
    print("test_8th_fallback_chest_circ_m_ref: PASSED")

if __name__ == '__main__':
    test_8th_fallback_chest_circ_m_ref()
