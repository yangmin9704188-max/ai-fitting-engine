#!/usr/bin/env python3
"""
BUST/UNDERBUST v0 Facts-Only Runner

Purpose: Record factual statistics for measure_bust_v0 and measure_underbust_v0.
No PASS/FAIL thresholds - factual recording only (Validation Layer principle).
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.measurements.bust_underbust_v0 import (
    measure_bust_v0,
    measure_underbust_v0,
    BustUnderbustResult
)


def get_git_sha() -> Optional[str]:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_npz_data(npz_path: str) -> tuple[List[np.ndarray], List[str], List[str]]:
    """
    Load verts from NPZ file.
    Supports multiple formats:
    - verts: (N, V, 3) float array
    - verts: (V, 3) float array (single case)
    - verts: (N,) object array, each element (V, 3) float array
    Returns: (list of verts arrays, list of case_ids, list of warnings)
    """
    warnings = []
    verts_list = []
    case_ids = []
    
    try:
        data = np.load(npz_path, allow_pickle=True)
    except Exception as e:
        warnings.append(f"NPZ_LOAD_FAILED: {str(e)}")
        return verts_list, case_ids, warnings
    
    # Check if this is a Golden dataset (has meta_unit or schema_version)
    is_golden = "meta_unit" in data or "schema_version" in data
    
    # Golden dataset strict shape check and meta_unit validation
    if is_golden:
        if "meta_unit" not in data:
            warnings.append("GOLDEN_META_MISSING: meta_unit key not found")
            warnings.append("UNIT_FAIL: Golden NPZ missing meta_unit")
        else:
            # Validate meta_unit is "m"
            meta_unit_value = data["meta_unit"]
            if isinstance(meta_unit_value, np.ndarray):
                meta_unit_str = str(meta_unit_value.item()) if meta_unit_value.size > 0 else None
            else:
                meta_unit_str = str(meta_unit_value)
            
            if meta_unit_str != "m":
                warnings.append(f"UNIT_FAIL: Golden NPZ meta_unit='{meta_unit_str}', expected 'm'")
        
        if "schema_version" not in data:
            warnings.append("GOLDEN_META_MISSING: schema_version key not found")
    
    # Try common keys
    if "verts" in data:
        verts = data["verts"]
        
        # Golden dataset: strict shape check (N, V, 3) only
        if is_golden:
            if verts.ndim != 3 or verts.shape[2] != 3:
                warnings.append(f"GOLDEN_SHAPE_VIOLATION: expected (N, V, 3), got {verts.shape}")
                # For Golden, do not attempt conversion - return empty with warnings
                return verts_list, case_ids, warnings
        
        # Handle object array: (N,) dtype=object, each element (V, 3)
        if verts.dtype == object and verts.ndim == 1:
            try:
                for i in range(verts.shape[0]):
                    v = verts[i]
                    if isinstance(v, np.ndarray) and v.ndim == 2 and v.shape[1] == 3:
                        verts_list.append(v.astype(np.float32))
                    else:
                        warnings.append(f"SKIP_INVALID_VERT: index={i}, shape={v.shape if isinstance(v, np.ndarray) else type(v)}")
            except Exception as e:
                warnings.append(f"OBJECT_ARRAY_PARSE_FAILED: {str(e)}")
        
        # Handle batched format: (T, N, 3) -> list of (N, 3)
        elif verts.ndim == 3:
            try:
                verts_list = [verts[i].astype(np.float32) for i in range(verts.shape[0])]
            except Exception as e:
                warnings.append(f"BATCHED_ARRAY_PARSE_FAILED: {str(e)}")
        
        # Handle single case: (V, 3)
        elif verts.ndim == 2:
            try:
                verts_list = [verts.astype(np.float32)]
            except Exception as e:
                warnings.append(f"SINGLE_ARRAY_PARSE_FAILED: {str(e)}")
        
        else:
            warnings.append(f"UNSUPPORTED_VERTS_SHAPE: {verts.shape}, dtype={verts.dtype}")
    
    elif "cases" in data:
        try:
            cases = data["cases"]
            if isinstance(cases, (list, np.ndarray)):
                if isinstance(cases, np.ndarray) and cases.dtype == object:
                    # Object array of arrays
                    for i, case in enumerate(cases):
                        if isinstance(case, np.ndarray) and case.ndim == 2:
                            verts_list.append(case.astype(np.float32))
                        else:
                            warnings.append(f"SKIP_INVALID_CASE: index={i}")
                else:
                    verts_list = [v.astype(np.float32) if isinstance(v, np.ndarray) else v for v in cases]
            else:
                warnings.append(f"UNSUPPORTED_CASES_TYPE: {type(cases)}")
        except Exception as e:
            warnings.append(f"CASES_PARSE_FAILED: {str(e)}")
    
    else:
        # Try to find any array-like data
        keys = list(data.keys())
        if len(keys) == 0:
            warnings.append("NO_DATA_FOUND: NPZ file is empty")
        else:
            warnings.append(f"VERTS_KEY_NOT_FOUND: available keys={keys}")
            # Try to extract from any array-like key
            for k in keys:
                try:
                    arr = data[k]
                    if isinstance(arr, np.ndarray):
                        if arr.dtype == object and arr.ndim == 1:
                            # Object array
                            for i, elem in enumerate(arr):
                                if isinstance(elem, np.ndarray) and elem.ndim == 2 and elem.shape[1] == 3:
                                    verts_list.append(elem.astype(np.float32))
                        elif arr.ndim == 3 and arr.shape[2] == 3:
                            # Batched format
                            verts_list.extend([arr[i].astype(np.float32) for i in range(arr.shape[0])])
                        elif arr.ndim == 2 and arr.shape[1] == 3:
                            # Single case
                            verts_list.append(arr.astype(np.float32))
                except Exception as e:
                    warnings.append(f"KEY_{k}_PARSE_FAILED: {str(e)}")
    
    # Get case_ids if available
    if "case_id" in data:
        try:
            case_id_data = data["case_id"]
            # Handle object array
            if isinstance(case_id_data, np.ndarray) and case_id_data.dtype == object:
                case_ids = [str(cid) for cid in case_id_data]
            elif isinstance(case_id_data, np.ndarray):
                case_ids = [str(cid) for cid in case_id_data]
            elif isinstance(case_id_data, (list, tuple)):
                case_ids = [str(cid) for cid in case_id_data]
            else:
                case_ids = [str(case_id_data)]
        except Exception as e:
            warnings.append(f"CASE_ID_PARSE_FAILED: {str(e)}")
            case_ids = []
    elif "case_ids" in data:
        try:
            case_id_data = data["case_ids"]
            # Handle object array
            if isinstance(case_id_data, np.ndarray) and case_id_data.dtype == object:
                case_ids = [str(cid) for cid in case_id_data]
            elif isinstance(case_id_data, np.ndarray):
                case_ids = [str(cid) for cid in case_id_data]
            elif isinstance(case_id_data, (list, tuple)):
                case_ids = [str(cid) for cid in case_id_data]
            else:
                case_ids = [str(case_id_data)]
        except Exception as e:
            warnings.append(f"CASE_IDS_PARSE_FAILED: {str(e)}")
            case_ids = []
    
    # Generate case_ids if not found or mismatch
    if len(case_ids) != len(verts_list):
        warnings.append(f"CASE_ID_COUNT_MISMATCH: case_ids={len(case_ids)}, verts={len(verts_list)}")
        case_ids = [f"case_{i:04d}" for i in range(len(verts_list))]
    
    return verts_list, case_ids, warnings


def process_sample(
    case_id: str,
    verts: np.ndarray,
) -> Dict[str, Any]:
    """
    Process a single sample for BUST and UNDERBUST measurements.
    Returns dict with results (no exceptions raised).
    """
    result = {
        "case_id": str(case_id),
        "underbust_circ_m": None,
        "bust_circ_m": None,
        "underbust_section_id": None,
        "bust_section_id": None,
        "underbust_method_tag": None,
        "bust_method_tag": None,
        "underbust_warnings": [],
        "bust_warnings": [],
        "underbust_is_nan": False,
        "bust_is_nan": False,
    }
    
    # Measure UNDERBUST
    try:
        underbust_result: BustUnderbustResult = measure_underbust_v0(
            verts=verts,
            bra_size_token=None,
            is_male=None,
            units_metadata=None,
        )
        result["underbust_circ_m"] = float(underbust_result.circumference_m) if np.isfinite(underbust_result.circumference_m) else None
        result["underbust_section_id"] = underbust_result.section_id
        result["underbust_method_tag"] = underbust_result.method_tag
        result["underbust_warnings"] = underbust_result.warnings
        result["underbust_is_nan"] = np.isnan(underbust_result.circumference_m)
    except Exception as e:
        result["underbust_warnings"] = [f"EXEC_FAIL: {str(e)}"]
        result["underbust_is_nan"] = True
    
    # Measure BUST
    try:
        bust_result: BustUnderbustResult = measure_bust_v0(
            verts=verts,
            bra_size_token=None,
            is_male=None,
            units_metadata=None,
        )
        result["bust_circ_m"] = float(bust_result.circumference_m) if np.isfinite(bust_result.circumference_m) else None
        result["bust_section_id"] = bust_result.section_id
        result["bust_method_tag"] = bust_result.method_tag
        result["bust_warnings"] = bust_result.warnings
        result["bust_is_nan"] = np.isnan(bust_result.circumference_m)
    except Exception as e:
        result["bust_warnings"] = [f"EXEC_FAIL: {str(e)}"]
        result["bust_is_nan"] = True
    
    return result


def compute_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute factual statistics from results.
    No PASS/FAIL thresholds - only facts.
    """
    n_total = len(results)
    
    # NaN rates
    underbust_nan_count = sum(1 for r in results if r["underbust_is_nan"])
    bust_nan_count = sum(1 for r in results if r["bust_is_nan"])
    underbust_nan_rate = underbust_nan_count / n_total if n_total > 0 else 0.0
    bust_nan_rate = bust_nan_count / n_total if n_total > 0 else 0.0
    
    # Warning frequency (all warnings)
    all_warnings = []
    for r in results:
        all_warnings.extend(r["underbust_warnings"])
        all_warnings.extend(r["bust_warnings"])
    
    warning_counter = Counter(all_warnings)
    warning_freq = dict(warning_counter.most_common(20))  # Top 20
    
    # Warning co-occurrence (2-way)
    co_occurrence = defaultdict(int)
    for r in results:
        warnings_set = set(r["underbust_warnings"] + r["bust_warnings"])
        warnings_list = list(warnings_set)
        for i in range(len(warnings_list)):
            for j in range(i + 1, len(warnings_list)):
                pair = tuple(sorted([warnings_list[i], warnings_list[j]]))
                co_occurrence[pair] += 1
    
    top_co_occurrence = dict(sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)[:20])
    top_co_occurrence_str = {f"{k[0]}+{k[1]}": v for k, v in top_co_occurrence.items()}
    
    # Value statistics (finite values only)
    underbust_values = [r["underbust_circ_m"] for r in results if r["underbust_circ_m"] is not None]
    bust_values = [r["bust_circ_m"] for r in results if r["bust_circ_m"] is not None]
    
    stats = {
        "n_total": n_total,
        "nan_rates": {
            "underbust": {
                "count": underbust_nan_count,
                "rate": underbust_nan_rate
            },
            "bust": {
                "count": bust_nan_count,
                "rate": bust_nan_rate
            }
        },
        "warning_frequency": warning_freq,
        "warning_co_occurrence": top_co_occurrence_str,
        "value_statistics": {
            "underbust": {
                "n_finite": len(underbust_values),
                "mean": float(np.mean(underbust_values)) if underbust_values else None,
                "std": float(np.std(underbust_values)) if underbust_values else None,
                "min": float(np.min(underbust_values)) if underbust_values else None,
                "max": float(np.max(underbust_values)) if underbust_values else None,
            },
            "bust": {
                "n_finite": len(bust_values),
                "mean": float(np.mean(bust_values)) if bust_values else None,
                "std": float(np.std(bust_values)) if bust_values else None,
                "min": float(np.min(bust_values)) if bust_values else None,
                "max": float(np.max(bust_values)) if bust_values else None,
            }
        }
    }
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="BUST/UNDERBUST v0 Facts-Only Runner (no PASS/FAIL thresholds)"
    )
    parser.add_argument(
        "--input_npz",
        type=str,
        default="verification/datasets/golden/bust_underbust_v0/s0_synthetic_cases.npz",
        help="Input NPZ file path (default: verification/datasets/golden/bust_underbust_v0/s0_synthetic_cases.npz)"
    )
    parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="Number of samples to process (default: all)"
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="verification/runs/facts/bust_underbust",
        help="Output directory (default: verification/runs/facts/bust_underbust)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print(f"Loading data from: {args.input_npz}")
    verts_list, case_ids, load_warnings = load_npz_data(args.input_npz)
    
    # Report load warnings
    if load_warnings:
        print(f"Load warnings ({len(load_warnings)}):")
        for w in load_warnings[:10]:  # Show first 10
            print(f"  {w}")
        if len(load_warnings) > 10:
            print(f"  ... and {len(load_warnings) - 10} more warnings")
    
    # Check if any data loaded
    if len(verts_list) == 0:
        print("WARNING: No valid cases loaded. Generating empty summary...")
        # Generate empty summary
        summary = {
            "git_sha": get_git_sha(),
            "input_npz": args.input_npz,
            "n_samples": 0,
            "load_warnings": load_warnings,
            "statistics": {
                "n_total": 0,
                "nan_rates": {
                    "underbust": {"count": 0, "rate": 0.0},
                    "bust": {"count": 0, "rate": 0.0}
                },
                "warning_frequency": {},
                "warning_co_occurrence": {},
                "value_statistics": {
                    "underbust": {"n_finite": 0, "mean": None, "std": None, "min": None, "max": None},
                    "bust": {"n_finite": 0, "mean": None, "std": None, "min": None, "max": None}
                }
            }
        }
        json_path = out_dir / "facts_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Saved empty summary: {json_path}")
        
        # Create empty CSV
        csv_path = out_dir / "facts_per_sample.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "case_id", "underbust_circ_m", "bust_circ_m", "underbust_is_nan", "bust_is_nan",
                "underbust_method_tag", "bust_method_tag", "underbust_warnings", "bust_warnings"
            ])
            writer.writeheader()
        print(f"Saved empty CSV: {csv_path}")
        print("\n=== Facts Summary ===")
        print(f"Total samples: 0")
        print(f"Load warnings: {len(load_warnings)}")
        return
    
    # Limit number of samples
    if args.n is not None and args.n < len(verts_list):
        verts_list = verts_list[:args.n]
        case_ids = case_ids[:args.n]
    
    print(f"Processing {len(verts_list)} samples...")
    
    # Process samples
    results = []
    for i, (case_id, verts) in enumerate(zip(case_ids, verts_list)):
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(verts_list)} samples...")
        result = process_sample(case_id, verts)
        results.append(result)
    
    print(f"Processed {len(results)} samples.")
    
    # Compute statistics
    print("Computing statistics...")
    stats = compute_statistics(results)
    
    # Save JSON summary
    summary = {
        "git_sha": get_git_sha(),
        "input_npz": args.input_npz,
        "n_samples": len(results),
        "load_warnings": load_warnings if load_warnings else None,
        "statistics": stats
    }
    
    json_path = out_dir / "facts_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved summary: {json_path}")
    
    # Save CSV per-sample results
    csv_path = out_dir / "facts_per_sample.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case_id",
            "underbust_circ_m",
            "bust_circ_m",
            "underbust_is_nan",
            "bust_is_nan",
            "underbust_method_tag",
            "bust_method_tag",
            "underbust_warnings",
            "bust_warnings"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "underbust_circ_m": r["underbust_circ_m"],
                "bust_circ_m": r["bust_circ_m"],
                "underbust_is_nan": r["underbust_is_nan"],
                "bust_is_nan": r["bust_is_nan"],
                "underbust_method_tag": r["underbust_method_tag"],
                "bust_method_tag": r["bust_method_tag"],
                "underbust_warnings": "; ".join(r["underbust_warnings"]),
                "bust_warnings": "; ".join(r["bust_warnings"])
            })
    print(f"Saved per-sample results: {csv_path}")
    
    # Print summary
    print("\n=== Facts Summary ===")
    print(f"Total samples: {stats['n_total']}")
    print(f"UNDERBUST NaN rate: {stats['nan_rates']['underbust']['rate']:.2%} ({stats['nan_rates']['underbust']['count']}/{stats['n_total']})")
    print(f"BUST NaN rate: {stats['nan_rates']['bust']['rate']:.2%} ({stats['nan_rates']['bust']['count']}/{stats['n_total']})")
    print(f"\nTop warnings:")
    for warning, count in list(stats['warning_frequency'].items())[:10]:
        print(f"  {warning}: {count}")
    print(f"\nOutput directory: {out_dir}")


if __name__ == "__main__":
    main()
