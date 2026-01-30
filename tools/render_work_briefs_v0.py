#!/usr/bin/env python3
"""
Work Briefs v0 Renderer (Round 9)

Generates per-module work briefs as markdown files under exports/brief/.
Reads PLAN_v0.yaml, LAB_SOURCES_v0.yaml, and each module's primary progress log.
Facts-only. No PASS/FAIL. Exit 0 always (errors become warnings in output).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repo root on path when run as py tools/render_work_briefs_v0.py
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Reuse parsing and aggregation from dashboard (no refactor of that file)
from tools.render_dashboard_v0 import (
    load_plan,
    load_sources,
    load_events,
    extract_steps,
    aggregate,
    compute_unlock,
)


MODULE_TO_LAB: Dict[str, str] = {
    "body": "hub",
    "fitting": "fitting_lab",
    "garment": "garment_lab",
}


def get_log_path_for_module(
    module: str,
    hub_root: Path,
    sources_cfg: Dict[str, Any],
) -> Tuple[Optional[Path], List[str]]:
    """Resolve progress log path for a module. Returns (path or None, warnings)."""
    warnings: List[str] = []
    lab_name = MODULE_TO_LAB.get(module)
    if not lab_name:
        warnings.append(f"Unknown module: {module}")
        return None, warnings

    if lab_name == "hub":
        path = hub_root / "exports" / "progress" / "PROGRESS_LOG.jsonl"
        return path, warnings

    lab_cfg = sources_cfg.get(lab_name)
    if not isinstance(lab_cfg, dict):
        warnings.append(f"Lab '{lab_name}' not found or invalid in LAB_SOURCES")
        return None, warnings

    log_path_str = lab_cfg.get("progress_log_path", "")
    if not log_path_str or "TBD" in str(log_path_str).upper():
        warnings.append(f"source '{lab_name}': path is TBD or empty ({log_path_str})")
        return None, warnings

    return Path(log_path_str), warnings


def load_events_from_path(
    log_path: Path,
    max_events: int,
) -> Tuple[List[Dict], List[str]]:
    """Load events from a single JSONL file. Skip invalid lines, record warnings."""
    events: List[Dict] = []
    warnings: List[str] = []

    if not log_path.exists():
        warnings.append(f"Progress log missing: {log_path}")
        return events, warnings

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                    events.append(evt)
                except json.JSONDecodeError as e:
                    warnings.append(f"Line {line_num}: invalid JSON ({e})")
    except Exception as e:
        warnings.append(f"Read error: {e}")

    events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    return events[:max_events], warnings


def render_brief(
    module: str,
    steps: Dict[str, Dict],
    unlock: Dict[str, str],
    plan: Dict,
    log_path_used: Optional[Path],
    module_events: List[Dict],
    plan_warnings: List[str],
    sources_warnings: List[str],
    module_log_warnings: List[str],
) -> str:
    """Render a single module work brief markdown."""
    lines: List[str] = []
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    if now_iso and len(now_iso) > 3:
        now_iso = now_iso[:-2] + ":" + now_iso[-2:]

    # Header
    lines.append("# WORK BRIEF (generated-only)")
    lines.append("")
    lines.append(f"Module: {module}")
    lines.append(f"Generated at: {now_iso}")
    lines.append(f"Source Progress Log: {log_path_used or '(none)'}")
    lines.append("")
    lines.append("⚠️ Do not hand-edit. Re-generate via tools/render_work_briefs_v0.py")
    lines.append("")
    lines.append("---")
    lines.append("")

    mod_steps = [s for s in steps.values() if s["module"] == module]
    mod_steps.sort(key=lambda x: x["id"])

    total_done = sum(s["dod_done"] for s in mod_steps)
    total_total = sum(
        s["dod_total"] for s in mod_steps if isinstance(s["dod_total"], int)
    )
    unlocked_count = sum(
        1 for s in mod_steps if unlock.get(s["id"]) == "UNLOCKED"
    )
    blocked_count = sum(
        1 for s in mod_steps if unlock.get(s["id"], "").startswith("BLOCKED")
    )
    warn_count = (
        len(plan_warnings)
        + len(sources_warnings)
        + len(module_log_warnings)
    )

    # 1) Status Summary
    lines.append("## 1) Status Summary")
    lines.append("")
    lines.append(f"- total_done / total_total (this module): {total_done} / {total_total}")
    lines.append(f"- UNLOCKED steps: {unlocked_count}")
    lines.append(f"- BLOCKED steps: {blocked_count}")
    lines.append(f"- Warnings encountered while reading inputs: {warn_count}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 2) Available Work (UNLOCKED, remaining > 0)
    lines.append("## 2) Available Work (UNLOCKED, remaining > 0)")
    lines.append("")
    available = []
    for s in mod_steps:
        sid = s["id"]
        dt = s["dod_total"]
        dd = s["dod_done"]
        if (
            unlock.get(sid) == "UNLOCKED"
            and isinstance(dt, int)
            and dd < dt
        ):
            remaining = dt - dd
            unlocks_str = ", ".join(
                (u.split(":")[-1] if ":" in u else u) for u in s["unlocks"]
            ) or "—"
            available.append({
                "step": sid,
                "name": s["name"],
                "done": dd,
                "total": dt,
                "remaining": remaining,
                "unlocks": unlocks_str,
            })
    if available:
        lines.append("| Step | Name | Done | Total | Remaining | Unlocks |")
        lines.append("|------|------|------|-------|-----------|---------|")
        for a in available:
            lines.append(
                f"| {a['step']} | {a['name']} | {a['done']} | {a['total']} | "
                f"{a['remaining']} | {a['unlocks']} |"
            )
    else:
        lines.append("(No available work: no UNLOCKED steps with remaining > 0)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 3) Next Unlock Targets (BLOCKED with exactly 1 incomplete dependency)
    lines.append("## 3) Next Unlock Targets (BLOCKED with exactly 1 incomplete dependency)")
    lines.append("")
    next_targets = []
    for s in mod_steps:
        sid = s["id"]
        if not unlock.get(sid, "").startswith("BLOCKED"):
            continue
        incomplete = []
        for dep_ref in s["depends_on"]:
            dep_id = dep_ref.split(":")[-1] if ":" in dep_ref else dep_ref
            dep_step = steps.get(dep_id)
            if dep_step:
                dt = dep_step["dod_total"]
                dd = dep_step["dod_done"]
                if not isinstance(dt, int) or dd < dt:
                    incomplete.append((dep_id, dd, dt))
        if len(incomplete) == 1:
            dep_id, dep_done, dep_total = incomplete[0]
            dep_total_str = str(dep_total) if isinstance(dep_total, int) else "N/A"
            next_targets.append({
                "step": sid,
                "name": s["name"],
                "blocking_dep": dep_id,
                "blocking_progress": f"{dep_done}/{dep_total_str}",
            })
    if next_targets:
        lines.append("| Step | Name | Blocking Dependency | Blocking Done/Total |")
        lines.append("|------|------|---------------------|---------------------|")
        for t in next_targets:
            lines.append(
                f"| {t['step']} | {t['name']} | {t['blocking_dep']} | "
                f"{t['blocking_progress']} |"
            )
    else:
        lines.append("(No steps with exactly one incomplete dependency)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 4) Recent Events (this module)
    lines.append("## 4) Recent Events (this module)")
    lines.append("")
    display = module_events[:10]
    lines.append("| # | Timestamp | Step | Delta | Evidence Count | Evidence Sample | Note |")
    lines.append("|---|-----------|------|-------|----------------|-----------------|------|")
    if display:
        for idx, evt in enumerate(display, 1):
            ts = evt.get("ts", "—")
            sid = evt.get("step_id", "—")
            delta = evt.get("dod_done_delta", "—")
            ep = evt.get("evidence_paths", [])
            ep_count = len(ep) if isinstance(ep, list) else "—"
            ep_sample = ep[0] if isinstance(ep, list) and ep else "—"
            note = evt.get("note", "")
            lines.append(f"| {idx} | {ts} | {sid} | {delta} | {ep_count} | {ep_sample} | {note} |")
    else:
        lines.append("| — | (no events) | | | | | |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 5) Warnings (facts-only)
    lines.append("## 5) Warnings (facts-only)")
    lines.append("")
    all_warnings = plan_warnings + sources_warnings + module_log_warnings
    if all_warnings:
        for w in all_warnings:
            lines.append(f"- {w}")
    else:
        lines.append("(None)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 6) Close-out (append-only progress log)
    lines.append("## Close-out (append-only progress log)")
    lines.append("")
    lines.append(
        "Progress for this module is recorded by appending one event line to the "
        "module progress log via the append-progress-event tool."
    )
    lines.append("")
    lab_name = MODULE_TO_LAB.get(module, "")
    if log_path_used and log_path_used.exists():
        log_path_display = str(log_path_used)
    else:
        log_path_display = "<TBD_PATH>"
        lines.append("- Warning: module log path is TBD or missing; use actual path in command.")
    lines.append("")
    lines.append("Copy/paste command template (replace placeholders):")
    lines.append("")
    lines.append(
        f'py tools/append_progress_event_v0.py --log-path "{log_path_display}" '
        f'--lab "{lab_name}" --module "{module}" --step-id "<STEP_ID>" '
        f'--dod-done-delta 1 --dod-total <TOTAL> --evidence "<EVIDENCE_PATH_1>" '
        f'--note "<NOTE_OPTIONAL>"'
    )
    lines.append("")
    lines.append("Step candidates (UNLOCKED, remaining > 0):")
    lines.append("")
    step_candidates = []
    for s in mod_steps:
        sid = s["id"]
        dt = s["dod_total"]
        dd = s["dod_done"]
        if (
            unlock.get(sid) == "UNLOCKED"
            and isinstance(dt, int)
            and dd < dt
        ):
            step_candidates.append({
                "step": sid,
                "total": dt,
                "current_done": dd,
                "remaining": dt - dd,
            })
    if step_candidates:
        lines.append("| Step | Total | Current Done | Remaining |")
        lines.append("|------|-------|---------------|-----------|")
        for c in step_candidates:
            lines.append(
                f"| {c['step']} | {c['total']} | {c['current_done']} | {c['remaining']} |"
            )
    else:
        lines.append("(No UNLOCKED steps with remaining work.)")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render per-module work briefs (Round 9)"
    )
    parser.add_argument(
        "--hub-root",
        default=".",
        help="Hub root directory (default: current directory)",
    )
    args = parser.parse_args()

    hub_root = Path(args.hub_root).resolve()
    plan_path = hub_root / "docs" / "ops" / "dashboard" / "PLAN_v0.yaml"
    sources_path = hub_root / "docs" / "ops" / "dashboard" / "LAB_SOURCES_v0.yaml"
    brief_dir = hub_root / "exports" / "brief"

    plan, plan_warnings = load_plan(plan_path)
    sources_cfg, sources_warnings = load_sources(sources_path)

    # Build sources for aggregation: hub log from hub_root; others from LAB_SOURCES
    sources_for_load: Dict[str, Any] = {
        "hub": {
            "progress_log_path": str(hub_root / "exports" / "progress" / "PROGRESS_LOG.jsonl"),
            "modules": ["body"],
        },
    }
    for lab in ("fitting_lab", "garment_lab"):
        if lab in sources_cfg and isinstance(sources_cfg[lab], dict):
            sources_for_load[lab] = dict(sources_cfg[lab])

    all_events, all_events_warnings = load_events(sources_for_load, max_events=999999)
    steps = extract_steps(plan)
    aggregate(steps, all_events)
    unlock = compute_unlock(steps)

    try:
        brief_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create brief dir: {e}", file=sys.stderr)

    for module in ("body", "fitting", "garment"):
        log_path, path_warnings = get_log_path_for_module(
            module, hub_root, sources_cfg
        )
        module_log_warnings = list(path_warnings)

        if log_path and log_path.exists():
            module_events, load_warnings = load_events_from_path(log_path, max_events=20)
            module_log_warnings.extend(load_warnings)
        else:
            module_events = []
            if log_path and not log_path.exists():
                module_log_warnings.append(f"Progress log missing: {log_path}")

        md = render_brief(
            module=module,
            steps=steps,
            unlock=unlock,
            plan=plan,
            log_path_used=log_path,
            module_events=module_events,
            plan_warnings=plan_warnings,
            sources_warnings=sources_warnings,
            module_log_warnings=module_log_warnings,
        )

        out_name = f"{module.upper()}_WORK_BRIEF.md"
        out_path = brief_dir / out_name
        try:
            out_path.write_text(md, encoding="utf-8")
            print(f"Brief written: {out_path}")
        except Exception as e:
            print(f"Warning: Failed to write {out_name}: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
