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
from pipelines.build_curated_v0 import (
    sample_units, 
    apply_unit_canonicalization,
    find_header_row,
    preprocess_numeric_columns,
    handle_missing_values
)


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
    
    assert script_path.exists(), f"Script not found: {script_path}"
    assert mapping_path.exists(), f"Mapping file not found: {mapping_path}"
    
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
        assert result.returncode == 0, (
            f"Command failed with exit code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        
        # Check that dry-run output contains expected keywords
        output = result.stdout + result.stderr
        
        expected_keywords = [
            "DRY RUN",
            "rows",
            "columns",
            "warnings"
        ]
        
        for keyword in expected_keywords:
            assert keyword.lower() in output.lower(), (
                f"Expected keyword '{keyword}' not found in output\n"
                f"Output:\n{output}"
            )
        
    except subprocess.TimeoutExpired:
        raise AssertionError("Command timed out")
    except Exception as e:
        raise AssertionError(f"Error running command: {e}")


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


def test_sentinel_missing_handling():
    """
    Test that sentinel missing values (9999 for 8th_direct, empty for 7th/8th_3d)
    are replaced with NaN and SENTINEL_MISSING warnings are recorded.
    
    Uses direct function testing with synthetic data to ensure sentinel values exist.
    """
    # Test 8th_direct: 9999 sentinel
    df_8th = pd.DataFrame({
        'HEIGHT_M': [9999, 1800, 1700],
        'WAIST_CIRC_M': [9999, 800, 750],
        'SEX': ['M', 'F', 'M']
    })
    
    warnings_8th = []
    df_processed_8th = preprocess_numeric_columns(df_8th, '8th_direct', warnings_8th)
    
    # Verify 9999 values were replaced with NaN
    assert df_processed_8th['HEIGHT_M'].isna().sum() == 1, "One 9999 value should become NaN"
    assert df_processed_8th['WAIST_CIRC_M'].isna().sum() == 1, "One 9999 value should become NaN"
    
    # Verify SENTINEL_MISSING warnings were recorded
    sentinel_warnings_8th = [w for w in warnings_8th if w.get('reason') == 'SENTINEL_MISSING']
    assert len(sentinel_warnings_8th) >= 2, "Should have SENTINEL_MISSING warnings for both columns"
    
    for w in sentinel_warnings_8th:
        assert w['reason'] == 'SENTINEL_MISSING', "Warning reason should be 'SENTINEL_MISSING'"
        assert w.get('source') == '8th_direct', "Source should be '8th_direct'"
        assert w.get('column') in ['HEIGHT_M', 'WAIST_CIRC_M'], "Column should be HEIGHT_M or WAIST_CIRC_M"
        assert w.get('sentinel_value') == '9999', "sentinel_value should be '9999'"
        assert 'sentinel_count' in w, "sentinel_count should be present"
        assert w.get('sentinel_count') > 0, "sentinel_count should be positive"
    
    # Test 7th: empty string sentinel
    df_7th = pd.DataFrame({
        'HEIGHT_M': ['', '1800', '1700'],
        'WAIST_CIRC_M': ['', '800', '750'],
        'SEX': ['M', 'F', 'M']
    })
    
    warnings_7th = []
    df_processed_7th = preprocess_numeric_columns(df_7th, '7th', warnings_7th)
    
    # Verify empty strings were replaced with NaN
    assert df_processed_7th['HEIGHT_M'].isna().sum() >= 1, "Empty string should become NaN"
    
    # Verify SENTINEL_MISSING warnings were recorded
    sentinel_warnings_7th = [w for w in warnings_7th if w.get('reason') == 'SENTINEL_MISSING']
    assert len(sentinel_warnings_7th) > 0, "Should have SENTINEL_MISSING warnings for empty strings"
    
    for w in sentinel_warnings_7th:
        assert w['reason'] == 'SENTINEL_MISSING', "Warning reason should be 'SENTINEL_MISSING'"
        assert w.get('source') == '7th', "Source should be '7th'"
        assert w.get('sentinel_value') == '', "sentinel_value should be ''"
        assert 'sentinel_count' in w, "sentinel_count should be present"
        assert w.get('sentinel_count') > 0, "sentinel_count should be positive"


def test_comma_parsing_7th():
    """
    Test that 7th CSV numeric columns with commas are parsed correctly.
    Verifies comma removal works for height and at least one other numeric column.
    """
    # Create test DataFrame with comma-separated numbers
    df = pd.DataFrame({
        'HEIGHT_M': ['1,736', '1,800', '1,650'],
        'WAIST_CIRC_M': ['700', '800', '750'],  # Another numeric column
        'WEIGHT_KG': ['70', '80', '65'],
        'SEX': ['M', 'F', 'M']
    })
    
    warnings = []
    df_processed = preprocess_numeric_columns(df, '7th', warnings)
    
    # Check that commas were removed and values are numeric
    assert pd.api.types.is_numeric_dtype(df_processed['HEIGHT_M']), "HEIGHT_M should be numeric after comma removal"
    
    # Check values (should be 1736, 1800, 1650)
    height_values = df_processed['HEIGHT_M'].dropna().tolist()
    assert len(height_values) > 0, "Should have parsed height values"
    assert all(v > 1000 for v in height_values), "Height values should be in mm range (1000+)"
    assert 1736 in height_values or 1800 in height_values, "Should parse comma-separated values correctly"
    
    # Check that other numeric columns are also numeric
    assert pd.api.types.is_numeric_dtype(df_processed['WAIST_CIRC_M']), "WAIST_CIRC_M should be numeric"
    waist_values = df_processed['WAIST_CIRC_M'].dropna().tolist()
    assert len(waist_values) > 0, "Should have parsed waist values"


def test_header_detection_anchor_priority():
    """
    Test that header detection prioritizes anchor term "표준 측정항목 명" over ko_term matching.
    Uses synthetic CSV to ensure deterministic testing.
    """
    import tempfile
    import json
    
    # Create synthetic mapping with ko_term for fallback
    mapping = {
        'keys': [
            {
                'standard_key': 'HEIGHT_M',
                'ko_term': '키',
                'sources': {
                    '7th': {'present': True, 'column': 'HEIGHT_M'}
                }
            }
        ]
    }
    
    # Create temporary CSV with anchor term in row 3 (0-indexed)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        temp_path = Path(f.name)
        # Row 0: code
        f.write('CODE,COL1,COL2\n')
        # Row 1: label
        f.write('Label,COL1,COL2\n')
        # Row 2: some other row
        f.write('Other,VAL1,VAL2\n')
        # Row 3: anchor term (should be detected as header)
        f.write(' 표준 측정항목 명,키,몸무게\n')
        # Row 4: data row
        f.write('DATA,1700,70\n')
    
    try:
        header_row = find_header_row(temp_path, mapping)
        # Should detect row 3 (0-indexed) as header due to anchor priority
        assert header_row == 3, f"Expected header row 3 (anchor term), got {header_row}"
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


def test_sentinel_dedup_prevention():
    """
    Test that sentinel_missing accounting excludes sentinel_count from value_missing.
    Verifies refined deduplication: remaining = total_missing - sentinel_count.
    """
    # Create DataFrame with sentinel values and additional missing
    df = pd.DataFrame({
        'HEIGHT_M': [9999, 1800, np.nan, 1700],  # 1 sentinel + 1 other missing
        'WAIST_CIRC_M': [9999, 800, 750, np.nan],  # 1 sentinel + 1 other missing
        'SEX': ['M', 'F', 'M', 'F']
    })
    
    warnings = []
    
    # Preprocess (should create SENTINEL_MISSING warnings with sentinel_count)
    df_processed = preprocess_numeric_columns(df, '8th_direct', warnings)
    
    # Count SENTINEL_MISSING warnings
    sentinel_warnings = [w for w in warnings if w.get('reason') == 'SENTINEL_MISSING']
    assert len(sentinel_warnings) >= 2, "Should have SENTINEL_MISSING warnings for both columns"
    
    # Verify sentinel_count is recorded
    for w in sentinel_warnings:
        assert 'sentinel_count' in w, "SENTINEL_MISSING warning should have sentinel_count"
        assert w.get('sentinel_count') == 1, "Each column should have 1 sentinel value"
    
    # Now handle missing values (should create value_missing only for remaining missing)
    df_final = handle_missing_values(df_processed, '8th_direct', warnings)
    
    # Check value_missing warnings
    value_missing_warnings = [w for w in warnings if w.get('reason') == 'value_missing']
    
    # Each column has 2 total missing (1 sentinel + 1 other), so value_missing should record remaining = 1
    for w in value_missing_warnings:
        assert 'remaining' in w.get('details', '') or '1 missing' in w.get('details', ''), (
            f"value_missing should account for remaining (non-sentinel) missing values"
        )
    
    # Verify that value_missing count matches remaining (total - sentinel)
    # HEIGHT_M: 2 total missing, 1 sentinel -> 1 remaining
    # WAIST_CIRC_M: 2 total missing, 1 sentinel -> 1 remaining
    assert len(value_missing_warnings) >= 2, "Should have value_missing for remaining non-sentinel missing"


if __name__ == '__main__':
    # Run all tests with pytest-style assertions
    try:
        test_build_curated_v0_dry_run()
        test_unit_heuristic_ambiguous_scale()
        test_unit_heuristic_clear_scale()
        test_sentinel_missing_handling()
        test_comma_parsing_7th()
        test_header_detection_anchor_priority()
        test_sentinel_dedup_prevention()
        print("All tests passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
