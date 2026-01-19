#!/usr/bin/env python3
"""Stop Trigger Slack Notification - Unified script to handle all logic."""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Fallback constants (used if YAML file is missing or unparseable)
STANDARD_TRIGGERS = [
    "FREEZE_REQUIRED",
    "AUDIT_FAILED",
    "SPEC_CHANGE",
    "UNEXPECTED_ERROR",
    "INSUFFICIENT_EVIDENCE",
    "RISK_HIGH"
]


def get_env(name, default=None):
    """Get environment variable."""
    return os.environ.get(name, default)


def load_trigger_policy():
    """Load trigger policy from tools/stop_triggers.yaml. Returns (triggers_dict, policy_dict)."""
    policy_path = Path('tools/stop_triggers.yaml')
    
    # Fallback: basic trigger definitions
    fallback_triggers = {key: False for key in STANDARD_TRIGGERS}
    fallback_policy = {}
    for trigger in STANDARD_TRIGGERS:
        fallback_policy[trigger] = {
            'severity': 'P1',
            'description': trigger.replace('_', ' ').title(),
            'runbook_url': '',
            'enabled': True
        }
    
    if not policy_path.exists():
        print("WARNING: tools/stop_triggers.yaml not found. Using fallback trigger definitions.")
        return fallback_triggers, fallback_policy
    
    if not YAML_AVAILABLE:
        print("WARNING: PyYAML not available. Using fallback trigger definitions.")
        return fallback_triggers, fallback_policy
    
    try:
        with open(policy_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'triggers' not in data:
            print("WARNING: Invalid YAML structure in tools/stop_triggers.yaml. Using fallback.")
            return fallback_triggers, fallback_policy
        
        triggers_dict = {key: False for key in STANDARD_TRIGGERS}
        policy_dict = {}
        
        for trigger_name, trigger_config in data['triggers'].items():
            if trigger_name in STANDARD_TRIGGERS:
                triggers_dict[trigger_name] = False
                policy_dict[trigger_name] = {
                    'severity': trigger_config.get('severity', 'P1'),
                    'description': trigger_config.get('description', trigger_name),
                    'runbook_url': trigger_config.get('runbook_url', ''),
                    'enabled': trigger_config.get('enabled', True)
                }
        
        # Fill in any missing triggers from STANDARD_TRIGGERS
        for trigger in STANDARD_TRIGGERS:
            if trigger not in policy_dict:
                policy_dict[trigger] = fallback_policy[trigger]
        
        return triggers_dict, policy_dict
    
    except Exception as e:
        print(f"WARNING: Failed to parse tools/stop_triggers.yaml: {e}. Using fallback.")
        return fallback_triggers, fallback_policy


def sort_triggers_by_severity(trigger_names, policy_dict):
    """Sort triggers by severity: P0 > P1 > P2 > P3."""
    severity_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    
    def get_severity_key(name):
        severity = policy_dict.get(name, {}).get('severity', 'P1')
        return severity_order.get(severity, 99)
    
    return sorted(trigger_names, key=get_severity_key)


def extract_triggers_from_files():
    """Extract triggers from evidence files (execution_report.md, pending_review.json, etc.)."""
    # Priority: execution_report.md > pending_review.json > v3 pack docs
    if Path('execution_report.md').exists():
        with open('execution_report.md', 'r', encoding='utf-8') as f:
            content = f.read()
        # Find "# Stop Triggers" section
        stop_triggers_match = re.search(r'# Stop Triggers\n(.*?)(?=\n# |$)', content, re.DOTALL)
        if stop_triggers_match:
            section_content = stop_triggers_match.group(1)
            # Extract JSON block
            json_match = re.search(r'```json\n(.*?)\n```', section_content, re.DOTALL)
            if json_match:
                try:
                    triggers_json = json.loads(json_match.group(1).strip())
                    triggers = {key: False for key in STANDARD_TRIGGERS}
                    for key in STANDARD_TRIGGERS:
                        if key in triggers_json:
                            triggers[key] = bool(triggers_json[key])
                    return triggers
                except Exception:
                    pass
    
    if Path('pending_review.json').exists():
        try:
            with open('pending_review.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            triggers = {key: False for key in STANDARD_TRIGGERS}
            for key in STANDARD_TRIGGERS:
                if key in data:
                    triggers[key] = bool(data[key])
            return triggers
        except Exception:
            pass
    
    # Default: all false, INSUFFICIENT_EVIDENCE=true
    triggers = {key: False for key in STANDARD_TRIGGERS}
    triggers["INSUFFICIENT_EVIDENCE"] = True
    return triggers


def get_active_triggers(triggers):
    """Get list of active (True) triggers."""
    return [key for key, value in triggers.items() if value is True]


def format_triggers_with_severity(trigger_names, policy_dict):
    """Format trigger list as 'TRIGGER(severity)'."""
    formatted = []
    for name in trigger_names:
        severity = policy_dict.get(name, {}).get('severity', 'P1')
        formatted.append(f"{name}({severity})")
    return formatted


def generate_stop_report(event_name, ref_name, event_path, server_url, repo, run_id, head_ref, ref_name_env, actor, triggers_detected, force_trigger, slack_status, policy_dict=None):
    """Generate stop_report.md as minimal evidence log (no artifact dependencies)."""
    branch = head_ref or ref_name_env or ref_name or 'N/A'
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else 'N/A'
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    if triggers_detected and policy_dict:
        triggers_list = ', '.join(format_triggers_with_severity(triggers_detected, policy_dict))
    else:
        triggers_list = ', '.join(triggers_detected) if triggers_detected else 'none'
    
    report_lines = [
        "# Stop Trigger Evidence Log",
        "",
        f"- Timestamp: {timestamp}",
        f"- Event: {event_name}",
        f"- Branch: {branch}",
        f"- Actor: {actor}",
        f"- Run URL: {run_url}",
        f"- Triggers Detected: {triggers_list}",
        f"- Force Trigger: {force_trigger}",
        f"- Slack Status: {slack_status}",
        ""
    ]
    
    with open('stop_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return branch, run_url


def send_slack_notification(webhook_url, triggers, is_pr_event, pr_number, pr_url, branch, run_url, repo, policy_dict=None):
    """Send Slack notification with minimal message."""
    active_triggers = get_active_triggers(triggers)
    
    if not active_triggers:
        print("No active triggers - skipping Slack notification")
        return "skipped"
    
    # Sort by severity and format with severity
    if policy_dict:
        sorted_triggers = sort_triggers_by_severity(active_triggers, policy_dict)
        formatted_triggers = format_triggers_with_severity(sorted_triggers, policy_dict)
        triggers_display = ', '.join(formatted_triggers)
    else:
        triggers_display = ', '.join(active_triggers)
    
    # Simple fallback message (no OpenAI summary for now)
    if is_pr_event and pr_number:
        text = f"[STOP] {repo} PR#{pr_number} - Active triggers: {triggers_display}"
    else:
        text = f"[STOP] {repo} {branch} - Active triggers: {triggers_display}"
    
    blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }]
    
    link_texts = []
    if is_pr_event and pr_url:
        link_texts.append(f"<{pr_url}|View PR>")
    if run_url:
        link_texts.append(f"<{run_url}|View Run>")
    
    # Add runbook URLs if available (max 3, priority to higher severity)
    if policy_dict:
        runbook_urls = []
        sorted_triggers = sort_triggers_by_severity(active_triggers, policy_dict)
        for trigger_name in sorted_triggers[:3]:
            url = policy_dict.get(trigger_name, {}).get('runbook_url', '')
            if url and url.strip():
                runbook_urls.append(f"<{url}|{trigger_name}>")
        
        if runbook_urls:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Runbooks: {' | '.join(runbook_urls)}"
                }
            })
    
    if link_texts:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " | ".join(link_texts)
            }
        })
    
    message = {
        "text": text,
        "blocks": blocks
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(message).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            return f"success ({response.status})"
    except Exception as e:
        return f"failed ({str(e)})"


def main():
    """Main entry point."""
    # Get GitHub context from environment
    event_name = get_env('GITHUB_EVENT_NAME', 'unknown')
    ref_name = get_env('GITHUB_REF_NAME', '')
    event_path = get_env('GITHUB_EVENT_PATH', '')
    run_id = get_env('GITHUB_RUN_ID', '')
    server_url = get_env('GITHUB_SERVER_URL', 'https://github.com')
    repo = get_env('GITHUB_REPOSITORY', 'N/A')
    head_ref = get_env('GITHUB_HEAD_REF', '')
    actor = get_env('GITHUB_ACTOR', 'unknown')
    webhook_url = get_env('SLACK_WEBHOOK_URL', '')
    force_trigger_str = get_env('FORCE_TRIGGER', 'false').lower()
    audit_failed_str = get_env('AUDIT_FAILED', 'false').lower()
    
    force_trigger = force_trigger_str in ('true', '1', 'yes')
    audit_failed = audit_failed_str in ('true', '1', 'yes')
    
    # Load trigger policy from YAML
    triggers_dict, policy_dict = load_trigger_policy()
    
    # Determine triggers based on priority:
    # Priority 1: FORCE_TRIGGER=true + AUDIT_FAILED=true (workflow_dispatch smoke test)
    if force_trigger and audit_failed:
        triggers = triggers_dict.copy()
        triggers["AUDIT_FAILED"] = True
        print(f"Event: {event_name} | Force mode: FORCE_TRIGGER=true, AUDIT_FAILED=true")
    # Priority 2: existing triggers.json (manual test file)
    elif Path('triggers.json').exists():
        print(f"Event: {event_name} | Using existing triggers.json")
        with open('triggers.json', 'r') as f:
            triggers_data = json.load(f)
        # Normalize to policy schema
        triggers = triggers_dict.copy()
        for key in STANDARD_TRIGGERS:
            if key in triggers_data:
                triggers[key] = bool(triggers_data[key])
    # Priority 3: extract from evidence files (normal PR flow)
    else:
        extracted = extract_triggers_from_files()
        # Merge with policy (use policy as base, override with extracted values)
        triggers = triggers_dict.copy()
        for key in STANDARD_TRIGGERS:
            if key in extracted:
                triggers[key] = extracted[key]
    
    # Save triggers.json
    with open('triggers.json', 'w') as f:
        json.dump(triggers, f, indent=2, sort_keys=True)
    
    active_triggers = get_active_triggers(triggers)
    has_triggers = len(active_triggers) > 0
    
    # Determine PR context for Slack notification
    is_pr_event = False
    pr_number = None
    pr_url = None
    
    if event_path and Path(event_path).exists():
        try:
            with open(event_path, 'r') as f:
                event_payload = json.load(f)
            if 'pull_request' in event_payload:
                is_pr_event = True
                pr_number = event_payload.get('pull_request', {}).get('number')
                if pr_number:
                    pr_url = f"{server_url}/{repo}/pull/{pr_number}"
        except Exception:
            if event_name == 'pull_request':
                is_pr_event = True
    elif event_name == 'pull_request':
        is_pr_event = True
    
    # Send Slack notification logic:
    # - If FORCE_TRIGGER=true: always send (even if no triggers detected)
    # - Otherwise: only send if has_triggers=true
    should_send = force_trigger or has_triggers
    
    webhook_result = "not_checked"
    if should_send:
        if not webhook_url:
            webhook_result = "webhook_not_set"
            if force_trigger:
                print("WARNING: FORCE_TRIGGER=true but SLACK_WEBHOOK_URL is not set")
        else:
            branch = head_ref or ref_name or 'N/A'
            run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else None
            webhook_result = send_slack_notification(
                webhook_url, triggers, is_pr_event, pr_number, pr_url, branch, run_url, repo, policy_dict
            )
            if webhook_result.startswith("failed") and force_trigger:
                print(f"WARNING: FORCE_TRIGGER=true but Slack notification {webhook_result}")
    
    # Sort active triggers by severity for consistent reporting
    if policy_dict:
        active_triggers = sort_triggers_by_severity(active_triggers, policy_dict)
    
    # Generate stop_report.md (minimal evidence log, no artifact dependencies)
    try:
        branch, run_url = generate_stop_report(
            event_name, ref_name, event_path, server_url, repo, run_id, head_ref, ref_name,
            actor, active_triggers, str(force_trigger), webhook_result, policy_dict
        )
        print(f"stop_report: minimal evidence log written | run_url={run_url} | triggers_detected={', '.join(active_triggers) if active_triggers else 'none'}")
    except Exception as e:
        print(f"WARNING: Failed to generate stop_report.md: {e}")
        branch = head_ref or ref_name or 'N/A'
        run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else 'N/A'
    
    # Core log output (5-7 lines)
    print(f"Event: {event_name}")
    print(f"Branch: {branch}")
    print(f"Run URL: {run_url or 'N/A'}")
    print(f"Force Trigger: {force_trigger}")
    print(f"Has Triggers: {has_triggers}")
    print(f"Webhook Result: {webhook_result}")
    
    # Exit with success code (operational stability)
    # Slack failures are logged but do not fail the job


if __name__ == '__main__':
    main()
