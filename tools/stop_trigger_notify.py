#!/usr/bin/env python3
"""Stop Trigger Slack Notification - Unified script to handle all logic."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

# Constants
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


def generate_stop_report(event_name, ref_name, event_path, server_url, repo, run_id, head_ref, ref_name_env):
    """Generate stop_report.md."""
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
        except Exception:
            if event_name == 'pull_request':
                is_pr_event = True
    elif event_name == 'pull_request':
        is_pr_event = True
    
    branch = head_ref or ref_name_env or ref_name or 'N/A'
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else None
    
    if is_pr_event and pr_number:
        pr_url = f"{server_url}/{repo}/pull/{pr_number}"
    
    report_lines = [
        "# Stop Trigger Report",
        "",
        "## Trigger Context",
        f"- Event Type: {event_name}",
    ]
    
    if pr_number:
        report_lines.append(f"- PR Number: {pr_number}")
    
    report_lines.append(f"- Branch: {branch}")
    if run_url:
        report_lines.append(f"- Workflow Run: {run_url}")
    else:
        report_lines.append("- Workflow Run: N/A")
    
    report_lines.extend([
        "",
        "## Infra Classification",
        "- Infra Only PR: N/A (see evidence-check workflow run)",
        "",
        "## Evidence Execution",
        "- Evidence Check Executed: N/A (evidence-check workflow runs separately)",
        "- Validation Mode: N/A (see evidence-check workflow run)",
        "",
        "## Result",
        "- Final Status: success",
        "",
        "## References",
    ])
    
    if pr_url:
        report_lines.append(f"- PR URL: {pr_url}")
    if run_url:
        report_lines.append(f"- Workflow URL: {run_url}")
    
    with open('stop_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines) + '\n')
    
    return is_pr_event, pr_number, pr_url, branch, run_url


def send_slack_notification(webhook_url, triggers, is_pr_event, pr_number, pr_url, branch, run_url, repo):
    """Send Slack notification with minimal message."""
    active_triggers = get_active_triggers(triggers)
    
    if not active_triggers:
        print("No active triggers - skipping Slack notification")
        return "skipped"
    
    # Simple fallback message (no OpenAI summary for now)
    if is_pr_event and pr_number:
        text = f"[STOP] {repo} PR#{pr_number} - Active triggers: {', '.join(active_triggers)}"
    else:
        text = f"[STOP] {repo} {branch} - Active triggers: {', '.join(active_triggers)}"
    
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
    webhook_url = get_env('SLACK_WEBHOOK_URL', '')
    force_trigger_str = get_env('FORCE_TRIGGER', 'false').lower()
    audit_failed_str = get_env('AUDIT_FAILED', 'false').lower()
    
    force_trigger = force_trigger_str in ('true', '1', 'yes')
    audit_failed = audit_failed_str in ('true', '1', 'yes')
    
    # Determine triggers based on priority:
    # Priority 1: FORCE_TRIGGER=true + AUDIT_FAILED=true (workflow_dispatch smoke test)
    if force_trigger and audit_failed:
        triggers = {key: False for key in STANDARD_TRIGGERS}
        triggers["AUDIT_FAILED"] = True
        print(f"Event: {event_name} | Force mode: FORCE_TRIGGER=true, AUDIT_FAILED=true")
    # Priority 2: existing triggers.json (manual test file)
    elif Path('triggers.json').exists():
        print(f"Event: {event_name} | Using existing triggers.json")
        with open('triggers.json', 'r') as f:
            triggers = json.load(f)
        # Normalize to standard schema
        normalized = {key: False for key in STANDARD_TRIGGERS}
        for key in STANDARD_TRIGGERS:
            if key in triggers:
                normalized[key] = bool(triggers[key])
        triggers = normalized
    # Priority 3: extract from evidence files (normal PR flow)
    else:
        triggers = extract_triggers_from_files()
    
    # Save triggers.json
    with open('triggers.json', 'w') as f:
        json.dump(triggers, f, indent=2, sort_keys=True)
    
    active_triggers = get_active_triggers(triggers)
    has_triggers = len(active_triggers) > 0
    
    # Generate stop_report.md
    is_pr_event, pr_number, pr_url, branch, run_url = generate_stop_report(
        event_name, ref_name, event_path, server_url, repo, run_id, head_ref, ref_name
    )
    
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
            webhook_result = send_slack_notification(
                webhook_url, triggers, is_pr_event, pr_number, pr_url, branch, run_url, repo
            )
            if webhook_result.startswith("failed") and force_trigger:
                print(f"WARNING: FORCE_TRIGGER=true but Slack notification {webhook_result}")
    
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
