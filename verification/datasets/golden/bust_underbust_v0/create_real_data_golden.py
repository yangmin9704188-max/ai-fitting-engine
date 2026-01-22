#!/usr/bin/env python3
"""
Create bust/underbust Golden NPZ from real processed data.

Purpose: Generate Golden NPZ from real processed(m_standard) data with provenance metadata.
This is separate from S0 synthetic cases and uses actual measurement data.

Workflow:
- Processed(m_standard) -> Extract measurement data -> Generate Golden NPZ with meta_unit="m" + provenance
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data.ingestion import get_provenance_dict


def load_processed_m_standard(csv_path: str) -> pd.DataFrame:
    """
    Load processed m_standard CSV file.
    
    Args:
        csv_path: Path to processed CSV (m_standard)
    
    Returns:
        DataFrame with measurement columns in meters
    """
    df = pd.read_csv(csv_path)
    return df


def create_golden_npz_from_processed(
    processed_csv: str,
    output_npz: str,
    source_unit: str,
    n_samples: int = None,
    warnings: list[str] = None,
):
    """
    Create Golden NPZ from processed(m_standard) CSV.
    
    Note: This is a placeholder that generates synthetic verts from measurement data.
    In a full implementation, this would load actual 3D mesh/verts from a mesh generation pipeline.
    
    Args:
        processed_csv: Path to processed CSV (m_standard)
        output_npz: Output NPZ file path
        source_unit: Source unit used in ingestion (for provenance)
        n_samples: Number of samples to include (None = all)
        warnings: List to append warnings (mutated in-place)
    
    Returns:
        Number of cases included
    """
    if warnings is None:
        warnings = []
    
    df = load_processed_m_standard(processed_csv)
    
    # Limit samples if specified
    if n_samples is not None and n_samples < len(df):
        df = df.sample(n=n_samples, random_state=42)
    
    # For now, generate placeholder verts from measurement data
    # In full implementation, this would load actual 3D meshes
    cases = []
    case_ids = []
    
    for idx, row in df.iterrows():
        # Placeholder: generate simple box-like verts based on measurements
        # In real implementation, this would load actual mesh data
        height_m = row.get("height", 1.7) if "height" in row else 1.7
        chest_m = row.get("chest_girth", 0.9) if "chest_girth" in row else 0.9
        
        # Generate placeholder verts (box shape)
        n_verts = 100
        verts = np.zeros((n_verts, 3), dtype=np.float32)
        for j in range(n_verts):
            x = (j % 10) / 10.0 * (chest_m / np.pi / 2) - (chest_m / np.pi / 4)
            y = (j // 10) / 10.0 * height_m
            z = ((j % 5) / 5.0) * (chest_m / np.pi / 2) - (chest_m / np.pi / 4)
            verts[j] = [x, y, z]
        
        cases.append(verts)
        case_ids.append(f"real_{idx:04d}")
    
    # Convert to batched format: (N, V, 3)
    if len(cases) == 0:
        warnings.append("EMPTY_CASES: No valid cases generated")
        return 0
    
    max_verts = max(v.shape[0] for v in cases)
    verts_batched = np.zeros((len(cases), max_verts, 3), dtype=np.float32)
    for i, v in enumerate(cases):
        verts_batched[i, :v.shape[0], :] = v
    
    # Get provenance
    provenance = get_provenance_dict(source_unit)
    
    # Save as NPZ with meta keys
    output_path = Path(output_npz)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    np.savez(
        str(output_path),
        verts=verts_batched.astype(np.float32),
        case_id=np.array(case_ids, dtype=object),
        meta_unit=np.array("m", dtype=object),
        schema_version=np.array("bust_underbust_v0_real@1", dtype=object),
        ingestion_provenance=np.array(json.dumps(provenance), dtype=object),
    )
    
    return len(cases)


def main():
    parser = argparse.ArgumentParser(
        description="Create bust/underbust Golden NPZ from real processed data"
    )
    parser.add_argument(
        "--processed_csv",
        type=str,
        required=True,
        help="Path to processed CSV (m_standard)"
    )
    parser.add_argument(
        "--output_npz",
        type=str,
        required=True,
        help="Output NPZ file path"
    )
    parser.add_argument(
        "--source_unit",
        type=str,
        required=True,
        choices=["mm", "cm", "m"],
        help="Source unit used in ingestion (for provenance)"
    )
    parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="Number of samples to include (default: all)"
    )
    
    args = parser.parse_args()
    
    warnings = []
    
    print(f"Processing: {args.processed_csv}")
    print(f"Source unit: {args.source_unit}")
    print(f"Output: {args.output_npz}")
    if args.n:
        print(f"Sample limit: {args.n}")
    print("=" * 80)
    
    n_cases = create_golden_npz_from_processed(
        args.processed_csv,
        args.output_npz,
        args.source_unit,
        n_samples=args.n,
        warnings=warnings,
    )
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    
    print(f"\nGenerated {n_cases} cases")
    print(f"Saved to: {args.output_npz}")


if __name__ == "__main__":
    main()
