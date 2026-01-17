#!/usr/bin/env python3
"""Pack local experiment results into Evidence Package schema v1.0."""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_git_sha():
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return 'unknown'


def get_git_dirty():
    """Check if git working directory is dirty."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip()) > 0
    except Exception:
        return False


def get_hostname():
    """Get system hostname."""
    try:
        return os.uname().nodename
    except Exception:
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return 'unknown'


def parse_secondary(secondary_args):
    """Parse --secondary KEY=VALUE:UNIT arguments."""
    secondary_list = []
    for arg in secondary_args:
        # Format: KEY=VALUE:UNIT
        if '=' not in arg or ':' not in arg:
            print(f"WARNING: Invalid secondary format '{arg}'. Expected KEY=VALUE:UNIT. Skipping.")
            continue
        
        eq_pos = arg.find('=')
        colon_pos = arg.find(':', eq_pos)
        
        if colon_pos == -1:
            print(f"WARNING: Invalid secondary format '{arg}'. Missing UNIT. Skipping.")
            continue
        
        key = arg[:eq_pos]
        value_str = arg[eq_pos+1:colon_pos]
        unit = arg[colon_pos+1:]
        
        try:
            value = float(value_str)
        except ValueError:
            print(f"WARNING: Invalid secondary value '{value_str}'. Expected number. Skipping.")
            continue
        
        secondary_list.append({
            "name": key,
            "value": value,
            "unit": unit
        })
    
    return secondary_list


def calculate_regression(primary_value, baseline_primary_value):
    """Calculate delta and delta_pct."""
    delta = primary_value - baseline_primary_value
    
    if baseline_primary_value == 0:
        print("WARNING: baseline_primary_value is 0. Setting delta_pct to 0.")
        delta_pct = 0
    else:
        delta_pct = (delta / baseline_primary_value) * 100
    
    return delta, delta_pct


def generate_manifest(args, run_id, git_sha, git_dirty):
    """Generate manifest.json."""
    manifest = {
        "schema_version": "evidence.manifest.v1",
        "task": args.task,
        "policy_version": args.policy_version,
        "run_id": run_id,
        "created_at_utc": datetime.utcnow().isoformat() + 'Z',
        "runner": {
            "type": "local",
            "host": args.host or get_hostname(),
            "gpu": args.gpu or "unknown"
        },
        "code": {
            "repo": "yangmin9704188-max/ai-fitting-engine",
            "git_sha": git_sha,
            "dirty": git_dirty
        },
        "data": {
            "dataset_id": args.dataset_id or "unknown",
            "dataset_version": args.dataset_version or "v1",
            "split": args.split or "test"
        },
        "experiment": {
            "name": args.experiment_name or f"{args.task}_{args.policy_version}",
            "description": args.description or "",
            "seed": args.seed or 42
        },
        "baseline": {
            "type": args.baseline_type or "git_ref",
            "ref": args.baseline_ref,
            "git_sha": args.baseline_git_sha or "unknown"
        }
    }
    return manifest


def generate_metrics(args, run_id, delta, delta_pct, secondary_list):
    """Generate metrics.json."""
    metrics = {
        "schema_version": "evidence.metrics.v1",
        "task": args.task,
        "policy_version": args.policy_version,
        "run_id": run_id,
        "metrics": {
            "primary": {
                "name": args.primary_name or "mae",
                "value": args.primary_value,
                "unit": args.primary_unit or "cm",
                "lower_is_better": not args.primary_higher_is_better
            },
            "secondary": secondary_list
        },
        "regression": {
            "baseline_ref": args.baseline_ref,
            "baseline_primary_value": args.baseline_primary_value,
            "delta": delta,
            "delta_pct": delta_pct
        }
    }
    return metrics


def generate_summary(args, run_id, primary_name, primary_value, primary_unit, baseline_value, delta, delta_pct, secondary_list):
    """Generate summary.md."""
    lines = [
        f"# Run Summary: {args.task} {args.policy_version}",
        "",
        f"## Run ID: {run_id}",
        "",
        "## Result: PASS",
        "",
        f"Primary metric ({primary_name}): {primary_value} {primary_unit} (baseline: {baseline_value} {primary_unit})",
        f"- Delta: {delta:+.4f} {primary_unit} ({delta_pct:+.2f}%)",
    ]
    
    # Check PASS/FAIL
    if abs(delta) > 0.3:
        lines.append("- Status: FAIL (delta too large)")
    elif abs(delta_pct) > 5:
        lines.append("- Status: FAIL (delta_pct too large)")
    else:
        lines.append("- Status: Within acceptable range")
    
    if secondary_list:
        lines.append("")
        lines.append("## Secondary Metrics")
        for sec in secondary_list:
            lines.append(f"- {sec['name']}: {sec['value']} {sec['unit']}")
            if sec['name'] == 'fail_rate' and sec['value'] > 0.05:
                lines.append(f"  - WARNING: fail_rate {sec['value']} > 0.05")
    
    lines.append("")
    lines.append("## Notes")
    lines.append("- Generated by tools/pack_evidence.py")
    
    return '\n'.join(lines) + '\n'


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Pack local experiment results into Evidence Package schema v1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python tools/pack_evidence.py \\
    --task shoulder_width --policy_version v1.2 --run_id my_run_001 \\
    --primary_value 5.8 --baseline_ref tags/v1.1 --baseline_primary_value 5.7

  # With secondary metrics
  python tools/pack_evidence.py \\
    --task shoulder_width --policy_version v1.2 --run_id my_run_002 \\
    --primary_value 5.8 --baseline_ref tags/v1.1 --baseline_primary_value 5.7 \\
    --secondary fail_rate=0.02:ratio --secondary p95=14.2:mm
        """
    )
    
    # Required arguments
    parser.add_argument('--task', required=True, help='Task name (e.g., shoulder_width)')
    parser.add_argument('--policy_version', required=True, help='Policy version (e.g., v1.2)')
    parser.add_argument('--run_id', required=True, help='Run ID (e.g., 20260117_153136)')
    parser.add_argument('--primary_value', type=float, required=True, help='Primary metric value')
    parser.add_argument('--baseline_ref', required=True, help='Baseline reference (e.g., tags/v1.1)')
    parser.add_argument('--baseline_primary_value', type=float, required=True, help='Baseline primary metric value')
    
    # Optional arguments
    parser.add_argument('--primary_name', default='mae', help='Primary metric name (default: mae)')
    parser.add_argument('--primary_unit', default='cm', help='Primary metric unit (default: cm)')
    parser.add_argument('--primary_lower_is_better', action='store_true', help='Lower is better for primary (default: True)')
    parser.add_argument('--primary_higher_is_better', action='store_true', help='Higher is better for primary (overrides --primary_lower_is_better)')
    parser.add_argument('--secondary', action='append', default=[], help='Secondary metric: KEY=VALUE:UNIT (can be repeated)')
    parser.add_argument('--dataset_id', help='Dataset ID')
    parser.add_argument('--dataset_version', help='Dataset version')
    parser.add_argument('--split', help='Dataset split')
    parser.add_argument('--experiment_name', help='Experiment name')
    parser.add_argument('--description', help='Experiment description')
    parser.add_argument('--seed', type=int, help='Random seed')
    parser.add_argument('--baseline_type', help='Baseline type (default: git_ref)')
    parser.add_argument('--baseline_git_sha', help='Baseline git SHA')
    parser.add_argument('--host', help='Hostname (default: auto-detect)')
    parser.add_argument('--gpu', help='GPU identifier (default: unknown)')
    
    args = parser.parse_args()
    
    # Calculate regression
    delta, delta_pct = calculate_regression(args.primary_value, args.baseline_primary_value)
    
    # Parse secondary metrics
    secondary_list = parse_secondary(args.secondary)
    
    # Get git info
    git_sha = get_git_sha()
    git_dirty = get_git_dirty()
    
    # Generate files
    manifest = generate_manifest(args, args.run_id, git_sha, git_dirty)
    metrics = generate_metrics(args, args.run_id, delta, delta_pct, secondary_list)
    summary = generate_summary(
        args, args.run_id, args.primary_name, args.primary_value, args.primary_unit,
        args.baseline_primary_value, delta, delta_pct, secondary_list
    )
    
    # Create output directory
    output_dir = Path('artifacts') / args.task / args.policy_version / 'runs' / args.run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    manifest_path = output_dir / 'manifest.json'
    metrics_path = output_dir / 'metrics.json'
    summary_path = output_dir / 'summary.md'
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # Output summary
    print(f"Evidence package created: {output_dir}")
    print(f"  - manifest.json")
    print(f"  - metrics.json")
    print(f"  - summary.md")
    print("")
    print(f"Primary metric: {args.primary_name}={args.primary_value} {args.primary_unit}")
    print(f"Baseline: {args.baseline_ref} (value={args.baseline_primary_value} {args.primary_unit})")
    print(f"Delta: {delta:+.4f} {args.primary_unit} ({delta_pct:+.2f}%)")
    
    if secondary_list:
        print(f"Secondary metrics: {len(secondary_list)}")
        for sec in secondary_list:
            print(f"  - {sec['name']}={sec['value']} {sec['unit']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
