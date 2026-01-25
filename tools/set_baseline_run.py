#!/usr/bin/env python3
"""
Set Baseline Run Tool

Baseline run directory를 _baseline.json에 기록합니다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(
        description="Set baseline run directory"
    )
    parser.add_argument(
        "--run_dir",
        type=str,
        required=True,
        help="Baseline run directory path"
    )
    
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Verify kpi.json exists
    kpi_json = run_dir / "kpi.json"
    if not kpi_json.exists():
        print(f"Warning: kpi.json not found in {run_dir}", file=sys.stderr)
        print(f"  Run postprocess_round.py first to generate kpi.json", file=sys.stderr)
    
    # Save baseline.json
    baseline_json = project_root / "verification" / "runs" / "facts" / "_baseline.json"
    baseline_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Use relative path from project root
    run_dir_rel = run_dir.relative_to(project_root)
    
    baseline_data = {
        "baseline_run_dir": str(run_dir_rel)
    }
    
    with open(baseline_json, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=2, ensure_ascii=False)
    
    print(f"Baseline set to: {run_dir_rel}")
    print(f"Saved to: {baseline_json}")


if __name__ == "__main__":
    main()
