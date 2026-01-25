#!/usr/bin/env python3
"""
Lineage Manifest Generator

라운드별 lineage manifest (LINEAGE.md)를 생성합니다.
재현성/추적성을 위한 facts-only 기록입니다.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def get_git_commit(file_path: Optional[Path] = None) -> Optional[str]:
    """Get git commit hash for a file or HEAD."""
    try:
        if file_path and file_path.exists():
            # Get commit hash for specific file
            result = subprocess.run(
                ["git", "log", "-n", "1", "--pretty=format:%H", "--", str(file_path.relative_to(project_root))],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(project_root)
            )
            return result.stdout.strip() if result.stdout.strip() else None
        else:
            # Get HEAD commit
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


def get_file_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get file mtime and size."""
    if not file_path.exists():
        return None
    try:
        stat = file_path.stat()
        return {
            "mtime": stat.st_mtime,
            "size_bytes": stat.st_size
        }
    except Exception:
        return None


def extract_npz_info(facts_summary_path: Path) -> Dict[str, Any]:
    """Extract NPZ information from facts_summary.json."""
    npz_info = {
        "npz_path": None,
        "npz_path_abs": None,
        "source_path_abs": None,
        "schema_version": None,
        "meta_unit": None
    }
    
    try:
        with open(facts_summary_path, "r", encoding="utf-8") as f:
            facts_data = json.load(f)
        
        # Extract npz_path
        npz_path = facts_data.get("dataset_path") or facts_data.get("npz_path_abs")
        if npz_path:
            npz_path_obj = Path(npz_path)
            if npz_path_obj.is_absolute():
                npz_info["npz_path_abs"] = str(npz_path_obj)
                try:
                    npz_info["npz_path"] = str(npz_path_obj.relative_to(project_root))
                except ValueError:
                    npz_info["npz_path"] = str(npz_path_obj)
            else:
                npz_info["npz_path"] = npz_path
                npz_path_resolved = (project_root / npz_path).resolve()
                if npz_path_resolved.exists():
                    npz_info["npz_path_abs"] = str(npz_path_resolved)
        
        # Extract source_path_abs
        source_path_abs = facts_data.get("source_path_abs")
        if source_path_abs:
            npz_info["source_path_abs"] = str(Path(source_path_abs).resolve())
        
        # Try to load NPZ metadata if available
        if npz_info["npz_path_abs"]:
            npz_path_obj = Path(npz_info["npz_path_abs"])
            if npz_path_obj.exists():
                try:
                    import numpy as np
                    npz_data = np.load(npz_path_obj, allow_pickle=True)
                    if "schema_version" in npz_data:
                        schema = npz_data["schema_version"]
                        if isinstance(schema, (str, bytes)):
                            npz_info["schema_version"] = str(schema)
                        elif hasattr(schema, 'item'):
                            npz_info["schema_version"] = str(schema.item())
                    
                    if "meta_unit" in npz_data:
                        unit = npz_data["meta_unit"]
                        if isinstance(unit, (str, bytes)):
                            npz_info["meta_unit"] = str(unit)
                        elif hasattr(unit, 'item'):
                            npz_info["meta_unit"] = str(unit.item())
                except Exception:
                    pass  # NPZ metadata extraction failed, continue
    
    except Exception:
        pass  # facts_summary.json parsing failed, continue
    
    return npz_info


def find_generator_script(npz_path: Optional[str]) -> Optional[str]:
    """Try to find generator script path from npz_path."""
    if not npz_path:
        return None
    
    # Common patterns
    patterns = [
        "create_real_data_golden.py",
        "create_s0_dataset.py",
        "export_golden_*.py"
    ]
    
    for pattern in patterns:
        for gen_file in project_root.rglob(pattern):
            if gen_file.exists():
                return str(gen_file.relative_to(project_root))
    
    return None


def generate_lineage_manifest(
    current_run_dir: Path,
    facts_summary_path: Path,
    lane: str,
    round_id: str,
    round_num: Optional[int]
) -> str:
    """Generate LINEAGE.md markdown."""
    lines = ["# Lineage Manifest", ""]
    lines.append(f"**schema_version**: lineage@1")
    lines.append("")
    
    # Basic info
    lines.append("## Basic Info")
    lines.append(f"- **current_run_dir**: `{current_run_dir.relative_to(project_root)}`")
    lines.append(f"- **lane**: `{lane}`")
    lines.append(f"- **round_id**: `{round_id}`")
    lines.append(f"- **round_num**: `{round_num or 'N/A'}`")
    lines.append("")
    
    # Inputs
    lines.append("## Inputs")
    npz_info = extract_npz_info(facts_summary_path)
    
    if npz_info["npz_path"]:
        lines.append(f"- **npz_path**: `{npz_info['npz_path']}`")
    if npz_info["npz_path_abs"]:
        lines.append(f"- **npz_path_abs**: `{npz_info['npz_path_abs']}`")
    if npz_info["source_path_abs"]:
        lines.append(f"- **source_path_abs**: `{npz_info['source_path_abs']}`")
    
    lines.append(f"- **facts_summary.json**: `{facts_summary_path.relative_to(project_root)}`")
    lines.append("")
    
    # Code fingerprints
    lines.append("## Code Fingerprints")
    
    postprocess_path = project_root / "tools" / "postprocess_round.py"
    postprocess_commit = get_git_commit(postprocess_path)
    if postprocess_commit:
        lines.append(f"- **tools/postprocess_round.py**: `{postprocess_commit[:8]}`")
    else:
        lines.append("- **tools/postprocess_round.py**: N/A")
    
    summarize_path = project_root / "tools" / "summarize_facts_kpi.py"
    summarize_commit = get_git_commit(summarize_path)
    if summarize_commit:
        lines.append(f"- **tools/summarize_facts_kpi.py**: `{summarize_commit[:8]}`")
    else:
        lines.append("- **tools/summarize_facts_kpi.py**: N/A")
    
    # Generator script
    generator_script = find_generator_script(npz_info["npz_path"])
    if generator_script:
        gen_path = project_root / generator_script
        gen_commit = get_git_commit(gen_path)
        lines.append(f"- **generator_script**: `{generator_script}`")
        if gen_commit:
            lines.append(f"  - **commit**: `{gen_commit[:8]}`")
        else:
            lines.append("  - **commit**: N/A")
    else:
        lines.append("- **generator_script**: N/A")
    
    lines.append("")
    
    # Timestamps
    lines.append("## Timestamps")
    lines.append(f"- **created_at**: `{datetime.now().isoformat()}`")
    
    if npz_info["npz_path_abs"]:
        npz_path_obj = Path(npz_info["npz_path_abs"])
        npz_meta = get_file_metadata(npz_path_obj)
        if npz_meta:
            lines.append(f"- **npz_mtime**: `{npz_meta['mtime']}`")
    
    facts_meta = get_file_metadata(facts_summary_path)
    if facts_meta:
        lines.append(f"- **facts_summary_mtime**: `{facts_meta['mtime']}`")
    
    lines.append("")
    
    # Outputs
    lines.append("## Outputs")
    
    kpi_path = current_run_dir / "KPI.md"
    if kpi_path.exists():
        lines.append(f"- **KPI.md**: `{kpi_path.relative_to(project_root)}`")
    else:
        lines.append("- **KPI.md**: not found")
    
    kpi_diff_path = current_run_dir / "KPI_DIFF.md"
    if kpi_diff_path.exists():
        lines.append(f"- **KPI_DIFF.md**: `{kpi_diff_path.relative_to(project_root)}`")
    else:
        lines.append("- **KPI_DIFF.md**: not found")
    
    # Report (try to get from round_registry)
    new_registry_path = project_root / "docs" / "verification" / "round_registry.json"
    report_path = None
    if new_registry_path.exists():
        try:
            with open(new_registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
            lane_data = registry.get("lanes", {}).get(lane, {})
            baseline = lane_data.get("baseline", {})
            report_path_str = baseline.get("report")
            if report_path_str:
                report_path = project_root / report_path_str
        except Exception:
            pass
    
    if report_path and report_path.exists():
        lines.append(f"- **report**: `{report_path.relative_to(project_root)}`")
    else:
        lines.append("- **report**: N/A")
    
    lines.append(f"- **round_registry.json**: `docs/verification/round_registry.json`")
    lines.append(f"- **golden_registry.json**: `docs/verification/golden_registry.json`")
    lines.append("")
    
    # NPZ metadata (if available)
    if npz_info["schema_version"] or npz_info["meta_unit"]:
        lines.append("## NPZ Metadata")
        if npz_info["schema_version"]:
            lines.append(f"- **schema_version**: `{npz_info['schema_version']}`")
        if npz_info["meta_unit"]:
            lines.append(f"- **meta_unit**: `{npz_info['meta_unit']}`")
        lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate lineage manifest (LINEAGE.md)"
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
        required=True,
        help="Path to facts_summary.json"
    )
    parser.add_argument(
        "--lane",
        type=str,
        required=True,
        help="Lane name"
    )
    parser.add_argument(
        "--round_id",
        type=str,
        required=True,
        help="Round ID"
    )
    parser.add_argument(
        "--round_num",
        type=int,
        default=None,
        help="Round number (optional)"
    )
    
    args = parser.parse_args()
    
    current_run_dir = (project_root / args.current_run_dir).resolve()
    facts_summary_path = (project_root / args.facts_summary).resolve()
    
    lineage_md = generate_lineage_manifest(
        current_run_dir=current_run_dir,
        facts_summary_path=facts_summary_path,
        lane=args.lane,
        round_id=args.round_id,
        round_num=args.round_num
    )
    
    # Save LINEAGE.md
    lineage_path = current_run_dir / "LINEAGE.md"
    with open(lineage_path, "w", encoding="utf-8") as f:
        f.write(lineage_md)
    
    print(f"Generated: {lineage_path}")


if __name__ == "__main__":
    main()
