#!/usr/bin/env python3
"""
Round Postprocessing Tool (v0.3)

라운드 실행 후 필수 후처리 도구:
- KPI 생성 (KPI.md, kpi.json)
- Prev/Baseline diff 생성 (KPI_DIFF.md) + Degradation Warning
- ROUND_CHARTER.md 자동 생성 + Prompt Snapshot
- Coverage backlog 업데이트
- Data Lineage Manifest 기록
- Visual Provenance PNG 생성
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


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


def check_degradation(current: Dict[str, Any], baseline: Dict[str, Any]) -> List[str]:
    """Check for degradation warnings. Returns list of warning messages."""
    warnings = []
    
    # NaN rate top5 sum/avg degradation
    current_nan = current.get("nan_rates_top5", {})
    baseline_nan = baseline.get("nan_rates_top5", {})
    if current_nan and baseline_nan:
        current_sum = sum(current_nan.values())
        baseline_sum = sum(baseline_nan.values())
        if current_sum > baseline_sum + 3.0:  # +3%p threshold
            warnings.append(f"NaN rate top5 sum increased: {baseline_sum:.2f}% → {current_sum:.2f}% (+{current_sum - baseline_sum:.2f}%p)")
    
    # HEIGHT p50 change > ±2%
    curr_height = current.get("height_m", {}).get("p50")
    base_height = baseline.get("height_m", {}).get("p50")
    if curr_height is not None and base_height is not None and base_height > 0:
        pct_change = abs((curr_height - base_height) / base_height) * 100.0
        if pct_change > 2.0:
            warnings.append(f"HEIGHT_M p50 changed: {base_height:.4f}m → {curr_height:.4f}m ({pct_change:.2f}% change)")
    
    # Failure reason top1 count increase > +3%
    current_fail = current.get("failure_reasons_top5", {})
    baseline_fail = baseline.get("failure_reasons_top5", {})
    if current_fail and baseline_fail:
        current_top1 = max(current_fail.values()) if current_fail.values() else 0
        baseline_top1 = max(baseline_fail.values()) if baseline_fail.values() else 0
        if baseline_top1 > 0:
            pct_increase = ((current_top1 - baseline_top1) / baseline_top1) * 100.0
            if pct_increase > 3.0:
                warnings.append(f"Failure reason top1 count increased: {baseline_top1} → {current_top1} (+{pct_increase:.2f}%)")
    
    return warnings


def generate_kpi_diff(run_dir: Path, current_kpi: Dict[str, Any]) -> None:
    """Generate KPI_DIFF.md with prev and baseline diffs + degradation warnings."""
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
    baseline_kpi = None
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
    
    # Degradation Warning
    if baseline_kpi:
        degradation_warnings = check_degradation(current_kpi, baseline_kpi)
        if degradation_warnings:
            lines.append("## Degradation Warning")
            lines.append("")
            lines.append("⚠️ DEGRADATION")
            lines.append("")
            for warning in degradation_warnings:
                lines.append(f"- {warning}")
            lines.append("")
    
    with open(diff_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Generated: {diff_path}")


def get_prompt_snapshot() -> Optional[str]:
    """Get prompt snapshot from env var or file."""
    # Try env var first
    prompt_text = os.environ.get("PROMPT_SNAPSHOT_TEXT")
    if prompt_text:
        return prompt_text
    
    # Try file path
    prompt_path = os.environ.get("PROMPT_SNAPSHOT_PATH")
    if prompt_path:
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Warning: Failed to read PROMPT_SNAPSHOT_PATH: {e}", file=sys.stderr)
    
    return None


def generate_round_charter(run_dir: Path) -> None:
    """Generate ROUND_CHARTER.md from template if it doesn't exist."""
    charter_path = run_dir / "ROUND_CHARTER.md"
    if charter_path.exists():
        # Update existing charter with prompt snapshot if needed
        with open(charter_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add prompt snapshot section if not exists
        if "## Prompt Snapshot" not in content:
            prompt_snapshot = get_prompt_snapshot()
            snapshot_section = "\n## Prompt Snapshot\n\n"
            if prompt_snapshot:
                snapshot_section += f"```\n{prompt_snapshot}\n```\n"
            else:
                snapshot_section += "(Set PROMPT_SNAPSHOT_TEXT env var or PROMPT_SNAPSHOT_PATH to record prompt context)\n"
            
            content += snapshot_section
            with open(charter_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {charter_path} (added Prompt Snapshot)")
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
    
    # Add prompt snapshot section
    prompt_snapshot = get_prompt_snapshot()
    snapshot_section = "\n## Prompt Snapshot\n\n"
    if prompt_snapshot:
        snapshot_section += f"```\n{prompt_snapshot}\n```\n"
    else:
        snapshot_section += "(Set PROMPT_SNAPSHOT_TEXT env var or PROMPT_SNAPSHOT_PATH to record prompt context)\n"
    
    template += snapshot_section
    
    with open(charter_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"Generated: {charter_path}")


def compute_file_hash(file_path: Path) -> Optional[str]:
    """Compute SHA256 hash of file."""
    if not file_path.exists():
        return None
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def get_file_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get file mtime and size."""
    if not file_path.exists():
        return None
    try:
        stat = file_path.stat()
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size
        }
    except Exception:
        return None


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


def update_data_lineage(run_dir: Path, facts_summary_path: Path) -> None:
    """Update data lineage manifest."""
    lineage_path = run_dir / "lineage.json"
    
    # Load facts_summary.json
    with open(facts_summary_path, "r", encoding="utf-8") as f:
        facts_data = json.load(f)
    
    lineage = {
        "created_at": datetime.now().isoformat(),
        "git_commit": get_git_commit(),
    }
    
    # Extract source information
    source_path_abs = facts_data.get("source_path_abs")
    if source_path_abs:
        source_path = Path(source_path_abs)
        if source_path.exists():
            source_meta = get_file_metadata(source_path)
            if source_meta:
                lineage["source"] = {
                    "path_abs": str(source_path_abs),
                    "mtime": source_meta["mtime"],
                    "size": source_meta["size"]
                }
    
    # Extract generator information from dataset_path
    dataset_path = facts_data.get("dataset_path") or facts_data.get("npz_path_abs")
    if dataset_path:
        dataset_path_obj = Path(dataset_path)
        if dataset_path_obj.exists():
            dataset_meta = get_file_metadata(dataset_path_obj)
            if dataset_meta:
                lineage["dataset"] = {
                    "path_abs": str(dataset_path),
                    "mtime": dataset_meta["mtime"],
                    "size": dataset_meta["size"]
                }
    
    # Try to find generator script (common patterns)
    generator_patterns = [
        "create_real_data_golden.py",
        "create_s0_dataset.py",
        "export_golden_*.py"
    ]
    
    for pattern in generator_patterns:
        for gen_file in project_root.rglob(pattern):
            if gen_file.exists():
                gen_hash = compute_file_hash(gen_file)
                if gen_hash:
                    lineage["generator"] = {
                        "script_path": str(gen_file.relative_to(project_root)),
                        "script_sha256": gen_hash
                    }
                    break
        if "generator" in lineage:
            break
    
    with open(lineage_path, "w", encoding="utf-8") as f:
        json.dump(lineage, f, indent=2, ensure_ascii=False)
    
    print(f"Generated: {lineage_path}")


def generate_visual_provenance(run_dir: Path, facts_summary_path: Path) -> Optional[List[str]]:
    """Generate lightweight visual provenance PNGs. Returns list of relative paths."""
    if not HAS_MATPLOTLIB:
        print("Warning: matplotlib not available, skipping visual provenance", file=sys.stderr)
        return None
    
    # Load facts_summary.json to get dataset path
    with open(facts_summary_path, "r", encoding="utf-8") as f:
        facts_data = json.load(f)
    
    dataset_path = facts_data.get("dataset_path") or facts_data.get("npz_path_abs")
    if not dataset_path:
        return None
    
    dataset_path_obj = Path(dataset_path)
    if not dataset_path_obj.exists():
        return None
    
    try:
        data = np.load(dataset_path_obj, allow_pickle=True)
        if "verts" not in data:
            return None
        
        verts = data["verts"]
        # Handle different shapes
        if verts.ndim == 3:
            # (N, V, 3) - take first case
            verts = verts[0]
        elif verts.ndim == 2:
            # (V, 3) - use as is
            pass
        else:
            return None
        
        if verts.shape[1] != 3:
            return None
        
        # Create visual directory
        visual_dir = run_dir / "visual"
        visual_dir.mkdir(exist_ok=True)
        
        # Compute bbox and aspect ratio
        x_min, x_max = verts[:, 0].min(), verts[:, 0].max()
        y_min, y_max = verts[:, 1].min(), verts[:, 1].max()
        z_min, z_max = verts[:, 2].min(), verts[:, 2].max()
        
        bbox_x = x_max - x_min
        bbox_y = y_max - y_min
        bbox_z = z_max - z_min
        aspect_xy = bbox_x / bbox_y if bbox_y > 0 else 1.0
        aspect_zy = bbox_z / bbox_y if bbox_y > 0 else 1.0
        
        visual_paths = []
        
        # XY scatter
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(verts[:, 0], verts[:, 1], s=0.1, alpha=0.5)
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title(f"normal_1 XY\nbbox: {bbox_x:.3f}m x {bbox_y:.3f}m, aspect: {aspect_xy:.2f}")
        ax.grid(True, alpha=0.3)
        xy_path = visual_dir / "normal_1_xy.png"
        plt.savefig(xy_path, dpi=100, bbox_inches="tight")
        plt.close()
        visual_paths.append(str(xy_path.relative_to(run_dir)))
        
        # ZY scatter
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(verts[:, 2], verts[:, 1], s=0.1, alpha=0.5)
        ax.set_xlabel("Z (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title(f"normal_1 ZY\nbbox: {bbox_z:.3f}m x {bbox_y:.3f}m, aspect: {aspect_zy:.2f}")
        ax.grid(True, alpha=0.3)
        zy_path = visual_dir / "normal_1_zy.png"
        plt.savefig(zy_path, dpi=100, bbox_inches="tight")
        plt.close()
        visual_paths.append(str(zy_path.relative_to(run_dir)))
        
        print(f"Generated: {xy_path}")
        print(f"Generated: {zy_path}")
        
        return visual_paths
        
    except Exception as e:
        print(f"Warning: Failed to generate visual provenance: {e}", file=sys.stderr)
        return None


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
        description="Round postprocessing tool (v0.3)"
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
    
    # 6. Update data lineage
    update_data_lineage(run_dir, facts_summary_path)
    
    # 7. Generate visual provenance
    visual_paths = generate_visual_provenance(run_dir, facts_summary_path)
    
    # 8. Update report with visual links if available
    if visual_paths:
        report_paths = list(run_dir.glob("*.md"))
        for report_path in report_paths:
            if report_path.name in ["KPI.md", "KPI_DIFF.md"]:
                continue  # Skip KPI files
            
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Add visual links if not already present
            if "Visual:" not in content:
                visual_section = "\n\n## Visual Provenance\n\n"
                for vpath in visual_paths:
                    vname = Path(vpath).stem.replace("_", " ").title()
                    visual_section += f"- [Visual: {vname}]({vpath})\n"
                
                content += visual_section
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated: {report_path} (added visual links)")
    
    print("\nPostprocessing complete!")


if __name__ == "__main__":
    main()
