#!/usr/bin/env python3
"""
Circumference v0 Verification Runner

Purpose: Record validation results for measure_circumference_v0.
No PASS/FAIL thresholds - factual recording only.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
import csv
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.measurements.circumference_v0 import measure_circumference_v0, CircumferenceResult

# Measurement keys to test
MEASUREMENT_KEYS = ["BUST", "WAIST", "HIP"]


def get_git_sha() -> Optional[str]:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def verify_case(
    case_id: str,
    verts: np.ndarray,
    measurement_key: str,
) -> Dict[str, Any]:
    """
    Verify a single case for a measurement key.
    Returns dict with results or failure info.
    """
    result = {
        "case_id": str(case_id),
        "measurement_key": measurement_key,
        "circumference_m": None,
        "section_id": None,
        "method_tag": None,
        "warnings_json": None,
        "failure_type": None,
    }
    
    try:
        # Call measurement function
        output: CircumferenceResult = measure_circumference_v0(
            verts=verts,
            measurement_key=measurement_key,
            units_metadata=None,
        )
        
        # Record output
        result["circumference_m"] = output.circumference_m
        result["section_id"] = output.section_id
        result["method_tag"] = output.method_tag
        result["warnings_json"] = json.dumps(output.warnings, ensure_ascii=False)
        
        # Check for unit failure suspicion
        if not np.isnan(output.circumference_m) and output.circumference_m > 10.0:
            result["failure_type"] = "UNIT_FAIL"
        
        # Check for degenerate cases
        if "EMPTY_CANDIDATES" in output.warnings or "BODY_AXIS_TOO_SHORT" in output.warnings:
            if result["failure_type"] is None:
                result["failure_type"] = "DEGEN_FAIL"
        
    except ValueError as e:
        # Input validation failure
        result["failure_type"] = "INPUT_CONTRACT_FAIL"
        stacktrace = traceback.format_exc()
        # Truncate if too long
        if len(stacktrace) > 500:
            stacktrace = stacktrace[:500] + "... (truncated)"
        result["warnings_json"] = json.dumps([f"INPUT_CONTRACT_FAIL: {str(e)}", stacktrace], ensure_ascii=False)
    except Exception as e:
        # Execution failure
        result["failure_type"] = "EXEC_FAIL"
        stacktrace = traceback.format_exc()
        # Truncate if too long
        if len(stacktrace) > 500:
            stacktrace = stacktrace[:500] + "... (truncated)"
        result["warnings_json"] = json.dumps([f"EXEC_FAIL: {str(e)}", stacktrace], ensure_ascii=False)
    
    return result


def check_determinism(
    case_id: str,
    verts: np.ndarray,
    measurement_key: str,
) -> bool:
    """
    Check determinism: call twice and compare section_id/method_tag.
    Returns True if deterministic, False otherwise.
    """
    try:
        result1 = measure_circumference_v0(verts=verts, measurement_key=measurement_key)
        result2 = measure_circumference_v0(verts=verts, measurement_key=measurement_key)
        
        return (
            result1.section_id == result2.section_id and
            result1.method_tag == result2.method_tag
        )
    except Exception:
        return False  # If exception, consider non-deterministic


def main():
    parser = argparse.ArgumentParser(
        description="Verify Circumference v0 (factual recording only)"
    )
    parser.add_argument(
        "--npz",
        type=str,
        default="verification/datasets/golden/circumference_v0/s0_synthetic_cases.npz",
        help="Path to NPZ file containing verts and case_id",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="verification/reports/circumference_v0",
        help="Output directory for results",
    )
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Circumference v0 Verification")
    print("=" * 80)
    print(f"Input NPZ: {args.npz}")
    print(f"Output dir: {args.out_dir}")
    print()
    
    # Load NPZ
    if not os.path.exists(args.npz):
        raise FileNotFoundError(f"NPZ file not found: {args.npz}")
    
    data = np.load(args.npz, allow_pickle=True)
    
    # Handle variable-length arrays
    verts_list = data["verts"]
    case_ids = data["case_id"]
    
    # Convert to list if needed
    if isinstance(verts_list, np.ndarray) and verts_list.dtype == object:
        verts_list = [verts_list[i] for i in range(len(verts_list))]
    if isinstance(case_ids, np.ndarray) and case_ids.dtype == object:
        case_ids = [case_ids[i] for i in range(len(case_ids))]
    
    n_cases = len(verts_list)
    print(f"Loaded {n_cases} cases from NPZ")
    print()
    
    # Run verification
    all_results = []
    determinism_results = []
    
    print("Running verification...")
    print("-" * 80)
    
    for case_idx in range(n_cases):
        case_id = case_ids[case_idx] if isinstance(case_ids, (list, np.ndarray)) else f"case_{case_idx}"
        verts = verts_list[case_idx]
        
        # Ensure float32
        if verts.dtype != np.float32:
            verts = verts.astype(np.float32)
        
        # Ensure shape (N, 3)
        if verts.ndim == 1:
            verts = verts.reshape(-1, 3)
        
        for measurement_key in MEASUREMENT_KEYS:
            result = verify_case(case_id, verts, measurement_key)
            all_results.append(result)
            
            # Check determinism (only for first measurement_key to avoid redundancy)
            if measurement_key == MEASUREMENT_KEYS[0]:
                is_deterministic = check_determinism(case_id, verts, measurement_key)
                determinism_results.append({
                    "case_id": str(case_id),
                    "measurement_key": measurement_key,
                    "is_deterministic": is_deterministic,
                })
            
            # Print status
            status = "OK" if result["failure_type"] is None else result["failure_type"]
            circ_str = f"{result['circumference_m']:.4f}" if result["circumference_m"] is not None and not np.isnan(result["circumference_m"]) else "NaN"
            print(f"  {case_id} / {measurement_key}: {status} | circ={circ_str}m")
    
    print()
    print("-" * 80)
    
    # Write CSV
    csv_path = os.path.join(args.out_dir, "validation_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case_id", "measurement_key", "circumference_m", "section_id",
            "method_tag", "warnings_json", "failure_type"
        ])
        writer.writeheader()
        for result in all_results:
            # Convert NaN to string for CSV
            row = result.copy()
            if row["circumference_m"] is not None and np.isnan(row["circumference_m"]):
                row["circumference_m"] = "NaN"
            writer.writerow(row)
    
    print(f"Wrote CSV: {csv_path}")
    
    # Compute summary statistics
    nan_count_by_key = {key: 0 for key in MEASUREMENT_KEYS}
    warning_histogram = {}
    failure_count_by_type = {}
    nonfinite_count = 0
    determinism_mismatch_count = 0
    
    for result in all_results:
        key = result["measurement_key"]
        
        # NaN count
        if result["circumference_m"] is None or (isinstance(result["circumference_m"], float) and np.isnan(result["circumference_m"])):
            nan_count_by_key[key] = nan_count_by_key.get(key, 0) + 1
            nonfinite_count += 1
        
        # Warning histogram
        if result["warnings_json"]:
            try:
                warnings = json.loads(result["warnings_json"])
                for warning in warnings:
                    if isinstance(warning, str):
                        # Extract warning type (first word before colon or underscore)
                        warning_type = warning.split(":")[0].split("_")[0]
                        warning_histogram[warning_type] = warning_histogram.get(warning_type, 0) + 1
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Failure count
        if result["failure_type"]:
            failure_count_by_type[result["failure_type"]] = failure_count_by_type.get(result["failure_type"], 0) + 1
    
    # Determinism mismatch count
    for det_result in determinism_results:
        if not det_result["is_deterministic"]:
            determinism_mismatch_count += 1
    
    # Compute NaN rates
    total_by_key = {key: len([r for r in all_results if r["measurement_key"] == key]) for key in MEASUREMENT_KEYS}
    nan_rate_by_key = {
        key: nan_count_by_key[key] / total_by_key[key] if total_by_key[key] > 0 else 0.0
        for key in MEASUREMENT_KEYS
    }
    
    # Extract dataset ID from NPZ path
    dataset_id = os.path.basename(args.npz).replace(".npz", "")
    
    # Create summary JSON
    summary = {
        "git_sha": get_git_sha(),
        "dataset_id": dataset_id,
        "nan_rate_by_key": nan_rate_by_key,
        "warning_histogram": warning_histogram,
        "determinism_mismatch_count": determinism_mismatch_count,
        "nonfinite_count": nonfinite_count,
        "failure_count_by_type": failure_count_by_type,
    }
    
    json_path = os.path.join(args.out_dir, "validation_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote JSON: {json_path}")
    print()
    print("Summary:")
    print(f"  NaN rate by key: {nan_rate_by_key}")
    print(f"  Determinism mismatches: {determinism_mismatch_count}")
    print(f"  Non-finite count: {nonfinite_count}")
    print(f"  Failures by type: {failure_count_by_type}")
    print()
    print("=" * 80)
    print("Verification complete (factual recording only, no PASS/FAIL judgment)")


if __name__ == "__main__":
    main()
