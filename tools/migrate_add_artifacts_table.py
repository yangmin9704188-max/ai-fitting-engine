#!/usr/bin/env python3
"""
Migration script: Add artifacts table for 5-Layer indexing

This script:
1. Creates automatic backup of db/metadata.db before migration
2. Adds artifacts table to schema
3. Performs minimal backfill from existing tables (specs, reports)
4. Logs skipped items (when layer cannot be determined)

Usage:
    python tools/migrate_add_artifacts_table.py [--db db/metadata.db]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def create_backup(db_path: Path) -> Path:
    """Create backup of database before migration."""
    backup_path = db_path.parent / f"{db_path.name}.bak"
    
    # If backup already exists, add timestamp
    if backup_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = db_path.parent / f"{db_path.name}.bak.{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"[OK] Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        raise RuntimeError(
            f"Failed to create backup: {e}\n"
            "Migration aborted for safety."
        ) from e


def infer_layer_from_path(file_path: Optional[str]) -> Optional[str]:
    """Infer layer from file path/name patterns."""
    if not file_path:
        return None
    
    path_lower = file_path.lower()
    
    # L1 Semantic
    if "semantic" in path_lower or "definition" in path_lower:
        return "L1"
    
    # L2 Contract
    if "contract" in path_lower or "interface" in path_lower:
        return "L2"
    
    # L3 Geometric
    if "geometric" in path_lower or "design" in path_lower:
        return "L3"
    
    # L4 Validation
    if "validation" in path_lower or "verify" in path_lower:
        return "L4"
    
    # L5 Judgment
    if "judgment" in path_lower:
        return "L5"
    
    return None


def infer_layer_from_spec_type(spec_type: Optional[str]) -> Optional[str]:
    """Infer layer from spec_type."""
    if not spec_type:
        return None
    
    spec_lower = spec_type.lower()
    
    if "semantic" in spec_lower:
        return "L1"
    if "contract" in spec_lower or "interface" in spec_lower:
        return "L2"
    if "geometric" in spec_lower or "design" in spec_lower:
        return "L3"
    if "validation" in spec_lower:
        return "L4"
    if "judgment" in spec_lower:
        return "L5"
    
    return None


def infer_measurement_key_from_path(file_path: Optional[str]) -> Optional[str]:
    """Infer measurement key from file path (UNDERBUST/BUST distinction)."""
    if not file_path:
        return None
    
    path_lower = file_path.lower()
    
    # Check for UNDERBUST
    if "underbust" in path_lower:
        return "UNDERBUST"
    
    # Check for BUST
    if "bust" in path_lower and "underbust" not in path_lower:
        return "BUST"
    
    # Legacy CHEST
    if "chest" in path_lower:
        return "CHEST_LEGACY"
    
    # Other measurements
    for key in ["hip", "waist", "thigh", "circumference", "shoulder"]:
        if key in path_lower:
            return key.upper()
    
    return None


def backfill_specs(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Backfill artifacts from specs table."""
    cursor = conn.cursor()
    
    # Check if specs table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='specs'
    """)
    if not cursor.fetchone():
        return 0, 0  # Table doesn't exist, skip
    
    cursor.execute("SELECT id, spec_type, git_commit, file_path FROM specs")
    specs = cursor.fetchall()
    
    inserted = 0
    skipped = 0
    
    for spec_id, spec_type, git_commit, file_path in specs:
        # Try to infer layer
        layer = infer_layer_from_spec_type(spec_type)
        if not layer:
            layer = infer_layer_from_path(file_path)
        
        if not layer:
            print(f"  [WARN] Skipped spec {spec_id}: cannot determine layer (type={spec_type}, path={file_path})")
            skipped += 1
            continue
        
        # Infer measurement key
        measurement_key = infer_measurement_key_from_path(file_path)
        
        # Insert artifact
        try:
            cursor.execute("""
                INSERT INTO artifacts (
                    artifact_type, layer, policy_id, related_measurement_key,
                    git_commit, file_path, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, (SELECT created_at FROM specs WHERE id = ?))
            """, (
                "spec",
                layer,
                None,  # policy_id would need join, skip for now
                measurement_key,
                git_commit,
                file_path,
                spec_id
            ))
            inserted += 1
        except sqlite3.Error as e:
            print(f"  [ERROR] Failed to insert spec {spec_id}: {e}")
            skipped += 1
    
    return inserted, skipped


def backfill_reports(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Backfill artifacts from reports table."""
    cursor = conn.cursor()
    
    # Check if reports table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='reports'
    """)
    if not cursor.fetchone():
        return 0, 0  # Table doesn't exist, skip
    
    # Try to get reports with artifacts_path
    cursor.execute("SELECT report_id, artifacts_path FROM reports WHERE artifacts_path IS NOT NULL")
    reports = cursor.fetchall()
    
    inserted = 0
    skipped = 0
    
    for report_id, artifacts_path in reports:
        # Infer layer from path
        layer = infer_layer_from_path(artifacts_path)
        
        # If validation-related path, assume L4
        if not layer:
            if "validation" in artifacts_path.lower() or "verify" in artifacts_path.lower():
                layer = "L4"
            elif "judgment" in artifacts_path.lower():
                layer = "L5"
        
        if not layer:
            print(f"  [WARN] Skipped report {report_id}: cannot determine layer (path={artifacts_path})")
            skipped += 1
            continue
        
        # Infer measurement key
        measurement_key = infer_measurement_key_from_path(artifacts_path)
        
        # Determine artifact_type
        artifact_type = "report"
        if "judgment" in artifacts_path.lower():
            artifact_type = "judgment_memo"
        
        # Insert artifact
        try:
            cursor.execute("""
                INSERT INTO artifacts (
                    artifact_type, layer, related_measurement_key,
                    artifacts_path, created_at
                )
                VALUES (?, ?, ?, ?, (SELECT created_at FROM reports WHERE report_id = ?))
            """, (
                artifact_type,
                layer,
                measurement_key,
                artifacts_path,
                report_id
            ))
            inserted += 1
        except sqlite3.Error as e:
            print(f"  [ERROR] Failed to insert report {report_id}: {e}")
            skipped += 1
    
    return inserted, skipped


def run_migration(db_path: Path) -> None:
    """Run migration: add artifacts table and backfill."""
    print(f"Starting migration on: {db_path}")
    
    # Step 1: Create backup
    backup_path = create_backup(db_path)
    
    # Step 2: Connect to database
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        
        # Step 3: Check if artifacts table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='artifacts'
        """)
        if cursor.fetchone():
            print("[WARN] artifacts table already exists. Skipping table creation.")
        else:
            # Step 4: Create artifacts table
            print("Creating artifacts table...")
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
                    extra_json TEXT,
                    FOREIGN KEY (policy_id) REFERENCES policies(id),
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_layer ON artifacts(layer)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_measurement_key ON artifacts(related_measurement_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_policy_id ON artifacts(policy_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_experiment_id ON artifacts(experiment_id)")
            
            conn.commit()
            print("[OK] artifacts table created")
        
        # Step 5: Backfill from existing tables
        print("\nBackfilling from existing tables...")
        
        # Backfill specs
        print("  Backfilling specs...")
        specs_inserted, specs_skipped = backfill_specs(conn)
        print(f"    [OK] Inserted: {specs_inserted}, Skipped: {specs_skipped}")
        
        # Backfill reports
        print("  Backfilling reports...")
        reports_inserted, reports_skipped = backfill_reports(conn)
        print(f"    [OK] Inserted: {reports_inserted}, Skipped: {reports_skipped}")
        
        conn.commit()
        
        total_inserted = specs_inserted + reports_inserted
        total_skipped = specs_skipped + reports_skipped
        
        print(f"\n[OK] Migration completed:")
        print(f"  Total inserted: {total_inserted}")
        print(f"  Total skipped: {total_skipped}")
        print(f"  Backup location: {backup_path}")
        
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Migration failed: {e}") from e
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate database: add artifacts table for 5-Layer indexing"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="db/metadata.db",
        help="Database path (default: db/metadata.db)"
    )
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    
    if not db_path.exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        run_migration(db_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
