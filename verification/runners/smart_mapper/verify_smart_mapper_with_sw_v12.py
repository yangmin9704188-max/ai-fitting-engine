#!/usr/bin/env python3
"""
Smart Mapper v0.1 Sanity Check with Shoulder Width v1.2

Purpose: Minimal sanity check to ensure Smart Mapper works with v1.2 shoulder width.
Tests a small batch (10-20 samples) to confirm:
- Loss is finite
- Gradients/optimization do not explode
- v1.2 measurement integration works

Note: This is optional and can be skipped if Smart Mapper is not available.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import torch
import pandas as pd

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from core.smart_mapper.smart_mapper_v001 import SmartMapper, load_beta_means
    from core.measurements.shoulder_width_v12 import measure_shoulder_width_v12, ShoulderWidthV12Config
    SMART_MAPPER_AVAILABLE = True
except ImportError as e:
    SMART_MAPPER_AVAILABLE = False
    IMPORT_ERROR = str(e)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Mapper v0.1 Sanity Check with Shoulder Width v1.2"
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
        "--n_samples",
        type=int,
        default=10,
        help="Number of test samples (default: 10)",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="artifacts/verification/smart_mapper_sw_v12",
        help="Output directory",
    )
    args = parser.parse_args()
    
    # Check if Smart Mapper is available
    if not SMART_MAPPER_AVAILABLE:
        print("=" * 80)
        print("Smart Mapper Sanity Check - SKIPPED")
        print("=" * 80)
        print(f"Smart Mapper module is not available in this repository.")
        print(f"Import error: {IMPORT_ERROR}")
        print()
        print("This check is optional and can be skipped.")
        print("=" * 80)
        return
    
    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)
    
    print("=" * 80)
    print("Smart Mapper v0.1 Sanity Check with Shoulder Width v1.2")
    print("=" * 80)
    print(f"Model path: {args.model_path}")
    print(f"Data dir: {args.data_dir}")
    print(f"Number of samples: {args.n_samples}")
    print(f"Output dir: {args.out_dir}")
    print()
    
    # Generate dummy test cases
    print("Generating test cases...")
    test_cases = []
    np.random.seed(42)
    
    for i in range(args.n_samples):
        sex = "male" if i % 2 == 0 else "female"
        # Random height: 160-180 cm
        height_m = np.random.uniform(1.60, 1.80)
        # Random weight: 50-80 kg
        weight_kg = np.random.uniform(50.0, 80.0)
        # Optional target shoulder width (roughly proportional to height)
        target_sw = height_m * 0.23 + np.random.uniform(-0.05, 0.05)
        
        test_cases.append({
            "case_id": i + 1,
            "sex": sex,
            "height_m": height_m,
            "weight_kg": weight_kg,
            "target_shoulder_width_m": target_sw,
        })
    
    print(f"Generated {len(test_cases)} test cases")
    print()
    
    # Load Smart Mapper
    print("Loading Smart Mapper...")
    beta_means = load_beta_means(args.data_dir)
    mapper = SmartMapper(
        model_path=args.model_path,
        beta_means=beta_means,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    )
    print("Smart Mapper loaded")
    print()
    
    # Run tests
    print("Running Smart Mapper on test cases...")
    print("-" * 80)
    
    results = []
    n_success = 0
    n_failed = 0
    
    for case in test_cases:
        case_id = case["case_id"]
        print(f"  Testing case {case_id}/{len(test_cases)}: {case['sex']}, "
              f"h={case['height_m']:.2f}m, w={case['weight_kg']:.1f}kg... ", end="", flush=True)
        
        try:
            result = mapper.optimize(
                sex=case["sex"],
                age=None,
                height_m=case["height_m"],
                weight_kg=case["weight_kg"],
                target_shoulder_width_m=case["target_shoulder_width_m"],
                debug_output_dir=None,
            )
            
            # Extract metrics
            final_loss = result.get("final_loss", np.nan)
            predicted_sw = result.get("predicted_shoulder_width_m", None)
            n_iter = result.get("n_iter", 0)
            
            # Sanity checks
            loss_finite = np.isfinite(final_loss) if not np.isnan(final_loss) else False
            sw_valid = predicted_sw is not None and np.isfinite(predicted_sw)
            
            if loss_finite and sw_valid:
                status = "OK"
                n_success += 1
            else:
                status = "WARN"
                n_failed += 1
            
            results.append({
                "case_id": case_id,
                "sex": case["sex"],
                "height_m": case["height_m"],
                "weight_kg": case["weight_kg"],
                "target_sw_m": case["target_shoulder_width_m"],
                "predicted_sw_m": predicted_sw,
                "final_loss": float(final_loss) if not np.isnan(final_loss) else None,
                "n_iter": n_iter,
                "status": status,
                "error": None,
            })
            
            print(f"{status} (loss={final_loss:.6f}, sw={predicted_sw:.4f}m, iter={n_iter})")
            
        except Exception as e:
            status = "FAIL"
            n_failed += 1
            
            results.append({
                "case_id": case_id,
                "sex": case["sex"],
                "height_m": case["height_m"],
                "weight_kg": case["weight_kg"],
                "target_sw_m": case["target_shoulder_width_m"],
                "predicted_sw_m": None,
                "final_loss": None,
                "n_iter": 0,
                "status": status,
                "error": f"{type(e).__name__}: {str(e)}",
            })
            
            print(f"{status} ({type(e).__name__})")
    
    print("-" * 80)
    print()
    
    # Save results
    df_results = pd.DataFrame(results)
    df_results.to_csv(
        os.path.join(args.out_dir, "sanity_check_results.csv"),
        index=False,
        encoding="utf-8-sig"
    )
    
    # Compute summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": args.n_samples,
        "n_success": n_success,
        "n_failed": n_failed,
        "success_rate": float(n_success) / args.n_samples if args.n_samples > 0 else 0.0,
        "loss_stats": {
            "min": float(df_results["final_loss"].min()) if df_results["final_loss"].notna().any() else None,
            "mean": float(df_results["final_loss"].mean()) if df_results["final_loss"].notna().any() else None,
            "max": float(df_results["final_loss"].max()) if df_results["final_loss"].notna().any() else None,
        } if df_results["final_loss"].notna().any() else None,
        "iter_stats": {
            "min": int(df_results["n_iter"].min()),
            "mean": float(df_results["n_iter"].mean()),
            "max": int(df_results["n_iter"].max()),
        },
        "sw_stats": {
            "predicted_min": float(df_results["predicted_sw_m"].min()) if df_results["predicted_sw_m"].notna().any() else None,
            "predicted_mean": float(df_results["predicted_sw_m"].mean()) if df_results["predicted_sw_m"].notna().any() else None,
            "predicted_max": float(df_results["predicted_sw_m"].max()) if df_results["predicted_sw_m"].notna().any() else None,
        } if df_results["predicted_sw_m"].notna().any() else None,
        "sanity_checks": {
            "all_losses_finite": df_results["final_loss"].notna().all() and df_results["final_loss"].apply(np.isfinite).all(),
            "all_sw_valid": df_results["predicted_sw_m"].notna().all(),
            "no_explosive_iterations": int(df_results["n_iter"].max()) < 100,  # Reasonable limit
        },
    }
    
    with open(os.path.join(args.out_dir, "sanity_check_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("=" * 80)
    print("Sanity Check Summary")
    print("=" * 80)
    print(f"Success: {n_success}/{args.n_samples} ({summary['success_rate']*100:.1f}%)")
    print(f"Failed: {n_failed}/{args.n_samples}")
    print()
    
    if summary["loss_stats"]:
        print("Loss statistics:")
        print(f"  min: {summary['loss_stats']['min']:.6f}")
        print(f"  mean: {summary['loss_stats']['mean']:.6f}")
        print(f"  max: {summary['loss_stats']['max']:.6f}")
        print()
    
    if summary["sw_stats"]:
        print("Predicted shoulder width statistics:")
        print(f"  min: {summary['sw_stats']['predicted_min']:.4f}m")
        print(f"  mean: {summary['sw_stats']['predicted_mean']:.4f}m")
        print(f"  max: {summary['sw_stats']['predicted_max']:.4f}m")
        print()
    
    print("Sanity checks:")
    print(f"  All losses finite: {'PASS' if summary['sanity_checks']['all_losses_finite'] else 'FAIL'}")
    print(f"  All SW valid: {'PASS' if summary['sanity_checks']['all_sw_valid'] else 'FAIL'}")
    print(f"  No explosive iterations: {'PASS' if summary['sanity_checks']['no_explosive_iterations'] else 'FAIL'}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
