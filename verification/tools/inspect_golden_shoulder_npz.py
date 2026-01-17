#!/usr/bin/env python3
"""
Inspect Golden Shoulder NPZ - Sanity Check

Purpose: Diagnose potential issues with golden NPZ data:
- Joint ID correctness
- Scale/units (meters)
- Geometric relationships (shoulder-shoulder, shoulder-elbow distances)

Output:
- Console summary
- artifacts/shoulder_width/v1.1.3/npz_sanity.json
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# SMPL-X joint IDs (standard)
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}


def compute_distances(joints_xyz: np.ndarray, joint_ids: Dict[str, int]) -> Dict[str, Any]:
    """Compute various distances for sanity checks."""
    n_frames = joints_xyz.shape[0] if joints_xyz.ndim == 3 else 1
    
    # Ensure 3D shape
    if joints_xyz.ndim == 2:
        joints_xyz = joints_xyz[None, ...]
    
    results = {
        "shoulder_to_shoulder": [],
        "L_shoulder_to_L_elbow": [],
        "R_shoulder_to_R_elbow": [],
    }
    
    # Test candidate shoulder pairs
    candidate_pairs = [
        (16, 17, "standard_L16_R17"),
        (17, 16, "reversed_R17_L16"),
        (15, 16, "alt_L15_R16"),  # Alternative if available
        (16, 18, "L16_R18"),  # Alternative
        (14, 17, "L14_R17"),  # Alternative
    ]
    
    for frame_idx in range(n_frames):
        joints = joints_xyz[frame_idx, :, :]
        
        # Standard shoulder-to-shoulder (L_shoulder=16, R_shoulder=17)
        if joint_ids.get("L_shoulder") is not None and joint_ids.get("R_shoulder") is not None:
            L_sh_idx = joint_ids["L_shoulder"]
            R_sh_idx = joint_ids["R_shoulder"]
            
            if L_sh_idx < joints.shape[0] and R_sh_idx < joints.shape[0]:
                L_sh = joints[L_sh_idx, :]
                R_sh = joints[R_sh_idx, :]
                dist = float(np.linalg.norm(L_sh - R_sh))
                results["shoulder_to_shoulder"].append(dist)
        
        # Shoulder-to-elbow distances
        if joint_ids.get("L_shoulder") is not None and joint_ids.get("L_elbow") is not None:
            L_sh_idx = joint_ids["L_shoulder"]
            L_el_idx = joint_ids["L_elbow"]
            
            if L_sh_idx < joints.shape[0] and L_el_idx < joints.shape[0]:
                L_sh = joints[L_sh_idx, :]
                L_el = joints[L_el_idx, :]
                dist = float(np.linalg.norm(L_sh - L_el))
                results["L_shoulder_to_L_elbow"].append(dist)
        
        if joint_ids.get("R_shoulder") is not None and joint_ids.get("R_elbow") is not None:
            R_sh_idx = joint_ids["R_shoulder"]
            R_el_idx = joint_ids["R_elbow"]
            
            if R_sh_idx < joints.shape[0] and R_el_idx < joints.shape[0]:
                R_sh = joints[R_sh_idx, :]
                R_el = joints[R_el_idx, :]
                dist = float(np.linalg.norm(R_sh - R_el))
                results["R_shoulder_to_R_elbow"].append(dist)
    
    # Compute statistics
    stats = {}
    for key, values in results.items():
        if len(values) > 0:
            stats[key] = {
                "count": len(values),
                "min": float(np.min(values)),
                "mean": float(np.mean(values)),
                "max": float(np.max(values)),
                "std": float(np.std(values)),
            }
        else:
            stats[key] = {"count": 0}
    
    # Test candidate pairs for alternative shoulder indices
    candidate_results = {}
    for idx1, idx2, name in candidate_pairs:
        if idx1 < joints_xyz.shape[-2] and idx2 < joints_xyz.shape[-2]:
            dists = []
            for frame_idx in range(n_frames):
                joints = joints_xyz[frame_idx, :, :]
                j1 = joints[idx1, :]
                j2 = joints[idx2, :]
                dist = float(np.linalg.norm(j1 - j2))
                dists.append(dist)
            
            if len(dists) > 0:
                candidate_results[name] = {
                    "indices": (int(idx1), int(idx2)),
                    "min": float(np.min(dists)),
                    "mean": float(np.mean(dists)),
                    "max": float(np.max(dists)),
                    "std": float(np.std(dists)),
                }
    
    return {
        "per_frame_distances": results,
        "statistics": stats,
        "candidate_pair_tests": candidate_results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Inspect Golden Shoulder NPZ - Sanity Check"
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
        default="artifacts/shoulder_width/v1.1.3",
        help="Output directory for JSON report",
    )
    args = parser.parse_args()
    
    print("=" * 80)
    print("Golden Shoulder NPZ Inspection - Sanity Check")
    print("=" * 80)
    print(f"Input NPZ: {args.npz}")
    print()
    
    # Load NPZ
    if not os.path.exists(args.npz):
        raise FileNotFoundError(f"NPZ file not found: {args.npz}")
    
    # Load NPZ (allow_pickle=True for joint_ids dict)
    data = np.load(args.npz, allow_pickle=True)
    keys = set(data.files)
    
    print("NPZ Keys:", sorted(keys))
    print()
    
    # Extract data
    verts = data["verts"]  # (T, N, 3) or (N, 3)
    lbs_weights = data["lbs_weights"]  # (T, N, J) or (N, J)
    joints_xyz = data["joints_xyz"]  # (T, J, 3) or (J, 3)
    
    # Handle joint_ids (may be stored as object array)
    if "joint_ids" in keys:
        joint_ids_raw = data["joint_ids"]
        if isinstance(joint_ids_raw, np.ndarray):
            if joint_ids_raw.shape == ():
                joint_ids = joint_ids_raw.item()
            elif joint_ids_raw.dtype == object:
                joint_ids = joint_ids_raw.item() if joint_ids_raw.size == 1 else dict(joint_ids_raw)
            else:
                joint_ids = dict(joint_ids_raw)
        elif isinstance(joint_ids_raw, dict):
            joint_ids = joint_ids_raw
        else:
            joint_ids = joint_ids_raw
    else:
        joint_ids = SMPLX_JOINT_IDS
        print("[WARNING] joint_ids not found in NPZ, using standard SMPL-X IDs")
    
    print("Shapes:")
    print(f"  verts: {verts.shape}")
    print(f"  lbs_weights: {lbs_weights.shape}")
    print(f"  joints_xyz: {joints_xyz.shape}")
    print(f"  joint_ids: {joint_ids}")
    print()
    
    # Ensure batched
    if verts.ndim == 2:
        verts = verts[None, ...]
    if lbs_weights.ndim == 2:
        lbs_weights = lbs_weights[None, ...]
    if joints_xyz.ndim == 2:
        joints_xyz = joints_xyz[None, ...]
    
    n_frames = verts.shape[0]
    print(f"Number of frames: {n_frames}")
    print()
    
    # Compute distances
    print("Computing distances...")
    dist_results = compute_distances(joints_xyz, joint_ids)
    
    # Print statistics
    print("Distance Statistics (meters):")
    print("-" * 80)
    for key, stats in dist_results["statistics"].items():
        if stats["count"] > 0:
            print(f"  {key}:")
            print(f"    min: {stats['min']:.4f}m")
            print(f"    mean: {stats['mean']:.4f}m")
            print(f"    max: {stats['max']:.4f}m")
            print(f"    std: {stats['std']:.4f}m")
    print()
    
    # Print candidate pair tests
    print("Candidate Pair Tests (alternative shoulder indices):")
    print("-" * 80)
    for name, result in dist_results["candidate_pair_tests"].items():
        print(f"  {name} (indices {result['indices']}):")
        print(f"    min: {result['min']:.4f}m")
        print(f"    mean: {result['mean']:.4f}m")
        print(f"    max: {result['max']:.4f}m")
    print()
    
    # Sample first frame
    frame_0_joints = joints_xyz[0, :, :]
    print("Frame 0 Sample Joints (first 5):")
    print("-" * 80)
    for i in range(min(5, frame_0_joints.shape[0])):
        j = frame_0_joints[i, :]
        print(f"  Joint {i}: [{j[0]:.4f}, {j[1]:.4f}, {j[2]:.4f}]")
    print()
    
    # Build report
    report = {
        "npz_path": args.npz,
        "shapes": {
            "verts": list(verts.shape),
            "lbs_weights": list(lbs_weights.shape),
            "joints_xyz": list(joints_xyz.shape),
            "n_frames": int(n_frames),
        },
        "joint_ids": {k: int(v) for k, v in joint_ids.items()} if isinstance(joint_ids, dict) else str(joint_ids),
        "distance_statistics": dist_results["statistics"],
        "candidate_pair_tests": dist_results["candidate_pair_tests"],
        "interpretation": {
            "typical_shoulder_width_m": {
                "human_range": [0.30, 0.50],  # Typical human shoulder width
                "observed_mean": dist_results["statistics"].get("shoulder_to_shoulder", {}).get("mean"),
                "observed_range": [
                    dist_results["statistics"].get("shoulder_to_shoulder", {}).get("min"),
                    dist_results["statistics"].get("shoulder_to_shoulder", {}).get("max"),
                ],
            },
            "typical_upper_arm_length_m": {
                "human_range": [0.25, 0.35],  # Typical upper arm length
                "observed_mean_L": dist_results["statistics"].get("L_shoulder_to_L_elbow", {}).get("mean"),
                "observed_mean_R": dist_results["statistics"].get("R_shoulder_to_R_elbow", {}).get("mean"),
            },
        },
    }
    
    # Save report
    os.makedirs(args.out_dir, exist_ok=True)
    report_path = os.path.join(args.out_dir, "npz_sanity.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved: {report_path}")
    print()
    
    # Interpretation
    print("=" * 80)
    print("Interpretation")
    print("=" * 80)
    
    shoulder_mean = dist_results["statistics"].get("shoulder_to_shoulder", {}).get("mean")
    if shoulder_mean is not None:
        if 0.30 <= shoulder_mean <= 0.50:
            print("[OK] Shoulder width is in typical human range (0.30-0.50m)")
        else:
            print(f"[WARNING] Shoulder width {shoulder_mean:.4f}m is outside typical range (0.30-0.50m)")
            print("   This suggests possible scale mismatch or joint ID error")
    
    arm_mean_L = dist_results["statistics"].get("L_shoulder_to_L_elbow", {}).get("mean")
    arm_mean_R = dist_results["statistics"].get("R_shoulder_to_R_elbow", {}).get("mean")
    if arm_mean_L is not None and arm_mean_R is not None:
        if 0.25 <= arm_mean_L <= 0.35 and 0.25 <= arm_mean_R <= 0.35:
            print("[OK] Upper arm length is in typical human range (0.25-0.35m)")
        else:
            print(f"[WARNING] Upper arm length (L: {arm_mean_L:.4f}m, R: {arm_mean_R:.4f}m) outside typical range (0.25-0.35m)")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
