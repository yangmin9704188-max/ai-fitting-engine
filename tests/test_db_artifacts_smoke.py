#!/usr/bin/env python3
"""
Smoke test for artifacts table and layer indexing.

This test verifies:
1. Migration script creates artifacts table
2. Basic upsert to artifacts table works
3. Layer inference works
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.migrate_add_artifacts_table import run_migration
from tools.db_upsert import upsert_artifact, infer_layer_from_path, infer_measurement_key_from_path


def test_layer_inference():
    """Test layer inference from paths."""
    assert infer_layer_from_path("docs/policies/measurements/SEMANTIC_DEFINITION_CHEST_VNEXT.md") == "L1"
    assert infer_layer_from_path("docs/policies/measurements/CONTRACT_INTERFACE_CHEST_V0.md") == "L2"
    assert infer_layer_from_path("docs/policies/measurements/GEOMETRIC_DESIGN_CHEST_V0.md") == "L3"
    assert infer_layer_from_path("verification/reports/chest_v0/validation_results.csv") == "L4"
    assert infer_layer_from_path("docs/judgments/measurements/CHEST_V0_JUDGMENT.md") == "L5"
    assert infer_layer_from_path("unknown/path.txt") is None
    print("[PASS] Layer inference test passed")


def test_measurement_key_inference():
    """Test measurement key inference from paths."""
    assert infer_measurement_key_from_path("docs/policies/measurements/UNDERBUST_V0.md") == "UNDERBUST"
    assert infer_measurement_key_from_path("docs/policies/measurements/BUST_V0.md") == "BUST"
    assert infer_measurement_key_from_path("docs/policies/measurements/CHEST_V0.md") == "CHEST_LEGACY"
    assert infer_measurement_key_from_path("verification/reports/hip_v0/validation_results.csv") == "HIP"
    assert infer_measurement_key_from_path("unknown/path.txt") is None
    print("[PASS] Measurement key inference test passed")


def test_artifacts_table_creation():
    """Test that migration creates artifacts table."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_metadata.db"
        
        # Create minimal schema (policies and experiments tables)
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL UNIQUE,
                    run_id TEXT,
                    status TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()
        
        # Run migration
        run_migration(db_path)
        
        # Verify artifacts table exists
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='artifacts'
            """)
            result = cursor.fetchone()
            assert result is not None, "artifacts table should exist"
            
            # Verify schema
            cursor.execute("PRAGMA table_info(artifacts)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            assert "layer" in columns, "artifacts table should have layer column"
            assert "artifact_type" in columns, "artifacts table should have artifact_type column"
            assert "extra_json" in columns, "artifacts table should have extra_json column"
            
            print("[PASS] Artifacts table creation test passed")
        finally:
            conn.close()


def test_artifact_upsert():
    """Test basic artifact upsert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_metadata.db"
        
        # Create schema
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_type TEXT NOT NULL,
                    layer TEXT NOT NULL CHECK(layer IN ('L1', 'L2', 'L3', 'L4', 'L5')),
                    policy_id INTEGER,
                    experiment_id INTEGER,
                    related_measurement_key TEXT,
                    git_commit TEXT,
                    file_path TEXT,
                    artifacts_path TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    extra_json TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()
        
        # Test upsert
        conn = sqlite3.connect(str(db_path))
        try:
            # Upsert with section_id and method_tag
            success = upsert_artifact(
                conn,
                artifact_type="report",
                layer="L4",
                file_path="verification/reports/chest_v0/validation_results.csv",
                related_measurement_key="BUST",
                section_id="plane_y_0.85",
                method_tag="median_slice",
            )
            assert success, "upsert should succeed"
            conn.commit()
            
            # Verify data
            cursor = conn.cursor()
            cursor.execute("SELECT layer, related_measurement_key, extra_json FROM artifacts WHERE file_path = ?", 
                         ("verification/reports/chest_v0/validation_results.csv",))
            row = cursor.fetchone()
            assert row is not None, "artifact should be inserted"
            assert row[0] == "L4", "layer should be L4"
            assert row[1] == "BUST", "measurement_key should be BUST"
            
            extra_json = json.loads(row[2])
            assert extra_json["section_id"] == "plane_y_0.85", "section_id should be in extra_json"
            assert extra_json["method_tag"] == "median_slice", "method_tag should be in extra_json"
            
            print("[PASS] Artifact upsert test passed")
        finally:
            conn.close()


def main():
    """Run all smoke tests."""
    print("Running artifacts table smoke tests...\n")
    
    try:
        test_layer_inference()
        test_measurement_key_inference()
        test_artifacts_table_creation()
        test_artifact_upsert()
        
        print("\n[PASS] All smoke tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
