#!/usr/bin/env python3
"""
Round Registry Maintenance Tool

round_registry.json을 자동으로 갱신합니다.
Facts-only 기록이며, "어떤 run_dir가 있었고 무엇을 생성했는지"만 기록합니다.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def normalize_path_to_relative(path_str: Optional[str]) -> Optional[str]:
    """
    Normalize path to repo-relative path (forward slashes, no absolute paths).
    Returns None if path_str is None or cannot be normalized.
    """
    if not path_str:
        return None
    
    try:
        # Convert backslashes to forward slashes (Windows compatibility)
        normalized = path_str.replace("\\", "/")
        
        # If absolute path, try to convert to relative
        path_obj = Path(normalized)
        if path_obj.is_absolute():
            try:
                # Try to make it relative to project_root
                normalized = str(path_obj.relative_to(project_root))
                # Ensure forward slashes
                normalized = normalized.replace("\\", "/")
            except ValueError:
                # Cannot make relative, return as-is but with forward slashes
                pass
        
        return normalized
    except Exception:
        # If normalization fails, return original with forward slashes
        return path_str.replace("\\", "/") if path_str else None


def extract_round_info(run_dir: Path) -> tuple[str, Optional[int], str]:
    """Extract lane, round_num, round_id from run_dir path."""
    # Example: verification/runs/facts/curated_v0/round20_20260125_164801
    parts = run_dir.parts
    
    # Extract lane
    lane = "unknown"
    try:
        facts_idx = parts.index("facts")
        if facts_idx + 1 < len(parts):
            lane = parts[facts_idx + 1]
    except ValueError:
        pass
    
    # Extract round_id and round_num
    run_name = run_dir.name
    round_match = re.search(r'round(\d+)', run_name, re.IGNORECASE)
    if round_match:
        round_num = int(round_match.group(1))
        round_id = run_name
    else:
        round_num = None
        round_id = run_name
    
    return lane, round_num, round_id


def normalize_registry_paths(registry: Dict[str, Any]) -> None:
    """Normalize all paths in registry to repo-relative (forward slashes)."""
    if "lanes" not in registry:
        return
    
    for lane_data in registry["lanes"].values():
        # Normalize baseline paths
        if lane_data.get("baseline"):
            baseline = lane_data["baseline"]
            baseline["run_dir"] = normalize_path_to_relative(baseline.get("run_dir"))
            baseline["report"] = normalize_path_to_relative(baseline.get("report"))
        
        # Normalize latest paths
        if lane_data.get("latest"):
            latest = lane_data["latest"]
            latest["run_dir"] = normalize_path_to_relative(latest.get("run_dir"))
        
        # Normalize round entry paths
        for round_entry in lane_data.get("rounds", []):
            round_entry["run_dir"] = normalize_path_to_relative(round_entry.get("run_dir"))
            round_entry["facts_summary"] = normalize_path_to_relative(round_entry.get("facts_summary"))
            round_entry["report"] = normalize_path_to_relative(round_entry.get("report"))
            round_entry["kpi"] = normalize_path_to_relative(round_entry.get("kpi"))
            round_entry["kpi_diff"] = normalize_path_to_relative(round_entry.get("kpi_diff"))
            round_entry["source_npz"] = normalize_path_to_relative(round_entry.get("source_npz"))
            # source_path_abs is intentionally kept as absolute (external reference)


def load_registry(registry_path: Path) -> Dict[str, Any]:
    """Load round registry and normalize paths."""
    if not registry_path.exists():
        return {
            "schema_version": "round_registry@1",
            "updated_at": datetime.now().isoformat(),
            "lanes": {}
        }
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        # Ensure schema_version
        if "schema_version" not in registry:
            registry["schema_version"] = "round_registry@1"
        
        # Ensure lanes
        if "lanes" not in registry:
            registry["lanes"] = {}
        
        # Normalize all paths in loaded registry
        normalize_registry_paths(registry)
        
        return registry
    except Exception as e:
        print(f"Warning: Failed to load registry: {e}", file=sys.stderr)
        return {
            "schema_version": "round_registry@1",
            "updated_at": datetime.now().isoformat(),
            "lanes": {}
        }


def ensure_baseline(registry: Dict[str, Any], lane: str, baselines: Dict[str, Any]) -> None:
    """Ensure baseline exists in registry (immutable once set)."""
    if "lanes" not in registry:
        registry["lanes"] = {}
    
    if lane not in registry["lanes"]:
        registry["lanes"][lane] = {
            "baseline": None,
            "rounds": [],
            "latest": None
        }
    
    lane_data = registry["lanes"][lane]
    
    # If baseline already exists, normalize its paths but don't change values
    if lane_data.get("baseline") is not None:
        baseline = lane_data["baseline"]
        baseline["run_dir"] = normalize_path_to_relative(baseline.get("run_dir"))
        baseline["report"] = normalize_path_to_relative(baseline.get("report"))
        return
    
    # Set initial baseline from baselines.json
    lane_config = baselines.get(lane, {})
    if lane_config:
        baseline_alias = lane_config.get("baseline_tag_alias")
        baseline_run_dir = lane_config.get("baseline_run_dir")
        baseline_report = lane_config.get("baseline_report")
        
        if baseline_alias and baseline_run_dir:
            lane_data["baseline"] = {
                "alias": baseline_alias,
                "run_dir": normalize_path_to_relative(baseline_run_dir),
                "report": normalize_path_to_relative(baseline_report)
            }


def find_round_entry(rounds: List[Dict[str, Any]], round_id: str) -> Optional[int]:
    """Find index of round entry with given round_id."""
    for i, entry in enumerate(rounds):
        if entry.get("round_id") == round_id:
            return i
    return None


def extract_source_info(facts_summary_path: Optional[Path]) -> tuple[Optional[str], Optional[str]]:
    """Extract source_npz and source_path_abs from facts_summary.json."""
    if not facts_summary_path or not facts_summary_path.exists():
        return None, None
    
    try:
        with open(facts_summary_path, "r", encoding="utf-8") as f:
            facts_data = json.load(f)
        
        # Extract source_npz (dataset_path or npz_path_abs)
        source_npz = facts_data.get("dataset_path") or facts_data.get("npz_path_abs")
        if source_npz:
            source_npz_path = Path(source_npz)
            if source_npz_path.is_absolute():
                # Convert to relative if possible
                try:
                    source_npz = str(source_npz_path.relative_to(project_root))
                except ValueError:
                    source_npz = str(source_npz_path)
            # Normalize path (forward slashes)
            source_npz = normalize_path_to_relative(source_npz)
        
        # Extract source_path_abs
        source_path_abs = facts_data.get("source_path_abs")
        if source_path_abs:
            source_path_abs = str(Path(source_path_abs).resolve())
        
        return source_npz, source_path_abs
    except Exception:
        return None, None


def check_artifacts_exist(run_dir: Path) -> Dict[str, bool]:
    """Check which artifacts exist in run_dir."""
    return {
        "kpi": (run_dir / "KPI.md").exists(),
        "kpi_diff": (run_dir / "KPI_DIFF.md").exists()
    }


def update_registry(
    registry_path: Path,
    current_run_dir: Path,
    facts_summary_path: Optional[Path],
    lane: str,
    round_num: Optional[int],
    round_id: str,
    baselines: Dict[str, Any],
    coverage_backlog_touched: bool
) -> None:
    """Update round registry with current round information."""
    registry = load_registry(registry_path)
    
    # Ensure baseline
    ensure_baseline(registry, lane, baselines)
    
    # Ensure lane structure
    if lane not in registry["lanes"]:
        registry["lanes"][lane] = {
            "baseline": None,
            "rounds": [],
            "latest": None
        }
    
    lane_data = registry["lanes"][lane]
    rounds = lane_data.get("rounds", [])
    
    # Extract source info
    source_npz, source_path_abs = extract_source_info(facts_summary_path)
    
    # Check artifacts
    artifacts = check_artifacts_exist(current_run_dir)
    
    # Determine report path (standardized to lanes/<lane>/)
    report_path = None
    # Check if report already exists in registry (preserve existing)
    existing_idx = find_round_entry(rounds, round_id)
    if existing_idx is not None:
        existing_entry = rounds[existing_idx]
        report_path = existing_entry.get("report")
    
    # If no existing report, try baseline
    if not report_path and lane_data.get("baseline") and lane_data["baseline"].get("report"):
        report_path = lane_data["baseline"]["report"]
    
    # If still no report, use standardized lanes path (but don't create file yet)
    if not report_path:
        # Standardized path: reports/validation/lanes/<lane>/<round_id>_facts.md
        report_path = f"reports/validation/lanes/{lane}/{round_id}_facts.md"
    
    # Normalize report path
    report_path = normalize_path_to_relative(report_path)
    
    # Create or update round entry (all paths normalized)
    round_entry = {
        "round_id": round_id,
        "round_num": round_num,
        "run_dir": normalize_path_to_relative(str(current_run_dir.relative_to(project_root))),
        "facts_summary": normalize_path_to_relative(str(facts_summary_path.relative_to(project_root))) if facts_summary_path else None,
        "report": report_path,
        "kpi": normalize_path_to_relative(str((current_run_dir / "KPI.md").relative_to(project_root))) if artifacts["kpi"] else None,
        "kpi_diff": normalize_path_to_relative(str((current_run_dir / "KPI_DIFF.md").relative_to(project_root))) if artifacts["kpi_diff"] else None,
        "coverage_backlog_touched": coverage_backlog_touched,
        "created_at": datetime.now().isoformat(),
        "source_npz": normalize_path_to_relative(source_npz),
        "source_path_abs": source_path_abs,  # Keep absolute for source_path_abs (external reference)
        "notes": ""
    }
    
    # Update existing entry or append new
    if existing_idx is not None:
        # Preserve existing report path if it exists and is not None
        existing_report = rounds[existing_idx].get("report")
        if existing_report:
            round_entry["report"] = normalize_path_to_relative(existing_report)
        # Update existing entry
        rounds[existing_idx] = round_entry
    else:
        # Append new entry
        rounds.append(round_entry)
    
    # Update latest (normalized)
    lane_data["latest"] = {
        "round_id": round_id,
        "run_dir": normalize_path_to_relative(str(current_run_dir.relative_to(project_root)))
    }
    
    # Update registry metadata
    registry["updated_at"] = datetime.now().isoformat()
    registry["lanes"][lane] = lane_data
    
    # Atomic write
    temp_path = registry_path.with_suffix(".json.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        # Ensure parent directory exists
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic rename
        shutil.move(str(temp_path), str(registry_path))
        
        print(f"Updated: {registry_path}")
    except Exception as e:
        print(f"Error: Failed to write registry: {e}", file=sys.stderr)
        if temp_path.exists():
            temp_path.unlink()
        raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update round registry"
    )
    parser.add_argument(
        "--registry_path",
        type=str,
        default="docs/verification/round_registry.json",
        help="Round registry path"
    )
    parser.add_argument(
        "--current_run_dir",
        type=str,
        required=True,
        help="Current run directory path"
    )
    parser.add_argument(
        "--facts_summary",
        type=str,
        default=None,
        help="Path to facts_summary.json (optional, will search if not provided)"
    )
    parser.add_argument(
        "--coverage_backlog_touched",
        action="store_true",
        help="Whether coverage_backlog was updated"
    )
    
    args = parser.parse_args()
    
    registry_path = project_root / args.registry_path
    current_run_dir = (project_root / args.current_run_dir).resolve()
    
    # Find facts_summary if not provided
    facts_summary_path = None
    if args.facts_summary:
        facts_summary_path = (project_root / args.facts_summary).resolve()
    else:
        # Search in run_dir
        candidate = current_run_dir / "facts_summary.json"
        if candidate.exists():
            facts_summary_path = candidate
        else:
            # Search subdirectories
            for subdir in current_run_dir.iterdir():
                if subdir.is_dir():
                    candidate = subdir / "facts_summary.json"
                    if candidate.exists():
                        facts_summary_path = candidate
                        break
    
    if not facts_summary_path:
        print(f"Warning: facts_summary.json not found in {current_run_dir}", file=sys.stderr)
    
    # Load baselines
    baselines_path = project_root / "docs" / "ops" / "baselines.json"
    baselines = {}
    if baselines_path.exists():
        try:
            with open(baselines_path, "r", encoding="utf-8") as f:
                baselines = json.load(f)
        except Exception:
            pass
    
    # Extract round info
    lane, round_num, round_id = extract_round_info(current_run_dir)
    
    # Update registry
    update_registry(
        registry_path=registry_path,
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=lane,
        round_num=round_num,
        round_id=round_id,
        baselines=baselines,
        coverage_backlog_touched=args.coverage_backlog_touched
    )


if __name__ == "__main__":
    main()
