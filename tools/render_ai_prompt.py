#!/usr/bin/env python3
"""
Render AI Prompt - Generate AI collaboration prompt from CURRENT_STATE.md

Purpose: Extract allowed sections from CURRENT_STATE.md and format as AI prompt.
No interpretation, judgment, or explanation logic is added.

Usage:
    python tools/render_ai_prompt.py
    python tools/render_ai_prompt.py --format json
    python tools/render_ai_prompt.py --out /tmp/prompt.txt
"""

from __future__ import annotations

import argparse
import json
import sys
import yaml
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict


# Required keys that must exist in CURRENT_STATE
REQUIRED_KEYS = {
    "snapshot",
    "pipeline",
    "signals",
    "decision",
    "constraints",
    "allowed_actions",
    "forbidden_actions",
    "last_update",
}


def load_current_state(file_path: Path) -> Dict[str, Any]:
    """Load and parse CURRENT_STATE.md YAML file."""
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
    
    # Check required keys
    missing_keys = REQUIRED_KEYS - set(data.keys())
    if missing_keys:
        print(f"Error: Missing required keys: {sorted(missing_keys)}", file=sys.stderr)
        sys.exit(1)
    
    return data


def extract_allowed_sections(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only allowed sections from CURRENT_STATE.
    Returns a dictionary with: snapshot, pipeline, signals, decision, constraints,
    allowed_actions, forbidden_actions, last_update.
    """
    return {
        "snapshot": data.get("snapshot", {}),
        "pipeline": data.get("pipeline", {}),
        "signals": data.get("signals", {}),
        "decision": data.get("decision", {}),
        "constraints": data.get("constraints", {}),
        "allowed_actions": data.get("allowed_actions", []),
        "forbidden_actions": data.get("forbidden_actions", []),
        "last_update": data.get("last_update", {}),
    }


def render_text_format(sections: Dict[str, Any]) -> str:
    """Render sections as text format prompt."""
    lines = ["AI Collaboration Prompt", ""]
    
    # CURRENT_STATE section
    lines.append("CURRENT_STATE:")
    current_state = {
        "snapshot": sections["snapshot"],
        "pipeline": sections["pipeline"],
        "signals": sections["signals"],
        "decision": sections["decision"],
        "constraints": sections["constraints"],
    }
    yaml_output = yaml.dump(
        current_state,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        encoding=None
    )
    lines.append(yaml_output.rstrip())
    lines.append("")
    
    # ALLOWED_ACTIONS section
    lines.append("ALLOWED_ACTIONS:")
    allowed_yaml = yaml.dump(
        sections["allowed_actions"],
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        encoding=None
    )
    lines.append(allowed_yaml.rstrip())
    lines.append("")
    
    # FORBIDDEN_ACTIONS section
    lines.append("FORBIDDEN_ACTIONS:")
    forbidden_yaml = yaml.dump(
        sections["forbidden_actions"],
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        encoding=None
    )
    lines.append(forbidden_yaml.rstrip())
    lines.append("")
    
    # LAST_UPDATE section (optional, but included as per requirements)
    lines.append("LAST_UPDATE:")
    last_update_yaml = yaml.dump(
        sections["last_update"],
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        encoding=None
    )
    lines.append(last_update_yaml.rstrip())
    
    return "\n".join(lines)


def json_serialize(obj: Any) -> Any:
    """Recursively serialize objects to JSON-compatible types."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serialize(item) for item in obj]
    else:
        return obj


def render_json_format(sections: Dict[str, Any]) -> str:
    """Render sections as JSON format."""
    output = {
        "current_state": {
            "snapshot": sections["snapshot"],
            "pipeline": sections["pipeline"],
            "signals": sections["signals"],
            "decision": sections["decision"],
            "constraints": sections["constraints"],
        },
        "allowed_actions": sections["allowed_actions"],
        "forbidden_actions": sections["forbidden_actions"],
        "last_update": sections["last_update"],
    }
    
    # Serialize date/datetime objects to strings
    serialized = json_serialize(output)
    
    return json.dumps(serialized, indent=2, ensure_ascii=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI collaboration prompt from CURRENT_STATE.md"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="docs/sync/CURRENT_STATE.md",
        help="Path to CURRENT_STATE.md file (default: docs/sync/CURRENT_STATE.md)"
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format: text or json (default: text)"
    )
    
    args = parser.parse_args()
    
    # Load CURRENT_STATE
    file_path = Path(args.file)
    data = load_current_state(file_path)
    
    # Extract allowed sections
    sections = extract_allowed_sections(data)
    
    # Render in requested format
    if args.format == "text":
        output = render_text_format(sections)
    else:
        output = render_json_format(sections)
    
    # Write output
    if args.out:
        output_path = Path(args.out)
        output_path.write_text(output, encoding="utf-8")
        print(f"Prompt written to: {output_path}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
