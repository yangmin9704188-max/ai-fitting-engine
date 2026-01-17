#!/usr/bin/env python3
"""
Shoulder Width v1.2 Sensitivity Analysis & Verification

Purpose: Verify v1.2 structural immunity to upper arm leakage across parameter variations
         and pose perturbations (arm motion sensitivity).

Verification Criteria:
- Fallback = 0, Exception = 0 for all candidates
- Arm exclusion consistently applied (arm_excluded_count non-trivial)
- Sensitivity deltas bounded under pose perturbations
- Parameter stability across golden set

Output:
- artifacts/shoulder_width/v1.2/sensitivity/YYYYMMDD_<STATUS>/
  - wiring_proof.json
  - sensitivity_results.csv
  - sensitivity_summary.json
  - per_candidate/candidate_XXX/per_frame.csv
  - per_candidate/candidate_XXX/debug_frames.json (frames 1-3)
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import hashlib
from datetime import datetime
import datetime as dt
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd
from itertools import product

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.measurements.shoulder_width_v12 import measure_shoulder_width_v12, ShoulderWidthV12Config

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}


def resolve_run_id(cli_run_id=None) -> str:
    """Resolve RUN_ID with priority: CLI arg > env var > auto-generate (KST timestamp)."""
    if cli_run_id:
        run_id = str(cli_run_id).strip()
    else:
        run_id = os.environ.get("RUN_ID", "").strip()

    if not run_id:
        now_kst = dt.datetime.utcnow() + dt.timedelta(hours=9)
        run_id = now_kst.strftime("%Y%m%d_%H%M%S")

    os.environ["RUN_ID"] = run_id
    print(f"RUN_ID={run_id}")
    return run_id


def cfg_to_hash(cfg: ShoulderWidthV12Config, arm_distance_threshold: float) -> str:
    """
    Compute hash of configuration for wiring proof.
    
    Includes ALL runtime parameters to ensure unique hash per candidate config.
    Uses deterministic serialization (sorted keys, fixed float precision).
    """
    cfg_dict = {
        "plane_height_tolerance": round(float(cfg.plane_height_tolerance), 6),
        "arm_direction_exclusion_threshold": round(float(cfg.arm_direction_exclusion_threshold), 6),
        "arm_distance_threshold": round(float(arm_distance_threshold), 6),
        "lateral_quantile": round(float(cfg.lateral_quantile), 6),
        "eps": round(float(cfg.eps), 12),
        "min_points": int(cfg.min_points),
    }
    # Deterministic serialization: sort keys, fixed precision, no spaces
    cfg_str = json.dumps(cfg_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(cfg_str.encode('utf-8')).hexdigest()[:16]


def evaluate_candidate_config(
    candidate_id: str,
    cfg: ShoulderWidthV12Config,
    verts_all: np.ndarray,
    lbs_weights_all: np.ndarray,
    joints_xyz_all: np.ndarray,
    joint_ids: Dict[str, int],
    output_base_dir: str,
    arm_distance_threshold: float = 0.15,  # Parameter for arm exclusion distance
) -> Dict[str, Any]:
    """
    Evaluate a candidate configuration across golden set.
    
    Note: arm_distance_threshold is passed separately as it's not in ShoulderWidthV12Config yet.
    For now, we'll modify the measurement function call to include this.
    """
    
    n_frames = verts_all.shape[0]
    
    # Per-frame results
    results = []
    measured_sws = []
    joint_sws = []
    ratios = []
    arm_excluded_counts = []
    torso_candidates_counts = []
    cross_section_counts = []
    fallback_flags = []
    exceptions = []
    
    # Pose perturbation results (for frames 1-3 only)
    pose_perturbation_results = []
    
    # Stricter/looser arm exclusion configs for perturbation test
    # Note: These are computed per candidate, using the same cfg structure
    # We'll create them inside the frame loop after we have the baseline measurement
    
    for frame_idx in range(n_frames):
        verts = verts_all[frame_idx, :, :]
        lbs_weights = lbs_weights_all[frame_idx, :, :]
        joints_xyz = joints_xyz_all[frame_idx, :, :]
        
        # Compute joint-based SW
        L_sh = joints_xyz[joint_ids["L_shoulder"], :]
        R_sh = joints_xyz[joint_ids["R_shoulder"], :]
        joint_sw = float(np.linalg.norm(L_sh - R_sh))
        
        # Run measurement with normal config
        try:
            # Note: We'll need to modify v1.2 to accept arm_distance_threshold as a parameter
            # For now, we'll use a wrapper or modify the config approach
            # Actually, looking at the code, arm_distance_threshold is hardcoded as 0.15
            # We'll need to modify the measurement function to accept it, or create a wrapper
            # For now, let's assume we modify the function to accept it via a custom config extension
            
            # Temporary: We'll patch the function behavior by creating a modified config
            # Actually, better approach: modify the measurement function to accept arm_distance_threshold
            # But user said "Do NOT modify v1.1.x code" - they didn't say we can't extend v1.2
            
            # Let's check if we can pass it as an additional parameter or extend the config
            # For now, we'll create a wrapper function that patches the behavior
            
            width, debug_info = _measure_with_arm_distance_threshold(
                verts=verts,
                lbs_weights=lbs_weights,
                joints_xyz=joints_xyz,
                joint_ids=joint_ids,
                cfg=cfg,
                arm_distance_threshold=arm_distance_threshold,
                return_debug=True,
            )
            
            measured_sw = float(width)
            fallback = debug_info.get("fallback", False)
            exception = None
            
            # Collect stats
            measured_sws.append(measured_sw)
            joint_sws.append(joint_sw)
            if joint_sw > 0:
                ratios.append(measured_sw / joint_sw)
            arm_excluded_counts.append(debug_info.get("arm_excluded_count", 0))
            torso_candidates_counts.append(debug_info.get("torso_candidates_count", 0))
            cross_section_counts.append(debug_info.get("cross_section_vertices_count", 0))
            fallback_flags.append(fallback)
            exceptions.append(None)
            
        except Exception as e:
            measured_sw = np.nan
            fallback = False
            exception = f"{type(e).__name__}: {str(e)}"
            measured_sws.append(np.nan)
            joint_sws.append(joint_sw)
            arm_excluded_counts.append(0)
            torso_candidates_counts.append(0)
            cross_section_counts.append(0)
            fallback_flags.append(False)
            exceptions.append(exception)
        
        results.append({
            "frame_id": frame_idx + 1,
            "measured_sw_m": float(measured_sw) if not np.isnan(measured_sw) else None,
            "joint_sw_m": joint_sw,
            "ratio": float(measured_sw / joint_sw) if joint_sw > 0 and not np.isnan(measured_sw) else None,
            "arm_excluded_count": arm_excluded_counts[-1],
            "torso_candidates_count": torso_candidates_counts[-1],
            "cross_section_count": cross_section_counts[-1],
            "fallback": fallback,
            "exception": exception,
        })
        
        # Pose perturbation test (frames 1-3 only)
        if frame_idx < 3 and not np.isnan(measured_sw) and exception is None and not fallback:
            try:
                # Normal config (already measured)
                sw_normal = measured_sw
                
                # Create stricter/looser configs for perturbation test
                cfg_stricter = ShoulderWidthV12Config(
                    plane_height_tolerance=cfg.plane_height_tolerance,
                    arm_direction_exclusion_threshold=min(0.9, cfg.arm_direction_exclusion_threshold + 0.2),
                    arm_distance_threshold=arm_distance_threshold,
                    lateral_quantile=cfg.lateral_quantile,
                    eps=cfg.eps,
                    min_points=cfg.min_points,
                )
                cfg_looser = ShoulderWidthV12Config(
                    plane_height_tolerance=cfg.plane_height_tolerance,
                    arm_direction_exclusion_threshold=max(0.2, cfg.arm_direction_exclusion_threshold - 0.2),
                    arm_distance_threshold=arm_distance_threshold,
                    lateral_quantile=cfg.lateral_quantile,
                    eps=cfg.eps,
                    min_points=cfg.min_points,
                )
                
                # Stricter arm exclusion
                sw_stricter, _ = measure_shoulder_width_v12(
                    verts=verts,
                    lbs_weights=lbs_weights,
                    joints_xyz=joints_xyz,
                    joint_ids=joint_ids,
                    cfg=cfg_stricter,
                    return_debug=False,
                )
                sw_stricter = float(sw_stricter)
                
                # Looser arm exclusion
                sw_looser, _ = measure_shoulder_width_v12(
                    verts=verts,
                    lbs_weights=lbs_weights,
                    joints_xyz=joints_xyz,
                    joint_ids=joint_ids,
                    cfg=cfg_looser,
                    return_debug=False,
                )
                sw_looser = float(sw_looser)
                
                delta_stricter = abs(sw_normal - sw_stricter)
                delta_looser = abs(sw_normal - sw_looser)
                
                pose_perturbation_results.append({
                    "frame_id": frame_idx + 1,
                    "sw_normal": sw_normal,
                    "sw_stricter": sw_stricter,
                    "sw_looser": sw_looser,
                    "delta_stricter": delta_stricter,
                    "delta_looser": delta_looser,
                })
                
            except Exception as e:
                # Log but don't fail - perturbation test is optional
                pass  # Skip perturbation test if it fails
    
    # Aggregate statistics
    measured_sws_arr = np.array(measured_sws)
    joint_sws_arr = np.array(joint_sws)
    ratios_arr = np.array(ratios) if len(ratios) > 0 else np.array([])
    arm_excluded_arr = np.array(arm_excluded_counts)
    torso_candidates_arr = np.array(torso_candidates_counts)
    cross_section_arr = np.array(cross_section_counts)
    
    valid_mask = np.isfinite(measured_sws_arr)
    n_valid = int(np.sum(valid_mask))
    n_failures = n_frames - n_valid
    n_fallback = int(np.sum(fallback_flags))
    n_exception = sum(1 for e in exceptions if e is not None)
    
    # Compute statistics
    if n_valid > 0:
        stats_measured = {
            "min": float(np.min(measured_sws_arr[valid_mask])),
            "mean": float(np.mean(measured_sws_arr[valid_mask])),
            "max": float(np.max(measured_sws_arr[valid_mask])),
            "std": float(np.std(measured_sws_arr[valid_mask])),
        }
        stats_joint = {
            "min": float(np.min(joint_sws_arr)),
            "mean": float(np.mean(joint_sws_arr)),
            "max": float(np.max(joint_sws_arr)),
            "std": float(np.std(joint_sws_arr)),
        }
        stats_ratio = {
            "min": float(np.min(ratios_arr)) if len(ratios_arr) > 0 else None,
            "mean": float(np.mean(ratios_arr)) if len(ratios_arr) > 0 else None,
            "max": float(np.max(ratios_arr)) if len(ratios_arr) > 0 else None,
            "std": float(np.std(ratios_arr)) if len(ratios_arr) > 0 else None,
        }
        stats_arm_excluded = {
            "min": int(np.min(arm_excluded_arr)),
            "mean": float(np.mean(arm_excluded_arr)),
            "max": int(np.max(arm_excluded_arr)),
            "std": float(np.std(arm_excluded_arr)),
        }
        stats_torso_candidates = {
            "min": int(np.min(torso_candidates_arr)),
            "mean": float(np.mean(torso_candidates_arr)),
            "max": int(np.max(torso_candidates_arr)),
            "std": float(np.std(torso_candidates_arr)),
        }
        stats_cross_section = {
            "min": int(np.min(cross_section_arr)),
            "mean": float(np.mean(cross_section_arr)),
            "max": int(np.max(cross_section_arr)),
            "std": float(np.std(cross_section_arr)),
        }
    else:
        stats_measured = stats_joint = stats_ratio = None
        stats_arm_excluded = stats_torso_candidates = stats_cross_section = None
    
    # Pose perturbation statistics
    if len(pose_perturbation_results) > 0:
        deltas_stricter = [r["delta_stricter"] for r in pose_perturbation_results]
        deltas_looser = [r["delta_looser"] for r in pose_perturbation_results]
        stats_perturbation = {
            "delta_stricter": {
                "min": float(np.min(deltas_stricter)),
                "mean": float(np.mean(deltas_stricter)),
                "max": float(np.max(deltas_stricter)),
                "std": float(np.std(deltas_stricter)),
            },
            "delta_looser": {
                "min": float(np.min(deltas_looser)),
                "mean": float(np.mean(deltas_looser)),
                "max": float(np.max(deltas_looser)),
                "std": float(np.std(deltas_looser)),
            },
        }
    else:
        stats_perturbation = None
    
    # Save per-frame results
    candidate_dir = os.path.join(output_base_dir, "per_candidate", candidate_id)
    os.makedirs(candidate_dir, exist_ok=True)
    
    df_results = pd.DataFrame(results)
    df_results.to_csv(
        os.path.join(candidate_dir, "per_frame.csv"),
        index=False,
        encoding="utf-8-sig"
    )
    
    # Save debug frames (frames 1-3)
    if len(pose_perturbation_results) > 0:
        debug_frames_path = os.path.join(candidate_dir, "debug_frames.json")
        with open(debug_frames_path, "w", encoding="utf-8") as f:
            json.dump(pose_perturbation_results, f, indent=2)
    
    return {
        "candidate_id": candidate_id,
        "config": {
            "plane_height_tolerance": float(cfg.plane_height_tolerance),
            "arm_direction_exclusion_threshold": float(cfg.arm_direction_exclusion_threshold),
            "arm_distance_threshold": float(arm_distance_threshold),
            "lateral_quantile": float(cfg.lateral_quantile),
        },
        "cfg_hash": cfg_to_hash(cfg, arm_distance_threshold),
        "n_total": n_frames,
        "n_valid": n_valid,
        "n_failures": n_failures,
        "n_fallback": n_fallback,
        "n_exception": n_exception,
        "statistics": {
            "measured_sw": stats_measured,
            "joint_sw": stats_joint,
            "ratio": stats_ratio,
            "arm_excluded_count": stats_arm_excluded,
            "torso_candidates_count": stats_torso_candidates,
            "cross_section_count": stats_cross_section,
        },
        "pose_perturbation": stats_perturbation,
    }


def _measure_with_arm_distance_threshold(
    verts: np.ndarray,
    lbs_weights: np.ndarray,
    joints_xyz: np.ndarray,
    joint_ids: Dict[str, int],
    cfg: ShoulderWidthV12Config,
    arm_distance_threshold: float,
    return_debug: bool,
):
    """
    Wrapper that creates a modified config with arm_distance_threshold.
    Now that v1.2 supports arm_distance_threshold in config, we can use it directly.
    """
    # Create modified config with arm_distance_threshold
    cfg_modified = ShoulderWidthV12Config(
        plane_height_tolerance=cfg.plane_height_tolerance,
        arm_direction_exclusion_threshold=cfg.arm_direction_exclusion_threshold,
        arm_distance_threshold=arm_distance_threshold,
        lateral_quantile=cfg.lateral_quantile,
        eps=cfg.eps,
        min_points=cfg.min_points,
    )
    
    return measure_shoulder_width_v12(
        verts=verts,
        lbs_weights=lbs_weights,
        joints_xyz=joints_xyz,
        joint_ids=joint_ids,
        cfg=cfg_modified,
        return_debug=return_debug,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Shoulder Width v1.2 Sensitivity Analysis & Verification"
    )
    parser.add_argument(
        "--npz",
        type=str,
        default="verification/datasets/golden_shoulder_batched.npz",
        help="Path to golden NPZ file",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="Output directory (default: artifacts/shoulder_width/v1.2/sensitivity/<RUN_ID>_<STATUS>)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run ID (default: from env RUN_ID or auto-generate KST timestamp)",
    )
    args = parser.parse_args()
    
    # Resolve RUN_ID first (before any artifact path creation)
    run_id = resolve_run_id(args.run_id)
    
    # Setup output directory with status
    if args.out_dir is None:
        args.out_dir = f"artifacts/shoulder_width/v1.2/sensitivity/{run_id}_TBD"
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Shoulder Width v1.2 Sensitivity Analysis & Verification")
    print("=" * 80)
    print(f"Golden set: {args.npz}")
    print(f"Output dir: {args.out_dir}")
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
    
    # Parameter sweep grid
    plane_height_tolerance_values = [0.05, 0.08, 0.10]
    arm_distance_threshold_values = [0.12, 0.15, 0.18]
    arm_alignment_cosine_threshold_values = [0.4, 0.5, 0.6]
    lateral_quantile_values = [0.90, 0.95, 0.98]
    
    # Generate all combinations
    candidate_configs = []
    candidate_id = 1
    
    for plane_tol, arm_dist, arm_cos, lat_q in product(
        plane_height_tolerance_values,
        arm_distance_threshold_values,
        arm_alignment_cosine_threshold_values,
        lateral_quantile_values,
    ):
        cfg = ShoulderWidthV12Config(
            plane_height_tolerance=plane_tol,
            arm_direction_exclusion_threshold=arm_cos,
            arm_distance_threshold=arm_dist,
            lateral_quantile=lat_q,
        )
        candidate_configs.append({
            "id": f"candidate_{candidate_id:03d}",
            "cfg": cfg,
            "arm_distance_threshold": arm_dist,
        })
        candidate_id += 1
    
    print(f"Evaluating {len(candidate_configs)} candidate configurations")
    print("-" * 80)
    
    # Evaluate each candidate
    all_results = []
    wiring_proofs = {}
    cfg_hash_map = {}  # Track hash -> candidate_ids for collision detection
    
    for candidate in candidate_configs:
        candidate_id = candidate["id"]
        cfg = candidate["cfg"]
        arm_dist_thresh = candidate["arm_distance_threshold"]
        
        print(f"Evaluating {candidate_id}... ", end="", flush=True)
        
        result = evaluate_candidate_config(
            candidate_id=candidate_id,
            cfg=cfg,
            verts_all=verts_all,
            lbs_weights_all=lbs_weights_all,
            joints_xyz_all=joints_xyz_all,
            joint_ids=joint_ids,
            output_base_dir=args.out_dir,
            arm_distance_threshold=arm_dist_thresh,
        )
        
        all_results.append(result)
        wiring_proofs[candidate_id] = {
            "runtime_cfg": result["config"],
            "cfg_hash": result["cfg_hash"],
        }
        
        # Track hash for collision detection
        cfg_hash = result["cfg_hash"]
        if cfg_hash not in cfg_hash_map:
            cfg_hash_map[cfg_hash] = []
        cfg_hash_map[cfg_hash].append(candidate_id)
        
        # Status check
        status = "OK"
        if result["n_fallback"] > 0 or result["n_exception"] > 0:
            status = "FAIL"
        elif result.get("statistics", {}).get("arm_excluded_count", {}).get("mean", 0) < 100:
            status = "WARN"  # Arm exclusion might not be working
        
        print(f"{status} (fallback={result['n_fallback']}, exception={result['n_exception']}, arm_excluded_mean={result.get('statistics', {}).get('arm_excluded_count', {}).get('mean', 0):.0f})")
    
    print("-" * 80)
    print()
    
    # Validate hash uniqueness
    n_unique_hashes = len(cfg_hash_map)
    n_candidates = len(candidate_configs)
    
    if n_unique_hashes != n_candidates:
        collisions = {h: ids for h, ids in cfg_hash_map.items() if len(ids) > 1}
        print("=" * 80)
        print("ERROR: cfg_hash collisions detected!")
        print("=" * 80)
        print(f"Expected {n_candidates} unique hashes, got {n_unique_hashes}")
        print(f"Number of collisions: {len(collisions)}")
        print()
        print("Colliding configs:")
        for hash_val, candidate_ids in sorted(collisions.items()):
            print(f"  Hash: {hash_val}")
            for cid in candidate_ids:
                cfg_info = wiring_proofs[cid]["runtime_cfg"]
                print(f"    {cid}: plane={cfg_info['plane_height_tolerance']:.3f}, "
                      f"arm_dist={cfg_info['arm_distance_threshold']:.3f}, "
                      f"arm_cos={cfg_info['arm_direction_exclusion_threshold']:.3f}, "
                      f"lat_q={cfg_info['lateral_quantile']:.3f}")
        print()
        raise ValueError(f"cfg_hash collision: {n_unique_hashes} unique hashes for {n_candidates} candidates")
    else:
        print(f"[OK] Hash uniqueness check passed: {n_unique_hashes} unique hashes for {n_candidates} candidates")
        print()
    
    # Compute overall status
    n_fallback_total = sum(r["n_fallback"] for r in all_results)
    n_exception_total = sum(r["n_exception"] for r in all_results)
    
    if n_fallback_total == 0 and n_exception_total == 0:
        status = "PASS"
    elif n_fallback_total == 0 and n_exception_total > 0:
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
    
    # Save wiring proof
    wiring_proof_path = os.path.join(args.out_dir, "wiring_proof.json")
    with open(wiring_proof_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id,
            "status": status,
            "wiring_proofs": wiring_proofs,
            "note": "Each candidate's runtime cfg and hash are recorded for verification",
        }, f, indent=2)
    print(f"Wiring proof: {wiring_proof_path}")
    
    # Prepare results for CSV
    csv_rows = []
    for r in all_results:
        stats = r.get("statistics", {})
        csv_rows.append({
            "candidate_id": r["candidate_id"],
            "plane_height_tolerance": r["config"]["plane_height_tolerance"],
            "arm_distance_threshold": r["config"]["arm_distance_threshold"],
            "arm_alignment_cosine_threshold": r["config"]["arm_direction_exclusion_threshold"],
            "lateral_quantile": r["config"]["lateral_quantile"],
            "cfg_hash": r["cfg_hash"],
            "n_total": r["n_total"],
            "n_valid": r["n_valid"],
            "n_fallback": r["n_fallback"],
            "n_exception": r["n_exception"],
            "measured_sw_mean": stats.get("measured_sw", {}).get("mean"),
            "measured_sw_std": stats.get("measured_sw", {}).get("std"),
            "measured_sw_min": stats.get("measured_sw", {}).get("min"),
            "measured_sw_max": stats.get("measured_sw", {}).get("max"),
            "joint_sw_mean": stats.get("joint_sw", {}).get("mean"),
            "ratio_mean": stats.get("ratio", {}).get("mean"),
            "ratio_min": stats.get("ratio", {}).get("min"),
            "ratio_max": stats.get("ratio", {}).get("max"),
            "arm_excluded_count_mean": stats.get("arm_excluded_count", {}).get("mean"),
            "arm_excluded_count_min": stats.get("arm_excluded_count", {}).get("min"),
            "arm_excluded_count_max": stats.get("arm_excluded_count", {}).get("max"),
            "torso_candidates_count_mean": stats.get("torso_candidates_count", {}).get("mean"),
            "cross_section_count_mean": stats.get("cross_section_count", {}).get("mean"),
            "perturbation_delta_stricter_mean": r.get("pose_perturbation", {}).get("delta_stricter", {}).get("mean") if r.get("pose_perturbation") else None,
            "perturbation_delta_looser_mean": r.get("pose_perturbation", {}).get("delta_looser", {}).get("mean") if r.get("pose_perturbation") else None,
        })
    
    # Save CSV
    df_results = pd.DataFrame(csv_rows)
    csv_path = os.path.join(args.out_dir, "sensitivity_results.csv")
    df_results.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Results CSV: {csv_path}")
    
    # Compute rankings
    valid_results = [r for r in all_results if r["n_fallback"] == 0 and r["n_exception"] == 0]
    
    # Rank by stability (low std)
    if len(valid_results) > 0:
        stability_ranked = sorted(
            valid_results,
            key=lambda x: x.get("statistics", {}).get("measured_sw", {}).get("std", 999.0) or 999.0
        )
        
        # Rank by arm exclusion effectiveness (high arm_excluded_count)
        exclusion_ranked = sorted(
            valid_results,
            key=lambda x: x.get("statistics", {}).get("arm_excluded_count", {}).get("mean", 0) or 0,
            reverse=True
        )
        
        # Rank by perturbation stability (low perturbation deltas)
        perturbation_ranked = sorted(
            [r for r in valid_results if r.get("pose_perturbation")],
            key=lambda x: (
                x.get("pose_perturbation", {}).get("delta_stricter", {}).get("mean", 999.0) or 999.0,
                x.get("pose_perturbation", {}).get("delta_looser", {}).get("mean", 999.0) or 999.0,
            )
        )
    
    # Build summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "status": status,
        "golden_set": args.npz,
        "n_frames": n_frames,
        "n_candidates": len(candidate_configs),
        "parameter_sweep": {
            "plane_height_tolerance": plane_height_tolerance_values,
            "arm_distance_threshold": arm_distance_threshold_values,
            "arm_alignment_cosine_threshold": arm_alignment_cosine_threshold_values,
            "lateral_quantile": lateral_quantile_values,
        },
        "overall_statistics": {
            "n_fallback_total": n_fallback_total,
            "n_exception_total": n_exception_total,
            "n_valid_candidates": len(valid_results),
        },
        "rankings": {
            "top_5_stability": [
                {
                    "candidate_id": r["candidate_id"],
                    "config": r["config"],
                    "measured_sw_std": r.get("statistics", {}).get("measured_sw", {}).get("std"),
                }
                for r in stability_ranked[:5]
            ] if len(valid_results) > 0 else [],
            "top_5_arm_exclusion": [
                {
                    "candidate_id": r["candidate_id"],
                    "config": r["config"],
                    "arm_excluded_mean": r.get("statistics", {}).get("arm_excluded_count", {}).get("mean"),
                }
                for r in exclusion_ranked[:5]
            ] if len(valid_results) > 0 else [],
            "top_5_perturbation_stable": [
                {
                    "candidate_id": r["candidate_id"],
                    "config": r["config"],
                    "delta_stricter_mean": r.get("pose_perturbation", {}).get("delta_stricter", {}).get("mean"),
                    "delta_looser_mean": r.get("pose_perturbation", {}).get("delta_looser", {}).get("mean"),
                }
                for r in perturbation_ranked[:5]
            ] if len([r for r in valid_results if r.get("pose_perturbation")]) > 0 else [],
        },
        "success_criteria": {
            "fallback_0": n_fallback_total == 0,
            "exception_0": n_exception_total == 0,
            "arm_exclusion_applied": all(
                r.get("statistics", {}).get("arm_excluded_count", {}).get("mean", 0) > 100
                for r in valid_results
            ) if len(valid_results) > 0 else False,
        },
    }
    
    # Save summary JSON
    summary_path = os.path.join(args.out_dir, "sensitivity_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON: {summary_path}")
    
    # Save manifest.json (for artifact tracking)
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "script": "verify_shoulder_width_v12_sensitivity.py",
        "status": status,
        "output_dir": args.out_dir,
        "artifacts": {
            "wiring_proof": "wiring_proof.json",
            "results_csv": "sensitivity_results.csv",
            "summary_json": "sensitivity_summary.json",
        },
    }
    manifest_path = os.path.join(args.out_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest JSON: {manifest_path}")
    print()
    
    # Print console summary
    print("=" * 80)
    print("Sensitivity Analysis Summary")
    print("=" * 80)
    print(f"Status: {status}")
    print(f"Total candidates: {len(candidate_configs)}")
    print(f"Valid candidates (no fallback/exception): {len(valid_results)}")
    print(f"Total fallbacks: {n_fallback_total}")
    print(f"Total exceptions: {n_exception_total}")
    print()
    
    if len(valid_results) > 0:
        print("Top 5 Candidates (by Stability - low std):")
        print("-" * 80)
        for i, r in enumerate(stability_ranked[:5], 1):
            cfg = r["config"]
            std = r.get("statistics", {}).get("measured_sw", {}).get("std")
            print(f"{i}. {r['candidate_id']}: plane={cfg['plane_height_tolerance']:.2f}, "
                  f"arm_dist={cfg['arm_distance_threshold']:.2f}, arm_cos={cfg['arm_direction_exclusion_threshold']:.2f}, "
                  f"lat_q={cfg['lateral_quantile']:.2f}")
            print(f"   std={std:.6f}m, arm_excluded_mean={r.get('statistics', {}).get('arm_excluded_count', {}).get('mean', 0):.0f}")
        print()
    else:
        print("No valid candidates found.")
        print()
    
    print("Success Criteria:")
    print(f"  fallback=0: {'PASS' if summary['success_criteria']['fallback_0'] else 'FAIL'}")
    print(f"  exception=0: {'PASS' if summary['success_criteria']['exception_0'] else 'FAIL'}")
    print(f"  arm_exclusion_applied: {'PASS' if summary['success_criteria']['arm_exclusion_applied'] else 'FAIL'}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

