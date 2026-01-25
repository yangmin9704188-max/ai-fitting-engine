#!/usr/bin/env python3
"""
Ops Lock Warning Sensor

금지된 경로/행동이 PR에 섞이는 것을 "경고만"으로 조기에 표면화합니다.
강제 차단(STOP) 금지. 실패로 빌드 깨지게 하지 않습니다.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Set

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


RESTRICTED_PATHS = [
    "core/",
    "pipelines/",
    "verification/",
    "tests/"
]


def get_changed_files(base_ref: str = "main") -> List[str]:
    """Get list of changed files from git diff."""
    try:
        # Try to get diff from base_ref...HEAD
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        
        # Also check staged files
        result_staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        staged_files = [f.strip() for f in result_staged.stdout.splitlines() if f.strip()]
        
        # Also check unstaged files
        result_unstaged = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        unstaged_files = [f.strip() for f in result_unstaged.stdout.splitlines() if f.strip()]
        
        # Combine and deduplicate
        all_files = set(files + staged_files + unstaged_files)
        return sorted(all_files)
    except subprocess.CalledProcessError:
        # Fallback: return empty list
        return []
    except FileNotFoundError:
        print("Warning: git not found. Cannot check changed files.", file=sys.stderr)
        return []


def check_deletions() -> List[str]:
    """Check for git rm (deletions)."""
    deleted_files = []
    
    try:
        # Check staged deletions
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=D"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        staged_deleted = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        
        # Check unstaged deletions
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=D"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root)
        )
        unstaged_deleted = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        
        deleted_files = list(set(staged_deleted + unstaged_deleted))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return deleted_files


def check_restricted_paths(changed_files: List[str]) -> List[str]:
    """Check if any changed files are in restricted paths."""
    restricted = []
    
    for file_path in changed_files:
        # Normalize path separators
        normalized = file_path.replace("\\", "/")
        
        for restricted_path in RESTRICTED_PATHS:
            if normalized.startswith(restricted_path):
                restricted.append(file_path)
                break
    
    return restricted


def main():
    parser = argparse.ArgumentParser(
        description="Check for ops-lock violations (warnings only)"
    )
    parser.add_argument(
        "--base",
        type=str,
        default="main",
        help="Base branch/ref for comparison (default: main)"
    )
    parser.add_argument(
        "--files",
        type=str,
        nargs="*",
        default=None,
        help="Explicit list of files to check (optional, overrides git diff)"
    )
    
    args = parser.parse_args()
    
    # Get changed files
    if args.files:
        changed_files = args.files
    else:
        changed_files = get_changed_files(args.base)
    
    if not changed_files:
        print("No changed files detected.")
        return 0
    
    # Check for violations
    warnings = []
    
    # Check restricted paths
    restricted = check_restricted_paths(changed_files)
    if restricted:
        warnings.append({
            "type": "restricted_path",
            "message": "WARNING: restricted path touched",
            "files": restricted
        })
    
    # Check deletions
    deleted = check_deletions()
    if deleted:
        warnings.append({
            "type": "deletion",
            "message": "WARNING: deletion detected",
            "files": deleted
        })
    
    # Print summary
    print("=" * 60)
    print("Ops Lock Warning Sensor")
    print("=" * 60)
    print(f"Changed files: {len(changed_files)}")
    print()
    
    if warnings:
        print("WARNINGS DETECTED:")
        print()
        for warning in warnings:
            print(f"  {warning['message']}")
            print(f"  Affected files ({len(warning['files'])}):")
            for f in warning['files'][:10]:  # Show first 10
                print(f"    - {f}")
            if len(warning['files']) > 10:
                print(f"    ... and {len(warning['files']) - 10} more")
            print()
        
        print("Note: These are warnings only. Build will not fail.")
        print("Please review if these changes are intentional.")
        return 0  # Exit code 0 (warning only, not error)
    else:
        print("OK: No ops-lock violations detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
