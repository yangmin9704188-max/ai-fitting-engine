#!/usr/bin/env python3
"""
A-Pose Normalization v1.1 Verification Script

Purpose: Verify that A-Pose Normalization v1.1 (FROZEN) meets all policy requirements.

Verification Criteria:
- dtype float32 maintained
- axis convention (y-axis)
- A-Pose angle range (30-45 deg, tol ±5) violation rate = 0
- exceptions = 0

Output:
- verification/reports/apose_v11/verification_results.csv
- verification/reports/apose_v11/verification_summary.json
- verification/reports/apose_v11/case_*_debug.json (for failures)
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
import torch
import smplx
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pose_policy import PoseNormalizer

# A-Pose policy constants (FROZEN)
APOSE_ANGLE_DEG = 30.0
APOSE_AXIS = 'y'
APOSE_L_IDX = 16
APOSE_R_IDX = 17
APOSE_SIGN_L = +1.0
APOSE_SIGN_R = -1.0

# Expected angle range: 30-45 deg, tol ±5 → [25, 50] deg
ANGLE_MIN_DEG = 25.0
ANGLE_MAX_DEG = 50.0


def compute_shoulder_elbow_angle_from_pose(body_pose: torch.Tensor, side: str) -> float:
    """Extract A-Pose angle from body_pose tensor."""
    if side == "L":
        idx = APOSE_L_IDX
        sign = APOSE_SIGN_L
    else:
        idx = APOSE_R_IDX
        sign = APOSE_SIGN_R
    
    # Get y-axis rotation (offset = 1 for y-axis)
    angle_rad = body_pose[0, idx * 3 + 1].item()
    angle_deg = np.degrees(angle_rad) * sign  # Apply sign
    
    return float(angle_deg)


def verify_apose_case(
    case_id: int,
    sex: str,
    betas: np.ndarray,
    model: smplx.SMPLX,
    normalizer: PoseNormalizer,
    device: torch.device,
    output_dir: str,
) -> Dict[str, Any]:
    """Verify A-Pose for a single case."""
    
    result = {
        "case_id": case_id,
        "sex": sex,
        "status": "SUCCESS",
        "errors": [],
        "dtype_check": None,
        "axis_check": None,
        "angle_L_deg": None,
        "angle_R_deg": None,
        "angle_violation": None,
        "exception": None,
    }
    
    try:
        # Convert betas to tensor
        beta_t = torch.tensor(betas, dtype=torch.float32, device=device).unsqueeze(0)
        
        # Get A-Pose from policy
        body_pose = normalizer.get_policy_a_pose(
            batch_size=1,
            device=device,
            dtype=torch.float32,
        )
        
        # Check dtype
        if body_pose.dtype != torch.float32:
            result["errors"].append(f"dtype mismatch: expected float32, got {body_pose.dtype}")
            result["dtype_check"] = False
        else:
            result["dtype_check"] = True
        
        # Check axis convention
        # Verify that only y-axis rotation is applied
        l_offset = APOSE_L_IDX * 3 + 1  # y-axis offset
        r_offset = APOSE_R_IDX * 3 + 1
        
        # Check that x and z components are zero
        body_pose_np = body_pose[0].detach().cpu().numpy()
        l_x = body_pose_np[APOSE_L_IDX * 3 + 0]
        l_z = body_pose_np[APOSE_L_IDX * 3 + 2]
        r_x = body_pose_np[APOSE_R_IDX * 3 + 0]
        r_z = body_pose_np[APOSE_R_IDX * 3 + 2]
        
        if abs(l_x) > 1e-6 or abs(l_z) > 1e-6 or abs(r_x) > 1e-6 or abs(r_z) > 1e-6:
            result["errors"].append(f"axis violation: non-zero x/z rotations detected")
            result["axis_check"] = False
        else:
            result["axis_check"] = True
        
        # Get A-Pose angles directly from body_pose
        angle_L = compute_shoulder_elbow_angle_from_pose(body_pose, "L")
        angle_R = compute_shoulder_elbow_angle_from_pose(body_pose, "R")
        
        result["angle_L_deg"] = angle_L
        result["angle_R_deg"] = angle_R
        
        # Check angle range
        angle_violation = False
        if angle_L is not None and (angle_L < ANGLE_MIN_DEG or angle_L > ANGLE_MAX_DEG):
            result["errors"].append(f"L angle {angle_L:.2f}deg out of range [{ANGLE_MIN_DEG}, {ANGLE_MAX_DEG}]")
            angle_violation = True
        if angle_R is not None and (angle_R < ANGLE_MIN_DEG or angle_R > ANGLE_MAX_DEG):
            result["errors"].append(f"R angle {angle_R:.2f}deg out of range [{ANGLE_MIN_DEG}, {ANGLE_MAX_DEG}]")
            angle_violation = True
        
        result["angle_violation"] = angle_violation
        
        # Final status
        if len(result["errors"]) > 0:
            result["status"] = "FAILED"
            
            # Save debug info
            debug_file = os.path.join(output_dir, f"case_{case_id}_debug.json")
            debug_info = {
                "case_id": case_id,
                "sex": sex,
                "errors": result["errors"],
                "body_pose": body_pose[0].detach().cpu().numpy().tolist(),
                "angle_L_deg": angle_L,
                "angle_R_deg": angle_R,
                "angle_range_expected": [ANGLE_MIN_DEG, ANGLE_MAX_DEG],
            }
            with open(debug_file, "w", encoding="utf-8") as f:
                json.dump(debug_info, f, indent=2)
    
    except Exception as e:
        result["status"] = "EXCEPTION"
        result["exception"] = str(e)
        result["errors"].append(f"Exception: {type(e).__name__}: {str(e)}")
        
        # Save debug info
        debug_file = os.path.join(output_dir, f"case_{case_id}_debug.json")
        debug_info = {
            "case_id": case_id,
            "sex": sex,
            "exception": str(e),
            "exception_type": type(e).__name__,
        }
        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(debug_info, f, indent=2)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Verify A-Pose Normalization v1.1 (FROZEN)"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="./models",
        help="Path to SMPL-X model directory",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./data/processed/step1_output",
        help="Path to step1 output directory",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="verification/reports/apose_v11",
        help="Output directory for results",
    )
    parser.add_argument(
        "--n_cases",
        type=int,
        default=20,
        help="Number of test cases to generate",
    )
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("A-Pose Normalization v1.1 Verification")
    print("=" * 80)
    print(f"Model path: {args.model_path}")
    print(f"Data dir: {args.data_dir}")
    print(f"Output dir: {args.out_dir}")
    print(f"Test cases: {args.n_cases}")
    print()
    
    # Load beta means
    male_betas_path = os.path.join(args.data_dir, "init_betas_male.npy")
    female_betas_path = os.path.join(args.data_dir, "init_betas_female.npy")
    
    if not os.path.exists(male_betas_path) or not os.path.exists(female_betas_path):
        raise FileNotFoundError(
            f"Beta mean files not found. Expected:\n"
            f"  - {male_betas_path}\n"
            f"  - {female_betas_path}"
        )
    
    male_betas_all = np.load(male_betas_path)  # (N, num_betas)
    female_betas_all = np.load(female_betas_path)  # (N, num_betas)
    
    num_betas = male_betas_all.shape[1]
    print(f"Loaded beta means:")
    print(f"  Male: {male_betas_all.shape[0]} samples, {num_betas} dims")
    print(f"  Female: {female_betas_all.shape[0]} samples, {num_betas} dims")
    print()
    
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    normalizer = PoseNormalizer(device=device)
    
    # Generate test cases
    cases = []
    np.random.seed(42)
    
    for i in range(args.n_cases):
        sex = "male" if i % 2 == 0 else "female"
        betas_all = male_betas_all if sex == "male" else female_betas_all
        
        # Random sample from betas
        idx = np.random.randint(0, len(betas_all))
        betas = betas_all[idx].astype(np.float32)
        
        cases.append({
            "case_id": i + 1,
            "sex": sex,
            "betas": betas,
        })
    
    print(f"Generated {len(cases)} test cases")
    print()
    
    # Run verification
    results = []
    print("Running verification...")
    print("-" * 80)
    
    for case in cases:
        # Load model for this sex
        gender = case["sex"]
        model = smplx.create(
            args.model_path,
            model_type="smplx",
            gender=gender,
            use_pca=False,
            num_betas=num_betas,
            ext="pkl",
        ).to(device)
        model.eval()
        
        result = verify_apose_case(
            case_id=case["case_id"],
            sex=case["sex"],
            betas=case["betas"],
            model=model,
            normalizer=normalizer,
            device=device,
            output_dir=args.out_dir,
        )
        
        results.append(result)
        
        status_icon = "[OK]" if result["status"] == "SUCCESS" else "[FAIL]"
        print(f"{status_icon} Case {case['case_id']:2d} ({case['sex']:6s}): {result['status']}")
        if result["errors"]:
            for err in result["errors"]:
                print(f"         - {err}")
    
    print("-" * 80)
    print()
    
    # Save results CSV
    import pandas as pd
    df = pd.DataFrame(results)
    csv_path = os.path.join(args.out_dir, "verification_results.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Results CSV: {csv_path}")
    
    # Compute summary
    n_total = len(results)
    n_success = sum(1 for r in results if r["status"] == "SUCCESS")
    n_failed = sum(1 for r in results if r["status"] == "FAILED")
    n_exception = sum(1 for r in results if r["status"] == "EXCEPTION")
    
    dtype_ok = sum(1 for r in results if r.get("dtype_check") is True)
    axis_ok = sum(1 for r in results if r.get("axis_check") is True)
    angle_violations = sum(1 for r in results if r.get("angle_violation") is True)
    
    summary = {
        "policy_version": "A-Pose Normalization v1.1",
        "policy_tag": "pose_apose_v11_frozen_2026-01-16",
        "cfg_used": {
            "angle_deg": APOSE_ANGLE_DEG,
            "axis": APOSE_AXIS,
            "l_idx": APOSE_L_IDX,
            "r_idx": APOSE_R_IDX,
            "sign_l": APOSE_SIGN_L,
            "sign_r": APOSE_SIGN_R,
        },
        "verification_criteria": {
            "dtype": "float32",
            "axis": "y-axis only",
            "angle_range_deg": [ANGLE_MIN_DEG, ANGLE_MAX_DEG],
        },
        "results": {
            "n_total": n_total,
            "n_success": n_success,
            "n_failed": n_failed,
            "n_exception": n_exception,
            "success_rate": float(n_success / n_total) if n_total > 0 else 0.0,
        },
        "checks": {
            "dtype_check_pass": dtype_ok,
            "dtype_check_fail": n_total - dtype_ok,
            "axis_check_pass": axis_ok,
            "axis_check_fail": n_total - axis_ok,
            "angle_violations": angle_violations,
        },
        "compliance": {
            "dtype_compliant": dtype_ok == n_total,
            "axis_compliant": axis_ok == n_total,
            "angle_compliant": angle_violations == 0,
            "exception_compliant": n_exception == 0,
            "all_compliant": (dtype_ok == n_total and axis_ok == n_total and 
                            angle_violations == 0 and n_exception == 0),
        },
    }
    
    # Save summary JSON
    summary_path = os.path.join(args.out_dir, "verification_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON: {summary_path}")
    print()
    
    # Print summary
    print("=" * 80)
    print("Verification Summary")
    print("=" * 80)
    print(f"Total cases: {n_total}")
    print(f"Success: {n_success}")
    print(f"Failed: {n_failed}")
    print(f"Exceptions: {n_exception}")
    print()
    print("Compliance:")
    print(f"  dtype (float32): {'PASS' if summary['compliance']['dtype_compliant'] else 'FAIL'}")
    print(f"  axis (y-axis only): {'PASS' if summary['compliance']['axis_compliant'] else 'FAIL'}")
    print(f"  angle range [{ANGLE_MIN_DEG}, {ANGLE_MAX_DEG}] deg: {'PASS' if summary['compliance']['angle_compliant'] else 'FAIL'}")
    print(f"  no exceptions: {'PASS' if summary['compliance']['exception_compliant'] else 'FAIL'}")
    print()
    print(f"Overall: {'PASS' if summary['compliance']['all_compliant'] else 'FAIL'}")
    print("=" * 80)
    
    # Exit code
    sys.exit(0 if summary['compliance']['all_compliant'] else 1)


if __name__ == "__main__":
    main()
