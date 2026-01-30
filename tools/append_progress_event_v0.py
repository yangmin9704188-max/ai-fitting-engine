#!/usr/bin/env python3
"""
Progress Event Appender v0

Appends a single progress event line to PROGRESS_LOG.jsonl.
Convenience tool — the authoritative contract is EXPORT_CONTRACT_v0.md §3.

Policy on invalid input:
  Required args missing → print warning to stderr, write nothing, exit 0.
  dod_done_delta < 0   → print warning to stderr, write nothing, exit 0.
  File/dir missing     → create parent dirs and file automatically.

Examples:
  1) From fitting_lab/ folder (CWD-relative default):
     py ../AI_model/tools/append_progress_event_v0.py \\
       --lab fitting_lab --module fitting --step-id F01 \\
       --dod-done-delta 1 --dod-total 3 \\
       --evidence-path docs/contract/fitting_interface_v0.md \\
       --note "fitting_interface_v0.md ported"

  2) From AI_model/ folder targeting fitting_lab via --lab-root:
     py tools/append_progress_event_v0.py \\
       --lab-root C:/path/to/fitting_lab \\
       --lab fitting_lab --module fitting --step-id F02 \\
       --dod-done-delta 2 --dod-total 2 \\
       --evidence-path modules/fitting/runners/run_fitting_v0_facts.py \\
       --evidence-path modules/fitting/specs/fitting_manifest.schema.json

  3) Using --log-path explicitly (e.g., hub body events):
     py tools/append_progress_event_v0.py \\
       --log-path exports/progress/PROGRESS_LOG.jsonl \\
       --lab hub --module body --step-id B01 \\
       --dod-done-delta 1 --dod-total 3 \\
       --evidence-path docs/contract/standard_keys.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))


def resolve_log_path(args: argparse.Namespace) -> Path:
    """Resolve the target PROGRESS_LOG.jsonl path."""
    if args.log_path:
        return Path(args.log_path)
    if args.lab_root:
        return Path(args.lab_root) / "exports" / "progress" / "PROGRESS_LOG.jsonl"
    return Path.cwd() / "exports" / "progress" / "PROGRESS_LOG.jsonl"


def build_event(args: argparse.Namespace) -> dict | None:
    """Build the event dict from CLI args. Returns None on validation failure."""
    # Required fields
    missing = []
    if not args.lab:
        missing.append("--lab")
    if not args.module:
        missing.append("--module")
    if not args.step_id:
        missing.append("--step-id")
    if args.dod_done_delta is None:
        missing.append("--dod-done-delta")

    if missing:
        print(f"Warning: missing required args: {', '.join(missing)}. No event written.", file=sys.stderr)
        return None

    delta = args.dod_done_delta
    if not isinstance(delta, int) or delta < 0:
        print(f"Warning: --dod-done-delta must be integer >= 0 (got {delta!r}). No event written.", file=sys.stderr)
        return None

    # Timestamp
    if args.ts:
        ts = args.ts
    else:
        ts = datetime.now(KST).isoformat()

    event: dict = {
        "ts": ts,
        "lab": args.lab,
        "module": args.module,
        "step_id": args.step_id,
        "dod_done_delta": delta,
    }

    if args.dod_total is not None:
        event["dod_total"] = args.dod_total

    event["evidence_paths"] = list(args.evidence_path) if args.evidence_path else []

    if args.rid:
        event["rid"] = args.rid
    if args.note:
        event["note"] = args.note

    return event


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append a single progress event to PROGRESS_LOG.jsonl"
    )

    # Log path resolution
    path_group = parser.add_argument_group("log path (pick one)")
    path_group.add_argument("--log-path", default=None, help="Exact path to PROGRESS_LOG.jsonl")
    path_group.add_argument("--lab-root", default=None, help="Lab root dir (appends exports/progress/PROGRESS_LOG.jsonl)")

    # Required event fields
    parser.add_argument("--lab", required=True, help='Lab identifier (e.g., "hub", "fitting_lab")')
    parser.add_argument("--module", required=True, choices=["body", "fitting", "garment"], help="Module name")
    parser.add_argument("--step-id", required=True, help="Step ID from PLAN_v0.yaml (e.g., B01, F02)")
    parser.add_argument("--dod-done-delta", type=int, required=True, help="Number of DoD items completed (>= 0)")

    # Optional event fields
    parser.add_argument("--dod-total", type=int, default=None, help="Total DoD items for this step")
    parser.add_argument("--rid", default=None, help="Round ID (interface_ledger_v0.md §4.3 format)")
    parser.add_argument("--note", default=None, help="Free-form note")
    parser.add_argument("--evidence-path", action="append", default=None, help="Evidence file path (repeatable)")
    parser.add_argument("--ts", default=None, help="Timestamp ISO 8601 (default: now +09:00)")

    args = parser.parse_args()

    # Build event
    event = build_event(args)
    if event is None:
        sys.exit(0)

    # Resolve path
    log_path = resolve_log_path(args)

    # Ensure parent directory
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: cannot create directory {log_path.parent}: {e}", file=sys.stderr)
        sys.exit(0)

    # Serialize (compact, single-line, ensure_ascii=False for Korean notes)
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))

    # Append
    try:
        with open(log_path, "a", encoding="utf-8", newline="") as f:
            f.write(line + "\n")
            f.flush()
    except Exception as e:
        print(f"Warning: cannot write to {log_path}: {e}", file=sys.stderr)
        sys.exit(0)

    print(f"Appended progress event to: {log_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
