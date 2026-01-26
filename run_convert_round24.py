#!/usr/bin/env python3
"""Temporary script to run convert_scan_xlsx_to_csv.py with proper encoding."""
import subprocess
import sys
from pathlib import Path

# Ensure we're in the repo root
repo_root = Path(__file__).parent
if not (repo_root / "20F_data.xlsx").exists():
    print(f"ERROR: 20F_data.xlsx not found in {repo_root}")
    sys.exit(1)

cmd = [
    sys.executable,
    str(repo_root / "verification" / "tools" / "convert_scan_xlsx_to_csv.py"),
    "--input_xlsx", str(repo_root / "20F_data.xlsx"),
    "--out_dir", "verification/datasets/golden/s1_mesh_v0/metadata",
    "--source_id", "scan_6th_20F",
    "--raw_unit", "mm",
    "--meta_unit", "m",
    "--precision", "0.001",
    "--major_names", "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
]

print(f"[RUN] Executing: {' '.join(cmd)}")
result = subprocess.run(cmd, cwd=str(repo_root), encoding='utf-8', errors='replace')
sys.exit(result.returncode)
