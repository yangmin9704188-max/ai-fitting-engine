#!/usr/bin/env python3
import subprocess
import sys

# Run conversion with proper encoding
cmd = [
    sys.executable,
    "verification/tools/convert_scan_xlsx_to_csv.py",
    "--input_xlsx", "./20F_data.xlsx",
    "--out_dir", "verification/datasets/golden/s1_mesh_v0/metadata",
    "--source_id", "scan_6th_20F",
    "--raw_unit", "mm",
    "--meta_unit", "m",
    "--precision", "0.001",
    "--major_names", "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
]

result = subprocess.run(cmd, encoding='utf-8', errors='replace')
sys.exit(result.returncode)
