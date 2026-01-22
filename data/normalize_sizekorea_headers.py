#!/usr/bin/env python3
"""
Normalize SizeKorea raw CSV headers from Korean to English standard keys.

Purpose: Convert Korean column names to English standard keys for integration/curation.
This is a prerequisite step before raw data integration (7th/8th join/union) and curated_v0 generation.

Workflow:
- Raw CSV (Korean headers) -> Column mapping -> Normalized CSV (English headers) -> raw_normalized_v0/
"""

import argparse
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Set


def load_column_mapping(mapping_file: str) -> Dict[str, str]:
    """
    Load column mapping from JSON file.
    
    Args:
        mapping_file: Path to mapping JSON file
    
    Returns:
        Dictionary mapping Korean column names to English keys
    """
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
    return mapping_data.get("mapping", {})


def normalize_csv_headers(
    input_csv: str,
    output_csv: str,
    mapping: Dict[str, str],
    header_row: int = 4,
    warnings: List[str] = None,
) -> Dict[str, any]:
    """
    Normalize CSV headers from Korean to English standard keys.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path
        mapping: Dictionary mapping Korean names to English keys
        header_row: Row index to use as header
        warnings: List to append warnings (mutated in-place)
    
    Returns:
        Dictionary with normalization statistics
    """
    if warnings is None:
        warnings = []
    
    # Read CSV with specified header row
    try:
        df = pd.read_csv(input_csv, encoding='utf-8-sig', header=header_row, low_memory=False)
    except Exception as e:
        warnings.append(f"CSV_READ_ERROR: {str(e)}")
        return {"error": str(e)}
    
    original_columns = list(df.columns)
    n_original = len(original_columns)
    
    # Normalize column names
    normalized_columns = []
    mapping_stats = {
        "mapped": 0,
        "unmapped": 0,
        "unmapped_list": []
    }
    
    unmapped_prefix = "ko__"
    unmapped_suffix = "__unmapped"
    
    for col in original_columns:
        col_str = str(col)
        
        # Check if column is mapped
        if col_str in mapping:
            normalized_columns.append(mapping[col_str])
            mapping_stats["mapped"] += 1
        elif "Unnamed" in col_str:
            # Keep Unnamed columns as-is with prefix
            normalized_columns.append(f"{unmapped_prefix}{col_str}")
            mapping_stats["unmapped"] += 1
            mapping_stats["unmapped_list"].append(col_str)
        else:
            # Unmapped column: add prefix/suffix
            normalized_columns.append(f"{unmapped_prefix}{col_str}{unmapped_suffix}")
            mapping_stats["unmapped"] += 1
            mapping_stats["unmapped_list"].append(col_str)
    
    # Rename columns
    df.columns = normalized_columns
    
    # Save normalized CSV
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    mapping_stats["n_total"] = n_original
    mapping_stats["mapping_rate"] = mapping_stats["mapped"] / n_original if n_original > 0 else 0.0
    
    return mapping_stats


def main():
    parser = argparse.ArgumentParser(
        description="Normalize SizeKorea raw CSV headers from Korean to English standard keys"
    )
    parser.add_argument(
        "--input_csv",
        type=str,
        required=True,
        help="Input CSV file path (raw, Korean headers)"
    )
    parser.add_argument(
        "--output_csv",
        type=str,
        required=True,
        help="Output CSV file path (normalized, English headers)"
    )
    parser.add_argument(
        "--mapping_file",
        type=str,
        default="data/column_map/sizekorea_v0.json",
        help="Column mapping JSON file (default: data/column_map/sizekorea_v0.json)"
    )
    parser.add_argument(
        "--header_row",
        type=int,
        default=4,
        help="Row index to use as header (default: 4)"
    )
    
    args = parser.parse_args()
    
    warnings = []
    
    print(f"Normalizing: {args.input_csv}")
    print(f"Mapping file: {args.mapping_file}")
    print(f"Header row: {args.header_row}")
    print(f"Output: {args.output_csv}")
    print("=" * 80)
    
    # Load mapping
    try:
        mapping = load_column_mapping(args.mapping_file)
        print(f"Loaded {len(mapping)} column mappings")
    except Exception as e:
        warnings.append(f"MAPPING_LOAD_ERROR: {str(e)}")
        print(f"Error loading mapping: {e}")
        return
    
    # Normalize
    stats = normalize_csv_headers(
        args.input_csv,
        args.output_csv,
        mapping,
        header_row=args.header_row,
        warnings=warnings,
    )
    
    if "error" in stats:
        print(f"\nError: {stats['error']}")
        return
    
    # Print statistics
    print("\nNormalization Statistics:")
    print(f"  Total columns: {stats['n_total']}")
    print(f"  Mapped: {stats['mapped']} ({stats['mapping_rate']*100:.1f}%)")
    print(f"  Unmapped: {stats['unmapped']}")
    
    if stats['unmapped_list']:
        print(f"\n  Unmapped columns (first 20):")
        for col in stats['unmapped_list'][:20]:
            print(f"    - {col}")
        if len(stats['unmapped_list']) > 20:
            print(f"    ... and {len(stats['unmapped_list']) - 20} more")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    
    print(f"\nSaved normalized CSV to: {args.output_csv}")


if __name__ == "__main__":
    main()
