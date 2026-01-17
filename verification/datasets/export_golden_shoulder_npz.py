#!/usr/bin/env python3
"""
Export Golden Set for Shoulder Width Verification

Purpose: Generate NPZ files containing verts/lbs_weights/joints_xyz/joint_ids
         for shoulder width verification.

Output:
- verification/golden_shoulder_*.npz (one file per case, or one batched file)
"""

from __future__ import annotations

import os
import sys
import argparse
import numpy as np
import torch
import smplx
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pose_policy import PoseNormalizer
from core.smart_mapper.smart_mapper_v001 import load_beta_means

# SMPL-X joint IDs
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}


def generate_golden_case(
    case_id: int,
    sex: str,
    betas: np.ndarray,
    model: smplx.SMPLX,
    normalizer: PoseNormalizer,
    device: torch.device,
) -> Dict[str, np.ndarray]:
    """Generate golden case data for shoulder width verification."""
    
    # Convert betas to tensor
    beta_t = torch.tensor(betas, dtype=torch.float32, device=device).unsqueeze(0)
    
    # Forward pass with A-Pose
    with torch.no_grad():
        out = normalizer.run_forward(
            model,
            beta_t,
            {},
            enforce_policy_apose=True,
        )
        
        # Extract data
        verts = out.vertices[0].detach().cpu().numpy()  # (N, 3)
        joints_xyz = out.joints[0].detach().cpu().numpy()  # (J, 3)
        lbs_weights = model.lbs_weights.detach().cpu().numpy()  # (N, J)
        
        # Use first 55 joints to match lbs_weights
        num_joints_weights = lbs_weights.shape[1]
        joints_xyz = joints_xyz[:num_joints_weights, :]
    
    return {
        "verts": verts.astype(np.float32),
        "lbs_weights": lbs_weights.astype(np.float32),
        "joints_xyz": joints_xyz.astype(np.float32),
        "joint_ids": SMPLX_JOINT_IDS,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export Golden Set for Shoulder Width Verification"
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
        default="verification",
        help="Output directory for NPZ files",
    )
    parser.add_argument(
        "--n_cases",
        type=int,
        default=10,
        help="Number of cases to generate",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["individual", "batched"],
        default="batched",
        help="Output format: individual files or one batched file",
    )
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Export Golden Set for Shoulder Width Verification")
    print("=" * 80)
    print(f"Model path: {args.model_path}")
    print(f"Data dir: {args.data_dir}")
    print(f"Output dir: {args.out_dir}")
    print(f"Number of cases: {args.n_cases}")
    print(f"Format: {args.format}")
    print()
    
    # Load beta means
    beta_means = load_beta_means(args.data_dir)
    
    num_betas = len(beta_means["male"])
    print(f"Loaded beta means:")
    print(f"  Male: {num_betas} dims")
    print(f"  Female: {num_betas} dims")
    print()
    
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    normalizer = PoseNormalizer(device=device)
    
    # Generate test cases
    cases = []
    np.random.seed(42)
    
    for i in range(args.n_cases):
        sex = "male" if i % 2 == 0 else "female"
        betas_all = np.load(os.path.join(args.data_dir, f"init_betas_{sex}.npy"))
        
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
    
    # Generate golden data
    print("Generating golden data...")
    print("-" * 80)
    
    if args.format == "batched":
        # Collect all cases into one batched array
        all_verts = []
        all_lbs_weights = []
        all_joints_xyz = []
        
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
            
            data = generate_golden_case(
                case_id=case["case_id"],
                sex=case["sex"],
                betas=case["betas"],
                model=model,
                normalizer=normalizer,
                device=device,
            )
            
            all_verts.append(data["verts"])
            all_lbs_weights.append(data["lbs_weights"])
            all_joints_xyz.append(data["joints_xyz"])
            
            print(f"[{case['case_id']}/{len(cases)}] {case['sex']:6s}: "
                  f"verts {data['verts'].shape}, joints {data['joints_xyz'].shape}")
        
        # Stack into batched format
        verts_batched = np.stack(all_verts, axis=0)  # (T, N, 3)
        lbs_weights_batched = np.stack(all_lbs_weights, axis=0)  # (T, N, J)
        joints_xyz_batched = np.stack(all_joints_xyz, axis=0)  # (T, J, 3)
        
        # Save batched NPZ
        output_file = os.path.join(args.out_dir, "golden_shoulder_batched.npz")
        np.savez(
            output_file,
            verts=verts_batched.astype(np.float32),
            lbs_weights=lbs_weights_batched.astype(np.float32),
            joints_xyz=joints_xyz_batched.astype(np.float32),
            joint_ids=SMPLX_JOINT_IDS,
        )
        print()
        print(f"Saved batched NPZ: {output_file}")
        print(f"  verts: {verts_batched.shape}")
        print(f"  lbs_weights: {lbs_weights_batched.shape}")
        print(f"  joints_xyz: {joints_xyz_batched.shape}")
    
    else:
        # Save individual files
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
            
            data = generate_golden_case(
                case_id=case["case_id"],
                sex=case["sex"],
                betas=case["betas"],
                model=model,
                normalizer=normalizer,
                device=device,
            )
            
            output_file = os.path.join(args.out_dir, f"golden_shoulder_{case['case_id']:03d}.npz")
            np.savez(
                output_file,
                verts=data["verts"],
                lbs_weights=data["lbs_weights"],
                joints_xyz=data["joints_xyz"],
                joint_ids=SMPLX_JOINT_IDS,
            )
            
            print(f"[{case['case_id']}/{len(cases)}] {case['sex']:6s}: {output_file}")
    
    print()
    print("=" * 80)
    print("[OK] Golden set export complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
