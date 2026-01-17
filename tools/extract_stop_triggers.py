#!/usr/bin/env python3
"""
Extract Stop Triggers - Extract and normalize stop triggers from various sources

Purpose: Extract stop triggers from execution_report.md, pending_review.json,
or v3 Execution Pack markdown files. Normalize to standard schema.

Usage:
    py tools/extract_stop_triggers.py > triggers.json
"""

from __future__ import annotations

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Bootstrap: Add project root to sys.path
_script_path = Path(__file__).resolve()
_project_root = _script_path.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# Standard stop trigger keys
STANDARD_TRIGGERS = [
    "FREEZE_REQUIRED",
    "AUDIT_FAILED",
    "SPEC_CHANGE",
    "UNEXPECTED_ERROR",
    "INSUFFICIENT_EVIDENCE",
    "RISK_HIGH",
]


def parse_markdown_stop_triggers(content: str) -> Optional[Dict[str, Any]]:
    """Parse Stop Triggers from markdown with # Stop Triggers section."""
    
    # Find "# Stop Triggers" section
    stop_triggers_match = re.search(r'# Stop Triggers\n(.*?)(?=\n# |$)', content, re.DOTALL)
    if not stop_triggers_match:
        return None
    
    section_content = stop_triggers_match.group(1)
    
    # Extract JSON block
    json_match = re.search(r'```json\n(.*?)\n```', section_content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            return None
    
    return None


def parse_json_file(content: str) -> Optional[Dict[str, Any]]:
    """Parse JSON file and extract stop trigger keys."""
    
    try:
        data = json.loads(content)
        
        # Check if it's a flat structure with trigger keys at top level
        triggers = {}
        for key in STANDARD_TRIGGERS:
            if key in data:
                value = data[key]
                # Normalize: convert to boolean if it's a dict, otherwise use value
                if isinstance(value, dict):
                    triggers[key] = True  # If dict exists, trigger is active
                elif isinstance(value, bool):
                    triggers[key] = value
                else:
                    triggers[key] = bool(value)
        
        if triggers:
            return triggers
        
        # Check nested structures (e.g., stop_triggers field)
        if "stop_triggers" in data and isinstance(data["stop_triggers"], dict):
            return data["stop_triggers"]
        
        # Check in observation or other nested paths
        if "observation" in data and isinstance(data["observation"], dict):
            obs = data["observation"]
            if "gates" in obs and isinstance(obs["gates"], dict):
                # Extract any stop trigger-like keys
                triggers = {}
                for key in STANDARD_TRIGGERS:
                    if key.lower() in {k.lower() for k in obs["gates"].keys()}:
                        # Find matching key (case-insensitive)
                        for k in obs["gates"].keys():
                            if k.upper() == key:
                                triggers[key] = bool(obs["gates"][k])
                                break
        
        if triggers:
            return triggers
        
    except json.JSONDecodeError:
        pass
    
    return None


def normalize_triggers(raw_triggers: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    """Normalize stop triggers to standard schema."""
    
    normalized = {key: False for key in STANDARD_TRIGGERS}
    
    if not raw_triggers:
        return normalized
    
    for key in STANDARD_TRIGGERS:
        # Check exact match
        if key in raw_triggers:
            value = raw_triggers[key]
            if isinstance(value, bool):
                normalized[key] = value
            elif isinstance(value, dict):
                normalized[key] = True  # Dict presence indicates active trigger
            else:
                normalized[key] = bool(value)
        # Check case-insensitive match
        else:
            for raw_key, raw_value in raw_triggers.items():
                if raw_key.upper() == key:
                    if isinstance(raw_value, bool):
                        normalized[key] = raw_value
                    elif isinstance(raw_value, dict):
                        normalized[key] = True
                    else:
                        normalized[key] = bool(raw_value)
                    break
    
    return normalized


def extract_stop_triggers() -> Dict[str, bool]:
    """Extract stop triggers from available sources in priority order."""
    
    # Priority 1: execution_report.md
    exec_report_path = _project_root / "execution_report.md"
    if exec_report_path.exists():
        try:
            content = exec_report_path.read_text(encoding="utf-8")
            triggers = parse_markdown_stop_triggers(content)
            if triggers:
                return normalize_triggers(triggers)
        except Exception:
            pass
    
    # Priority 2: pending_review.json
    pending_review_path = _project_root / "pending_review.json"
    if pending_review_path.exists():
        try:
            content = pending_review_path.read_text(encoding="utf-8")
            triggers = parse_json_file(content)
            if triggers:
                return normalize_triggers(triggers)
        except Exception:
            pass
    
    # Priority 3: v3 Execution Pack sample or any v3 pack in docs/samples/
    samples_dir = _project_root / "docs" / "samples"
    if samples_dir.exists():
        for md_file in samples_dir.glob("v3_execution_pack*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                triggers = parse_markdown_stop_triggers(content)
                if triggers:
                    return normalize_triggers(triggers)
            except Exception:
                continue
    
    # If no triggers found, set INSUFFICIENT_EVIDENCE
    # (This is not an error - evidence is missing, so we signal it)
    result = {key: False for key in STANDARD_TRIGGERS}
    result["INSUFFICIENT_EVIDENCE"] = True
    return result


def main():
    """Main entry point."""
    
    try:
        triggers = extract_stop_triggers()
        
        # Output normalized triggers as JSON to stdout
        print(json.dumps(triggers, indent=2, sort_keys=True))
        
        # Exit with 0 (success) even if INSUFFICIENT_EVIDENCE is true
        # This allows workflow to continue and decide whether to notify
        sys.exit(0)
        
    except Exception as e:
        # On fatal error, set INSUFFICIENT_EVIDENCE and exit 0
        # (Not exit 1 - we want workflow to handle this gracefully)
        result = {key: False for key in STANDARD_TRIGGERS}
        result["INSUFFICIENT_EVIDENCE"] = True
        print(json.dumps(result, indent=2, sort_keys=True), file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
