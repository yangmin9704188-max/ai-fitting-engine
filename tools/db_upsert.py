#!/usr/bin/env python3
"""
DB Upsert - Single entry point for database writes

Purpose: Upsert experiment/report metadata to SQLite database.
Called by Antigravity after each experiment completion.

Usage:
    python tools/db_upsert.py --artifacts artifacts/runs/smart_mapper/20260120_120000
    python tools/db_upsert.py --report verification/reports/shoulder_width_v112/summary.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Optional


DB_PATH = "db/metadata.db"


def ensure_db_schema(db_path: str) -> None:
    """Ensure database schema exists."""
    schema_path = Path("db/schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {schema_path}\n"
            "Please ensure db/schema.sql exists."
        )
    
    conn = sqlite3.connect(db_path)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    except Exception as e:
        conn.close()
        raise RuntimeError(
            f"Failed to initialize database schema: {e}\n"
            "Please check db/schema.sql syntax."
        ) from e
    finally:
        conn.close()


def upsert_from_artifacts(artifacts_path: str, db_path: str) -> None:
    """Upsert metadata from artifacts run folder."""
    artifacts_dir = Path(artifacts_path)
    if not artifacts_dir.exists():
        raise FileNotFoundError(
            f"Artifacts directory not found: {artifacts_path}\n"
            "Please check the path and try again."
        )
    
    # Look for manifest.json or result.json
    manifest_path = artifacts_dir / "manifest.json"
    result_path = artifacts_dir / "result.json"
    
    if not manifest_path.exists() and not result_path.exists():
        raise FileNotFoundError(
            f"No manifest.json or result.json found in: {artifacts_path}\n"
            "Artifacts folder must contain at least one of these files."
        )
    
    # Load metadata
    metadata: Dict[str, Any] = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                metadata.update(json.load(f))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in manifest.json: {e}\n"
                "Please check the file format."
            ) from e
    
    if result_path.exists():
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                result_data = json.load(f)
                metadata.setdefault("result", result_data)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in result.json: {e}\n"
                "Please check the file format."
            ) from e
    
    # Extract run_id
    run_id = metadata.get("run_id")
    if not run_id:
        raise ValueError(
            "run_id not found in metadata.\n"
            "manifest.json or result.json must contain 'run_id' field."
        )
    
    # Upsert to database
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # Upsert experiment
        cursor.execute("""
            INSERT OR REPLACE INTO experiments (experiment_id, run_id, status, extra_json)
            VALUES (?, ?, ?, ?)
        """, (
            run_id,
            run_id,
            metadata.get("status", "completed"),
            json.dumps(metadata.get("extra", {}))
        ))
        
        conn.commit()
        print(f"Upserted experiment: {run_id}")
        
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(
            f"Database error during upsert: {e}\n"
            "Please check database connection and schema."
        ) from e
    finally:
        conn.close()


def upsert_from_report(report_path: str, db_path: str) -> None:
    """Upsert metadata from report JSON file."""
    report_file = Path(report_path)
    if not report_file.exists():
        raise FileNotFoundError(
            f"Report file not found: {report_path}\n"
            "Please check the path and try again."
        )
    
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON in report file: {e}\n"
            "Please check the file format."
        ) from e
    
    # Extract experiment_id
    experiment_id = report_data.get("experiment_id") or report_data.get("run_id")
    if not experiment_id:
        raise ValueError(
            "experiment_id or run_id not found in report.\n"
            "Report JSON must contain 'experiment_id' or 'run_id' field."
        )
    
    # Upsert to database
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # Ensure experiment exists
        cursor.execute("""
            INSERT OR IGNORE INTO experiments (experiment_id, run_id, status)
            VALUES (?, ?, ?)
        """, (experiment_id, experiment_id, "completed"))
        
        # Get experiment internal ID
        cursor.execute("SELECT id FROM experiments WHERE experiment_id = ?", (experiment_id,))
        exp_row = cursor.fetchone()
        if not exp_row:
            raise RuntimeError(f"Failed to create/find experiment: {experiment_id}")
        exp_internal_id = exp_row[0]
        
        # Upsert report
        cursor.execute("""
            INSERT OR REPLACE INTO reports (
                experiment_id, report_type, result, gate_failed,
                evaluated_policy_commit, verification_tool_commit,
                artifacts_path, dataset, metrics_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exp_internal_id,
            report_data.get("report_type", "verification"),
            report_data.get("result"),
            report_data.get("gate_failed"),
            report_data.get("evaluated_policy_commit"),
            report_data.get("verification_tool_commit"),
            report_data.get("artifacts_path"),
            report_data.get("dataset"),
            json.dumps(report_data.get("metrics", {}))
        ))
        
        conn.commit()
        print(f"Upserted report for experiment: {experiment_id}")
        
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(
            f"Database error during upsert: {e}\n"
            "Please check database connection and schema."
        ) from e
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Upsert experiment/report metadata to SQLite database"
    )
    parser.add_argument(
        "--artifacts",
        type=str,
        help="Path to artifacts run folder (must contain manifest.json or result.json)"
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Path to report JSON file"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=DB_PATH,
        help=f"Database path (default: {DB_PATH})"
    )
    
    args = parser.parse_args()
    
    if not args.artifacts and not args.report:
        print("Error: Either --artifacts or --report must be specified", file=sys.stderr)
        sys.exit(1)
    
    if args.artifacts and args.report:
        print("Error: Cannot specify both --artifacts and --report", file=sys.stderr)
        sys.exit(1)
    
    # Ensure database directory exists
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure schema exists
    try:
        ensure_db_schema(str(db_path))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Upsert based on input type
    try:
        if args.artifacts:
            upsert_from_artifacts(args.artifacts, str(db_path))
        else:
            upsert_from_report(args.report, str(db_path))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
