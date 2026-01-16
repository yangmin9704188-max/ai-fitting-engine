#!/usr/bin/env python3
"""
Shoulder Width v1.1.3 (Candidate) Parameter Sweep Verification

Purpose: Evaluate candidate parameter configurations for Shoulder Width v1.1.3
         with semantic validity gates, wiring proof, and regression analysis.

Semantic Validity Gates:
- Upper arm leakage detection (landmark distance, ratio threshold)
- Fallback rate = 0
- Exception rate = 0

Wiring Proof:
- Runtime cfg hash matches policy cfg hash

Golden Set Regression:
- Error statistics (mean, std, max deviation)
- Variance analysis
- Per-case breakdown

Output:
- artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/sweep_results.csv
- artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/sweep_summary.json
- artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/candidate_*/ (pass/fail cases)
- artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD/wiring_proof.json
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.measurements.shoulder_width_v112 import measure_shoulder_width_v112, ShoulderWidthV112Config

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}

# Semantic validity thresholds
RATIO_MAX = 1.3  # measured_sw / joint_sw must be <= 1.3
LANDMARK_DIST_MAX = 0.20  # meters - landmark distance from shoulder joint


def cfg_to_hash(cfg: ShoulderWidthV112Config) -> str:
    """Compute hash of configuration for wiring proof."""
    cfg_dict = {
        "r0_ratio": float(cfg.r0_ratio),
        "r1_ratio": float(cfg.r1_ratio),
        "cap_quantile": float(cfg.cap_quantile),
        "distal_w_threshold": float(cfg.distal_w_threshold),
        "s_min_ratio": float(cfg.s_min_ratio),
        "s_max_ratio": float(cfg.s_max_ratio),
        "min_cap_points": int(cfg.min_cap_points),
    }
    cfg_str = json.dumps(cfg_dict, sort_keys=True)
    return hashlib.sha256(cfg_str.encode()).hexdigest()[:16]


def detect_upper_arm_leakage(
    landmark_L: np.ndarray,
    landmark_R: np.ndarray,
    shoulder_L: np.ndarray,
    shoulder_R: np.ndarray,
    measured_sw: float,
    joint_sw: float,
) -> Tuple[bool, str]:
    """
    Detect upper arm leakage based on geometric checks.
    
    Returns:
        (is_leakage, reason)
    """
    dist_L = float(np.linalg.norm(landmark_L - shoulder_L))
    dist_R = float(np.linalg.norm(landmark_R - shoulder_R))
    
    ratio = measured_sw / joint_sw if joint_sw > 0 else None
    
    reasons = []
    
    if dist_L >= LANDMARK_DIST_MAX:
        reasons.append(f"L_landmark_dist={dist_L:.4f}m>={LANDMARK_DIST_MAX}m")
    if dist_R >= LANDMARK_DIST_MAX:
        reasons.append(f"R_landmark_dist={dist_R:.4f}m>={LANDMARK_DIST_MAX}m")
    if ratio is not None and ratio > RATIO_MAX:
        reasons.append(f"ratio={ratio:.3f}>{RATIO_MAX}")
    
    if len(reasons) > 0:
        return True, "; ".join(reasons)
    return False, ""


def evaluate_candidate_config(
    candidate_id: str,
    cfg: ShoulderWidthV112Config,
    verts_all: np.ndarray,
    lbs_weights_all: np.ndarray,
    joints_xyz_all: np.ndarray,
    output_base_dir: str,
) -> Dict[str, Any]:
    """Evaluate a single candidate configuration across golden set."""
    
    n_frames = verts_all.shape[0]
    results = []
    cfg_hash = cfg_to_hash(cfg)
    
    # Per-frame results
    widths = []
    joint_sws = []
    ratios = []
    landmark_dists_L = []
    landmark_dists_R = []
    fallback_flags = []
    leakage_flags = []
    leakage_reasons = []
    exceptions = []
    
    for frame_idx in range(n_frames):
        verts = verts_all[frame_idx, :, :]
        lbs_weights = lbs_weights_all[frame_idx, :, :]
        joints_xyz = joints_xyz_all[frame_idx, :, :]
        
        frame_result = {
            "frame_id": frame_idx + 1,
            "measured_sw_m": None,
            "joint_sw_m": None,
            "ratio": None,
            "landmark_L_dist_m": None,
            "landmark_R_dist_m": None,
            "fallback": None,
            "leakage": None,
            "leakage_reason": None,
            "exception": None,
        }
        
        try:
            # Run measurement with debug
            width, debug_info = measure_shoulder_width_v112(
                verts=verts,
                lbs_weights=lbs_weights,
                joints_xyz=joints_xyz,
                joint_ids=SMPLX_JOINT_IDS,
                cfg=cfg,
                return_debug=True,
            )
            
            # Compute joint-based SW
            shoulder_L = joints_xyz[SMPLX_JOINT_IDS["L_shoulder"], :]
            shoulder_R = joints_xyz[SMPLX_JOINT_IDS["R_shoulder"], :]
            joint_sw = float(np.linalg.norm(shoulder_L - shoulder_R))
            
            landmark_L = debug_info["landmark_L"]
            landmark_R = debug_info["landmark_R"]
            
            dist_L = float(np.linalg.norm(landmark_L - shoulder_L))
            dist_R = float(np.linalg.norm(landmark_R - shoulder_R))
            ratio = width / joint_sw if joint_sw > 0 else None
            
            fallback = bool(debug_info["fallback"][0])
            
            # Detect leakage
            is_leakage, leakage_reason = detect_upper_arm_leakage(
                landmark_L, landmark_R, shoulder_L, shoulder_R, width, joint_sw
            )
            
            frame_result.update({
                "measured_sw_m": float(width),
                "joint_sw_m": joint_sw,
                "ratio": ratio,
                "landmark_L_dist_m": dist_L,
                "landmark_R_dist_m": dist_R,
                "fallback": fallback,
                "leakage": is_leakage,
                "leakage_reason": leakage_reason if is_leakage else "",
            })
            
            widths.append(width)
            joint_sws.append(joint_sw)
            if ratio is not None:
                ratios.append(ratio)
            landmark_dists_L.append(dist_L)
            landmark_dists_R.append(dist_R)
            fallback_flags.append(fallback)
            leakage_flags.append(is_leakage)
            leakage_reasons.append(leakage_reason if is_leakage else "")
            exceptions.append(None)
            
        except Exception as e:
            frame_result["exception"] = f"{type(e).__name__}: {str(e)}"
            exceptions.append(frame_result["exception"])
            widths.append(np.nan)
            joint_sws.append(np.nan)
            leakage_flags.append(False)  # Exception is separate from leakage
            fallback_flags.append(False)
            leakage_reasons.append("")
        
        results.append(frame_result)
    
    # Aggregate statistics
    widths_arr = np.array(widths)
    joint_sws_arr = np.array(joint_sws)
    ratios_arr = np.array(ratios) if len(ratios) > 0 else np.array([])
    
    valid_mask = np.isfinite(widths_arr)
    n_valid = int(np.sum(valid_mask))
    n_failures = n_frames - n_valid
    
    n_fallback = int(np.sum(fallback_flags))
    n_leakage = int(np.sum(leakage_flags))
    
    # Regression statistics (only for valid cases)
    if n_valid > 0:
        widths_valid = widths_arr[valid_mask]
        joint_sws_valid = joint_sws_arr[valid_mask]
        ratios_valid = ratios_arr[ratios_arr > 0] if len(ratios_arr) > 0 else np.array([])
        
        mean_sw = float(np.mean(widths_valid))
        std_sw = float(np.std(widths_valid))
        max_sw = float(np.max(widths_valid))
        min_sw = float(np.min(widths_valid))
        
        mean_ratio = float(np.mean(ratios_valid)) if len(ratios_valid) > 0 else None
        std_ratio = float(np.std(ratios_valid)) if len(ratios_valid) > 0 else None
        max_ratio = float(np.max(ratios_valid)) if len(ratios_valid) > 0 else None
        
        max_deviation = max(abs(max_sw - mean_sw), abs(min_sw - mean_sw))
    else:
        mean_sw = None
        std_sw = None
        max_sw = None
        min_sw = None
        mean_ratio = None
        std_ratio = None
        max_ratio = None
        max_deviation = None
    
    # Semantic validity gate
    semantic_valid = (n_failures == 0 and n_fallback == 0 and n_leakage == 0)
    validity_reasons = []
    if n_failures > 0:
        validity_reasons.append(f"exceptions={n_failures}")
    if n_fallback > 0:
        validity_reasons.append(f"fallbacks={n_fallback}")
    if n_leakage > 0:
        validity_reasons.append(f"leakage_cases={n_leakage}")
    
    validity_reason = "; ".join(validity_reasons) if len(validity_reasons) > 0 else "PASS"
    
    # Save per-frame results
    # Remove "candidate_" prefix if already present to avoid duplication
    dir_name = candidate_id if not candidate_id.startswith("candidate_") else candidate_id.replace("candidate_", "", 1)
    candidate_dir = os.path.join(output_base_dir, dir_name)
    os.makedirs(candidate_dir, exist_ok=True)
    
    # Save detailed results
    df_results = pd.DataFrame(results)
    df_results.to_csv(
        os.path.join(candidate_dir, "per_frame_results.csv"),
        index=False,
        encoding="utf-8-sig"
    )
    
    # Save worst-case and best-case examples
    if len(leakage_flags) > 0:
        leakage_indices = [i for i, f in enumerate(leakage_flags) if f]
        pass_indices = [i for i, f in enumerate(leakage_flags) if not f and exceptions[i] is None]
        
        # Save worst leakage case (if any)
        if len(leakage_indices) > 0:
            worst_idx = max(leakage_indices, key=lambda i: ratios[i] if ratios[i] is not None else 0)
            worst_case = results[worst_idx]
            with open(
                os.path.join(candidate_dir, "worst_leakage_case.json"),
                "w",
                encoding="utf-8"
            ) as f:
                json.dump({
                    "frame_id": worst_idx + 1,
                    "config": {
                        "r0_ratio": float(cfg.r0_ratio),
                        "r1_ratio": float(cfg.r1_ratio),
                        "cap_quantile": float(cfg.cap_quantile),
                    },
                    **worst_case,
                }, f, indent=2)
        
        # Save best pass case (if any)
        if len(pass_indices) > 0:
            best_idx = pass_indices[0]  # Use first pass case
            best_case = results[best_idx]
            with open(
                os.path.join(candidate_dir, "best_pass_case.json"),
                "w",
                encoding="utf-8"
            ) as f:
                json.dump({
                    "frame_id": best_idx + 1,
                    "config": {
                        "r0_ratio": float(cfg.r0_ratio),
                        "r1_ratio": float(cfg.r1_ratio),
                        "cap_quantile": float(cfg.cap_quantile),
                    },
                    **best_case,
                }, f, indent=2)
    
    # Return summary
    return {
        "candidate_id": candidate_id,
        "config": {
            "r0_ratio": float(cfg.r0_ratio),
            "r1_ratio": float(cfg.r1_ratio),
            "cap_quantile": float(cfg.cap_quantile),
            "distal_w_threshold": float(cfg.distal_w_threshold),
            "s_min_ratio": float(cfg.s_min_ratio),
            "s_max_ratio": float(cfg.s_max_ratio),
            "min_cap_points": int(cfg.min_cap_points),
        },
        "cfg_hash": cfg_hash,
        "semantic_valid": semantic_valid,
        "validity_reason": validity_reason,
        "n_total": n_frames,
        "n_valid": n_valid,
        "n_failures": n_failures,
        "n_fallback": n_fallback,
        "n_leakage": n_leakage,
        "regression": {
            "mean_sw_m": mean_sw,
            "std_sw_m": std_sw,
            "min_sw_m": min_sw,
            "max_sw_m": max_sw,
            "max_deviation_m": max_deviation,
            "mean_ratio": mean_ratio,
            "std_ratio": std_ratio,
            "max_ratio": max_ratio,
        },
        "leakage_details": {
            "leakage_cases": [i + 1 for i, f in enumerate(leakage_flags) if f],
            "top_3_leakage_reasons": sorted(
                set(leakage_reasons),
                key=lambda x: leakage_reasons.count(x),
                reverse=True
            )[:3] if len(set(leakage_reasons)) > 0 else [],
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Shoulder Width v1.1.3 Candidate Parameter Sweep"
    )
    parser.add_argument(
        "--npz",
        type=str,
        required=True,
        help="Path to golden set NPZ file",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="Output directory (default: artifacts/shoulder_width/v1.1.3/sweep_YYYYMMDD)",
    )
    parser.add_argument(
        "--configs",
        type=str,
        default=None,
        help="JSON file with candidate configs (if not provided, uses default sweep)",
    )
    args = parser.parse_args()
    
    # Setup output directory
    if args.out_dir is None:
        date_str = datetime.now().strftime("%Y%m%d")
        args.out_dir = f"artifacts/shoulder_width/v1.1.3/sweep_{date_str}"
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Shoulder Width v1.1.3 Candidate Parameter Sweep")
    print("=" * 80)
    print(f"Golden set: {args.npz}")
    print(f"Output dir: {args.out_dir}")
    print()
    
    # Load golden set
    if not os.path.exists(args.npz):
        raise FileNotFoundError(f"Golden set NPZ not found: {args.npz}")
    
    data = np.load(args.npz, allow_pickle=False)
    verts_all = data["verts"]  # (T, N, 3) or (N, 3)
    lbs_weights_all = data["lbs_weights"]  # (T, N, J) or (N, J)
    joints_xyz_all = data["joints_xyz"]  # (T, J, 3) or (J, 3)
    
    # Ensure batched
    if verts_all.ndim == 2:
        verts_all = verts_all[None, ...]
    if lbs_weights_all.ndim == 2:
        lbs_weights_all = lbs_weights_all[None, ...]
    if joints_xyz_all.ndim == 2:
        joints_xyz_all = joints_xyz_all[None, ...]
    
    n_frames = verts_all.shape[0]
    print(f"Loaded {n_frames} frames from golden set")
    print()
    
    # Load candidate configs
    if args.configs and os.path.exists(args.configs):
        with open(args.configs, "r", encoding="utf-8") as f:
            configs_data = json.load(f)
        candidate_configs = []
        for i, cfg_dict in enumerate(configs_data["candidates"]):
            candidate_configs.append({
                "id": cfg_dict.get("id", f"candidate_{i+1:03d}"),
                "config": ShoulderWidthV112Config(**cfg_dict["config"]),
            })
    else:
        # Default parameter sweep
        print("Using default parameter sweep (no --configs provided)")
        print()
        candidate_configs = []
        candidate_id = 1
        
        # Sweep r0_ratio and r1_ratio (reduced from v1.1.2 to reduce leakage)
        for r0_ratio in [0.20, 0.22, 0.24, 0.26]:
            for r1_ratio in [0.14, 0.16, 0.18]:
                for cap_quantile in [0.92, 0.94, 0.96]:
                    candidate_configs.append({
                        "id": f"candidate_{candidate_id:03d}",
                        "config": ShoulderWidthV112Config(
                            r0_ratio=r0_ratio,
                            r1_ratio=r1_ratio,
                            cap_quantile=cap_quantile,
                        ),
                    })
                    candidate_id += 1
    
    print(f"Evaluating {len(candidate_configs)} candidate configurations")
    print("-" * 80)
    
    # Evaluate each candidate
    all_results = []
    wiring_proofs = {}
    
    for candidate in candidate_configs:
        candidate_id = candidate["id"]
        cfg = candidate["config"]
        
        print(f"Evaluating {candidate_id}... ", end="", flush=True)
        
        result = evaluate_candidate_config(
            candidate_id=candidate_id,
            cfg=cfg,
            verts_all=verts_all,
            lbs_weights_all=lbs_weights_all,
            joints_xyz_all=joints_xyz_all,
            output_base_dir=args.out_dir,
        )
        
        all_results.append(result)
        wiring_proofs[candidate_id] = {
            "runtime_cfg": result["config"],
            "cfg_hash": result["cfg_hash"],
        }
        
        status = "PASS" if result["semantic_valid"] else "FAIL"
        print(f"{status} ({result['validity_reason']})")
    
    print("-" * 80)
    print()
    
    # Save wiring proof
    wiring_proof_path = os.path.join(args.out_dir, "wiring_proof.json")
    with open(wiring_proof_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "wiring_proofs": wiring_proofs,
            "note": "Each candidate's runtime cfg and hash are recorded for policy-to-run verification",
        }, f, indent=2)
    print(f"Wiring proof: {wiring_proof_path}")
    
    # Save summary CSV
    df_summary = pd.DataFrame(all_results)
    csv_path = os.path.join(args.out_dir, "sweep_results.csv")
    df_summary.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Results CSV: {csv_path}")
    
    # Save summary JSON
    summary = {
        "timestamp": datetime.now().isoformat(),
        "golden_set": args.npz,
        "n_frames": n_frames,
        "n_candidates": len(candidate_configs),
        "semantic_validity_thresholds": {
            "ratio_max": RATIO_MAX,
            "landmark_dist_max_m": LANDMARK_DIST_MAX,
        },
        "results": all_results,
        "rankings": {
            "by_validity": sorted(
                all_results,
                key=lambda x: (x["semantic_valid"], -x.get("n_leakage", 999)),
                reverse=True
            )[:10],
            "by_stability": sorted(
                [r for r in all_results if r["regression"]["std_sw_m"] is not None],
                key=lambda x: x["regression"]["std_sw_m"]
            )[:10],
            "by_max_ratio": sorted(
                [r for r in all_results if r["regression"]["max_ratio"] is not None],
                key=lambda x: x["regression"]["max_ratio"]
            )[:10],
        },
        "failure_analysis": {
            "top_failure_reasons": sorted(
                set(r["validity_reason"] for r in all_results if not r["semantic_valid"]),
                key=lambda x: sum(1 for r in all_results if r["validity_reason"] == x),
                reverse=True
            )[:5],
        },
    }
    
    summary_path = os.path.join(args.out_dir, "sweep_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON: {summary_path}")
    print()
    
    # Print console summary
    print("=" * 80)
    print("Console Summary")
    print("=" * 80)
    print()
    print("Top 5 Candidates (by Validity + Stability):")
    print("-" * 80)
    valid_results = [r for r in all_results if r["semantic_valid"]]
    if len(valid_results) > 0:
        valid_sorted = sorted(
            valid_results,
            key=lambda x: x["regression"]["std_sw_m"] if x["regression"]["std_sw_m"] is not None else 999.0
        )[:5]
        for i, r in enumerate(valid_sorted, 1):
            print(f"{i}. {r['candidate_id']}: r0={r['config']['r0_ratio']:.2f}, "
                  f"r1={r['config']['r1_ratio']:.2f}, cap={r['config']['cap_quantile']:.2f}")
            print(f"   std={r['regression']['std_sw_m']:.6f}m, "
                  f"max_ratio={r['regression']['max_ratio']:.3f}")
    else:
        print("No valid candidates found.")
    print()
    
    print("Top 5 Failure Reasons:")
    print("-" * 80)
    failure_reasons = {}
    for r in all_results:
        if not r["semantic_valid"]:
            reason = r["validity_reason"]
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
    
    for i, (reason, count) in enumerate(
        sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5],
        1
    ):
        print(f"{i}. {reason}: {count} candidates")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
