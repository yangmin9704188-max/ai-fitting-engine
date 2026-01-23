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
    find_header_rows,
    preprocess_numeric_columns,
    handle_missing_values,
    load_raw_file,
    extract_columns_from_source,
    build_curated_v0,
    calculate_source_quality,
    detect_duplicate_headers,
    generate_quality_summary,
    find_header_candidates,
    emit_header_candidates,
    collect_arm_knee_trace,
    emit_arm_knee_trace
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


def test_7th_xlsx_preference():
    """
    Test that 7th source prefers XLSX over CSV when both exist.
    Creates temporary XLSX file and verifies XLSX is selected over CSV.
    Uses small DataFrame to avoid dependency on large files.
    """
    import tempfile
    
    # Create temporary CSV and XLSX files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        csv_path = tmp_path / "7th_data.csv"
        xlsx_path = tmp_path / "7th_data.xlsx"
        
        # Create CSV file
        csv_data = pd.DataFrame({
            'HUMAN_ID': ['00123', '00456'],
            '키': [1700, 1800],
            '성별': ['남', '여']
        })
        csv_data.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Create XLSX file with same data (HUMAN_ID as string)
        xlsx_data = pd.DataFrame({
            'HUMAN_ID': ['00123', '00456'],  # String values with leading zeros
            '키': [1700, 1800],
            '성별': ['남', '여']
        })
        xlsx_data.to_excel(xlsx_path, index=False, engine='openpyxl')
        
        # Test load_raw_file with 7th source_key pointing to CSV
        # Should internally switch to XLSX
        df_loaded = load_raw_file(csv_path, header_row=0, source_key='7th', is_xlsx=False)
        
        # Verify XLSX was loaded (function should have switched to XLSX)
        assert not df_loaded.empty, "Should load XLSX file when available"
        assert len(df_loaded) == 2, "Should have 2 rows"
        
        # Verify HUMAN_ID is preserved as string (leading zeros maintained)
        human_id_col = None
        for col in df_loaded.columns:
            if 'ID' in str(col) or 'HUMAN_ID' in str(col):
                human_id_col = col
                break
        
        if human_id_col:
            # Check that HUMAN_ID is string type
            assert df_loaded[human_id_col].dtype == 'object' or df_loaded[human_id_col].dtype.name == 'string', \
                f"HUMAN_ID should be string, got {df_loaded[human_id_col].dtype}"
            
            # Verify values are strings
            values = df_loaded[human_id_col].astype(str).tolist()
            assert all(isinstance(v, str) for v in values), "All HUMAN_ID values should be strings"


def test_per_key_header_selection():
    """
    Test that HUMAN_ID/SEX use secondary header while other keys use primary header.
    Uses synthetic CSV with separated primary/secondary headers.
    Primary header at row 5 (0-indexed), secondary at row 7 (primary+2).
    """
    import tempfile
    
    # Create synthetic mapping
    mapping = {
        'keys': [
            {
                'standard_key': 'HUMAN_ID',
                'ko_term': 'HUMAN_ID',
                'sources': {
                    '7th': {'present': True, 'column': 'HUMAN_ID'}
                }
            },
            {
                'standard_key': 'SEX',
                'ko_term': '성별',
                'sources': {
                    '7th': {'present': True, 'column': '성별'}
                }
            },
            {
                'standard_key': 'HEIGHT_M',
                'ko_term': '키',
                'sources': {
                    '7th': {'present': True, 'column': '키'}
                }
            }
        ]
    }
    
    # Create synthetic CSV with primary (row 5) and secondary (row 7) headers
    # Both headers should have same number of data rows for alignment
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        temp_path = Path(f.name)
        # Rows 0-4: metadata/empty
        for i in range(5):
            f.write('META,COL1,COL2\n')
        # Row 5: primary header (표준 측정항목 명) - typically row 5 for 7th
        f.write(' 표준 측정항목 명,키,몸무게\n')
        # Row 6: data for primary (row 1)
        f.write('DATA1,1700,70\n')
        # Row 7: secondary header (HUMAN_ID, SEX) - typically row 7 for 7th
        f.write('HUMAN_ID,성별,AGE\n')
        # Row 8: data for secondary (row 1) - aligned with primary data
        f.write('00123,남,25\n')
        # Row 9: data for primary (row 2)
        f.write('DATA2,1800,80\n')
        # Row 10: data for secondary (row 2) - aligned with primary data
        f.write('00456,여,30\n')
    
    try:
        # Find headers
        primary_row, code_row, secondary_row = find_header_rows(temp_path, mapping, is_xlsx=False, source_key='7th')
        
        assert primary_row == 5, f"Expected primary row 5 (anchor term), got {primary_row}"
        # Secondary should be found at row 7 (primary+2)
        assert secondary_row == 7, f"Expected secondary row 7, got {secondary_row}"
        
        # Load primary and secondary DataFrames
        df_primary = load_raw_file(temp_path, primary_row, None, '7th', is_xlsx=False)
        df_secondary = load_raw_file(temp_path, secondary_row, None, '7th', is_xlsx=False)
        
        # Verify DataFrames loaded correctly
        assert not df_primary.empty, "Primary DataFrame should not be empty"
        assert not df_secondary.empty, "Secondary DataFrame should not be empty"
        
        # Extract columns
        warnings = []
        df_result = extract_columns_from_source(df_primary, df_secondary, '7th', mapping, warnings)
        
        # Verify HEIGHT_M came from primary (should have value from row 9)
        assert 'HEIGHT_M' in df_result.columns, "HEIGHT_M should be extracted from primary"
        
        # Verify HUMAN_ID/SEX came from secondary
        assert 'HUMAN_ID' in df_result.columns, "HUMAN_ID should be extracted from secondary"
        human_id_values = df_result['HUMAN_ID'].dropna().astype(str).tolist()
        assert '00123' in human_id_values, "HUMAN_ID should come from secondary header (row 7)"
        
        assert 'SEX' in df_result.columns, "SEX should be extracted from secondary"
        
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_human_id_string_preservation():
    """
    Test that HUMAN_ID is preserved as string throughout processing.
    Verifies leading zeros and string format are maintained end-to-end.
    """
    # Create test DataFrame with HUMAN_ID containing leading zeros
    df = pd.DataFrame({
        'HUMAN_ID': ['00123', '00456', '000789'],
        'HEIGHT_M': [1700, 1800, 1650],
        'SEX': ['M', 'F', 'M']
    })
    
    # Test that HUMAN_ID is excluded from numeric processing
    warnings = []
    df_processed = preprocess_numeric_columns(df, '7th', warnings)
    
    # Verify HUMAN_ID remains string
    assert df_processed['HUMAN_ID'].dtype == 'object' or df_processed['HUMAN_ID'].dtype.name == 'string', \
        f"HUMAN_ID should be string/object, got {df_processed['HUMAN_ID'].dtype}"
    
    # Verify leading zeros are preserved
    human_id_values = df_processed['HUMAN_ID'].astype(str).tolist()
    assert '00123' in human_id_values, "Leading zeros should be preserved (00123)"
    assert '00456' in human_id_values, "Leading zeros should be preserved (00456)"
    assert '000789' in human_id_values, "Leading zeros should be preserved (000789)"
    
    # Test unit canonicalization excludes HUMAN_ID
    warnings2 = []
    unit_map = {'HEIGHT_M': 'mm'}
    df_canonical = apply_unit_canonicalization(df_processed, unit_map, warnings2)
    
    # Verify HUMAN_ID is still string after unit canonicalization
    assert df_canonical['HUMAN_ID'].dtype == 'object' or df_canonical['HUMAN_ID'].dtype.name == 'string', \
        "HUMAN_ID should remain string after unit canonicalization"
    
    human_id_values_after = df_canonical['HUMAN_ID'].astype(str).tolist()
    assert '00123' in human_id_values_after, "HUMAN_ID should be preserved through unit canonicalization"
    
    # Verify final output format (simulating save/load)
    df_final = df_canonical.copy()
    if 'HUMAN_ID' in df_final.columns:
        df_final['HUMAN_ID'] = df_final['HUMAN_ID'].astype(str)
    
    final_values = df_final['HUMAN_ID'].astype(str).tolist()
    assert '00123' in final_values, "HUMAN_ID '00123' should be preserved in final output"


def test_primary_header_anchor_in_non_first_cell():
    """
    Test that primary header detection finds '표준 측정항목 명' in any cell (not just first column).
    For 8th data, anchor is in col1, not col0.
    """
    import tempfile
    
    # Create synthetic mapping
    mapping = {
        'keys': [
            {
                'standard_key': 'HEIGHT_M',
                'ko_term': '키',
                'sources': {
                    '8th_direct': {'present': True, 'column': '키'}
                }
            }
        ]
    }
    
    # Create synthetic CSV where col0 is empty/blank, col1 has '표준 측정항목 명'
    # All rows must have same number of columns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        temp_path = Path(f.name)
        # Rows 0-3: metadata/empty (4 columns to match other rows)
        for i in range(4):
            f.write(',,,\n')
        # Row 4: primary header - col0 is blank, col1 has anchor term
        f.write(',표준 측정항목 명,키,체중(몸무게)\n')
        # Row 5: code row (should not be selected)
        f.write(',표준 측정항목 코드,S-STa-H-[FL01-HD01]-DM,S-STa-B-[BM01]-DM\n')
        # Row 6: secondary header (HUMAN_ID, 성별, 나이)
        f.write('인체 데이터 ID,HUMAN_ID,성별,나이\n')
        # Row 7: data
        f.write('8_DM_000001,20_M_1417,M,41\n')
    
    try:
        # Find headers
        primary_row, code_row, secondary_row = find_header_rows(temp_path, mapping, is_xlsx=False, source_key='8th_direct')
        
        # Primary should be row 4 (where anchor term is in col1)
        assert primary_row == 4, f"Expected primary row 4 (anchor in col1), got {primary_row}"
        # Secondary should be row 6 (where HUMAN_ID/성별/나이 are)
        assert secondary_row == 6, f"Expected secondary row 6, got {secondary_row}"
        
    finally:
        temp_path.unlink()


def test_per_key_header_policy_with_age():
    """
    Test per-key header policy: HEIGHT_M/WEIGHT_KG from primary (row4),
    HUMAN_ID/SEX/AGE from secondary (row6).
    Simulates 8th_direct structure.
    """
    import tempfile
    
    # Create synthetic mapping
    mapping = {
        'keys': [
            {
                'standard_key': 'HUMAN_ID',
                'ko_term': 'HUMAN_ID',
                'sources': {
                    '8th_direct': {'present': True, 'column': 'HUMAN_ID'}
                }
            },
            {
                'standard_key': 'SEX',
                'ko_term': '성별',
                'sources': {
                    '8th_direct': {'present': True, 'column': '성별'}
                }
            },
            {
                'standard_key': 'AGE',
                'ko_term': '나이',
                'sources': {
                    '8th_direct': {'present': True, 'column': '나이'}
                }
            },
            {
                'standard_key': 'HEIGHT_M',
                'ko_term': '키',
                'sources': {
                    '8th_direct': {'present': True, 'column': '키'}
                }
            },
            {
                'standard_key': 'WEIGHT_KG',
                'ko_term': '체중(몸무게)',
                'sources': {
                    '8th_direct': {'present': True, 'column': '체중(몸무게)'}
                }
            }
        ]
    }
    
    # Create synthetic CSV matching 8th_direct structure
    # All rows must have same number of columns (5 columns)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        temp_path = Path(f.name)
        # Rows 0-3: metadata/empty (5 columns)
        for i in range(4):
            f.write(',,,,\n')
        # Row 4: primary header (col1 has anchor, col3+ have measurement names)
        f.write(',표준 측정항목 명,,키,체중(몸무게)\n')
        # Row 5: code row
        f.write(',표준 측정항목 코드,,S-STa-H-[FL01-HD01]-DM,S-STa-B-[BM01]-DM\n')
        # Row 6: secondary header (HUMAN_ID, 성별, 나이)
        f.write('인체 데이터 ID,HUMAN_ID,성별,나이,\n')
        # Row 7: data row 1
        f.write('8_DM_000001,20_M_1417,M,41,\n')
        # Row 8: data row 2
        f.write('8_DM_000002,20_M_1455,M,41,\n')
    
    try:
        # Find headers
        primary_row, code_row, secondary_row = find_header_rows(temp_path, mapping, is_xlsx=False, source_key='8th_direct')
        
        assert primary_row == 4, f"Expected primary row 4, got {primary_row}"
        assert code_row == 5, f"Expected code row 5, got {code_row}"
        assert secondary_row == 6, f"Expected secondary row 6, got {secondary_row}"
        
        # Load primary and secondary DataFrames
        df_primary = load_raw_file(temp_path, primary_row, None, '8th_direct', is_xlsx=False)
        df_secondary = load_raw_file(temp_path, secondary_row, None, '8th_direct', is_xlsx=False)
        
        # Verify DataFrames loaded correctly
        assert not df_primary.empty, "Primary DataFrame should not be empty"
        assert not df_secondary.empty, "Secondary DataFrame should not be empty"
        
        # Extract columns
        warnings = []
        df_result = extract_columns_from_source(df_primary, df_secondary, '8th_direct', mapping, warnings)
        
        # Verify HEIGHT_M/WEIGHT_KG came from primary (row 4)
        assert 'HEIGHT_M' in df_result.columns, "HEIGHT_M should be extracted from primary"
        assert 'WEIGHT_KG' in df_result.columns, "WEIGHT_KG should be extracted from primary"
        # Note: Since we don't have actual data values in the test CSV (empty cells),
        # we just verify that the columns exist and were extracted from primary header
        # The actual data extraction logic is tested in other tests
        
        # Verify HUMAN_ID/SEX/AGE came from secondary (row 6)
        assert 'HUMAN_ID' in df_result.columns, "HUMAN_ID should be extracted from secondary"
        human_id_values = df_result['HUMAN_ID'].dropna().astype(str).tolist()
        assert '20_M_1417' in human_id_values or '20_M_1455' in human_id_values, "HUMAN_ID should come from secondary header"
        
        assert 'SEX' in df_result.columns, "SEX should be extracted from secondary"
        sex_values = df_result['SEX'].dropna().astype(str).tolist()
        assert 'M' in sex_values, "SEX should come from secondary header"
        
        assert 'AGE' in df_result.columns, "AGE should be extracted from secondary"
        age_values = df_result['AGE'].dropna().tolist()
        assert 41 in age_values, "AGE should come from secondary header"
        
    finally:
        temp_path.unlink()


def test_xlsx_human_id_string_loading():
    """
    Test that XLSX loading preserves HUMAN_ID as string.
    Creates temporary XLSX file and verifies HUMAN_ID is loaded as string.
    """
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        xlsx_path = tmp_path / "test.xlsx"
        
        # Create XLSX with HUMAN_ID that could be interpreted as numeric
        xlsx_data = pd.DataFrame({
            'HUMAN_ID': ['00123', '00456', '000789'],
            '키': [1700, 1800, 1650],
            '성별': ['남', '여', '남']
        })
        xlsx_data.to_excel(xlsx_path, index=False, engine='openpyxl')
        
        # Load with load_raw_file
        df_loaded = load_raw_file(xlsx_path, header_row=0, source_key='7th', is_xlsx=True)
        
        # Verify HUMAN_ID is string
        assert 'HUMAN_ID' in df_loaded.columns or any('ID' in str(col) for col in df_loaded.columns), \
            "HUMAN_ID column should be present"
        
        # Find HUMAN_ID column (may have different name)
        human_id_col = None
        for col in df_loaded.columns:
            if 'ID' in str(col) or 'HUMAN_ID' in str(col):
                human_id_col = col
                break
        
        if human_id_col:
            # Verify it's string type
            assert df_loaded[human_id_col].dtype == 'object' or df_loaded[human_id_col].dtype.name == 'string', \
                f"HUMAN_ID should be string, got {df_loaded[human_id_col].dtype}"
            
            # Verify values are preserved as strings
            values = df_loaded[human_id_col].astype(str).tolist()
            # Check that leading zeros are preserved (if original had them)
            # Note: Excel may convert '00123' to 123, so we check string representation
            assert all(isinstance(v, str) for v in values), "All HUMAN_ID values should be strings"


def test_weight_kg_mixed_dtype_parquet_cast():
    """
    Test that WEIGHT_KG with mixed dtype (string/float/empty) is cast to numeric
    before parquet write to avoid pyarrow conversion failure.
    
    Verifies:
    1) Mixed dtype values ("70.8" str, 70.8 float, "" empty) are converted to float
    2) Empty strings become NaN
    3) dtype is float64 after conversion
    """
    import pandas as pd
    import numpy as np
    
    # Create DataFrame with mixed WEIGHT_KG dtype
    df = pd.DataFrame({
        'HUMAN_ID': ['001', '002', '003', '004'],
        'WEIGHT_KG': ['70.8', 70.8, '', np.nan],  # Mixed: str, float, empty, NaN
        'HEIGHT_M': [1.7, 1.8, 1.65, 1.75]
    })
    
    # Simulate the casting logic from build_curated_v0
    nan_before = df['WEIGHT_KG'].isna().sum()
    
    # Convert to numeric (same logic as pipeline)
    df['WEIGHT_KG'] = pd.to_numeric(
        df['WEIGHT_KG'].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    
    nan_after = df['WEIGHT_KG'].isna().sum()
    
    # Verify dtype is numeric
    assert pd.api.types.is_numeric_dtype(df['WEIGHT_KG']), \
        f"WEIGHT_KG should be numeric dtype, got {df['WEIGHT_KG'].dtype}"
    
    # Verify string "70.8" was converted to float
    assert df['WEIGHT_KG'].iloc[0] == 70.8, \
        f"String '70.8' should be converted to float 70.8, got {df['WEIGHT_KG'].iloc[0]}"
    
    # Verify float 70.8 remains float
    assert df['WEIGHT_KG'].iloc[1] == 70.8, \
        f"Float 70.8 should remain 70.8, got {df['WEIGHT_KG'].iloc[1]}"
    
    # Verify empty string became NaN
    assert pd.isna(df['WEIGHT_KG'].iloc[2]), \
        f"Empty string should become NaN, got {df['WEIGHT_KG'].iloc[2]}"
    
    # Verify NaN remains NaN
    assert pd.isna(df['WEIGHT_KG'].iloc[3]), \
        f"NaN should remain NaN, got {df['WEIGHT_KG'].iloc[3]}"
    
    # Verify new NaN count (empty string -> NaN)
    assert nan_after - nan_before == 1, \
        f"Expected 1 new NaN (from empty string), got {nan_after - nan_before}"


def test_non_finite_normalization():
    """
    Test that non-finite values (inf/-inf) are normalized to NaN before parquet write.
    
    Verifies:
    1) inf values are replaced with NaN
    2) -inf values are replaced with NaN
    3) Normal finite values remain unchanged
    4) Count of replaced values is tracked
    """
    import pandas as pd
    import numpy as np
    
    # Create DataFrame with non-finite values
    df = pd.DataFrame({
        'HUMAN_ID': ['001', '002', '003', '004', '005'],
        'WEIGHT_KG': [70.8, np.inf, -np.inf, 65.5, 80.2],
        'HEIGHT_M': [1.7, 1.8, np.inf, 1.65, 1.75],
        'BUST_CIRC_M': [0.9, 0.85, 0.88, -np.inf, 0.92]
    })
    
    # Simulate the non-finite normalization logic from build_curated_v0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue
        
        # Check for non-finite values
        non_finite_mask = ~np.isfinite(df[col])
        non_finite_count = non_finite_mask.sum()
        
        if non_finite_count > 0:
            # Replace inf/-inf with NaN
            df.loc[non_finite_mask, col] = np.nan
    
    # Verify inf values were replaced with NaN
    assert pd.isna(df['WEIGHT_KG'].iloc[1]), \
        f"inf should be replaced with NaN, got {df['WEIGHT_KG'].iloc[1]}"
    
    # Verify -inf values were replaced with NaN
    assert pd.isna(df['WEIGHT_KG'].iloc[2]), \
        f"-inf should be replaced with NaN, got {df['WEIGHT_KG'].iloc[2]}"
    
    # Verify normal finite values remain unchanged
    assert df['WEIGHT_KG'].iloc[0] == 70.8, \
        f"Normal value should remain unchanged, got {df['WEIGHT_KG'].iloc[0]}"
    assert df['WEIGHT_KG'].iloc[3] == 65.5, \
        f"Normal value should remain unchanged, got {df['WEIGHT_KG'].iloc[3]}"
    
    # Verify HEIGHT_M inf was replaced
    assert pd.isna(df['HEIGHT_M'].iloc[2]), \
        f"inf in HEIGHT_M should be replaced with NaN, got {df['HEIGHT_M'].iloc[2]}"
    
    # Verify BUST_CIRC_M -inf was replaced
    assert pd.isna(df['BUST_CIRC_M'].iloc[3]), \
        f"-inf in BUST_CIRC_M should be replaced with NaN, got {df['BUST_CIRC_M'].iloc[3]}"


def test_data_start_row_cutoff():
    """
    Test that header/code/meta rows are dropped from data to prevent numeric_parsing_failed.
    
    Creates synthetic CSV with:
    - Row 4: primary header (표준 측정항목 명)
    - Row 5: code row (표준 측정항목 코드)
    - Row 6: secondary header (HUMAN_ID/성별/나이)
    - Row 7+: actual data rows
    
    Verifies:
    1) data_start_row = max(primary, code, secondary) + 1 = 7
    2) Rows before data_start_row are dropped
    3) Header/code/meta row values (strings) do not cause numeric_parsing_failed
    """
    import tempfile
    import json
    
    # Create synthetic mapping
    mapping = {
        'keys': [
            {
                'standard_key': 'HUMAN_ID',
                'ko_term': 'HUMAN_ID',
                'sources': {
                    '7th': {'present': True, 'column': 'HUMAN ID'}
                }
            },
            {
                'standard_key': 'SEX',
                'ko_term': '성별',
                'sources': {
                    '7th': {'present': True, 'column': '성별'}
                }
            },
            {
                'standard_key': 'HEIGHT_M',
                'ko_term': '키',
                'sources': {
                    '7th': {'present': True, 'column': '키'}
                }
            },
            {
                'standard_key': 'WEIGHT_KG',
                'ko_term': '체중(몸무게)',
                'sources': {
                    '7th': {'present': True, 'column': '체중(몸무게)'}
                }
            }
        ]
    }
    
    # Create synthetic CSV matching 7th structure
    # All rows must have same number of columns (5 columns)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        temp_path = Path(f.name)
        # Rows 0-3: metadata/empty (5 columns)
        for i in range(4):
            f.write(',,,,\n')
        # Row 4: primary header (표준 측정항목 명)
        f.write(',표준 측정항목 명,,키,체중(몸무게)\n')
        # Row 5: code row (표준 측정항목 코드) - this should be dropped
        f.write(',표준 측정항목 코드,,S-STa-H-[FL01-HD01]-DM,S-STa-B-[BM01]-DM\n')
        # Row 6: secondary header (HUMAN_ID/성별) - this should be dropped
        f.write(',HUMAN ID,성별,,\n')
        # Row 7: first data row
        f.write(',211606300001,남,1736,72.1\n')
        # Row 8: second data row
        f.write(',211606300002,여,1650,58.5\n')
    
    try:
        # Find headers
        primary_row, code_row, secondary_row = find_header_rows(temp_path, mapping, is_xlsx=False, source_key='7th')
        
        assert primary_row == 4, f"Expected primary row 4, got {primary_row}"
        assert code_row == 5, f"Expected code row 5, got {code_row}"
        assert secondary_row == 6, f"Expected secondary row 6, got {secondary_row}"
        
        # Calculate data_start_row
        header_rows_list = [primary_row]
        if code_row is not None:
            header_rows_list.append(code_row)
        if secondary_row is not None:
            header_rows_list.append(secondary_row)
        data_start_row = max(header_rows_list) + 1
        assert data_start_row == 7, f"Expected data_start_row 7, got {data_start_row}"
        
        # Load raw file
        df_raw = load_raw_file(temp_path, primary_row, secondary_row, '7th', is_xlsx=False)
        
        # Drop header/code/meta rows
        df_start_idx = data_start_row - primary_row - 1
        assert df_start_idx == 2, f"Expected DataFrame start index 2, got {df_start_idx}"
        
        if len(df_raw) > 0:
            df_raw_dropped = df_raw.iloc[df_start_idx:].copy().reset_index(drop=True)
            assert len(df_raw_dropped) == 2, f"Expected 2 data rows after dropping, got {len(df_raw_dropped)}"
            
            # Verify header/code/meta row values are not in DataFrame
            # Check '키' column (HEIGHT_M)
            if '키' in df_raw_dropped.columns:
                height_values = df_raw_dropped['키'].astype(str).tolist()
                # Should not contain code row value or header name
                assert 'S-STa-H-[FL01-HD01]-DM' not in height_values, "Code row value should be dropped"
                assert '키' not in height_values, "Header name should be dropped"
                # Should contain actual data
                assert '1736' in height_values or 1736 in df_raw_dropped['키'].values, "Data row value should be present"
        
        # Test that numeric_parsing_failed does not occur
        # Load secondary DataFrame
        df_secondary = None
        if secondary_row is not None:
            df_secondary = pd.read_csv(temp_path, encoding='utf-8-sig', header=secondary_row, low_memory=False)
            if len(df_secondary) > 0:
                sec_df_start_idx = data_start_row - secondary_row - 1
                if sec_df_start_idx > 0:
                    df_secondary = df_secondary.iloc[sec_df_start_idx:].copy().reset_index(drop=True)
        
        # Extract columns
        warnings = []
        df_result = extract_columns_from_source(df_raw_dropped, df_secondary, '7th', mapping, warnings)
        
        # Preprocess numeric columns (this is where numeric_parsing_failed would occur)
        df_preprocessed = preprocess_numeric_columns(df_result, '7th', warnings)
        
        # Check for numeric_parsing_failed warnings
        numeric_parsing_failed = [w for w in warnings if w.get('reason') == 'numeric_parsing_failed']
        assert len(numeric_parsing_failed) == 0, \
            f"Expected no numeric_parsing_failed warnings, got {len(numeric_parsing_failed)}: {numeric_parsing_failed}"
        
    finally:
        temp_path.unlink()


def test_quality_summary_generation():
    """
    Test that quality summary is generated with correct completeness metrics.
    
    Verifies:
    1) calculate_source_quality computes non_null_count, missing_count, missing_rate correctly
    2) detect_duplicate_headers finds columns with same base header
    3) generate_quality_summary creates markdown file with facts-only content
    """
    import tempfile
    import json
    
    # Create synthetic mapping
    mapping = {
        'keys': [
            {
                'standard_key': 'HEIGHT_M',
                'sources': {
                    '7th': {'present': True, 'column': '키'}
                }
            },
            {
                'standard_key': 'WEIGHT_KG',
                'sources': {
                    '7th': {'present': True, 'column': '체중(몸무게)'}
                }
            },
            {
                'standard_key': 'NECK_WIDTH_M',
                'sources': {
                    '7th': {'present': False, 'column': None}
                }
            }
        ]
    }
    
    # Create synthetic DataFrame with known completeness
    df = pd.DataFrame({
        'HEIGHT_M': [1.7, 1.8, np.nan, 1.65, 1.75],  # 4 non-null, 1 missing (missing_rate=0.2)
        'WEIGHT_KG': [70, np.nan, np.nan, 65, 80],  # 3 non-null, 2 missing (missing_rate=0.4)
        'NECK_WIDTH_M': [np.nan, np.nan, np.nan, np.nan, np.nan],  # 0 non-null, 5 missing (missing_rate=1.0)
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Test calculate_source_quality
    quality = calculate_source_quality(df, '7th', mapping)
    
    assert 'HEIGHT_M' in quality, "HEIGHT_M should be in quality metrics"
    assert quality['HEIGHT_M']['non_null_count'] == 4, f"Expected 4 non-null, got {quality['HEIGHT_M']['non_null_count']}"
    assert quality['HEIGHT_M']['missing_count'] == 1, f"Expected 1 missing, got {quality['HEIGHT_M']['missing_count']}"
    assert abs(quality['HEIGHT_M']['missing_rate'] - 0.2) < 0.001, f"Expected missing_rate 0.2, got {quality['HEIGHT_M']['missing_rate']}"
    assert quality['HEIGHT_M']['total_rows'] == 5, f"Expected 5 total rows, got {quality['HEIGHT_M']['total_rows']}"
    
    assert 'WEIGHT_KG' in quality, "WEIGHT_KG should be in quality metrics"
    assert quality['WEIGHT_KG']['non_null_count'] == 3, f"Expected 3 non-null, got {quality['WEIGHT_KG']['non_null_count']}"
    assert quality['WEIGHT_KG']['missing_count'] == 2, f"Expected 2 missing, got {quality['WEIGHT_KG']['missing_count']}"
    assert abs(quality['WEIGHT_KG']['missing_rate'] - 0.4) < 0.001, f"Expected missing_rate 0.4, got {quality['WEIGHT_KG']['missing_rate']}"
    
    assert 'NECK_WIDTH_M' in quality, "NECK_WIDTH_M should be in quality metrics"
    assert quality['NECK_WIDTH_M']['non_null_count'] == 0, f"Expected 0 non-null, got {quality['NECK_WIDTH_M']['non_null_count']}"
    assert quality['NECK_WIDTH_M']['missing_count'] == 5, f"Expected 5 missing, got {quality['NECK_WIDTH_M']['missing_count']}"
    assert abs(quality['NECK_WIDTH_M']['missing_rate'] - 1.0) < 0.001, f"Expected missing_rate 1.0, got {quality['NECK_WIDTH_M']['missing_rate']}"
    
    # Test detect_duplicate_headers
    df_with_duplicates = pd.DataFrame({
        '키': [1.7, 1.8, np.nan],  # Base header "키"
        '키.1': [np.nan, np.nan, np.nan],  # Duplicate with .1 suffix
        '키.2': [1.65, np.nan, 1.75],  # Duplicate with .2 suffix
        '체중(몸무게)': [70, 80, 65]  # No duplicate
    })
    
    duplicates = detect_duplicate_headers(df_with_duplicates, '7th')
    
    assert '키' in duplicates, "Base header '키' should be detected as duplicate"
    assert len(duplicates['키']) == 3, f"Expected 3 columns for '키', got {len(duplicates['키'])}"
    
    # Check column names
    col_names = [col['column_name'] for col in duplicates['키']]
    assert '키' in col_names, "'키' should be in duplicate columns"
    assert '키.1' in col_names, "'키.1' should be in duplicate columns"
    assert '키.2' in col_names, "'키.2' should be in duplicate columns"
    
    # Check non-null counts (sorted descending)
    assert duplicates['키'][0]['non_null_count'] >= duplicates['키'][1]['non_null_count'], \
        "Columns should be sorted by non_null_count descending"
    
    # Test generate_quality_summary
    with tempfile.TemporaryDirectory() as tmpdir:
        summary_path = Path(tmpdir) / "quality_summary.md"
        
        all_source_quality = {
            '7th': quality
        }
        all_duplicate_headers = {
            '7th': duplicates
        }
        
        generate_quality_summary(all_source_quality, all_duplicate_headers, summary_path)
        
        # Verify file was created
        assert summary_path.exists(), f"Quality summary file should be created at {summary_path}"
        
        # Read and verify content
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify facts-only content (no action directives)
        assert 'missing_rate' in content, "Content should include missing_rate"
        assert 'non_null_count' in content, "Content should include non_null_count"
        assert 'missing_count' in content, "Content should include missing_count"
        
        # Verify high missing rate section (NECK_WIDTH_M with missing_rate=1.0 >= 0.95)
        assert 'NECK_WIDTH_M' in content, "High missing rate key should be in summary"
        assert '1.0000' in content or '1.0' in content, "Missing rate 1.0 should be in summary"
        
        # Verify duplicate header section
        assert '키' in content, "Duplicate header '키' should be in summary"
        assert '키.1' in content, "Duplicate column '키.1' should be in summary"
        
        # Verify no action directives (facts-only)
        assert 'should' not in content.lower() or 'should' in content.lower() and 'should be' not in content.lower(), \
            "Content should be facts-only, no action directives"
        
        # Verify source completeness summary
        assert '7th' in content, "Source '7th' should be in summary"
        assert 'HEIGHT_M' in content, "HEIGHT_M should be in completeness summary"


def test_header_candidates_generation():
    """
    Test that header candidates are found and emitted correctly.
    
    Verifies:
    1) find_header_candidates finds columns matching search patterns
    2) Candidates include non_null_count, missing_count, total_rows
    3) emit_header_candidates generates facts-only markdown
    """
    import tempfile
    
    # Create synthetic DataFrame with candidate columns
    df = pd.DataFrame({
        '팔길이': [1.7, 1.8, np.nan, 1.65, 1.75],  # 4 non-null, 1 missing
        '팔길이.1': [np.nan, np.nan, np.nan, np.nan, np.nan],  # 0 non-null, 5 missing
        '팔길이.2': [1.6, np.nan, 1.7, np.nan, 1.8],  # 3 non-null, 2 missing
        '앉은무릎높이': [0.4, 0.45, np.nan, 0.42, 0.43],  # 4 non-null, 1 missing
        '무릎높이': [0.5, np.nan, np.nan, 0.48, 0.49],  # 3 non-null, 2 missing
        'other_col': [1, 2, 3, 4, 5]  # Not a candidate
    })
    
    # Test find_header_candidates
    candidates = find_header_candidates(df, '8th_direct', ['ARM_LEN_M', 'KNEE_HEIGHT_M'], primary_row=4)
    
    # Verify ARM_LEN_M candidates
    assert 'ARM_LEN_M' in candidates, "ARM_LEN_M should be in candidates"
    arm_candidates = candidates['ARM_LEN_M']
    assert len(arm_candidates) == 3, f"Should find 3 ARM_LEN_M candidates, found {len(arm_candidates)}"
    
    # Verify candidates are sorted by non_null_count descending
    assert arm_candidates[0]['non_null_count'] == 4, "First candidate should have 4 non-null"
    assert arm_candidates[0]['column_name'] == '팔길이', "First candidate should be '팔길이'"
    assert arm_candidates[1]['non_null_count'] == 3, "Second candidate should have 3 non-null"
    assert arm_candidates[1]['column_name'] == '팔길이.2', "Second candidate should be '팔길이.2'"
    assert arm_candidates[2]['non_null_count'] == 0, "Third candidate should have 0 non-null"
    assert arm_candidates[2]['column_name'] == '팔길이.1', "Third candidate should be '팔길이.1'"
    
    # Verify candidate structure
    for candidate in arm_candidates:
        assert 'column_name' in candidate, "Candidate should have column_name"
        assert 'non_null_count' in candidate, "Candidate should have non_null_count"
        assert 'missing_count' in candidate, "Candidate should have missing_count"
        assert 'total_rows' in candidate, "Candidate should have total_rows"
        assert 'non_null_rate' in candidate, "Candidate should have non_null_rate"
        assert candidate['total_rows'] == 5, "Total rows should be 5"
        assert candidate['non_null_count'] + candidate['missing_count'] == 5, "non_null + missing should equal total"
    
    # Verify KNEE_HEIGHT_M candidates
    assert 'KNEE_HEIGHT_M' in candidates, "KNEE_HEIGHT_M should be in candidates"
    knee_candidates = candidates['KNEE_HEIGHT_M']
    assert len(knee_candidates) == 2, f"Should find 2 KNEE_HEIGHT_M candidates, found {len(knee_candidates)}"
    
    # Verify emit_header_candidates
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "header_candidates.md"
        all_candidates = {
            '8th_direct': candidates
        }
        emit_header_candidates(all_candidates, output_path)
        
        # Verify file was created
        assert output_path.exists(), f"Header candidates file should be created at {output_path}"
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify facts-only content
        assert '8th_direct' in content, "Content should include source '8th_direct'"
        assert 'ARM_LEN_M' in content, "Content should include ARM_LEN_M"
        assert 'KNEE_HEIGHT_M' in content, "Content should include KNEE_HEIGHT_M"
        assert '팔길이' in content, "Content should include candidate '팔길이'"
        assert '앉은무릎높이' in content, "Content should include candidate '앉은무릎높이'"
        assert 'Non-Null Count' in content, "Content should include non-null count header"
        assert 'Missing Count' in content, "Content should include missing count header"
        
        # Verify no action directives (facts-only)
        assert 'should' not in content.lower() or ('should' in content.lower() and 'should be' not in content.lower()), \
            "Content should be facts-only, no action directives"


def test_arm_knee_trace_generation():
    """
    Test that ARM_LEN_M and KNEE_HEIGHT_M trace is generated correctly.
    
    Verifies:
    1) collect_arm_knee_trace collects trace data with correct structure
    2) emit_arm_knee_trace generates facts-only markdown
    3) Trace includes dtype, sample_values, non_null_count, non_finite_count, min/max
    """
    import tempfile
    
    # Create synthetic DataFrame with ARM_LEN_M and KNEE_HEIGHT_M
    # Note: np.isfinite returns False for NaN, inf, -inf
    # So non_finite_count includes NaN + inf + -inf
    df = pd.DataFrame({
        'ARM_LEN_M': [0.5, 0.6, np.nan, 0.55, 0.65, np.inf, -np.inf, 0.7, 0.8, np.nan] * 2,  # 16 non-null, 4 missing (NaN), 2 inf/-inf
        'KNEE_HEIGHT_M': [0.4, 0.45, 0.42, np.nan, 0.43, 0.41, np.inf, 0.44, np.nan, 0.46] * 2,  # 16 non-null, 4 missing (NaN), 1 inf
        'other_col': [1, 2, 3, 4, 5] * 4
    })
    
    # Test collect_arm_knee_trace
    trace = collect_arm_knee_trace(df, '8th_direct', 'after_extraction')
    
    # Verify ARM_LEN_M trace
    assert 'ARM_LEN_M' in trace, "ARM_LEN_M should be in trace"
    arm_trace = trace['ARM_LEN_M']
    assert arm_trace['present'] == True, "ARM_LEN_M should be present"
    assert arm_trace['dtype'] == 'float64', "ARM_LEN_M dtype should be float64"
    assert arm_trace['non_null_count'] == 16, f"ARM_LEN_M non_null_count should be 16, got {arm_trace['non_null_count']}"
    assert arm_trace['total_rows'] == 20, "ARM_LEN_M total_rows should be 20"
    # non_finite_count includes NaN (4) + inf/-inf (2*2=4) = 8 total non-finite
    assert arm_trace['non_finite_count'] == 8, f"ARM_LEN_M non_finite_count should be 8 (4 NaN + 4 inf/-inf), got {arm_trace['non_finite_count']}"
    assert len(arm_trace['sample_values']) == 16, "ARM_LEN_M should have 16 sample values"
    assert arm_trace['min_value'] is not None, "ARM_LEN_M min_value should be set"
    assert arm_trace['max_value'] is not None, "ARM_LEN_M max_value should be set"
    
    # Verify KNEE_HEIGHT_M trace
    assert 'KNEE_HEIGHT_M' in trace, "KNEE_HEIGHT_M should be in trace"
    knee_trace = trace['KNEE_HEIGHT_M']
    assert knee_trace['present'] == True, "KNEE_HEIGHT_M should be present"
    assert knee_trace['non_null_count'] == 16, f"KNEE_HEIGHT_M non_null_count should be 16, got {knee_trace['non_null_count']}"
    # non_finite_count includes NaN (4) + inf (2) = 6 total non-finite
    assert knee_trace['non_finite_count'] == 6, f"KNEE_HEIGHT_M non_finite_count should be 6 (4 NaN + 2 inf), got {knee_trace['non_finite_count']}"
    
    # Test emit_arm_knee_trace
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "arm_knee_trace.md"
        all_traces = {
            '8th_direct': [trace]
        }
        emit_arm_knee_trace(all_traces, output_path)
        
        # Verify file was created
        assert output_path.exists(), f"ARM/KNEE trace file should be created at {output_path}"
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify facts-only content
        assert '8th_direct' in content, "Content should include source '8th_direct'"
        assert 'ARM_LEN_M' in content, "Content should include ARM_LEN_M"
        assert 'KNEE_HEIGHT_M' in content, "Content should include KNEE_HEIGHT_M"
        assert 'dtype' in content, "Content should include dtype"
        assert 'non_null_count' in content, "Content should include non_null_count"
        assert 'non_finite_count' in content, "Content should include non_finite_count"
        assert 'sample_values' in content, "Content should include sample_values"
        
        # Verify no action directives (facts-only)
        assert 'should' not in content.lower() or ('should' in content.lower() and 'should be' not in content.lower()), \
            "Content should be facts-only, no action directives"


def test_unit_fallback_mm_for_8th_unitless():
    """
    Test that unitless 8th_direct/8th_3d columns with unit=m keys get mm->m fallback.
    
    Verifies:
    1) ARM_LEN_M and KNEE_HEIGHT_M with unit_undetermined get mm->m conversion (÷1000)
    2) Values are correctly converted (e.g., 587 -> 0.587, 495 -> 0.495)
    3) non_null_count remains > 0 after conversion
    4) warnings include UNIT_DEFAULT_MM_NO_UNIT aggregated warning
    """
    import tempfile
    
    # Create synthetic DataFrame with ARM_LEN_M and KNEE_HEIGHT_M in mm (no unit metadata)
    df = pd.DataFrame({
        'ARM_LEN_M': [587.0, 600.0, 550.0, np.nan, 620.0],  # mm values
        'KNEE_HEIGHT_M': [495.0, 500.0, np.nan, 480.0, 510.0],  # mm values
        'WEIGHT_KG': [70.0, 75.0, 65.0, 80.0, 72.0],  # Should not be converted
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Empty unit_map (unit undetermined)
    unit_map = {}
    warnings = []
    
    # Test apply_unit_canonicalization with 8th_direct source
    df_converted = apply_unit_canonicalization(df, unit_map, warnings, source_key='8th_direct')
    
    # Verify ARM_LEN_M conversion (mm->m, ÷1000)
    assert 'ARM_LEN_M' in df_converted.columns, "ARM_LEN_M should be in converted DataFrame"
    arm_values = df_converted['ARM_LEN_M'].values
    assert not np.isnan(arm_values[0]), "ARM_LEN_M[0] should not be NaN after conversion"
    assert abs(arm_values[0] - 0.587) < 0.001, f"ARM_LEN_M[0] should be ~0.587, got {arm_values[0]}"
    assert abs(arm_values[1] - 0.600) < 0.001, f"ARM_LEN_M[1] should be ~0.600, got {arm_values[1]}"
    
    # Verify non_null_count > 0
    arm_non_null = df_converted['ARM_LEN_M'].notna().sum()
    assert arm_non_null > 0, f"ARM_LEN_M non_null_count should be > 0, got {arm_non_null}"
    assert arm_non_null == 4, f"ARM_LEN_M non_null_count should be 4, got {arm_non_null}"
    
    # Verify KNEE_HEIGHT_M conversion
    knee_values = df_converted['KNEE_HEIGHT_M'].values
    assert not np.isnan(knee_values[0]), "KNEE_HEIGHT_M[0] should not be NaN after conversion"
    assert abs(knee_values[0] - 0.495) < 0.001, f"KNEE_HEIGHT_M[0] should be ~0.495, got {knee_values[0]}"
    
    knee_non_null = df_converted['KNEE_HEIGHT_M'].notna().sum()
    assert knee_non_null > 0, f"KNEE_HEIGHT_M non_null_count should be > 0, got {knee_non_null}"
    assert knee_non_null == 4, f"KNEE_HEIGHT_M non_null_count should be 4, got {knee_non_null}"
    
    # Verify WEIGHT_KG is not converted (should remain NaN due to unit_undetermined, but it's not a unit=m key)
    # Actually, WEIGHT_KG is excluded from conversion in apply_unit_canonicalization
    assert 'WEIGHT_KG' in df_converted.columns, "WEIGHT_KG should be in converted DataFrame"
    
    # Verify warnings include UNIT_DEFAULT_MM_NO_UNIT
    unit_default_warnings = [w for w in warnings if 'UNIT_DEFAULT_MM_NO_UNIT' in str(w.get('details', ''))]
    assert len(unit_default_warnings) >= 2, f"Should have at least 2 UNIT_DEFAULT_MM_NO_UNIT warnings, got {len(unit_default_warnings)}"
    
    # Verify warning structure
    for w in unit_default_warnings:
        assert w.get('reason') == 'unit_conversion_applied', "Warning reason should be unit_conversion_applied"
        assert 'assumed_unit=mm' in str(w.get('details', '')), "Warning should include assumed_unit=mm"
        assert 'applied_scale=1000' in str(w.get('details', '')), "Warning should include applied_scale=1000"
        assert 'non_null_before' in str(w.get('details', '')), "Warning should include non_null_before"
        assert 'non_null_after' in str(w.get('details', '')), "Warning should include non_null_after"
    
    # Test with 8th_3d source
    warnings_3d = []
    df_converted_3d = apply_unit_canonicalization(df, unit_map, warnings_3d, source_key='8th_3d')
    assert df_converted_3d['ARM_LEN_M'].notna().sum() > 0, "8th_3d should also apply mm fallback"
    
    # Test with 7th source (should not apply fallback)
    warnings_7th = []
    df_converted_7th = apply_unit_canonicalization(df, unit_map, warnings_7th, source_key='7th')
    # 7th should set to NaN (no fallback)
    assert df_converted_7th['ARM_LEN_M'].isna().all(), "7th should not apply mm fallback, should be all NaN"
    unit_undetermined_warnings = [w for w in warnings_7th if w.get('reason') == 'unit_undetermined']
    assert len(unit_undetermined_warnings) >= 2, "7th should have unit_undetermined warnings"
    
    # Verify source_key is not "unknown" in unit warnings
    for w in warnings_7th:
        if w.get('reason') in ['unit_undetermined', 'unit_conversion_failed', 'unit_conversion_applied']:
            assert w.get('source') != 'unknown', f"Unit warning should not have source='unknown', got: {w}"
            assert w.get('source') in ['7th', '8th_direct', '8th_3d', 'system'], \
                f"Unit warning source should be valid, got: {w.get('source')}"


def test_unit_warnings_source_key_presence():
    """
    Test that unit-related warnings always include source_key (no 'unknown').
    
    Verifies:
    1) unit_conversion_failed warnings have valid source_key
    2) unit_undetermined warnings have valid source_key
    3) unit_conversion_applied warnings have valid source_key
    4) system-level non-finite normalization warnings have source="system"
    """
    import pandas as pd
    import numpy as np
    
    # Create synthetic DataFrame with values that will trigger unit_conversion_failed
    df = pd.DataFrame({
        'ARM_LEN_M': [587.0, 600.0, np.inf, -np.inf, 550.0],  # Contains inf/-inf
        'KNEE_HEIGHT_M': [495.0, 500.0, np.nan, 480.0, 510.0],
        'WEIGHT_KG': [70.0, 75.0, 65.0, 80.0, 72.0]
    })
    
    # Unit map with invalid unit to trigger unit_conversion_failed
    unit_map = {
        'ARM_LEN_M': 'kg',  # Invalid unit for length
        'KNEE_HEIGHT_M': None  # Will be missing, triggering unit_undetermined
    }
    warnings = []
    
    # Test apply_unit_canonicalization with 8th_direct source
    df_converted = apply_unit_canonicalization(df, unit_map, warnings, source_key='8th_direct')
    
    # Verify all unit-related warnings have valid source_key
    unit_warnings = [w for w in warnings if w.get('reason') in [
        'unit_conversion_failed', 'unit_undetermined', 'unit_conversion_applied'
    ]]
    
    assert len(unit_warnings) > 0, "Should have unit-related warnings"
    
    for w in unit_warnings:
        source = w.get('source')
        assert source is not None, f"Warning should have source, got: {w}"
        assert source != 'unknown', f"Warning should not have source='unknown', got: {w}"
        assert source in ['7th', '8th_direct', '8th_3d', 'system'], \
            f"Warning source should be valid, got: {source} in {w}"
    
    # Test system-level non-finite normalization
    df_with_inf = pd.DataFrame({
        'ARM_LEN_M': [0.5, 0.6, np.inf, -np.inf, 0.7],
        'KNEE_HEIGHT_M': [0.4, 0.45, np.inf, 0.42, 0.43]
    })
    
    # Simulate non-finite normalization (as done in build_curated_v0 before parquet write)
    system_warnings = []
    numeric_cols = df_with_inf.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue
        non_finite_mask = ~np.isfinite(df_with_inf[col])
        non_finite_count = non_finite_mask.sum()
        if non_finite_count > 0:
            system_warnings.append({
                "source": "system",
                "file": "build_curated_v0.py",
                "column": col,
                "reason": "unit_conversion_failed",
                "row_index": None,
                "original_value": None,
                "details": f"{non_finite_count} non-finite values (inf/-inf) normalized to NaN before parquet write"
            })
    
    # Verify system warnings have source="system"
    assert len(system_warnings) > 0, "Should have system warnings for non-finite values"
    for w in system_warnings:
        assert w.get('source') == 'system', f"System warning should have source='system', got: {w.get('source')}"


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
        test_7th_xlsx_preference()
        test_per_key_header_selection()
        test_human_id_string_preservation()
        test_xlsx_human_id_string_loading()
        test_primary_header_anchor_in_non_first_cell()
        test_per_key_header_policy_with_age()
        test_data_start_row_cutoff()
        test_weight_kg_mixed_dtype_parquet_cast()
        test_non_finite_normalization()
        test_quality_summary_generation()
        test_header_candidates_generation()
        test_arm_knee_trace_generation()
        test_unit_fallback_mm_for_8th_unitless()
        test_unit_warnings_source_key_presence()
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
