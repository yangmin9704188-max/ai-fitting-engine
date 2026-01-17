#!/usr/bin/env python3
"""
Capture Session - Generate pending_review.json

Purpose: Capture current observation.md and artifacts into pending_review.json
for review and approval workflow.
"""

from __future__ import annotations

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def capture_session() -> Dict[str, Any]:
    """Capture current session data into pending_review.json."""
    
    obs_path = Path("logs/observation.md")
    if not obs_path.exists():
        raise FileNotFoundError("logs/observation.md not found")
    
    content = obs_path.read_text(encoding="utf-8")
    
    # Extract YAML frontmatter
    if "```yaml" not in content:
        raise ValueError("No YAML block found in observation.md")
    
    yaml_part = content.split("```yaml")[1].split("```")[0]
    obs_data = yaml.safe_load(yaml_part)
    
    # Extract markdown content (after YAML block)
    md_content = content.split("```")[-1].strip() if "```" in content.split("```yaml")[1] else ""
    
    # Build pending_review structure
    pending_review = {
        "timestamp": datetime.now().isoformat(),
        "observation": {
            "policy_name": obs_data.get("policy_name"),
            "version": obs_data.get("version"),
            "measurement": obs_data.get("measurement"),
            "run_id": obs_data.get("run_id"),
            "state_intent": obs_data.get("state_intent"),
            "gates": obs_data.get("gates", {}),
        },
        "artifacts": {
            "run_dir": obs_data.get("artifacts", {}).get("run_dir"),
            "verification_tool_path": obs_data.get("verification_tool_path"),
            "provenance": {
                "command": obs_data.get("provenance", {}).get("command"),
            },
        },
        "evidence": {
            "observation_md_path": str(obs_path),
            "manifest_json_path": None,
            "summary_json_path": None,
        },
    }
    
    # Add manifest.json path if available
    run_dir = obs_data.get("artifacts", {}).get("run_dir")
    if run_dir:
        manifest_path = Path(run_dir) / "manifest.json"
        if manifest_path.exists():
            pending_review["evidence"]["manifest_json_path"] = str(manifest_path)
            
            # Read manifest to get summary path
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                artifacts = manifest.get("artifacts", {})
                if "summary_json" in artifacts:
                    summary_path = Path(run_dir) / artifacts["summary_json"]
                    if summary_path.exists():
                        pending_review["evidence"]["summary_json_path"] = str(summary_path)
                
                # Copy manifest data
                pending_review["evidence"]["manifest"] = manifest
            except Exception as e:
                print(f"Warning: Could not read manifest.json: {e}")
    
    # Save pending_review.json
    output_path = Path("pending_review.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pending_review, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Captured session to {output_path}")
    print(f"  Run ID: {obs_data.get('run_id')}")
    print(f"  Artifacts: {run_dir}")
    
    return pending_review


if __name__ == "__main__":
    try:
        capture_session()
    except Exception as e:
        print(f"[FAIL] {e}")
        import sys
        sys.exit(1)
