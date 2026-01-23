#!/usr/bin/env python3
"""
Build curated_v0 dataset from SizeKorea raw data.

This pipeline:
1. Extracts columns based on sizekorea column mapping (v2 by default)
2. Standardizes headers to standard_key (45 keys)
3. Applies unit canonicalization (mm/cm/m -> m)
4. Handles outliers (if rules exist) or records warnings
5. Handles missing values (NaN + warnings)

Contract: docs/data/curated_v0_plan.md
"""

import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import sys
import re

# Import canonicalization function
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.ingestion import canonicalize_units_to_m


# Source file mapping
SOURCE_FILES = {
    "7th": "data/raw/sizekorea_raw/7th_data.csv",  # CSV fallback, XLSX preferred
    "8th_direct": "data/raw/sizekorea_raw/8th_data_direct.csv",
    "8th_3d": "data/raw/sizekorea_raw/8th_data_3d.csv",
}

# Header row for each source (from columns_by_file.json)
HEADER_ROWS = {
    "7th": 6,
    "8th_direct": 6,
    "8th_3d": 6,
}


def find_header_rows(file_path: Path, mapping: Dict[str, Any], is_xlsx: bool = False, 
                     source_key: str = None, max_check: int = 20) -> tuple[int, Optional[int], Optional[int]]:
    """
    Find primary, code, and secondary header rows.
    
    Primary header: First column value exactly matches "표준 측정항목 명" (for measurements).
    - Typically row 4 (0-indexed) for 7th data when anchor is found.
    
    Code row: Row containing "표준 측정항목 코드" (typically primary_row + 1).
    - Typically row 5 (0-indexed) for 7th data.
    
    Secondary header: Row containing "성별"/"SEX" or "ID"/"HUMAN_ID" tokens (for meta columns).
    - Searched in range primary+1 to primary+6 (typically row 6 for 7th data).
    - For 8th series, secondary header strings are cleaned (numeric prefix removed).
    
    Returns (primary_row, code_row, secondary_row) where code_row and secondary_row may be None.
    """
    anchor_term = "표준 측정항목 명"
    anchor_term_with_space = " " + anchor_term
    code_term = "표준 측정항목 코드"
    
    # Secondary header tokens (exact match or contains)
    secondary_tokens = ["성별", "SEX", "ID", "HUMAN_ID", "HUMAN ID", "나이"]
    
    primary_row = None
    code_row = None
    secondary_row = None
    
    if is_xlsx:
        # Read Excel file
        try:
            df_sample = pd.read_excel(file_path, header=None, nrows=max_check, engine='openpyxl')
        except Exception:
            return (HEADER_ROWS.get('7th', 4), None, None)
    else:
        # Read CSV file
        encodings = ['utf-8-sig', 'cp949', 'utf-8']
        df_sample = None
        for enc in encodings:
            try:
                df_sample = pd.read_csv(file_path, encoding=enc, header=None, nrows=max_check, low_memory=False)
                break
            except (UnicodeDecodeError, Exception):
                continue
        
        if df_sample is None:
            return (HEADER_ROWS.get('7th', 4), None, None)
    
    # Find primary header (anchor term)
    # Search for "표준 측정항목 명" in ANY cell of the row (not just first column)
    # For 8th data, anchor is in col1, not col0
    for i in range(len(df_sample)):
        # Check all columns in this row
        for col_idx in range(len(df_sample.columns)):
            cell_val = df_sample.iloc[i, col_idx]
            if pd.notna(cell_val):
                cell_val_str = str(cell_val).strip()
                if cell_val_str == anchor_term or cell_val_str == anchor_term_with_space:
                    primary_row = i
                    break
        if primary_row is not None:
            break
    
    # Find code row (표준 측정항목 코드) - typically primary_row + 1
    if primary_row is not None:
        # Check primary_row + 1 for code term
        if primary_row + 1 < len(df_sample):
            code_candidate_row = primary_row + 1
            for col_idx in range(len(df_sample.columns)):
                cell_val = df_sample.iloc[code_candidate_row, col_idx]
                if pd.notna(cell_val):
                    cell_val_str = str(cell_val).strip()
                    if code_term in cell_val_str:
                        code_row = code_candidate_row
                        break
    
    # Find secondary header (SEX/HUMAN_ID) near primary
    # Search range: primary+1 to primary+6 (typically row 7 for 7th when primary is row 5)
    if primary_row is not None:
        search_start = primary_row + 1  # Start after primary
        search_end = min(len(df_sample), primary_row + 7)  # Up to +6 rows after primary
        
        for i in range(search_start, search_end):
            if i == primary_row:
                continue  # Skip primary row
            
            # Check all columns for secondary tokens
            row_values = [str(v) for v in df_sample.iloc[i].astype(str).tolist() if pd.notna(v)]
            row_str = ' '.join(row_values)
            
            # Clean numeric prefix for 8th series (remove leading numbers)
            cleaned_row_str = row_str
            if '8th' in str(file_path):
                # Remove leading numeric patterns (e.g., "123.0 성별" -> "성별")
                cleaned_row_str = re.sub(r'^\d+\.?\d*\s*', '', row_str)
            
            # Check each column value individually for secondary tokens
            for col_idx in range(len(df_sample.columns)):
                if col_idx >= len(row_values):
                    continue
                cell_value = str(df_sample.iloc[i, col_idx]).strip() if pd.notna(df_sample.iloc[i, col_idx]) else ""
                
                # Clean numeric prefix if needed
                if '8th' in str(file_path):
                    cell_value = re.sub(r'^\d+\.?\d*\s*', '', cell_value)
                
                # Check for secondary tokens (contains match)
                for token in secondary_tokens:
                    if token in cell_value:
                        secondary_row = i
                        break
                
                if secondary_row is not None:
                    break
            
            if secondary_row is not None:
                break
    
    # Fallback: if primary not found, use default
    if primary_row is None:
        if '7th' in str(file_path):
            primary_row = HEADER_ROWS.get('7th', 4)
        elif '8th_direct' in str(file_path):
            primary_row = HEADER_ROWS.get('8th_direct', 4)
        elif '8th_3d' in str(file_path):
            primary_row = HEADER_ROWS.get('8th_3d', 4)
        else:
            primary_row = 4
    
    return (primary_row, code_row, secondary_row)


def find_header_row(file_path: Path, mapping: Dict[str, Any], encoding: str = 'utf-8-sig', max_check: int = 20) -> int:
    """
    Find header row (primary) - kept for backward compatibility.
    """
    primary_row, _, _ = find_header_rows(file_path, mapping, is_xlsx=False, max_check=max_check)
    return primary_row


def load_mapping_v1(mapping_path: Path) -> Dict[str, Any]:
    """Load sizekorea column mapping (v1 or v2)."""
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_raw_file(file_path: Path, header_row: int, secondary_header_row: Optional[int] = None, 
                  source_key: str = None, encoding: str = 'utf-8-sig', is_xlsx: bool = False) -> pd.DataFrame:
    """
    Load raw file (CSV or XLSX) with specified header row(s).
    
    For 7th source, prefers XLSX over CSV to preserve HUMAN_ID as string.
    For HUMAN_ID/SEX columns, uses secondary_header_row if available.
    
    Args:
        file_path: Path to file
        header_row: Primary header row (for measurements)
        secondary_header_row: Secondary header row (for HUMAN_ID/SEX), optional
        source_key: Source key ('7th', '8th_direct', '8th_3d')
        encoding: Encoding for CSV (ignored for XLSX)
        is_xlsx: Whether file is XLSX format
    """
    # For 7th, prefer XLSX if available
    if source_key == '7th' and not is_xlsx:
        xlsx_path = file_path.parent / "7th_data.xlsx"
        if xlsx_path.exists():
            file_path = xlsx_path
            is_xlsx = True
    
    if is_xlsx:
        # Load XLSX with HUMAN_ID as string
        try:
            # Find HUMAN_ID column index from secondary header if available
            converters = {}
            if secondary_header_row is not None:
                # Read secondary header to find HUMAN_ID column
                df_secondary_header = pd.read_excel(file_path, header=secondary_header_row, nrows=0, engine='openpyxl')
                for col_idx, col_name in enumerate(df_secondary_header.columns):
                    col_str = str(col_name).strip()
                    # Check if column contains ID or HUMAN_ID token
                    if 'ID' in col_str or 'HUMAN_ID' in col_str:
                        # Use column name as key for converter
                        converters[col_name] = lambda x: str(x).strip() if pd.notna(x) else ""
            
            # Load with primary header
            df = pd.read_excel(file_path, header=header_row, engine='openpyxl', converters=converters)
            
            # Ensure HUMAN_ID is string if present
            for col in df.columns:
                col_str = str(col).strip()
                if 'ID' in col_str or 'HUMAN_ID' in col_str:
                    df[col] = df[col].astype(str).str.strip()
                    # Remove .0 suffix if present (conservative normalization)
                    df[col] = df[col].str.replace(r'\.0$', '', regex=True)
            
            return df
        except Exception as e:
            # Fallback to CSV if XLSX load fails
            if source_key == '7th':
                csv_path = file_path.parent / "7th_data.csv"
                if csv_path.exists():
                    return load_raw_file(csv_path, header_row, secondary_header_row, source_key, encoding, is_xlsx=False)
            return pd.DataFrame()
    else:
        # Load CSV
        encodings = [encoding, 'cp949', 'utf-8']
        
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc, header=header_row, low_memory=False)
                
                # Ensure HUMAN_ID is string if present (for CSV fallback)
                for col in df.columns:
                    col_str = str(col).strip()
                    if 'ID' in col_str or 'HUMAN_ID' in col_str:
                        df[col] = df[col].astype(str).str.strip()
                        # Remove .0 suffix if present
                        df[col] = df[col].str.replace(r'\.0$', '', regex=True)
                
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if enc == encodings[-1]:
                    return pd.DataFrame()
                continue
        
        return pd.DataFrame()


def preprocess_numeric_columns(df: pd.DataFrame, source_key: str, warnings: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Preprocess numeric columns: remove commas (7th), replace sentinel values.
    
    - 7th: Remove thousand separators (commas) from numeric columns
    - 8th_direct: Replace 9999 with NaN (sentinel missing)
    - 7th/8th_3d: Replace empty strings with NaN
    """
    result_df = df.copy()
    
    # Identify numeric columns (exclude meta columns)
    meta_cols = ['SEX', 'AGE', 'HUMAN_ID']
    numeric_cols = [col for col in df.columns if col not in meta_cols]
    
    for col in numeric_cols:
        if col not in df.columns:
            continue
        
        original_series = df[col]
        
        # 7th: Remove commas from numeric strings
        if source_key == '7th':
            if original_series.dtype == 'object':
                # Try to remove commas and convert to numeric
                cleaned = original_series.astype(str).str.replace(',', '', regex=False)
                try:
                    numeric_series = pd.to_numeric(cleaned, errors='coerce')
                    result_df[col] = numeric_series
                    # Count parsing failures
                    failed_count = numeric_series.isna().sum() - original_series.isna().sum()
                    if failed_count > 0:
                        warnings.append({
                            "source": source_key,
                            "file": SOURCE_FILES[source_key],
                            "column": col,
                            "reason": "numeric_parsing_failed",
                            "row_index": None,
                            "original_value": None,
                            "details": f"{failed_count} values failed to parse after comma removal"
                        })
                except Exception:
                    pass  # Keep original if conversion fails
        
        # 8th_direct: Replace 9999 with NaN (dtype-agnostic)
        if source_key == '8th_direct':
            # Handle both numeric and string/object types
            if pd.api.types.is_numeric_dtype(result_df[col]):
                sentinel_mask = result_df[col] == 9999
            else:
                # For object/string types, check string representation
                sentinel_mask = (result_df[col].astype(str).str.strip() == '9999')
            
            sentinel_count = sentinel_mask.sum()
            if sentinel_count > 0:
                result_df.loc[sentinel_mask, col] = np.nan
                warnings.append({
                    "source": source_key,
                    "file": SOURCE_FILES[source_key],
                    "column": col,
                    "reason": "SENTINEL_MISSING",
                    "row_index": None,
                    "original_value": None,  # Aggregated warning, individual row values not tracked
                    "sentinel_value": "9999",
                    "sentinel_count": int(sentinel_count),
                    "details": f"{sentinel_count} sentinel values (9999) replaced with NaN"
                })
        
        # 7th/8th_3d: Replace empty strings with NaN
        if source_key in ['7th', '8th_3d']:
            if original_series.dtype == 'object':
                empty_mask = (original_series.astype(str).str.strip() == '') | (original_series.isna())
                # Count non-null empty strings
                empty_count = ((original_series.astype(str).str.strip() == '') & (original_series.notna())).sum()
                if empty_count > 0:
                    result_df.loc[empty_mask, col] = np.nan
                    warnings.append({
                        "source": source_key,
                        "file": SOURCE_FILES[source_key],
                        "column": col,
                        "reason": "SENTINEL_MISSING",
                        "row_index": None,
                        "original_value": None,  # Aggregated warning, individual row values not tracked
                        "sentinel_value": "",
                        "sentinel_count": int(empty_count),
                        "details": f"{empty_count} empty string values replaced with NaN"
                    })
    
    return result_df


def normalize_sex(df: pd.DataFrame, source_key: str, warnings: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Normalize sex values: 남/여 → M/F.
    
    Contract: 남/M → M, 여/F → F
    """
    result_df = df.copy()
    
    if 'SEX' not in df.columns:
        return result_df
    
    # Normalize based on source
    if source_key == '7th':
        # 7th uses 남/여
        result_df['SEX'] = result_df['SEX'].astype(str).str.strip()
        result_df['SEX'] = result_df['SEX'].replace({'남': 'M', '여': 'F'})
    else:
        # 8th_direct/8th_3d use M/F (already normalized)
        result_df['SEX'] = result_df['SEX'].astype(str).str.strip().str.upper()
        # Ensure only M/F
        invalid_mask = ~result_df['SEX'].isin(['M', 'F'])
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            warnings.append({
                "source": source_key,
                "file": SOURCE_FILES[source_key],
                "column": "SEX",
                "reason": "value_missing",
                "row_index": None,
                "original_value": None,
                "details": f"{invalid_count} invalid sex values found"
            })
            result_df.loc[invalid_mask, 'SEX'] = np.nan
    
    return result_df


def extract_columns_from_source(
    df: pd.DataFrame,
    df_secondary: Optional[pd.DataFrame],
    source_key: str,
    mapping: Dict[str, Any],
    warnings: List[Dict[str, Any]],
    collect_trace: bool = False,
    trace_data: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Extract and standardize columns from raw DataFrame based on mapping.
    
    Uses per-key header selection:
    - HUMAN_ID/SEX: Use secondary header DataFrame if available
    - Other keys: Use primary header DataFrame
    
    Returns DataFrame with standard_key columns (45 keys).
    Missing columns are filled with NaN.
    """
    result_data = {}
    num_rows = len(df)
    
    # Keys that use secondary header
    secondary_keys = {'HUMAN_ID', 'SEX', 'AGE'}
    
    for key_info in mapping['keys']:
        standard_key = key_info['standard_key']
        source_info = key_info['sources'].get(source_key, {})
        
        if not source_info.get('present', False) or source_info.get('column') is None:
            # Column not present in this source
            result_data[standard_key] = np.full(num_rows, np.nan)
            warnings.append({
                "source": source_key,
                "file": SOURCE_FILES[source_key],
                "column": standard_key,
                "reason": "column_not_present",
                "row_index": None,
                "original_value": None,
                "details": f"Column '{source_info.get('column')}' not mapped in {source_key}"
            })
            continue
        
        raw_column = source_info['column']
        
        # Select DataFrame based on key type
        source_df = df_secondary if (standard_key in secondary_keys and df_secondary is not None) else df
        
        if raw_column not in source_df.columns:
            # Column name exists in mapping but not in DataFrame
            result_data[standard_key] = np.full(num_rows, np.nan)
            warnings.append({
                "source": source_key,
                "file": SOURCE_FILES[source_key],
                "column": standard_key,
                "reason": "column_not_found",
                "row_index": None,
                "original_value": None,
                "details": f"Mapped column '{raw_column}' not found in DataFrame"
            })
            continue
        
        # Extract column values
        # Align lengths: use primary DataFrame length as reference
        if standard_key == 'HUMAN_ID':
            # Ensure HUMAN_ID is string
            values = source_df[raw_column].astype(str).values
            # Align to primary DataFrame length if needed
            if len(values) != num_rows:
                # Pad or truncate to match primary DataFrame
                if len(values) < num_rows:
                    values = np.concatenate([values, [""] * (num_rows - len(values))])
                else:
                    values = values[:num_rows]
            result_data[standard_key] = values
        else:
            values = source_df[raw_column].values
            # Align to primary DataFrame length if needed
            if len(values) != num_rows:
                if len(values) < num_rows:
                    values = np.concatenate([values, [np.nan] * (num_rows - len(values))])
                else:
                    values = values[:num_rows]
            result_data[standard_key] = values
    
    # Create DataFrame before preprocessing for trace
    df_before_preprocess = pd.DataFrame(result_data, index=df.index)
    
    # Collect trace before preprocessing (for ARM_LEN_M and KNEE_HEIGHT_M only)
    if collect_trace and trace_data is not None and source_key in ['8th_direct', '8th_3d']:
        trace_before = collect_arm_knee_trace(df_before_preprocess, source_key, 'after_extraction_before_preprocess')
        if 'traces' not in trace_data:
            trace_data['traces'] = []
        trace_data['traces'].append(trace_before)
    
    # Preprocess numeric columns (comma removal, sentinel replacement)
    # HUMAN_ID is excluded from numeric processing
    df_preprocessed = preprocess_numeric_columns(df_before_preprocess, source_key, warnings)
    
    # Normalize sex values
    if 'SEX' in df_preprocessed.columns:
        df_preprocessed = normalize_sex(df_preprocessed, source_key, warnings)
    
    # Update result_data with preprocessed values
    for col in df_preprocessed.columns:
        if col in result_data:
            result_data[col] = df_preprocessed[col].values
    
    # Ensure HUMAN_ID remains string
    if 'HUMAN_ID' in result_data:
        result_data['HUMAN_ID'] = pd.Series(result_data['HUMAN_ID']).astype(str).values
    
    # Create DataFrame with all standard keys
    result_df = pd.DataFrame(result_data, index=df.index)
    
    # Ensure all 45 standard keys are present (fill missing with NaN)
    all_keys = [k['standard_key'] for k in mapping['keys']]
    for key in all_keys:
        if key not in result_df.columns:
            if key == 'HUMAN_ID':
                result_df[key] = pd.Series([""] * num_rows, dtype=str)
            else:
                result_df[key] = np.nan
    
    # Reorder columns to match standard keys order
    result_df = result_df[all_keys]
    
    return result_df


def sample_units(df: pd.DataFrame, sample_size: int = 100) -> Dict[str, str]:
    """
    Sample values to determine source units.
    
    Returns dict mapping column -> unit ("mm", "cm", or "m").
    Uses heuristics based on value ranges.
    
    Contract:
    - Length/circumference: mm → m (÷1000)
    - Weight: kg (no conversion)
    """
    unit_map = {}
    
    # Sample numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue  # Skip meta columns
        
        # Sample non-null values
        sample_values = df[col].dropna().head(sample_size)
        
        if len(sample_values) == 0:
            continue
        
        max_val = sample_values.max()
        min_val = sample_values.min()
        median_val = sample_values.median()
        
        # Contract: Weight is in kg (no conversion)
        if col == 'WEIGHT_KG':
            unit_map[col] = "kg"
            continue
        
        # Contract: Length/circumference are in mm (convert to m)
        # Heuristic: typical human measurements
        # Height: ~1.5-2.0m, if in mm: 1500-2000, if in cm: 150-200
        # Circumference: ~0.5-1.5m, if in mm: 500-1500, if in cm: 50-150
        
        if col == 'HEIGHT_M':
            if median_val > 1000:
                unit_map[col] = "mm"
            elif median_val > 10:
                unit_map[col] = "cm"
            else:
                unit_map[col] = "m"
        elif 'CIRC' in col or 'LEN' in col or 'WIDTH' in col or 'DEPTH' in col or 'HEIGHT' in col:
            # Measurement columns (length/circumference)
            if median_val > 1000:
                unit_map[col] = "mm"  # Will be converted to m
            elif median_val > 10:
                unit_map[col] = "cm"  # Will be converted to m
            else:
                unit_map[col] = "m"
        else:
            # Default: assume mm (SizeKorea standard) for measurements
            if median_val > 1000:
                unit_map[col] = "mm"
            elif median_val > 10:
                unit_map[col] = "cm"
            else:
                unit_map[col] = "m"
    
    return unit_map


def apply_unit_canonicalization(
    df: pd.DataFrame,
    unit_map: Dict[str, str],
    warnings: List[Dict[str, Any]],
    source_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Apply unit canonicalization to DataFrame.
    
    Converts all measurement columns to meters (m) with 0.001m quantization.
    HUMAN_ID is explicitly excluded from any conversion.
    """
    result_df = df.copy()
    warning_list = []  # For canonicalize_units_to_m
    
    for col in df.columns:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue  # Meta columns, no conversion (HUMAN_ID must remain string)
        
        if col == 'WEIGHT_KG':
            # Weight is already in kg, no conversion
            continue
        
        if col not in unit_map:
            # Unit not determined
            # For 8th_direct/8th_3d, apply mm->m fallback for unit=m keys (length/height/circumference)
            if source_key in {"8th_direct", "8th_3d"}:
                # Check if this is a unit=m key (standard_key ends with _M or is a measurement key)
                is_m_unit_key = (
                    col.endswith("_M") or 
                    col.endswith("_CIRC_M") or 
                    col.endswith("_LEN_M") or 
                    col.endswith("_HEIGHT_M") or
                    col.endswith("_WIDTH_M") or
                    col.endswith("_DEPTH_M")
                ) and col not in ['SEX', 'AGE', 'HUMAN_ID', 'WEIGHT_KG']
                
                if is_m_unit_key:
                    # Apply mm->m fallback (÷1000)
                    values = df[col].values
                    non_null_before = pd.Series(values).notna().sum()
                    
                    # Convert mm to m
                    converted = canonicalize_units_to_m(values, "mm", warning_list)
                    result_df[col] = converted
                    
                    non_null_after = pd.Series(converted).notna().sum()
                    
                    # Record aggregated warning
                    file_path = SOURCE_FILES.get(source_key, "unknown")
                    warnings.append({
                        "source": source_key,
                        "file": file_path,
                        "column": col,
                        "reason": "unit_conversion_applied",
                        "row_index": None,
                        "original_value": None,
                        "details": f"UNIT_DEFAULT_MM_NO_UNIT: assumed_unit=mm, applied_scale=1000, non_null_before={non_null_before}, non_null_after={non_null_after}"
                    })
                    
                    # Convert warning_list strings to structured warnings
                    for w in warning_list:
                        if "UNIT_FAIL" in w or "PROVENANCE" in w:
                            warnings.append({
                                "source": source_key,
                                "file": file_path,
                                "column": col,
                                "reason": "unit_conversion_failed" if "UNIT_FAIL" in w else "unit_conversion_applied",
                                "row_index": None,
                                "original_value": None,
                                "details": w
                            })
                    
                    warning_list.clear()
                    continue
            
            # Default: unit not determined, set to NaN
            result_df[col] = np.nan
            # Ensure source_key is set (should not be None at this point)
            warning_source = source_key if source_key else "system"
            file_path = SOURCE_FILES.get(warning_source, "unknown") if warning_source != "system" else "build_curated_v0.py"
            warnings.append({
                "source": warning_source,
                "file": file_path,
                "column": col,
                "reason": "unit_undetermined",
                "row_index": None,
                "original_value": None,
                "details": "Could not determine source unit for column"
            })
            continue
        
        source_unit = unit_map[col]
        
        if source_unit not in ["mm", "cm", "m"]:
            # Invalid unit (e.g., "kg" for measurement, "g" for weight)
            result_df[col] = np.nan
            # Ensure source_key is set (should not be None at this point)
            warning_source = source_key if source_key else "system"
            warnings.append({
                "source": warning_source,
                "file": SOURCE_FILES.get(warning_source, "unknown") if warning_source != "system" else "build_curated_v0.py",
                "column": col,
                "reason": "unit_conversion_failed",
                "row_index": None,
                "original_value": None,
                "details": f"Invalid source unit '{source_unit}' for column"
            })
            continue
        
        # Apply canonicalization
        values = df[col].values
        converted = canonicalize_units_to_m(values, source_unit, warning_list)
        result_df[col] = converted
        
        # Convert warning_list strings to structured warnings
        # Ensure source_key is set (should not be None at this point)
        warning_source = source_key if source_key else "system"
        file_path = SOURCE_FILES.get(warning_source, "unknown") if warning_source != "system" else "build_curated_v0.py"
        for w in warning_list:
            if "UNIT_FAIL" in w or "PROVENANCE" in w:
                warnings.append({
                    "source": warning_source,
                    "file": file_path,
                    "column": col,
                    "reason": "unit_conversion_failed" if "UNIT_FAIL" in w else "unit_conversion_applied",
                    "row_index": None,
                    "original_value": None,
                    "details": w
                })
        
        warning_list.clear()  # Clear for next column
    
    return result_df


def apply_outlier_removal(
    df: pd.DataFrame,
    warnings: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Apply outlier removal if rules exist.
    
    Currently, no explicit outlier removal rules are found in the codebase.
    Records warning and returns DataFrame unchanged.
    """
    # Check if outlier rules exist (they don't in current codebase)
    warnings.append({
        "source": "system",
        "file": "build_curated_v0.py",
        "column": "all",
        "reason": "OUTLIER_RULES_NOT_FOUND",
        "row_index": None,
        "original_value": None,
        "details": "No explicit outlier removal rules found in codebase. Outlier removal step skipped."
    })
    
    # Apply age filter (20-50대) if AGE column exists
    if 'AGE' in df.columns:
        age_mask = df['AGE'].between(20, 59, inclusive='both')
        removed_count = (~age_mask).sum()
        if removed_count > 0:
            warnings.append({
                "source": "system",
                "file": "build_curated_v0.py",
                "column": "AGE",
                "reason": "age_filter_applied",
                "row_index": None,
                "original_value": None,
                "details": f"Filtered {removed_count} rows outside age range 20-59"
            })
            df = df[age_mask].copy()
    
    return df


def handle_missing_values(
    df: pd.DataFrame,
    source_key: str,
    warnings: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Handle missing values: record warnings, keep NaN.
    
    Refined deduplication: Exclude sentinel_count from value_missing accounting.
    - For columns with SENTINEL_MISSING warnings, subtract sentinel_count from total missing
    - Only record value_missing for remaining missing values (non-sentinel missing)
    
    No exceptions raised (NaN + warnings policy).
    """
    # Build map of columns to sentinel_count from SENTINEL_MISSING warnings
    sentinel_counts = {}
    for w in warnings:
        if (w.get('reason') == 'SENTINEL_MISSING' and 
            w.get('source') == source_key and 
            w.get('column') != 'all'):
            col = w.get('column')
            sentinel_count = w.get('sentinel_count', 0)
            if col not in sentinel_counts:
                sentinel_counts[col] = 0
            sentinel_counts[col] += sentinel_count
    
    for col in df.columns:
        missing_count_total = df[col].isna().sum()
        if missing_count_total > 0:
            # Calculate remaining missing (excluding sentinel counts)
            sentinel_count_total = sentinel_counts.get(col, 0)
            remaining = max(missing_count_total - sentinel_count_total, 0)
            
            # Only record value_missing if there are remaining non-sentinel missing values
            if remaining > 0:
                warnings.append({
                    "source": source_key,
                    "file": SOURCE_FILES[source_key],
                    "column": col,
                    "reason": "value_missing",
                    "row_index": None,
                    "original_value": None,
                    "details": f"{remaining} missing values in column (excluding {sentinel_count_total} sentinel values)"
                })
    
    return df


def detect_duplicate_headers(df: pd.DataFrame, source_key: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect duplicate headers (e.g., "키", "키.1") and report non-null counts for each.
    
    Returns dict mapping base_header -> list of {column_name, non_null_count, total_rows}
    """
    duplicate_info = {}
    
    # Group columns by base header (remove .1, .2 suffixes)
    base_header_map = {}
    for col in df.columns:
        col_str = str(col).strip()
        # Remove numeric suffix (e.g., "키.1" -> "키")
        base_header = re.sub(r'\.\d+$', '', col_str)
        if base_header not in base_header_map:
            base_header_map[base_header] = []
        base_header_map[base_header].append(col)
    
    # Find duplicates (base headers with multiple columns)
    for base_header, columns in base_header_map.items():
        if len(columns) > 1:
            duplicate_info[base_header] = []
            for col in columns:
                non_null_count = df[col].notna().sum()
                total_rows = len(df)
                duplicate_info[base_header].append({
                    "column_name": str(col),
                    "non_null_count": int(non_null_count),
                    "total_rows": int(total_rows),
                    "non_null_rate": float(non_null_count / total_rows) if total_rows > 0 else 0.0
                })
            # Sort by non_null_count descending
            duplicate_info[base_header].sort(key=lambda x: x["non_null_count"], reverse=True)
    
    return duplicate_info


def calculate_source_quality(
    df: pd.DataFrame,
    source_key: str,
    mapping: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate quality metrics for each standard_key in the source.
    
    Returns dict mapping standard_key -> {non_null_count, missing_count, missing_rate, total_rows}
    """
    quality = {}
    total_rows = len(df)
    
    # Get all standard keys from mapping
    for key_info in mapping['keys']:
        standard_key = key_info['standard_key']
        
        if standard_key not in df.columns:
            quality[standard_key] = {
                "non_null_count": 0,
                "missing_count": total_rows,
                "missing_rate": 1.0,
                "total_rows": total_rows
            }
            continue
        
        non_null_count = df[standard_key].notna().sum()
        missing_count = total_rows - non_null_count
        missing_rate = missing_count / total_rows if total_rows > 0 else 1.0
        
        quality[standard_key] = {
            "non_null_count": int(non_null_count),
            "missing_count": int(missing_count),
            "missing_rate": float(missing_rate),
            "total_rows": int(total_rows)
        }
    
    return quality


def generate_quality_summary(
    all_source_quality: Dict[str, Dict[str, Dict[str, Any]]],
    all_duplicate_headers: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_path: Path
) -> None:
    """
    Generate facts-only quality summary markdown file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# curated_v0 v3 Quality Summary (facts-only)\n\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 1. High missing rate keys (missing_rate >= 0.95)
        f.write("## High Missing Rate Keys (missing_rate >= 0.95)\n\n")
        high_missing = []
        for source_key, quality in all_source_quality.items():
            for standard_key, metrics in quality.items():
                if metrics["missing_rate"] >= 0.95:
                    high_missing.append({
                        "source": source_key,
                        "standard_key": standard_key,
                        "missing_rate": metrics["missing_rate"],
                        "missing_count": metrics["missing_count"],
                        "non_null_count": metrics["non_null_count"],
                        "total_rows": metrics["total_rows"]
                    })
        
        # Sort by missing_rate descending, then by source
        high_missing.sort(key=lambda x: (-x["missing_rate"], x["source"], x["standard_key"]))
        
        if high_missing:
            f.write("| source | standard_key | missing_rate | missing_count | non_null_count | total_rows |\n")
            f.write("|--------|--------------|--------------|---------------|----------------|------------|\n")
            for item in high_missing:
                f.write(f"| {item['source']} | {item['standard_key']} | {item['missing_rate']:.4f} | "
                       f"{item['missing_count']} | {item['non_null_count']} | {item['total_rows']} |\n")
        else:
            f.write("No keys with missing_rate >= 0.95.\n")
        f.write("\n")
        
        # 2. Duplicate header detection
        f.write("## Duplicate Header Detection\n\n")
        has_duplicates = False
        for source_key, duplicate_info in all_duplicate_headers.items():
            if duplicate_info:
                has_duplicates = True
                f.write(f"### {source_key}\n\n")
                for base_header, columns in duplicate_info.items():
                    f.write(f"**Base header: {base_header}**\n\n")
                    f.write("| column_name | non_null_count | total_rows | non_null_rate |\n")
                    f.write("|-------------|-----------------|------------|---------------|\n")
                    for col_info in columns:
                        f.write(f"| {col_info['column_name']} | {col_info['non_null_count']} | "
                               f"{col_info['total_rows']} | {col_info['non_null_rate']:.4f} |\n")
                    f.write("\n")
        
        if not has_duplicates:
            f.write("No duplicate headers detected.\n\n")
        
        # 3. Source completeness summary
        f.write("## Source Completeness Summary\n\n")
        for source_key, quality in all_source_quality.items():
            f.write(f"### {source_key}\n\n")
            f.write("| standard_key | non_null_count | missing_count | missing_rate | total_rows |\n")
            f.write("|--------------|----------------|---------------|--------------|------------|\n")
            
            # Sort by missing_rate descending
            sorted_keys = sorted(quality.items(), key=lambda x: (-x[1]["missing_rate"], x[0]))
            for standard_key, metrics in sorted_keys:
                f.write(f"| {standard_key} | {metrics['non_null_count']} | {metrics['missing_count']} | "
                       f"{metrics['missing_rate']:.4f} | {metrics['total_rows']} |\n")
            f.write("\n")


def find_header_candidates(
    df: pd.DataFrame,
    source_key: str,
    target_keys: List[str],
    primary_row: int
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Find header candidates for target keys in DataFrame.
    
    Args:
        df: Raw DataFrame with headers
        source_key: Source identifier (e.g., '8th_direct', '8th_3d')
        target_keys: List of standard keys to find candidates for
        primary_row: Primary header row index (for reference)
    
    Returns:
        Dictionary mapping standard_key -> list of candidate info
        Each candidate info contains: column_name, non_null_count, total_rows, missing_count
    """
    candidates = {}
    total_rows = len(df)
    
    # Search patterns for each target key
    search_patterns = {
        'ARM_LEN_M': ['팔길이'],
        'KNEE_HEIGHT_M': ['무릎높이', '앉은무릎높이']
    }
    
    for standard_key in target_keys:
        patterns = search_patterns.get(standard_key, [])
        if not patterns:
            continue
        
        key_candidates = []
        
        # Search all columns for matching headers
        for col in df.columns:
            col_str = str(col).strip()
            
            # Check if column name contains any search pattern
            matches_pattern = False
            for pattern in patterns:
                if pattern in col_str:
                    matches_pattern = True
                    break
            
            if matches_pattern:
                # Calculate non-null count
                non_null_count = df[col].notna().sum()
                missing_count = total_rows - non_null_count
                
                key_candidates.append({
                    "column_name": col_str,
                    "non_null_count": int(non_null_count),
                    "missing_count": int(missing_count),
                    "total_rows": int(total_rows),
                    "non_null_rate": float(non_null_count / total_rows) if total_rows > 0 else 0.0
                })
        
        # Sort by non_null_count descending
        key_candidates.sort(key=lambda x: x["non_null_count"], reverse=True)
        candidates[standard_key] = key_candidates
    
    return candidates


def emit_header_candidates(
    all_candidates: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_path: Path
):
    """
    Emit header candidates to markdown file (facts-only).
    
    Args:
        all_candidates: Dictionary mapping source_key -> {standard_key -> [candidate_info]}
        output_path: Path to output markdown file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Header Candidates Diagnostic (facts-only)\n\n")
        f.write("This document lists header candidates for specific keys in 8th_direct/8th_3d sources.\n")
        f.write("Each candidate shows non-null count and missing count for manual confirmation.\n\n")
        
        for source_key in ['8th_direct', '8th_3d']:
            if source_key not in all_candidates:
                continue
            
            f.write(f"## {source_key}\n\n")
            
            source_candidates = all_candidates[source_key]
            
            for standard_key in ['ARM_LEN_M', 'KNEE_HEIGHT_M']:
                if standard_key not in source_candidates:
                    f.write(f"### {standard_key}\n\n")
                    f.write("No candidates found.\n\n")
                    continue
                
                f.write(f"### {standard_key}\n\n")
                f.write("| Column Name | Non-Null Count | Missing Count | Total Rows | Non-Null Rate |\n")
                f.write("|-------------|----------------|---------------|------------|---------------|\n")
                
                for candidate in source_candidates[standard_key]:
                    col_name = candidate["column_name"]
                    non_null = candidate["non_null_count"]
                    missing = candidate["missing_count"]
                    total = candidate["total_rows"]
                    rate = candidate["non_null_rate"]
                    
                    f.write(f"| {col_name} | {non_null} | {missing} | {total} | {rate:.2%} |\n")
                
                f.write("\n")
    
    print(f"Saved header candidates: {output_path}")


def collect_arm_knee_trace(
    df: pd.DataFrame,
    source_key: str,
    stage: str,
    target_keys: List[str] = ['ARM_LEN_M', 'KNEE_HEIGHT_M']
) -> Dict[str, Dict[str, Any]]:
    """
    Collect trace data for ARM_LEN_M and KNEE_HEIGHT_M at a specific processing stage.
    
    Args:
        df: DataFrame at current stage
        source_key: Source identifier
        stage: Stage name (e.g., 'after_extraction', 'after_preprocess', 'after_unit_conversion')
        target_keys: List of standard keys to trace
    
    Returns:
        Dictionary mapping standard_key -> trace_info
    """
    trace_data = {}
    
    for standard_key in target_keys:
        if standard_key not in df.columns:
            trace_data[standard_key] = {
                "stage": stage,
                "source": source_key,
                "present": False,
                "dtype": None,
                "sample_values": [],
                "non_null_count": 0,
                "total_rows": len(df),
                "non_finite_count": 0,
                "min_value": None,
                "max_value": None
            }
            continue
        
        series = df[standard_key]
        non_null_count = series.notna().sum()
        
        # Get sample values (first 20 non-null values)
        sample_values = []
        non_null_series = series.dropna()
        if len(non_null_series) > 0:
            sample_values = non_null_series.head(20).tolist()
            # Convert to string for markdown output
            sample_values = [str(v) for v in sample_values]
        
        # Check for non-finite values
        if pd.api.types.is_numeric_dtype(series):
            non_finite_mask = ~np.isfinite(series)
            non_finite_count = non_finite_mask.sum()
            
            # Get min/max from finite values
            finite_series = series[np.isfinite(series)]
            min_value = float(finite_series.min()) if len(finite_series) > 0 else None
            max_value = float(finite_series.max()) if len(finite_series) > 0 else None
        else:
            non_finite_count = 0
            min_value = None
            max_value = None
        
        trace_data[standard_key] = {
            "stage": stage,
            "source": source_key,
            "present": True,
            "dtype": str(series.dtype),
            "sample_values": sample_values,
            "non_null_count": int(non_null_count),
            "total_rows": int(len(df)),
            "non_finite_count": int(non_finite_count),
            "min_value": min_value,
            "max_value": max_value
        }
    
    return trace_data


def collect_unit_fail_trace(
    df: pd.DataFrame,
    source_key: str,
    stage: str,
    target_keys: List[str] = ['NECK_WIDTH_M', 'NECK_DEPTH_M', 'UNDERBUST_CIRC_M', 'CHEST_CIRC_M_REF']
) -> Dict[str, Dict[str, Any]]:
    """
    Collect trace data for unit-fail keys at a specific processing stage.
    
    Args:
        df: DataFrame at current stage
        source_key: Source identifier
        stage: Stage name (e.g., 'after_extraction_before_preprocess', 'after_preprocess', 'after_unit_conversion')
        target_keys: List of standard keys to trace
    
    Returns:
        Dictionary mapping standard_key -> trace_info
    """
    trace_data = {}
    
    for standard_key in target_keys:
        if standard_key not in df.columns:
            trace_data[standard_key] = {
                "stage": stage,
                "source": source_key,
                "present": False,
                "dtype": None,
                "sample_values": [],
                "non_null_count": 0,
                "total_rows": len(df),
                "non_finite_count": 0,
                "min": None,
                "max": None
            }
            continue
        
        col = df[standard_key]
        dtype = str(col.dtype)
        non_null_count = col.notna().sum()
        total_rows = len(df)
        
        # Collect sample values (prioritize non-finite/invalid values)
        sample_values = []
        values = col.values
        
        # First, collect non-finite values (inf, -inf, NaN)
        non_finite_mask = ~np.isfinite(values)
        non_finite_count = non_finite_mask.sum()
        non_finite_values = values[non_finite_mask]
        
        # Collect non-finite samples (up to 10)
        for val in non_finite_values[:10]:
            if len(sample_values) >= 20:
                break
            if pd.notna(val):  # inf/-inf (not NaN)
                sample_values.append(str(val))
            else:  # NaN
                sample_values.append("NaN")
        
        # Then collect finite values
        finite_mask = np.isfinite(values) & pd.notna(values)
        finite_values = values[finite_mask]
        
        # Add finite samples (up to remaining slots)
        remaining = 20 - len(sample_values)
        for val in finite_values[:remaining]:
            sample_values.append(str(val))
        
        # Calculate min/max for finite values only
        min_val = None
        max_val = None
        if len(finite_values) > 0:
            min_val = float(np.min(finite_values))
            max_val = float(np.max(finite_values))
        
        trace_data[standard_key] = {
            "stage": stage,
            "source": source_key,
            "present": True,
            "dtype": dtype,
            "sample_values": sample_values[:20],
            "non_null_count": int(non_null_count),
            "total_rows": int(total_rows),
            "non_finite_count": int(non_finite_count),
            "min": min_val,
            "max": max_val
        }
    
    return trace_data


def emit_unit_fail_trace(
    all_traces: Dict[str, List[Dict[str, Dict[str, Any]]]],
    output_path: Path
):
    """
    Emit unit-fail trace to markdown file (facts-only).
    
    Args:
        all_traces: Dictionary mapping source_key -> list of trace_data dicts
        output_path: Path to output markdown file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# curated_v0 Unit Fail Trace (facts-only)\n\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Target keys: NECK_WIDTH_M, NECK_DEPTH_M, UNDERBUST_CIRC_M, CHEST_CIRC_M_REF\n\n")
        
        for source_key in ['7th', '8th_direct', '8th_3d']:
            if source_key not in all_traces or not all_traces[source_key]:
                continue
            
            f.write(f"## {source_key}\n\n")
            
            # Group traces by standard_key
            key_traces = defaultdict(list)
            for trace_dict in all_traces[source_key]:
                for standard_key, trace_info in trace_dict.items():
                    key_traces[standard_key].append(trace_info)
            
            for standard_key in ['NECK_WIDTH_M', 'NECK_DEPTH_M', 'UNDERBUST_CIRC_M', 'CHEST_CIRC_M_REF']:
                if standard_key not in key_traces:
                    continue
                
                f.write(f"### {standard_key}\n\n")
                
                traces = key_traces[standard_key]
                # Sort by stage order
                stage_order = {'after_extraction_before_preprocess': 0, 'after_preprocess': 1, 'after_unit_conversion': 2}
                traces.sort(key=lambda x: stage_order.get(x.get('stage', ''), 999))
                
                for trace in traces:
                    stage = trace.get('stage', 'unknown')
                    f.write(f"#### {stage}\n\n")
                    
                    if not trace.get('present', False):
                        f.write("- present: false\n\n")
                        continue
                    
                    f.write(f"- dtype: {trace.get('dtype', 'unknown')}\n")
                    f.write(f"- non_null_count: {trace.get('non_null_count', 0)}\n")
                    f.write(f"- total_rows: {trace.get('total_rows', 0)}\n")
                    f.write(f"- non_finite_count: {trace.get('non_finite_count', 0)}\n")
                    
                    min_val = trace.get('min')
                    max_val = trace.get('max')
                    if min_val is not None and max_val is not None:
                        f.write(f"- min: {min_val}\n")
                        f.write(f"- max: {max_val}\n")
                    
                    sample_values = trace.get('sample_values', [])
                    if sample_values:
                        f.write(f"- sample_values (first 20, non-finite prioritized):\n")
                        for i, val in enumerate(sample_values[:20], 1):
                            f.write(f"  {i}. {val}\n")
                    else:
                        f.write("- sample_values: []\n")
                    
                    f.write("\n")
            
            f.write("\n")


def emit_arm_knee_trace(
    all_traces: Dict[str, List[Dict[str, Dict[str, Any]]]],
    output_path: Path
):
    """
    Emit ARM_LEN_M and KNEE_HEIGHT_M trace to markdown file (facts-only).
    
    Args:
        all_traces: Dictionary mapping source_key -> list of trace_data dicts
        output_path: Path to output markdown file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# ARM_LEN_M and KNEE_HEIGHT_M Trace Diagnostic (facts-only)\n\n")
        f.write("This document traces values for ARM_LEN_M and KNEE_HEIGHT_M through processing stages.\n\n")
        
        for source_key in ['8th_direct', '8th_3d']:
            if source_key not in all_traces:
                continue
            
            f.write(f"## {source_key}\n\n")
            
            source_traces = all_traces[source_key]
            
            for standard_key in ['ARM_LEN_M', 'KNEE_HEIGHT_M']:
                f.write(f"### {standard_key}\n\n")
                
                # Find traces for this key
                key_traces = []
                for trace_dict in source_traces:
                    if standard_key in trace_dict:
                        key_traces.append(trace_dict[standard_key])
                
                if not key_traces:
                    f.write("No trace data available.\n\n")
                    continue
                
                # Write trace for each stage
                for trace in key_traces:
                    stage = trace.get('stage', 'unknown')
                    f.write(f"#### {stage}\n\n")
                    
                    if not trace.get('present', False):
                        f.write("- Column not present in DataFrame\n\n")
                        continue
                    
                    f.write(f"- **dtype**: {trace.get('dtype', 'unknown')}\n")
                    f.write(f"- **non_null_count**: {trace.get('non_null_count', 0)} / {trace.get('total_rows', 0)}\n")
                    f.write(f"- **non_finite_count**: {trace.get('non_finite_count', 0)}\n")
                    
                    min_val = trace.get('min_value')
                    max_val = trace.get('max_value')
                    if min_val is not None and max_val is not None:
                        f.write(f"- **min_value**: {min_val}\n")
                        f.write(f"- **max_value**: {max_val}\n")
                    
                    sample_values = trace.get('sample_values', [])
                    if sample_values:
                        f.write(f"- **sample_values** (first {len(sample_values)} non-null):\n")
                        for i, val in enumerate(sample_values[:20], 1):
                            f.write(f"  {i}. {val}\n")
                    else:
                        f.write("- **sample_values**: (no non-null values)\n")
                    
                    f.write("\n")
    
    print(f"Saved ARM/KNEE trace: {output_path}")


def build_curated_v0(
    mapping_path: Path,
    output_path: Path,
    output_format: str = "parquet",
    dry_run: bool = False,
    max_rows: Optional[int] = None,
    warnings_output_path: Optional[Path] = None,
    quality_summary_path: Optional[Path] = None,
    header_candidates_path: Optional[Path] = None,
    arm_knee_trace_path: Optional[Path] = None,
    unit_fail_trace_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Build curated_v0 dataset.
    
    Args:
        mapping_path: Path to sizekorea column mapping (v2 by default)
        output_path: Output file path
        output_format: "parquet" or "csv"
        dry_run: If True, only check headers/mapping, don't create file
        max_rows: Limit number of rows processed (for testing)
        warnings_output_path: Path to save warnings JSONL (optional)
    
    Returns:
        Dictionary with statistics
    """
    warnings = []
    
    # Load mapping
    mapping = load_mapping_v1(mapping_path)
    
    # Process each source
    all_dfs = []
    all_source_quality = {}  # source_key -> {standard_key -> quality_metrics}
    all_duplicate_headers = {}  # source_key -> {base_header -> [column_info]}
    all_header_candidates = {}  # source_key -> {standard_key -> [candidate_info]}
    all_arm_knee_traces = {}  # source_key -> [list of trace_data dicts]
    all_unit_fail_traces = {}  # source_key -> [list of trace_data dicts]
    stats = {
        "sources_processed": [],
        "total_rows": 0,
        "columns_created": [],
        "warnings_count": 0
    }
    
    for source_key, file_path_str in SOURCE_FILES.items():
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            warnings.append({
                "source": source_key,
                "file": str(file_path),
                "column": "all",
                "reason": "file_not_found",
                "row_index": None,
                "original_value": None,
                "details": f"Source file not found: {file_path}"
            })
            continue
        
        print(f"Processing {source_key}: {file_path}")
        
        # For 7th, prefer XLSX over CSV
        is_xlsx = False
        if source_key == '7th':
            xlsx_path = file_path.parent / "7th_data.xlsx"
            if xlsx_path.exists():
                file_path = xlsx_path
                is_xlsx = True
                print(f"  Using XLSX: {file_path}")
            else:
                print(f"  Warning: XLSX not found, using CSV fallback: {file_path}")
        
        # Find header rows (primary, code, and secondary)
        # Primary: "표준 측정항목 명" anchor row (typically row 4 for 7th)
        # Code: "표준 측정항목 코드" row (typically row 5 for 7th, primary_row + 1)
        # Secondary: Row with "성별"/"HUMAN_ID" tokens near primary (typically row 6 for 7th)
        primary_row, code_row, secondary_row = find_header_rows(file_path, mapping, is_xlsx=is_xlsx, source_key=source_key)
        print(f"  Detected primary header row: {primary_row}")
        if code_row is not None:
            print(f"  Detected code row: {code_row}")
        if secondary_row is not None:
            print(f"  Detected secondary header row: {secondary_row}")
        
        # Calculate data start row: max of all header rows + 1
        # This ensures header/code/meta rows are excluded from data
        header_rows_list = [primary_row]
        if code_row is not None:
            header_rows_list.append(code_row)
        if secondary_row is not None:
            header_rows_list.append(secondary_row)
        data_start_row = max(header_rows_list) + 1
        print(f"  Data start row (after header cutoff): {data_start_row}")
        
        # Load raw file
        df_raw = load_raw_file(file_path, primary_row, secondary_row, source_key, is_xlsx=is_xlsx)
        
        # Drop header/code/meta rows from DataFrame
        # After load_raw_file with header=primary_row, DataFrame index starts from 0
        # Original file row (primary_row + 1) becomes DataFrame index 0
        # Original file row (code_row) becomes DataFrame index (code_row - primary_row - 1) if code_row > primary_row
        # Original file row (secondary_row) becomes DataFrame index (secondary_row - primary_row - 1) if secondary_row > primary_row
        # We need to drop rows before data_start_row in original file coordinates
        # In DataFrame coordinates: drop rows with index < (data_start_row - primary_row - 1)
        if len(df_raw) > 0:
            df_start_idx = data_start_row - primary_row - 1
            if df_start_idx > 0:
                df_raw = df_raw.iloc[df_start_idx:].copy().reset_index(drop=True)
                print(f"  Dropped {df_start_idx} header/code/meta rows, remaining: {len(df_raw)} rows")
        
        # Load secondary DataFrame if secondary header exists
        df_secondary = None
        if secondary_row is not None:
            try:
                if is_xlsx:
                    df_secondary = pd.read_excel(file_path, header=secondary_row, engine='openpyxl')
                else:
                    encodings = ['utf-8-sig', 'cp949', 'utf-8']
                    for enc in encodings:
                        try:
                            df_secondary = pd.read_csv(file_path, encoding=enc, header=secondary_row, low_memory=False)
                            break
                        except (UnicodeDecodeError, Exception):
                            continue
                
                if df_secondary is not None and len(df_secondary) > 0:
                    # Drop header/code/meta rows from secondary DataFrame as well
                    # After load with header=secondary_row, DataFrame index starts from 0
                    # Original file row (secondary_row + 1) becomes DataFrame index 0
                    # We need to drop rows before data_start_row in original file coordinates
                    # In DataFrame coordinates: drop rows with index < (data_start_row - secondary_row - 1)
                    sec_df_start_idx = data_start_row - secondary_row - 1
                    if sec_df_start_idx > 0:
                        df_secondary = df_secondary.iloc[sec_df_start_idx:].copy().reset_index(drop=True)
                
                # Ensure HUMAN_ID/SEX columns are string in secondary
                if df_secondary is not None:
                    for col in df_secondary.columns:
                        col_str = str(col).strip()
                        if 'ID' in col_str or 'HUMAN_ID' in col_str or '성별' in col_str or 'SEX' in col_str:
                            df_secondary[col] = df_secondary[col].astype(str).str.strip()
                            df_secondary[col] = df_secondary[col].str.replace(r'\.0$', '', regex=True)
            except Exception:
                df_secondary = None
        
        if df_raw.empty:
            warnings.append({
                "source": source_key,
                "file": str(file_path),
                "column": "all",
                "reason": "file_load_failed",
                "row_index": None,
                "original_value": None,
                "details": "Failed to load file"
            })
            continue
        
        # Limit rows if specified
        if max_rows and len(df_raw) > max_rows:
            df_raw = df_raw.head(max_rows)
            print(f"  Limited to {max_rows} rows")
        
        print(f"  Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
        
        # Extract and standardize columns
        # Collect trace data if requested (for 8th_direct/8th_3d only)
        trace_data = {}
        if arm_knee_trace_path is not None and source_key in ['8th_direct', '8th_3d']:
            df_extracted = extract_columns_from_source(df_raw, df_secondary, source_key, mapping, warnings, 
                                                       collect_trace=True, trace_data=trace_data)
            # Store traces collected during extraction
            if 'traces' in trace_data:
                if source_key not in all_arm_knee_traces:
                    all_arm_knee_traces[source_key] = []
                all_arm_knee_traces[source_key].extend(trace_data['traces'])
                # Also add trace after preprocessing (df_extracted is already preprocessed)
                trace_after_preprocess = collect_arm_knee_trace(df_extracted, source_key, 'after_preprocess')
                all_arm_knee_traces[source_key].append(trace_after_preprocess)
        else:
            df_extracted = extract_columns_from_source(df_raw, df_secondary, source_key, mapping, warnings)
        print(f"  Extracted {len(df_extracted.columns)} standard columns")
        
        # Collect unit-fail trace after extraction (before preprocessing)
        if unit_fail_trace_path is not None:
            if source_key not in all_unit_fail_traces:
                all_unit_fail_traces[source_key] = []
            trace_after_extraction = collect_unit_fail_trace(df_extracted, source_key, 'after_extraction_before_preprocess')
            all_unit_fail_traces[source_key].append(trace_after_extraction)
        
        # Sample units
        unit_map = sample_units(df_extracted, sample_size=min(100, len(df_extracted)))
        print(f"  Detected units: {len(unit_map)} columns")
        
        # Collect unit-fail trace after preprocessing
        if unit_fail_trace_path is not None:
            trace_after_preprocess = collect_unit_fail_trace(df_extracted, source_key, 'after_preprocess')
            all_unit_fail_traces[source_key].append(trace_after_preprocess)
        
        # Apply unit canonicalization
        df_canonical = apply_unit_canonicalization(df_extracted, unit_map, warnings, source_key=source_key)
        
        # Collect trace after unit conversion (for 8th_direct/8th_3d only)
        if arm_knee_trace_path is not None and source_key in ['8th_direct', '8th_3d']:
            trace_after_unit = collect_arm_knee_trace(df_canonical, source_key, 'after_unit_conversion')
            all_arm_knee_traces[source_key].append(trace_after_unit)
        
        # Collect unit-fail trace after unit conversion
        if unit_fail_trace_path is not None:
            trace_after_unit = collect_unit_fail_trace(df_canonical, source_key, 'after_unit_conversion')
            all_unit_fail_traces[source_key].append(trace_after_unit)
        
        # Handle missing values
        df_final = handle_missing_values(df_canonical, source_key, warnings)
        
        # Apply outlier removal (or record warning)
        df_final = apply_outlier_removal(df_final, warnings)
        
        # Add source column
        df_final['_source'] = source_key
        
        # Calculate quality metrics if quality summary is requested
        if quality_summary_path is not None:
            source_quality = calculate_source_quality(df_final, source_key, mapping)
            all_source_quality[source_key] = source_quality
            
            # Detect duplicate headers in raw DataFrame (before extraction)
            duplicate_headers = detect_duplicate_headers(df_raw, source_key)
            if duplicate_headers:
                all_duplicate_headers[source_key] = duplicate_headers
        
        # Find header candidates if requested (for 8th_direct/8th_3d only)
        if header_candidates_path is not None and source_key in ['8th_direct', '8th_3d']:
            target_keys = ['ARM_LEN_M', 'KNEE_HEIGHT_M']
            source_candidates = find_header_candidates(df_raw, source_key, target_keys, primary_row)
            if source_candidates:
                all_header_candidates[source_key] = source_candidates
        
        all_dfs.append(df_final)
        stats["sources_processed"].append(source_key)
        stats["total_rows"] += len(df_final)
        stats["columns_created"] = list(df_final.columns)
    
    if dry_run:
        print("\n=== DRY RUN ===")
        print(f"Would create {len(all_dfs)} source DataFrames")
        print(f"Total rows: {stats['total_rows']}")
        print(f"Columns: {len(stats['columns_created'])}")
        print(f"Warnings: {len(warnings)}")
        return stats
    
    # Concatenate all sources
    if not all_dfs:
        warnings.append({
            "source": "system",
            "file": "build_curated_v0.py",
            "column": "all",
            "reason": "no_data_processed",
            "row_index": None,
            "original_value": None,
            "details": "No data was successfully processed from any source"
        })
        return stats
    
    df_combined = pd.concat(all_dfs, ignore_index=True)
    
    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure HUMAN_ID is string before saving
    if 'HUMAN_ID' in df_combined.columns:
        df_combined['HUMAN_ID'] = df_combined['HUMAN_ID'].astype(str)
    
    # Force WEIGHT_KG to numeric before parquet write to avoid pyarrow conversion failure
    # when mixed string/float values exist
    if 'WEIGHT_KG' in df_combined.columns:
        # Count NaN before conversion
        nan_before = df_combined['WEIGHT_KG'].isna().sum()
        
        # Convert to string, remove commas, strip, then convert to numeric
        df_combined['WEIGHT_KG'] = pd.to_numeric(
            df_combined['WEIGHT_KG'].astype(str).str.replace(',', '', regex=False).str.strip(),
            errors='coerce'
        )
        
        # Count NaN after conversion
        nan_after = df_combined['WEIGHT_KG'].isna().sum()
        new_nan_count = nan_after - nan_before
        
        # Record warning if new NaN values were created
        if new_nan_count > 0:
            warnings.append({
                "source": "system",
                "file": "build_curated_v0.py",
                "column": "WEIGHT_KG",
                "reason": "numeric_parsing_failed",
                "row_index": None,
                "original_value": None,
                "details": f"{new_nan_count} WEIGHT_KG values failed to convert to numeric during parquet write preparation"
            })
    
    # Normalize non-finite values (inf/-inf) to NaN for all numeric columns
    # This prevents pyarrow conversion failures and silent invalid values
    numeric_cols = df_combined.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue  # Skip meta columns
        
        # Check for non-finite values
        non_finite_mask = ~np.isfinite(df_combined[col])
        non_finite_count = non_finite_mask.sum()
        
        if non_finite_count > 0:
            # Replace inf/-inf with NaN
            df_combined.loc[non_finite_mask, col] = np.nan
            
            # Record aggregated warning
            warnings.append({
                "source": "system",
                "file": "build_curated_v0.py",
                "column": col,
                "reason": "unit_conversion_failed",
                "row_index": None,
                "original_value": None,
                "details": f"{non_finite_count} non-finite values (inf/-inf) normalized to NaN before parquet write"
            })
    
    if output_format == "parquet":
        df_combined.to_parquet(output_path, index=False)
    else:
        df_combined.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\nSaved output: {output_path}")
    print(f"  Rows: {len(df_combined)}")
    print(f"  Columns: {len(df_combined.columns)}")
    
    # Save warnings if path specified
    if warnings_output_path:
        warnings_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(warnings_output_path, 'w', encoding='utf-8') as f:
            for w in warnings:
                f.write(json.dumps(w, ensure_ascii=False) + '\n')
        print(f"Saved warnings: {warnings_output_path} ({len(warnings)} entries)")
    
    stats["warnings_count"] = len(warnings)
    
    # Generate quality summary if requested
    if quality_summary_path is not None and all_source_quality:
        generate_quality_summary(all_source_quality, all_duplicate_headers, quality_summary_path)
        print(f"Saved quality summary: {quality_summary_path}")
    
    # Emit header candidates if requested
    if header_candidates_path is not None and all_header_candidates:
        emit_header_candidates(all_header_candidates, header_candidates_path)
    
    # Emit ARM/KNEE trace if requested
    if arm_knee_trace_path is not None and all_arm_knee_traces:
        emit_arm_knee_trace(all_arm_knee_traces, arm_knee_trace_path)
    
    # Emit unit-fail trace if requested
    if unit_fail_trace_path is not None and all_unit_fail_traces:
        emit_unit_fail_trace(all_unit_fail_traces, unit_fail_trace_path)
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Sources processed: {len(stats['sources_processed'])}")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Columns: {len(stats['columns_created'])}")
    print(f"Warnings: {stats['warnings_count']}")
    
    # Warning breakdown
    warning_reasons = {}
    for w in warnings:
        reason = w.get('reason', 'unknown')
        warning_reasons[reason] = warning_reasons.get(reason, 0) + 1
    
    print("\nWarning breakdown:")
    for reason, count in sorted(warning_reasons.items()):
        print(f"  {reason}: {count}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Build curated_v0 dataset from SizeKorea raw data"
    )
    parser.add_argument(
        '--mapping',
        type=str,
        default='data/column_map/sizekorea_v2.json',
        help='Path to sizekorea column mapping file (default: v2)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/curated_v0/curated_v0.parquet',
        help='Output file path'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['parquet', 'csv'],
        default='parquet',
        help='Output format (default: parquet)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Check headers/mapping only, do not create output file'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        default=None,
        help='Limit number of rows processed (for testing)'
    )
    parser.add_argument(
        '--warnings-output',
        type=str,
        default=None,
        help='Path to save warnings JSONL file (optional)'
    )
    parser.add_argument(
        '--emit-quality-summary',
        type=str,
        default=None,
        help='Path to save quality summary markdown file (optional)'
    )
    parser.add_argument(
        '--emit-header-candidates',
        type=str,
        default=None,
        help='Path to save header candidates diagnostic markdown file (optional, for 8th_direct/8th_3d)'
    )
    parser.add_argument(
        '--emit-arm-knee-trace',
        type=str,
        default=None,
        help='Path to save ARM_LEN_M and KNEE_HEIGHT_M trace diagnostic markdown file (optional, for 8th_direct/8th_3d)'
    )
    parser.add_argument(
        '--emit-unit-fail-trace',
        type=str,
        default=None,
        help='Path to save unit-fail trace diagnostic markdown file (optional, for NECK_WIDTH_M, NECK_DEPTH_M, UNDERBUST_CIRC_M, CHEST_CIRC_M_REF)'
    )
    
    args = parser.parse_args()
    
    mapping_path = Path(args.mapping)
    output_path = Path(args.output)
    warnings_output_path = Path(args.warnings_output) if args.warnings_output else None
    quality_summary_path = Path(args.emit_quality_summary) if args.emit_quality_summary else None
    header_candidates_path = Path(args.emit_header_candidates) if args.emit_header_candidates else None
    arm_knee_trace_path = Path(args.emit_arm_knee_trace) if args.emit_arm_knee_trace else None
    unit_fail_trace_path = Path(args.emit_unit_fail_trace) if args.emit_unit_fail_trace else None
    
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {mapping_path}")
        return 1
    
    stats = build_curated_v0(
        mapping_path=mapping_path,
        output_path=output_path,
        output_format=args.format,
        dry_run=args.dry_run,
        max_rows=args.max_rows,
        warnings_output_path=warnings_output_path,
        quality_summary_path=quality_summary_path,
        header_candidates_path=header_candidates_path,
        arm_knee_trace_path=arm_knee_trace_path,
        unit_fail_trace_path=unit_fail_trace_path
    )
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
