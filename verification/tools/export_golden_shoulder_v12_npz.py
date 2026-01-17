#!/usr/bin/env python3
"""
Export Extended Golden Set for Shoulder Width v1.2 Regression

Purpose: Generate extended NPZ dataset (>= 200 frames) for v1.2 regression verification.
Includes variation in body shapes to test measurement robustness.

Output:
- verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import torch
import smplx

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

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


def generate_golden_frame(
    sex: str,
    betas: np.ndarray,
    model: smplx.SMPLX,
    normalizer: PoseNormalizer,
    device: torch.device,
) -> Dict[str, np.ndarray]:
    """Generate golden frame data for shoulder width verification."""
    
    # Convert betas to tensor
    beta_t = torch.tensor(betas, dtype=torch.float32, device=device).unsqueeze(0)
    
    # Forward pass with A-Pose (frozen policy)
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
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export Extended Golden Set for Shoulder Width v1.2"
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
        default="verification/datasets/golden/shoulder_width",
        help="Output directory for NPZ file",
    )
    parser.add_argument(
        "--n_frames",
        type=int,
        default=200,
        help="Target number of frames (minimum 200)",
    )
    args = parser.parse_args()
    
    # Ensure minimum frames
    if args.n_frames < 200:
        print(f"Warning: n_frames={args.n_frames} < 200, using 200")
        args.n_frames = 200
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Export Extended Golden Set for Shoulder Width v1.2")
    print("=" * 80)
    print(f"Model path: {args.model_path}")
    print(f"Data dir: {args.data_dir}")
    print(f"Output dir: {args.out_dir}")
    print(f"Target frames: {args.n_frames}")
    print()
    
    # Load beta means
    print("Loading beta means...")
    beta_means = load_beta_means(args.data_dir)
    num_betas = len(beta_means["male"])
    print(f"  Male: {num_betas} dims")
    print(f"  Female: {num_betas} dims")
    print()
    
    # Load beta distributions
    male_betas_all = np.load(os.path.join(args.data_dir, "init_betas_male.npy"))
    female_betas_all = np.load(os.path.join(args.data_dir, "init_betas_female.npy"))
    
    print(f"Beta distributions:")
    print(f"  Male: {male_betas_all.shape[0]} samples")
    print(f"  Female: {female_betas_all.shape[0]} samples")
    print()
    
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    normalizer = PoseNormalizer(device=device)
    
    # Generate frames by sampling from beta distributions
    # Mix of male/female, random sampling with replacement if needed
    np.random.seed(42)  # Deterministic for reproducibility
    
    all_verts = []
    all_lbs_weights = []
    all_joints_xyz = []
    frame_metadata = []  # For provenance tracking
    
    print("Generating frames...")
    print("-" * 80)
    
    n_male = 0
    n_female = 0
    
    for frame_idx in range(args.n_frames):
        # Alternate between male/female, with some randomness
        if frame_idx % 2 == 0:
            sex = "male"
            betas_pool = male_betas_all
            n_male += 1
        else:
            sex = "female"
            betas_pool = female_betas_all
            n_female += 1
        
        # Sample random beta from pool
        beta_idx = np.random.randint(0, len(betas_pool))
        betas = betas_pool[beta_idx].astype(np.float32)
        
        # Load model for this sex (will be cached per sex)
        gender_map = {"male": "male", "female": "female"}
        model = smplx.create(
            args.model_path,
            model_type="smplx",
            gender=gender_map[sex],
            use_pca=False,
            num_betas=num_betas,
            ext="pkl",
        ).to(device)
        model.eval()
        
        # Generate frame
        data = generate_golden_frame(
            sex=sex,
            betas=betas,
            model=model,
            normalizer=normalizer,
            device=device,
        )
        
        all_verts.append(data["verts"])
        all_lbs_weights.append(data["lbs_weights"])
        all_joints_xyz.append(data["joints_xyz"])
        
        frame_metadata.append({
            "frame_id": frame_idx,
            "sex": sex,
            "beta_idx": int(beta_idx),
            "betas_shape": list(betas.shape),
        })
        
        if (frame_idx + 1) % 50 == 0:
            print(f"  Generated {frame_idx + 1}/{args.n_frames} frames...")
    
    # Stack into batched format
    verts_batched = np.stack(all_verts, axis=0)  # (T, N, 3)
    lbs_weights_batched = np.stack(all_lbs_weights, axis=0)  # (T, N, J)
    # Note: lbs_weights are the same across frames, but we store per frame for consistency
    joints_xyz_batched = np.stack(all_joints_xyz, axis=0)  # (T, J, 3)
    
    # Create provenance metadata
    provenance = {
        "generator": "export_golden_shoulder_v12_npz.py",
        "n_frames": args.n_frames,
        "n_male": n_male,
        "n_female": n_female,
        "num_betas": int(num_betas),
        "model_path": args.model_path,
        "data_dir": args.data_dir,
        "seed": 42,
        "pose_policy": "A-Pose Normalization v1.1 (frozen)",
        "note": "All frames use A-Pose normalization. Variation comes from body shape (betas) diversity.",
        "frame_metadata_sample": frame_metadata[:10],  # Sample first 10 for reference
    }
    
    # Save batched NPZ
    output_file = os.path.join(args.out_dir, "golden_shoulder_v12_extended.npz")
    np.savez(
        output_file,
        verts=verts_batched.astype(np.float32),
        lbs_weights=lbs_weights_batched.astype(np.float32),
        joints_xyz=joints_xyz_batched.astype(np.float32),
        joint_ids=SMPLX_JOINT_IDS,
        provenance=json.dumps(provenance).encode('utf-8'),  # Store as bytes for NPZ compatibility
    )
    
    print()
    print(f"Saved extended NPZ: {output_file}")
    print(f"  verts: {verts_batched.shape}")
    print(f"  lbs_weights: {lbs_weights_batched.shape}")
    print(f"  joints_xyz: {joints_xyz_batched.shape}")
    print()
    print("Provenance:")
    print(f"  Generator: {provenance['generator']}")
    print(f"  Total frames: {provenance['n_frames']}")
    print(f"  Male: {provenance['n_male']}, Female: {provenance['n_female']}")
    print(f"  Pose policy: {provenance['pose_policy']}")
    print()
    print("=" * 80)
    print("[OK] Extended golden set export complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
