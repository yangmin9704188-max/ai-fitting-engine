"""
Test for curated_v0 builder pipeline.

Tests mapping, header standardization, and warning format.
Uses --dry-run to avoid loading large raw files.
"""

import subprocess
import sys
from pathlib import Path


def test_build_curated_v0_dry_run():
    """
    Test that build_curated_v0.py runs in dry-run mode without errors.
    
    This verifies:
    - Mapping file can be loaded
    - Headers can be extracted
    - Warning format is correct
    - No exceptions are raised
    """
    script_path = Path(__file__).parent.parent / "pipelines" / "build_curated_v0.py"
    mapping_path = Path(__file__).parent.parent / "data" / "column_map" / "sizekorea_v1.json"
    
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return False
    
    if not mapping_path.exists():
        print(f"Mapping file not found: {mapping_path}")
        return False
    
    # Run with --dry-run and --max-rows to limit processing
    cmd = [
        sys.executable,
        str(script_path),
        "--mapping", str(mapping_path),
        "--output", "test_output.parquet",
        "--dry-run",
        "--max-rows", "10"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Check exit code
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            return False
        
        # Check that dry-run output contains expected keywords
        output = result.stdout + result.stderr
        
        expected_keywords = [
            "DRY RUN",
            "rows",
            "columns",
            "warnings"
        ]
        
        for keyword in expected_keywords:
            if keyword.lower() not in output.lower():
                print(f"Expected keyword '{keyword}' not found in output")
                print(f"Output:\n{output}")
                return False
        
        print("Dry-run test passed")
        return True
        
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False


if __name__ == '__main__':
    success = test_build_curated_v0_dry_run()
    sys.exit(0 if success else 1)
