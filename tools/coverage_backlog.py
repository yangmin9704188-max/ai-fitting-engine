#!/usr/bin/env python3
"""
Coverage Backlog Maintenance Tool

facts_summary.json에서 NaN 100% 키를 추출하여 coverage_backlog.md를 자동 갱신합니다.
Facts-only 기록이며, 판정/추측 없이 누적만 수행합니다.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def extract_round_from_path(run_dir: Path) -> str:
    """Extract round number from run_dir path."""
    # Example: verification/runs/facts/curated_v0/round20_20260125_164801 -> round20
    run_name = run_dir.name
    match = re.search(r'round(\d+)', run_name, re.IGNORECASE)
    if match:
        return f"round{match.group(1)}"
    
    # Try parent directory
    parent_name = run_dir.parent.name
    match = re.search(r'round(\d+)', parent_name, re.IGNORECASE)
    if match:
        return f"round{match.group(1)}"
    
    return "unknown"


def find_100pct_nan_keys(facts_summary_path: Path) -> List[Dict[str, Any]]:
    """Find keys with 100% NaN rate from facts_summary.json."""
    try:
        with open(facts_summary_path, "r", encoding="utf-8") as f:
            facts_data = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load facts_summary.json: {e}", file=sys.stderr)
        return []
    
    summary = facts_data.get("summary", {})
    if not isinstance(summary, dict):
        summary = facts_data.get("statistics", {})
    
    if not isinstance(summary, dict):
        return []
    
    n_samples = facts_data.get("n_samples", 0)
    if not isinstance(n_samples, (int, float)) or n_samples == 0:
        return []
    
    nan_100_keys = []
    for key, stats in summary.items():
        if not isinstance(stats, dict):
            continue
        
        nan_rate_pct = stats.get("nan_rate_pct", 0.0)
        if nan_rate_pct >= 100.0:
            # Check for VALUE_MISSING in warnings
            warnings = stats.get("warnings_top5", [])
            has_value_missing = False
            value_missing_count = 0
            
            if isinstance(warnings, list):
                for w in warnings:
                    if isinstance(w, dict):
                        reason = w.get("reason", "")
                        if "VALUE_MISSING" in reason.upper() or "MISSING" in reason.upper():
                            has_value_missing = True
                            value_missing_count = w.get("n", 0)
                            break
            
            # Generate note
            if has_value_missing:
                note = f"coverage gap suspected (VALUE_MISSING: {value_missing_count}/{n_samples})"
            else:
                note = "all-null in curated_v0"
            
            nan_100_keys.append({
                "key": key,
                "nan_rate_pct": nan_rate_pct,
                "n_samples": n_samples,
                "note": note,
                "has_value_missing": has_value_missing
            })
    
    # Sort by VALUE_MISSING priority, then by key name
    nan_100_keys.sort(key=lambda x: (not x["has_value_missing"], x["key"]))
    
    return nan_100_keys


def parse_existing_backlog(backlog_path: Path) -> tuple[str, Dict[str, Dict[str, Any]]]:
    """Parse existing backlog and extract manual notes and existing entries."""
    if not backlog_path.exists():
        return "", {}
    
    try:
        with open(backlog_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return "", {}
    
    # Split by auto-generated markers
    auto_start = "<!-- AUTO-GENERATED:START -->"
    auto_end = "<!-- AUTO-GENERATED:END -->"
    
    if auto_start in content and auto_end in content:
        parts = content.split(auto_start, 1)
        manual_part = parts[0]
        auto_part = parts[1].split(auto_end, 1)[0] if len(parts) > 1 else ""
        manual_after = parts[1].split(auto_end, 1)[1] if len(parts) > 1 and auto_end in parts[1] else ""
    else:
        # No markers, treat all as manual
        manual_part = content
        auto_part = ""
        manual_after = ""
    
    # Parse existing entries from auto part
    existing_entries = {}
    if auto_part:
        # Parse entries (simplified: look for key patterns)
        for line in auto_part.splitlines():
            # Look for: - **KEY**: ... (status: ACTIVE/RESOLVED)
            match = re.search(r'\*\*([A-Z_]+)\*\*', line)
            if match:
                key = match.group(1)
                # Extract status if present
                status_match = re.search(r'status:\s*(\w+)', line, re.IGNORECASE)
                status = status_match.group(1).upper() if status_match else "ACTIVE"
                
                # Try to extract round info
                first_seen_match = re.search(r'first_seen_round:\s*(\S+)', line)
                last_seen_match = re.search(r'last_seen_round:\s*(\S+)', line)
                seen_count_match = re.search(r'seen_count:\s*(\d+)', line)
                
                existing_entries[key] = {
                    "status": status,
                    "first_seen_round": first_seen_match.group(1) if first_seen_match else None,
                    "last_seen_round": last_seen_match.group(1) if last_seen_match else None,
                    "seen_count": int(seen_count_match.group(1)) if seen_count_match else 1
                }
    
    # Combine manual parts
    manual_content = manual_part.rstrip() + "\n" + manual_after.lstrip()
    
    return manual_content, existing_entries


def update_coverage_backlog(
    facts_summary_path: Path,
    run_dir: Path,
    registry_path: Path
) -> None:
    """Update coverage_backlog.md with 100% NaN keys."""
    backlog_path = project_root / "docs" / "verification" / "coverage_backlog.md"
    
    # Extract round number
    current_round = extract_round_from_path(run_dir)
    
    # Find 100% NaN keys
    nan_100_keys = find_100pct_nan_keys(facts_summary_path)
    if not nan_100_keys:
        print("No 100% NaN keys found.")
        return
    
    # Load registry to get seen_count
    registry = []
    if registry_path.exists():
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            pass
    
    # Count how many times each key was seen in registry
    key_seen_rounds = defaultdict(set)
    for entry in registry:
        lane = entry.get("lane", "")
        if "curated_v0" in lane or "curated" in lane.lower():
            # Extract round from current_run_dir
            run_dir_str = entry.get("current_run_dir", "")
            round_match = re.search(r'round(\d+)', run_dir_str, re.IGNORECASE)
            if round_match:
                round_num = f"round{round_match.group(1)}"
                # We can't know which keys were 100% NaN in past rounds without loading their facts_summary
                # For now, we'll just track current round
                pass
    
    # Parse existing backlog
    manual_content, existing_entries = parse_existing_backlog(backlog_path)
    
    # Update entries
    updated_entries = {}
    for key_info in nan_100_keys:
        key = key_info["key"]
        existing = existing_entries.get(key, {})
        
        if existing.get("status") == "RESOLVED":
            # Key was resolved but is now 100% NaN again - reactivate
            updated_entries[key] = {
                "status": "ACTIVE",
                "first_seen_round": existing.get("first_seen_round") or current_round,
                "last_seen_round": current_round,
                "seen_count": existing.get("seen_count", 0) + 1,
                "last_observed_n_cases": key_info["n_samples"],
                "note": key_info["note"]
            }
        else:
            # New or continuing
            updated_entries[key] = {
                "status": "ACTIVE",
                "first_seen_round": existing.get("first_seen_round") or current_round,
                "last_seen_round": current_round,
                "seen_count": existing.get("seen_count", 0) + 1,
                "last_observed_n_cases": key_info["n_samples"],
                "note": key_info["note"]
            }
    
    # Check for resolved keys (keys that were in backlog but are not 100% NaN now)
    for key, existing in existing_entries.items():
        if existing.get("status") == "ACTIVE" and key not in updated_entries:
            # Key was active but is no longer 100% NaN - mark as resolved
            updated_entries[key] = {
                "status": "RESOLVED",
                "first_seen_round": existing.get("first_seen_round", "unknown"),
                "last_seen_round": existing.get("last_seen_round", "unknown"),
                "seen_count": existing.get("seen_count", 1),
                "resolved_round": current_round,
                "note": "recovered to non-null"
            }
    
    # Generate auto-generated section
    auto_lines = ["<!-- AUTO-GENERATED:START -->", ""]
    auto_lines.append(f"*Last updated: {datetime.now().isoformat()}*")
    auto_lines.append("")
    
    if updated_entries:
        # Group by status
        active_keys = {k: v for k, v in updated_entries.items() if v.get("status") == "ACTIVE"}
        resolved_keys = {k: v for k, v in updated_entries.items() if v.get("status") == "RESOLVED"}
        
        if active_keys:
            auto_lines.append("## Active Coverage Gaps")
            auto_lines.append("")
            for key, info in sorted(active_keys.items()):
                auto_lines.append(f"- **{key}**: {info['note']}")
                auto_lines.append(f"  - first_seen_round: {info['first_seen_round']}")
                auto_lines.append(f"  - last_seen_round: {info['last_seen_round']}")
                auto_lines.append(f"  - seen_count: {info['seen_count']}")
                auto_lines.append(f"  - last_observed_n_cases: {info['last_observed_n_cases']}")
                auto_lines.append(f"  - status: ACTIVE")
                auto_lines.append("")
        
        if resolved_keys:
            auto_lines.append("## Resolved Coverage Gaps")
            auto_lines.append("")
            for key, info in sorted(resolved_keys.items()):
                auto_lines.append(f"- **{key}**: {info['note']}")
                auto_lines.append(f"  - first_seen_round: {info['first_seen_round']}")
                auto_lines.append(f"  - last_seen_round: {info['last_seen_round']}")
                auto_lines.append(f"  - resolved_round: {info.get('resolved_round', 'unknown')}")
                auto_lines.append(f"  - seen_count: {info['seen_count']}")
                auto_lines.append(f"  - status: RESOLVED")
                auto_lines.append("")
    else:
        auto_lines.append("No coverage gaps detected.")
        auto_lines.append("")
    
    auto_lines.append("<!-- AUTO-GENERATED:END -->")
    
    # Combine manual content and auto-generated section
    if not manual_content.strip():
        # Create header if file doesn't exist
        manual_content = """# Coverage Backlog

**Facts-only, no judgement, no auto-fix**

이 파일은 NaN 100% 키를 자동으로 기록합니다.
판정/추측 없이 누적만 수행합니다.

"""
    
    final_content = manual_content.rstrip() + "\n\n" + "\n".join(auto_lines)
    
    # Ensure parent directory exists
    backlog_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write updated backlog
    with open(backlog_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"Updated: {backlog_path} ({len(updated_entries)} entries)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update coverage backlog from facts_summary.json"
    )
    parser.add_argument(
        "--facts_summary",
        type=str,
        required=True,
        help="Path to facts_summary.json"
    )
    parser.add_argument(
        "--run_dir",
        type=str,
        required=True,
        help="Current run directory path"
    )
    parser.add_argument(
        "--registry_path",
        type=str,
        default="reports/validation/round_registry.json",
        help="Round registry path"
    )
    
    args = parser.parse_args()
    
    facts_summary_path = (project_root / args.facts_summary).resolve()
    run_dir = (project_root / args.run_dir).resolve()
    registry_path = project_root / args.registry_path
    
    update_coverage_backlog(facts_summary_path, run_dir, registry_path)


if __name__ == "__main__":
    main()
