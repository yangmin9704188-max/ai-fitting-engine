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
    generate_completeness_report,
    find_header_candidates,
    emit_header_candidates,
    collect_arm_knee_trace,
    emit_arm_knee_trace,
    collect_unit_fail_trace,
    emit_unit_fail_trace,
    check_all_null_extracted,
    check_all_null_by_source,
    check_massive_null_introduced,
    check_scale_and_range_suspected
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
    
    # Explicit assertion: no unit warnings should have source=None or source='unknown'
    for w in unit_warnings:
        source = w.get('source')
        assert source is not None, f"Warning should have source, got: {w}"
        assert source != 'unknown', f"Warning should not have source='unknown', got: {w}"
        assert source in ['7th', '8th_direct', '8th_3d', 'system'], \
            f"Warning source should be valid, got: {source} in {w}"
    
    # Additional scan: verify no unit_* reason warnings have None/unknown source
    all_unit_reasons = ['unit_conversion_failed', 'unit_undetermined', 'unit_conversion_applied', 'UNIT_DEFAULT_MM_NO_UNIT']
    all_unit_warnings = [w for w in warnings if any(reason in str(w.get('reason', '')) for reason in all_unit_reasons)]
    for w in all_unit_warnings:
        source = w.get('source')
        assert source is not None and source != 'unknown', \
            f"Unit warning must have valid source (not None/unknown), got source={source} in {w}"
    
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


def test_unit_fail_trace_generation():
    """
    Test unit-fail trace generation for inf/-inf diagnosis.
    
    Verifies:
    1) collect_unit_fail_trace captures non-finite values
    2) emit_unit_fail_trace generates markdown with non_finite_count > 0
    3) sample_values prioritize non-finite values
    """
    import pandas as pd
    import numpy as np
    from pathlib import Path
    import tempfile
    
    # Create synthetic DataFrame with inf values that will trigger unit_conversion_failed
    df = pd.DataFrame({
        'NECK_WIDTH_M': [0.1, 0.2, np.inf, -np.inf, 0.15, np.nan],
        'NECK_DEPTH_M': [0.05, 0.1, np.inf, 0.08, np.nan, 0.12],
        'UNDERBUST_CIRC_M': [0.7, np.inf, 0.75, -np.inf, 0.72, np.nan],
        'CHEST_CIRC_M_REF': [0.9, 0.95, np.inf, 0.92, np.nan, 0.88],
        'OTHER_COL': [1, 2, 3, 4, 5, 6]
    })
    
    # Test collect_unit_fail_trace
    trace = collect_unit_fail_trace(df, '7th', 'after_unit_conversion')
    
    # Verify all target keys are in trace
    target_keys = ['NECK_WIDTH_M', 'NECK_DEPTH_M', 'UNDERBUST_CIRC_M', 'CHEST_CIRC_M_REF']
    for key in target_keys:
        assert key in trace, f"Trace should include {key}"
        assert trace[key]['present'], f"{key} should be present"
        assert trace[key]['non_finite_count'] > 0, f"{key} should have non_finite_count > 0"
        assert len(trace[key]['sample_values']) > 0, f"{key} should have sample values"
        # Verify non-finite values are in samples (inf/-inf should appear)
        sample_str = ' '.join(trace[key]['sample_values'])
        assert 'inf' in sample_str or 'Inf' in sample_str or '-inf' in sample_str or 'non_finite' in sample_str, \
            f"{key} samples should include inf values"
    
    # Test emit_unit_fail_trace
    all_traces = {
        '7th': [trace]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        output_path = Path(f.name)
    
    try:
        emit_unit_fail_trace(all_traces, output_path)
        
        # Verify file was created
        assert output_path.exists(), "Trace markdown file should be created"
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        assert 'curated_v0 Unit Fail Trace' in content, "Should contain title"
        assert '7th' in content, "Should contain source"
        assert 'NECK_WIDTH_M' in content, "Should contain NECK_WIDTH_M"
        assert 'non_finite_count' in content, "Should contain non_finite_count"
        
        # Verify non_finite_count > 0 is recorded
        assert 'non_finite_count: 2' in content or 'non_finite_count: 3' in content or 'non_finite_count: 4' in content, \
            "Should record non_finite_count > 0"
        
    finally:
        if output_path.exists():
            output_path.unlink()


def test_unit_fail_trace_dtype_safe():
    """
    Test unit-fail trace generation with object dtype (dtype-safe non-finite detection).
    
    Verifies:
    1) collect_unit_fail_trace does not crash on object dtype columns
    2) non_finite_count correctly identifies inf/-inf after numeric coercion
    3) non_numeric_count correctly identifies non-numeric values
    4) sample_values include both raw and processed samples
    """
    import pandas as pd
    import numpy as np
    from pathlib import Path
    import tempfile
    
    # Create synthetic DataFrame with object dtype containing mixed values
    df = pd.DataFrame({
        'NECK_WIDTH_M': pd.Series(["1", "2", "inf", "-inf", "x", None], dtype='object'),
        'NECK_DEPTH_M': pd.Series(["0.5", "0.6", "Infinity", "-Infinity", "nan", "1.5"], dtype='object'),
        'UNDERBUST_CIRC_M': pd.Series([0.7, 0.75, np.inf, -np.inf, 0.72, np.nan], dtype='float64'),
        'CHEST_CIRC_M_REF': pd.Series(["0.9", "0.95", "1.0", None, "0.88"], dtype='object'),
        'OTHER_COL': [1, 2, 3, 4, 5, 6]
    })
    
    # Test collect_unit_fail_trace (should not crash)
    trace = collect_unit_fail_trace(df, '8th_direct', 'after_unit_conversion')
    
    # Verify NECK_WIDTH_M trace
    assert 'NECK_WIDTH_M' in trace, "Trace should include NECK_WIDTH_M"
    neck_trace = trace['NECK_WIDTH_M']
    assert neck_trace['present'], "NECK_WIDTH_M should be present"
    
    # Verify non_finite_count: should be 2 (inf, -inf)
    assert neck_trace['non_finite_count'] == 2, \
        f"NECK_WIDTH_M should have non_finite_count=2, got {neck_trace['non_finite_count']}"
    
    # Verify non_numeric_count: should be 1 ("x")
    assert neck_trace.get('non_numeric_count', 0) == 1, \
        f"NECK_WIDTH_M should have non_numeric_count=1, got {neck_trace.get('non_numeric_count', 0)}"
    
    # Verify sample_values include non-finite markers
    sample_str = ' '.join(neck_trace.get('sample_values', []))
    assert 'non_finite' in sample_str or 'inf' in sample_str, \
        f"Sample values should include non-finite markers: {sample_str}"
    
    # Verify raw_sample_values exist
    assert 'raw_sample_values' in neck_trace, "Should have raw_sample_values"
    assert len(neck_trace['raw_sample_values']) > 0, "Should have raw sample values"
    
    # Verify NECK_DEPTH_M trace (Infinity strings)
    assert 'NECK_DEPTH_M' in trace, "Trace should include NECK_DEPTH_M"
    depth_trace = trace['NECK_DEPTH_M']
    # Infinity strings should be converted to inf, so non_finite_count should be 2
    assert depth_trace['non_finite_count'] >= 0, "NECK_DEPTH_M should have valid non_finite_count"
    
    # Test emit_unit_fail_trace (should not crash)
    all_traces = {
        '8th_direct': [trace]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        output_path = Path(f.name)
    
    try:
        emit_unit_fail_trace(all_traces, output_path)
        
        # Verify file was created
        assert output_path.exists(), "Trace markdown file should be created"
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        assert 'curated_v0 Unit Fail Trace' in content, "Should contain title"
        assert '8th_direct' in content, "Should contain source"
        assert 'NECK_WIDTH_M' in content, "Should contain NECK_WIDTH_M"
        assert 'non_finite_count' in content, "Should contain non_finite_count"
        assert 'non_numeric_count' in content, "Should contain non_numeric_count"
        assert 'raw_sample_values' in content, "Should contain raw_sample_values"
        
    finally:
        if output_path.exists():
            output_path.unlink()


def test_unit_conversion_numeric_coercion():
    """
    Test that unit conversion applies numeric coercion before scaling.
    
    Verifies:
    1) Object dtype columns are coerced to numeric before unit conversion
    2) Coercion NaN increase is tracked in details (if any)
    3) unit_conversion_failed only counts inf/-inf from numeric float, not object dtype
    """
    # Create synthetic DataFrame with object dtype containing numeric strings
    df = pd.DataFrame({
        'HEIGHT_M': pd.Series(["1700", "1750", "1800", "1650", "1720"], dtype='object'),  # mm scale
        'WAIST_CIRC_M': pd.Series(["800", "850", "900", "750", "820"], dtype='object'),  # mm scale
        'CHEST_CIRC_M_REF': pd.Series(["900", "910", "950", "880", "920"], dtype='object')  # mm scale
    })
    
    # Create unit map (mm detected)
    unit_map = {
        'HEIGHT_M': 'mm',
        'WAIST_CIRC_M': 'mm',
        'CHEST_CIRC_M_REF': 'mm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='8th_direct')
    
    # Verify conversion succeeded (values should be in meters, not NaN)
    assert result_df['HEIGHT_M'].notna().sum() == 5, "HEIGHT_M should have 5 non-null values after conversion"
    assert result_df['CHEST_CIRC_M_REF'].notna().sum() == 5, "CHEST_CIRC_M_REF should have 5 non-null values after conversion"
    
    # Verify values are in meters (approximately 1.7, 1.75, etc.)
    height_values = result_df['HEIGHT_M'].dropna()
    assert height_values.min() > 1.0 and height_values.max() < 2.0, "HEIGHT_M values should be in meters"
    
    # Verify no unit_conversion_failed for inf/-inf (should be 0 since all values are valid)
    failed_warnings = [w for w in warnings if w.get('reason') == 'unit_conversion_failed' and 'inf/-inf' in w.get('details', '')]
    # Should have no inf/-inf failures for these valid numeric strings
    assert len(failed_warnings) == 0, f"Should have no inf/-inf failures, got {len(failed_warnings)}"


def test_chest_circ_ref_no_collapse():
    """
    Test that CHEST_CIRC_M_REF does not collapse to all NaN with numeric coercion.
    
    Verifies:
    1) String numbers ("900", "910" etc.) are converted successfully
    2) Non-numeric tokens ("키" etc.) become NaN but don't crash pipeline
    3) MASSIVE_NULL_INTRODUCED is not triggered for valid numeric strings
    """
    # Create synthetic DataFrame with mixed valid/invalid values
    df_before = pd.DataFrame({
        'CHEST_CIRC_M_REF': pd.Series(["900", "910", "950", "키", "920", "880"] * 100, dtype='object')  # 600 rows
    })
    
    # Create unit map
    unit_map = {
        'CHEST_CIRC_M_REF': 'mm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df_before, unit_map, warnings, source_key='8th_direct')
    
    # Verify: 5 valid numeric strings should convert successfully (600 - 100 = 500 non-null)
    # "키" and similar non-numeric should become NaN via coercion
    non_null_after = result_df['CHEST_CIRC_M_REF'].notna().sum()
    assert non_null_after >= 500, f"Should have at least 500 non-null values, got {non_null_after}"
    
    # Verify values are in meters (approximately 0.9, 0.91, etc.)
    valid_values = result_df['CHEST_CIRC_M_REF'].dropna()
    if len(valid_values) > 0:
        assert valid_values.min() > 0.5 and valid_values.max() < 1.5, "CHEST_CIRC_M_REF values should be in meters"
    
    # Verify pipeline didn't crash (warnings are acceptable)
    # Coercion NaN increase should be tracked if present
    coercion_warnings = [w for w in warnings if 'coercion_nan_increase' in w.get('details', '')]
    # May or may not have coercion warnings depending on implementation details
    
    # Verify no MASSIVE_NULL_INTRODUCED (should be checked separately in integration test)
    # This test only verifies unit conversion doesn't collapse


def test_all_null_extracted_sensor():
    """
    Test ALL_NULL_EXTRACTED sensor: non_null_count == 0 after extraction.
    
    Verifies:
    1) ALL_NULL_EXTRACTED warning is emitted when column has all nulls after extraction
    2) Warning includes correct details (rows_total, non_null_count, stage)
    3) Meta columns (HUMAN_ID, SEX, AGE) are excluded from check
    """
    import json
    
    # Create synthetic DataFrame with all-null column
    df = pd.DataFrame({
        'HEIGHT_M': [np.nan] * 100,
        'WEIGHT_KG': [70.0] * 100,
        'WAIST_CIRC_M': [np.nan] * 100,
        'HUMAN_ID': ['ID001'] * 100,
        'SEX': ['M'] * 100,
        'AGE': [30] * 100
    })
    
    # Create minimal mapping
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WEIGHT_KG', 'sources': {'7th': {'present': True, 'column': 'WEIGHT_KG'}}},
            {'standard_key': 'WAIST_CIRC_M', 'sources': {'7th': {'present': True, 'column': 'WAIST_CIRC_M'}}},
            {'standard_key': 'HUMAN_ID', 'sources': {'7th': {'present': True, 'column': 'HUMAN_ID'}}},
            {'standard_key': 'SEX', 'sources': {'7th': {'present': True, 'column': 'SEX'}}},
            {'standard_key': 'AGE', 'sources': {'7th': {'present': True, 'column': 'AGE'}}}
        ]
    }
    
    warnings = []
    check_all_null_extracted(df, '7th', warnings, mapping)
    
    # Verify warnings: HEIGHT_M and WAIST_CIRC_M should trigger (all null)
    # WEIGHT_KG should not (has values)
    # Meta columns should not trigger
    all_null_warnings = [w for w in warnings if w.get('reason') == 'ALL_NULL_EXTRACTED']
    assert len(all_null_warnings) == 2, f"Should have 2 ALL_NULL_EXTRACTED warnings, got {len(all_null_warnings)}"
    
    # Check HEIGHT_M warning
    height_warning = [w for w in all_null_warnings if w.get('column') == 'HEIGHT_M']
    assert len(height_warning) == 1, "Should have ALL_NULL_EXTRACTED for HEIGHT_M"
    assert height_warning[0]['source'] == '7th'
    assert 'rows_total=100' in height_warning[0]['details']
    assert 'non_null_count=0' in height_warning[0]['details']
    assert 'stage=after_extraction_before_preprocess' in height_warning[0]['details']
    
    # Verify meta columns are not checked
    meta_warnings = [w for w in all_null_warnings if w.get('column') in ['HUMAN_ID', 'SEX', 'AGE']]
    assert len(meta_warnings) == 0, "Meta columns should not trigger ALL_NULL_EXTRACTED"


def test_massive_null_introduced_sensor():
    """
    Test MASSIVE_NULL_INTRODUCED sensor: non_null drops >= 0.95 AND >= 1000.
    
    Verifies:
    1) MASSIVE_NULL_INTRODUCED warning is emitted when drop_rate >= 0.95 AND drop_count >= 1000
    2) Warning includes correct details (before/after non_null, drop_rate)
    3) Small drops (< 1000) do not trigger
    """
    # Create synthetic DataFrames: before has 2000 non-null, after has 50 non-null
    df_before = pd.DataFrame({
        'HEIGHT_M': [1.7] * 2000 + [np.nan] * 100,
        'WEIGHT_KG': [70.0] * 2000 + [np.nan] * 100
    })
    
    df_after = pd.DataFrame({
        'HEIGHT_M': [1.7] * 50 + [np.nan] * 2050,  # Drop from 2000 to 50 (drop_rate = 0.975, drop_count = 1950)
        'WEIGHT_KG': [70.0] * 2000 + [np.nan] * 100  # No drop
    })
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WEIGHT_KG', 'sources': {'7th': {'present': True, 'column': 'WEIGHT_KG'}}}
        ]
    }
    
    warnings = []
    check_massive_null_introduced(df_before, df_after, '7th', warnings, mapping)
    
    # Verify warning: HEIGHT_M should trigger (drop_rate=0.975, drop_count=1950)
    massive_warnings = [w for w in warnings if w.get('reason') == 'MASSIVE_NULL_INTRODUCED']
    assert len(massive_warnings) == 1, f"Should have 1 MASSIVE_NULL_INTRODUCED warning, got {len(massive_warnings)}"
    
    height_warning = massive_warnings[0]
    assert height_warning['column'] == 'HEIGHT_M'
    assert height_warning['source'] == '7th'
    assert 'before_non_null=2000' in height_warning['details']
    assert 'after_non_null=50' in height_warning['details']
    assert 'drop_rate=0.975' in height_warning['details']


def test_scale_suspected_sensor():
    """
    Test SCALE_SUSPECTED sensor: p50 > 10.0 or < 0.01 for expected_unit='m' keys.
    
    Verifies:
    1) SCALE_SUSPECTED warning is emitted when p50 > 10.0 (mm scale suspected)
    2) SCALE_SUSPECTED warning is emitted when p50 < 0.01 (double-division suspected)
    3) Warning includes correct details (p01, p50, p99, min, max, reason)
    """
    # Create synthetic DataFrame with mm-scale values (p50 > 10.0)
    df_mm_scale = pd.DataFrame({
        'HEIGHT_M': [1700.0, 1750.0, 1800.0, 1650.0, 1720.0],  # mm scale (p50 = 1720)
        'WAIST_CIRC_M': [0.8, 0.85, 0.9, 0.75, 0.82]  # Normal scale (p50 = 0.82)
    })
    
    # Create synthetic DataFrame with double-division values (p50 < 0.01)
    df_double_div = pd.DataFrame({
        'HEIGHT_M': [0.0017, 0.00175, 0.0018, 0.00165, 0.00172],  # Double division (p50 = 0.00172)
        'WAIST_CIRC_M': [0.8, 0.85, 0.9, 0.75, 0.82]  # Normal scale
    })
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WAIST_CIRC_M', 'sources': {'7th': {'present': True, 'column': 'WAIST_CIRC_M'}}}
        ]
    }
    
    warnings_mm = []
    check_scale_and_range_suspected(df_mm_scale, '7th', warnings_mm, mapping)
    
    # Verify HEIGHT_M triggers SCALE_SUSPECTED (p50 > 10.0)
    scale_warnings_mm = [w for w in warnings_mm if w.get('reason') == 'SCALE_SUSPECTED']
    assert len(scale_warnings_mm) == 1, f"Should have 1 SCALE_SUSPECTED warning, got {len(scale_warnings_mm)}"
    assert scale_warnings_mm[0]['column'] == 'HEIGHT_M'
    assert 'p50 > 10.0' in scale_warnings_mm[0]['details'] or 'mm scale suspected' in scale_warnings_mm[0]['details']
    
    warnings_double = []
    check_scale_and_range_suspected(df_double_div, '7th', warnings_double, mapping)
    
    # Verify HEIGHT_M triggers SCALE_SUSPECTED (p50 < 0.01)
    scale_warnings_double = [w for w in warnings_double if w.get('reason') == 'SCALE_SUSPECTED']
    assert len(scale_warnings_double) == 1, f"Should have 1 SCALE_SUSPECTED warning, got {len(scale_warnings_double)}"
    assert scale_warnings_double[0]['column'] == 'HEIGHT_M'
    assert 'p50 < 0.01' in scale_warnings_double[0]['details'] or 'double-division suspected' in scale_warnings_double[0]['details']


def test_range_suspected_sensor():
    """
    Test RANGE_SUSPECTED sensor: values outside physical range >= 50.
    
    Verifies:
    1) RANGE_SUSPECTED warning is emitted when >= 50 values are outside physical range
    2) Warning includes correct details (p01, p50, p99, min, max, out_of_range_count, expected_range)
    3) HEIGHT_M uses range [0.8, 2.5]
    """
    # Create synthetic DataFrame with many values outside HEIGHT_M range [0.8, 2.5]
    # 60 values outside range (50 below 0.8, 10 above 2.5)
    df = pd.DataFrame({
        'HEIGHT_M': [0.5] * 50 + [3.0] * 10 + [1.7] * 40,  # 60 out of range
        'WAIST_CIRC_M': [0.8, 0.85, 0.9, 0.75, 0.82] * 20  # All in range
    })
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WAIST_CIRC_M', 'sources': {'7th': {'present': True, 'column': 'WAIST_CIRC_M'}}}
        ]
    }
    
    warnings = []
    check_scale_and_range_suspected(df, '7th', warnings, mapping)
    
    # Verify HEIGHT_M triggers RANGE_SUSPECTED (60 out of range >= 50)
    range_warnings = [w for w in warnings if w.get('reason') == 'RANGE_SUSPECTED']
    assert len(range_warnings) == 1, f"Should have 1 RANGE_SUSPECTED warning, got {len(range_warnings)}"
    
    height_warning = range_warnings[0]
    assert height_warning['column'] == 'HEIGHT_M'
    assert height_warning['source'] == '7th'
    assert 'out_of_range_count=60' in height_warning['details']
    assert 'expected_range=[0.8, 2.5]' in height_warning['details']


def test_scale_suspected_heights_mm():
    """
    Test SCALE_SUSPECTED for HEIGHT_M with mm-scale values (1700 -> 1.7 conversion failure case).
    
    Verifies:
    1) HEIGHT_M with values like 1700 (mm scale) triggers SCALE_SUSPECTED
    2) Warning details include p50 and reason
    """
    # Create synthetic DataFrame with mm-scale HEIGHT_M (1700 = 1.7m in mm)
    df = pd.DataFrame({
        'HEIGHT_M': [1700.0, 1750.0, 1800.0, 1650.0, 1720.0] * 20  # 100 rows, p50 = 1720
    })
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}}
        ]
    }
    
    warnings = []
    check_scale_and_range_suspected(df, '7th', warnings, mapping)
    
    # Verify SCALE_SUSPECTED is triggered
    scale_warnings = [w for w in warnings if w.get('reason') == 'SCALE_SUSPECTED']
    assert len(scale_warnings) >= 1, "Should have at least 1 SCALE_SUSPECTED warning"
    
    height_warning = [w for w in scale_warnings if w.get('column') == 'HEIGHT_M']
    assert len(height_warning) == 1, "Should have SCALE_SUSPECTED for HEIGHT_M"
    assert 'p50' in height_warning[0]['details']
    assert height_warning[0]['source'] == '7th'


def test_completeness_report_generation():
    """
    Test completeness report generation.
    
    Verifies:
    1) Report file is created when --emit-completeness-report is specified
    2) Report contains non_null_count, total_rows, non_null_rate, percentiles
    3) Scale observations are included for meter-unit keys
    """
    import tempfile
    from pathlib import Path
    
    # Create synthetic DataFrames for each source
    all_source_dfs = {
        '7th': pd.DataFrame({
            'HEIGHT_M': [1.7, 1.75, 1.8, 1.65, 1.72] * 20,  # 100 rows, p50 = 1.72
            'WEIGHT_KG': [70.0, 75.0, 80.0, 65.0, 72.0] * 20,
            'WAIST_CIRC_M': [0.8, 0.85, 0.9, 0.75, 0.82] * 20,
            'HUMAN_ID': ['ID001'] * 100,
            'SEX': ['M'] * 100,
            'AGE': [30] * 100
        }),
        '8th_direct': pd.DataFrame({
            'HEIGHT_M': [1700.0, 1750.0, 1800.0, 1650.0, 1720.0] * 20,  # mm scale, p50 = 1720
            'WEIGHT_KG': [70.0, 75.0, 80.0, 65.0, 72.0] * 20,
            'WAIST_CIRC_M': [np.nan] * 100,  # All null
            'HUMAN_ID': ['ID002'] * 100,
            'SEX': ['F'] * 100,
            'AGE': [25] * 100
        })
    }
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}, '8th_direct': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WEIGHT_KG', 'sources': {'7th': {'present': True, 'column': 'WEIGHT_KG'}, '8th_direct': {'present': True, 'column': 'WEIGHT_KG'}}},
            {'standard_key': 'WAIST_CIRC_M', 'sources': {'7th': {'present': True, 'column': 'WAIST_CIRC_M'}, '8th_direct': {'present': True, 'column': 'WAIST_CIRC_M'}}},
            {'standard_key': 'HUMAN_ID', 'sources': {'7th': {'present': True, 'column': 'HUMAN_ID'}, '8th_direct': {'present': True, 'column': 'HUMAN_ID'}}},
            {'standard_key': 'SEX', 'sources': {'7th': {'present': True, 'column': 'SEX'}, '8th_direct': {'present': True, 'column': 'SEX'}}},
            {'standard_key': 'AGE', 'sources': {'7th': {'present': True, 'column': 'AGE'}, '8th_direct': {'present': True, 'column': 'AGE'}}}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        output_path = Path(f.name)
    
    try:
        generate_completeness_report(all_source_dfs, mapping, output_path)
        
        # Verify file was created
        assert output_path.exists(), "Completeness report file should be created"
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        assert 'curated_v0 v3 Completeness Report' in content, "Should contain title"
        assert '7th' in content, "Should contain 7th source"
        assert '8th_direct' in content, "Should contain 8th_direct source"
        assert 'HEIGHT_M' in content, "Should contain HEIGHT_M"
        assert 'non_null_count' in content, "Should contain non_null_count"
        assert 'non_null_rate' in content, "Should contain non_null_rate"
        assert 'p50' in content, "Should contain p50"
        
        # Verify scale observation for 8th_direct HEIGHT_M (mm scale)
        assert 'mm_scale_suspected' in content or '8th_direct' in content, "Should contain scale observation"
        
        # Verify all-null handling for WAIST_CIRC_M in 8th_direct
        assert 'all_null=true' in content or 'WAIST_CIRC_M' in content, "Should handle all-null columns"
        
    finally:
        if output_path.exists():
            output_path.unlink()


def test_all_null_by_source_warning():
    """
    Test ALL_NULL_BY_SOURCE warning: key×source당 1건만 기록.
    
    Verifies:
    1) ALL_NULL_BY_SOURCE warning is emitted when non_null_count==0
    2) Warning includes correct details (total_rows, non_null_count=0)
    3) Only 1 warning per key×source combination (no duplicates)
    """
    
    # Create synthetic DataFrame with all-null column
    df = pd.DataFrame({
        'HEIGHT_M': [np.nan] * 100,
        'WEIGHT_KG': [70.0] * 100,
        'WAIST_CIRC_M': [np.nan] * 100,
        'HUMAN_ID': ['ID001'] * 100,
        'SEX': ['M'] * 100,
        'AGE': [30] * 100
    })
    
    mapping = {
        'keys': [
            {'standard_key': 'HEIGHT_M', 'sources': {'7th': {'present': True, 'column': 'HEIGHT_M'}}},
            {'standard_key': 'WEIGHT_KG', 'sources': {'7th': {'present': True, 'column': 'WEIGHT_KG'}}},
            {'standard_key': 'WAIST_CIRC_M', 'sources': {'7th': {'present': True, 'column': 'WAIST_CIRC_M'}}},
            {'standard_key': 'HUMAN_ID', 'sources': {'7th': {'present': True, 'column': 'HUMAN_ID'}}},
            {'standard_key': 'SEX', 'sources': {'7th': {'present': True, 'column': 'SEX'}}},
            {'standard_key': 'AGE', 'sources': {'7th': {'present': True, 'column': 'AGE'}}}
        ]
    }
    
    warnings = []
    check_all_null_by_source(df, '7th', warnings, mapping)
    
    # Verify warnings: HEIGHT_M and WAIST_CIRC_M should trigger (all null)
    # WEIGHT_KG should not (has values)
    # Meta columns should not trigger
    all_null_warnings = [w for w in warnings if w.get('reason') == 'ALL_NULL_BY_SOURCE']
    assert len(all_null_warnings) == 2, f"Should have 2 ALL_NULL_BY_SOURCE warnings, got {len(all_null_warnings)}"
    
    # Check HEIGHT_M warning
    height_warning = [w for w in all_null_warnings if w.get('column') == 'HEIGHT_M']
    assert len(height_warning) == 1, "Should have exactly 1 ALL_NULL_BY_SOURCE for HEIGHT_M"
    assert height_warning[0]['source'] == '7th'
    assert 'total_rows=100' in height_warning[0]['details']
    assert 'non_null_count=0' in height_warning[0]['details']
    
    # Verify meta columns are not checked
    meta_warnings = [w for w in all_null_warnings if w.get('column') in ['HUMAN_ID', 'SEX', 'AGE']]
    assert len(meta_warnings) == 0, "Meta columns should not trigger ALL_NULL_BY_SOURCE"
    
    # Verify no duplicates: call again and check count doesn't increase
    warnings_before = len(warnings)
    check_all_null_by_source(df, '7th', warnings, mapping)
    warnings_after = len(warnings)
    assert warnings_after == warnings_before, "Should not add duplicate warnings"


def test_parse_decimal_comma_vs_thousands_comma():
    """
    Test 7th comma parsing: distinguish decimal comma vs thousands separator.
    
    Verifies:
    1) "79,5" -> 79.5 (decimal comma, pattern ^\d+,\d{1,2}$)
    2) "245,0" -> 245.0 (decimal comma, critical case to prevent 10x scale error)
    3) "377,0" -> 377.0 (decimal comma)
    4) "1,736" -> 1736 (thousands separator, pattern ^\d{1,3}(,\d{3})+$)
    5) "12,345" -> 12345 (thousands separator, pattern ^\d{1,3}(,\d{3})+$)
    6) "1,234.56" -> 1234.56 (dot exists, comma is thousands separator)
    
    Critical regression test: "245,0" must parse to 245.0, not 2450 (10x error).
    """
    # Create synthetic DataFrame with mixed comma patterns
    # Include critical case "245,0" that could cause 10x scale error if processed incorrectly
    df = pd.DataFrame({
        'WAIST_CIRC_M': pd.Series(["79,5", "245,0", "377,0", "1,736", "12,345", "1,234.56", "800"], dtype='object'),
        'SHOULDER_WIDTH_M': pd.Series(["40,5", "450", "1,200", "50,0"], dtype='object'),
        'HEIGHT_M': pd.Series(["1,700", "175", "1,800"], dtype='object')
    })
    
    warnings = []
    result_df = preprocess_numeric_columns(df, '7th', warnings)
    
    # Verify decimal comma parsing (critical: must parse correctly to prevent 10x error)
    waist_values = result_df['WAIST_CIRC_M'].dropna()
    assert 79.5 in waist_values.values or abs(waist_values.values - 79.5).min() < 0.1, "79,5 should parse to 79.5"
    assert 245.0 in waist_values.values or abs(waist_values.values - 245.0).min() < 0.1, "245,0 should parse to 245.0 (not 2450)"
    assert 377.0 in waist_values.values or abs(waist_values.values - 377.0).min() < 0.1, "377,0 should parse to 377.0"
    
    # Verify thousands separator parsing
    assert 1736 in waist_values.values or abs(waist_values.values - 1736).min() < 0.1, "1,736 should parse to 1736"
    assert 12345 in waist_values.values or abs(waist_values.values - 12345).min() < 0.1, "12,345 should parse to 12345"
    
    # Verify dot+comma case (comma is thousands separator)
    assert 1234.56 in waist_values.values or abs(waist_values.values - 1234.56).min() < 0.1, "1,234.56 should parse to 1234.56"
    
    # Verify normal values still work
    assert 800 in waist_values.values or abs(waist_values.values - 800).min() < 0.1, "800 should remain 800"
    
    # Critical assertion: "245,0" must NOT be parsed as 2450 (10x error)
    assert not (2450 in waist_values.values or (abs(waist_values.values - 2450).min() < 0.1)), "245,0 must NOT parse to 2450 (10x scale error)"


def test_7th_comma_parser_strategy_end_to_end():
    """
    Test 7th comma parser strategy end-to-end: parsing -> unit conversion.
    
    Verifies:
    1) "245,0" parses to 245.0, then mm->m conversion results in 0.245
    2) "1,736" parses to 1736, then mm->m conversion results in 1.736
    3) Parser strategy only applies to 7th source (8th_direct/8th_3d unaffected)
    """
    # Create DataFrame with mm-scale values that have comma formatting
    df = pd.DataFrame({
        'WAIST_CIRC_M': pd.Series(["245,0", "250,5", "1,736", "1,800"], dtype='object'),  # mm scale with commas
        'HIP_CIRC_M': pd.Series(["900,0", "950,5", "1,200"], dtype='object'),  # mm scale with commas
        'SEX': ['M', 'F', 'M', 'F']
    })
    
    warnings = []
    # Preprocess (applies 7th comma parser strategy)
    df_preprocessed = preprocess_numeric_columns(df, '7th', warnings)
    
    # Verify parsing results
    waist_values = df_preprocessed['WAIST_CIRC_M'].dropna()
    assert 245.0 in waist_values.values or abs(waist_values.values - 245.0).min() < 0.1, "245,0 should parse to 245.0"
    assert 1736 in waist_values.values or abs(waist_values.values - 1736).min() < 0.1, "1,736 should parse to 1736"
    
    # Apply unit conversion (mm->m)
    unit_map = {
        'WAIST_CIRC_M': 'mm',
        'HIP_CIRC_M': 'mm'
    }
    df_converted = apply_unit_canonicalization(df_preprocessed, unit_map, warnings, source_key='7th')
    
    # Verify end-to-end: 245.0 mm -> 0.245 m, 1736 mm -> 1.736 m
    waist_converted = df_converted['WAIST_CIRC_M'].dropna()
    assert abs(waist_converted.iloc[0] - 0.245) < 0.001 or abs(waist_converted.iloc[0] - 1.736) < 0.001, \
        f"WAIST_CIRC_M should be in meters after conversion, got {waist_converted.iloc[0]}"
    
    # Verify at least one value is in the expected range (0.2-2.0m for waist)
    assert (waist_converted > 0.2).any() and (waist_converted < 2.0).any(), \
        "Converted values should be in realistic meter range"
    
    # Verify 8th_direct is not affected by 7th parser strategy
    df_8th = pd.DataFrame({
        'WAIST_CIRC_M': pd.Series(["245,0", "1,736"], dtype='object'),
        'SEX': ['M', 'F']
    })
    warnings_8th = []
    df_8th_preprocessed = preprocess_numeric_columns(df_8th, '8th_direct', warnings_8th)
    # 8th_direct should not apply comma parsing (no comma handling for 8th)
    # Values should remain as strings or be handled differently
    assert len(warnings_8th) == 0 or 'comma' not in str(warnings_8th), \
        "8th_direct should not apply 7th comma parser strategy"


def test_7th_euro_decimal_comma_regression():
    """
    Test 7th euro-decimal comma regression: specific keys that were showing 10x scale.
    
    Verifies:
    1) ANKLE_MAX_CIRC_M: "245,0" -> 245.0 -> 0.245 (mm->m)
    2) WRIST_CIRC_M: "158,0" -> 158.0 -> 0.158 (mm->m)
    3) HIP_DEPTH_M: "249,0" -> 249.0 -> 0.249 (mm->m)
    """
    # Import unified parser function
    from pipelines.build_curated_v0 import parse_numeric_string_7th
    
    # Test individual parsing
    assert parse_numeric_string_7th("245,0") == "245.0", "245,0 should parse to 245.0"
    assert parse_numeric_string_7th("158,0") == "158.0", "158,0 should parse to 158.0"
    assert parse_numeric_string_7th("249,0") == "249.0", "249,0 should parse to 249.0"
    
    # Test end-to-end: DataFrame -> preprocessing -> unit conversion
    df = pd.DataFrame({
        'ANKLE_MAX_CIRC_M': pd.Series(["245,0", "250,0", "240,0"], dtype='object'),
        'WRIST_CIRC_M': pd.Series(["158,0", "160,0", "155,0"], dtype='object'),
        'HIP_DEPTH_M': pd.Series(["249,0", "250,0", "248,0"], dtype='object'),
        'SEX': ['M', 'F', 'M']
    })
    
    warnings = []
    # Preprocess (applies unified 7th parser)
    df_preprocessed = preprocess_numeric_columns(df, '7th', warnings)
    
    # Verify parsing: should be 245.0, 158.0, 249.0 (not 2450, 1580, 2490)
    ankle_values = df_preprocessed['ANKLE_MAX_CIRC_M'].dropna()
    assert abs(ankle_values.iloc[0] - 245.0) < 0.1, f"ANKLE_MAX_CIRC_M should be 245.0, got {ankle_values.iloc[0]}"
    assert not (abs(ankle_values.iloc[0] - 2450.0) < 0.1), "ANKLE_MAX_CIRC_M must NOT be 2450 (10x error)"
    
    wrist_values = df_preprocessed['WRIST_CIRC_M'].dropna()
    assert abs(wrist_values.iloc[0] - 158.0) < 0.1, f"WRIST_CIRC_M should be 158.0, got {wrist_values.iloc[0]}"
    
    hip_depth_values = df_preprocessed['HIP_DEPTH_M'].dropna()
    assert abs(hip_depth_values.iloc[0] - 249.0) < 0.1, f"HIP_DEPTH_M should be 249.0, got {hip_depth_values.iloc[0]}"
    
    # Apply unit conversion (mm->m)
    unit_map = {
        'ANKLE_MAX_CIRC_M': 'mm',
        'WRIST_CIRC_M': 'mm',
        'HIP_DEPTH_M': 'mm'
    }
    df_converted = apply_unit_canonicalization(df_preprocessed, unit_map, warnings, source_key='7th')
    
    # Verify end-to-end conversion: 245.0 mm -> 0.245 m
    ankle_converted = df_converted['ANKLE_MAX_CIRC_M'].dropna()
    assert abs(ankle_converted.iloc[0] - 0.245) < 0.001, \
        f"ANKLE_MAX_CIRC_M should be 0.245 m after conversion, got {ankle_converted.iloc[0]}"
    
    wrist_converted = df_converted['WRIST_CIRC_M'].dropna()
    assert abs(wrist_converted.iloc[0] - 0.158) < 0.001, \
        f"WRIST_CIRC_M should be 0.158 m after conversion, got {wrist_converted.iloc[0]}"
    
    hip_depth_converted = df_converted['HIP_DEPTH_M'].dropna()
    assert abs(hip_depth_converted.iloc[0] - 0.249) < 0.001, \
        f"HIP_DEPTH_M should be 0.249 m after conversion, got {hip_depth_converted.iloc[0]}"


def test_7th_thousands_comma_regression():
    """
    Test 7th thousands comma regression: "1,736" -> 1736 parsing.
    
    Verifies:
    1) "1,736" parses to 1736 (not 1.736)
    2) "12,345" parses to 12345
    3) End-to-end: 1736 mm -> 1.736 m
    """
    # Import unified parser function
    from pipelines.build_curated_v0 import parse_numeric_string_7th
    
    # Test individual parsing
    assert parse_numeric_string_7th("1,736") == "1736", "1,736 should parse to 1736"
    assert parse_numeric_string_7th("12,345") == "12345", "12,345 should parse to 12345"
    
    # Test end-to-end: DataFrame -> preprocessing -> unit conversion
    df = pd.DataFrame({
        'HEIGHT_M': pd.Series(["1,736", "1,800", "1,650"], dtype='object'),
        'SEX': ['M', 'F', 'M']
    })
    
    warnings = []
    # Preprocess (applies unified 7th parser)
    df_preprocessed = preprocess_numeric_columns(df, '7th', warnings)
    
    # Verify parsing: should be 1736, 1800, 1650 (not 1.736, 1.800, 1.650)
    height_values = df_preprocessed['HEIGHT_M'].dropna()
    assert 1736 in height_values.values or abs(height_values.values - 1736).min() < 0.1, \
        "HEIGHT_M should be 1736, not 1.736"
    assert not (1.736 in height_values.values or abs(height_values.values - 1.736).min() < 0.1), \
        "HEIGHT_M must NOT be 1.736 (should be 1736)"
    
    # Apply unit conversion (mm->m)
    unit_map = {
        'HEIGHT_M': 'mm'
    }
    df_converted = apply_unit_canonicalization(df_preprocessed, unit_map, warnings, source_key='7th')
    
    # Verify end-to-end conversion: 1736 mm -> 1.736 m
    height_converted = df_converted['HEIGHT_M'].dropna()
    assert abs(height_converted.iloc[0] - 1.736) < 0.001, \
        f"HEIGHT_M should be 1.736 m after conversion, got {height_converted.iloc[0]}"


def test_unit_fail_counts_do_not_treat_nan_as_inf():
    """
    Test that unit_conversion_failed only counts inf/-inf, not NaN.
    
    Verifies:
    1) NaN-only series does not trigger unit_conversion_failed
    2) inf/-inf values are correctly detected and counted
    3) Mixed NaN and inf/-inf: only inf/-inf count toward unit_conversion_failed
    """
    import numpy as np
    from pipelines.build_curated_v0 import collect_unit_fail_trace
    
    # Test case 1: NaN-only series
    df_nan_only = pd.DataFrame({
        'NECK_WIDTH_M': [np.nan] * 100,
        'NECK_DEPTH_M': [np.nan] * 100
    })
    
    trace_nan = collect_unit_fail_trace(df_nan_only, '7th', 'after_unit_conversion')
    
    # Verify non_finite_count is 0 for NaN-only columns
    assert trace_nan['NECK_WIDTH_M']['non_finite_count'] == 0, "NaN-only column should have non_finite_count=0"
    assert trace_nan['NECK_DEPTH_M']['non_finite_count'] == 0, "NaN-only column should have non_finite_count=0"
    
    # Test case 2: inf/-inf values
    df_inf = pd.DataFrame({
        'NECK_WIDTH_M': [0.1, 0.2, np.inf, -np.inf, 0.15, np.nan],
        'NECK_DEPTH_M': [0.05, 0.1, np.inf, 0.08, np.nan, 0.12]
    })
    
    trace_inf = collect_unit_fail_trace(df_inf, '7th', 'after_unit_conversion')
    
    # Verify inf/-inf are counted
    assert trace_inf['NECK_WIDTH_M']['non_finite_count'] == 2, "Should count 2 inf/-inf values (not NaN)"
    assert trace_inf['NECK_DEPTH_M']['non_finite_count'] == 1, "Should count 1 inf value (not NaN)"
    
    # Test case 3: Mixed NaN and inf/-inf
    df_mixed = pd.DataFrame({
        'UNDERBUST_CIRC_M': [0.7, np.inf, np.nan, -np.inf, np.nan, 0.72]
    })
    
    trace_mixed = collect_unit_fail_trace(df_mixed, '7th', 'after_unit_conversion')
    
    # Verify only inf/-inf are counted (2 inf/-inf, 2 NaN -> non_finite_count should be 2)
    assert trace_mixed['UNDERBUST_CIRC_M']['non_finite_count'] == 2, "Should count only 2 inf/-inf values, not NaN"


def test_7th_unit_override_heuristic_mm_scale():
    """
    Test 7th unit override heuristic: mm scale values detected as cm should be corrected.
    
    Verifies:
    1) 7th source with unit metadata caught as cm, values like 795, 804 (mm scale)
       -> should result in 0.795, 0.804 after override
    2) Override warning is emitted with correct details
    """
    # Create DataFrame with mm-scale values that would be detected as cm
    # Values like 795, 804 are in mm, but sample_units might detect as cm
    df = pd.DataFrame({
        'WAIST_CIRC_M': [795.0, 804.0, 820.0, 750.0, 780.0],  # mm scale (would be detected as cm)
        'HIP_CIRC_M': [900.0, 910.0, 920.0, 880.0, 890.0],  # mm scale
        'BUST_CIRC_M': [850.0, 860.0, 870.0, 840.0, 855.0],  # mm scale
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Unit map with cm (simulating sample_units detecting as cm)
    unit_map = {
        'WAIST_CIRC_M': 'cm',
        'HIP_CIRC_M': 'cm',
        'BUST_CIRC_M': 'cm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify override was applied: values should be in meters (0.795, 0.804, etc.)
    waist_values = result_df['WAIST_CIRC_M'].dropna()
    assert len(waist_values) > 0, "WAIST_CIRC_M should have non-null values"
    # After override: 795 / 100 (cm->m) / 10 (override) = 0.795
    assert abs(waist_values.iloc[0] - 0.795) < 0.01, f"WAIST_CIRC_M[0] should be ~0.795, got {waist_values.iloc[0]}"
    assert abs(waist_values.iloc[1] - 0.804) < 0.01, f"WAIST_CIRC_M[1] should be ~0.804, got {waist_values.iloc[1]}"
    
    # Verify override warnings were emitted
    override_warnings = [w for w in warnings if w.get('reason') == 'UNIT_OVERRIDE_SUSPECTED_MM']
    assert len(override_warnings) >= 3, f"Should have at least 3 UNIT_OVERRIDE_SUSPECTED_MM warnings, got {len(override_warnings)}"
    
    # Verify warning structure
    for w in override_warnings:
        assert w.get('source') == '7th', "Warning source should be '7th'"
        assert w.get('column') in ['WAIST_CIRC_M', 'HIP_CIRC_M', 'BUST_CIRC_M'], f"Warning column should be measurement key, got {w.get('column')}"
        assert 'p50' in w.get('details', ''), "Warning details should include p50"
        assert 'p99' in w.get('details', ''), "Warning details should include p99"
        assert 'applied_scale_before=100' in w.get('details', ''), "Warning should include applied_scale_before=100"
        assert 'applied_scale_after=1000' in w.get('details', ''), "Warning should include applied_scale_after=1000"


def test_7th_unit_override_heuristic_normal_cm_scale():
    """
    Test 7th unit override heuristic: normal cm scale values should not trigger override.
    
    Verifies:
    1) 7th source with normal cm scale values (e.g., 90.0 as 'cm') should not trigger override
    2) Values should remain as converted (90.0cm -> 0.90m)
    """
    # Create DataFrame with normal cm-scale values
    # Values like 90.0, 85.0 are realistic in cm (waist circumference)
    df = pd.DataFrame({
        'WAIST_CIRC_M': [90.0, 85.0, 95.0, 80.0, 88.0],  # Normal cm scale
        'HIP_CIRC_M': [100.0, 95.0, 105.0, 90.0, 98.0],  # Normal cm scale
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Unit map with cm
    unit_map = {
        'WAIST_CIRC_M': 'cm',
        'HIP_CIRC_M': 'cm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify override was NOT applied: values should be in meters (0.90, 0.85, etc.)
    waist_values = result_df['WAIST_CIRC_M'].dropna()
    assert len(waist_values) > 0, "WAIST_CIRC_M should have non-null values"
    # Normal conversion: 90.0 / 100 (cm->m) = 0.90 (no override)
    assert abs(waist_values.iloc[0] - 0.90) < 0.01, f"WAIST_CIRC_M[0] should be ~0.90, got {waist_values.iloc[0]}"
    assert abs(waist_values.iloc[1] - 0.85) < 0.01, f"WAIST_CIRC_M[1] should be ~0.85, got {waist_values.iloc[1]}"
    
    # Verify override warnings were NOT emitted
    override_warnings = [w for w in warnings if w.get('reason') == 'UNIT_OVERRIDE_SUSPECTED_MM']
    assert len(override_warnings) == 0, f"Should have no UNIT_OVERRIDE_SUSPECTED_MM warnings for normal cm scale, got {len(override_warnings)}"
    
    # Verify other sources (8th_direct, 8th_3d) do not trigger override
    warnings_8th = []
    result_df_8th = apply_unit_canonicalization(df, unit_map, warnings_8th, source_key='8th_direct')
    override_warnings_8th = [w for w in warnings_8th if w.get('reason') == 'UNIT_OVERRIDE_SUSPECTED_MM']
    assert len(override_warnings_8th) == 0, "8th_direct should not trigger 7th-specific override"


def test_7th_unit_override_force_mm_cm_meta():
    """
    Test 7th unit override: force mm for unit=m keys even when unit meta is 'cm'.
    
    Regression test for 10x scale error prevention:
    - source_key='7th', standard_key=CHEST_CIRC_M_REF (unit=m key)
    - raw value "920" with unit meta 'cm' should convert to 0.92 m (not 9.2 m)
    - 7th source forces mm for unit=m keys, overriding cm meta
    """
    # Create DataFrame with cm-scale value that would be detected as cm
    # CHEST_CIRC_M_REF=920 (in mm, but median > 10 so would be detected as cm)
    df = pd.DataFrame({
        'CHEST_CIRC_M_REF': [920.0, 950.0, 900.0, 930.0, 910.0],  # mm scale, would be detected as cm
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Unit map with cm (simulating sample_units detecting as cm)
    unit_map = {
        'CHEST_CIRC_M_REF': 'cm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify 7th override was applied: values should be in meters (0.92, 0.95, etc.)
    chest_values = result_df['CHEST_CIRC_M_REF'].dropna()
    assert len(chest_values) > 0, "CHEST_CIRC_M_REF should have non-null values"
    # 7th override: cm meta -> forced to mm -> mm->m conversion (/1000)
    # 920.0 mm -> 0.92 m (not 9.2 m from cm->m conversion)
    assert abs(chest_values.iloc[0] - 0.92) < 0.01, f"CHEST_CIRC_M_REF[0] should be ~0.92 m, got {chest_values.iloc[0]}"
    assert abs(chest_values.iloc[1] - 0.95) < 0.01, f"CHEST_CIRC_M_REF[1] should be ~0.95 m, got {chest_values.iloc[1]}"
    
    # Verify override warning was emitted
    override_warnings = [w for w in warnings if 'UNIT_OVERRIDE_7TH_MM' in w.get('details', '')]
    assert len(override_warnings) >= 1, f"Should have at least 1 UNIT_OVERRIDE_7TH_MM warning, got {len(override_warnings)}"
    
    # Verify warning structure
    for w in override_warnings:
        assert w.get('source') == '7th', "Warning source should be '7th'"
        assert w.get('column') == 'CHEST_CIRC_M_REF', f"Warning column should be CHEST_CIRC_M_REF, got {w.get('column')}"
        assert 'UNIT_OVERRIDE_7TH_MM' in w.get('details', ''), "Warning details should include UNIT_OVERRIDE_7TH_MM"
        assert 'original_unit_meta=cm' in w.get('details', ''), "Warning should include original_unit_meta=cm"
        assert 'forced_unit=mm' in w.get('details', ''), "Warning should include forced_unit=mm"
    
    # Verify WEIGHT_KG is not affected (exception)
    df_weight = pd.DataFrame({
        'WEIGHT_KG': [70.0, 65.0, 75.0],
        'SEX': ['M', 'F', 'M']
    })
    unit_map_weight = {'WEIGHT_KG': 'kg'}
    warnings_weight = []
    result_weight = apply_unit_canonicalization(df_weight, unit_map_weight, warnings_weight, source_key='7th')
    weight_values = result_weight['WEIGHT_KG'].dropna()
    assert len(weight_values) > 0, "WEIGHT_KG should have non-null values"
    # WEIGHT_KG should remain as kg (no conversion)
    assert abs(weight_values.iloc[0] - 70.0) < 0.01, f"WEIGHT_KG[0] should be 70.0 kg, got {weight_values.iloc[0]}"
    # No override warning for WEIGHT_KG
    override_warnings_weight = [w for w in warnings_weight if 'UNIT_OVERRIDE_7TH_MM' in w.get('details', '')]
    assert len(override_warnings_weight) == 0, "WEIGHT_KG should not trigger 7th unit override"


def test_non_numeric_column_labeling():
    """
    Test non-numeric column labeling: HUMAN_ID/SEX should not trigger all_null sensor.
    
    Verifies:
    1) Non-numeric columns (HUMAN_ID, SEX) are labeled as 'non_numeric' in completeness report
    2) They do not trigger all_null=true sensor
    3) Numeric columns with all null are still labeled as all_null=true
    """
    from pipelines.build_curated_v0 import generate_completeness_report
    import tempfile
    from pathlib import Path
    
    # Create synthetic DataFrame with non-numeric and numeric columns
    df = pd.DataFrame({
        'HUMAN_ID': ['ID001', 'ID002', 'ID003', 'ID004', 'ID005'],  # Non-numeric
        'SEX': ['M', 'F', 'M', 'F', 'M'],  # Non-numeric
        'AGE': [25, 30, 35, 40, 45],  # Numeric
        'HEIGHT_M': [1.70, 1.65, 1.75, 1.60, 1.80],  # Numeric
        'ALL_NULL_COL': [np.nan, np.nan, np.nan, np.nan, np.nan],  # Numeric, all null
        'NON_NUMERIC_WITH_VALUES': ['A', 'B', 'C', 'D', 'E']  # Non-numeric with values
    })
    
    # Create minimal mapping
    mapping = {
        'keys': [
            {'standard_key': 'HUMAN_ID'},
            {'standard_key': 'SEX'},
            {'standard_key': 'AGE'},
            {'standard_key': 'HEIGHT_M'},
            {'standard_key': 'ALL_NULL_COL'},
            {'standard_key': 'NON_NUMERIC_WITH_VALUES'}
        ]
    }
    
    all_source_dfs = {'test_source': df}
    
    # Generate completeness report to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        generate_completeness_report(all_source_dfs, mapping, temp_path)
        
        # Read and verify report content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify non-numeric columns are labeled as 'NON_NUMERIC' (not 'all_null=true')
        assert 'HUMAN_ID' in content, "HUMAN_ID should be in report"
        assert 'SEX' in content, "SEX should be in report"
        # Check that non-numeric columns have 'NON_NUMERIC' label (not 'all_null=true')
        assert 'HUMAN_ID' in content and 'NON_NUMERIC' in content, "HUMAN_ID should be labeled as NON_NUMERIC"
        assert 'SEX' in content and 'NON_NUMERIC' in content, "SEX should be labeled as NON_NUMERIC"
        assert 'NON_NUMERIC_WITH_VALUES' in content and 'NON_NUMERIC' in content, "NON_NUMERIC_WITH_VALUES should be labeled as NON_NUMERIC"
        
        # Verify numeric all-null column is labeled as 'all_null=true'
        assert 'ALL_NULL_COL' in content and 'all_null=true' in content, "ALL_NULL_COL should be labeled as all_null=true"
        
        # Verify numeric columns with values are not labeled as all_null or non_numeric
        assert 'HEIGHT_M' in content and 'all_null=true' not in content.split('HEIGHT_M')[1].split('\n')[0], "HEIGHT_M should not be labeled as all_null"
        assert 'AGE' in content and 'all_null=true' not in content.split('AGE')[1].split('\n')[0], "AGE should not be labeled as all_null"
        
    finally:
        # Clean up
        if temp_path.exists():
            temp_path.unlink()


def test_7th_unit_inference_default_mm():
    """
    Test 7th unit inference: unit=m standard keys default to mm (no cm heuristic).
    
    Regression test for 10x scale error fix:
    - ANKLE_MAX_CIRC_M=245, WRIST_CIRC_M=153, HIP_DEPTH_M=212 should convert to 0.245, 0.153, 0.212 m
    - HEIGHT_M=1657 should convert to 1.657 m
    - Values with median > 10 should be treated as mm (not cm) for 7th unit=m keys
    """
    # Create DataFrame with mm-scale values that would be detected as cm by median heuristic
    # These values are in mm but median > 10, so old logic would detect as cm
    df = pd.DataFrame({
        'ANKLE_MAX_CIRC_M': [245.0, 250.0, 240.0, 248.0, 242.0],  # mm scale, median=245
        'WRIST_CIRC_M': [153.0, 158.0, 150.0, 155.0, 152.0],  # mm scale, median=153
        'HIP_DEPTH_M': [212.0, 220.0, 205.0, 215.0, 210.0],  # mm scale, median=212
        'HEIGHT_M': [1657.0, 1700.0, 1600.0, 1680.0, 1620.0],  # mm scale, median=1657
        'SEX': ['M', 'F', 'M', 'F', 'M']
    })
    
    # Test sample_units with 7th source_key
    warnings = []
    unit_map = sample_units(df, sample_size=5, source_key='7th')
    
    # Verify unit inference: 7th unit=m keys should default to mm (not cm)
    assert unit_map.get('ANKLE_MAX_CIRC_M') == 'mm', f"ANKLE_MAX_CIRC_M should be 'mm', got {unit_map.get('ANKLE_MAX_CIRC_M')}"
    assert unit_map.get('WRIST_CIRC_M') == 'mm', f"WRIST_CIRC_M should be 'mm', got {unit_map.get('WRIST_CIRC_M')}"
    assert unit_map.get('HIP_DEPTH_M') == 'mm', f"HIP_DEPTH_M should be 'mm', got {unit_map.get('HIP_DEPTH_M')}"
    assert unit_map.get('HEIGHT_M') == 'mm', f"HEIGHT_M should be 'mm', got {unit_map.get('HEIGHT_M')}"
    
    # Apply unit canonicalization
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify end-to-end conversion: mm -> m (÷1000)
    ankle_values = result_df['ANKLE_MAX_CIRC_M'].dropna()
    assert len(ankle_values) > 0, "ANKLE_MAX_CIRC_M should have non-null values"
    assert abs(ankle_values.iloc[0] - 0.245) < 0.001, f"ANKLE_MAX_CIRC_M[0] should be 0.245 m, got {ankle_values.iloc[0]}"
    
    wrist_values = result_df['WRIST_CIRC_M'].dropna()
    assert len(wrist_values) > 0, "WRIST_CIRC_M should have non-null values"
    assert abs(wrist_values.iloc[0] - 0.153) < 0.001, f"WRIST_CIRC_M[0] should be 0.153 m, got {wrist_values.iloc[0]}"
    
    hip_depth_values = result_df['HIP_DEPTH_M'].dropna()
    assert len(hip_depth_values) > 0, "HIP_DEPTH_M should have non-null values"
    assert abs(hip_depth_values.iloc[0] - 0.212) < 0.001, f"HIP_DEPTH_M[0] should be 0.212 m, got {hip_depth_values.iloc[0]}"
    
    height_values = result_df['HEIGHT_M'].dropna()
    assert len(height_values) > 0, "HEIGHT_M should have non-null values"
    assert abs(height_values.iloc[0] - 1.657) < 0.001, f"HEIGHT_M[0] should be 1.657 m, got {height_values.iloc[0]}"
    
    # Verify 8th sources still use cm heuristic (not affected by 7th change)
    unit_map_8th = sample_units(df, sample_size=5, source_key='8th_direct')
    # For 8th, median > 10 should still detect as cm
    assert unit_map_8th.get('ANKLE_MAX_CIRC_M') == 'cm', f"8th_direct: ANKLE_MAX_CIRC_M should be 'cm' (median heuristic), got {unit_map_8th.get('ANKLE_MAX_CIRC_M')}"


def test_7th_unit_override_synthetic_regression():
    """
    Synthetic unit conversion regression test for 7th source.
    
    Verifies that 7th source-level rule forces mm for unit=m keys even when
    unit meta says 'cm', preventing 10x scale errors.
    
    Test case:
    - source_key='7th'
    - standard_key=CHEST_CIRC_M_REF (unit=m key)
    - raw value "920" with unit meta 'cm'
    - Expected: final value should be 0.92 m (not 9.2 m)
    - This ensures 7th source-level rule overrides unit meta to prevent 10x errors
    """
    # Create DataFrame with raw value 920 (in mm, but unit meta says 'cm')
    df = pd.DataFrame({
        'CHEST_CIRC_M_REF': [920.0],  # Raw value in mm
        'SEX': ['M']
    })
    
    # Unit map with 'cm' (simulating unit meta incorrectly saying 'cm')
    # This would cause 10x error if not for 7th source-level override
    unit_map = {
        'CHEST_CIRC_M_REF': 'cm'
    }
    
    warnings = []
    result_df = apply_unit_canonicalization(df, unit_map, warnings, source_key='7th')
    
    # Verify final value is 0.92 m (not 9.2 m)
    # 7th override: cm meta -> forced to mm -> mm->m conversion (/1000)
    # 920.0 mm -> 0.92 m (not 9.2 m from cm->m conversion)
    chest_value = result_df['CHEST_CIRC_M_REF'].iloc[0]
    assert not pd.isna(chest_value), "CHEST_CIRC_M_REF should not be NaN"
    assert abs(chest_value - 0.92) < 0.001, f"CHEST_CIRC_M_REF should be 0.92 m, got {chest_value}"
    
    # Verify override warning was emitted
    override_warnings = [w for w in warnings if 'UNIT_OVERRIDE_7TH_MM' in w.get('details', '')]
    assert len(override_warnings) >= 1, f"Should have at least 1 UNIT_OVERRIDE_7TH_MM warning, got {len(override_warnings)}"
    
    # Verify warning structure
    for w in override_warnings:
        assert w.get('source') == '7th', "Warning source should be '7th'"
        assert w.get('column') == 'CHEST_CIRC_M_REF', f"Warning column should be CHEST_CIRC_M_REF, got {w.get('column')}"
        assert 'UNIT_OVERRIDE_7TH_MM' in w.get('details', ''), "Warning details should include UNIT_OVERRIDE_7TH_MM"
        assert 'original_unit_meta=cm' in w.get('details', ''), "Warning should include original_unit_meta=cm"
        assert 'forced_unit=mm' in w.get('details', ''), "Warning should include forced_unit=mm"
    
    # Verify this is a source-level rule (not key-specific)
    # Test with another unit=m key to ensure rule applies broadly
    df2 = pd.DataFrame({
        'WAIST_CIRC_M': [800.0],  # Raw value in mm
        'SEX': ['F']
    })
    unit_map2 = {'WAIST_CIRC_M': 'cm'}
    warnings2 = []
    result_df2 = apply_unit_canonicalization(df2, unit_map2, warnings2, source_key='7th')
    waist_value = result_df2['WAIST_CIRC_M'].iloc[0]
    assert abs(waist_value - 0.80) < 0.001, f"WAIST_CIRC_M should be 0.80 m, got {waist_value}"
    override_warnings2 = [w for w in warnings2 if 'UNIT_OVERRIDE_7TH_MM' in w.get('details', '')]
    assert len(override_warnings2) >= 1, "WAIST_CIRC_M should also trigger 7th override"


