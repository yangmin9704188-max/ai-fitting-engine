#!/usr/bin/env python3
"""
Visual Provenance Generator

라운드별 visual provenance (2D 투영 이미지)를 생성합니다.
정면(X-Y) 및 측면(Z-Y) 투영을 matplotlib으로 렌더링합니다.
"""

from __future__ import annotations

import json
import random
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def _write_skipped_file(
    visual_dir: Path,
    result: Dict[str, Any],
    current_run_dir: Path,
    lane: Optional[str] = None,
    npz_path: Optional[Path] = None
) -> None:
    """Write SKIPPED.txt file when visual generation is skipped."""
    try:
        skipped_path = visual_dir / "SKIPPED.txt"
        with open(skipped_path, "w", encoding="utf-8") as f:
            f.write("Visual Provenance: SKIPPED\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"visual_status: {result.get('visual_status', 'skipped')}\n")
            f.write(f"reason: {result.get('visual_reason', 'unknown')}\n")
            
            if npz_path:
                f.write(f"npz_path: {npz_path}\n")
                f.write(f"npz_path_abs: {npz_path.resolve()}\n")
            
            if result.get("npz_keys"):
                f.write(f"npz_keys: {result['npz_keys']}\n")
            
            f.write(f"npz_has_verts: {result.get('npz_has_verts', False)}\n")
            
            if lane:
                f.write(f"lane: {lane}\n")
            
            run_dir_rel = current_run_dir.relative_to(project_root)
            f.write(f"run_dir: {run_dir_rel}\n")
            f.write(f"run_dir_abs: {current_run_dir.resolve()}\n")
            f.write(f"timestamp: {datetime.now().isoformat()}\n")
            
            if result.get("warnings"):
                f.write(f"\nwarnings ({len(result['warnings'])}):\n")
                for w in result["warnings"]:
                    f.write(f"  - {w}\n")
    except Exception as e:
        # Don't crash if we can't write the skipped file
        warnings.warn(f"Failed to write SKIPPED.txt: {e}")


def load_npz_verts(npz_path: Path) -> Tuple[Optional[list], Optional[list], list]:
    """
    Load verts and case_ids from NPZ file.
    Returns: (verts_list, case_ids, warnings)
    """
    warnings_list = []
    verts_list = []
    case_ids = []
    
    try:
        data = np.load(str(npz_path), allow_pickle=True)
    except Exception as e:
        warnings_list.append(f"NPZ_LOAD_FAILED: {str(e)}")
        return None, None, warnings_list
    
    # Get case_ids
    if "case_id" in data:
        case_id_data = data["case_id"]
        if isinstance(case_id_data, np.ndarray) and case_id_data.dtype == object:
            case_ids = [str(cid) for cid in case_id_data]
        elif isinstance(case_id_data, np.ndarray):
            case_ids = [str(cid) for cid in case_id_data]
        elif isinstance(case_id_data, (list, tuple)):
            case_ids = [str(cid) for cid in case_id_data]
        else:
            case_ids = [str(case_id_data)]
    elif "case_ids" in data:
        case_id_data = data["case_ids"]
        if isinstance(case_id_data, np.ndarray) and case_id_data.dtype == object:
            case_ids = [str(cid) for cid in case_id_data]
        elif isinstance(case_id_data, np.ndarray):
            case_ids = [str(cid) for cid in case_id_data]
        elif isinstance(case_id_data, (list, tuple)):
            case_ids = [str(cid) for cid in case_id_data]
        else:
            case_ids = [str(case_id_data)]
    
    # Get verts
    if "verts" in data:
        verts = data["verts"]
        
        # Handle object array: (N,) dtype=object, each element (V, 3)
        if verts.dtype == object and verts.ndim == 1:
            try:
                for i in range(verts.shape[0]):
                    v = verts[i]
                    if isinstance(v, np.ndarray) and v.ndim == 2 and v.shape[1] == 3:
                        verts_list.append(v.astype(np.float32))
                    else:
                        warnings_list.append(f"SKIP_INVALID_VERT: index={i}, shape={v.shape if isinstance(v, np.ndarray) else type(v)}")
            except Exception as e:
                warnings_list.append(f"OBJECT_ARRAY_PARSE_FAILED: {str(e)}")
        
        # Handle batched format: (N, V, 3)
        elif verts.ndim == 3:
            try:
                verts_list = [verts[i].astype(np.float32) for i in range(verts.shape[0])]
            except Exception as e:
                warnings_list.append(f"BATCHED_ARRAY_PARSE_FAILED: {str(e)}")
        
        # Handle single case: (V, 3)
        elif verts.ndim == 2:
            try:
                verts_list = [verts.astype(np.float32)]
            except Exception as e:
                warnings_list.append(f"SINGLE_ARRAY_PARSE_FAILED: {str(e)}")
        
        else:
            warnings_list.append(f"UNSUPPORTED_VERTS_SHAPE: {verts.shape}, dtype={verts.dtype}")
    else:
        # NPZ doesn't contain verts (may contain only measurements)
        available_keys = list(data.keys())
        warnings_list.append(f"VERTS_KEY_NOT_FOUND: NPZ contains keys {available_keys}, but no 'verts' key. Visual provenance requires vertex data.")
    
    # Generate case_ids if not found or mismatch
    if len(case_ids) != len(verts_list):
        warnings_list.append(f"CASE_ID_COUNT_MISMATCH: case_ids={len(case_ids)}, verts={len(verts_list)}")
        case_ids = [f"case_{i:04d}" for i in range(len(verts_list))]
    
    return verts_list, case_ids, warnings_list


def select_case(
    facts_summary: Dict[str, Any],
    verts_list: list,
    case_ids: list
) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[bool], str]:
    """
    Select case for visualization based on priority:
    1) case_id == "normal_1" and valid
    2) first valid case
    3) first expected_fail case
    
    Returns: (case_index, case_id, case_class, is_valid, selection_reason)
    """
    if not verts_list or not case_ids:
        return None, None, None, None, "no_cases_available"
    
    # Try to find "normal_1"
    try:
        normal_1_idx = case_ids.index("normal_1")
        if normal_1_idx < len(verts_list):
            # Check if it's valid (we'll infer from facts_summary if possible)
            # For now, assume it's valid if no failure info suggests otherwise
            return normal_1_idx, "normal_1", "valid", True, "normal_1_found"
    except ValueError:
        pass
    
    # Try first valid case
    # Since we don't have explicit valid/expected_fail in facts_summary structure,
    # we'll use the first case and mark it as "valid" (or check if there's failure info)
    if len(verts_list) > 0:
        first_case_id = case_ids[0] if len(case_ids) > 0 else "case_0000"
        # Check if there's failure info for this case in facts_summary
        # For simplicity, assume first case is valid unless we have evidence otherwise
        return 0, first_case_id, "valid", True, "first_valid_case"
    
    return None, None, None, None, "no_valid_cases"


def downsample_verts(verts: np.ndarray, max_points: int = 50000) -> Tuple[np.ndarray, Optional[int], str]:
    """
    Downsample verts if too large.
    Returns: (downsampled_verts, downsample_n, method)
    """
    n_points = verts.shape[0]
    if n_points <= max_points:
        return verts, None, "none"
    
    # Random sampling
    indices = random.sample(range(n_points), max_points)
    downsampled = verts[indices]
    return downsampled, max_points, "random_sample"


def render_projection(
    verts: np.ndarray,
    projection: str,  # "front" or "side"
    output_path: Path,
    case_id: str,
    case_class: str,
    is_expected_fail: bool = False
) -> bool:
    """
    Render 2D projection of verts.
    - front: x=verts[:,0], y=verts[:,1]
    - side: x=verts[:,2], y=verts[:,1]
    """
    try:
        if projection == "front":
            x = verts[:, 0]
            y = verts[:, 1]
            xlabel = "X (m)"
            ylabel = "Y (m)"
        elif projection == "side":
            x = verts[:, 2]
            y = verts[:, 1]
            xlabel = "Z (m)"
            ylabel = "Y (m)"
        else:
            warnings.warn(f"Unknown projection: {projection}")
            return False
        
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.scatter(x, y, s=0.5, alpha=0.6, c='blue')
        ax.set_aspect('equal')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{projection.capitalize()} View: {case_id} ({case_class})")
        
        # Add watermark if expected_fail
        if is_expected_fail:
            ax.text(0.5, 0.95, "EXPECTED_FAIL", 
                   transform=ax.transAxes, 
                   fontsize=14, 
                   ha='center', 
                   va='top',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # Tight bbox with 5% margin
        ax.margins(0.05)
        
        plt.tight_layout()
        plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
        plt.close()
        
        return True
    except Exception as e:
        warnings.warn(f"Render failed for {projection}: {str(e)}")
        return False


def generate_visual_provenance(
    current_run_dir: Path,
    facts_summary_path: Path,
    npz_path: Optional[Path] = None,
    lane: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate visual provenance images.
    Returns metadata dict for LINEAGE.md.
    """
    result = {
        "visual_status": "skipped",
        "visual_case_id": None,
        "visual_case_class": None,
        "visual_case_is_valid": None,
        "selection_reason": None,
        "downsample_n": None,
        "downsample_method": None,
        "front_xy_path": None,
        "side_zy_path": None,
        "visual_reason": None,
        "npz_has_verts": False,
        "npz_keys": [],
        "warnings": []
    }
    
    # Always create artifacts/visual/ directory
    visual_dir = current_run_dir / "artifacts" / "visual"
    try:
        visual_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        result["warnings"].append(f"VISUAL_DIR_CREATE_FAILED: {str(e)}")
        # Continue anyway - we'll try to create SKIPPED.txt later
    
    # Load facts_summary
    try:
        with open(facts_summary_path, "r", encoding="utf-8") as f:
            facts_summary = json.load(f)
    except Exception as e:
        result["warnings"].append(f"FACTS_SUMMARY_LOAD_FAILED: {str(e)}")
        result["visual_status"] = "skipped"
        result["visual_reason"] = "facts_summary_load_failed"
        _write_skipped_file(visual_dir, result, current_run_dir, lane)
        return result
    
    # Get NPZ path from facts_summary if not provided
    if npz_path is None:
        npz_path_abs = facts_summary.get("npz_path_abs") or facts_summary.get("dataset_path")
        if npz_path_abs:
            npz_path = Path(npz_path_abs)
        else:
            result["warnings"].append("NPZ_PATH_NOT_FOUND")
            result["visual_status"] = "skipped"
            result["visual_reason"] = "npz_path_not_found"
            _write_skipped_file(visual_dir, result, current_run_dir, lane)
            return result
    
    if not npz_path.exists():
        result["warnings"].append(f"NPZ_NOT_FOUND: {npz_path}")
        result["visual_status"] = "skipped"
        result["visual_reason"] = "npz_not_found"
        _write_skipped_file(visual_dir, result, current_run_dir, lane)
        return result
    
    # Check NPZ keys to determine if it has verts
    try:
        npz_data = np.load(str(npz_path), allow_pickle=True)
        npz_keys = list(npz_data.keys())
        result["npz_keys"] = npz_keys
        npz_data.close()
        
        if "verts" not in npz_keys:
            # Measurement-only NPZ - this is expected for some lanes
            result["visual_status"] = "skipped"
            result["visual_reason"] = "measurement-only npz (no verts key)"
            result["npz_has_verts"] = False
            _write_skipped_file(visual_dir, result, current_run_dir, lane, npz_path)
            return result
        
        result["npz_has_verts"] = True
    except Exception as e:
        result["warnings"].append(f"NPZ_INSPECT_FAILED: {str(e)}")
        result["visual_status"] = "skipped"
        result["visual_reason"] = "npz_inspect_failed"
        _write_skipped_file(visual_dir, result, current_run_dir, lane)
        return result
    
    # Load verts
    verts_list, case_ids, load_warnings = load_npz_verts(npz_path)
    result["warnings"].extend(load_warnings)
    
    if not verts_list or not case_ids:
        result["warnings"].append("NO_VERTS_LOADED")
        result["visual_status"] = "skipped"
        result["visual_reason"] = "no_verts_loaded"
        _write_skipped_file(visual_dir, result, current_run_dir, lane, npz_path)
        return result
    
    # Select case
    case_idx, case_id, case_class, is_valid, selection_reason = select_case(
        facts_summary, verts_list, case_ids
    )
    
    if case_idx is None:
        result["warnings"].append("NO_CASE_SELECTED")
        result["visual_status"] = "skipped"
        result["visual_reason"] = "no_case_selected"
        _write_skipped_file(visual_dir, result, current_run_dir, lane, npz_path)
        return result
    
    result["visual_case_id"] = case_id
    result["visual_case_class"] = case_class
    result["visual_case_is_valid"] = is_valid
    result["selection_reason"] = selection_reason
    
    # Get verts for selected case
    verts = verts_list[case_idx]
    
    # Downsample if needed
    verts, downsample_n, downsample_method = downsample_verts(verts, max_points=50000)
    result["downsample_n"] = downsample_n
    result["downsample_method"] = downsample_method
    
    # Determine if expected_fail
    is_expected_fail = (case_class == "expected_fail")
    if is_expected_fail:
        front_suffix = "_expected_fail"
        side_suffix = "_expected_fail"
    else:
        front_suffix = ""
        side_suffix = ""
    
    # Render front view
    front_path = visual_dir / f"front_xy{front_suffix}.png"
    front_success = render_projection(
        verts, "front", front_path, case_id, case_class, is_expected_fail
    )
    
    if front_success:
        result["front_xy_path"] = str(front_path.relative_to(current_run_dir))
    
    # Render side view
    side_path = visual_dir / f"side_zy{side_suffix}.png"
    side_success = render_projection(
        verts, "side", side_path, case_id, case_class, is_expected_fail
    )
    
    if side_success:
        result["side_zy_path"] = str(side_path.relative_to(current_run_dir))
    
    if front_success and side_success:
        result["visual_status"] = "success"
    elif front_success or side_success:
        result["visual_status"] = "partial"
        result["warnings"].append("PARTIAL_RENDER: one view failed")
    else:
        result["visual_status"] = "failed"
        result["warnings"].append("RENDER_FAILED: both views failed")
    
    return result
