#!/usr/bin/env python3
"""
DB Upsert - Single entry point for database writes

Purpose: Upsert experiment/report metadata to SQLite database.
Called by Antigravity after each experiment completion.

Usage:
    python tools/db_upsert.py --artifacts artifacts/runs/smart_mapper/20260120_120000
    python tools/db_upsert.py --report verification/reports/shoulder_width_v112/summary.json
    python tools/db_upsert.py --policy-md docs/policies/apose_normalization/v1.1.md
    python tools/db_upsert.py --report-md docs/reports/AN-v11-R1.md
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Optional


DB_PATH = "db/metadata.db"


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


def upsert_artifact(
    conn: sqlite3.Connection,
    artifact_type: str,
    layer: Optional[str],
    policy_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    related_measurement_key: Optional[str] = None,
    git_commit: Optional[str] = None,
    file_path: Optional[str] = None,
    artifacts_path: Optional[str] = None,
    status: Optional[str] = None,
    section_id: Optional[str] = None,
    method_tag: Optional[str] = None,
) -> bool:
    """
    Upsert artifact to artifacts table.
    
    Returns:
        True if upserted successfully, False if layer could not be determined (skipped)
    """
    # If layer not provided, try to infer
    if not layer:
        layer = infer_layer_from_path(file_path)
        if not layer:
            layer = infer_layer_from_path(artifacts_path)
    
    # If still no layer, skip (log warning but don't fail)
    if not layer:
        print(f"  [WARN] Skipped artifact upsert: cannot determine layer (type={artifact_type}, path={file_path or artifacts_path})")
        return False
    
    # If measurement_key not provided, try to infer
    if not related_measurement_key:
        related_measurement_key = infer_measurement_key_from_path(file_path)
        if not related_measurement_key:
            related_measurement_key = infer_measurement_key_from_path(artifacts_path)
    
    # Build extra_json
    extra_json_dict: Dict[str, Any] = {}
    if section_id:
        extra_json_dict["section_id"] = section_id
    if method_tag:
        extra_json_dict["method_tag"] = method_tag
    
    extra_json_str = json.dumps(extra_json_dict) if extra_json_dict else None
    
    cursor = conn.cursor()
    
    # Try to find existing artifact (by file_path or artifacts_path)
    existing_id = None
    if file_path:
        cursor.execute("SELECT id FROM artifacts WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        if row:
            existing_id = row[0]
    elif artifacts_path:
        cursor.execute("SELECT id FROM artifacts WHERE artifacts_path = ?", (artifacts_path,))
        row = cursor.fetchone()
        if row:
            existing_id = row[0]
    
    if existing_id:
        # Update existing
        cursor.execute("""
            UPDATE artifacts
            SET artifact_type = ?, layer = ?, policy_id = ?, experiment_id = ?,
                related_measurement_key = ?, git_commit = ?, file_path = ?,
                artifacts_path = ?, status = ?, extra_json = ?
            WHERE id = ?
        """, (
            artifact_type, layer, policy_id, experiment_id,
            related_measurement_key, git_commit, file_path,
            artifacts_path, status, extra_json_str, existing_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO artifacts (
                artifact_type, layer, policy_id, experiment_id,
                related_measurement_key, git_commit, file_path,
                artifacts_path, status, extra_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact_type, layer, policy_id, experiment_id,
            related_measurement_key, git_commit, file_path,
            artifacts_path, status, extra_json_str
        ))
    
    return True


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
        
        # Get experiment internal ID for artifact upsert
        cursor.execute("SELECT id FROM experiments WHERE experiment_id = ?", (run_id,))
        exp_row = cursor.fetchone()
        exp_internal_id = exp_row[0] if exp_row else None
        
        # Upsert artifact (L4 Validation for run artifacts)
        upsert_artifact(
            conn,
            artifact_type="run",
            layer="L4",  # Run artifacts are typically L4 Validation
            experiment_id=exp_internal_id,
            artifacts_path=artifacts_path,
            status=metadata.get("status", "completed"),
            section_id=metadata.get("section_id"),
            method_tag=metadata.get("method_tag"),
        )
        
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


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        raise ValueError(
            "No YAML frontmatter found in markdown file.\n"
            "File must start with '---' delimited frontmatter."
        )
    
    frontmatter: Dict[str, Any] = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value
    
    return frontmatter


def upsert_policy(policy_md_path: str, db_path: str) -> None:
    """Upsert policy metadata from markdown frontmatter."""
    policy_file = Path(policy_md_path)
    if not policy_file.exists():
        raise FileNotFoundError(
            f"Policy file not found: {policy_md_path}\n"
            "Please check the path and try again."
        )
    
    try:
        with open(policy_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read policy file: {e}") from e
    
    frontmatter = parse_frontmatter(content)
    
    # Extract required fields
    name = frontmatter.get("title")
    version = frontmatter.get("version")
    status = frontmatter.get("status", "").lower()
    created_date = frontmatter.get("created_date")
    frozen_commit_sha = frontmatter.get("frozen_commit_sha")
    frozen_git_tag = frontmatter.get("frozen_git_tag")
    
    if not name:
        raise ValueError("'title' field is required in frontmatter.")
    if not version:
        raise ValueError("'version' field is required in frontmatter.")
    if not status:
        raise ValueError("'status' field is required in frontmatter.")
    
    # Validate status
    valid_statuses = {'draft', 'candidate', 'frozen', 'archived', 'deprecated'}
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Upsert to database
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # Check if policy exists
        cursor.execute("SELECT id FROM policies WHERE name = ? AND version = ?", (name, version))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing policy
            cursor.execute("""
                UPDATE policies
                SET status = ?, created_at = ?, frozen_commit_sha = ?, frozen_git_tag = ?
                WHERE name = ? AND version = ?
            """, (status, created_date, frozen_commit_sha, frozen_git_tag, name, version))
        else:
            # Insert new policy
            cursor.execute("""
                INSERT INTO policies (name, version, status, created_at, frozen_commit_sha, frozen_git_tag)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, version, status, created_date, frozen_commit_sha, frozen_git_tag))
        
        # Get policy internal ID for artifact upsert
        cursor.execute("SELECT id FROM policies WHERE name = ? AND version = ?", (name, version))
        policy_row = cursor.fetchone()
        policy_internal_id = policy_row[0] if policy_row else None
        
        # Upsert artifact (L1 Semantic for policy documents)
        policy_file_path = str(policy_file)
        upsert_artifact(
            conn,
            artifact_type="policy",
            layer="L1",  # Policy documents are typically L1 Semantic
            policy_id=policy_internal_id,
            git_commit=frozen_commit_sha,
            file_path=policy_file_path,
        )
        
        conn.commit()
        print(f"Upserted policy: {name} {version} (status={status}, commit={frozen_commit_sha})")
        
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(
            f"Database error during policy upsert: {e}\n"
            "Please check database connection and schema."
        ) from e
    finally:
        conn.close()


def upsert_report_from_md(report_md_path: str, db_path: str) -> None:
    """Upsert report metadata from markdown frontmatter."""
    report_file = Path(report_md_path)
    if not report_file.exists():
        raise FileNotFoundError(
            f"Report file not found: {report_md_path}\n"
            "Please check the path and try again."
        )
    
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read report file: {e}") from e
    
    frontmatter = parse_frontmatter(content)
    
    # Extract required fields
    report_id = frontmatter.get("report_id")
    policy_name = frontmatter.get("policy_name")
    policy_version = frontmatter.get("policy_version")
    result = frontmatter.get("result", "").lower()
    created_date = frontmatter.get("created_date")
    artifacts_path = frontmatter.get("artifacts_path")
    inputs = frontmatter.get("inputs")
    
    if not report_id:
        raise ValueError("'report_id' field is required in frontmatter.")
    if not policy_name:
        raise ValueError("'policy_name' field is required in frontmatter.")
    if not policy_version:
        raise ValueError("'policy_version' field is required in frontmatter.")
    if not result:
        raise ValueError("'result' field is required in frontmatter.")
    if not created_date:
        raise ValueError("'created_date' field is required in frontmatter.")
    
    # Validate result
    valid_results = {'pass', 'fail', 'hold'}
    if result not in valid_results:
        raise ValueError(
            f"Invalid result '{result}'. Must be one of: {', '.join(valid_results)}"
        )
    
    # Upsert to database
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # Check if report exists
        cursor.execute("SELECT id FROM reports WHERE report_id = ?", (report_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing report
            cursor.execute("""
                UPDATE reports
                SET policy_name = ?, policy_version = ?, result = ?, created_at = ?,
                    artifacts_path = ?, inputs = ?
                WHERE report_id = ?
            """, (policy_name, policy_version, result, created_date, artifacts_path, inputs, report_id))
        else:
            # Insert new report
            cursor.execute("""
                INSERT INTO reports (report_id, policy_name, policy_version, result, created_at, artifacts_path, inputs)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (report_id, policy_name, policy_version, result, created_date, artifacts_path, inputs))
        
        # Upsert artifact (infer layer from artifacts_path)
        artifact_type = "report"
        if artifacts_path and "judgment" in artifacts_path.lower():
            artifact_type = "judgment_memo"
        
        upsert_artifact(
            conn,
            artifact_type=artifact_type,
            layer=None,  # Will be inferred from artifacts_path
            file_path=str(report_file),
            artifacts_path=artifacts_path,
        )
        
        conn.commit()
        print(f"Upserted report: {report_id} (result={result}, policy={policy_name} {policy_version})")
        
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(
            f"Database error during report upsert: {e}\n"
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
        
        # Upsert artifact (L4 Validation for verification reports)
        artifacts_path = report_data.get("artifacts_path")
        artifact_type = report_data.get("report_type", "report")
        if "judgment" in str(artifacts_path).lower() if artifacts_path else False:
            artifact_type = "judgment_memo"
        
        # Extract section_id and method_tag from report data if available
        metrics = report_data.get("metrics", {})
        section_id = metrics.get("section_id")
        method_tag = metrics.get("method_tag")
        
        upsert_artifact(
            conn,
            artifact_type=artifact_type,
            layer="L4",  # Verification reports are typically L4
            experiment_id=exp_internal_id,
            artifacts_path=artifacts_path,
            section_id=section_id,
            method_tag=method_tag,
        )
        
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
        "--policy-md",
        type=str,
        help="Path to policy markdown file (with frontmatter)"
    )
    parser.add_argument(
        "--report-md",
        type=str,
        help="Path to report markdown file (with frontmatter)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=DB_PATH,
        help=f"Database path (default: {DB_PATH})"
    )
    
    args = parser.parse_args()
    
    # Count specified options
    option_count = sum([bool(args.artifacts), bool(args.report), bool(args.policy_md), bool(args.report_md)])
    
    if option_count == 0:
        print("Error: One of --artifacts, --report, --policy-md, or --report-md must be specified", file=sys.stderr)
        sys.exit(1)
    
    if option_count > 1:
        print("Error: Cannot specify multiple options at once", file=sys.stderr)
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
        elif args.report:
            upsert_from_report(args.report, str(db_path))
        elif args.policy_md:
            upsert_policy(args.policy_md, str(db_path))
        else:
            upsert_report_from_md(args.report_md, str(db_path))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
