#!/usr/bin/env python3
"""
Round Postprocessing Tool (round3)

라운드 마감 단일 엔트리포인트:
- KPI 생성 (KPI.md)
- KPI_DIFF 생성 (KPI_DIFF.md)
- Prev/Baseline 자동 해석
- Round Registry 기록
- Coverage Backlog 갱신
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def find_facts_summary(run_dir: Path, required: bool = True) -> Optional[Path]:
    """Find facts_summary.json in run_dir with priority."""
    # Priority 1: direct path
    facts_path = run_dir / "facts_summary.json"
    if facts_path.exists():
        return facts_path
    
    # Priority 2: search in subdirectories
    for subdir in run_dir.iterdir():
        if subdir.is_dir():
            candidate = subdir / "facts_summary.json"
            if candidate.exists():
                return candidate
    
    if required:
        print(f"Error: facts_summary.json not found in {run_dir}", file=sys.stderr)
        print(f"  Searched: {run_dir}/facts_summary.json", file=sys.stderr)
        print(f"  And subdirectories", file=sys.stderr)
        sys.exit(2)
    
    return None


def infer_lane_from_path(run_dir: Path) -> str:
    """Infer lane from run_dir path."""
    # Example: verification/runs/facts/curated_v0/round20_... -> curated_v0
    parts = run_dir.parts
    try:
        facts_idx = parts.index("facts")
        if facts_idx + 1 < len(parts):
            return parts[facts_idx + 1]
    except ValueError:
        pass
    
    # Fallback: use parent directory name
    return run_dir.parent.name


def load_baselines() -> Dict[str, Any]:
    """Load baselines.json."""
    baselines_path = project_root / "docs" / "ops" / "baselines.json"
    if not baselines_path.exists():
        return {}
    
    try:
        with open(baselines_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load baselines.json: {e}", file=sys.stderr)
        return {}


def get_baseline_run_dir(lane: str, baselines: Dict[str, Any], explicit_baseline: Optional[str] = None) -> Optional[Path]:
    """Get baseline run directory."""
    if explicit_baseline:
        baseline_path = project_root / explicit_baseline
        if baseline_path.exists():
            return baseline_path.resolve()
        return None
    
    lane_config = baselines.get(lane, {})
    baseline_rel = lane_config.get("baseline_run_dir")
    if baseline_rel:
        baseline_path = project_root / baseline_rel
        if baseline_path.exists():
            return baseline_path.resolve()
    
    return None


def load_round_registry(registry_path: Path) -> List[Dict[str, Any]]:
    """Load round registry."""
    if not registry_path.exists():
        return []
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load round registry: {e}", file=sys.stderr)
        return []


def get_prev_run_dir(lane: str, registry: List[Dict[str, Any]], baseline_run_dir: Optional[Path]) -> Optional[Path]:
    """Get previous run directory from registry."""
    # Find last entry for same lane
    for entry in reversed(registry):
        if entry.get("lane") == lane:
            prev_rel = entry.get("current_run_dir")
            if prev_rel:
                prev_path = project_root / prev_rel
                if prev_path.exists():
                    return prev_path.resolve()
    
    # Fallback to baseline
    return baseline_run_dir


def generate_kpi(run_dir: Path, facts_summary_path: Path) -> Path:
    """Generate KPI.md using summarize_facts_kpi.py."""
    kpi_md_path = run_dir / "KPI.md"
    
    # Call summarize_facts_kpi.py
    cmd = [
        sys.executable,
        str(project_root / "tools" / "summarize_facts_kpi.py"),
        str(facts_summary_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
    if result.returncode != 0:
        print(f"Error: Failed to generate KPI: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    # Save KPI.md
    with open(kpi_md_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)
    
    print(f"Generated: {kpi_md_path}")
    return kpi_md_path


def generate_kpi_diff(
    current_run_dir: Path,
    current_facts_path: Path,
    prev_run_dir: Optional[Path],
    baseline_run_dir: Optional[Path]
) -> None:
    """Generate KPI_DIFF.md using summarize_facts_kpi.py."""
    from tools.summarize_facts_kpi import generate_kpi_diff as gen_diff
    
    # Find prev and baseline facts_summary.json
    prev_facts_path = find_facts_summary(prev_run_dir, required=False) if prev_run_dir else None
    baseline_facts_path = find_facts_summary(baseline_run_dir, required=False) if baseline_run_dir else None
    
    if not prev_facts_path and prev_run_dir:
        print(f"Warning: prev facts_summary.json not found in {prev_run_dir}", file=sys.stderr)
    
    if not baseline_facts_path and baseline_run_dir:
        print(f"Warning: baseline facts_summary.json not found in {baseline_run_dir}", file=sys.stderr)
    
    # Generate diff
    diff_md = gen_diff(
        current_path=current_facts_path,
        prev_path=prev_facts_path,
        baseline_path=baseline_facts_path,
        current_run_dir=str(current_run_dir.relative_to(project_root)),
        prev_run_dir=str(prev_run_dir.relative_to(project_root)) if prev_run_dir else None,
        baseline_run_dir=str(baseline_run_dir.relative_to(project_root)) if baseline_run_dir else None
    )
    
    # Save KPI_DIFF.md
    diff_path = current_run_dir / "KPI_DIFF.md"
    with open(diff_path, "w", encoding="utf-8") as f:
        f.write(diff_md)
    
    print(f"Generated: {diff_path}")


def update_coverage_backlog(
    facts_summary_path: Path,
    run_dir: Path,
    registry_path: Path
) -> None:
    """Update coverage backlog using coverage_backlog.py."""
    from tools.coverage_backlog import update_coverage_backlog as update_backlog
    
    update_backlog(
        facts_summary_path=facts_summary_path,
        run_dir=run_dir,
        registry_path=registry_path
    )


def get_git_commit() -> Optional[str]:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        return result.stdout.strip()
    except Exception:
        return None


def update_round_registry(
    registry_path: Path,
    current_run_dir: Path,
    facts_summary_path: Path,
    kpi_path: Path,
    lane: str,
    baseline_run_dir: Optional[Path],
    prev_run_dir: Optional[Path],
    baselines: Dict[str, Any]
) -> None:
    """Update round registry with new entry."""
    registry = load_round_registry(registry_path)
    
    # Get baseline tag alias
    baseline_tag_alias = None
    lane_config = baselines.get(lane, {})
    if lane_config:
        baseline_tag_alias = lane_config.get("baseline_tag_alias")
    
    entry = {
        "created_at": datetime.now().isoformat(),
        "lane": lane,
        "current_run_dir": str(current_run_dir.relative_to(project_root)),
        "current_run_dir_abs": str(current_run_dir.resolve()),
        "facts_summary_path": str(facts_summary_path.resolve()),
        "kpi_path": str(kpi_path.resolve()),
        "baseline_run_dir": str(baseline_run_dir.relative_to(project_root)) if baseline_run_dir else None,
        "baseline_run_dir_abs": str(baseline_run_dir.resolve()) if baseline_run_dir else None,
        "prev_run_dir": str(prev_run_dir.relative_to(project_root)) if prev_run_dir else None,
        "prev_run_dir_abs": str(prev_run_dir.resolve()) if prev_run_dir else None,
        "git_commit": get_git_commit(),
        "baseline_tag_alias": baseline_tag_alias
    }
    
    registry.append(entry)
    
    # Ensure parent directory exists
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save registry
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"Updated: {registry_path} ({len(registry)} entries)")


def main():
    parser = argparse.ArgumentParser(
        description="Round postprocessing tool (round3)"
    )
    parser.add_argument(
        "--current_run_dir",
        type=str,
        required=True,
        help="Current run directory path"
    )
    parser.add_argument(
        "--lane",
        type=str,
        default=None,
        help="Lane name (default: inferred from current_run_dir path)"
    )
    parser.add_argument(
        "--baseline_run_dir",
        type=str,
        default=None,
        help="Baseline run directory (default: loaded from baselines.json)"
    )
    parser.add_argument(
        "--registry_path",
        type=str,
        default="reports/validation/round_registry.json",
        help="Round registry path (default: reports/validation/round_registry.json)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    current_run_dir = (project_root / args.current_run_dir).resolve()
    if not current_run_dir.exists():
        print(f"Error: Current run directory not found: {current_run_dir}", file=sys.stderr)
        sys.exit(1)
    
    registry_path = project_root / args.registry_path
    
    # Infer lane if not provided
    lane = args.lane or infer_lane_from_path(current_run_dir)
    print(f"Lane: {lane}")
    
    # Load baselines
    baselines = load_baselines()
    
    # Get baseline run directory
    baseline_run_dir = get_baseline_run_dir(lane, baselines, args.baseline_run_dir)
    if baseline_run_dir:
        print(f"Baseline: {baseline_run_dir.relative_to(project_root)}")
    else:
        print("Baseline: None")
    
    # Load registry and get prev run directory
    registry = load_round_registry(registry_path)
    prev_run_dir = get_prev_run_dir(lane, registry, baseline_run_dir)
    if prev_run_dir:
        print(f"Prev: {prev_run_dir.relative_to(project_root)}")
    else:
        print("Prev: None")
    
    # Find facts_summary.json
    facts_summary_path = find_facts_summary(current_run_dir, required=True)
    if not facts_summary_path:
        sys.exit(2)
    print(f"Facts summary: {facts_summary_path.relative_to(project_root)}")
    
    # Generate KPI
    kpi_path = generate_kpi(current_run_dir, facts_summary_path)
    
    # Generate KPI_DIFF
    generate_kpi_diff(
        current_run_dir=current_run_dir,
        current_facts_path=facts_summary_path,
        prev_run_dir=prev_run_dir,
        baseline_run_dir=baseline_run_dir
    )
    
    # Update registry
    update_round_registry(
        registry_path=registry_path,
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        kpi_path=kpi_path,
        lane=lane,
        baseline_run_dir=baseline_run_dir,
        prev_run_dir=prev_run_dir,
        baselines=baselines
    )
    
    # Update coverage backlog
    update_coverage_backlog(
        facts_summary_path=facts_summary_path,
        run_dir=current_run_dir,
        registry_path=registry_path
    )
    
    print("\nPostprocessing complete!")


if __name__ == "__main__":
    main()
