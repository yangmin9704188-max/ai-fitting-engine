# smart_mapper_run.py
# CLI entry point for Smart Mapper v0.1

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import datetime as dt
from typing import Optional
import csv

from core.smart_mapper.smart_mapper_v001 import SmartMapper, load_beta_means


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


def create_dummy_config(output_path: str):
    """Create a dummy config file for testing."""
    config = {
        "sex": "male",
        "age": 30,
        "height_m": 1.75,
        "weight_kg": 70.0,
        "shoulder_width_m": None,  # Optional
        "model_path": "./models",
        "data_dir": "./data/processed/step1_output",
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print(f"Created dummy config: {output_path}")


def run_smart_mapper(config_path: str, output_dir: Optional[str] = None, run_id_override: Optional[str] = None):
    """
    Run Smart Mapper with config file.
    
    Args:
        config_path: Path to JSON config file
        output_dir: Output directory (default: artifacts/runs/smart_mapper/<run_id>)
        run_id_override: Optional RUN_ID override (default: from env or auto-generate)
    """
    # Resolve RUN_ID first (before any artifact path creation)
    run_id = resolve_run_id(run_id_override)
    
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Validate required fields
    required = ["sex", "height_m", "weight_kg", "model_path", "data_dir"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Config missing required fields: {missing}")
    
    sex = config["sex"]
    age = config.get("age")
    height_m = float(config["height_m"])
    weight_kg = float(config["weight_kg"])
    target_shoulder_width_m = config.get("shoulder_width_m")
    if target_shoulder_width_m is not None:
        target_shoulder_width_m = float(target_shoulder_width_m)
    
    model_path = config["model_path"]
    data_dir = config["data_dir"]
    
    # Create output directory
    if output_dir is None:
        output_dir = f"artifacts/runs/smart_mapper/{run_id}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("Smart Mapper v0.1")
    print("=" * 80)
    print(f"Config: {config_path}")
    print(f"Output: {output_dir}")
    print(f"Sex: {sex}, Age: {age}, Height: {height_m:.3f}m, Weight: {weight_kg:.1f}kg")
    if target_shoulder_width_m is not None:
        print(f"Target shoulder width: {target_shoulder_width_m:.4f}m")
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
    
    # Run optimization
    print("Running optimization...")
    result = mapper.optimize(
        sex=sex,
        age=age,
        height_m=height_m,
        weight_kg=weight_kg,
        target_shoulder_width_m=target_shoulder_width_m,
        debug_output_dir=output_dir,
    )
    
    print(f"  Completed in {result['n_iter']} iterations")
    print(f"  Final loss: {result['loss_total']:.6f}")
    if result['predicted_shoulder_width_m'] is not None:
        print(f"  Predicted shoulder width: {result['predicted_shoulder_width_m']:.4f}m")
    print()
    
    # Save results
    print("Saving results...")
    
    # 1. Save config
    config_out_path = os.path.join(output_dir, "config.json")
    with open(config_out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"  Config: {config_out_path}")
    
    # 2. Save result
    result_out = {
        "run_id": run_id,
        "scale": result["scale"],
        "betas": result["betas"].tolist(),
        "beta_init": result["beta_init"].tolist(),
        "predicted_shoulder_width_m": result["predicted_shoulder_width_m"],
        "loss_total": result["loss_total"],
        "loss_measurement": result["loss_measurement"],
        "loss_anchor": result["loss_anchor"],
        "loss_beta_mag": result["loss_beta_mag"],
        "n_iter": result["n_iter"],
        "status": result.get("status", "SUCCESS"),
        "fail_reason": result.get("fail_reason"),
        # Sanity checks
        "height_pred_m": result.get("height_pred_m"),
        "joint_sw_m": result.get("joint_sw_m"),
        "measured_sw_m": result.get("measured_sw_m"),
    }
    
    result_out_path = os.path.join(output_dir, "result.json")
    with open(result_out_path, "w", encoding="utf-8") as f:
        json.dump(result_out, f, indent=2)
    print(f"  Result: {result_out_path}")
    
    # 3. Save trace
    trace_out_path = os.path.join(output_dir, "trace.csv")
    with open(trace_out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["iter", "loss_total", "loss_meas", "loss_anchor", "loss_beta_mag", "dt_ms"])
        writer.writeheader()
        for row in result["trace"]:
            writer.writerow(row)
    print(f"  Trace: {trace_out_path}")
    
    # Save manifest.json (for artifact tracking)
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "script": "smart_mapper_run.py",
        "config_path": config_path,
        "output_dir": output_dir,
        "artifacts": {
            "config": "config.json",
            "result": "result.json",
            "trace": "trace.csv",
        },
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest: {manifest_path}")
    
    print()
    print("=" * 80)
    print("[OK] Complete!")
    print(f"Results saved to: {output_dir}")
    print("=" * 80)
    
    return result


def main():
    ap = argparse.ArgumentParser(
        description="Smart Mapper v0.1 - Map anthropometric measurements to SMPL-X parameters"
    )
    ap.add_argument(
        "--config",
        type=str,
        required=False,
        help="Path to JSON config file",
    )
    ap.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Output directory (default: artifacts/runs/smart_mapper/<run_id>)",
    )
    ap.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run ID (default: from env RUN_ID or auto-generate KST timestamp)",
    )
    ap.add_argument(
        "--create_dummy_config",
        type=str,
        default=None,
        help="Create a dummy config file at the specified path and exit",
    )
    
    args = ap.parse_args()
    
    if args.create_dummy_config:
        create_dummy_config(args.create_dummy_config)
        return
    
    if args.config is None:
        ap.error("--config is required (unless using --create_dummy_config)")
    
    try:
        run_smart_mapper(args.config, args.output_dir, args.run_id)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
