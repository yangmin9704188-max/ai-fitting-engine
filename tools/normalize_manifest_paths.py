#!/usr/bin/env python3
"""
Normalize mesh_path values in Round60 manifest for Round63.

Deterministic path normalization:
- Extract canonical base directory from existing known-good paths
- Rewrite basename-only paths to use canonical base directory
- Verify rewritten paths exist on disk
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

def find_canonical_base_dir(manifest_path: str) -> Tuple[str, str]:
    """
    Find canonical base directory from existing known-good mesh paths.

    Returns:
        Tuple of (canonical_base_dir, example_path)
    """
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Known-good mesh basenames
    target_basenames = ['6th_20M.obj', '6th_30M.obj', '6th_40M.obj']

    for case in data['cases']:
        mesh_path = case.get('mesh_path')
        if not mesh_path:
            continue

        # Check if this is a full path (contains directory separator)
        if '/' in mesh_path or '\\' in mesh_path:
            # Check if it ends with one of our target basenames
            for basename in target_basenames:
                if mesh_path.endswith(basename):
                    # Check if file exists
                    if os.path.exists(mesh_path):
                        canonical_base_dir = str(Path(mesh_path).parent)
                        print(f"Found canonical base directory from: {mesh_path}")
                        print(f"Canonical base dir: {canonical_base_dir}")
                        return canonical_base_dir, mesh_path

    raise ValueError("No known-good mesh_path found in manifest")

def normalize_manifest(
    input_path: str,
    output_path: str,
    canonical_base_dir: str
) -> Dict[str, any]:
    """
    Normalize mesh_path values in manifest.

    Returns:
        Dict with normalization statistics
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {
        'total_cases': len(data['cases']),
        'normalized_count': 0,
        'already_full_path': 0,
        'null_path': 0,
        'still_missing': [],
        'normalized_examples': []
    }

    for case in data['cases']:
        mesh_path = case.get('mesh_path')

        if mesh_path is None:
            stats['null_path'] += 1
            continue

        # Check if basename-only (no directory separator)
        if '/' not in mesh_path and '\\' not in mesh_path:
            # Normalize to canonical path
            normalized_path = str(Path(canonical_base_dir) / mesh_path)

            # Record example (first 3)
            if len(stats['normalized_examples']) < 3:
                stats['normalized_examples'].append({
                    'case_id': case['case_id'],
                    'before': mesh_path,
                    'after': normalized_path
                })

            # Update the case
            case['mesh_path'] = normalized_path
            stats['normalized_count'] += 1

            # Verify normalized path exists
            if not os.path.exists(normalized_path):
                stats['still_missing'].append({
                    'case_id': case['case_id'],
                    'path': normalized_path
                })
        else:
            stats['already_full_path'] += 1

    # Write normalized manifest
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return stats

def main():
    # Paths
    repo_root = Path(__file__).parent.parent
    input_manifest = repo_root / 'verification' / 'manifests' / 's1_manifest_v0_round60.json'
    output_manifest = repo_root / 'verification' / 'manifests' / 's1_manifest_v0_round63.json'

    print("Round63 Manifest Path Normalization")
    print("=" * 60)
    print(f"Input:  {input_manifest}")
    print(f"Output: {output_manifest}")
    print()

    # Step 1: Find canonical base directory
    print("Step 1: Finding canonical base directory...")
    canonical_base_dir, example_path = find_canonical_base_dir(str(input_manifest))
    print()

    # Step 2: Normalize manifest
    print("Step 2: Normalizing manifest paths...")
    stats = normalize_manifest(
        str(input_manifest),
        str(output_manifest),
        canonical_base_dir
    )
    print()

    # Step 3: Report
    print("Step 3: Normalization Report")
    print("=" * 60)
    print(f"Total cases:         {stats['total_cases']}")
    print(f"Already full path:   {stats['already_full_path']}")
    print(f"Normalized:          {stats['normalized_count']}")
    print(f"Null path:           {stats['null_path']}")
    print(f"Still missing:       {len(stats['still_missing'])}")
    print()

    if stats['normalized_examples']:
        print("Normalization examples:")
        for ex in stats['normalized_examples']:
            print(f"  {ex['case_id']}:")
            print(f"    Before: {ex['before']}")
            print(f"    After:  {ex['after']}")
        print()

    if stats['still_missing']:
        print(f"WARNING: {len(stats['still_missing'])} normalized paths still missing:")
        for item in stats['still_missing'][:3]:
            print(f"  {item['case_id']}: {item['path']}")
        if len(stats['still_missing']) > 3:
            print(f"  ... and {len(stats['still_missing']) - 3} more")
    else:
        print("SUCCESS: All normalized paths exist on disk")

    print()
    print(f"Output written to: {output_manifest}")

if __name__ == '__main__':
    main()
