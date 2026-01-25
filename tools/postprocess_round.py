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
    """Get previous run directory from registry (old schema)."""
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


def get_prev_and_baseline_from_new_registry(
    lane: str,
    current_round_num: Optional[int],
    new_registry_path: Path
) -> tuple[Optional[Path], Optional[Path]]:
    """Get prev and baseline run directories from new round_registry.json schema."""
    if not new_registry_path.exists():
        return None, None
    
    try:
        with open(new_registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception:
        return None, None
    
    lanes = registry.get("lanes", {})
    lane_data = lanes.get(lane, {})
    
    # Get baseline
    baseline_info = lane_data.get("baseline")
    baseline_run_dir = None
    if baseline_info and baseline_info.get("run_dir"):
        baseline_path = project_root / baseline_info["run_dir"]
        if baseline_path.exists():
            baseline_run_dir = baseline_path.resolve()
    
    # Get prev (current round_num보다 작은 round 중 가장 큰 round)
    prev_run_dir = None
    if current_round_num is not None:
        rounds = lane_data.get("rounds", [])
        prev_candidates = [
            r for r in rounds
            if r.get("round_num") is not None and r.get("round_num") < current_round_num
        ]
        if prev_candidates:
            # Sort by round_num descending and take the largest
            prev_candidates.sort(key=lambda x: x.get("round_num", 0), reverse=True)
            prev_entry = prev_candidates[0]
            prev_run_dir_str = prev_entry.get("run_dir")
            if prev_run_dir_str:
                prev_path = project_root / prev_run_dir_str
                if prev_path.exists():
                    prev_run_dir = prev_path.resolve()
    
    return prev_run_dir, baseline_run_dir


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
    """Generate KPI_DIFF.md using kpi_diff.py."""
    from tools.kpi_diff import generate_kpi_diff as gen_diff
    
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


def update_new_round_registry(
    current_run_dir: Path,
    facts_summary_path: Optional[Path],
    lane: str,
    baselines: Dict[str, Any],
    coverage_backlog_touched: bool
) -> tuple[Optional[int], str]:
    """Update new round registry schema using round_registry.py."""
    from tools.round_registry import update_registry, extract_round_info
    
    # Extract round info
    _, round_num, round_id = extract_round_info(current_run_dir)
    
    # New registry path
    new_registry_path = project_root / "docs" / "verification" / "round_registry.json"
    
    # Update registry
    update_registry(
        registry_path=new_registry_path,
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=lane,
        round_num=round_num,
        round_id=round_id,
        baselines=baselines,
        coverage_backlog_touched=coverage_backlog_touched
    )
    
    return round_num, round_id


def generate_lineage_manifest(
    current_run_dir: Path,
    facts_summary_path: Path,
    lane: str,
    round_id: str,
    round_num: Optional[int]
) -> None:
    """Generate LINEAGE.md using lineage.py."""
    from tools.lineage import generate_lineage_manifest as gen_lineage
    
    lineage_md = gen_lineage(
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=lane,
        round_id=round_id,
        round_num=round_num
    )
    
    # Save LINEAGE.md
    lineage_path = current_run_dir / "LINEAGE.md"
    with open(lineage_path, "w", encoding="utf-8") as f:
        f.write(lineage_md)
    
    print(f"Generated: {lineage_path}")


def update_golden_registry(
    facts_summary_path: Path
) -> None:
    """Update golden registry from facts_summary.json."""
    try:
        with open(facts_summary_path, "r", encoding="utf-8") as f:
            facts_data = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load facts_summary.json for golden registry: {e}", file=sys.stderr)
        return
    
    # Extract npz_path
    npz_path_str = facts_data.get("dataset_path") or facts_data.get("npz_path_abs")
    if not npz_path_str:
        return  # No NPZ path, skip
    
    npz_path = Path(npz_path_str)
    if npz_path.is_absolute():
        npz_path_obj = npz_path
    else:
        npz_path_obj = project_root / npz_path
    
    if not npz_path_obj.exists():
        print(f"Warning: NPZ file not found: {npz_path_obj}", file=sys.stderr)
        return
    
    # Extract source_path_abs
    source_path_abs = facts_data.get("source_path_abs")
    if source_path_abs:
        source_path_abs = str(Path(source_path_abs).resolve())
    
    # Update golden registry
    from tools.golden_registry import upsert_golden_entry
    
    registry_path = project_root / "docs" / "verification" / "golden_registry.json"
    
    try:
        upsert_golden_entry(
            registry_path=registry_path,
            npz_path=npz_path_obj,
            source_path_abs=source_path_abs
        )
    except Exception as e:
        print(f"Warning: Failed to update golden registry: {e}", file=sys.stderr)


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
        description="Round postprocessing tool (round5)"
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
    
    # Load new registry and get prev/baseline from new schema
    new_registry_path = project_root / "docs" / "verification" / "round_registry.json"
    
    # Extract round_num and round_id for prev lookup
    from tools.round_registry import extract_round_info
    _, round_num, round_id = extract_round_info(current_run_dir)
    
    # Get prev and baseline from new registry
    prev_run_dir_new, baseline_run_dir_new = get_prev_and_baseline_from_new_registry(
        lane=lane,
        current_round_num=round_num,
        new_registry_path=new_registry_path
    )
    
    # Use new registry values if available, otherwise fallback to old logic
    if prev_run_dir_new:
        prev_run_dir = prev_run_dir_new
    else:
        # Fallback to old registry logic
        registry = load_round_registry(registry_path)
        prev_run_dir = get_prev_run_dir(lane, registry, baseline_run_dir)
    
    if baseline_run_dir_new:
        baseline_run_dir = baseline_run_dir_new
    # else: keep baseline_run_dir from baselines.json (already set above)
    
    if prev_run_dir:
        print(f"Prev: {prev_run_dir.relative_to(project_root)}")
    else:
        print("Prev: None")
    
    if baseline_run_dir:
        print(f"Baseline: {baseline_run_dir.relative_to(project_root)}")
    else:
        print("Baseline: None")
    
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
    
    # Update old registry (for backward compatibility, keep existing logic)
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
    coverage_backlog_touched = False
    try:
        update_coverage_backlog(
            facts_summary_path=facts_summary_path,
            run_dir=current_run_dir,
            registry_path=registry_path
        )
        coverage_backlog_touched = True
    except Exception as e:
        print(f"Warning: Failed to update coverage backlog: {e}", file=sys.stderr)
    
    # Update round registry (new schema) and get round info
    round_num, round_id = update_new_round_registry(
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=lane,
        baselines=baselines,
        coverage_backlog_touched=coverage_backlog_touched
    )
    
    # Generate lineage manifest
    generate_lineage_manifest(
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=lane,
        round_id=round_id,
        round_num=round_num
    )
    
    # Update golden registry
    update_golden_registry(
        facts_summary_path=facts_summary_path
    )
    
    print("\nPostprocessing complete!")


if __name__ == "__main__":
    main()
