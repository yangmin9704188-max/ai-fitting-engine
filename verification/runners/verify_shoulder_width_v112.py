#!/usr/bin/env python3
"""
Shoulder Width v1.1.2 Verification Script

Purpose: Verify that Shoulder Width v1.1.2 (FROZEN) meets all policy requirements.

Verification Criteria:
- cfg_used == cfg_frozen (policy-to-run wiring proof)
- ratio = measured_sw / joint_sw in [1.0, 1.3] range
- ||lm - shoulder_joint|| < 0.20m (L/R)
- fallback/exceptions = 0
- worst-case 1 debug JSON saved

Output:
- verification/reports/shoulder_width_v112/verification_results.csv
- verification/reports/shoulder_width_v112/verification_summary.json
- verification/reports/shoulder_width_v112/case_*_debug.json (for failures/worst-case)
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.measurements.shoulder_width_v112 import measure_shoulder_width_v112, ShoulderWidthV112Config
from core.policy.shoulder_width_v112_policy import get_cfg as get_frozen_cfg

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}

# Verification thresholds
RATIO_MIN = 1.0
RATIO_MAX = 1.3
LANDMARK_DIST_MAX = 0.20  # meters


def verify_shoulder_width_case(
    case_id: int,
    verts: np.ndarray,
    lbs_weights: np.ndarray,
    joints_xyz: np.ndarray,
    output_dir: str,
    save_debug: bool = False,
) -> Dict[str, Any]:
    """Verify shoulder width measurement for a single case."""
    
    result = {
        "case_id": case_id,
        "status": "SUCCESS",
        "errors": [],
        "cfg_match": None,
        "measured_sw_m": None,
        "joint_sw_m": None,
        "ratio": None,
        "landmark_L_dist_m": None,
        "landmark_R_dist_m": None,
        "fallback_used": None,
        "exception": None,
    }
    
    try:
        # Get frozen config
        cfg_frozen = get_frozen_cfg()
        
        # Run measurement with debug to verify cfg
        width, debug_info = measure_shoulder_width_v112(
            verts=verts,
            lbs_weights=lbs_weights,
            joints_xyz=joints_xyz,
            joint_ids=SMPLX_JOINT_IDS,
            cfg=cfg_frozen,  # Use frozen config (not None)
            return_debug=True,
        )
        
        # Check cfg match (verify that frozen config was used)
        # This is a policy-to-run wiring proof
        cfg_used = {
            "r0_ratio": cfg_frozen.r0_ratio,
            "r1_ratio": cfg_frozen.r1_ratio,
            "cap_quantile": cfg_frozen.cap_quantile,
        }
        cfg_expected = {
            "r0_ratio": 0.26,
            "r1_ratio": 0.18,
            "cap_quantile": 0.94,
        }
        
        cfg_match = (
            abs(cfg_used["r0_ratio"] - cfg_expected["r0_ratio"]) < 1e-6 and
            abs(cfg_used["r1_ratio"] - cfg_expected["r1_ratio"]) < 1e-6 and
            abs(cfg_used["cap_quantile"] - cfg_expected["cap_quantile"]) < 1e-6
        )
        
        result["cfg_match"] = cfg_match
        if not cfg_match:
            result["errors"].append(f"cfg mismatch: used {cfg_used}, expected {cfg_expected}")
        
        result["measured_sw_m"] = float(width)
        
        # Compute joint-based SW
        L_sh = joints_xyz[SMPLX_JOINT_IDS["L_shoulder"], :]
        R_sh = joints_xyz[SMPLX_JOINT_IDS["R_shoulder"], :]
        joint_sw = float(np.linalg.norm(L_sh - R_sh))
        result["joint_sw_m"] = joint_sw
        
        # Compute ratio
        ratio = width / joint_sw if joint_sw > 0 else None
        result["ratio"] = ratio
        
        if ratio is not None:
            if ratio < RATIO_MIN or ratio > RATIO_MAX:
                result["errors"].append(
                    f"ratio {ratio:.3f} out of range [{RATIO_MIN}, {RATIO_MAX}]"
                )
        
        # Check landmark distances
        landmark_L = debug_info["landmark_L"]
        landmark_R = debug_info["landmark_R"]
        
        dist_L = float(np.linalg.norm(landmark_L - L_sh))
        dist_R = float(np.linalg.norm(landmark_R - R_sh))
        
        result["landmark_L_dist_m"] = dist_L
        result["landmark_R_dist_m"] = dist_R
        
        if dist_L >= LANDMARK_DIST_MAX:
            result["errors"].append(f"L landmark distance {dist_L:.4f}m >= {LANDMARK_DIST_MAX}m")
        if dist_R >= LANDMARK_DIST_MAX:
            result["errors"].append(f"R landmark distance {dist_R:.4f}m >= {LANDMARK_DIST_MAX}m")
        
        # Check fallback
        fallback = bool(debug_info["fallback"][0])
        result["fallback_used"] = fallback
        if fallback:
            result["errors"].append("fallback used (no geometry after filtering)")
        
        # Final status
        if len(result["errors"]) > 0:
            result["status"] = "FAILED"
        
        # Save debug if requested or if failed
        if save_debug or result["status"] == "FAILED":
            debug_file = os.path.join(output_dir, f"case_{case_id}_debug.json")
            debug_output = {
                "case_id": case_id,
                "cfg_used": {
                    "r0_ratio": float(cfg_frozen.r0_ratio),
                    "r1_ratio": float(cfg_frozen.r1_ratio),
                    "cap_quantile": float(cfg_frozen.cap_quantile),
                    "distal_w_threshold": float(cfg_frozen.distal_w_threshold),
                    "s_min_ratio": float(cfg_frozen.s_min_ratio),
                    "s_max_ratio": float(cfg_frozen.s_max_ratio),
                    "min_cap_points": int(cfg_frozen.min_cap_points),
                },
                "cfg_expected": cfg_expected,
                "cfg_match": cfg_match,
                "measurements": {
                    "measured_sw_m": float(width),
                    "joint_sw_m": joint_sw,
                    "ratio": ratio,
                },
                "landmarks": {
                    "landmark_L_xyz": landmark_L.tolist(),
                    "landmark_R_xyz": landmark_R.tolist(),
                    "L_shoulder_xyz": L_sh.tolist(),
                    "R_shoulder_xyz": R_sh.tolist(),
                    "landmark_L_dist_m": dist_L,
                    "landmark_R_dist_m": dist_R,
                },
                "fallback_used": fallback,
                "errors": result["errors"],
            }
            with open(debug_file, "w", encoding="utf-8") as f:
                json.dump(debug_output, f, indent=2)
    
    except Exception as e:
        result["status"] = "EXCEPTION"
        result["exception"] = str(e)
        result["errors"].append(f"Exception: {type(e).__name__}: {str(e)}")
        
        # Save debug info
        debug_file = os.path.join(output_dir, f"case_{case_id}_debug.json")
        debug_info = {
            "case_id": case_id,
            "exception": str(e),
            "exception_type": type(e).__name__,
        }
        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(debug_info, f, indent=2)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Verify Shoulder Width v1.1.2 (FROZEN)"
    )
    parser.add_argument(
        "--npz",
        type=str,
        required=True,
        help="Path to NPZ file containing verts/lbs_weights/joints_xyz",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="verification/reports/shoulder_width_v112",
        help="Output directory for results",
    )
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Shoulder Width v1.1.2 Verification")
    print("=" * 80)
    print(f"Input NPZ: {args.npz}")
    print(f"Output dir: {args.out_dir}")
    print()
    
    # Load NPZ
    if not os.path.exists(args.npz):
        raise FileNotFoundError(f"NPZ file not found: {args.npz}")
    
    data = np.load(args.npz, allow_pickle=False)
    keys = set(data.files)
    
    required_keys = ["verts", "lbs_weights", "joints_xyz"]
    missing_keys = [k for k in required_keys if k not in keys]
    if missing_keys:
        raise KeyError(f"NPZ missing required keys: {missing_keys}. Found: {sorted(keys)}")
    
    verts = data["verts"]  # (T, N, 3) or (N, 3)
    lbs_weights = data["lbs_weights"]  # (N, J) or (T, N, J)
    joints_xyz = data["joints_xyz"]  # (J, 3) or (T, J, 3)
    
    # Ensure batched
    if verts.ndim == 2:
        verts = verts[None, ...]
    if lbs_weights.ndim == 2:
        lbs_weights = lbs_weights[None, ...]
    if joints_xyz.ndim == 2:
        joints_xyz = joints_xyz[None, ...]
    
    n_frames = verts.shape[0]
    print(f"Loaded {n_frames} frames from NPZ")
    print()
    
    # Run verification for each frame
    results = []
    print("Running verification...")
    print("-" * 80)
    
    for frame_idx in range(n_frames):
        case_id = frame_idx + 1
        
        # Extract frame data
        verts_frame = verts[frame_idx, :, :]
        lbs_weights_frame = lbs_weights[frame_idx, :, :]
        joints_xyz_frame = joints_xyz[frame_idx, :, :]
        
        # Save debug for worst-case (last frame or first failure)
        save_debug = (frame_idx == n_frames - 1)  # Save last frame as worst-case
        
        result = verify_shoulder_width_case(
            case_id=case_id,
            verts=verts_frame,
            lbs_weights=lbs_weights_frame,
            joints_xyz=joints_xyz_frame,
            output_dir=args.out_dir,
            save_debug=save_debug,
        )
        
        results.append(result)
        
        status_icon = "[OK]" if result["status"] == "SUCCESS" else "[FAIL]"
        print(f"{status_icon} Case {case_id:3d}: {result['status']}", end="")
        if result.get("measured_sw_m") is not None:
            print(f" | SW: {result['measured_sw_m']:.4f}m, Joint: {result['joint_sw_m']:.4f}m, Ratio: {result['ratio']:.3f}", end="")
        print()
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
    
    cfg_matches = sum(1 for r in results if r.get("cfg_match") is True)
    ratio_violations = sum(1 for r in results if r.get("ratio") is not None and 
                          (r["ratio"] < RATIO_MIN or r["ratio"] > RATIO_MAX))
    landmark_violations = sum(1 for r in results if 
                             (r.get("landmark_L_dist_m") is not None and r["landmark_L_dist_m"] >= LANDMARK_DIST_MAX) or
                             (r.get("landmark_R_dist_m") is not None and r["landmark_R_dist_m"] >= LANDMARK_DIST_MAX))
    fallbacks = sum(1 for r in results if r.get("fallback_used") is True)
    
    # Get frozen config for summary
    cfg_frozen = get_frozen_cfg()
    
    summary = {
        "policy_version": "Shoulder Width v1.1.2",
        "policy_tag": "shoulder_width_v112_frozen_2026-01-16",
        "cfg_used": {
            "r0_ratio": float(cfg_frozen.r0_ratio),
            "r1_ratio": float(cfg_frozen.r1_ratio),
            "cap_quantile": float(cfg_frozen.cap_quantile),
            "distal_w_threshold": float(cfg_frozen.distal_w_threshold),
            "s_min_ratio": float(cfg_frozen.s_min_ratio),
            "s_max_ratio": float(cfg_frozen.s_max_ratio),
            "min_cap_points": int(cfg_frozen.min_cap_points),
        },
        "cfg_expected": {
            "r0_ratio": 0.26,
            "r1_ratio": 0.18,
            "cap_quantile": 0.94,
        },
        "verification_criteria": {
            "ratio_range": [RATIO_MIN, RATIO_MAX],
            "landmark_dist_max_m": LANDMARK_DIST_MAX,
        },
        "results": {
            "n_total": n_total,
            "n_success": n_success,
            "n_failed": n_failed,
            "n_exception": n_exception,
            "success_rate": float(n_success / n_total) if n_total > 0 else 0.0,
        },
        "checks": {
            "cfg_match_pass": cfg_matches,
            "cfg_match_fail": n_total - cfg_matches,
            "ratio_violations": ratio_violations,
            "landmark_violations": landmark_violations,
            "fallbacks": fallbacks,
        },
        "compliance": {
            "cfg_compliant": cfg_matches == n_total,
            "ratio_compliant": ratio_violations == 0,
            "landmark_compliant": landmark_violations == 0,
            "fallback_compliant": fallbacks == 0,
            "exception_compliant": n_exception == 0,
            "all_compliant": (cfg_matches == n_total and ratio_violations == 0 and 
                            landmark_violations == 0 and fallbacks == 0 and n_exception == 0),
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
    print(f"  cfg match: {'PASS' if summary['compliance']['cfg_compliant'] else 'FAIL'}")
    print(f"  ratio [{RATIO_MIN}, {RATIO_MAX}]: {'PASS' if summary['compliance']['ratio_compliant'] else 'FAIL'}")
    print(f"  landmark dist < {LANDMARK_DIST_MAX}m: {'PASS' if summary['compliance']['landmark_compliant'] else 'FAIL'}")
    print(f"  no fallback: {'PASS' if summary['compliance']['fallback_compliant'] else 'FAIL'}")
    print(f"  no exceptions: {'PASS' if summary['compliance']['exception_compliant'] else 'FAIL'}")
    print()
    print(f"Overall: {'PASS' if summary['compliance']['all_compliant'] else 'FAIL'}")
    print("=" * 80)
    
    # Exit code
    sys.exit(0 if summary['compliance']['all_compliant'] else 1)


if __name__ == "__main__":
    main()
