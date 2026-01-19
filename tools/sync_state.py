#!/usr/bin/env python3
"""
Sync State CLI - Patch CURRENT_STATE.md with whitelisted paths

Purpose: Apply key-value patches to docs/sync/CURRENT_STATE.md
without interpreting or validating the semantic meaning of the content.

Usage:
    python tools/sync_state.py --set snapshot.status=candidate --set last_update.trigger=ci_guard_update
    python tools/sync_state.py --file docs/sync/CURRENT_STATE.md --set pipeline.position=rd --dry-run
"""

from __future__ import annotations

import argparse
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Whitelist of allowed paths (exact match required)
ALLOWED_PATHS = {
    "snapshot.id",
    "snapshot.status",
    "snapshot.last_change",
    "snapshot.version_keys.snapshot",
    "snapshot.version_keys.semantic",
    "snapshot.version_keys.geometry_impl",
    "snapshot.version_keys.dataset",
    "pipeline.position",
    "pipeline.active_runbook",
    "signals.validation.status",
    "signals.validation.uncertainty_trend",
    "signals.cost.pure",
    "signals.cost.egress",
    "signals.cost.cost_model_version",
    "signals.latency",
    "decision.promotion",
    "decision.release",
    "decision.authority",
    "decision.artifacts.adr",
    "decision.artifacts.validation_report",
    "constraints.technical",
    "constraints.operational",
    "allowed_actions",
    "forbidden_actions",
    "last_update.date",
    "last_update.trigger",
}


def parse_value(value_str: str) -> Any:
    """
    Attempt to parse value as YAML scalar (bool, int, float, list, dict, str).
    Falls back to string if parsing fails.
    """
    try:
        # Try parsing as YAML
        parsed = yaml.safe_load(value_str)
        # If it's None and original wasn't empty, treat as string
        if parsed is None and value_str.strip() != "":
            return value_str
        return parsed
    except Exception:
        # If parsing fails, return as string
        return value_str


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set a nested value in a dictionary using dot notation path.
    Creates intermediate dictionaries if needed.
    """
    keys = path.split(".")
    current = data
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            raise ValueError(f"Path conflict: '{key}' exists but is not a dictionary")
        current = current[key]
    
    # Set the final value
    final_key = keys[-1]
    current[final_key] = value


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """
    Get a nested value from a dictionary using dot notation path.
    Returns None if path doesn't exist.
    """
    keys = path.split(".")
    current = data
    
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    
    return current


def validate_path_exists(data: Dict[str, Any], path: str) -> bool:
    """
    Check if the path structure exists in the data (parent keys exist).
    Returns True if path can be set (parent structure exists or can be created).
    """
    keys = path.split(".")
    current = data
    
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            # Parent doesn't exist, but we can create it
            return True
        if not isinstance(current[key], dict):
            # Parent exists but is not a dict - conflict
            return False
        current = current[key]
    
    return True


def apply_patches(
    data: Dict[str, Any],
    patches: List[Tuple[str, Any]],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Apply patches to data dictionary.
    Returns modified data (or original if dry_run).
    """
    result = data.copy() if not dry_run else data
    
    for path, value in patches:
        # Validate path is whitelisted
        if path not in ALLOWED_PATHS:
            print(f"Error: Path '{path}' is not in the whitelist", file=sys.stderr)
            sys.exit(1)
        
        # Validate path structure
        if not validate_path_exists(result, path):
            print(f"Error: Path conflict at '{path}' - parent key exists but is not a dictionary", file=sys.stderr)
            sys.exit(1)
        
        # Get old value for dry-run display
        old_value = get_nested_value(result, path) if dry_run else None
        
        if not dry_run:
            set_nested_value(result, path, value)
        else:
            print(f"  {path}: {old_value} -> {value}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Patch CURRENT_STATE.md with whitelisted key-value pairs"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="docs/sync/CURRENT_STATE.md",
        help="Path to CURRENT_STATE.md file (default: docs/sync/CURRENT_STATE.md)"
    )
    parser.add_argument(
        "--set",
        action="append",
        dest="patches",
        metavar="PATH=VALUE",
        help="Set a path to a value (can be used multiple times). Example: --set snapshot.status=candidate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying the file"
    )
    
    args = parser.parse_args()
    
    # Validate patches are provided
    if not args.patches:
        print("Error: At least one --set option is required", file=sys.stderr)
        sys.exit(1)
    
    # Parse patches
    patches: List[Tuple[str, Any]] = []
    for patch_str in args.patches:
        if "=" not in patch_str:
            print(f"Error: Invalid patch format '{patch_str}'. Expected PATH=VALUE", file=sys.stderr)
            sys.exit(1)
        
        path, value_str = patch_str.split("=", 1)
        path = path.strip()
        value = parse_value(value_str.strip())
        patches.append((path, value))
    
    # Load file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            data = {}
    except Exception as e:
        print(f"Error: Failed to parse YAML file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Apply patches
    if args.dry_run:
        print(f"Dry-run: Would apply {len(patches)} patch(es) to {file_path}")
        apply_patches(data, patches, dry_run=True)
    else:
        modified_data = apply_patches(data, patches, dry_run=False)
        
        # Save file
        try:
            # Use default_flow_style=False for block style, sort_keys=False to preserve order
            output = yaml.dump(
                modified_data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                encoding=None
            )
            file_path.write_text(output, encoding="utf-8")
            print(f"Applied {len(patches)} patch(es) to {file_path}")
        except Exception as e:
            print(f"Error: Failed to write file: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
