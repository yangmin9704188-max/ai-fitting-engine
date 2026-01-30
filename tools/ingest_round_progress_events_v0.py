#!/usr/bin/env python3
"""
Round Progress Event Ingest v0

Extracts progress events from a round markdown document's
"## Progress Events (dashboard)" ```jsonl fenced block,
validates required keys, and appends them to PROGRESS_LOG.jsonl.

Facts-only. No PASS/FAIL. Exit 0 always.
Errors are warnings to stderr only (no crash).

Authoritative contract: docs/ops/dashboard/EXPORT_CONTRACT_v0.md §3.

Usage:
  py tools/ingest_round_progress_events_v0.py \\
    --round-path docs/ops/rounds/round71.md

  py tools/ingest_round_progress_events_v0.py \\
    --round-path docs/ops/rounds/round71.md --dry-run

  py tools/ingest_round_progress_events_v0.py \\
    --round-path docs/ops/rounds/round71.md \\
    --log-path exports/progress/PROGRESS_LOG.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))

REQUIRED_KEYS = {"lab", "module", "step_id", "dod_done_delta", "evidence_paths"}

DEDUP_TAIL_LINES = 200


def extract_jsonl_block(round_text: str) -> list[str]:
    """Extract lines from the first ```jsonl block under '## Progress Events (dashboard)'."""
    lines = round_text.split("\n")
    in_section = False
    in_fence = False
    result: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Detect section header
        if stripped.startswith("## Progress Events"):
            in_section = True
            continue

        # Another H2 heading ends the section
        if in_section and stripped.startswith("## ") and not stripped.startswith("## Progress Events"):
            break

        if not in_section:
            continue

        # Inside section: look for ```jsonl fence
        if not in_fence and stripped.startswith("```jsonl"):
            in_fence = True
            continue

        if in_fence and stripped.startswith("```"):
            break

        if in_fence and stripped:
            result.append(stripped)

    return result


def validate_event(evt: dict) -> list[str]:
    """Check required keys exist. Return list of missing key names."""
    return [k for k in REQUIRED_KEYS if k not in evt]


def compute_line_hash(round_path_str: str, raw_line: str) -> str:
    """Compute a short hash for weak dedup (round_path + raw_line)."""
    payload = f"{round_path_str}|{raw_line}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load_tail_hashes(log_path: Path, n: int) -> set[str]:
    """Load _ingest_hash values from the last N lines of log."""
    if not log_path.exists():
        return set()
    hashes: set[str] = set()
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        for raw in all_lines[-n:]:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
                h = obj.get("_ingest_hash")
                if h:
                    hashes.add(h)
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest progress events from round markdown into PROGRESS_LOG.jsonl"
    )
    parser.add_argument("--round-path", required=True,
                        help="Path to round markdown file")
    parser.add_argument("--log-path", default=None,
                        help="Path to PROGRESS_LOG.jsonl (default: exports/progress/PROGRESS_LOG.jsonl)")
    parser.add_argument("--max-events", type=int, default=100,
                        help="Max events to ingest per round (default: 100)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and validate only, do not append")

    args = parser.parse_args()

    round_path = Path(args.round_path)
    log_path = (Path(args.log_path) if args.log_path
                else Path.cwd() / "exports" / "progress" / "PROGRESS_LOG.jsonl")

    # ── Read round document ──
    if not round_path.exists():
        print(f"Warning: round file not found: {round_path}. No events ingested.",
              file=sys.stderr)
        sys.exit(0)

    try:
        round_text = round_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: cannot read {round_path}: {e}. No events ingested.",
              file=sys.stderr)
        sys.exit(0)

    # ── Extract jsonl block ──
    raw_lines = extract_jsonl_block(round_text)
    if not raw_lines:
        print(f"No 'Progress Events (dashboard)' jsonl block found in {round_path}. "
              f"Nothing to ingest.", file=sys.stderr)
        sys.exit(0)

    # ── Cap ──
    if len(raw_lines) > args.max_events:
        print(f"Warning: {len(raw_lines)} lines exceed --max-events={args.max_events}. "
              f"Truncating.", file=sys.stderr)
        raw_lines = raw_lines[:args.max_events]

    # ── Load existing hashes for weak dedup ──
    existing_hashes = load_tail_hashes(log_path, DEDUP_TAIL_LINES)

    # ── Parse, validate, dedup ──
    events_to_append: list[dict] = []
    round_path_str = str(round_path).replace("\\", "/")
    ts_now = datetime.now(KST).isoformat()

    for idx, raw in enumerate(raw_lines, 1):
        # Parse JSON
        try:
            evt = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"Warning: line {idx} JSON parse error: {e}. Skipped.",
                  file=sys.stderr)
            continue

        if not isinstance(evt, dict):
            print(f"Warning: line {idx} is not a JSON object. Skipped.",
                  file=sys.stderr)
            continue

        # Validate required keys
        missing = validate_event(evt)
        if missing:
            print(f"Warning: line {idx} missing required keys: "
                  f"{', '.join(missing)}. Skipped.", file=sys.stderr)
            continue

        # Add ts if missing
        if "ts" not in evt:
            evt["ts"] = ts_now

        # Weak dedup
        line_hash = compute_line_hash(round_path_str, raw)
        if line_hash in existing_hashes:
            print(f"Dedup: line {idx} already ingested (hash={line_hash}). Skipped.",
                  file=sys.stderr)
            continue

        # Attach ingest metadata (underscore-prefixed, ignored by renderer)
        evt["_ingest_hash"] = line_hash
        evt["_ingest_source"] = round_path_str

        events_to_append.append(evt)

    if not events_to_append:
        print("No new events to append.", file=sys.stderr)
        sys.exit(0)

    # ── Dry-run ──
    if args.dry_run:
        print(f"Dry-run: {len(events_to_append)} event(s) would be appended to {log_path}")
        for evt in events_to_append:
            print(json.dumps(evt, ensure_ascii=False, separators=(",", ":")))
        sys.exit(0)

    # ── Ensure directory ──
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: cannot create directory {log_path.parent}: {e}",
              file=sys.stderr)
        sys.exit(0)

    # ── Append ──
    try:
        with open(log_path, "a", encoding="utf-8", newline="") as f:
            for evt in events_to_append:
                line = json.dumps(evt, ensure_ascii=False, separators=(",", ":"))
                f.write(line + "\n")
            f.flush()
    except Exception as e:
        print(f"Warning: cannot write to {log_path}: {e}", file=sys.stderr)
        sys.exit(0)

    print(f"Ingested {len(events_to_append)} event(s) from {round_path} -> {log_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
