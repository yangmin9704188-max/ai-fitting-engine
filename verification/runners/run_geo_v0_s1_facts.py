#!/usr/bin/env python3
"""
Geometric v0 S1 Facts-Only Runner (Round 23)

Purpose: Collect measurement results from S1 manifest (mesh/verts input contract).
Facts-only: records mesh/verts availability and skip reasons (Type A/B).
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.measurements.core_measurements_v0 import (
    measure_circumference_v0_with_metadata,
    measure_width_depth_v0_with_metadata,
    measure_height_v0_with_metadata,
    measure_arm_length_v0_with_metadata,
    create_weight_metadata,
    measure_waist_group_with_shared_slice,
    measure_hip_group_with_shared_slice,
    MeasurementResult,
)

# This round's keys (same as geo v0)
CIRCUMFERENCE_KEYS = [
    "NECK_CIRC_M", "BUST_CIRC_M", "UNDERBUST_CIRC_M", 
    "WAIST_CIRC_M", "HIP_CIRC_M", "THIGH_CIRC_M", "MIN_CALF_CIRC_M"
]

WIDTH_DEPTH_KEYS = [
    "CHEST_WIDTH_M", "CHEST_DEPTH_M",
    "WAIST_WIDTH_M", "WAIST_DEPTH_M",
    "HIP_WIDTH_M", "HIP_DEPTH_M"
]

HEIGHT_KEYS = ["HEIGHT_M", "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M"]

ALL_KEYS = CIRCUMFERENCE_KEYS + WIDTH_DEPTH_KEYS + HEIGHT_KEYS + ["ARM_LEN_M", "WEIGHT_KG"]


def get_git_sha() -> Optional[str]:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_s1_manifest(manifest_path: str) -> Dict[str, Any]:
    """Load S1 manifest JSON."""
    manifest_path_abs = Path(manifest_path).resolve()
    if not manifest_path_abs.exists():
        raise FileNotFoundError(f"S1 manifest not found: {manifest_path_abs}")
    
    with open(manifest_path_abs, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Validate schema
    if manifest.get("schema_version") != "s1_mesh_v0@1":
        raise ValueError(f"Invalid schema_version: {manifest.get('schema_version')}, expected 's1_mesh_v0@1'")
    
    if manifest.get("meta_unit") != "m":
        raise ValueError(f"Invalid meta_unit: {manifest.get('meta_unit')}, expected 'm'")
    
    return manifest


def load_verts_from_path(verts_path: str) -> Optional[np.ndarray]:
    """Load verts from file path (NPZ, OBJ, or other format).
    
    Returns:
        (V, 3) numpy array of vertices in meters, or None if load failed
    """
    path = Path(verts_path).resolve()
    if not path.exists():
        return None
    
    # Try NPZ first
    if path.suffix == ".npz":
        try:
            data = np.load(str(path), allow_pickle=True)
            if "verts" in data:
                verts = data["verts"]
                # Handle various formats
                if verts.dtype == object and verts.ndim == 1:
                    return verts[0] if len(verts) > 0 else None
                elif verts.ndim == 3:
                    return verts[0]  # (N, V, 3) -> (V, 3)
                elif verts.ndim == 2:
                    return verts  # (V, 3)
            return None
        except Exception as e:
            print(f"[WARN] Failed to load NPZ from {path}: {e}")
            return None
    
    # Try OBJ file (A안: OBJ 직접 로드)
    if path.suffix.lower() == ".obj":
        try:
            # Try trimesh first (if available)
            try:
                import trimesh
                mesh = trimesh.load(str(path), process=False)
                if hasattr(mesh, 'vertices') and mesh.vertices is not None:
                    verts = np.array(mesh.vertices, dtype=np.float32)
                    # OBJ files may be in mm/cm, but S1 manifest meta_unit="m" assumes meters
                    # If OBJ is in mm, convert to m (assume > 1.0 means mm/cm scale)
                    if verts.shape[0] > 0:
                        max_abs = np.abs(verts).max()
                        if max_abs > 10.0:  # Likely in mm/cm, convert to m
                            verts = verts / 1000.0  # mm -> m
                            print(f"[OBJ] Converted from mm to m (max_abs={max_abs:.2f})")
                    return verts
            except ImportError:
                # Fallback: simple OBJ parser (v lines only)
                verts = []
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('v ') and not line.startswith('vn ') and not line.startswith('vt '):
                            parts = line.split()
                            if len(parts) >= 4:
                                try:
                                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                                    verts.append([x, y, z])
                                except ValueError:
                                    continue
                
                if len(verts) > 0:
                    verts_array = np.array(verts, dtype=np.float32)
                    # OBJ files may be in mm/cm, but S1 manifest meta_unit="m" assumes meters
                    # If OBJ is in mm, convert to m (assume > 1.0 means mm/cm scale)
                    max_abs = np.abs(verts_array).max()
                    if max_abs > 10.0:  # Likely in mm/cm, convert to m
                        verts_array = verts_array / 1000.0  # mm -> m
                        print(f"[OBJ] Converted from mm to m (max_abs={max_abs:.2f})")
                    return verts_array
                return None
        except Exception as e:
            print(f"[WARN] Failed to load OBJ from {path}: {e}")
            return None
    
    # Add other formats as needed
    return None


def measure_all_keys(verts: np.ndarray, case_id: str) -> Dict[str, MeasurementResult]:
    """Measure all keys for a single case (reuse existing geo v0 logic)."""
    results = {}
    
    # WAIST group: Use shared slice (CIRC, WIDTH, DEPTH)
    try:
        waist_results = measure_waist_group_with_shared_slice(verts)
        results.update(waist_results)
    except Exception as e:
        for key in ["WAIST_CIRC_M", "WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # HIP group: Use shared slice (CIRC, WIDTH, DEPTH)
    try:
        hip_results = measure_hip_group_with_shared_slice(verts)
        results.update(hip_results)
    except Exception as e:
        for key in ["HIP_CIRC_M", "HIP_WIDTH_M", "HIP_DEPTH_M"]:
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # Circumference keys
    for key in CIRCUMFERENCE_KEYS:
        if key not in results:
            try:
                result = measure_circumference_v0_with_metadata(verts, key)
                results[key] = result
            except Exception as e:
                results[key] = MeasurementResult(
                    standard_key=key,
                    value_m=float('nan'),
                    metadata={
                        "standard_key": key,
                        "value_m": float('nan'),
                        "unit": "m",
                        "precision": 0.001,
                        "warnings": [f"EXEC_FAIL: {str(e)}"],
                        "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                    }
                )
    
    # Width/Depth keys
    for key in WIDTH_DEPTH_KEYS:
        if key not in results:
            try:
                result = measure_width_depth_v0_with_metadata(verts, key)
                results[key] = result
            except Exception as e:
                results[key] = MeasurementResult(
                    standard_key=key,
                    value_m=float('nan'),
                    metadata={
                        "standard_key": key,
                        "value_m": float('nan'),
                        "unit": "m",
                        "precision": 0.001,
                        "warnings": [f"EXEC_FAIL: {str(e)}"],
                        "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                    }
                )
    
    # Height keys
    for key in HEIGHT_KEYS:
        try:
            result = measure_height_v0_with_metadata(verts, key)
            results[key] = result
        except Exception as e:
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # ARM_LEN_M
    try:
        result = measure_arm_length_v0_with_metadata(verts)
        results["ARM_LEN_M"] = result
    except Exception as e:
        results["ARM_LEN_M"] = MeasurementResult(
            standard_key="ARM_LEN_M",
            value_m=float('nan'),
            metadata={
                "standard_key": "ARM_LEN_M",
                "value_m": float('nan'),
                "unit": "m",
                "precision": 0.001,
                "warnings": [f"EXEC_FAIL: {str(e)}"],
                "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
            }
        )
    
    # WEIGHT_KG (metadata only, no measurement)
    results["WEIGHT_KG"] = create_weight_metadata()
    
    return results


def process_case(
    case: Dict[str, Any],
    out_dir: Path,
    skipped_entries: List[Dict[str, Any]]
) -> Optional[Dict[str, MeasurementResult]]:
    """Process a single case from S1 manifest.
    
    Returns:
        Measurement results if processed, None if skipped
    """
    case_id = case["case_id"]
    mesh_path = case.get("mesh_path")
    verts_path = case.get("verts_path")
    
    # Type A: manifest path is null
    if mesh_path is None and verts_path is None:
        skipped_entries.append({
            "Type": "manifest_path_is_null",
            "case_id": case_id,
            "Reason": "S1 manifest has null path (no mesh/verts assigned)"
        })
        return None
    
    # Determine which path to use (prefer verts_path over mesh_path)
    path_to_use = verts_path if verts_path is not None else mesh_path
    
    # Type B: manifest path set but file missing
    if path_to_use is not None:
        path_abs = Path(path_to_use).resolve()
        if not path_abs.exists():
            skipped_entries.append({
                "Type": "manifest_path_set_but_file_missing",
                "case_id": case_id,
                "path": str(path_to_use),
                "Reason": "path specified but file not found"
            })
            return None
    
    # Load verts (prefer verts_path, fallback to mesh_path)
    verts = None
    load_error = None
    
    if verts_path is not None:
        try:
            verts = load_verts_from_path(verts_path)
            if verts is None:
                load_error = f"verts_path specified but load returned None: {verts_path}"
        except Exception as e:
            load_error = f"verts_path load exception: {str(e)}"
    
    if verts is None and mesh_path is not None:
        try:
            verts = load_verts_from_path(mesh_path)
            if verts is None:
                if load_error:
                    load_error = f"{load_error}; mesh_path load also returned None: {mesh_path}"
                else:
                    load_error = f"mesh_path specified but load returned None: {mesh_path}"
        except Exception as e:
            if load_error:
                load_error = f"{load_error}; mesh_path load exception: {str(e)}"
            else:
                load_error = f"mesh_path load exception: {str(e)}"
    
    if verts is None:
        # Type B or Type C (parse error)
        skip_type = "manifest_path_set_but_file_missing"
        if load_error and ("exception" in load_error.lower() or "failed" in load_error.lower()):
            skip_type = "parse_error"
        
        skipped_entries.append({
            "Type": skip_type,
            "case_id": case_id,
            "path": str(path_to_use) if path_to_use else "N/A",
            "Reason": load_error if load_error else "path specified but file not found or load failed"
        })
        return None
    
    # Validate verts shape
    if verts.ndim != 2 or verts.shape[1] != 3:
        skipped_entries.append({
            "Type": "parse_error",
            "case_id": case_id,
            "path": str(path_to_use) if path_to_use else "N/A",
            "Reason": f"invalid verts shape: {verts.shape}, expected (V, 3)"
        })
        return None
    
    # Process with existing geo v0 logic
    try:
        results = measure_all_keys(verts, case_id)
        return results
    except Exception as e:
        # Record execution failure but don't skip (return empty results)
        print(f"[WARN] Measurement failed for {case_id}: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="Geometric v0 S1 Facts-Only Runner (Round 23)"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json",
        help="S1 manifest JSON path"
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        required=True,
        help="Output directory for facts summary"
    )
    args = parser.parse_args()
    
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Create artifacts/visual directory for skip records
    visual_dir = out_dir / "artifacts" / "visual"
    visual_dir.mkdir(parents=True, exist_ok=True)
    
    # Load S1 manifest
    print(f"[S1 MANIFEST] Loading: {args.manifest}")
    manifest = load_s1_manifest(args.manifest)
    cases = manifest.get("cases", [])
    print(f"[S1 MANIFEST] Loaded {len(cases)} cases")
    print(f"[S1 MANIFEST] meta_unit: {manifest.get('meta_unit')}")
    print(f"[S1 MANIFEST] schema_version: {manifest.get('schema_version')}")
    
    # Process cases
    all_results: Dict[str, Dict[str, MeasurementResult]] = {}
    skipped_entries: List[Dict[str, Any]] = []
    
    print(f"[PROCESS] Processing {len(cases)} cases...")
    for i, case in enumerate(cases):
        case_id = case["case_id"]
        if (i + 1) % 50 == 0:
            print(f"[PROCESS] Processed {i + 1}/{len(cases)} cases...")
        
        results = process_case(case, out_dir, skipped_entries)
        if results is not None:
            all_results[case_id] = results
    
    print(f"[PROCESS] Completed: {len(all_results)} processed, {len(skipped_entries)} skipped")
    
    # Write SKIPPED.txt if any skips
    if skipped_entries:
        skipped_path = visual_dir / "SKIPPED.txt"
        with open(skipped_path, 'w', encoding='utf-8') as f:
            f.write("# S1 Facts Runner Skip Records\n\n")
            for entry in skipped_entries:
                f.write(f"Type: {entry['Type']}\n")
                f.write(f"case_id: {entry['case_id']}\n")
                if 'path' in entry:
                    f.write(f"path: {entry['path']}\n")
                f.write(f"Reason: {entry['Reason']}\n")
                f.write("\n")
        print(f"[SKIP] Wrote {len(skipped_entries)} skip records to {skipped_path}")
    
    # Generate facts summary (similar to run_geo_v0_facts_round1.py)
    summary: Dict[str, Any] = defaultdict(dict)
    
    for case_id, results in all_results.items():
        for key, result in results.items():
            if key not in summary:
                summary[key] = {
                    "total_count": 0,
                    "nan_count": 0,
                    "values": [],
                    "warnings": defaultdict(int),
                }
            
            s = summary[key]
            s["total_count"] += 1
            
            value = result.value_m
            if np.isnan(value) or not np.isfinite(value):
                s["nan_count"] += 1
            else:
                s["values"].append(float(value))
            
            # Collect warnings
            if result.metadata and "warnings" in result.metadata:
                for warning in result.metadata["warnings"]:
                    s["warnings"][warning] += 1
    
    # Compute statistics
    for key in summary:
        s = summary[key]
        s["nan_rate"] = s["nan_count"] / s["total_count"] if s["total_count"] > 0 else 0.0
        
        if s["values"]:
            s["value_stats"] = {
                "min": float(np.min(s["values"])),
                "max": float(np.max(s["values"])),
                "median": float(np.median(s["values"])),
                "mean": float(np.mean(s["values"])),
            }
        else:
            s["value_stats"] = {}
    
    # Save facts summary
    facts_summary = {
        "schema_version": "facts_summary_v1",
        "git_sha": get_git_sha(),
        "manifest_path": str(Path(args.manifest).resolve()),
        "total_cases": len(cases),
        "processed_cases": len(all_results),
        "skipped_cases": len(skipped_entries),
        "summary": dict(summary),
    }
    
    facts_summary_path = out_dir / "facts_summary.json"
    with open(facts_summary_path, 'w', encoding='utf-8') as f:
        json.dump(facts_summary, f, indent=2, ensure_ascii=False)
    
    print(f"[DONE] Facts summary saved: {facts_summary_path}")
    print(f"[DONE] Processed: {len(all_results)}, Skipped: {len(skipped_entries)}")


if __name__ == "__main__":
    main()
