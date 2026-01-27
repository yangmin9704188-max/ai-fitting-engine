#!/usr/bin/env python3
"""
Round60: Create manifest with 100 enabled cases (50 from Round58 + 50 new ones).
"""
import json
import sys

def main():
    # Load Round58 manifest
    round58_path = "verification/manifests/s1_manifest_v0_round58.json"
    with open(round58_path, 'r', encoding='utf-8') as f:
        round58_data = json.load(f)
    
    # Separate enabled and null cases
    enabled_cases = [c for c in round58_data['cases'] if c.get('mesh_path')]
    null_cases = [c for c in round58_data['cases'] if not c.get('mesh_path')]
    
    print(f"Round58: Enabled={len(enabled_cases)}, Nulls={len(null_cases)}, Total={len(round58_data['cases'])}")
    
    # Select first 50 null cases for Round60
    new_enabled_cases = null_cases[:50]
    remaining_null_cases = null_cases[50:]
    
    # OBJ files for round-robin assignment
    obj_files = ["6th_20M.obj", "6th_30M.obj", "6th_40M.obj"]
    
    # Assign OBJ files round-robin (balanced: 17, 17, 16)
    for i, case in enumerate(new_enabled_cases):
        obj_index = i % len(obj_files)
        case['mesh_path'] = obj_files[obj_index]
        if 'note' not in case:
            case['note'] = ""
        case['note'] = f"Round60 coverage expansion. {case['note']}".strip()
    
    # Create Round60 manifest
    round60_cases = enabled_cases + new_enabled_cases + remaining_null_cases
    
    round60_data = {
        "schema_version": round58_data['schema_version'],
        "meta_unit": round58_data['meta_unit'],
        "cases": round60_cases
    }
    
    # Verify counts
    enabled_count = len([c for c in round60_cases if c.get('mesh_path')])
    null_count = len([c for c in round60_cases if not c.get('mesh_path')])
    
    print(f"Round60: Enabled={enabled_count}, Nulls={null_count}, Total={len(round60_cases)}")
    
    # Record assignment details
    assignment_details = {}
    for i, case in enumerate(new_enabled_cases):
        obj_index = i % len(obj_files)
        assignment_details[case['case_id']] = obj_files[obj_index]
    
    # Count per OBJ
    obj_counts = {}
    for obj in obj_files:
        obj_counts[obj] = sum(1 for c in new_enabled_cases if c.get('mesh_path') == obj)
    
    print(f"New enabled case_ids (50): {[c['case_id'] for c in new_enabled_cases]}")
    print(f"OBJ assignment counts: {obj_counts}")
    
    # Save Round60 manifest
    round60_path = "verification/manifests/s1_manifest_v0_round60.json"
    with open(round60_path, 'w', encoding='utf-8') as f:
        json.dump(round60_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: {round60_path}")
    
    # Return assignment details for documentation
    return {
        'new_case_ids': [c['case_id'] for c in new_enabled_cases],
        'assignment_details': assignment_details,
        'obj_counts': obj_counts
    }

if __name__ == "__main__":
    result = main()
    # Print assignment details as JSON for easy parsing
    print("\n=== Assignment Details ===")
    print(json.dumps(result, indent=2))
