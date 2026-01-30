#!/usr/bin/env python3
"""
Build Round71 manifest: 200 unique cases
- Base: Round70 (199 unique cases)
- Add: 1 synthetic case with deterministic case_id
"""
import json
from pathlib import Path
from collections import Counter

def main():
    # Load round70 manifest (199 unique)
    round70_path = Path('verification/manifests/s1_manifest_v0_round70.json')
    with open(round70_path, 'r', encoding='utf-8') as f:
        m70 = json.load(f)

    cases_out = m70.get('cases', []).copy()
    print(f'Round70 base: {len(cases_out)} entries')

    # Verify uniqueness
    case_ids_set = set(c.get('case_id') for c in cases_out)
    print(f'Round70 unique case_ids: {len(case_ids_set)}')

    # Create synthetic 200th case
    # Use deterministic case_id: "20_F_3012_restored" (reference to the duplicate that was removed)
    # Alternative: use "SYNTH_200" for clarity
    synthetic_case_id = "SYNTH_200"

    # Canonical mesh path (per task: 6th_20M.obj first choice)
    canonical_mesh_path = "verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj"

    # Verify mesh file exists
    if not Path(canonical_mesh_path).exists():
        print(f'WARNING: Mesh file not found: {canonical_mesh_path}')
        print('Falling back to 6th_30M.obj')
        canonical_mesh_path = "verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj"

    synthetic_case = {
        "case_id": synthetic_case_id,
        "mesh_path": canonical_mesh_path
    }

    cases_out.append(synthetic_case)

    print(f'\nAdded synthetic case:')
    print(f'  case_id: {synthetic_case_id}')
    print(f'  mesh_path: {canonical_mesh_path}')

    # Build output manifest (copy structure from round70)
    manifest_out = {
        "schema_version": m70.get("schema_version", "s1_mesh_v0@1"),
        "meta_unit": m70.get("meta_unit", "m"),
        "cases": cases_out
    }

    # Validation
    total_entries = len(cases_out)
    case_ids_out = [c.get('case_id') for c in cases_out]
    unique_case_ids = len(set(case_ids_out))
    duplicate_count = len(case_ids_out) - unique_case_ids
    has_mesh_path_true = sum(1 for c in cases_out if c.get('mesh_path'))
    has_mesh_path_null = sum(1 for c in cases_out if not c.get('mesh_path'))

    print(f'\n=== VALIDATION ===')
    print(f'manifest_total_entries: {total_entries}')
    print(f'manifest_unique_case_ids: {unique_case_ids}')
    print(f'manifest_duplicate_case_id_count: {duplicate_count}')
    print(f'has_mesh_path_true: {has_mesh_path_true}')
    print(f'has_mesh_path_null: {has_mesh_path_null}')

    # Check for duplicates
    counter = Counter(case_ids_out)
    dupes = {k: v for k, v in counter.items() if v > 1}
    if dupes:
        print(f'ERROR: Duplicates found: {dupes}')
        return 1

    # Write output
    output_path = Path('verification/manifests/s1_manifest_v0_round71.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_out, f, indent=2, ensure_ascii=False)

    print(f'\nWrote: {output_path}')
    print(f'Size: {output_path.stat().st_size} bytes')

    return 0

if __name__ == '__main__':
    exit(main())
