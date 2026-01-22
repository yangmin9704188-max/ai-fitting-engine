#!/usr/bin/env python3
"""
Regenerate processed data in meters (m) with 0.001m quantization.

Purpose: Convert raw data to processed/m_standard/ with meters canonicalization.
This path is separate from existing cm-based processed data to avoid confusion.

Workflow:
- Raw (mm/cm, source unit preserved) -> Ingestion (canonicalize_units_to_m) -> Processed/m_standard (m, 0.001m)
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.ingestion import canonicalize_units_to_m, get_provenance_dict


def process_csv_to_m_standard(
    input_csv: str,
    output_dir: str,
    source_unit: str,
    measurement_columns: dict[str, str],
    warnings: list[str],
):
    """
    Process CSV file: convert measurement columns to meters and save to m_standard/.
    
    Args:
        input_csv: Input CSV file path
        output_dir: Output directory (data/processed/m_standard/)
        source_unit: Source unit ("mm", "cm", or "m")
        measurement_columns: Dict mapping standard column names to CSV column names
            e.g., {"height": "Height", "chest_girth": "Chest_Girth"}
        warnings: List to append warnings (mutated in-place)
    
    Returns:
        Number of rows processed successfully
    """
    df = pd.read_csv(input_csv)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create output dataframe with canonicalized values
    output_data = {}
    n_processed = 0
    
    for std_col, csv_col in measurement_columns.items():
        if csv_col not in df.columns:
            warnings.append(f"COLUMN_MISSING: {csv_col} not found in {input_csv}")
            continue
        
        # Get values
        values = df[csv_col].values
        
        # Canonicalize to meters
        values_m = canonicalize_units_to_m(values, source_unit, warnings)
        
        # Store with standard column name
        output_data[std_col] = values_m
        n_processed = len(df)
    
    # Create output dataframe
    output_df = pd.DataFrame(output_data)
    
    # Add provenance metadata as comment/separate file
    provenance = get_provenance_dict(source_unit)
    provenance_file = output_path / f"{Path(input_csv).stem}_provenance.json"
    import json
    with open(provenance_file, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, ensure_ascii=False)
    
    # Save processed CSV
    output_csv = output_path / f"{Path(input_csv).stem}_m.csv"
    output_df.to_csv(output_csv, index=False)
    
    return n_processed


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate processed data in meters (m) with 0.001m quantization"
    )
    parser.add_argument(
        "--input_csv",
        type=str,
        required=True,
        help="Input CSV file path (raw data)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/processed/m_standard",
        help="Output directory (default: data/processed/m_standard)"
    )
    parser.add_argument(
        "--source_unit",
        type=str,
        required=True,
        choices=["mm", "cm", "m"],
        help="Source unit of input data (mm, cm, or m) - MUST be explicitly specified"
    )
    parser.add_argument(
        "--columns",
        type=str,
        nargs="+",
        default=["height:Height", "chest_girth:Chest_Girth", "waist_girth:Waist_Girth", "hip_girth:Hip_Girth"],
        help="Column mappings in format 'std_name:csv_name' (default: height:Height, chest_girth:Chest_Girth, ...)"
    )
    
    args = parser.parse_args()
    
    # Parse column mappings
    measurement_columns = {}
    for col_map in args.columns:
        if ":" not in col_map:
            warnings = []
            warnings.append(f"INVALID_COLUMN_MAPPING: {col_map} (expected format: 'std_name:csv_name')")
            continue
        std_name, csv_name = col_map.split(":", 1)
        measurement_columns[std_name] = csv_name
    
    warnings = []
    
    print(f"Processing: {args.input_csv}")
    print(f"Source unit: {args.source_unit}")
    print(f"Output directory: {args.output_dir}")
    print(f"Column mappings: {measurement_columns}")
    print("=" * 80)
    
    n_processed = process_csv_to_m_standard(
        args.input_csv,
        args.output_dir,
        args.source_unit,
        measurement_columns,
        warnings,
    )
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    
    print(f"\nProcessed {n_processed} rows")
    print(f"Output saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
