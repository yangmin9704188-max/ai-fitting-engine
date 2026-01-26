#!/usr/bin/env python3
"""
Extract case_ids manifest from existing golden_real_data_v0.npz.

Purpose: Round22 – Create SSoT manifest for real-data golden reproducibility.
Output: golden_real_data_v0.case_ids.json (ordered list of case_ids)
"""

import json
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[4]


def extract_case_ids_manifest(npz_path: Path, out_json_path: Path) -> int:
    """
    Extract case_ids from NPZ and save as ordered JSON list.
    
    Returns:
        Number of case_ids extracted
    """
    npz_path = _REPO_ROOT / npz_path if not npz_path.is_absolute() else npz_path
    out_json_path = _REPO_ROOT / out_json_path if not out_json_path.is_absolute() else out_json_path
    
    if not npz_path.exists():
        print(f"ERROR: NPZ file not found: {npz_path}")
        sys.exit(1)
    
    data = np.load(str(npz_path), allow_pickle=True)
    case_ids = data['case_id'].tolist()
    
    # Ensure parent directory exists
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as ordered JSON list (SSoT: set + order)
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(case_ids, f, indent=2, ensure_ascii=False)
    
    print(f"[MANIFEST] Extracted {len(case_ids)} case_ids")
    print(f"[MANIFEST] Saved: {out_json_path}")
    return len(case_ids)


def main():
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Extract case_ids manifest from golden_real_data_v0.npz"
    )
    ap.add_argument(
        "--npz",
        type=str,
        default=str(Path(__file__).parent / "golden_real_data_v0.npz"),
        help="Input NPZ path (default: .../core_measurements_v0/golden_real_data_v0.npz)",
    )
    ap.add_argument(
        "--out_json",
        type=str,
        default=str(Path(__file__).parent / "golden_real_data_v0.case_ids.json"),
        help="Output JSON manifest path (default: .../core_measurements_v0/golden_real_data_v0.case_ids.json)",
    )
    args = ap.parse_args()
    
    n = extract_case_ids_manifest(Path(args.npz), Path(args.out_json))
    print(f"[DONE] {n} case_ids -> {Path(args.out_json).resolve()}")


if __name__ == "__main__":
    main()
