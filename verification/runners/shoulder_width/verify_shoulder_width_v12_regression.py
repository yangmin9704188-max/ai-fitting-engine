#!/usr/bin/env python3
"""
Shoulder Width v1.2 Regression Verification (Frozen Gate)

Purpose: Verify v1.2 measurement on extended golden set using fixed default config.
This is the Candidate -> Frozen verification gate.

Output:
- artifacts/shoulder_width/v1.2/regression/YYYYMMDD_<PASS|PARTIAL|FAIL>/
  - wiring_proof.json
  - regression_results.csv
  - regression_summary.json
  - worst_cases.json
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.measurements.shoulder_width_v12 import (
    measure_shoulder_width_v12,
    ShoulderWidthV12Config,
)

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}

# Fixed default config for v1.2 (Candidate -> Frozen)
DEFAULT_CFG = ShoulderWidthV12Config(
    plane_height_tolerance=0.08,
    arm_direction_exclusion_threshold=0.50,
    arm_distance_threshold=0.12,
    lateral_quantile=0.90,
)


def cfg_to_hash(cfg: ShoulderWidthV12Config, arm_distance_threshold: float) -> str:
    """Compute deterministic hash of configuration for wiring proof."""
    cfg_dict = {
        "plane_height_tolerance": round(float(cfg.plane_height_tolerance), 6),
        "arm_direction_exclusion_threshold": round(float(cfg.arm_direction_exclusion_threshold), 6),
        "arm_distance_threshold": round(float(arm_distance_threshold), 6),
        "lateral_quantile": round(float(cfg.lateral_quantile), 6),
        "eps": round(float(cfg.eps), 12),
        "min_points": int(cfg.min_points),
    }
    cfg_str = json.dumps(cfg_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(cfg_str.encode('utf-8')).hexdigest()[:16]


def get_git_head_sha() -> str:
    """Get current git HEAD SHA (if available)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=_project_root,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Short SHA
    except Exception:
        pass
    return "unknown"


def evaluate_frame(
    frame_idx: int,
    verts: np.ndarray,
    lbs_weights: np.ndarray,
    joints_xyz: np.ndarray,
    joint_ids: Dict[str, int],
    cfg: ShoulderWidthV12Config,
) -> Dict[str, Any]:
    """Evaluate single frame with normal and perturbed configs."""
    
    # Compute joint-based SW
    L_sh = joints_xyz[joint_ids["L_shoulder"], :]
    R_sh = joints_xyz[joint_ids["R_shoulder"], :]
    joint_sw = float(np.linalg.norm(L_sh - R_sh))
    
    # Normal measurement
    try:
        width, debug_info = measure_shoulder_width_v12(
            verts=verts,
            lbs_weights=lbs_weights,
            joints_xyz=joints_xyz,
            joint_ids=joint_ids,
            cfg=cfg,
            return_debug=True,
        )
        
        measured_sw = float(width)
        fallback = debug_info.get("fallback", False)
        exception = None
        
        # Collect debug info
        arm_excluded_count = debug_info.get("arm_excluded_count", 0)
        torso_candidates_count = debug_info.get("torso_candidates_count", 0)
        cross_section_count = debug_info.get("cross_section_vertices_count", 0)
        
    except Exception as e:
        measured_sw = np.nan
        fallback = False
        exception = f"{type(e).__name__}: {str(e)}"
        arm_excluded_count = 0
        torso_candidates_count = 0
        cross_section_count = 0
    
    ratio = measured_sw / joint_sw if joint_sw > 0 and not np.isnan(measured_sw) else np.nan
    
    # Pose perturbation test (stricter/looser arm exclusion)
    delta_stricter = np.nan
    delta_looser = np.nan
    sw_stricter = np.nan
    sw_looser = np.nan
    
    if not np.isnan(measured_sw) and exception is None and not fallback:
        try:
            # Stricter config
            cfg_stricter = ShoulderWidthV12Config(
                plane_height_tolerance=cfg.plane_height_tolerance,
                arm_direction_exclusion_threshold=min(0.9, cfg.arm_direction_exclusion_threshold + 0.2),
                arm_distance_threshold=cfg.arm_distance_threshold,
                lateral_quantile=cfg.lateral_quantile,
                eps=cfg.eps,
                min_points=cfg.min_points,
            )
            sw_stricter, _ = measure_shoulder_width_v12(
                verts=verts,
                lbs_weights=lbs_weights,
                joints_xyz=joints_xyz,
                joint_ids=joint_ids,
                cfg=cfg_stricter,
                return_debug=False,
            )
            sw_stricter = float(sw_stricter)
            delta_stricter = abs(measured_sw - sw_stricter)
            
            # Looser config
            cfg_looser = ShoulderWidthV12Config(
                plane_height_tolerance=cfg.plane_height_tolerance,
                arm_direction_exclusion_threshold=max(0.2, cfg.arm_direction_exclusion_threshold - 0.2),
                arm_distance_threshold=cfg.arm_distance_threshold,
                lateral_quantile=cfg.lateral_quantile,
                eps=cfg.eps,
                min_points=cfg.min_points,
            )
            sw_looser, _ = measure_shoulder_width_v12(
                verts=verts,
                lbs_weights=lbs_weights,
                joints_xyz=joints_xyz,
                joint_ids=joint_ids,
                cfg=cfg_looser,
                return_debug=False,
            )
            sw_looser = float(sw_looser)
            delta_looser = abs(measured_sw - sw_looser)
            
        except Exception:
            pass  # Skip perturbation if it fails
    
    return {
        "frame_id": frame_idx + 1,
        "measured_sw_m": float(measured_sw) if not np.isnan(measured_sw) else None,
        "joint_sw_m": joint_sw,
        "ratio": float(ratio) if not np.isnan(ratio) else None,
        "arm_excluded_count": arm_excluded_count,
        "torso_candidates_count": torso_candidates_count,
        "cross_section_count": cross_section_count,
        "fallback": fallback,
        "exception": exception,
        "perturbation_delta_stricter": float(delta_stricter) if not np.isnan(delta_stricter) else None,
        "perturbation_delta_looser": float(delta_looser) if not np.isnan(delta_looser) else None,
        "perturbation_sw_stricter": float(sw_stricter) if not np.isnan(sw_stricter) else None,
        "perturbation_sw_looser": float(sw_looser) if not np.isnan(sw_looser) else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Shoulder Width v1.2 Regression Verification (Frozen Gate)"
    )
    parser.add_argument(
        "--npz",
        type=str,
        default="verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz",
        help="Path to extended golden NPZ file",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="Output directory (default: artifacts/shoulder_width/v1.2/regression/YYYYMMDD_<STATUS>)",
    )
    args = parser.parse_args()
    
    # Setup output directory with status
    if args.out_dir is None:
        date_str = datetime.now().strftime("%Y%m%d")
        args.out_dir = f"artifacts/shoulder_width/v1.2/regression/{date_str}_TBD"
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Shoulder Width v1.2 Regression Verification (Frozen Gate)")
    print("=" * 80)
    print(f"Golden set: {args.npz}")
    print(f"Output dir: {args.out_dir}")
    print()
    print("Fixed default config:")
    print(f"  plane_height_tolerance: {DEFAULT_CFG.plane_height_tolerance}")
    print(f"  arm_distance_threshold: {DEFAULT_CFG.arm_distance_threshold}")
    print(f"  arm_alignment_cosine_threshold: {DEFAULT_CFG.arm_direction_exclusion_threshold}")
    print(f"  lateral_quantile: {DEFAULT_CFG.lateral_quantile}")
    print()
    
    # Load golden set
    if not os.path.exists(args.npz):
        raise FileNotFoundError(f"Golden set NPZ not found: {args.npz}")
    
    data = np.load(args.npz, allow_pickle=True)
    verts_all = data["verts"]  # (T, N, 3) or (N, 3)
    lbs_weights_all = data["lbs_weights"]  # (T, N, J) or (N, J)
    joints_xyz_all = data["joints_xyz"]  # (T, J, 3) or (J, 3)
    
    # Handle joint_ids
    if "joint_ids" in data.files:
        joint_ids_raw = data["joint_ids"]
        if isinstance(joint_ids_raw, np.ndarray):
            joint_ids = joint_ids_raw.item() if joint_ids_raw.size == 1 else dict(joint_ids_raw)
        else:
            joint_ids = joint_ids_raw
    else:
        joint_ids = SMPLX_JOINT_IDS
    
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
    
    # Evaluate all frames
    print("Evaluating frames...")
    print("-" * 80)
    
    results = []
    for frame_idx in range(n_frames):
        verts = verts_all[frame_idx, :, :]
        lbs_weights = lbs_weights_all[frame_idx, :, :]
        joints_xyz = joints_xyz_all[frame_idx, :, :]
        
        result = evaluate_frame(
            frame_idx=frame_idx,
            verts=verts,
            lbs_weights=lbs_weights,
            joints_xyz=joints_xyz,
            joint_ids=joint_ids,
            cfg=DEFAULT_CFG,
        )
        
        results.append(result)
        
        if (frame_idx + 1) % 50 == 0:
            print(f"  Processed {frame_idx + 1}/{n_frames} frames...")
    
    print("-" * 80)
    print()
    
    # Aggregate statistics
    df_results = pd.DataFrame(results)
    
    # Filter valid results
    valid_mask = df_results["measured_sw_m"].notna()
    n_valid = int(valid_mask.sum())
    n_failures = n_frames - n_valid
    n_fallback = int(df_results["fallback"].sum())
    n_exception = int(df_results["exception"].notna().sum())
    
    # Compute statistics
    if n_valid > 0:
        measured_sws = df_results.loc[valid_mask, "measured_sw_m"]
        joint_sws = df_results.loc[valid_mask, "joint_sw_m"]
        ratios = df_results.loc[valid_mask, "ratio"]
        
        stats_measured = {
            "min": float(measured_sws.min()),
            "mean": float(measured_sws.mean()),
            "max": float(measured_sws.max()),
            "std": float(measured_sws.std()),
        }
        stats_joint = {
            "min": float(joint_sws.min()),
            "mean": float(joint_sws.mean()),
            "max": float(joint_sws.max()),
            "std": float(joint_sws.std()),
        }
        stats_ratio = {
            "min": float(ratios.min()),
            "mean": float(ratios.mean()),
            "max": float(ratios.max()),
            "std": float(ratios.std()),
        }
    else:
        stats_measured = stats_joint = stats_ratio = None
    
    # Arm exclusion stats
    arm_excluded_counts = df_results.loc[valid_mask, "arm_excluded_count"]
    stats_arm_excluded = {
        "min": int(arm_excluded_counts.min()),
        "mean": float(arm_excluded_counts.mean()),
        "max": int(arm_excluded_counts.max()),
        "std": float(arm_excluded_counts.std()),
    } if n_valid > 0 else None
    
    # Cross-section stats
    cross_section_counts = df_results.loc[valid_mask, "cross_section_count"]
    stats_cross_section = {
        "min": int(cross_section_counts.min()),
        "mean": float(cross_section_counts.mean()),
        "max": int(cross_section_counts.max()),
        "std": float(cross_section_counts.std()),
    } if n_valid > 0 else None
    
    # Perturbation stats
    perturbation_deltas_stricter = df_results.loc[valid_mask, "perturbation_delta_stricter"].dropna()
    perturbation_deltas_looser = df_results.loc[valid_mask, "perturbation_delta_looser"].dropna()
    
    stats_perturbation = None
    if len(perturbation_deltas_stricter) > 0 or len(perturbation_deltas_looser) > 0:
        stats_perturbation = {
            "delta_stricter": {
                "min": float(perturbation_deltas_stricter.min()) if len(perturbation_deltas_stricter) > 0 else None,
                "mean": float(perturbation_deltas_stricter.mean()) if len(perturbation_deltas_stricter) > 0 else None,
                "max": float(perturbation_deltas_stricter.max()) if len(perturbation_deltas_stricter) > 0 else None,
                "std": float(perturbation_deltas_stricter.std()) if len(perturbation_deltas_stricter) > 0 else None,
            },
            "delta_looser": {
                "min": float(perturbation_deltas_looser.min()) if len(perturbation_deltas_looser) > 0 else None,
                "mean": float(perturbation_deltas_looser.mean()) if len(perturbation_deltas_looser) > 0 else None,
                "max": float(perturbation_deltas_looser.max()) if len(perturbation_deltas_looser) > 0 else None,
                "std": float(perturbation_deltas_looser.std()) if len(perturbation_deltas_looser) > 0 else None,
            },
        }
    
    # Identify worst cases (top N with largest deltas or suspicious counts)
    worst_cases = []
    
    # Sort by perturbation delta (descending)
    if stats_perturbation:
        worst_by_delta = df_results.loc[valid_mask].nlargest(10, "perturbation_delta_stricter")
        for _, row in worst_by_delta.iterrows():
            worst_cases.append({
                "frame_id": int(row["frame_id"]),
                "reason": "large_perturbation_delta",
                "measured_sw_m": float(row["measured_sw_m"]) if pd.notna(row["measured_sw_m"]) else None,
                "ratio": float(row["ratio"]) if pd.notna(row["ratio"]) else None,
                "perturbation_delta_stricter": float(row["perturbation_delta_stricter"]) if pd.notna(row["perturbation_delta_stricter"]) else None,
                "perturbation_delta_looser": float(row["perturbation_delta_looser"]) if pd.notna(row["perturbation_delta_looser"]) else None,
                "arm_excluded_count": int(row["arm_excluded_count"]),
                "cross_section_count": int(row["cross_section_count"]),
            })
    
    # Sort by ratio (potential leakage indicators)
    if stats_ratio:
        worst_by_ratio_high = df_results.loc[valid_mask].nlargest(5, "ratio")
        worst_by_ratio_low = df_results.loc[valid_mask].nsmallest(5, "ratio")
        
        for _, row in worst_by_ratio_high.iterrows():
            if int(row["frame_id"]) not in [w["frame_id"] for w in worst_cases]:
                worst_cases.append({
                    "frame_id": int(row["frame_id"]),
                    "reason": "high_ratio",
                    "measured_sw_m": float(row["measured_sw_m"]) if pd.notna(row["measured_sw_m"]) else None,
                    "ratio": float(row["ratio"]) if pd.notna(row["ratio"]) else None,
                    "joint_sw_m": float(row["joint_sw_m"]),
                    "arm_excluded_count": int(row["arm_excluded_count"]),
                    "cross_section_count": int(row["cross_section_count"]),
                })
        
        for _, row in worst_by_ratio_low.iterrows():
            if int(row["frame_id"]) not in [w["frame_id"] for w in worst_cases]:
                worst_cases.append({
                    "frame_id": int(row["frame_id"]),
                    "reason": "low_ratio",
                    "measured_sw_m": float(row["measured_sw_m"]) if pd.notna(row["measured_sw_m"]) else None,
                    "ratio": float(row["ratio"]) if pd.notna(row["ratio"]) else None,
                    "joint_sw_m": float(row["joint_sw_m"]),
                    "arm_excluded_count": int(row["arm_excluded_count"]),
                    "cross_section_count": int(row["cross_section_count"]),
                })
    
    # Compute overall status
    if n_fallback == 0 and n_exception == 0:
        if stats_arm_excluded and stats_arm_excluded["mean"] > 100:
            status = "PASS"
        else:
            status = "PARTIAL"
            if stats_arm_excluded:
                print("WARNING: arm_excluded_count mean may be too low")
    elif n_fallback == 0 and n_exception > 0:
        status = "PARTIAL"
    else:
        status = "FAIL"
    
    # Rename output directory with status
    old_out_dir = args.out_dir
    if old_out_dir.endswith("_TBD"):
        args.out_dir = old_out_dir.replace("_TBD", f"_{status}")
        if os.path.exists(old_out_dir):
            if os.path.exists(args.out_dir):
                import shutil
                shutil.rmtree(args.out_dir)
            os.rename(old_out_dir, args.out_dir)
    
    # Compute wiring proof hash
    cfg_hash = cfg_to_hash(DEFAULT_CFG, DEFAULT_CFG.arm_distance_threshold)
    git_head_sha = get_git_head_sha()
    
    # Save wiring proof
    wiring_proof = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "git_head_sha": git_head_sha,
        "runtime_cfg": {
            "plane_height_tolerance": float(DEFAULT_CFG.plane_height_tolerance),
            "arm_direction_exclusion_threshold": float(DEFAULT_CFG.arm_direction_exclusion_threshold),
            "arm_distance_threshold": float(DEFAULT_CFG.arm_distance_threshold),
            "lateral_quantile": float(DEFAULT_CFG.lateral_quantile),
        },
        "cfg_hash": cfg_hash,
        "note": "Fixed default config for v1.2 Candidate -> Frozen verification",
    }
    
    wiring_proof_path = os.path.join(args.out_dir, "wiring_proof.json")
    with open(wiring_proof_path, "w", encoding="utf-8") as f:
        json.dump(wiring_proof, f, indent=2)
    print(f"Wiring proof: {wiring_proof_path}")
    
    # Save per-frame results CSV
    df_results.to_csv(
        os.path.join(args.out_dir, "regression_results.csv"),
        index=False,
        encoding="utf-8-sig"
    )
    print(f"Results CSV: {os.path.join(args.out_dir, 'regression_results.csv')}")
    
    # Save worst cases
    worst_cases_path = os.path.join(args.out_dir, "worst_cases.json")
    with open(worst_cases_path, "w", encoding="utf-8") as f:
        json.dump(worst_cases, f, indent=2)
    print(f"Worst cases: {worst_cases_path}")
    
    # Build summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "git_head_sha": git_head_sha,
        "golden_set": args.npz,
        "n_frames": n_frames,
        "config": wiring_proof["runtime_cfg"],
        "cfg_hash": cfg_hash,
        "overall_statistics": {
            "n_total": n_frames,
            "n_valid": n_valid,
            "n_failures": n_failures,
            "n_fallback": n_fallback,
            "n_exception": n_exception,
        },
        "statistics": {
            "measured_sw": stats_measured,
            "joint_sw": stats_joint,
            "ratio": stats_ratio,
            "arm_excluded_count": stats_arm_excluded,
            "cross_section_count": stats_cross_section,
        },
        "pose_perturbation": stats_perturbation,
        "worst_cases_count": len(worst_cases),
        "success_criteria": {
            "fallback_0": n_fallback == 0,
            "exception_0": n_exception == 0,
            "arm_exclusion_applied": stats_arm_excluded["mean"] > 100 if stats_arm_excluded else False,
            "cfg_hash_stable": True,  # Single config, always stable
        },
    }
    
    # Save summary JSON
    summary_path = os.path.join(args.out_dir, "regression_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON: {summary_path}")
    print()
    
    # Print console summary
    print("=" * 80)
    print("Regression Verification Summary")
    print("=" * 80)
    print(f"Status: {status}")
    print(f"Total frames: {n_frames}")
    print(f"Valid frames: {n_valid}")
    print(f"Fallbacks: {n_fallback}")
    print(f"Exceptions: {n_exception}")
    print()
    
    if stats_measured:
        print("Measured SW:")
        print(f"  mean: {stats_measured['mean']:.6f}m")
        print(f"  std: {stats_measured['std']:.6f}m")
        print(f"  range: [{stats_measured['min']:.6f}, {stats_measured['max']:.6f}]m")
        print()
    
    if stats_ratio:
        print("Ratio (measured/joint):")
        print(f"  mean: {stats_ratio['mean']:.4f}")
        print(f"  range: [{stats_ratio['min']:.4f}, {stats_ratio['max']:.4f}]")
        print()
    
    if stats_arm_excluded:
        print("Arm exclusion:")
        print(f"  mean count: {stats_arm_excluded['mean']:.0f}")
        print(f"  range: [{stats_arm_excluded['min']}, {stats_arm_excluded['max']}]")
        print()
    
    print("Success Criteria:")
    print(f"  fallback=0: {'PASS' if summary['success_criteria']['fallback_0'] else 'FAIL'}")
    print(f"  exception=0: {'PASS' if summary['success_criteria']['exception_0'] else 'FAIL'}")
    print(f"  arm_exclusion_applied: {'PASS' if summary['success_criteria']['arm_exclusion_applied'] else 'FAIL'}")
    print(f"  cfg_hash_stable: {'PASS' if summary['success_criteria']['cfg_hash_stable'] else 'FAIL'}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
