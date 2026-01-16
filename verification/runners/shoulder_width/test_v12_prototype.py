#!/usr/bin/env python3
"""
Test Shoulder Width v1.2 Prototype

Purpose: Validate v1.2 measurement definition on golden set.
Generate debug artifacts to answer:
"Why is this value shoulder width, not arm width?"

Output:
- artifacts/shoulder_width/v1.2_prototype/test_results.json
- artifacts/shoulder_width/v1.2_prototype/per_frame_debug.csv
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd

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


def test_v12_on_golden_set(
    npz_path: str,
    output_dir: str,
) -> Dict[str, Any]:
    """Test v1.2 measurement on golden set and generate debug artifacts."""
    
    # Load golden set
    data = np.load(npz_path, allow_pickle=True)
    verts_all = data["verts"]  # (T, N, 3)
    lbs_weights_all = data["lbs_weights"]  # (T, N, J)
    joints_xyz_all = data["joints_xyz"]  # (T, J, 3)
    
    # Handle joint_ids
    if "joint_ids" in data.files:
        joint_ids_raw = data["joint_ids"]
        if isinstance(joint_ids_raw, np.ndarray):
            joint_ids = joint_ids_raw.item() if joint_ids_raw.size == 1 else dict(joint_ids_raw)
        else:
            joint_ids = joint_ids_raw
    else:
        joint_ids = SMPLX_JOINT_IDS
    
    n_frames = verts_all.shape[0]
    
    # Test with default config
    cfg = ShoulderWidthV12Config()
    
    # Per-frame results
    results = []
    per_frame_debug = []
    
    for frame_idx in range(n_frames):
        verts = verts_all[frame_idx, :, :]
        lbs_weights = lbs_weights_all[frame_idx, :, :]
        joints_xyz = joints_xyz_all[frame_idx, :, :]
        
        # Compute joint-based SW for comparison
        L_sh = joints_xyz[joint_ids["L_shoulder"], :]
        R_sh = joints_xyz[joint_ids["R_shoulder"], :]
        joint_sw = float(np.linalg.norm(L_sh - R_sh))
        
        # Run v1.2 measurement
        width, debug_info = measure_shoulder_width_v12(
            verts=verts,
            lbs_weights=lbs_weights,
            joints_xyz=joints_xyz,
            joint_ids=joint_ids,
            cfg=cfg,
            return_debug=True,
        )
        
        # Collect results
        frame_result = {
            "frame_id": frame_idx + 1,
            "measured_sw_m": float(width),
            "joint_sw_m": joint_sw,
            "ratio": float(width / joint_sw) if joint_sw > 0 else None,
            "fallback": debug_info.get("fallback", False),
            "fallback_reason": debug_info.get("reason"),
            "cross_section_vertices_count": debug_info.get("cross_section_vertices_count", 0),
            "arm_excluded_count": debug_info.get("arm_excluded_count", 0),
            "torso_candidates_count": debug_info.get("torso_candidates_count", 0),
        }
        
        results.append(frame_result)
        
        # Per-frame debug (sample first 3 frames in detail)
        if frame_idx < 3:
            per_frame_debug.append({
                "frame_id": frame_idx + 1,
                **debug_info,
            })
    
    # Aggregate statistics
    measured_sws = [r["measured_sw_m"] for r in results]
    joint_sws = [r["joint_sw_m"] for r in results]
    ratios = [r["ratio"] for r in results if r["ratio"] is not None]
    
    summary = {
        "n_frames": n_frames,
        "config": {
            "plane_height_tolerance": float(cfg.plane_height_tolerance),
            "arm_direction_exclusion_threshold": float(cfg.arm_direction_exclusion_threshold),
            "lateral_quantile": float(cfg.lateral_quantile),
        },
        "statistics": {
            "measured_sw": {
                "min": float(np.min(measured_sws)),
                "mean": float(np.mean(measured_sws)),
                "max": float(np.max(measured_sws)),
                "std": float(np.std(measured_sws)),
            },
            "joint_sw": {
                "min": float(np.min(joint_sws)),
                "mean": float(np.mean(joint_sws)),
                "max": float(np.max(joint_sws)),
                "std": float(np.std(joint_sws)),
            },
            "ratio": {
                "min": float(np.min(ratios)) if len(ratios) > 0 else None,
                "mean": float(np.mean(ratios)) if len(ratios) > 0 else None,
                "max": float(np.max(ratios)) if len(ratios) > 0 else None,
                "std": float(np.std(ratios)) if len(ratios) > 0 else None,
            },
        },
        "fallback_count": sum(1 for r in results if r["fallback"]),
        "per_frame_results": results,
    }
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    
    # Summary JSON
    summary_path = os.path.join(output_dir, "test_results.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    # Per-frame CSV
    df_results = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, "per_frame_debug.csv")
    df_results.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    # Detailed debug JSON (first 3 frames)
    if len(per_frame_debug) > 0:
        debug_path = os.path.join(output_dir, "detailed_debug_frames.json")
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(per_frame_debug, f, indent=2)
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Test Shoulder Width v1.2 Prototype"
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
        default="artifacts/shoulder_width/v1.2_prototype",
        help="Output directory",
    )
    args = parser.parse_args()
    
    print("=" * 80)
    print("Shoulder Width v1.2 Prototype Test")
    print("=" * 80)
    print(f"Input NPZ: {args.npz}")
    print(f"Output dir: {args.out_dir}")
    print()
    
    summary = test_v12_on_golden_set(args.npz, args.out_dir)
    
    print("Results Summary:")
    print("-" * 80)
    print(f"Frames tested: {summary['n_frames']}")
    print(f"Fallback count: {summary['fallback_count']}")
    print()
    print("Measured SW statistics:")
    stats_sw = summary["statistics"]["measured_sw"]
    print(f"  min: {stats_sw['min']:.4f}m")
    print(f"  mean: {stats_sw['mean']:.4f}m")
    print(f"  max: {stats_sw['max']:.4f}m")
    print(f"  std: {stats_sw['std']:.4f}m")
    print()
    print("Joint SW statistics:")
    stats_joint = summary["statistics"]["joint_sw"]
    print(f"  min: {stats_joint['min']:.4f}m")
    print(f"  mean: {stats_joint['mean']:.4f}m")
    print(f"  max: {stats_joint['max']:.4f}m")
    print()
    if summary["statistics"]["ratio"]["mean"] is not None:
        print("Ratio (measured_sw / joint_sw):")
        stats_ratio = summary["statistics"]["ratio"]
        print(f"  min: {stats_ratio['min']:.4f}")
        print(f"  mean: {stats_ratio['mean']:.4f}")
        print(f"  max: {stats_ratio['max']:.4f}")
    print()
    print(f"Results saved to: {args.out_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
