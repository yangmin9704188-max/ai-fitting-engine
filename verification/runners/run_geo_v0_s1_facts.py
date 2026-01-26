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
import traceback

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


def load_obj_with_trimesh(path: Path) -> Optional[tuple[np.ndarray, Optional[np.ndarray], Optional[str]]]:
    """Load OBJ using trimesh (loader A, optional).
    
    Returns:
        (vertices, faces, scale_warning) or None if failed
    """
    try:
        import trimesh
        mesh = trimesh.load(str(path), process=False)
        if hasattr(mesh, 'vertices') and mesh.vertices is not None:
            verts = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.int32) if hasattr(mesh, 'faces') and mesh.faces is not None else None
            # Round33: OBJ files may be in mm/cm, but S1 manifest meta_unit="m" assumes meters
            # If OBJ is in mm, convert to m (assume > 10.0 means mm/cm scale)
            scale_warning = None
            if verts.shape[0] > 0:
                max_abs = np.abs(verts).max()
                if max_abs > 10.0:  # Likely in mm/cm, convert to m
                    verts = verts / 1000.0  # mm -> m
                    scale_warning = f"SCALE_ASSUMED_MM_TO_M (max_abs={max_abs:.2f})"
                    print(f"[OBJ/trimesh] Converted from mm to m (max_abs={max_abs:.2f})")
            return (verts, faces, scale_warning)
    except ImportError:
        return None
    except Exception:
        return None
    return None


def load_obj_with_fallback_parser(path: Path) -> Optional[tuple[np.ndarray, Optional[np.ndarray], Optional[str]]]:
    """Load OBJ using pure Python parser (loader B, required).
    
    Returns:
        (vertices, faces, scale_warning) or None if failed
    """
    try:
        vertices = []
        faces = []
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse vertex: "v x y z"
                if line.startswith('v ') and not line.startswith('vn ') and not line.startswith('vt '):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            vertices.append([x, y, z])
                        except ValueError:
                            continue
                
                # Parse face: "f a/b/c d/e/f g/h/i" or "f a d g"
                elif line.startswith('f '):
                    parts = line.split()[1:]  # Skip 'f'
                    face_indices = []
                    for part in parts:
                        # Extract vertex index (before first slash, or whole if no slash)
                        if '/' in part:
                            idx_str = part.split('/')[0]
                        else:
                            idx_str = part
                        try:
                            idx = int(idx_str) - 1  # 1-indexed -> 0-indexed
                            if idx >= 0:
                                face_indices.append(idx)
                        except ValueError:
                            continue
                    
                    if len(face_indices) >= 3:
                        faces.append(face_indices)
        
        if len(vertices) == 0:
            return None
        
        verts_array = np.array(vertices, dtype=np.float32)
        # Round33: OBJ files may be in mm/cm, but S1 manifest meta_unit="m" assumes meters
        # If OBJ is in mm, convert to m (assume > 10.0 means mm/cm scale)
        max_abs = np.abs(verts_array).max()
        scale_warning = None
        if max_abs > 10.0:  # Likely in mm/cm, convert to m
            verts_array = verts_array / 1000.0  # mm -> m
            scale_warning = f"SCALE_ASSUMED_MM_TO_M (max_abs={max_abs:.2f})"
            print(f"[OBJ/fallback] Converted from mm to m (max_abs={max_abs:.2f})")
        
        faces_array = np.array(faces, dtype=np.int32) if len(faces) > 0 else None
        
        # Return with scale warning for logging
        return (verts_array, faces_array, scale_warning)
    except Exception:
        return None


def load_verts_from_path_with_info(verts_path: str) -> Optional[tuple[np.ndarray, str, Optional[np.ndarray], Optional[str]]]:
    """Load verts from file path (NPZ or OBJ format) with loader info.
    
    For OBJ files, uses 2-stage loader:
    - Loader A: trimesh (optional)
    - Loader B: pure Python OBJ parser (required fallback)
    
    Returns:
        (verts, loader_name, faces, scale_warning) or None if failed
    """
    path = Path(verts_path)
    if not path.exists():
        return None
    
    # Resolve path (absolute or relative to cwd)
    if path.is_absolute():
        path_resolved = path.resolve()
    else:
        path_resolved = (Path.cwd() / path).resolve()
    
    if not path_resolved.exists():
        return None
    
    # Try NPZ first
    if path_resolved.suffix == ".npz":
        try:
            data = np.load(str(path_resolved), allow_pickle=True)
            if "verts" in data:
                verts = data["verts"]
                # Handle various formats
                if verts.dtype == object and verts.ndim == 1:
                    verts_result = verts[0] if len(verts) > 0 else None
                elif verts.ndim == 3:
                    verts_result = verts[0]  # (N, V, 3) -> (V, 3)
                elif verts.ndim == 2:
                    verts_result = verts  # (V, 3)
                else:
                    verts_result = None
                
                if verts_result is not None:
                    return (verts_result, "npz", None, None)
            return None
        except Exception as e:
            print(f"[WARN] Failed to load NPZ from {path_resolved}: {e}")
            return None
    
    # Try OBJ (2-stage loader)
    if path_resolved.suffix.lower() == ".obj":
        # Loader A: trimesh (optional)
        result = load_obj_with_trimesh(path_resolved)
        if result is not None:
            verts, faces, scale_warning = result
            return (verts, "trimesh", faces, scale_warning)
        
        # Loader B: pure Python OBJ parser (required fallback)
        result = load_obj_with_fallback_parser(path_resolved)
        if result is not None:
            verts, faces, scale_warning = result
            return (verts, "fallback_obj_parser", faces, scale_warning)
        
        return None
    
    return None


def load_verts_from_path(verts_path: str) -> Optional[np.ndarray]:
    """Load verts from file path (NPZ or OBJ format) - backward compatibility."""
    result = load_verts_from_path_with_info(verts_path)
    if result is not None:
        verts, _, _, _ = result
        return verts
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
    # A안: weight 값이 없으면 metadata 생성 스킵 + reason 기록
    # Weight cannot be computed from mesh - it must be provided as input.
    # Since we don't have weight input in S1 manifest, skip WEIGHT_KG metadata creation.
    # This is facts-only: we record that weight is not available, not a failure.
    
    return results


def log_skip_reason(
    skip_reasons_file: Path,
    case_id: str,
    has_mesh_path: bool,
    mesh_path: Optional[str],
    attempted_load: bool,
    stage: str,
    reason: str,
    exception_1line: Optional[str] = None,
    mesh_path_resolved: Optional[str] = None,
    mesh_exists: Optional[bool] = None,
    exception_type: Optional[str] = None,
    loader_name: Optional[str] = None,
    loaded_verts: Optional[int] = None,
    loaded_faces: Optional[int] = None
) -> None:
    """Log skip reason to JSONL file (SSoT for per-case skip reasons)."""
    record = {
        "case_id": case_id,
        "has_mesh_path": has_mesh_path,
        "mesh_path": mesh_path,
        "attempted_load": attempted_load,
        "stage": stage,
        "reason": reason,
    }
    if exception_1line:
        record["exception_1line"] = exception_1line
    if mesh_path_resolved is not None:
        record["mesh_path_resolved"] = mesh_path_resolved
    if mesh_exists is not None:
        record["mesh_exists"] = mesh_exists
    if exception_type:
        record["exception_type"] = exception_type
    if loader_name:
        record["loader_name"] = loader_name
    if loaded_verts is not None:
        record["loaded_verts"] = loaded_verts
    if loaded_faces is not None:
        record["loaded_faces"] = loaded_faces
    
    with open(skip_reasons_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def resolve_mesh_path(mesh_path: str) -> tuple[Path, bool]:
    """Resolve mesh path (absolute or relative to cwd).
    
    Returns:
        (resolved_path, exists)
    """
    if Path(mesh_path).is_absolute():
        resolved = Path(mesh_path).resolve()
    else:
        # Relative path: resolve from current working directory
        resolved = (Path.cwd() / mesh_path).resolve()
    
    return resolved, resolved.exists()


def process_case(
    case: Dict[str, Any],
    out_dir: Path,
    skipped_entries: List[Dict[str, Any]],
    skip_reasons_file: Path
) -> Optional[Dict[str, MeasurementResult]]:
    """Process a single case from S1 manifest.
    
    Returns:
        Measurement results if processed, None if skipped
    
    Invariant: Each case_id must log exactly 1 record to skip_reasons.jsonl
    """
    case_id = case["case_id"]
    mesh_path = case.get("mesh_path")
    verts_path = case.get("verts_path")
    # Round32: has_mesh_path 판정 단일화
    has_mesh_path = (mesh_path is not None) and (str(mesh_path).strip() != "")
    
    # Track if we've logged this case (invariant: exactly 1 record per case)
    logged = False
    
    # Use try/finally to ensure logging even on unexpected exceptions
    try:
    
        # Round33: Type A: manifest path is null (precheck stage)
        if mesh_path is None and verts_path is None:
            skip_reason = "manifest_path_is_null"
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=False,
                mesh_path=None,
                attempted_load=False,
                stage="precheck",
                reason=skip_reason
            )
            logged = True
            skipped_entries.append({
                "Type": "A: manifest_path_is_null",
                "case_id": case_id,
                "Reason": "S1 manifest has null path (no mesh/verts assigned)"
            })
            return None
        
        # Determine which path to use (prefer verts_path over mesh_path)
        path_to_use = verts_path if verts_path is not None else mesh_path
        
        # Resolve mesh_path for diagnostics (Round30)
        mesh_path_resolved = None
        mesh_exists = None
        mesh_path_resolved_obj = None
        if mesh_path is not None:
            mesh_path_resolved_obj, mesh_exists = resolve_mesh_path(mesh_path)
            mesh_path_resolved = str(mesh_path_resolved_obj)
        
        # Type B: manifest path set but file missing (precheck stage)
        if path_to_use is not None:
            if verts_path is not None:
                path_abs = Path(verts_path).resolve() if Path(verts_path).is_absolute() else (Path.cwd() / verts_path).resolve()
            else:
                path_abs = mesh_path_resolved_obj if mesh_path_resolved_obj else None
            
            if path_abs is None or not path_abs.exists():
                skip_reason = "file_not_found"
                log_skip_reason(
                    skip_reasons_file=skip_reasons_file,
                    case_id=case_id,
                    has_mesh_path=has_mesh_path,
                    mesh_path=mesh_path,
                    attempted_load=False,
                    stage="precheck",
                    reason=skip_reason,
                    exception_1line=f"File not found: {path_to_use}",
                    mesh_path_resolved=mesh_path_resolved,
                    mesh_exists=mesh_exists
                )
                logged = True
                skipped_entries.append({
                    "Type": "B: mesh_exists_false",
                    "case_id": case_id,
                    "path": str(path_to_use),
                    "Reason": "path specified but file not found"
                })
                return None
        
        # Resolve mesh_path for diagnostics (Round30) - ensure it's done after file check
        if mesh_path is not None and mesh_path_resolved is None:
            if Path(mesh_path).is_absolute():
                mesh_path_resolved_obj = Path(mesh_path).resolve()
            else:
                mesh_path_resolved_obj = (Path.cwd() / mesh_path).resolve()
            mesh_path_resolved = str(mesh_path_resolved_obj)
            mesh_exists = mesh_path_resolved_obj.exists()
        
        # Load verts (prefer verts_path, fallback to mesh_path) - load_mesh stage
        # Proxy 슬롯 5개는 반드시 attempted_load=True까지 진입
        verts = None
        faces = None
        load_error = None
        attempted_load = False
        exception_1line = None
        exception_type = None
        loader_name = None
        loaded_verts = None
        loaded_faces = None
        
        scale_warning = None
        if verts_path is not None:
            attempted_load = True
            try:
                result = load_verts_from_path_with_info(verts_path)
                if result is not None:
                    verts, loader_name, faces, scale_warn = result
                    loaded_verts = verts.shape[0] if verts is not None else None
                    loaded_faces = faces.shape[0] if faces is not None else None
                    if scale_warn and not scale_warning:
                        scale_warning = scale_warn
                else:
                    load_error = f"verts_path specified but load returned None: {verts_path}"
            except Exception as e:
                load_error = f"verts_path load exception: {str(e)}"
                exception_1line = str(e).splitlines()[0] if str(e).splitlines() else repr(e)
                exception_type = type(e).__name__
        
        if verts is None and mesh_path is not None:
            attempted_load = True
            try:
                result = load_verts_from_path_with_info(mesh_path)
                if result is not None:
                    verts, loader_name, faces, scale_warn = result
                    loaded_verts = verts.shape[0] if verts is not None else None
                    loaded_faces = faces.shape[0] if faces is not None else None
                    if scale_warn and not scale_warning:
                        scale_warning = scale_warn
                else:
                    if load_error:
                        load_error = f"{load_error}; mesh_path load also returned None: {mesh_path}"
                    else:
                        load_error = f"mesh_path specified but load returned None: {mesh_path}"
            except Exception as e:
                if load_error:
                    load_error = f"{load_error}; mesh_path load exception: {str(e)}"
                else:
                    load_error = f"mesh_path load exception: {str(e)}"
                if not exception_1line:
                    exception_1line = str(e).splitlines()[0] if str(e).splitlines() else repr(e)
                if not exception_type:
                    exception_type = type(e).__name__
        
        if verts is None:
            # Type B or Type C (parse error) - load_mesh stage
            skip_reason = "load_failed"
            if load_error and ("exception" in load_error.lower() or "failed" in load_error.lower()):
                skip_reason = "load_failed"
            
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=attempted_load,
                stage="load_mesh",
                reason=skip_reason,
                exception_1line=exception_1line,
                mesh_path_resolved=mesh_path_resolved,
                mesh_exists=mesh_exists,
                exception_type=exception_type,
                loader_name=loader_name,
                loaded_verts=loaded_verts,
                loaded_faces=loaded_faces
            )
            logged = True
            skipped_entries.append({
                "Type": "D: load_failed",
                "case_id": case_id,
                "path": str(path_to_use) if path_to_use else "N/A",
                "Reason": load_error if load_error else "path specified but file not found or load failed"
            })
            return None
        
        # Validate verts shape (precheck stage after load)
        if verts.ndim != 2 or verts.shape[1] != 3:
            skip_reason = "invalid_verts_shape"
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=attempted_load,
                stage="precheck",
                reason=skip_reason,
                exception_1line=f"Invalid shape: {verts.shape}, expected (V, 3)",
                mesh_path_resolved=mesh_path_resolved,
                mesh_exists=mesh_exists
            )
            logged = True
            skipped_entries.append({
                "Type": "D: load_failed",
                "case_id": case_id,
                "path": str(path_to_use) if path_to_use else "N/A",
                "Reason": f"invalid verts shape: {verts.shape}, expected (V, 3)"
            })
            return None
        
        # Process with existing geo v0 logic (measure stage)
        try:
            results = measure_all_keys(verts, case_id)
            # Round32: 성공 케이스도 로깅 (invariant: 1 record per case)
            # Round33: scale_warning을 exception_1line에 포함 (facts-only)
            exception_1line_for_log = scale_warning if scale_warning else None
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=attempted_load,
                stage="measure",
                reason="success",
                mesh_path_resolved=mesh_path_resolved,
                mesh_exists=mesh_exists,
                loader_name=loader_name,
                loaded_verts=loaded_verts,
                loaded_faces=loaded_faces,
                exception_1line=exception_1line_for_log
            )
            logged = True
            # Round33: Return results with verts and scale_warning for NPZ generation
            return {"results": results, "verts": verts, "case_id": case_id, "scale_warning": scale_warning}
        except Exception as e:
            # Record execution failure but don't skip (return empty results)
            # However, log skip reason for tracking
            exception_1line = str(e).split('\n')[0]
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=attempted_load,
                stage="measure",
                reason="measurement_exception",
                exception_1line=exception_1line,
                mesh_path_resolved=mesh_path_resolved,
                mesh_exists=mesh_exists,
                exception_type=type(e).__name__
            )
            logged = True
            print(f"[WARN] Measurement failed for {case_id}: {e}")
            return {}
    except Exception as e:
        # Round32: 예상치 못한 예외 발생 시에도 로깅 보장
        if not logged:
            exception_1line = str(e).splitlines()[0] if str(e).splitlines() else repr(e)
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=False,
                stage="unexpected_exception",
                reason="unexpected_exception",
                exception_1line=exception_1line,
                exception_type=type(e).__name__
            )
            logged = True
        raise
    finally:
        # Round32: 최종 확인 - 로깅이 누락되었는지 체크 (should not happen, but safety net)
        if not logged:
            print(f"[WARN] Case {case_id} was not logged to skip_reasons.jsonl - this should not happen!")
            log_skip_reason(
                skip_reasons_file=skip_reasons_file,
                case_id=case_id,
                has_mesh_path=has_mesh_path,
                mesh_path=mesh_path,
                attempted_load=False,
                stage="invariant_fill",
                reason="missing_log_record"
            )


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
    
    # Create artifacts directories
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    visual_dir = artifacts_dir / "visual"
    visual_dir.mkdir(parents=True, exist_ok=True)
    
    # Create skip_reasons.jsonl file (SSoT for per-case skip reasons)
    skip_reasons_file = artifacts_dir / "skip_reasons.jsonl"
    if skip_reasons_file.exists():
        skip_reasons_file.unlink()  # Clear previous run
    print(f"[SKIP REASONS] Logging to: {skip_reasons_file}")
    
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
    # Round33: Collect verts from processed cases for NPZ generation
    processed_verts: List[np.ndarray] = []
    processed_case_ids: List[str] = []
    scale_warnings: List[str] = []
    
    print(f"[PROCESS] Processing {len(cases)} cases...")
    for i, case in enumerate(cases):
        case_id = case["case_id"]
        if (i + 1) % 50 == 0:
            print(f"[PROCESS] Processed {i + 1}/{len(cases)} cases...")
        
        result_data = process_case(case, out_dir, skipped_entries, skip_reasons_file)
        if result_data is not None:
            # Round33: Handle new return format with verts
            if isinstance(result_data, dict) and "results" in result_data:
                all_results[case_id] = result_data["results"]
                if "verts" in result_data:
                    processed_verts.append(result_data["verts"])
                    processed_case_ids.append(case_id)
                    if result_data.get("scale_warning"):
                        scale_warnings.append(result_data["scale_warning"])
            else:
                # Backward compatibility: old format (just results dict)
                all_results[case_id] = result_data
    
    print(f"[PROCESS] Completed: {len(all_results)} processed, {len(skipped_entries)} skipped")
    
    # Round34: Generate verts NPZ for proxy cases (if any processed)
    npz_path = None
    npz_path_abs = None
    npz_has_verts = False
    if len(processed_verts) > 0:
        try:
            # Round34: Save verts NPZ to artifacts/visual/ (postprocess가 찾는 위치)
            verts_npz_path = visual_dir / "verts_proxy.npz"
            # Format: object array of (V, 3) arrays (각 케이스마다 다른 vertex 수 허용)
            if len(processed_verts) == 1:
                # Single case: wrap in object array
                verts_array = np.array([processed_verts[0]], dtype=object)
            else:
                # Multiple cases: use object array to handle different vertex counts
                verts_array = np.array(processed_verts, dtype=object)
            
            # Round34: Use case_id (not case_ids) for compatibility
            np.savez_compressed(
                str(verts_npz_path),
                verts=verts_array,
                case_id=np.array(processed_case_ids, dtype=object),
                meta_unit="m",
                schema_version="s1_mesh_v0@1"
            )
            # Round34: Store relative path (run_dir 기준)
            npz_path = str(verts_npz_path.relative_to(out_dir))
            npz_path_abs = str(verts_npz_path.resolve())
            npz_has_verts = True
            print(f"[NPZ] Saved verts NPZ: {verts_npz_path} ({len(processed_verts)} cases)")
            if scale_warnings:
                print(f"[NPZ] Scale warnings: {len(scale_warnings)} cases had mm->m conversion")
        except Exception as e:
            print(f"[WARN] Failed to save verts NPZ: {e}")
    
    # Write SKIPPED.txt if any skips (visual best-effort 증빙 헤더만)
    # 케이스별 상세 사유는 skip_reasons.jsonl에 기록됨 (overwrite 방지)
    if skipped_entries:
        skipped_path = visual_dir / "SKIPPED.txt"
        with open(skipped_path, 'w', encoding='utf-8') as f:
            f.write("# S1 Facts Runner Skip Records\n")
            f.write("# Per-case skip reasons are logged to artifacts/skip_reasons.jsonl\n")
            f.write(f"# Total skipped: {len(skipped_entries)}\n")
            f.write(f"# Total processed: {len(all_results)}\n\n")
        print(f"[SKIP] Wrote skip header to {skipped_path} (per-case details in {skip_reasons_file})")
    
    # Round32: Invariant check - ensure exactly 1 record per case
    manifest_case_ids = set(case["case_id"] for case in cases)
    expected_count = len(manifest_case_ids)
    
    if skip_reasons_file.exists():
        logged_case_ids = set()
        has_mesh_path_true_count = 0
        
        with open(skip_reasons_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    case_id = record.get("case_id")
                    if case_id:
                        logged_case_ids.add(case_id)
                    if record.get("has_mesh_path") is True:
                        has_mesh_path_true_count += 1
                except json.JSONDecodeError:
                    continue
        
        skip_reasons_count = len(logged_case_ids)
        
        # Check invariants
        missing_case_ids = manifest_case_ids - logged_case_ids
        
        if skip_reasons_count != expected_count or missing_case_ids:
            print(f"[WARN] Invariant violation detected:")
            print(f"  Expected records: {expected_count}, Actual: {skip_reasons_count}")
            print(f"  Missing case_ids: {len(missing_case_ids)}")
            if missing_case_ids:
                print(f"  Missing cases: {sorted(list(missing_case_ids))[:10]}...")  # Show first 10
            
            # Fill missing records
            with open(skip_reasons_file, 'a', encoding='utf-8') as f:
                for case_id in missing_case_ids:
                    # Find the case to get mesh_path info
                    case_info = next((c for c in cases if c["case_id"] == case_id), None)
                    mesh_path = case_info.get("mesh_path") if case_info else None
                    has_mesh_path = (mesh_path is not None) and (str(mesh_path).strip() != "")
                    
                    log_skip_reason(
                        skip_reasons_file=skip_reasons_file,
                        case_id=case_id,
                        has_mesh_path=has_mesh_path,
                        mesh_path=mesh_path,
                        attempted_load=False,
                        stage="invariant_fill",
                        reason="missing_log_record"
                    )
                    logged_case_ids.add(case_id)
                    if has_mesh_path:
                        has_mesh_path_true_count += 1
            
            print(f"[INVARIANT] Filled {len(missing_case_ids)} missing records")
        
        # Re-count after filling
        skip_reasons_count = len(logged_case_ids)
        
        # Check has_mesh_path_true count (expected: 5 for proxy cases)
        expected_has_mesh_path_true = 5
        if has_mesh_path_true_count != expected_has_mesh_path_true:
            print(f"[WARN] has_mesh_path_true count mismatch:")
            print(f"  Expected: {expected_has_mesh_path_true}, Actual: {has_mesh_path_true_count}")
        
        print(f"[SKIP REASONS] Logged {skip_reasons_count} skip reason records to {skip_reasons_file}")
        print(f"[SKIP REASONS] has_mesh_path=true: {has_mesh_path_true_count} (expected: {expected_has_mesh_path_true})")
        
        # Final invariant check
        if skip_reasons_count == expected_count:
            print(f"[INVARIANT] ✓ Records invariant satisfied: {skip_reasons_count} == {expected_count}")
        else:
            print(f"[WARN] Records invariant still violated: {skip_reasons_count} != {expected_count}")
    else:
        print(f"[WARN] skip_reasons.jsonl file not found after processing!")
    
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
    
    # Round34: Save facts summary with KPI fields and NPZ paths
    facts_summary = {
        "schema_version": "facts_summary_v1",
        "git_sha": get_git_sha(),
        "manifest_path": str(Path(args.manifest).resolve()),
        "total_cases": len(cases),
        "processed_cases": len(all_results),
        "skipped_cases": len(skipped_entries),
        "summary": dict(summary),
        # Round34: KPI 필드 (summarize_facts_kpi.py가 기대하는 형태)
        "n_samples": len(cases),  # total_cases와 동일
        "meta_unit": "m",
    }
    
    # Round34: summary.valid_cases 추가 (KPI가 기대하는 형태)
    if "summary" not in facts_summary:
        facts_summary["summary"] = {}
    facts_summary["summary"]["valid_cases"] = len(all_results)  # processed_cases와 동일
    
    # Round34: NPZ evidence fields (postprocess/visual_provenance가 찾는 키)
    # Round33 호환성: verts_npz_path도 포함
    if npz_path:
        facts_summary["npz_path"] = npz_path  # 상대 경로
        facts_summary["verts_npz_path"] = npz_path  # Round33 호환성
        facts_summary["dataset_path"] = npz_path  # visual_provenance.py가 찾는 키
        if npz_path_abs:
            facts_summary["npz_path_abs"] = npz_path_abs  # 절대 경로
        facts_summary["npz_has_verts"] = npz_has_verts
        facts_summary["missing_key"] = ""  # verts가 있으면 빈 문자열
    else:
        facts_summary["npz_has_verts"] = False
        facts_summary["missing_key"] = "verts"  # verts가 없으면
    
    # Round34: scale_warnings 추가 (있으면)
    if scale_warnings:
        facts_summary["scale_warnings"] = list(set(scale_warnings))  # Unique warnings
    
    facts_summary_path = out_dir / "facts_summary.json"
    with open(facts_summary_path, 'w', encoding='utf-8') as f:
        json.dump(facts_summary, f, indent=2, ensure_ascii=False)
    
    print(f"[DONE] Facts summary saved: {facts_summary_path}")
    print(f"[DONE] Processed: {len(all_results)}, Skipped: {len(skipped_entries)}")
    if npz_path:
        print(f"[DONE] NPZ path: {npz_path} (has_verts: {npz_has_verts})")


if __name__ == "__main__":
    main()
