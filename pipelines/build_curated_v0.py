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
import sys

# Import canonicalization function
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.ingestion import canonicalize_units_to_m


# Source file mapping
SOURCE_FILES = {
    "7th": "data/raw/sizekorea_raw/7th_data.csv",
    "8th_direct": "data/raw/sizekorea_raw/8th_data_direct.csv",
    "8th_3d": "data/raw/sizekorea_raw/8th_data_3d.csv",
}

# Header row for each source (from columns_by_file.json)
HEADER_ROWS = {
    "7th": 6,
    "8th_direct": 6,
    "8th_3d": 6,
}


def find_header_row(file_path: Path, mapping: Dict[str, Any], encoding: str = 'utf-8-sig', max_check: int = 20) -> int:
    """
    Find header row by matching first column value with standard measurement terms.
    
    Looks for rows where first column (after strip) matches ko_term from mapping.
    Returns row index or falls back to default HEADER_ROWS.
    """
    # Collect all ko_terms from mapping
    ko_terms = set()
    for key_info in mapping['keys']:
        ko_term = key_info.get('ko_term', '')
        if ko_term and ko_term != 'HUMAN_ID':
            ko_terms.add(ko_term.strip())
            # Also check with leading space (as per user requirement)
            ko_terms.add(' ' + ko_term.strip())
    
    encodings = [encoding, 'cp949', 'utf-8']
    
    for enc in encodings:
        try:
            # Read first max_check rows without header
            df_sample = pd.read_csv(file_path, encoding=enc, header=None, nrows=max_check, low_memory=False)
            
            # Check each row's first column
            for i in range(len(df_sample)):
                first_val = df_sample.iloc[i, 0]
                if pd.notna(first_val):
                    first_val_str = str(first_val).strip()
                    # Check exact match with ko_terms
                    if first_val_str in ko_terms:
                        return i
                    # Also check without leading space
                    if first_val_str.lstrip() in ko_terms:
                        return i
            
            # If no match found, return default based on file name
            if '7th' in str(file_path):
                return HEADER_ROWS.get('7th', 6)
            elif '8th_direct' in str(file_path):
                return HEADER_ROWS.get('8th_direct', 6)
            elif '8th_3d' in str(file_path):
                return HEADER_ROWS.get('8th_3d', 6)
            return 6  # Default fallback
            
        except UnicodeDecodeError:
            continue
        except Exception:
            if enc == encodings[-1]:
                # Last encoding failed, return default
                return HEADER_ROWS.get('7th', 6)
            continue
    
    return 6  # Final fallback


def load_mapping_v1(mapping_path: Path) -> Dict[str, Any]:
    """Load sizekorea column mapping (v1 or v2)."""
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_raw_file(file_path: Path, header_row: int, encoding: str = 'utf-8-sig') -> pd.DataFrame:
    """
    Load raw CSV file with specified header row.
    
    Tries multiple encodings if the first fails.
    """
    encodings = [encoding, 'cp949', 'utf-8']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, header=header_row, low_memory=False)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            if enc == encodings[-1]:
                # Last encoding failed, return empty DataFrame
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
        
        # 8th_direct: Replace 9999 with NaN
        if source_key == '8th_direct':
            if pd.api.types.is_numeric_dtype(result_df[col]):
                sentinel_mask = result_df[col] == 9999
                sentinel_count = sentinel_mask.sum()
                if sentinel_count > 0:
                    result_df.loc[sentinel_mask, col] = np.nan
                    warnings.append({
                        "source": source_key,
                        "file": SOURCE_FILES[source_key],
                        "column": col,
                        "reason": "SENTINEL_MISSING",
                        "row_index": None,
                        "original_value": "9999",
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
                        "original_value": "",
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
    source_key: str,
    mapping: Dict[str, Any],
    warnings: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Extract and standardize columns from raw DataFrame based on mapping.
    
    Returns DataFrame with standard_key columns (45 keys).
    Missing columns are filled with NaN.
    """
    result_data = {}
    num_rows = len(df)
    
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
        
        if raw_column not in df.columns:
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
        result_data[standard_key] = df[raw_column].values
    
    # Preprocess numeric columns (comma removal, sentinel replacement)
    df_preprocessed = preprocess_numeric_columns(pd.DataFrame(result_data, index=df.index), source_key, warnings)
    
    # Normalize sex values
    if 'SEX' in df_preprocessed.columns:
        df_preprocessed = normalize_sex(df_preprocessed, source_key, warnings)
    
    # Update result_data with preprocessed values
    for col in df_preprocessed.columns:
        if col in result_data:
            result_data[col] = df_preprocessed[col].values
    
    # Create DataFrame with all standard keys
    result_df = pd.DataFrame(result_data, index=df.index)
    
    # Ensure all 45 standard keys are present (fill missing with NaN)
    all_keys = [k['standard_key'] for k in mapping['keys']]
    for key in all_keys:
        if key not in result_df.columns:
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
    warnings: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Apply unit canonicalization to DataFrame.
    
    Converts all measurement columns to meters (m) with 0.001m quantization.
    """
    result_df = df.copy()
    warning_list = []  # For canonicalize_units_to_m
    
    for col in df.columns:
        if col in ['SEX', 'AGE', 'HUMAN_ID']:
            continue  # Meta columns, no conversion
        
        if col == 'WEIGHT_KG':
            # Weight is already in kg, no conversion
            continue
        
        if col not in unit_map:
            # Unit not determined, set to NaN
            result_df[col] = np.nan
            warnings.append({
                "source": "unknown",
                "file": "unknown",
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
            warnings.append({
                "source": "unknown",
                "file": "unknown",
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
        for w in warning_list:
            if "UNIT_FAIL" in w or "PROVENANCE" in w:
                warnings.append({
                    "source": "unknown",
                    "file": "unknown",
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
    
    No exceptions raised (NaN + warnings policy).
    """
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            warnings.append({
                "source": source_key,
                "file": SOURCE_FILES[source_key],
                "column": col,
                "reason": "value_missing",
                "row_index": None,
                "original_value": None,
                "details": f"{missing_count} missing values in column"
            })
    
    return df


def build_curated_v0(
    mapping_path: Path,
    output_path: Path,
    output_format: str = "parquet",
    dry_run: bool = False,
    max_rows: Optional[int] = None,
    warnings_output_path: Optional[Path] = None
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
        
        # Find header row dynamically
        header_row = find_header_row(file_path, mapping)
        print(f"  Detected header row: {header_row}")
        
        # Load raw file
        df_raw = load_raw_file(file_path, header_row)
        
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
        df_extracted = extract_columns_from_source(df_raw, source_key, mapping, warnings)
        print(f"  Extracted {len(df_extracted.columns)} standard columns")
        
        # Sample units
        unit_map = sample_units(df_extracted, sample_size=min(100, len(df_extracted)))
        print(f"  Detected units: {len(unit_map)} columns")
        
        # Apply unit canonicalization
        df_canonical = apply_unit_canonicalization(df_extracted, unit_map, warnings)
        
        # Handle missing values
        df_final = handle_missing_values(df_canonical, source_key, warnings)
        
        # Apply outlier removal (or record warning)
        df_final = apply_outlier_removal(df_final, warnings)
        
        # Add source column
        df_final['_source'] = source_key
        
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
    
    args = parser.parse_args()
    
    mapping_path = Path(args.mapping)
    output_path = Path(args.output)
    warnings_output_path = Path(args.warnings_output) if args.warnings_output else None
    
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {mapping_path}")
        return 1
    
    stats = build_curated_v0(
        mapping_path=mapping_path,
        output_path=output_path,
        output_format=args.format,
        dry_run=args.dry_run,
        max_rows=args.max_rows,
        warnings_output_path=warnings_output_path
    )
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
