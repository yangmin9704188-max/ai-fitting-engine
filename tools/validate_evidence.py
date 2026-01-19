#!/usr/bin/env python3
"""Validate Evidence Package schema v1.0."""
import json
import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path


def get_changed_runs(base_sha, head_sha):
    """Find changed run directories from git diff."""
    import subprocess
    
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f'{base_sha}...{head_sha}'],
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        return []
    
    run_dirs = set()
    pattern = re.compile(r'artifacts/[^/]+/[^/]+/runs/([^/]+)/manifest\.json')
    
    for file in changed_files:
        if not file:
            continue
        match = pattern.match(file)
        if match:
            # Extract directory path: artifacts/task/policy_version/runs/run_id/
            parts = file.split('/')
            if len(parts) >= 5 and parts[-1] == 'manifest.json':
                run_dir = '/'.join(parts[:-1])
                run_dirs.add(run_dir)
    
    return sorted(run_dirs)


def load_json(file_path):
    """Load and parse JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load {file_path}: {e}")


def validate_manifest(manifest_path, run_id):
    """Validate manifest.json schema."""
    errors = []
    manifest = load_json(manifest_path)
    
    required_keys = [
        'schema_version', 'task', 'policy_version', 'run_id', 'created_at_utc',
        'runner', 'code', 'data', 'experiment', 'baseline'
    ]
    
    for key in required_keys:
        if key not in manifest:
            errors.append(f"Missing required key: {key}")
    
    if 'schema_version' in manifest and manifest['schema_version'] != 'evidence.manifest.v1':
        errors.append(f"Invalid schema_version: {manifest['schema_version']} (expected: evidence.manifest.v1)")
    
    if 'baseline' in manifest:
        baseline = manifest['baseline']
        if 'ref' not in baseline or not baseline['ref']:
            errors.append("baseline.ref is required and must be non-empty")
    
    return manifest, errors


def validate_metrics(metrics_path, run_id, baseline_ref):
    """Validate metrics.json schema."""
    errors = []
    metrics = load_json(metrics_path)
    
    required_keys = ['schema_version', 'task', 'policy_version', 'run_id', 'metrics', 'regression']
    
    for key in required_keys:
        if key not in metrics:
            errors.append(f"Missing required key: {key}")
    
    if 'schema_version' in metrics and metrics['schema_version'] != 'evidence.metrics.v1':
        errors.append(f"Invalid schema_version: {metrics['schema_version']} (expected: evidence.metrics.v1)")
    
    if 'metrics' in metrics and 'primary' not in metrics['metrics']:
        errors.append("metrics.primary is required")
    
    if 'regression' in metrics:
        reg = metrics['regression']
        if 'baseline_ref' not in reg or not reg['baseline_ref']:
            errors.append("regression.baseline_ref is required")
        elif reg['baseline_ref'] != baseline_ref:
            errors.append(f"regression.baseline_ref ({reg['baseline_ref']}) does not match manifest baseline.ref ({baseline_ref})")
    
    return metrics, errors


def check_pass_fail_rules(manifest, metrics):
    """Apply PASS/FAIL rules v1.0."""
    errors = []
    warnings = []
    
    if 'metrics' not in metrics or 'primary' not in metrics['metrics']:
        return False, errors, warnings
    
    primary = metrics['metrics']['primary']
    regression = metrics.get('regression', {})
    
    delta = regression.get('delta', 0)
    delta_pct = regression.get('delta_pct', 0)
    lower_is_better = primary.get('lower_is_better', True)
    
    # Rule 4: Primary metric regression
    if lower_is_better:
        if abs(delta) > 0.3:
            errors.append(f"Primary metric regression too large: abs(delta)={abs(delta)} > 0.3")
        if abs(delta_pct) > 5:
            errors.append(f"Primary metric regression too large: abs(delta_pct)={abs(delta_pct)} > 5")
    
    # Rule 5: Secondary metric fail_rate
    secondary = metrics['metrics'].get('secondary', [])
    for sec in secondary:
        if sec.get('name') == 'fail_rate':
            fail_rate_value = sec.get('value', 0)
            if fail_rate_value > 0.05:
                errors.append(f"fail_rate too high: {fail_rate_value} > 0.05")
    
    return len(errors) == 0, errors, warnings


def validate_run(run_dir):
    """Validate a single run directory."""
    run_dir_path = Path(run_dir)
    
    manifest_path = run_dir_path / 'manifest.json'
    metrics_path = run_dir_path / 'metrics.json'
    summary_path = run_dir_path / 'summary.md'
    
    # Rule 1: Check required files
    missing_files = []
    if not manifest_path.exists():
        missing_files.append('manifest.json')
    if not metrics_path.exists():
        missing_files.append('metrics.json')
    if not summary_path.exists():
        missing_files.append('summary.md')
    
    if missing_files:
        return False, None, None, None, [f"Missing required files: {', '.join(missing_files)}"]
    
    run_id = run_dir_path.name
    all_errors = []
    
    # Validate manifest.json
    manifest, manifest_errors = validate_manifest(manifest_path, run_id)
    all_errors.extend(manifest_errors)
    
    baseline_ref = None
    if 'baseline' in manifest and 'ref' in manifest['baseline']:
        baseline_ref = manifest['baseline']['ref']
    
    # Validate metrics.json
    metrics, metrics_errors = validate_metrics(metrics_path, run_id, baseline_ref)
    all_errors.extend(metrics_errors)
    
    if all_errors:
        return False, None, None, None, all_errors
    
    # Apply PASS/FAIL rules
    passed, rule_errors, warnings = check_pass_fail_rules(manifest, metrics)
    all_errors.extend(rule_errors)
    
    if all_errors:
        passed = False
    
    # Extract display info
    primary_metric = None
    delta = None
    delta_pct = None
    fail_rate = None
    
    if 'metrics' in metrics and 'primary' in metrics['metrics']:
        primary = metrics['metrics']['primary']
        primary_metric = f"{primary.get('name', 'N/A')}={primary.get('value', 'N/A')} {primary.get('unit', '')}"
    
    if 'regression' in metrics:
        reg = metrics['regression']
        delta = reg.get('delta', 0)
        delta_pct = reg.get('delta_pct', 0)
    
    if 'metrics' in metrics and 'secondary' in metrics['metrics']:
        for sec in metrics['metrics']['secondary']:
            if sec.get('name') == 'fail_rate':
                fail_rate = sec.get('value', 0)
                break
    
    errors_list = all_errors if all_errors else None
    return passed, primary_metric, delta, delta_pct, errors_list, fail_rate


def main():
    """Main entry point."""
    parser = ArgumentParser(description='Validate Evidence Package schema v1.0')
    parser.add_argument('--base', help='Base SHA for git diff (default: auto-detect)')
    parser.add_argument('--head', help='Head SHA for git diff (default: HEAD)')
    args = parser.parse_args()
    
    # Detect base and head from environment or arguments
    base_sha = args.base
    head_sha = args.head or 'HEAD'
    
    if not base_sha:
        # Try to get from environment
        pr_base = os.environ.get('GITHUB_BASE_REF')
        if pr_base:
            base_sha = f'origin/{pr_base}'
        else:
            base_sha = 'HEAD~1'
    
    # Get changed runs
    changed_runs = get_changed_runs(base_sha, head_sha)
    
    if not changed_runs:
        print("No evidence runs changed; skipping validation.")
        return 0
    
    print(f"Validating evidence runs: {len(changed_runs)}")
    print("")
    
    results = []
    for run_dir in changed_runs:
        passed, primary, delta, delta_pct, errors, fail_rate = validate_run(run_dir)
        run_id = Path(run_dir).name
        status = "PASS" if passed else "FAIL"
        
        print(f"[{status}] {run_id}")
        if primary:
            print(f"  Primary metric: {primary}")
        if delta is not None:
            print(f"  Delta: {delta:.4f} ({delta_pct:+.2f}%)")
        if fail_rate is not None:
            print(f"  Fail rate: {fail_rate:.4f}")
        if errors:
            for error in errors:
                print(f"  ERROR: {error}")
        print("")
        
        results.append((run_id, passed))
    
    # Summary
    passed_count = sum(1 for _, p in results if p)
    failed_count = len(results) - passed_count
    
    print("=" * 60)
    print(f"Summary: PASSED {passed_count} / FAILED {failed_count}")
    print("=" * 60)
    
    if failed_count > 0:
        print("\nValidation failed. Please fix the errors above.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
