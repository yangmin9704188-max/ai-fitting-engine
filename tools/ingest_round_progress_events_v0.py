#!/usr/bin/env python3
"""
Round Progress Event Ingest Tool v0 (Round 12)

Extracts progress events from a round markdown's "## Progress Events (dashboard)"
section and appends them to the hub progress log.

Facts-only. Append-only. Exit 0 always.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Required keys for a valid event (presence check only)
REQUIRED_KEYS = {"lab", "module", "step_id", "dod_done_delta", "evidence_paths"}


def extract_jsonl_block(md_text: str) -> Tuple[Optional[str], List[str]]:
    """
    Extract the jsonl fenced code block under "## Progress Events (dashboard)".
    Returns: (block_content or None, warnings)
    """
    warnings: List[str] = []

    # Find the section heading
    section_pattern = r"^##\s+Progress Events\s*\(dashboard\)\s*$"
    lines = md_text.split("\n")
    section_start = None

    for i, line in enumerate(lines):
        if re.match(section_pattern, line.strip(), re.IGNORECASE):
            section_start = i
            break

    if section_start is None:
        warnings.append("Section '## Progress Events (dashboard)' not found")
        return None, warnings

    # Find the next fenced block with ```jsonl
    in_block = False
    block_lines: List[str] = []
    fence_found = False

    for i in range(section_start + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Stop if we hit another section heading (## or #)
        if stripped.startswith("##") or (stripped.startswith("#") and not stripped.startswith("##")):
            break

        if not in_block:
            if stripped.startswith("```jsonl") or stripped == "```jsonl":
                in_block = True
                fence_found = True
                continue
        else:
            if stripped.startswith("```"):
                # End of block
                break
            block_lines.append(line)

    if not fence_found:
        warnings.append("No ```jsonl fenced block found in Progress Events section")
        return None, warnings

    if not block_lines:
        warnings.append("Progress Events jsonl block is empty")
        return None, warnings

    return "\n".join(block_lines), warnings


def parse_event_line(line: str, line_num: int) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Parse a single JSONL line. Returns (event or None, warnings).
    """
    warnings: List[str] = []
    stripped = line.strip()

    # Skip empty lines and comment lines
    if not stripped or stripped.startswith("#"):
        return None, []

    try:
        event = json.loads(stripped)
    except json.JSONDecodeError as e:
        warnings.append(f"Line {line_num}: invalid JSON ({e})")
        return None, warnings

    if not isinstance(event, dict):
        warnings.append(f"Line {line_num}: not a JSON object")
        return None, warnings

    # Check required keys (presence only)
    missing = REQUIRED_KEYS - set(event.keys())
    if missing:
        warnings.append(f"Line {line_num}: missing required keys {missing}")
        return None, warnings

    return event, warnings


def add_timestamp_if_missing(event: Dict[str, Any]) -> Dict[str, Any]:
    """Add ts field if missing, using current time with +09:00 timezone."""
    if "ts" not in event:
        tz_kst = timezone(timedelta(hours=9))
        now = datetime.now(tz_kst)
        event["ts"] = now.isoformat()
    return event


def compute_line_hash(round_path: str, line_content: str) -> str:
    """Compute a hash for dedup: sha256(round_path + line_content)."""
    data = f"{round_path}:{line_content}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def load_recent_hashes(log_path: Path, n_lines: int = 500) -> set:
    """Load hashes from the last N lines of the log for weak dedup."""
    hashes: set = set()
    if not log_path.exists():
        return hashes

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Take last n_lines
        recent = lines[-n_lines:] if len(lines) > n_lines else lines

        for line in recent:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                evt = json.loads(stripped)
                # Check for _ingest_hash field
                if "_ingest_hash" in evt:
                    hashes.add(evt["_ingest_hash"])
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    return hashes


def append_events_to_log(
    log_path: Path,
    events: List[Dict[str, Any]],
    raw_lines: List[str],
    round_path: str,
    existing_hashes: set,
    dry_run: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Append events to log. Returns (appended_count, skipped_count, warnings).
    raw_lines: original JSON lines (before ts added) for stable hash.
    """
    warnings: List[str] = []
    appended = 0
    skipped = 0

    if dry_run:
        for i, evt in enumerate(events):
            raw = raw_lines[i] if i < len(raw_lines) else ""
            line_hash = compute_line_hash(round_path, raw)
            if line_hash in existing_hashes:
                skipped += 1
            else:
                appended += 1
        return appended, skipped, warnings

    # Ensure log directory exists
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        warnings.append(f"Cannot create log directory: {e}")
        return 0, len(events), warnings

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            for i, evt in enumerate(events):
                # Compute hash from raw line (before ts added)
                raw = raw_lines[i] if i < len(raw_lines) else ""
                line_hash = compute_line_hash(round_path, raw)

                if line_hash in existing_hashes:
                    skipped += 1
                    continue

                # Add ingest hash for future dedup
                evt["_ingest_hash"] = line_hash
                final_json = json.dumps(evt, ensure_ascii=False, separators=(",", ":"))
                f.write(final_json + "\n")
                appended += 1
                existing_hashes.add(line_hash)
    except Exception as e:
        warnings.append(f"Failed to write to log: {e}")
        return appended, skipped + (len(events) - appended), warnings

    return appended, skipped, warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest progress events from a round markdown (Round 12)"
    )
    parser.add_argument(
        "--round-path",
        type=str,
        required=True,
        help="Path to the round markdown file"
    )
    parser.add_argument(
        "--hub-root",
        type=str,
        default=".",
        help="Hub root directory (default: current directory)"
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default=None,
        help="Progress log path (default: <hub-root>/exports/progress/PROGRESS_LOG.jsonl)"
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=100,
        help="Maximum events to process (default: 100)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report only; do not append to log"
    )
    args = parser.parse_args()

    hub_root = Path(args.hub_root).resolve()
    round_path = Path(args.round_path)

    if not round_path.is_absolute():
        round_path = hub_root / round_path

    if args.log_path:
        log_path = Path(args.log_path)
        if not log_path.is_absolute():
            log_path = hub_root / log_path
    else:
        log_path = hub_root / "exports" / "progress" / "PROGRESS_LOG.jsonl"

    all_warnings: List[str] = []

    # Check round file exists
    if not round_path.exists():
        all_warnings.append(f"Round file not found: {round_path}")
        print(f"[ingest] Round file not found: {round_path}", file=sys.stderr)
        print("[ingest] Warnings:", len(all_warnings))
        for w in all_warnings:
            print(f"  - {w}", file=sys.stderr)
        sys.exit(0)

    # Read round markdown
    try:
        md_text = round_path.read_text(encoding="utf-8")
    except Exception as e:
        all_warnings.append(f"Failed to read round file: {e}")
        print(f"[ingest] Failed to read round file: {e}", file=sys.stderr)
        sys.exit(0)

    # Extract jsonl block
    block_content, extract_warnings = extract_jsonl_block(md_text)
    all_warnings.extend(extract_warnings)

    if block_content is None:
        print(f"[ingest] No progress events found in {round_path.name}")
        if all_warnings:
            print("[ingest] Warnings:")
            for w in all_warnings:
                print(f"  - {w}", file=sys.stderr)
        sys.exit(0)

    # Parse events
    events: List[Dict[str, Any]] = []
    lines = block_content.split("\n")

    raw_lines: List[str] = []  # Keep raw lines for hash calculation
    for i, line in enumerate(lines[:args.max_events], 1):
        evt, parse_warnings = parse_event_line(line, i)
        all_warnings.extend(parse_warnings)
        if evt:
            raw_lines.append(line.strip())
            evt = add_timestamp_if_missing(evt)
            events.append(evt)

    if not events:
        print(f"[ingest] No valid events in {round_path.name}")
        if all_warnings:
            print("[ingest] Warnings:")
            for w in all_warnings:
                print(f"  - {w}", file=sys.stderr)
        sys.exit(0)

    # Load existing hashes for dedup
    existing_hashes = load_recent_hashes(log_path, n_lines=500)

    # Append events
    round_path_str = str(round_path.resolve())
    appended, skipped, append_warnings = append_events_to_log(
        log_path=log_path,
        events=events,
        raw_lines=raw_lines,
        round_path=round_path_str,
        existing_hashes=existing_hashes,
        dry_run=args.dry_run
    )
    all_warnings.extend(append_warnings)

    # Report
    mode_label = "[dry-run] " if args.dry_run else ""
    print(f"[ingest] {mode_label}Round: {round_path.name}")
    print(f"[ingest] {mode_label}Events parsed: {len(events)}")
    print(f"[ingest] {mode_label}Appended: {appended}, Skipped (dedup): {skipped}")
    print(f"[ingest] {mode_label}Log: {log_path}")

    if all_warnings:
        print("[ingest] Warnings:")
        for w in all_warnings:
            print(f"  - {w}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
