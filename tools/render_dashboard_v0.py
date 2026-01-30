#!/usr/bin/env python3
"""
Dashboard v0 Renderer

Reads PLAN_v0.yaml + LAB_SOURCES_v0.yaml + PROGRESS_LOG.jsonl,
aggregates DoD progress per step, computes unlock status,
and renders PROJECT_DASHBOARD.md.

Facts-only. No PASS/FAIL. No threshold/clamp. No date estimation.
Exit 0 always (errors degrade gracefully as warnings in dashboard).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Minimal YAML parser (scoped to dashboard config structures) ──────────

def _indent_of(line: str) -> int:
    """Count leading spaces."""
    return len(line) - len(line.lstrip(" "))


def _strip_comment(line: str) -> str:
    """Strip inline comment outside of quotes."""
    in_q: Optional[str] = None
    for i, ch in enumerate(line):
        if ch in ('"', "'") and in_q is None:
            in_q = ch
        elif ch == in_q:
            in_q = None
        elif ch == "#" and in_q is None:
            return line[:i].rstrip()
    return line.rstrip()


def _parse_scalar(val: str) -> Any:
    """Parse a YAML scalar value."""
    v = val.strip()
    if not v or v in ("~", "null", "Null", "NULL"):
        return None
    if v in ("true", "True", "TRUE"):
        return True
    if v in ("false", "False", "FALSE"):
        return False
    # Flow-style array: ["a", "b"] or []
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    # Quoted string
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    # Integer
    try:
        return int(v)
    except ValueError:
        pass
    # Float
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _split_kv(s: str) -> Tuple[str, Optional[str]]:
    """Split 'key: value' -> (key, value_str) or (key, None) if value is nested."""
    # Find the first ':' that is followed by space or EOL and not inside quotes
    in_q: Optional[str] = None
    for i, ch in enumerate(s):
        if ch in ('"', "'") and in_q is None:
            in_q = ch
        elif ch == in_q:
            in_q = None
        elif ch == ":" and in_q is None:
            after = s[i + 1:]
            if not after or after[0] == " ":
                key = s[:i].strip().strip('"').strip("'")
                val = after.strip()
                return (key, val if val else None)
    return (s.strip(), None)


def _skip(lines: List[str], i: int) -> int:
    """Skip blank and comment-only lines."""
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith("#"):
            return i
        i += 1
    return i


def _parse_block(lines: List[str], i: int, base: int) -> Tuple[Any, int]:
    """Recursively parse a YAML block at expected indent `base`."""
    i = _skip(lines, i)
    if i >= len(lines):
        return None, i
    ind = _indent_of(lines[i])
    content = lines[i][ind:]
    if content.startswith("- "):
        return _parse_list(lines, i, ind)
    return _parse_dict(lines, i, ind)


def _parse_dict(lines: List[str], i: int, base: int) -> Tuple[Dict, int]:
    result: Dict[str, Any] = {}
    while True:
        i = _skip(lines, i)
        if i >= len(lines):
            break
        ind = _indent_of(lines[i])
        if ind != base:
            break
        content = _strip_comment(lines[i][ind:])
        if content.startswith("- "):
            break
        k, v = _split_kv(content)
        if v is not None:
            result[k] = _parse_scalar(v)
            i += 1
        else:
            child, i = _parse_block(lines, i + 1, base + 2)
            result[k] = child
    return result, i


def _parse_list(lines: List[str], i: int, base: int) -> Tuple[List, int]:
    result: List[Any] = []
    while True:
        i = _skip(lines, i)
        if i >= len(lines):
            break
        ind = _indent_of(lines[i])
        if ind != base:
            break
        content = _strip_comment(lines[i][ind:])
        if not content.startswith("- "):
            break
        after = content[2:]
        k, v = _split_kv(after)
        # Check if after dash is a key-value pair
        if v is not None or (v is None and ":" in after and not after.startswith('"') and not after.startswith("'")):
            # Dict item in list
            item: Dict[str, Any] = {}
            if v is not None:
                item[k] = _parse_scalar(v)
                i += 1
            else:
                child, i = _parse_block(lines, i + 1, base + 4)
                item[k] = child
            # Continuation keys at base + 2
            cont = base + 2
            while True:
                j = _skip(lines, i)
                if j >= len(lines):
                    i = j
                    break
                ci = _indent_of(lines[j])
                if ci != cont:
                    i = j
                    break
                cs = _strip_comment(lines[j][ci:])
                if cs.startswith("- "):
                    i = j
                    break
                ck, cv = _split_kv(cs)
                if cv is not None:
                    item[ck] = _parse_scalar(cv)
                    i = j + 1
                else:
                    child, i = _parse_block(lines, j + 1, ci + 2)
                    item[ck] = child
            result.append(item)
        else:
            # Scalar item
            result.append(_parse_scalar(after))
            i += 1
    return result, i


def load_yaml(path: Path) -> Any:
    """Load YAML: PyYAML first, minimal parser fallback."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    lines = text.split("\n")
    result, _ = _parse_block(lines, 0, 0)
    return result if result else {}


# ── Data Loading ─────────────────────────────────────────────────────────

def load_plan(path: Path) -> Tuple[Dict, List[str]]:
    """Load PLAN and return (plan_dict, warnings)."""
    warnings: List[str] = []
    if not path.exists():
        warnings.append(f"PLAN not found: {path}")
        return {}, warnings
    try:
        plan = load_yaml(path)
    except Exception as e:
        warnings.append(f"PLAN parse error: {e}")
        return {}, warnings
    return plan, warnings


def load_sources(path: Path) -> Tuple[Dict, List[str]]:
    """Load LAB_SOURCES and return (sources_dict, warnings)."""
    warnings: List[str] = []
    if not path.exists():
        warnings.append(f"LAB_SOURCES not found: {path}")
        return {}, warnings
    try:
        data = load_yaml(path)
    except Exception as e:
        warnings.append(f"LAB_SOURCES parse error: {e}")
        return {}, warnings
    return data.get("sources", {}), warnings


def load_events(sources: Dict, max_events: int) -> Tuple[List[Dict], List[str]]:
    """Load events from all PROGRESS_LOG.jsonl files. Return (events, warnings)."""
    all_events: List[Dict] = []
    warnings: List[str] = []

    for lab_name, lab_cfg in sources.items():
        if not isinstance(lab_cfg, dict):
            continue
        log_path_str = lab_cfg.get("progress_log_path", "")
        if not log_path_str or "TBD" in str(log_path_str).upper():
            warnings.append(f"source '{lab_name}': path is TBD ({log_path_str})")
            continue
        log_path = Path(log_path_str)
        if not log_path.exists():
            warnings.append(f"source '{lab_name}': file missing ({log_path})")
            continue
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        evt = json.loads(line)
                        all_events.append(evt)
                    except json.JSONDecodeError as e:
                        warnings.append(f"source '{lab_name}' line {line_num}: JSON error ({e})")
        except Exception as e:
            warnings.append(f"source '{lab_name}': read error ({e})")

    # Sort by ts descending
    all_events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    return all_events, warnings


# ── Aggregation ──────────────────────────────────────────────────────────

def extract_steps(plan: Dict) -> Dict[str, Dict]:
    """Extract all steps from PLAN into {step_id: step_info} map."""
    steps: Dict[str, Dict] = {}
    modules = plan.get("modules", {})
    if not isinstance(modules, dict):
        return steps
    for mod_name, mod_data in modules.items():
        if not isinstance(mod_data, dict):
            continue
        for step in mod_data.get("steps", []):
            if not isinstance(step, dict):
                continue
            sid = step.get("id", "")
            if not sid:
                continue
            dod = step.get("dod", {})
            dod_total = dod.get("total") if isinstance(dod, dict) else None
            dod_items = dod.get("items", []) if isinstance(dod, dict) else []
            depends = step.get("depends_on", [])
            unlocks = step.get("unlocks", [])
            steps[sid] = {
                "id": sid,
                "name": step.get("name", ""),
                "layer": step.get("layer", ""),
                "module": mod_name,
                "depends_on": depends if isinstance(depends, list) else [],
                "unlocks": unlocks if isinstance(unlocks, list) else [],
                "dod_total": dod_total,
                "dod_items": dod_items if isinstance(dod_items, list) else [],
                "dod_done": 0,
            }
    return steps


def aggregate(steps: Dict[str, Dict], events: List[Dict]) -> None:
    """Aggregate events into steps (mutates steps in-place)."""
    for evt in events:
        sid = evt.get("step_id", "")
        delta = evt.get("dod_done_delta", 0)
        if sid in steps and isinstance(delta, (int, float)) and delta > 0:
            steps[sid]["dod_done"] += int(delta)
    # Clamp dod_done to dod_total (facts-only: renderer caps, does not judge)
    for s in steps.values():
        t = s["dod_total"]
        if isinstance(t, int) and s["dod_done"] > t:
            s["dod_done"] = t


def compute_unlock(steps: Dict[str, Dict]) -> Dict[str, str]:
    """Compute unlock status for each step. Returns {step_id: status_string}."""
    result: Dict[str, str] = {}
    for sid, s in steps.items():
        deps = s["depends_on"]
        if not deps:
            result[sid] = "UNLOCKED"
            continue
        all_met = True
        unknown = False
        for dep_ref in deps:
            # dep_ref is like "body:B01"
            dep_id = dep_ref.split(":")[-1] if ":" in dep_ref else dep_ref
            dep_step = steps.get(dep_id)
            if not dep_step:
                unknown = True
                all_met = False
                continue
            dt = dep_step["dod_total"]
            if not isinstance(dt, int):
                unknown = True
                all_met = False
                continue
            if dep_step["dod_done"] < dt:
                all_met = False
        if unknown:
            result[sid] = "BLOCKED (unknown prerequisite)"
        elif all_met:
            result[sid] = "UNLOCKED"
        else:
            result[sid] = "BLOCKED"
    return result


# ── Markdown Rendering ───────────────────────────────────────────────────

def _fmt_progress(done: int, total) -> str:
    if not isinstance(total, int):
        return f"{done}/N·A"
    return f"{done}/{total}"


def _fmt_pct(done: int, total) -> str:
    if not isinstance(total, int) or total == 0:
        return "—%"
    return f"{int(done * 100 / total)}%"


def render_dashboard(
    plan: Dict,
    steps: Dict[str, Dict],
    unlock: Dict[str, str],
    events: List[Dict],
    sources_warnings: List[str],
    event_warnings: List[str],
    plan_warnings: List[str],
    max_events: int,
    plan_path: str,
    sources_path: str,
    contract_path: str,
    sources_cfg: Dict,
) -> str:
    """Render the full PROJECT_DASHBOARD.md content."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    milestone = plan.get("milestone", "unknown")

    lines: List[str] = []

    # ── Header ──
    lines.append("<!-- GENERATED — DO NOT EDIT MANUALLY -->")
    lines.append("<!-- This file is rendered by tools/render_dashboard_v0.py -->")
    lines.append("<!-- Manual edits will be overwritten on next render cycle. -->")
    lines.append(f"<!-- To change plan/structure: edit {plan_path} -->")
    lines.append(f"<!-- To change data sources: edit {sources_path} -->")
    lines.append("")
    lines.append("# Project Dashboard")
    lines.append("")
    lines.append(f"**Milestone**: {milestone}")
    lines.append(f"**Rendered**: {now_utc}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Data Sources ──
    lines.append("## Data Sources")
    lines.append("")
    lines.append("| Source | Path | Status |")
    lines.append("|--------|------|--------|")
    lines.append(f"| Plan (SSoT) | `{plan_path}` | loaded |")
    lines.append(f"| Lab Sources | `{sources_path}` | loaded |")
    lines.append(f"| Export Contract | `{contract_path}` | reference |")
    for lab_name in sources_cfg:
        cfg = sources_cfg[lab_name] if isinstance(sources_cfg[lab_name], dict) else {}
        lp = cfg.get("progress_log_path", "")
        mods = cfg.get("modules", [])
        mod_label = ", ".join(mods) if isinstance(mods, list) else ""
        if "TBD" in str(lp).upper():
            status = "TBD"
        elif lp and Path(lp).exists():
            status = "loaded"
        elif lp:
            status = "missing"
        else:
            status = "not configured"
        label = f"{lab_name} ({mod_label})" if mod_label else lab_name
        lines.append(f"| {label} log | `{lp}` | {status} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Phase × Module Matrix ──
    phases = plan.get("phases", [])
    mod_order = ["body", "fitting", "garment"]

    lines.append("## Phase x Module Matrix")
    lines.append("")
    lines.append("| Phase | Body | Fitting | Garment |")
    lines.append("|-------|------|---------|---------|")
    for ph in (phases if isinstance(phases, list) else []):
        if not isinstance(ph, dict):
            continue
        pid = ph.get("id", "")
        pname = ph.get("name", "")
        cells: Dict[str, List[str]] = {m: [] for m in mod_order}
        for ps in ph.get("steps", []):
            if not isinstance(ps, dict):
                continue
            pm = ps.get("module", "")
            psid = ps.get("step_id", "")
            s = steps.get(psid)
            if s:
                cells.setdefault(pm, []).append(f"{psid}: {_fmt_progress(s['dod_done'], s['dod_total'])}")
            else:
                cells.setdefault(pm, []).append(f"{psid}: —")
        row_cells = []
        for m in mod_order:
            c = cells.get(m, [])
            row_cells.append(" , ".join(c) if c else "—")
        lines.append(f"| **{pid}** {pname} | {row_cells[0]} | {row_cells[1]} | {row_cells[2]} |")
    lines.append("")
    lines.append("> Cell format: `<step_id>: <done>/<total>`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Module Progress ──
    lines.append("## Module Progress")
    lines.append("")
    for mod_name in mod_order:
        mod_steps = [s for s in steps.values() if s["module"] == mod_name]
        if not mod_steps:
            continue
        # Sort by id
        mod_steps.sort(key=lambda x: x["id"])
        lines.append(f"### {mod_name.capitalize()}")
        lines.append("")
        lines.append("| Step | Name | Layer | Done | Total | Progress | Unlocks |")
        lines.append("|------|------|-------|------|-------|----------|---------|")
        total_done = 0
        total_total = 0
        for s in mod_steps:
            sid = s["id"]
            dt = s["dod_total"]
            dd = s["dod_done"]
            total_done += dd
            if isinstance(dt, int):
                total_total += dt
            ul = ", ".join(s["unlocks"]) if s["unlocks"] else "—"
            dt_str = str(dt) if isinstance(dt, int) else "N/A"
            lines.append(f"| {sid} | {s['name']} | {s['layer']} | {dd} | {dt_str} | {_fmt_pct(dd, dt)} | {ul} |")
        lines.append(f"| **Total** | | | **{total_done}** | **{total_total}** | **{_fmt_pct(total_done, total_total)}** | |")
        lines.append("")

    lines.append("---")
    lines.append("")

    # ── Unlock Status ──
    lines.append("## Unlock Status")
    lines.append("")
    lines.append("| Step | Depends On | Unlock Status |")
    lines.append("|------|------------|---------------|")
    for sid in sorted(steps.keys()):
        s = steps[sid]
        deps = ", ".join(s["depends_on"]) if s["depends_on"] else "(none)"
        status = unlock.get(sid, "BLOCKED")
        lines.append(f"| {sid} | {deps} | {status} |")
    lines.append("")
    lines.append("> UNLOCKED = all dependencies have done == total. BLOCKED = at least one dependency incomplete.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Warnings ──
    all_warnings = plan_warnings + sources_warnings + event_warnings
    if all_warnings:
        lines.append("## Warnings (facts-only)")
        lines.append("")
        for w in all_warnings:
            lines.append(f"- {w}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # ── Recent Events ──
    lines.append("## Recent Events")
    lines.append("")
    display_events = events[:max_events]
    if display_events:
        lines.append("| # | Timestamp | Lab | Module | Step | Delta | Evidence Count | Note |")
        lines.append("|---|-----------|-----|--------|------|-------|----------------|------|")
        for idx, evt in enumerate(display_events, 1):
            ts = evt.get("ts", "—")
            lab = evt.get("lab", "—")
            mod = evt.get("module", "—")
            sid = evt.get("step_id", "—")
            delta = evt.get("dod_done_delta", "—")
            ep = evt.get("evidence_paths", [])
            ep_count = len(ep) if isinstance(ep, list) else "—"
            note = evt.get("note", "")
            lines.append(f"| {idx} | {ts} | {lab} | {mod} | {sid} | {delta} | {ep_count} | {note} |")
    else:
        lines.append("| # | Timestamp | Lab | Module | Step | Delta | Evidence Count | Note |")
        lines.append("|---|-----------|-----|--------|------|-------|----------------|------|")
        lines.append("| — | (no events collected) | | | | | | |")
    lines.append("")
    lines.append(f"> Maximum {max_events} most recent events displayed. Full history in each lab's PROGRESS_LOG.jsonl.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Mermaid (optional, dependency flowchart only) ──
    lines.append("## Dependency Graph (Mermaid, optional viewer support)")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    for sid in sorted(steps.keys()):
        s = steps[sid]
        label = f"{sid} {s['name']}"
        for dep_ref in s["depends_on"]:
            dep_id = dep_ref.split(":")[-1] if ":" in dep_ref else dep_ref
            dep_s = steps.get(dep_id)
            dep_label = f"{dep_id} {dep_s['name']}" if dep_s else dep_id
            lines.append(f"    {dep_id}[{dep_label}] --> {sid}[{label}]")
    # Also emit orphan nodes (no incoming or outgoing edges)
    connected = set()
    for s in steps.values():
        if s["depends_on"]:
            connected.add(s["id"])
            for d in s["depends_on"]:
                connected.add(d.split(":")[-1] if ":" in d else d)
    for sid in sorted(steps.keys()):
        if sid not in connected:
            s = steps[sid]
            lines.append(f"    {sid}[{sid} {s['name']}]")
    lines.append("```")
    lines.append("")
    lines.append("> Text tables above are the primary view. Mermaid is supplementary only.")
    lines.append("")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard v0 Renderer")
    parser.add_argument("--hub-root", default=".", help="Project hub root (default: cwd)")
    parser.add_argument("--plan-path", default=None, help="Override PLAN_v0.yaml path")
    parser.add_argument("--sources-path", default=None, help="Override LAB_SOURCES_v0.yaml path")
    parser.add_argument("--dashboard-path", default=None, help="Override output dashboard path")
    parser.add_argument("--max-events", type=int, default=20, help="Max recent events (default: 20)")
    args = parser.parse_args()

    hub = Path(args.hub_root).resolve()

    plan_path = Path(args.plan_path) if args.plan_path else hub / "docs" / "ops" / "dashboard" / "PLAN_v0.yaml"
    sources_path = Path(args.sources_path) if args.sources_path else hub / "docs" / "ops" / "dashboard" / "LAB_SOURCES_v0.yaml"
    dashboard_path = Path(args.dashboard_path) if args.dashboard_path else hub / "docs" / "ops" / "PROJECT_DASHBOARD.md"
    contract_rel = "docs/ops/dashboard/EXPORT_CONTRACT_v0.md"

    # Relative display paths
    try:
        plan_rel = str(plan_path.relative_to(hub))
    except ValueError:
        plan_rel = str(plan_path)
    try:
        sources_rel = str(sources_path.relative_to(hub))
    except ValueError:
        sources_rel = str(sources_path)

    # Load
    plan, plan_warnings = load_plan(plan_path)
    sources_cfg, sources_warnings = load_sources(sources_path)
    events, event_warnings = load_events(sources_cfg, args.max_events)

    # Aggregate
    steps = extract_steps(plan)
    aggregate(steps, events)
    unlock = compute_unlock(steps)

    # Render
    md = render_dashboard(
        plan=plan,
        steps=steps,
        unlock=unlock,
        events=events,
        sources_warnings=sources_warnings,
        event_warnings=event_warnings,
        plan_warnings=plan_warnings,
        max_events=args.max_events,
        plan_path=plan_rel.replace("\\", "/"),
        sources_path=sources_rel.replace("\\", "/"),
        contract_path=contract_rel,
        sources_cfg=sources_cfg,
    )

    # Write
    try:
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(md, encoding="utf-8")
        print(f"Dashboard rendered: {dashboard_path}")
    except Exception as e:
        print(f"Warning: Failed to write dashboard: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
