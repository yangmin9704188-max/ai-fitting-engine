#!/usr/bin/env python3
"""Debug shoulder width measurement for case 2."""

import os
import sys
import json
import numpy as np
import torch
import smplx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.smart_mapper.smart_mapper_v001 import SmartMapper, load_beta_means
from core.measurements.shoulder_width_v112 import measure_shoulder_width_v112
from core.policy.shoulder_width_v112_policy import get_cfg as get_shoulder_width_cfg

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}

def main():
    # Case 2: male, age=30, h=1.80m, w=80.0kg, sw=0.420m
    case = {
        "sex": "male",
        "age": 30,
        "height_m": 1.80,
        "weight_kg": 80.0,
        "shoulder_width_m": 0.420,
    }
    
    print("=" * 80)
    print("Debug Shoulder Width Measurement - Case 2")
    print("=" * 80)
    print(f"Case: {case['sex']}, age={case['age']}, h={case['height_m']}m, w={case['weight_kg']}kg, sw={case['shoulder_width_m']}m")
    print()
    
    # Initialize Smart Mapper
    model_root = "./models"
    data_dir = "./data/processed/step1_output"
    
    print("Loading beta means...")
    beta_means = load_beta_means(data_dir)
    
    print("Initializing Smart Mapper...")
    mapper = SmartMapper(model_root, beta_means)
    
    # Run optimization
    print("\nRunning optimization...")
    result = mapper.optimize(
        sex=case["sex"],
        age=case["age"],
        height_m=case["height_m"],
        weight_kg=case["weight_kg"],
        target_shoulder_width_m=case["shoulder_width_m"],
        debug_output_dir="verification/reports/smart_mapper_v001/case_2_debug",
    )
    
    print(f"\nOptimization result:")
    print(f"  Status: {result['status']}")
    print(f"  Scale: {result['scale']:.4f}")
    print(f"  Height pred: {result['height_pred_m']:.4f}m (target: {case['height_m']:.4f}m)")
    print(f"  Joint SW: {result['joint_sw_m']:.4f}m")
    print(f"  Measured SW: {result['measured_sw_m']:.4f}m (target: {case['shoulder_width_m']:.4f}m)")
    print()
    
    # Re-run measurement with debug=True
    print("=" * 80)
    print("Re-running measurement with debug=True")
    print("=" * 80)
    
    # Get model and forward pass
    model = mapper._get_model(case["sex"])
    device = mapper.device
    
    # Get optimized betas
    beta_opt = torch.tensor(result["betas"], dtype=torch.float32, device=device).unsqueeze(0)
    scale_t = torch.tensor(result["scale"], dtype=torch.float32, device=device)
    
    # Forward pass
    with torch.no_grad():
        out = mapper.pose_normalizer.run_forward(
            model,
            beta_opt,
            {},
            enforce_policy_apose=True,
        )
        
        # Apply scale
        verts_scaled = out.vertices[0] * scale_t
        verts_np = verts_scaled.detach().cpu().numpy()
        lbs_weights_np = model.lbs_weights.detach().cpu().numpy()
        joints_full = out.joints
        num_joints_weights = lbs_weights_np.shape[1]
        joints_scaled = joints_full[0, :num_joints_weights, :] * scale_t
        joints_np = joints_scaled.detach().cpu().numpy()
    
    # Get frozen policy config
    sw_cfg = get_shoulder_width_cfg()
    print(f"\nFrozen policy config:")
    print(f"  r0_ratio: {sw_cfg.r0_ratio}")
    print(f"  r1_ratio: {sw_cfg.r1_ratio}")
    print(f"  cap_quantile: {sw_cfg.cap_quantile}")
    print()
    
    # Run measurement with debug
    print("Running measure_shoulder_width_v112 with return_debug=True...")
    width, debug_info = measure_shoulder_width_v112(
        verts=verts_np,
        lbs_weights=lbs_weights_np,
        joints_xyz=joints_np,
        joint_ids=SMPLX_JOINT_IDS,
        cfg=sw_cfg,
        return_debug=True,
    )
    
    # Extract debug information
    mask_step1 = debug_info["mask_keep_step1"]
    mask_step2 = debug_info["mask_keep_step2"]
    landmark_L = debug_info["landmark_L"]
    landmark_R = debug_info["landmark_R"]
    L_shoulder = debug_info["L_shoulder"]
    R_shoulder = debug_info["R_shoulder"]
    fallback = debug_info["fallback"][0]
    
    # Count points after each step
    n_total = len(verts_np)
    n_after_step1 = mask_step1.sum()
    n_after_step2 = mask_step2.sum()
    
    # Split by L/R for step 3
    pts = verts_np[mask_step2]
    dL = np.linalg.norm(pts - L_shoulder[None, :], axis=1)
    dR = np.linalg.norm(pts - R_shoulder[None, :], axis=1)
    pts_L = pts[dL <= dR]
    pts_R = pts[dR < dL]
    n_pts_L = len(pts_L)
    n_pts_R = len(pts_R)
    
    # Compute joint-based SW
    joint_sw = float(np.linalg.norm(L_shoulder - R_shoulder))
    
    # Bbox of step2 mask
    pts_step2 = verts_np[mask_step2]
    bbox_min = pts_step2.min(axis=0).tolist()
    bbox_max = pts_step2.max(axis=0).tolist()
    bbox_center = pts_step2.mean(axis=0).tolist()
    
    # Prepare debug output
    debug_output = {
        "case": case,
        "optimization_result": {
            "scale": float(result["scale"]),
            "height_pred_m": float(result["height_pred_m"]),
            "joint_sw_m": float(result["joint_sw_m"]),
            "measured_sw_m": float(result["measured_sw_m"]),
        },
        "frozen_policy_config": {
            "r0_ratio": float(sw_cfg.r0_ratio),
            "r1_ratio": float(sw_cfg.r1_ratio),
            "cap_quantile": float(sw_cfg.cap_quantile),
            "distal_w_threshold": float(sw_cfg.distal_w_threshold),
            "s_min_ratio": float(sw_cfg.s_min_ratio),
            "s_max_ratio": float(sw_cfg.s_max_ratio),
            "min_cap_points": int(sw_cfg.min_cap_points),
        },
        "point_counts": {
            "n_total_vertices": int(n_total),
            "n_after_step1": int(n_after_step1),
            "n_after_step2": int(n_after_step2),
            "n_pts_L_after_step3": int(n_pts_L),
            "n_pts_R_after_step3": int(n_pts_R),
        },
        "landmarks": {
            "landmark_L_xyz": landmark_L.tolist(),
            "landmark_R_xyz": landmark_R.tolist(),
            "L_shoulder_xyz": L_shoulder.tolist(),
            "R_shoulder_xyz": R_shoulder.tolist(),
        },
        "measurements": {
            "measured_sw_m": float(width),
            "joint_sw_m": float(joint_sw),
            "measured_joint_ratio": float(width / joint_sw),
        },
        "step2_mask_bbox": {
            "min_xyz": bbox_min,
            "max_xyz": bbox_max,
            "center_xyz": bbox_center,
        },
        "fallback_used": bool(fallback),
        "measurement_definition": {
            "code_line": "width = float(np.linalg.norm(lm_L - lm_R))  # Line 225 in shoulder_width_v112.py",
            "description": "Final width is Euclidean distance between left and right landmarks in meters",
            "formula": "||landmark_L - landmark_R||",
        },
    }
    
    # Save debug output
    output_dir = "verification/reports/smart_mapper_v001/case_2_debug"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "measurement_debug.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(debug_output, f, indent=2)
    
    print(f"\nDebug output saved to: {output_file}")
    print()
    print("=" * 80)
    print("Debug Summary")
    print("=" * 80)
    print(f"Point counts:")
    print(f"  Total vertices: {n_total}")
    print(f"  After step1 (distal arm removal): {n_after_step1}")
    print(f"  After step2 (geometric filter): {n_after_step2}")
    print(f"  After step3 L: {n_pts_L}")
    print(f"  After step3 R: {n_pts_R}")
    print()
    print(f"Measurements:")
    print(f"  Joint SW: {joint_sw:.4f}m")
    print(f"  Measured SW: {width:.4f}m")
    print(f"  Ratio: {width / joint_sw:.2f}x")
    print()
    print(f"Landmarks:")
    print(f"  L_shoulder: {L_shoulder}")
    print(f"  R_shoulder: {R_shoulder}")
    print(f"  landmark_L: {landmark_L}")
    print(f"  landmark_R: {landmark_R}")
    print()
    print(f"Step2 mask bbox:")
    print(f"  Min: {bbox_min}")
    print(f"  Max: {bbox_max}")
    print(f"  Center: {bbox_center}")
    print()
    print(f"Fallback used: {fallback}")
    print()
    print("=" * 80)
    
    # Analysis
    print("\nAnalysis:")
    print("-" * 80)
    
    # Check if arm points remain
    # Arm points would be in negative X (left) or positive X (right) relative to center
    x_coords = pts_step2[:, 0]
    y_coords = pts_step2[:, 1]
    z_coords = pts_step2[:, 2]
    
    # Check if points extend far in X direction (arms)
    x_range = x_coords.max() - x_coords.min()
    y_range = y_coords.max() - y_coords.min()
    z_range = z_coords.max() - z_coords.min()
    
    print(f"Step2 mask spatial extent:")
    print(f"  X range: {x_range:.4f}m (shoulder width direction)")
    print(f"  Y range: {y_range:.4f}m (height)")
    print(f"  Z range: {z_range:.4f}m (depth)")
    print()
    
    if x_range > 0.5:  # If X range is > 0.5m, arms might be included
        print("[WARNING] X range > 0.5m suggests arms may still be present in step2 mask")
    else:
        print("[OK] X range < 0.5m, arms likely removed")
    print()
    
    # Check landmark positions
    landmark_x_dist = abs(landmark_L[0] - landmark_R[0])
    landmark_y_dist = abs(landmark_L[1] - landmark_R[1])
    landmark_z_dist = abs(landmark_L[2] - landmark_R[2])
    
    print(f"Landmark separation:")
    print(f"  X distance: {landmark_x_dist:.4f}m (main component)")
    print(f"  Y distance: {landmark_y_dist:.4f}m")
    print(f"  Z distance: {landmark_z_dist:.4f}m")
    print()
    
    if landmark_x_dist > 0.5:
        print("[WARNING] Landmark X separation > 0.5m, suggests arms included")
    else:
        print("[OK] Landmark X separation < 0.5m, reasonable for shoulder width")
    print()
    
    # Check if landmarks are too far from shoulders
    dist_L = np.linalg.norm(landmark_L - L_shoulder)
    dist_R = np.linalg.norm(landmark_R - R_shoulder)
    
    print(f"Landmark distances from shoulder joints:")
    print(f"  L_landmark - L_shoulder: {dist_L:.4f}m")
    print(f"  R_landmark - R_shoulder: {dist_R:.4f}m")
    print()
    
    if dist_L > 0.2 or dist_R > 0.2:
        print("[WARNING] Landmarks > 0.2m from shoulder joints, may be capturing arm geometry")
    else:
        print("[OK] Landmarks < 0.2m from shoulder joints, reasonable")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()
