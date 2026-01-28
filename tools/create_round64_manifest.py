#!/usr/bin/env python3
"""
Create Round64 manifest by backfilling 100 null mesh_path entries.

Round-robin assignment across:
- verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj
- verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj
- verification/datasets/golden/s1_mesh_v0/meshes/6th_40M.obj
"""

import json
import os
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parents[1]
    input_manifest = repo_root / "verification/manifests/s1_manifest_v0_round63.json"
    output_manifest = repo_root / "verification/manifests/s1_manifest_v0_round64.json"

    # Load Round63 manifest
    with open(input_manifest, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Define proxy OBJ files (round-robin order)
    proxy_objs = [
        "verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj",
        "verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj",
        "verification/datasets/golden/s1_mesh_v0/meshes/6th_40M.obj",
    ]

    # Verify all proxy OBJ files exist
    for obj_path in proxy_objs:
        full_path = repo_root / obj_path
        if not full_path.exists():
            raise FileNotFoundError(f"Proxy OBJ file not found: {full_path}")

    print(f"[OK] All 3 proxy OBJ files verified to exist on disk")

    # Identify null mesh_path cases
    null_cases = []
    non_null_count = 0
    for case in data['cases']:
        if case['mesh_path'] is None:
            null_cases.append(case)
        else:
            non_null_count += 1

    print(f"[OK] Found {non_null_count} cases with mesh_path")
    print(f"[OK] Found {len(null_cases)} cases with null mesh_path")

    # Select first 100 null cases (deterministic, manifest order)
    cases_to_fill = null_cases[:100]
    print(f"[OK] Selecting first 100 null cases for backfill")

    # Round-robin assignment
    assignment_counts = {obj: 0 for obj in proxy_objs}
    filled_case_ids = []

    for i, case in enumerate(cases_to_fill):
        proxy_obj = proxy_objs[i % 3]
        case['mesh_path'] = proxy_obj
        case['note'] = "Round64: proxy mesh for coverage expansion (assigned to {})".format(
            os.path.basename(proxy_obj)
        )
        assignment_counts[proxy_obj] += 1
        filled_case_ids.append(case['case_id'])

    # Print assignment distribution
    print(f"\n[OK] Assignment distribution:")
    for obj, count in assignment_counts.items():
        print(f"  - {os.path.basename(obj)}: {count} cases")

    # Print example before/after
    print(f"\n[OK] Example before/after:")
    print(f"  - case_id '{filled_case_ids[0]}': null -> {proxy_objs[0]}")

    # Write Round64 manifest
    with open(output_manifest, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Created {output_manifest}")
    print(f"[OK] Total cases: {len(data['cases'])}")
    print(f"[OK] Total with mesh_path: {non_null_count + len(cases_to_fill)}")
    print(f"[OK] Total with null mesh_path: {len(null_cases) - len(cases_to_fill)}")

    # Save filled case IDs for BACKFILL_LOG
    filled_case_ids_file = repo_root / "verification/manifests/round64_filled_case_ids.txt"
    with open(filled_case_ids_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filled_case_ids))

    print(f"\n[OK] Saved filled case IDs to {filled_case_ids_file}")

if __name__ == '__main__':
    main()
