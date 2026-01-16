# verify_smart_mapper_v001.py
# Verification script for Smart Mapper v0.1
# Tests 10 diverse dummy cases and compares results

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd

# Add pipelines to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, ".."))

from core.smart_mapper.smart_mapper_v001 import SmartMapper, load_beta_means


def generate_dummy_cases() -> List[Dict[str, Any]]:
    """
    Generate 10 diverse dummy test cases.
    
    Returns:
        List of dicts with keys: sex, age, height_m, weight_kg, shoulder_width_m (optional)
    """
    cases = [
        # Male cases
        {"sex": "male", "age": 25, "height_m": 1.75, "weight_kg": 70.0, "shoulder_width_m": None},
        {"sex": "male", "age": 30, "height_m": 1.80, "weight_kg": 80.0, "shoulder_width_m": 0.42},
        {"sex": "male", "age": 35, "height_m": 1.70, "weight_kg": 65.0, "shoulder_width_m": 0.38},
        {"sex": "male", "age": 40, "height_m": 1.85, "weight_kg": 90.0, "shoulder_width_m": 0.45},
        {"sex": "male", "age": 28, "height_m": 1.78, "weight_kg": 75.0, "shoulder_width_m": None},
        
        # Female cases
        {"sex": "female", "age": 25, "height_m": 1.65, "weight_kg": 55.0, "shoulder_width_m": None},
        {"sex": "female", "age": 30, "height_m": 1.70, "weight_kg": 60.0, "shoulder_width_m": 0.36},
        {"sex": "female", "age": 35, "height_m": 1.60, "weight_kg": 50.0, "shoulder_width_m": 0.34},
        {"sex": "female", "age": 28, "height_m": 1.68, "weight_kg": 58.0, "shoulder_width_m": None},
        {"sex": "female", "age": 32, "height_m": 1.72, "weight_kg": 62.0, "shoulder_width_m": 0.37},
    ]
    
    return cases


def run_verification(
    model_path: str,
    data_dir: str,
    output_dir: str,
    cases: List[Dict[str, Any]],
) -> pd.DataFrame:
    """
    Run Smart Mapper on all test cases and collect results.
    
    Returns:
        DataFrame with results for all cases
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("Smart Mapper v0.1 Verification")
    print("=" * 80)
    print(f"Model path: {model_path}")
    print(f"Data dir: {data_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Test cases: {len(cases)}")
    print()
    
    # Load beta means
    print("Loading beta means...")
    beta_means = load_beta_means(data_dir)
    print(f"  Male betas: {len(beta_means['male'])} dims")
    print(f"  Female betas: {len(beta_means['female'])} dims")
    print()
    
    # Initialize Smart Mapper
    print("Initializing Smart Mapper...")
    mapper = SmartMapper(
        model_path=model_path,
        beta_means=beta_means,
    )
    print(f"  Device: {mapper.device}")
    print()
    
    # Run all cases
    results = []
    
    print("Running test cases...")
    print("-" * 80)
    
    for idx, case in enumerate(cases, 1):
        print(f"\n[{idx}/{len(cases)}] {case['sex']}, age={case['age']}, "
              f"h={case['height_m']:.2f}m, w={case['weight_kg']:.1f}kg", end="")
        
        if case.get('shoulder_width_m') is not None:
            print(f", sw={case['shoulder_width_m']:.3f}m", end="")
        print()
        
        try:
            result = mapper.optimize(
                sex=case["sex"],
                age=case.get("age"),
                height_m=case["height_m"],
                weight_kg=case["weight_kg"],
                target_shoulder_width_m=case.get("shoulder_width_m"),
                debug_output_dir=os.path.join(output_dir, f"case_{idx}_debug"),
            )
            
            # Collect results
            status = result.get("status", "SUCCESS")
            fail_reason = result.get("fail_reason")
            
            row = {
                "case_id": idx,
                "sex": case["sex"],
                "age": case["age"],
                "height_m": case["height_m"],
                "weight_kg": case["weight_kg"],
                "target_shoulder_width_m": case.get("shoulder_width_m"),
                "scale": result["scale"],
                "beta0": float(result["betas"][0]) if result.get("betas") is not None and len(result["betas"]) > 0 else None,
                "beta_init_0": float(result["beta_init"][0]) if result.get("beta_init") is not None and len(result["beta_init"]) > 0 else None,
                "predicted_shoulder_width_m": result.get("predicted_shoulder_width_m"),
                "loss_total": result.get("loss_total"),
                "loss_measurement": result.get("loss_measurement"),
                "loss_anchor": result.get("loss_anchor"),
                "loss_beta_mag": result.get("loss_beta_mag"),
                "n_iter": result.get("n_iter", 0),
                "status": status,
                "success": status == "SUCCESS",
                "error": None,
                "fail_reason": fail_reason,
                # Sanity checks
                "height_pred_m": result.get("height_pred_m"),
                "joint_sw_m": result.get("joint_sw_m"),
                "measured_sw_m": result.get("measured_sw_m"),
            }
            
            # Shoulder width error (if target provided)
            if case.get("shoulder_width_m") is not None and result.get("predicted_shoulder_width_m") is not None:
                sw_error = abs(result["predicted_shoulder_width_m"] - case["shoulder_width_m"])
                sw_error_pct = (sw_error / case["shoulder_width_m"]) * 100.0
                row["shoulder_width_error_m"] = sw_error
                row["shoulder_width_error_pct"] = sw_error_pct
            else:
                row["shoulder_width_error_m"] = None
                row["shoulder_width_error_pct"] = None
            
            results.append(row)
            
            # Print result
            if status == "SUCCESS":
                loss_str = f"{result.get('loss_total', 0):.6f}" if result.get('loss_total') is not None else "N/A"
                print(f"  -> Success: {result.get('n_iter', 0)} iter, loss={loss_str}")
                if result.get("predicted_shoulder_width_m") is not None:
                    print(f"     Predicted SW: {result['predicted_shoulder_width_m']:.4f}m")
                    if case.get("shoulder_width_m") is not None and row.get("shoulder_width_error_m") is not None:
                        print(f"     Error: {row['shoulder_width_error_m']:.4f}m ({row['shoulder_width_error_pct']:.2f}%)")
            else:
                print(f"  -> Status: {status}")
                if fail_reason:
                    print(f"     Reason: {fail_reason[:100]}")  # Truncate long messages
        
        except Exception as e:
            print(f"  -> ERROR: {e}")
            results.append({
                "case_id": idx,
                "sex": case["sex"],
                "age": case["age"],
                "height_m": case["height_m"],
                "weight_kg": case["weight_kg"],
                "target_shoulder_width_m": case.get("shoulder_width_m"),
                "scale": None,
                "beta0": None,
                "beta_init_0": None,
                "predicted_shoulder_width_m": None,
                "loss_total": None,
                "loss_measurement": None,
                "loss_anchor": None,
                "loss_beta_mag": None,
                "n_iter": None,
                "status": "ERROR",
                "status": "ERROR",
                "success": False,
                "error": str(e),
                "fail_reason": str(e),
                "height_pred_m": None,
                "joint_sw_m": None,
                "measured_sw_m": None,
                "shoulder_width_error_m": None,
                "shoulder_width_error_pct": None,
            })
    
    print()
    print("-" * 80)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    return df


def print_summary(df: pd.DataFrame):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    # Overall stats
    n_total = len(df)
    n_success = df["success"].sum()
    n_failed = n_total - n_success
    
    print(f"\nOverall:")
    print(f"  Total cases: {n_total}")
    print(f"  Successful: {n_success}")
    print(f"  Failed: {n_failed}")
    
    if n_success == 0:
        print("\n⚠️  All cases failed!")
        return
    
    # Success rate
    success_rate = (n_success / n_total) * 100.0
    print(f"  Success rate: {success_rate:.1f}%")
    
    # Filter successful cases
    df_success = df[df["success"] == True].copy()
    
    # Iteration stats
    print(f"\nIterations:")
    print(f"  Mean: {df_success['n_iter'].mean():.1f}")
    print(f"  Min: {int(df_success['n_iter'].min())}")
    print(f"  Max: {int(df_success['n_iter'].max())}")
    
    # Loss stats
    print(f"\nLoss (total):")
    print(f"  Mean: {df_success['loss_total'].mean():.6f}")
    print(f"  Min: {df_success['loss_total'].min():.6f}")
    print(f"  Max: {df_success['loss_total'].max():.6f}")
    
    # Scale stats
    print(f"\nScale:")
    print(f"  Mean: {df_success['scale'].mean():.4f}")
    print(f"  Min: {df_success['scale'].min():.4f}")
    print(f"  Max: {df_success['scale'].max():.4f}")
    
    # Beta0 stats
    print(f"\nBeta[0] (adiposity):")
    print(f"  Mean: {df_success['beta0'].mean():.6f}")
    print(f"  Min: {df_success['beta0'].min():.6f}")
    print(f"  Max: {df_success['beta0'].max():.6f}")
    
    # Sanity checks
    print(f"\nSanity Checks:")
    df_with_checks = df_success[df_success["height_pred_m"].notna()]
    if len(df_with_checks) > 0:
        print(f"  Height prediction vs target:")
        height_errors = (df_with_checks["height_pred_m"] - df_with_checks["height_m"]).abs()
        print(f"    Mean error: {height_errors.mean():.4f}m")
        print(f"    Max error: {height_errors.max():.4f}m")
        
        print(f"  Joint-based shoulder width:")
        print(f"    Mean: {df_with_checks['joint_sw_m'].mean():.4f}m")
        print(f"    Min: {df_with_checks['joint_sw_m'].min():.4f}m")
        print(f"    Max: {df_with_checks['joint_sw_m'].max():.4f}m")
        
        sw_cases = df_with_checks[df_with_checks["target_shoulder_width_m"].notna() & 
                                  df_with_checks["measured_sw_m"].notna()]
        if len(sw_cases) > 0:
            print(f"  Measured shoulder width (n={len(sw_cases)}):")
            print(f"    Mean: {sw_cases['measured_sw_m'].mean():.4f}m")
            print(f"    Min: {sw_cases['measured_sw_m'].min():.4f}m")
            print(f"    Max: {sw_cases['measured_sw_m'].max():.4f}m")
            print(f"    vs Target - Mean error: {sw_cases['shoulder_width_error_m'].mean():.4f}m")
            print(f"    vs Target - Mean error %: {sw_cases['shoulder_width_error_pct'].mean():.2f}%")
    
    # Shoulder width stats (if available) - legacy
    sw_cases = df_success[df_success["target_shoulder_width_m"].notna() & 
                          df_success["predicted_shoulder_width_m"].notna()]
    
    if len(sw_cases) > 0:
        print(f"\nShoulder Width (n={len(sw_cases)} cases with target):")
        print(f"  Mean error: {sw_cases['shoulder_width_error_m'].mean():.4f}m")
        print(f"  Mean error %: {sw_cases['shoulder_width_error_pct'].mean():.2f}%")
        print(f"  Max error: {sw_cases['shoulder_width_error_m'].max():.4f}m")
        print(f"  Max error %: {sw_cases['shoulder_width_error_pct'].max():.2f}%")
    
    # By sex
    print(f"\nBy Sex:")
    for sex in ["male", "female"]:
        df_sex = df_success[df_success["sex"] == sex]
        if len(df_sex) > 0:
            print(f"  {sex.capitalize()} (n={len(df_sex)}):")
            print(f"    Success rate: {(len(df_sex) / len(df[df['sex'] == sex])) * 100:.1f}%")
            print(f"    Mean iterations: {df_sex['n_iter'].mean():.1f}")
            print(f"    Mean loss: {df_sex['loss_total'].mean():.6f}")
    
    print("=" * 80 + "\n")


def save_results(df: pd.DataFrame, output_dir: str):
    """Save results to CSV and JSON."""
    # Save CSV
    csv_path = os.path.join(output_dir, "verification_results.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Results CSV: {csv_path}")
    
    # Save JSON summary
    summary = {
        "n_total": int(len(df)),
        "n_success": int(df["success"].sum()),
        "n_failed": int(len(df) - df["success"].sum()),
        "success_rate_pct": float((df["success"].sum() / len(df)) * 100.0),
    }
    
    df_success = df[df["success"] == True]
    if len(df_success) > 0:
        summary["stats"] = {
            "iterations": {
                "mean": float(df_success["n_iter"].mean()),
                "min": int(df_success["n_iter"].min()),
                "max": int(df_success["n_iter"].max()),
            },
            "loss_total": {
                "mean": float(df_success["loss_total"].mean()),
                "min": float(df_success["loss_total"].min()),
                "max": float(df_success["loss_total"].max()),
            },
            "scale": {
                "mean": float(df_success["scale"].mean()),
                "min": float(df_success["scale"].min()),
                "max": float(df_success["scale"].max()),
            },
            "beta0": {
                "mean": float(df_success["beta0"].mean()),
                "min": float(df_success["beta0"].min()),
                "max": float(df_success["beta0"].max()),
            },
        }
        
        # Shoulder width stats
        sw_cases = df_success[df_success["target_shoulder_width_m"].notna() & 
                              df_success["predicted_shoulder_width_m"].notna()]
        if len(sw_cases) > 0:
            summary["stats"]["shoulder_width"] = {
                "n_cases": int(len(sw_cases)),
                "mean_error_m": float(sw_cases["shoulder_width_error_m"].mean()),
                "mean_error_pct": float(sw_cases["shoulder_width_error_pct"].mean()),
                "max_error_m": float(sw_cases["shoulder_width_error_m"].max()),
                "max_error_pct": float(sw_cases["shoulder_width_error_pct"].max()),
            }
    
    json_path = os.path.join(output_dir, "verification_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON: {json_path}")


def main():
    ap = argparse.ArgumentParser(
        description="Verify Smart Mapper v0.1 with diverse test cases"
    )
    ap.add_argument(
        "--model_path",
        type=str,
        default="./models",
        help="Path to SMPL-X model directory",
    )
    ap.add_argument(
        "--data_dir",
        type=str,
        default="./data/processed/step1_output",
        help="Path to step1_output directory",
    )
    ap.add_argument(
        "--output_dir",
        type=str,
        default="verification/reports/smart_mapper_v001",
        help="Output directory for results",
    )
    ap.add_argument(
        "--cases",
        type=int,
        default=10,
        help="Number of test cases to generate (default: 10)",
    )
    
    args = ap.parse_args()
    
    # Generate test cases
    if args.cases == 10:
        cases = generate_dummy_cases()
    else:
        # Generate custom number (simplified)
        cases = generate_dummy_cases()[:args.cases]
    
    try:
        # Run verification
        df = run_verification(
            model_path=args.model_path,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            cases=cases,
        )
        
        # Print summary
        print_summary(df)
        
        # Save results
        save_results(df, args.output_dir)
        
        print("\n[OK] Verification complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
