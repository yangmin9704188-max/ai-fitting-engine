#!/usr/bin/env python3
"""
Work Brief Publisher v0 (Round 10)

Publishes hub-generated module work briefs to external lab folders
(fitting_lab, garment_lab) strictly within exports/brief/**.

Facts-only. Exit 0 always. Errors become warnings.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repo root on path when run as py tools/publish_work_briefs_v0.py
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from tools.render_dashboard_v0 import load_sources


# Lab -> (brief filename to copy from hub)
LAB_BRIEFS: Dict[str, str] = {
    "fitting_lab": "FITTING_WORK_BRIEF.md",
    "garment_lab": "GARMENT_WORK_BRIEF.md",
}


def get_lab_root(lab_name: str, sources_cfg: Dict[str, Any]) -> Tuple[Optional[Path], List[str]]:
    """Resolve lab root path from LAB_SOURCES. Returns (path or None, warnings)."""
    warnings: List[str] = []
    lab_cfg = sources_cfg.get(lab_name)
    if not isinstance(lab_cfg, dict):
        warnings.append(f"LAB_SOURCES: '{lab_name}' not found or invalid")
        return None, warnings

    root_str = lab_cfg.get("root", "")
    if not root_str or "TBD" in str(root_str).upper():
        warnings.append(f"LAB_SOURCES: '{lab_name}' root is TBD or empty ({root_str})")
        return None, warnings

    return Path(root_str), warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish hub work briefs to external labs (Round 10)"
    )
    parser.add_argument(
        "--hub-root",
        default=".",
        help="Hub root directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report only; do not create directories or copy files",
    )
    args = parser.parse_args()

    hub_root = Path(args.hub_root).resolve()
    sources_path = hub_root / "docs" / "ops" / "dashboard" / "LAB_SOURCES_v0.yaml"
    hub_brief_dir = hub_root / "exports" / "brief"

    warnings: List[str] = []
    targets_attempted: List[str] = []
    files_copied: List[str] = []

    sources_cfg, src_warnings = load_sources(sources_path)
    warnings.extend(src_warnings)

    for lab_name, brief_name in LAB_BRIEFS.items():
        lab_root, lab_warnings = get_lab_root(lab_name, sources_cfg)
        warnings.extend(lab_warnings)

        if lab_root is None:
            continue

        targets_attempted.append(f"{lab_name} -> {lab_root}")

        src_file = hub_brief_dir / brief_name
        if not src_file.exists():
            warnings.append(f"Source brief missing: {src_file}")
            continue

        dest_dir = lab_root / "exports" / "brief"
        dest_file = dest_dir / brief_name

        if args.dry_run:
            files_copied.append(f"[dry-run] would copy {brief_name} -> {dest_file}")
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            warnings.append(f"Cannot create {dest_dir} ({lab_name}): {e}")
            continue

        try:
            shutil.copy2(src_file, dest_file)
            files_copied.append(f"{brief_name} -> {dest_file}")
        except Exception as e:
            warnings.append(f"Copy failed {src_file} -> {dest_file}: {e}")

    # Facts-only report
    print("--- Publish Work Briefs v0 (facts-only) ---")
    print("Targets attempted:", len(targets_attempted))
    for t in targets_attempted:
        print(f"  - {t}")
    print("Files copied:", len(files_copied))
    for f in files_copied:
        print(f"  - {f}")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
    print("---")

    sys.exit(0)


if __name__ == "__main__":
    main()
