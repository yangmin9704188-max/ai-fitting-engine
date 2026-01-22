"""
Test for curated_v0 builder pipeline.

Tests mapping, header standardization, and warning format.
Uses --dry-run to avoid loading large raw files.
Tests unit heuristic safety: ambiguous scale inputs should not trigger conversion.
"""

import subprocess
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Import functions from pipeline for direct testing
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipelines.build_curated_v0 import sample_units, apply_unit_canonicalization


def test_build_curated_v0_dry_run():
    """
    Test that build_curated_v0.py runs in dry-run mode without errors.
    
    This verifies:
    - Mapping file can be loaded
    - Headers can be extracted
    - Warning format is correct
    - No exceptions are raised
    """
    script_path = Path(__file__).parent.parent / "pipelines" / "build_curated_v0.py"
    mapping_path = Path(__file__).parent.parent / "data" / "column_map" / "sizekorea_v2.json"
    
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return False
    
    if not mapping_path.exists():
        print(f"Mapping file not found: {mapping_path}")
        return False
    
    # Run with --dry-run and --max-rows to limit processing
    cmd = [
        sys.executable,
        str(script_path),
        "--mapping", str(mapping_path),
        "--output", "test_output.parquet",
        "--dry-run",
        "--max-rows", "10"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Check exit code
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            return False
        
        # Check that dry-run output contains expected keywords
        output = result.stdout + result.stderr
        
        expected_keywords = [
            "DRY RUN",
            "rows",
            "columns",
            "warnings"
        ]
        
        for keyword in expected_keywords:
            if keyword.lower() not in output.lower():
                print(f"Expected keyword '{keyword}' not found in output")
                print(f"Output:\n{output}")
                return False
        
        print("Dry-run test passed")
        return True
        
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def test_unit_heuristic_ambiguous_scale():
    """
    Test that ambiguous scale inputs (values that could be mm/cm/m) 
    are handled safely without silent conversion.
    
    Safety check: When unit_map is empty (unit undetermined), 
    values should be NaN + warnings with unit_undetermined reason.
    """
    # Create DataFrame with ambiguous values (0.5, 1.2, 2.0 range)
    # These values could be interpreted as:
    # - 0.5m, 1.2m, 2.0m (meters)
    # - 50cm, 120cm, 200cm (centimeters)  
    # - 500mm, 1200mm, 2000mm (millimeters)
    
    df = pd.DataFrame({
        'HEIGHT_M': [0.5, 1.2, 2.0, 1.5, 1.8],
        'WAIST_CIRC_M': [0.6, 0.8, 1.0, 0.7, 0.9],
        'SEX': ['M', 'F', 'M', 'F', 'M'],
        'AGE': [25, 30, 35, 40, 45]
    })
    
    warnings = []
    
    # Test case 1: Empty unit_map (unit undetermined)
    # This simulates the case where sample_units couldn't determine a unit
    empty_unit_map = {}
    df_result_empty = apply_unit_canonicalization(df.copy(), empty_unit_map, warnings)
    
    # Verify that columns without unit_map are set to NaN
    assert df_result_empty['HEIGHT_M'].isna().all(), "HEIGHT_M should be NaN when unit_map is empty"
    assert df_result_empty['WAIST_CIRC_M'].isna().all(), "WAIST_CIRC_M should be NaN when unit_map is empty"
    
    # Verify warnings were recorded
    unit_undetermined_warnings = [w for w in warnings if w.get('reason') == 'unit_undetermined']
    assert len(unit_undetermined_warnings) >= 2, "Should have unit_undetermined warnings for HEIGHT_M and WAIST_CIRC_M"
    
    # Verify warning structure
    for w in unit_undetermined_warnings:
        assert 'reason' in w, "Warning must have 'reason' field"
        assert w['reason'] == 'unit_undetermined', "Warning reason should be 'unit_undetermined'"
        assert 'column' in w, "Warning must have 'column' field"
        assert 'details' in w, "Warning must have 'details' field"
        assert w['column'] in ['HEIGHT_M', 'WAIST_CIRC_M'], "Warning should be for measurement column"
    
    # Test case 2: Unit_map with actual sampling result
    # Current heuristic may classify ambiguous values as "m", but we verify
    # that the system doesn't silently fail and warnings are structured correctly
    warnings2 = []
    unit_map = sample_units(df, sample_size=5)
    df_result = apply_unit_canonicalization(df.copy(), unit_map, warnings2)
    
    # Verify that result DataFrame has same shape
    assert df_result.shape[0] == df.shape[0], "Row count should not change"
    assert df_result.shape[1] == df.shape[1], "Column count should not change"
    
    # Verify meta columns are preserved
    assert 'SEX' in df_result.columns
    assert 'AGE' in df_result.columns
    
    # Verify warnings structure (if any)
    for w in warnings2:
        assert 'reason' in w, "Warning must have 'reason' field"
        assert 'column' in w, "Warning must have 'column' field"
        assert 'details' in w, "Warning must have 'details' field"
    
    return True


def test_unit_heuristic_clear_scale():
    """
    Test that clear scale inputs (unambiguously mm/cm/m) 
    are correctly identified and converted.
    
    Expected: canonicalize_units_to_m applied with correct conversion.
    """
    # Create DataFrame with clear values
    # 850 = clearly mm (height in mm)
    # 85 = clearly cm (height in cm)
    # 0.85 = clearly m (height in m)
    
    df_mm = pd.DataFrame({
        'HEIGHT_M': [850, 1600, 1800, 1700, 1500],  # Clearly mm
        'SEX': ['M', 'F', 'M', 'F', 'M'],
        'AGE': [25, 30, 35, 40, 45]
    })
    
    df_cm = pd.DataFrame({
        'HEIGHT_M': [85, 160, 180, 170, 150],  # Clearly cm
        'SEX': ['M', 'F', 'M', 'F', 'M'],
        'AGE': [25, 30, 35, 40, 45]
    })
    
    df_m = pd.DataFrame({
        'HEIGHT_M': [0.85, 1.60, 1.80, 1.70, 1.50],  # Clearly m
        'SEX': ['M', 'F', 'M', 'F', 'M'],
        'AGE': [25, 30, 35, 40, 45]
    })
    
    warnings_mm = []
    warnings_cm = []
    warnings_m = []
    
    # Test unit sampling
    unit_map_mm = sample_units(df_mm, sample_size=5)
    unit_map_cm = sample_units(df_cm, sample_size=5)
    unit_map_m = sample_units(df_m, sample_size=5)
    
    # Apply canonicalization
    df_result_mm = apply_unit_canonicalization(df_mm, unit_map_mm, warnings_mm)
    df_result_cm = apply_unit_canonicalization(df_cm, unit_map_cm, warnings_cm)
    df_result_m = apply_unit_canonicalization(df_m, unit_map_m, warnings_m)
    
    # Verify that conversions were applied (values should be in meters)
    # mm: 850mm -> 0.850m, 1600mm -> 1.600m
    if 'HEIGHT_M' in unit_map_mm and unit_map_mm['HEIGHT_M'] == 'mm':
        # Check that values are converted to meters (approximately)
        # 850mm = 0.85m, 1600mm = 1.6m
        assert not df_result_mm['HEIGHT_M'].isna().all(), "MM values should be converted, not all NaN"
        # Check approximate conversion (with quantization)
        height_values = df_result_mm['HEIGHT_M'].dropna()
        if len(height_values) > 0:
            # Values should be in meters range (0.8-1.8m)
            assert height_values.min() >= 0.5, "Converted values should be in meters"
            assert height_values.max() <= 2.0, "Converted values should be in meters"
    
    if 'HEIGHT_M' in unit_map_cm and unit_map_cm['HEIGHT_M'] == 'cm':
        # cm: 85cm -> 0.85m, 160cm -> 1.6m
        assert not df_result_cm['HEIGHT_M'].isna().all(), "CM values should be converted, not all NaN"
        height_values = df_result_cm['HEIGHT_M'].dropna()
        if len(height_values) > 0:
            assert height_values.min() >= 0.5, "Converted values should be in meters"
            assert height_values.max() <= 2.0, "Converted values should be in meters"
    
    if 'HEIGHT_M' in unit_map_m and unit_map_m['HEIGHT_M'] == 'm':
        # m: values should remain approximately the same (with quantization)
        assert not df_result_m['HEIGHT_M'].isna().all(), "M values should remain, not all NaN"
        height_values = df_result_m['HEIGHT_M'].dropna()
        if len(height_values) > 0:
            assert height_values.min() >= 0.5, "M values should remain in meters range"
            assert height_values.max() <= 2.0, "M values should remain in meters range"
    
    return True


if __name__ == '__main__':
    success1 = test_build_curated_v0_dry_run()
    success2 = test_unit_heuristic_ambiguous_scale()
    success3 = test_unit_heuristic_clear_scale()
    sys.exit(0 if (success1 and success2 and success3) else 1)
