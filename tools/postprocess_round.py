#!/usr/bin/env python3
"""
Round Postprocessing Tool (v0.2)

라운드 실행 후 필수 후처리 도구:
- KPI 생성 (KPI.md, kpi.json)
- Prev/Baseline diff 생성 (KPI_DIFF.md)
- ROUND_CHARTER.md 자동 생성
- Coverage backlog 업데이트
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def find_facts_summary(run_dir: Path) -> Path:
    """Find facts_summary.json in run_dir."""
    facts_path = run_dir / "facts_summary.json"
    if not facts_path.exists():
        print(f"Error: facts_summary.json not found in {run_dir}", file=sys.stderr)
        print(f"  Expected: {facts_path}", file=sys.stderr)
        sys.exit(2)
    return facts_path


def generate_kpi(run_dir: Path, facts_summary_path: Path) -> Tuple[str, Dict[str, Any]]:
    """Generate KPI.md and kpi.json."""
    kpi_md_path = run_dir / "KPI.md"
    kpi_json_path = run_dir / "kpi.json"
    
    # Call summarize_facts_kpi.py
    cmd = [
        sys.executable,
        str(project_root / "tools" / "summarize_facts_kpi.py"),
        str(facts_summary_path),
        "--out_json",
        str(kpi_json_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
    if result.returncode != 0:
        print(f"Error: Failed to generate KPI: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    # Save KPI.md
    with open(kpi_md_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)
    
    # Load kpi.json
    with open(kpi_json_path, "r", encoding="utf-8") as f:
        kpi_data = json.load(f)
    
    print(f"Generated: {kpi_md_path}")
    print(f"Generated: {kpi_json_path}")
    
    return str(kpi_md_path), kpi_data


def find_prev_run(run_dir: Path) -> Optional[Path]:
    """Find previous run directory in the same parent folder."""
    parent_dir = run_dir.parent
    if not parent_dir.exists():
        return None
    
    # Get all subdirectories
    all_dirs = [d for d in parent_dir.iterdir() if d.is_dir() and d != run_dir]
    if not all_dirs:
        return None
    
    # Sort by modification time (newest first)
    all_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    
    # Find the most recent one that has kpi.json
    for d in all_dirs:
        kpi_json = d / "kpi.json"
        if kpi_json.exists():
            return d
    
    return None


def find_baseline_run() -> Optional[Path]:
    """Find baseline run directory from _baseline.json or golden registry."""
    # Priority 1: _baseline.json
    baseline_json = project_root / "verification" / "runs" / "facts" / "_baseline.json"
    if baseline_json.exists():
        try:
            with open(baseline_json, "r", encoding="utf-8") as f:
                baseline_data = json.load(f)
            baseline_run_dir = baseline_data.get("baseline_run_dir")
            if baseline_run_dir:
                baseline_path = project_root / baseline_run_dir
                if baseline_path.exists():
                    return baseline_path
        except Exception as e:
            print(f"Warning: Failed to read _baseline.json: {e}", file=sys.stderr)
    
    # Priority 2: golden registry (TODO: implement if needed)
    # For now, return None
    return None


def load_kpi_json(kpi_json_path: Path) -> Optional[Dict[str, Any]]:
    """Load kpi.json if it exists."""
    if not kpi_json_path.exists():
        return None
    try:
        with open(kpi_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {kpi_json_path}: {e}", file=sys.stderr)
        return None


def compute_diff(current: Dict[str, Any], other: Dict[str, Any], label: str) -> List[str]:
    """Compute diff between two KPI JSONs. Returns list of markdown lines."""
    lines = [f"## {label}", ""]
    
    # NaN rates changes
    current_nan = current.get("nan_rates_top5", {})
    other_nan = other.get("nan_rates_top5", {})
    nan_changes = []
    all_keys = set(current_nan.keys()) | set(other_nan.keys())
    for key in sorted(all_keys):
        curr_val = current_nan.get(key, 0.0)
        other_val = other_nan.get(key, 0.0)
        if abs(curr_val - other_val) > 0.01:  # Significant change
            delta = curr_val - other_val
            nan_changes.append((key, curr_val, other_val, delta))
    
    if nan_changes:
        lines.append("### NaN Rate Changes")
        for key, curr, prev, delta in sorted(nan_changes, key=lambda x: abs(x[3]), reverse=True)[:5]:
            sign = "+" if delta > 0 else ""
            lines.append(f"- **{key}**: {prev:.2f}% → {curr:.2f}% ({sign}{delta:.2f}%)")
        lines.append("")
    
    # Failure reason changes
    current_fail = current.get("failure_reasons_top5", {})
    other_fail = other.get("failure_reasons_top5", {})
    fail_changes = []
    all_reasons = set(current_fail.keys()) | set(other_fail.keys())
    for reason in sorted(all_reasons):
        curr_count = current_fail.get(reason, 0)
        other_count = other_fail.get(reason, 0)
        if curr_count != other_count:
            delta = curr_count - other_count
            fail_changes.append((reason, curr_count, other_count, delta))
    
    if fail_changes:
        lines.append("### Failure Reason Changes")
        for reason, curr, prev, delta in sorted(fail_changes, key=lambda x: abs(x[3]), reverse=True)[:5]:
            sign = "+" if delta > 0 else ""
            lines.append(f"- **{reason}**: {prev} → {curr} ({sign}{delta})")
        lines.append("")
    
    # HEIGHT/BUST/WAIST/HIP p50 changes
    height_changes = []
    curr_height = current.get("height_m", {}).get("p50")
    other_height = other.get("height_m", {}).get("p50")
    if curr_height is not None and other_height is not None:
        delta = curr_height - other_height
        if abs(delta) > 0.001:  # 1mm threshold
            height_changes.append(("HEIGHT_M", curr_height, other_height, delta))
    
    circ_changes = []
    curr_circ = current.get("circumference_p50", {})
    other_circ = other.get("circumference_p50", {})
    for key in ["BUST_CIRC_M", "WAIST_CIRC_M", "HIP_CIRC_M"]:
        curr_val = curr_circ.get(key)
        other_val = other_circ.get(key)
        if curr_val is not None and other_val is not None:
            delta = curr_val - other_val
            if abs(delta) > 0.001:  # 1mm threshold
                circ_changes.append((key, curr_val, other_val, delta))
    
    if height_changes or circ_changes:
        lines.append("### Measurement p50 Changes")
        for key, curr, prev, delta in height_changes + circ_changes:
            sign = "+" if delta > 0 else ""
            lines.append(f"- **{key}**: {prev:.4f}m → {curr:.4f}m ({sign}{delta:.4f}m)")
        lines.append("")
    
    if len(lines) == 2:  # Only header
        lines.append("No significant changes detected.")
        lines.append("")
    
    return lines


def generate_kpi_diff(run_dir: Path, current_kpi: Dict[str, Any]) -> None:
    """Generate KPI_DIFF.md with prev and baseline diffs."""
    diff_path = run_dir / "KPI_DIFF.md"
    
    lines = ["# KPI Diff", ""]
    
    # Prev diff
    prev_run = find_prev_run(run_dir)
    if prev_run:
        prev_kpi_json = prev_run / "kpi.json"
        prev_kpi = load_kpi_json(prev_kpi_json)
        if prev_kpi:
            lines.extend(compute_diff(current_kpi, prev_kpi, "Diff vs Prev"))
        else:
            lines.append("## Diff vs Prev")
            lines.append("")
            lines.append("Previous run found but kpi.json not available.")
            lines.append("")
    else:
        lines.append("## Diff vs Prev")
        lines.append("")
        lines.append("No previous run found.")
        lines.append("")
    
    # Baseline diff
    baseline_run = find_baseline_run()
    if baseline_run:
        baseline_kpi_json = baseline_run / "kpi.json"
        baseline_kpi = load_kpi_json(baseline_kpi_json)
        if baseline_kpi:
            lines.extend(compute_diff(current_kpi, baseline_kpi, "Diff vs Baseline"))
        else:
            lines.append("## Diff vs Baseline")
            lines.append("")
            lines.append("Baseline run found but kpi.json not available.")
            lines.append("")
    else:
        lines.append("## Diff vs Baseline")
        lines.append("")
        lines.append("No baseline run configured. Use `py tools/set_baseline_run.py --run_dir <dir>` to set.")
        lines.append("")
    
    with open(diff_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Generated: {diff_path}")


def generate_round_charter(run_dir: Path) -> None:
    """Generate ROUND_CHARTER.md from template if it doesn't exist."""
    charter_path = run_dir / "ROUND_CHARTER.md"
    if charter_path.exists():
        print(f"ROUND_CHARTER.md already exists: {charter_path}")
        return
    
    template_path = project_root / "docs" / "verification" / "round_charter_template.md"
    if not template_path.exists():
        print(f"Warning: Template not found: {template_path}", file=sys.stderr)
        return
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Replace placeholder with run_dir name
    run_name = run_dir.name
    template = template.replace("roundXX", run_name)
    template = template.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
    
    with open(charter_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"Generated: {charter_path}")


def update_coverage_backlog(run_dir: Path, facts_summary_path: Path) -> None:
    """Update coverage_backlog.md with 100% NaN or VALUE_MISSING keys."""
    backlog_path = project_root / "docs" / "verification" / "coverage_backlog.md"
    
    # Load facts_summary.json
    with open(facts_summary_path, "r", encoding="utf-8") as f:
        facts_data = json.load(f)
    
    # Find 100% NaN keys
    summary = facts_data.get("summary", {})
    if not isinstance(summary, dict):
        summary = facts_data.get("statistics", {})
    
    if not isinstance(summary, dict):
        return
    
    backlog_entries = []
    for key, stats in summary.items():
        if not isinstance(stats, dict):
            continue
        
        # Check NaN rate
        nan_rate_pct = stats.get("nan_rate_pct", 0.0)
        if nan_rate_pct >= 100.0:
            backlog_entries.append({
                "key": key,
                "reason": "NaN 100%",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "run_dir": str(run_dir.relative_to(project_root))
            })
        
        # Check for VALUE_MISSING in warnings
        warnings = stats.get("warnings_top5", [])
        if isinstance(warnings, list):
            for w in warnings:
                if isinstance(w, dict):
                    reason = w.get("reason", "")
                    if "VALUE_MISSING" in reason or "MISSING" in reason.upper():
                        count = w.get("n", 0)
                        total = facts_data.get("n_samples", 0)
                        if isinstance(total, (int, float)) and total > 0:
                            rate = (count / total) * 100.0
                            if rate >= 100.0:
                                backlog_entries.append({
                                    "key": key,
                                    "reason": f"VALUE_MISSING 100% ({reason})",
                                    "date": datetime.now().strftime("%Y-%m-%d"),
                                    "run_dir": str(run_dir.relative_to(project_root))
                                })
                                break
    
    if not backlog_entries:
        return
    
    # Append to backlog
    backlog_lines = []
    if backlog_path.exists():
        with open(backlog_path, "r", encoding="utf-8") as f:
            backlog_lines = f.read().splitlines()
    
    # Add new entries
    backlog_lines.append("")
    backlog_lines.append(f"## {datetime.now().strftime('%Y-%m-%d')} - {run_dir.name}")
    for entry in backlog_entries:
        backlog_lines.append(f"- **{entry['key']}**: {entry['reason']} (run: `{entry['run_dir']}`)")
    
    with open(backlog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(backlog_lines))
    
    print(f"Updated: {backlog_path} ({len(backlog_entries)} entries)")


def main():
    parser = argparse.ArgumentParser(
        description="Round postprocessing tool (v0.2)"
    )
    parser.add_argument(
        "--run_dir",
        type=str,
        required=True,
        help="Run directory path (e.g., verification/runs/facts/curated_v0/round20_20260125_164801)"
    )
    
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Postprocessing round: {run_dir}")
    
    # 1. Find facts_summary.json
    facts_summary_path = find_facts_summary(run_dir)
    
    # 2. Generate KPI
    kpi_md_path, kpi_data = generate_kpi(run_dir, facts_summary_path)
    
    # 3. Generate KPI diff
    generate_kpi_diff(run_dir, kpi_data)
    
    # 4. Generate ROUND_CHARTER.md
    generate_round_charter(run_dir)
    
    # 5. Update coverage backlog
    update_coverage_backlog(run_dir, facts_summary_path)
    
    print("\nPostprocessing complete!")


if __name__ == "__main__":
    main()
