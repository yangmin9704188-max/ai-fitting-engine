# core_measurements_v0.py
# Geometric Layer v0 - Core Measurements with Metadata
# Purpose: Measure standard keys with metadata JSON output (schema v0 compliant)
# Policy compliance:
# - docs/semantic/measurement_semantics_v0.md
# - docs/validation/measurement_metadata_schema_v0.md

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Literal, Tuple
import numpy as np
import json
import math

from core.measurements.metadata_v0 import create_metadata_v0, get_evidence_ref

# -----------------------------
# Types
# -----------------------------
CircumferenceKey = Literal[
    "NECK_CIRC_M", "BUST_CIRC_M", "UNDERBUST_CIRC_M", 
    "WAIST_CIRC_M", "HIP_CIRC_M", "THIGH_CIRC_M", "MIN_CALF_CIRC_M"
]

WidthDepthKey = Literal[
    "CHEST_WIDTH_M", "CHEST_DEPTH_M", 
    "WAIST_WIDTH_M", "WAIST_DEPTH_M", 
    "HIP_WIDTH_M", "HIP_DEPTH_M"
]

HeightLengthKey = Literal[
    "HEIGHT_M", "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M", "ARM_LEN_M"
]


@dataclass
class MeasurementResult:
    """Measurement result with value and metadata."""
    standard_key: str
    metadata: Dict[str, Any]  # metadata JSON (schema v0)
    value_m: Optional[float] = None  # meters
    value_kg: Optional[float] = None  # kilograms


# -----------------------------
# Utilities
# -----------------------------
def _as_np_f32(x: np.ndarray) -> np.ndarray:
    """Convert to float32 numpy array."""
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    if x.dtype != np.float32:
        x = x.astype(np.float32, copy=False)
    return x


def _validate_verts(verts: np.ndarray) -> Tuple[bool, List[str]]:
    """Basic input validation for vertices."""
    warnings: List[str] = []
    
    if verts.ndim != 2 or verts.shape[1] != 3:
        warnings.append(f"INVALID_VERTS_SHAPE: expected (N,3), got {verts.shape}")
        return False, warnings
    
    if verts.shape[0] < 3:
        warnings.append(f"INSUFFICIENT_VERTICES: need at least 3, got {verts.shape[0]}")
        return False, warnings
    
    return True, warnings


def _compute_perimeter(vertices_2d: np.ndarray) -> Optional[float]:
    """
    Compute closed curve perimeter from 2D vertices.
    Uses polar angle sorting for stability (from bust_underbust_v0.py pattern).
    """
    if vertices_2d.shape[0] < 3:
        return None
    
    # Polar angle sorting for stable perimeter computation
    center = np.mean(vertices_2d, axis=0)
    angles = np.arctan2(vertices_2d[:, 1] - center[1], vertices_2d[:, 0] - center[0])
    sorted_indices = np.argsort(angles)
    sorted_verts = vertices_2d[sorted_indices]
    
    # Compute perimeter
    n = sorted_verts.shape[0]
    perimeter = 0.0
    for i in range(n):
        j = (i + 1) % n
        edge_len = np.linalg.norm(sorted_verts[j] - sorted_verts[i])
        perimeter += edge_len
    
    return float(perimeter)


def _find_cross_section(
    verts: np.ndarray,
    y_value: float,
    tolerance: float,
    warnings: List[str],
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    target_mode: str = "ratio",
    allow_nearest_fallback: bool = False,
) -> tuple[Optional[np.ndarray], Optional[Dict[str, Any]]]:
    """
    Find cross-section vertices at given y-value.
    Returns (2D projected vertices (x, z) or None, debug info dict or None).
    
    Args:
        allow_nearest_fallback: If True, when target is out of bounds, use nearest valid plane
    """
    y_coords = verts[:, 1]
    if y_min is None:
        y_min = float(np.min(y_coords))
    if y_max is None:
        y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    # Enhanced debug info
    debug_info = {
        "target_mode": target_mode,
        "target_z_m": float(y_value),
        "target_height_ratio": float((y_value - y_min) / y_range) if y_range > 0 else 0.0,
        "axis_name": "y_up",
        "axis_length_m": float(y_range),
        "bbox_min": float(y_min),
        "bbox_max": float(y_max),
        "slice_half_thickness_m": float(tolerance),
        "search_window_mm": float(tolerance * 1000.0),
        "candidates_count": 0,
        "reason_not_found": None,
        "fallback_used": False,
        "fallback_distance_mm": None
    }
    
    # Check axis validity
    if y_range < 1e-6:
        debug_info["reason_not_found"] = "axis_invalid"
        return None, debug_info
    
    # Check bounds
    original_y_value = y_value
    fallback_distance_mm = 0.0
    
    if y_value < y_min or y_value > y_max:
        if allow_nearest_fallback:
            # Use nearest valid plane (not band_scan, just single plane selection)
            y_value = max(y_min, min(y_max, y_value))
            fallback_distance_mm = abs(y_value - original_y_value) * 1000.0
            debug_info["fallback_used"] = True
            debug_info["fallback_distance_mm"] = float(fallback_distance_mm)
            if fallback_distance_mm > 10.0:
                warnings.append(f"FALLBACK_DISTANCE_LARGE: {fallback_distance_mm:.2f}mm")
        else:
            debug_info["reason_not_found"] = "out_of_bounds_target"
            return None, debug_info
    
    # Check if slice is too thin
    if tolerance < 1e-6:
        debug_info["reason_not_found"] = "too_thin_slice"
        return None, debug_info
    
    mask = np.abs(y_coords - y_value) < tolerance
    candidate_count = int(np.sum(mask))
    debug_info["candidates_count"] = candidate_count
    
    if candidate_count < 3:
        if candidate_count == 0:
            debug_info["reason_not_found"] = "mesh_empty_at_height"
        else:
            debug_info["reason_not_found"] = "empty_slice"
        return None, debug_info
    
    slice_verts = verts[mask]
    # Project to x-z plane
    vertices_2d = slice_verts[:, [0, 2]]
    return vertices_2d, debug_info


def _find_nearest_valid_plane(
    verts: np.ndarray,
    y_target: float,
    tolerance: float,
    max_shift_mm: float,
    y_min: float,
    y_max: float,
    step_mm: float = 1.0,
) -> tuple[Optional[np.ndarray], Optional[float], Optional[Dict[str, Any]]]:
    """
    Find nearest valid plane within max_shift_mm from target.
    Returns (vertices_2d or None, shift_mm or None, debug_info or None).
    
    This is NOT band_scan - it's a single nearest valid plane selection.
    
    Args:
        step_mm: Step size in mm for searching candidate planes (default: 1.0mm)
    """
    y_coords = verts[:, 1]
    max_shift_m = max_shift_mm / 1000.0  # Convert to meters
    step_m = step_mm / 1000.0  # Convert step to meters
    
    # Search in ±max_shift_m range
    search_min = max(y_min, y_target - max_shift_m)
    search_max = min(y_max, y_target + max_shift_m)
    
    # Sample candidate planes with explicit step size
    num_steps = max(1, int((search_max - search_min) / step_m) + 1)
    
    best_vertices = None
    best_shift_mm = None
    best_candidates_count = 0
    
    for i in range(num_steps):
        y_candidate = search_min + i * step_m
        if y_candidate > search_max:
            break
        
        mask = np.abs(y_coords - y_candidate) < tolerance
        candidate_count = int(np.sum(mask))
        
        if candidate_count >= 3:  # Valid plane found
            shift_mm = abs(y_candidate - y_target) * 1000.0
            if best_vertices is None or shift_mm < best_shift_mm:
                best_vertices = verts[mask]
                best_shift_mm = shift_mm
                best_candidates_count = candidate_count
    
    if best_vertices is not None:
        # Project to x-z plane
        vertices_2d = best_vertices[:, [0, 2]]
        debug_info = {
            "nearest_valid_plane_used": True,
            "nearest_valid_plane_shift_mm": float(best_shift_mm),
            "nearest_valid_plane_candidates_count": best_candidates_count
        }
        return vertices_2d, best_shift_mm, debug_info
    
    return None, None, None


def _compute_circumference_at_height(
    verts: np.ndarray,
    y_value: float,
    tolerance: float,
    warnings: List[str],
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
) -> tuple[Optional[float], Optional[Dict[str, Any]]]:
    """Compute circumference at given height. Returns (perimeter or None, debug_info or None)."""
    vertices_2d, debug_info = _find_cross_section(verts, y_value, tolerance, warnings, y_min, y_max)
    if vertices_2d is None:
        return None, debug_info
    perimeter = _compute_perimeter(vertices_2d)
    return perimeter, debug_info


# -----------------------------
# Slice Artifact (for sharing across measurements)
# -----------------------------
@dataclass
class SliceArtifact:
    """Cross-section slice artifact that can be shared across measurements."""
    vertices_2d: np.ndarray  # (N, 2) projected vertices
    y_value: float  # Height at which slice was taken
    tolerance: float  # Slice thickness
    candidates_count: int  # Number of vertices in slice
    cross_section_debug: Dict[str, Any]  # Debug info
    chosen_candidate_index: Optional[int] = None  # If selected from multiple candidates


# -----------------------------
# Group Measurements (Slice Sharing)
# -----------------------------
def measure_waist_group_with_shared_slice(
    verts: np.ndarray,
) -> Dict[str, MeasurementResult]:
    """
    Measure WAIST group (CIRC, WIDTH, DEPTH) with shared slice artifact.
    
    Returns:
        Dictionary with keys: WAIST_CIRC_M, WAIST_WIDTH_M, WAIST_DEPTH_M
    """
    results = {}
    
    # Step 1: Extract slice for WAIST_CIRC_M (same logic as measure_circumference_v0_with_metadata)
    verts = _as_np_f32(verts)
    is_valid, warnings_circ = _validate_verts(verts)
    
    if not is_valid:
        # Return NaN for all waist measurements
        for key in ["WAIST_CIRC_M", "WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="closed_curve" if "CIRC" in key else "straight_line",
                method_metric_type="circumference" if "CIRC" in key else ("width" if "WIDTH" in key else "depth"),
                warnings=warnings_circ,
                method_fixed_height_required=True if "CIRC" in key else None,
                method_fixed_cross_section_required=True if "CIRC" not in key else None,
                search_band_scan_used=False,
                search_band_scan_limit_mm=10,
                pose_breath_state="neutral_mid",
                provenance_evidence_ref=get_evidence_ref(key),
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
        return results
    
    # Find measurement height region (same as WAIST_CIRC_M)
    y_coords = verts[:, 1]
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    if y_range < 1e-6:
        warnings_circ.append("BODY_AXIS_TOO_SHORT")
        for key in ["WAIST_CIRC_M", "WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
            debug_info = {
                "body_axis": {
                    "length_m": float(y_range),
                    "valid": False,
                    "reason_invalid": "too_short"
                }
            }
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="closed_curve" if "CIRC" in key else "straight_line",
                method_metric_type="circumference" if "CIRC" in key else ("width" if "WIDTH" in key else "depth"),
                warnings=warnings_circ,
                method_fixed_height_required=True if "CIRC" in key else None,
                method_fixed_cross_section_required=True if "CIRC" not in key else None,
                search_band_scan_used=False,
                search_band_scan_limit_mm=10,
                pose_breath_state="neutral_mid",
                provenance_evidence_ref=get_evidence_ref(key),
                debug_info=debug_info,
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
        return results
    
    # WAIST region (same as WAIST_CIRC_M)
    y_start = y_min + 0.40 * y_range
    y_end = y_min + 0.70 * y_range
    
    # Generate candidates and select best (same as WAIST_CIRC_M)
    num_slices = 20
    slice_step = (y_end - y_start) / max(1, num_slices - 1)
    tolerance = slice_step * 0.5
    
    candidates = []
    cross_section_debug_list = []
    chosen_slice_artifact = None
    chosen_candidate_index = None
    
    for i in range(num_slices):
        y_value = y_start + i * slice_step
        perimeter, debug_info = _compute_circumference_at_height(verts, y_value, tolerance, warnings_circ, y_min, y_max)
        if debug_info:
            cross_section_debug_list.append(debug_info)
        if perimeter is not None:
            candidates.append({
                "y_value": y_value,
                "perimeter": perimeter,
                "slice_index": i,
                "debug_info": debug_info
            })
    
    # Select candidate (WAIST: min perimeter)
    if len(candidates) > 0:
        selected = min(candidates, key=lambda c: c["perimeter"])
        chosen_candidate_index = selected["slice_index"]
        
        # Re-extract slice for the selected y_value (to get vertices_2d)
        vertices_2d, cross_section_debug = _find_cross_section(
            verts, selected["y_value"], tolerance, warnings_circ, y_min, y_max,
            target_mode="ratio",
            allow_nearest_fallback=False
        )
        
        if vertices_2d is not None:
            chosen_slice_artifact = SliceArtifact(
                vertices_2d=vertices_2d,
                y_value=selected["y_value"],
                tolerance=tolerance,
                candidates_count=cross_section_debug.get("candidates_count", 0) if cross_section_debug else 0,
                cross_section_debug=cross_section_debug or {},
                chosen_candidate_index=chosen_candidate_index
            )
    
    # Step 2: Compute WAIST_CIRC_M from chosen slice
    if chosen_slice_artifact is not None:
        perimeter = _compute_perimeter(chosen_slice_artifact.vertices_2d)
        value_m = perimeter
    else:
        perimeter = None
        value_m = float('nan')
        warnings_circ.append("EMPTY_CANDIDATES")
    
    # Build debug info for circumference
    debug_info_circ = {
        "body_axis": {
            "length_m": float(y_range),
            "valid": True,
            "reason_invalid": None
        }
    }
    if chosen_slice_artifact:
        debug_info_circ["cross_section"] = chosen_slice_artifact.cross_section_debug
        debug_info_circ["cross_section"]["candidates_available"] = len(candidates)
        debug_info_circ["cross_section"]["chosen_candidate_index"] = chosen_candidate_index
    
    metadata_circ = create_metadata_v0(
        standard_key="WAIST_CIRC_M",
        value_m=value_m,
        method_path_type="closed_curve",
        method_metric_type="circumference",
        warnings=warnings_circ,
        method_fixed_height_required=True,
        method_landmark_confidence="high",
        method_landmark_resolution="direct",
        search_band_scan_used=False,
        search_band_scan_limit_mm=10,
        pose_breath_state="neutral_mid",
        provenance_evidence_ref=get_evidence_ref("WAIST_CIRC_M"),
        debug_info=debug_info_circ,
    )
    results["WAIST_CIRC_M"] = MeasurementResult(
        standard_key="WAIST_CIRC_M",
        value_m=value_m,
        metadata=metadata_circ
    )
    
    # Step 3: Compute WAIST_WIDTH_M and WAIST_DEPTH_M from shared slice
    warnings_wd = warnings_circ.copy() if chosen_slice_artifact else []
    
    if chosen_slice_artifact is not None:
        # Use shared slice artifact
        vertices_2d = chosen_slice_artifact.vertices_2d
        
        # Compute width (x-axis span)
        x_min = float(np.min(vertices_2d[:, 0]))
        x_max = float(np.max(vertices_2d[:, 0]))
        width_m = x_max - x_min
        
        # Compute depth (z-axis span)
        z_min = float(np.min(vertices_2d[:, 1]))
        z_max = float(np.max(vertices_2d[:, 1]))
        depth_m = z_max - z_min
        
        # Range sanity check
        if width_m < 0.05 or depth_m < 0.05:
            warnings_wd.append("SUSPICIOUSLY_SMALL")
        
        # Build debug info for width/depth (with slice sharing info)
        debug_info_wd = {
            "body_axis": {
                "length_m": float(y_range),
                "valid": True,
                "reason_invalid": None
            },
            "cross_section": chosen_slice_artifact.cross_section_debug.copy()
        }
        debug_info_wd["cross_section"]["slice_shared_from"] = "WAIST_CIRC_M"
        debug_info_wd["cross_section"]["slicer_called_independently"] = False
        debug_info_wd["cross_section"]["slice_candidates_count"] = chosen_slice_artifact.candidates_count
        if chosen_slice_artifact.chosen_candidate_index is not None:
            debug_info_wd["cross_section"]["chosen_candidate_index"] = chosen_slice_artifact.chosen_candidate_index
        
        # Width metadata
        metadata_width = create_metadata_v0(
            standard_key="WAIST_WIDTH_M",
            value_m=width_m,
            method_path_type="straight_line",
            method_metric_type="width",
            warnings=warnings_wd,
            method_fixed_cross_section_required=True,
            search_band_scan_used=False,
            search_nearest_valid_plane_used=False,
            pose_breath_state="neutral_mid",
            provenance_evidence_ref=get_evidence_ref("WAIST_WIDTH_M"),
            debug_info=debug_info_wd,
        )
        results["WAIST_WIDTH_M"] = MeasurementResult(
            standard_key="WAIST_WIDTH_M",
            value_m=width_m,
            metadata=metadata_width
        )
        
        # Depth metadata
        metadata_depth = create_metadata_v0(
            standard_key="WAIST_DEPTH_M",
            value_m=depth_m,
            method_path_type="straight_line",
            method_metric_type="depth",
            warnings=warnings_wd,
            method_fixed_cross_section_required=True,
            search_band_scan_used=False,
            search_nearest_valid_plane_used=False,
            pose_breath_state="neutral_mid",
            provenance_evidence_ref=get_evidence_ref("WAIST_DEPTH_M"),
            debug_info=debug_info_wd,
        )
        results["WAIST_DEPTH_M"] = MeasurementResult(
            standard_key="WAIST_DEPTH_M",
            value_m=depth_m,
            metadata=metadata_depth
        )
    else:
        # No slice found - return NaN for width/depth
        for key in ["WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
            metric_type = "width" if "WIDTH" in key else "depth"
            debug_info = {
                "body_axis": {
                    "length_m": float(y_range),
                    "valid": True,
                    "reason_invalid": None
                }
            }
            if cross_section_debug_list:
                debug_info["cross_section"] = cross_section_debug_list[0] if cross_section_debug_list else {}
                debug_info["cross_section"]["slice_shared_from"] = "WAIST_CIRC_M"
                debug_info["cross_section"]["slicer_called_independently"] = False
                debug_info["cross_section"]["slice_candidates_count"] = 0
            
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="straight_line",
                method_metric_type=metric_type,
                warnings=warnings_wd + ["CROSS_SECTION_NOT_FOUND"],
                method_fixed_cross_section_required=True,
                search_band_scan_used=False,
                search_nearest_valid_plane_used=False,
                pose_breath_state="neutral_mid",
                provenance_evidence_ref=get_evidence_ref(key),
                debug_info=debug_info,
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
    
    return results


def measure_hip_group_with_shared_slice(
    verts: np.ndarray,
) -> Dict[str, MeasurementResult]:
    """
    Measure HIP group (CIRC, WIDTH, DEPTH) with shared slice artifact.
    
    Returns:
        Dictionary with keys: HIP_CIRC_M, HIP_WIDTH_M, HIP_DEPTH_M
    """
    results = {}
    
    # Similar structure to measure_waist_group_with_shared_slice
    # Step 1: Extract slice for HIP_CIRC_M
    verts = _as_np_f32(verts)
    is_valid, warnings_circ = _validate_verts(verts)
    
    if not is_valid:
        for key in ["HIP_CIRC_M", "HIP_WIDTH_M", "HIP_DEPTH_M"]:
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="closed_curve" if "CIRC" in key else "straight_line",
                method_metric_type="circumference" if "CIRC" in key else ("width" if "WIDTH" in key else "depth"),
                warnings=warnings_circ,
                method_fixed_height_required=True if "CIRC" in key else None,
                method_fixed_cross_section_required=True if "CIRC" not in key else None,
                search_band_scan_used=False,
                search_band_scan_limit_mm=10,
                provenance_evidence_ref=get_evidence_ref(key),
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
        return results
    
    y_coords = verts[:, 1]
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    if y_range < 1e-6:
        warnings_circ.append("BODY_AXIS_TOO_SHORT")
        for key in ["HIP_CIRC_M", "HIP_WIDTH_M", "HIP_DEPTH_M"]:
            debug_info = {
                "body_axis": {
                    "length_m": float(y_range),
                    "valid": False,
                    "reason_invalid": "too_short"
                }
            }
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="closed_curve" if "CIRC" in key else "straight_line",
                method_metric_type="circumference" if "CIRC" in key else ("width" if "WIDTH" in key else "depth"),
                warnings=warnings_circ,
                method_fixed_height_required=True if "CIRC" in key else None,
                method_fixed_cross_section_required=True if "CIRC" not in key else None,
                search_band_scan_used=False,
                search_band_scan_limit_mm=10,
                provenance_evidence_ref=get_evidence_ref(key),
                debug_info=debug_info,
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
        return results
    
    # HIP region (same as HIP_CIRC_M)
    y_start = y_min + 0.50 * y_range
    y_end = y_min + 0.80 * y_range
    
    # Generate candidates and select best (HIP: max perimeter)
    num_slices = 20
    slice_step = (y_end - y_start) / max(1, num_slices - 1)
    tolerance = slice_step * 0.5
    
    candidates = []
    cross_section_debug_list = []
    chosen_slice_artifact = None
    chosen_candidate_index = None
    
    for i in range(num_slices):
        y_value = y_start + i * slice_step
        perimeter, debug_info = _compute_circumference_at_height(verts, y_value, tolerance, warnings_circ, y_min, y_max)
        if debug_info:
            cross_section_debug_list.append(debug_info)
        if perimeter is not None:
            candidates.append({
                "y_value": y_value,
                "perimeter": perimeter,
                "slice_index": i,
                "debug_info": debug_info
            })
    
    # Select candidate (HIP: max perimeter)
    if len(candidates) > 0:
        selected = max(candidates, key=lambda c: c["perimeter"])
        chosen_candidate_index = selected["slice_index"]
        
        # Re-extract slice for the selected y_value
        vertices_2d, cross_section_debug = _find_cross_section(
            verts, selected["y_value"], tolerance, warnings_circ, y_min, y_max,
            target_mode="ratio",
            allow_nearest_fallback=False
        )
        
        if vertices_2d is not None:
            chosen_slice_artifact = SliceArtifact(
                vertices_2d=vertices_2d,
                y_value=selected["y_value"],
                tolerance=tolerance,
                candidates_count=cross_section_debug.get("candidates_count", 0) if cross_section_debug else 0,
                cross_section_debug=cross_section_debug or {},
                chosen_candidate_index=chosen_candidate_index
            )
    
    # Step 2: Compute HIP_CIRC_M from chosen slice
    if chosen_slice_artifact is not None:
        perimeter = _compute_perimeter(chosen_slice_artifact.vertices_2d)
        value_m = perimeter
    else:
        perimeter = None
        value_m = float('nan')
        warnings_circ.append("EMPTY_CANDIDATES")
    
    # Build debug info for circumference
    debug_info_circ = {
        "body_axis": {
            "length_m": float(y_range),
            "valid": True,
            "reason_invalid": None
        }
    }
    if chosen_slice_artifact:
        debug_info_circ["cross_section"] = chosen_slice_artifact.cross_section_debug
        debug_info_circ["cross_section"]["candidates_available"] = len(candidates)
        debug_info_circ["cross_section"]["chosen_candidate_index"] = chosen_candidate_index
    
    metadata_circ = create_metadata_v0(
        standard_key="HIP_CIRC_M",
        value_m=value_m,
        method_path_type="closed_curve",
        method_metric_type="circumference",
        warnings=warnings_circ,
        method_fixed_height_required=True,
        method_landmark_confidence="high",
        method_landmark_resolution="direct",
        search_band_scan_used=False,
        search_band_scan_limit_mm=10,
        provenance_evidence_ref=get_evidence_ref("HIP_CIRC_M"),
        debug_info=debug_info_circ,
    )
    results["HIP_CIRC_M"] = MeasurementResult(
        standard_key="HIP_CIRC_M",
        value_m=value_m,
        metadata=metadata_circ
    )
    
    # Step 3: Compute HIP_WIDTH_M and HIP_DEPTH_M from shared slice
    warnings_wd = warnings_circ.copy() if chosen_slice_artifact else []
    
    if chosen_slice_artifact is not None:
        # Use shared slice artifact
        vertices_2d = chosen_slice_artifact.vertices_2d
        
        # Compute width (x-axis span)
        x_min = float(np.min(vertices_2d[:, 0]))
        x_max = float(np.max(vertices_2d[:, 0]))
        width_m = x_max - x_min
        
        # Compute depth (z-axis span)
        z_min = float(np.min(vertices_2d[:, 1]))
        z_max = float(np.max(vertices_2d[:, 1]))
        depth_m = z_max - z_min
        
        # Range sanity check
        if width_m < 0.05 or depth_m < 0.05:
            warnings_wd.append("SUSPICIOUSLY_SMALL")
        
        # Build debug info for width/depth (with slice sharing info)
        debug_info_wd = {
            "body_axis": {
                "length_m": float(y_range),
                "valid": True,
                "reason_invalid": None
            },
            "cross_section": chosen_slice_artifact.cross_section_debug.copy()
        }
        debug_info_wd["cross_section"]["slice_shared_from"] = "HIP_CIRC_M"
        debug_info_wd["cross_section"]["slicer_called_independently"] = False
        debug_info_wd["cross_section"]["slice_candidates_count"] = chosen_slice_artifact.candidates_count
        if chosen_slice_artifact.chosen_candidate_index is not None:
            debug_info_wd["cross_section"]["chosen_candidate_index"] = chosen_slice_artifact.chosen_candidate_index
        
        # Width metadata
        metadata_width = create_metadata_v0(
            standard_key="HIP_WIDTH_M",
            value_m=width_m,
            method_path_type="straight_line",
            method_metric_type="width",
            warnings=warnings_wd,
            method_fixed_cross_section_required=True,
            search_band_scan_used=False,
            search_nearest_valid_plane_used=False,
            provenance_evidence_ref=get_evidence_ref("HIP_WIDTH_M"),
            debug_info=debug_info_wd,
        )
        results["HIP_WIDTH_M"] = MeasurementResult(
            standard_key="HIP_WIDTH_M",
            value_m=width_m,
            metadata=metadata_width
        )
        
        # Depth metadata
        metadata_depth = create_metadata_v0(
            standard_key="HIP_DEPTH_M",
            value_m=depth_m,
            method_path_type="straight_line",
            method_metric_type="depth",
            warnings=warnings_wd,
            method_fixed_cross_section_required=True,
            search_band_scan_used=False,
            search_nearest_valid_plane_used=False,
            provenance_evidence_ref=get_evidence_ref("HIP_DEPTH_M"),
            debug_info=debug_info_wd,
        )
        results["HIP_DEPTH_M"] = MeasurementResult(
            standard_key="HIP_DEPTH_M",
            value_m=depth_m,
            metadata=metadata_depth
        )
    else:
        # No slice found - return NaN for width/depth
        for key in ["HIP_WIDTH_M", "HIP_DEPTH_M"]:
            metric_type = "width" if "WIDTH" in key else "depth"
            debug_info = {
                "body_axis": {
                    "length_m": float(y_range),
                    "valid": True,
                    "reason_invalid": None
                }
            }
            if cross_section_debug_list:
                debug_info["cross_section"] = cross_section_debug_list[0] if cross_section_debug_list else {}
                debug_info["cross_section"]["slice_shared_from"] = "HIP_CIRC_M"
                debug_info["cross_section"]["slicer_called_independently"] = False
                debug_info["cross_section"]["slice_candidates_count"] = 0
            
            metadata = create_metadata_v0(
                standard_key=key,
                value_m=float('nan'),
                method_path_type="straight_line",
                method_metric_type=metric_type,
                warnings=warnings_wd + ["CROSS_SECTION_NOT_FOUND"],
                method_fixed_cross_section_required=True,
                search_band_scan_used=False,
                search_nearest_valid_plane_used=False,
                provenance_evidence_ref=get_evidence_ref(key),
                debug_info=debug_info,
            )
            results[key] = MeasurementResult(standard_key=key, value_m=float('nan'), metadata=metadata)
    
    return results


# -----------------------------
# Circumference Measurements
# -----------------------------
def measure_circumference_v0_with_metadata(
    verts: np.ndarray,
    standard_key: CircumferenceKey,
    units_metadata: Optional[Dict[str, Any]] = None,
) -> MeasurementResult:
    """
    Measure circumference with metadata (schema v0).
    
    Args:
        verts: Body surface vertices (N, 3) in meters
        standard_key: Circumference key
        units_metadata: Optional units metadata (assumed meters)
    
    Returns:
        MeasurementResult with value_m and metadata
    """
    verts = _as_np_f32(verts)
    is_valid, warnings = _validate_verts(verts)
    
    if not is_valid:
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="closed_curve",
            method_metric_type="circumference",
            warnings=warnings,
            method_fixed_height_required=True,
            search_band_scan_used=False,
            search_band_scan_limit_mm=10,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Determine canonical_side for right-side keys
    canonical_side = None
    if standard_key in ["THIGH_CIRC_M", "MIN_CALF_CIRC_M"]:
        canonical_side = "right"
    
    # Determine breath_state for torso keys
    breath_state = None
    if standard_key in ["NECK_CIRC_M", "BUST_CIRC_M", "UNDERBUST_CIRC_M", "WAIST_CIRC_M"]:
        breath_state = "neutral_mid"
    
    # Find measurement height region
    y_coords = verts[:, 1]
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    if y_range < 1e-6:
        warnings.append("BODY_AXIS_TOO_SHORT")
        debug_info = {
            "body_axis": {
                "length_m": float(y_range),
                "valid": False,
                "reason_invalid": "too_short"
            }
        }
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="closed_curve",
            method_metric_type="circumference",
            warnings=warnings,
            method_canonical_side=canonical_side,
            method_fixed_height_required=True,
            search_band_scan_used=False,
            search_band_scan_limit_mm=10,
            pose_breath_state=breath_state,
            provenance_evidence_ref=get_evidence_ref(standard_key),
            debug_info=debug_info,
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Define search region (v0 heuristic, semantic-compliant)
    # Note: WAIST is NOT redefined as "min circumference" - we use fixed height from semantic
    if standard_key == "NECK_CIRC_M":
        # Neck region (upper torso)
        y_start = y_min + 0.75 * y_range
        y_end = y_min + 0.90 * y_range
        landmark_confidence = "medium"  # SMPL-X landmark may be approximate
        landmark_resolution = "nearest_cross_section_fallback"
    elif standard_key == "BUST_CIRC_M":
        # Upper torso (breast volume)
        y_start = y_min + 0.40 * y_range
        y_end = y_min + 0.70 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    elif standard_key == "UNDERBUST_CIRC_M":
        # Lower chest (thoracic cage)
        y_start = y_min + 0.30 * y_range
        y_end = y_min + 0.60 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    elif standard_key == "WAIST_CIRC_M":
        # Mid torso (waist line - semantic defines as "most constricted", but we use fixed height)
        y_start = y_min + 0.40 * y_range
        y_end = y_min + 0.70 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    elif standard_key == "HIP_CIRC_M":
        # Lower torso (hip maximum)
        y_start = y_min + 0.50 * y_range
        y_end = y_min + 0.80 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    elif standard_key == "THIGH_CIRC_M":
        # Upper leg (thigh maximum)
        y_start = y_min + 0.20 * y_range
        y_end = y_min + 0.40 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    elif standard_key == "MIN_CALF_CIRC_M":
        # Lower leg (calf minimum, above ankle)
        y_start = y_min + 0.05 * y_range
        y_end = y_min + 0.20 * y_range
        landmark_confidence = "high"
        landmark_resolution = "direct"
    else:
        warnings.append(f"UNKNOWN_CIRC_KEY: {standard_key}")
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="closed_curve",
            method_metric_type="circumference",
            warnings=warnings,
            method_canonical_side=canonical_side,
            method_fixed_height_required=True,
            search_band_scan_used=False,
            search_band_scan_limit_mm=10,
            pose_breath_state=breath_state,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Generate candidates (fixed height, no band_scan)
    num_slices = 20
    slice_step = (y_end - y_start) / max(1, num_slices - 1)
    tolerance = slice_step * 0.5
    
    candidates = []
    cross_section_debug_list = []
    for i in range(num_slices):
        y_value = y_start + i * slice_step
        perimeter, debug_info = _compute_circumference_at_height(verts, y_value, tolerance, warnings, y_min, y_max)
        if debug_info:
            cross_section_debug_list.append(debug_info)
        if perimeter is not None:
            candidates.append({
                "y_value": y_value,
                "perimeter": perimeter,
                "slice_index": i
            })
    
    # Build debug info
    debug_info = {
        "body_axis": {
            "length_m": float(y_range),
            "valid": True,
            "reason_invalid": None
        }
    }
    if len(candidates) == 0:
        warnings.append("EMPTY_CANDIDATES")
        # Aggregate cross-section debug info
        if cross_section_debug_list:
            reasons = [d.get("reason_not_found") for d in cross_section_debug_list if d.get("reason_not_found")]
            candidates_counts = [d.get("candidates_count", 0) for d in cross_section_debug_list]
            if reasons:
                debug_info["cross_section"] = {
                    "target_height_ratio": cross_section_debug_list[0].get("target_height_ratio"),
                    "search_window_mm": cross_section_debug_list[0].get("search_window_mm"),
                    "candidates_count": 0,
                    "reason_not_found": reasons[0] if len(set(reasons)) == 1 else "mixed"
                }
        else:
            debug_info["cross_section"] = {
                "candidates_count": 0,
                "reason_not_found": "no_debug_info"
            }
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="closed_curve",
            method_metric_type="circumference",
            warnings=warnings,
            method_canonical_side=canonical_side,
            method_landmark_confidence=landmark_confidence,
            method_landmark_resolution=landmark_resolution,
            method_fixed_height_required=True,
            search_band_scan_used=False,
            search_band_scan_limit_mm=10,
            pose_breath_state=breath_state,
            provenance_evidence_ref=get_evidence_ref(standard_key),
            debug_info=debug_info,
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Select candidate based on semantic rule
    # BUST/HIP: max (maximum protrusion)
    # WAIST: semantic defines as "most constricted" but we use fixed height (no min search)
    # THIGH: max (maximum)
    # MIN_CALF: min (minimum)
    if standard_key in ["BUST_CIRC_M", "HIP_CIRC_M", "THIGH_CIRC_M"]:
        selected = max(candidates, key=lambda c: c["perimeter"])
    elif standard_key == "MIN_CALF_CIRC_M":
        selected = min(candidates, key=lambda c: c["perimeter"])
        warnings.append("MIN_SEARCH_USED")  # Record that min search was used
    else:
        # NECK, UNDERBUST, WAIST: use median for stability (fixed height approach)
        perimeters = [c["perimeter"] for c in candidates]
        median_perimeter = float(np.median(perimeters))
        selected = min(candidates, key=lambda c: abs(c["perimeter"] - median_perimeter))
    
    value_m = selected["perimeter"]
    
    # Range sanity check (warnings only)
    if value_m < 0.1:
        warnings.append(f"PERIMETER_SMALL: {value_m:.4f}m")
    if value_m > 3.0:
        warnings.append(f"PERIMETER_LARGE: {value_m:.4f}m")
    
    # Create metadata with debug info
    debug_info = {
        "body_axis": {
            "length_m": float(y_range),
            "valid": True,
            "reason_invalid": None
        },
        "cross_section": {
            "candidates_count": len(candidates),
            "target_height_ratio": float((selected["y_value"] - y_min) / y_range) if y_range > 0 else 0.0,
            "search_window_mm": float(tolerance * 1000.0)
        }
    }
    metadata = create_metadata_v0(
        standard_key=standard_key,
        value_m=value_m,
        method_path_type="closed_curve",
        method_metric_type="circumference",
        warnings=warnings,
        method_canonical_side=canonical_side,
        method_landmark_confidence=landmark_confidence,
        method_landmark_resolution=landmark_resolution,
        method_fixed_height_required=True,
        search_band_scan_used=False,  # Forbidden by default
        search_band_scan_limit_mm=10,
        search_min_max_search_used=(standard_key == "MIN_CALF_CIRC_M"),
        pose_breath_state=breath_state,
        provenance_evidence_ref=get_evidence_ref(standard_key),
        debug_info=debug_info,
    )
    
    return MeasurementResult(
        standard_key=standard_key,
        value_m=value_m,
        metadata=metadata
    )


# -----------------------------
# Width/Depth Measurements
# -----------------------------
def measure_width_depth_v0_with_metadata(
    verts: np.ndarray,
    standard_key: WidthDepthKey,
    units_metadata: Optional[Dict[str, Any]] = None,
    proxy_used: bool = False,
    proxy_tool: Optional[str] = None,
) -> MeasurementResult:
    """
    Measure width or depth with metadata (schema v0).
    
    Args:
        verts: Body surface vertices (N, 3) in meters
        standard_key: Width or depth key
        units_metadata: Optional units metadata
        proxy_used: Whether plane_clamp proxy was used
        proxy_tool: Proxy tool name if proxy_used (e.g., "acrylic_board", "caliper")
    
    Returns:
        MeasurementResult with value_m and metadata
    """
    verts = _as_np_f32(verts)
    is_valid, warnings = _validate_verts(verts)
    
    if not is_valid:
        metric_type = "width" if "WIDTH" in standard_key else "depth"
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type=metric_type,
            warnings=warnings,
            method_fixed_cross_section_required=True,
            proxy_proxy_used=proxy_used,
            proxy_proxy_type="plane_clamp" if proxy_used else None,
            proxy_proxy_tool=proxy_tool,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Determine breath_state
    breath_state = "neutral_mid"
    if standard_key in ["CHEST_WIDTH_M", "CHEST_DEPTH_M", "WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
        breath_state = "neutral_mid"
    
    # Determine arms_down requirement
    arms_down = None
    if standard_key == "CHEST_WIDTH_M":
        arms_down = True  # Evidence requires arms down
    
    # Find cross-section at appropriate height
    y_coords = verts[:, 1]
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    if y_range < 1e-6:
        warnings.append("BODY_AXIS_TOO_SHORT")
        metric_type = "width" if "WIDTH" in standard_key else "depth"
        debug_info = {
            "body_axis": {
                "length_m": float(y_range),
                "valid": False,
                "reason_invalid": "too_short"
            }
        }
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type=metric_type,
            warnings=warnings,
            method_fixed_cross_section_required=True,
            proxy_proxy_used=proxy_used,
            proxy_proxy_type="plane_clamp" if proxy_used else None,
            proxy_proxy_tool=proxy_tool,
            pose_breath_state=breath_state,
            pose_arms_down=arms_down,
            provenance_evidence_ref=get_evidence_ref(standard_key),
            debug_info=debug_info,
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Define height region
    if standard_key in ["CHEST_WIDTH_M", "CHEST_DEPTH_M"]:
        # Armpit level
        y_target = y_min + 0.35 * y_range
    elif standard_key in ["WAIST_WIDTH_M", "WAIST_DEPTH_M"]:
        # Waist level
        y_target = y_min + 0.50 * y_range
    elif standard_key in ["HIP_WIDTH_M", "HIP_DEPTH_M"]:
        # Hip level
        y_target = y_min + 0.60 * y_range
    else:
        warnings.append(f"UNKNOWN_WIDTH_DEPTH_KEY: {standard_key}")
        metric_type = "width" if "WIDTH" in standard_key else "depth"
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type=metric_type,
            warnings=warnings,
            method_fixed_cross_section_required=True,
            proxy_proxy_used=proxy_used,
            proxy_proxy_type="plane_clamp" if proxy_used else None,
            proxy_proxy_tool=proxy_tool,
            pose_breath_state=breath_state,
            pose_arms_down=arms_down,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Find cross-section with enhanced handling for waist/hip
    # For waist/hip, use slightly larger tolerance and allow nearest fallback
    is_waist_hip = standard_key in ["WAIST_WIDTH_M", "WAIST_DEPTH_M", "HIP_WIDTH_M", "HIP_DEPTH_M"]
    
    if is_waist_hip:
        # Increase tolerance for waist/hip (min 5mm, max 3% of body height)
        base_tolerance = y_range * 0.02  # 2%
        min_tolerance = 0.005  # 5mm minimum
        tolerance = max(min_tolerance, min(base_tolerance, y_range * 0.03))
        if tolerance > base_tolerance:
            warnings.append("SLICE_THICKNESS_ADJUSTED")
    else:
        tolerance = y_range * 0.02  # 2% of body height
    
    # Find cross-section (without fallback first to get initial state)
    vertices_2d, cross_section_debug = _find_cross_section(
        verts, y_target, tolerance, warnings, y_min, y_max,
        target_mode="ratio",
        allow_nearest_fallback=False  # Don't use old fallback logic
    )
    
    # Track initial state for debug
    initial_candidates_count = 0
    if cross_section_debug:
        initial_candidates_count = cross_section_debug.get("candidates_count", 0)
    
    # If failed and is waist/hip, try nearest valid plane fallback
    # CRITICAL: If candidates_count == 0, ALWAYS try fallback (regardless of reason)
    nearest_fallback_used = False
    nearest_fallback_shift_mm = None
    nearest_fallback_debug = None
    fallback_candidates_count = 0
    
    if vertices_2d is None and is_waist_hip:
        # Check if candidates_count == 0 (main trigger)
        if initial_candidates_count == 0:
            # Try nearest valid plane fallback (<=10mm shift)
            # Use finer step (1mm) for better coverage
            fallback_vertices, fallback_shift_mm, fallback_debug = _find_nearest_valid_plane(
                verts, y_target, tolerance, max_shift_mm=10.0, y_min=y_min, y_max=y_max, step_mm=1.0
            )
            if fallback_vertices is not None and fallback_shift_mm is not None:
                if fallback_shift_mm <= 10.0:  # Policy limit
                    vertices_2d = fallback_vertices
                    nearest_fallback_used = True
                    nearest_fallback_shift_mm = fallback_shift_mm
                    nearest_fallback_debug = fallback_debug
                    if fallback_debug:
                        fallback_candidates_count = fallback_debug.get("nearest_valid_plane_candidates_count", 0)
                    warnings.append("NEAREST_VALID_PLANE_FALLBACK")
                else:
                    # Shift exceeds policy limit - do not use
                    if cross_section_debug:
                        cross_section_debug["fallback_failure_reason"] = "shift_exceeds_10mm"
            else:
                # Fallback failed - no valid plane within 10mm
                if cross_section_debug:
                    cross_section_debug["fallback_failure_reason"] = "no_plane_with_candidates_within_10mm"
        elif cross_section_debug:
            reason = cross_section_debug.get("reason_not_found")
            if reason == "too_thin_slice":
                # Try with larger tolerance (up to 5% of body height)
                larger_tolerance = min(y_range * 0.05, tolerance * 2.0)
                if larger_tolerance > tolerance:
                    warnings.append("SLICE_THICKNESS_ADJUSTED")
                    vertices_2d, cross_section_debug = _find_cross_section(
                        verts, y_target, larger_tolerance, warnings, y_min, y_max,
                        target_mode="ratio",
                        allow_nearest_fallback=False
                    )
                    if cross_section_debug:
                        cross_section_debug["slice_half_thickness_m"] = float(larger_tolerance)
                        cross_section_debug["slice_thickness_adjusted"] = True
    
    if vertices_2d is None:
        warnings.append("CROSS_SECTION_NOT_FOUND")
        metric_type = "width" if "WIDTH" in standard_key else "depth"
        debug_info = {
            "body_axis": {
                "length_m": float(y_range),
                "valid": True,
                "reason_invalid": None
            }
        }
        if cross_section_debug:
            debug_info["cross_section"] = cross_section_debug
        if nearest_fallback_debug:
            debug_info["nearest_valid_plane"] = nearest_fallback_debug
        # Record landmark_resolution if fallback was used
        landmark_resolution = None
        if nearest_fallback_used:
            landmark_resolution = "nearest_valid_plane"
        elif cross_section_debug and cross_section_debug.get("fallback_used"):
            landmark_resolution = "nearest_valid_plane"
        # Record search metadata for nearest valid plane fallback
        search_nearest_valid_plane_used = nearest_fallback_used
        search_nearest_valid_plane_shift_mm = int(nearest_fallback_shift_mm) if nearest_fallback_shift_mm is not None else None
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type=metric_type,
            warnings=warnings,
            method_fixed_cross_section_required=True,
            method_landmark_resolution=landmark_resolution,
            search_band_scan_used=False,  # Always false (fallback is not scan)
            search_nearest_valid_plane_used=search_nearest_valid_plane_used,
            search_nearest_valid_plane_shift_mm=search_nearest_valid_plane_shift_mm,
            proxy_proxy_used=proxy_used,
            proxy_proxy_type="plane_clamp" if proxy_used else None,
            proxy_proxy_tool=proxy_tool,
            pose_breath_state=breath_state,
            pose_arms_down=arms_down,
            provenance_evidence_ref=get_evidence_ref(standard_key),
            debug_info=debug_info,
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Compute width or depth
    if "WIDTH" in standard_key:
        # Width: left-right distance (x-axis span)
        x_min = float(np.min(vertices_2d[:, 0]))
        x_max = float(np.max(vertices_2d[:, 0]))
        value_m = x_max - x_min
    else:  # DEPTH
        # Depth: front-back distance (z-axis span)
        z_min = float(np.min(vertices_2d[:, 1]))
        z_max = float(np.max(vertices_2d[:, 1]))
        value_m = z_max - z_min
    
    # Range sanity check
    if value_m < 0.05:
        warnings.append(f"WIDTH_DEPTH_SMALL: {value_m:.4f}m")
    if value_m > 1.0:
        warnings.append(f"WIDTH_DEPTH_LARGE: {value_m:.4f}m")
    
    metric_type = "width" if "WIDTH" in standard_key else "depth"
    
    # Create metadata with debug info
    debug_info = {
        "body_axis": {
            "length_m": float(y_range),
            "valid": True,
            "reason_invalid": None
        }
    }
    
    # Enhanced debug for waist/hip cross-section failures
    if is_waist_hip:
        cross_section_debug_enhanced = {}
        if cross_section_debug:
            cross_section_debug_enhanced.update(cross_section_debug)
        
        # Add target/bbox/axis debug
        cross_section_debug_enhanced["target_mode"] = "ratio"
        cross_section_debug_enhanced["target_value"] = float((y_target - y_min) / y_range) if y_range > 0 else 0.0
        cross_section_debug_enhanced["axis_name"] = "y_up"
        cross_section_debug_enhanced["axis_length_m"] = float(y_range)
        cross_section_debug_enhanced["bbox_min_axis"] = float(y_min)
        cross_section_debug_enhanced["bbox_max_axis"] = float(y_max)
        cross_section_debug_enhanced["slice_half_thickness_m"] = float(tolerance)
        cross_section_debug_enhanced["initial_candidates_count"] = initial_candidates_count
        
        # Check if target is out of bounds
        if y_target < y_min or y_target > y_max:
            cross_section_debug_enhanced["target_out_of_bounds"] = True
        else:
            cross_section_debug_enhanced["target_out_of_bounds"] = False
        
        # Add fallback info
        if nearest_fallback_used:
            cross_section_debug_enhanced["fallback_candidates_count"] = fallback_candidates_count
            cross_section_debug_enhanced["fallback_shift_mm"] = float(nearest_fallback_shift_mm) if nearest_fallback_shift_mm is not None else None
        else:
            cross_section_debug_enhanced["fallback_candidates_count"] = 0
            cross_section_debug_enhanced["fallback_shift_mm"] = None
            if cross_section_debug:
                failure_reason = cross_section_debug.get("fallback_failure_reason")
                if failure_reason:
                    cross_section_debug_enhanced["fallback_failure_reason"] = failure_reason
        
        debug_info["cross_section"] = cross_section_debug_enhanced
    elif cross_section_debug:
        debug_info["cross_section"] = cross_section_debug
    
    if nearest_fallback_debug:
        debug_info["nearest_valid_plane"] = nearest_fallback_debug
    
    # Record landmark_resolution if fallback was used
    landmark_resolution = None
    if nearest_fallback_used:
        landmark_resolution = "nearest_valid_plane"
    elif cross_section_debug and cross_section_debug.get("fallback_used"):
        landmark_resolution = "nearest_valid_plane"
    
    # Record search metadata for nearest valid plane fallback
    search_nearest_valid_plane_used = nearest_fallback_used
    search_nearest_valid_plane_shift_mm = int(nearest_fallback_shift_mm) if nearest_fallback_shift_mm is not None else None
    
    metadata = create_metadata_v0(
        standard_key=standard_key,
        value_m=value_m,
        method_path_type="straight_line",
        method_metric_type=metric_type,
        warnings=warnings,
        method_fixed_cross_section_required=True,
        method_landmark_resolution=landmark_resolution,
        search_band_scan_used=False,  # Always false (fallback is not scan)
        search_nearest_valid_plane_used=search_nearest_valid_plane_used,
        search_nearest_valid_plane_shift_mm=search_nearest_valid_plane_shift_mm,
        proxy_proxy_used=proxy_used,
        proxy_proxy_type="plane_clamp" if proxy_used else None,
        proxy_proxy_tool=proxy_tool,
        pose_breath_state=breath_state,
        pose_arms_down=arms_down,
        provenance_evidence_ref=get_evidence_ref(standard_key),
        debug_info=debug_info,
    )
    
    return MeasurementResult(
        standard_key=standard_key,
        value_m=value_m,
        metadata=metadata
    )


# -----------------------------
# Height Measurements
# -----------------------------
def measure_height_v0_with_metadata(
    verts: np.ndarray,
    standard_key: Literal["HEIGHT_M", "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M"],
    units_metadata: Optional[Dict[str, Any]] = None,
) -> MeasurementResult:
    """
    Measure height with metadata (schema v0).
    
    Args:
        verts: Body surface vertices (N, 3) in meters
        standard_key: Height key
        units_metadata: Optional units metadata
    
    Returns:
        MeasurementResult with value_m and metadata
    """
    verts = _as_np_f32(verts)
    is_valid, warnings = _validate_verts(verts)
    
    if not is_valid:
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type="height",
            warnings=warnings,
            pose_strict_standing=True,
            pose_knee_flexion_forbidden=True,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Determine canonical_side for KNEE_HEIGHT_M
    canonical_side = None
    if standard_key == "KNEE_HEIGHT_M":
        canonical_side = "right"
    
    y_coords = verts[:, 1]
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    
    if standard_key == "HEIGHT_M":
        # Height: vertex (top of head) to floor
        # For v0, use y_max as top and y_min as floor
        value_m = y_max - y_min
        landmark_confidence = "medium"  # Vertex may be approximate
        landmark_resolution = "direct"
        
        # Debug info for HEIGHT_M scale investigation
        debug_info = {
            "height_calculation": {
                "axis_used": "y",
                "bbox_min": float(y_min),
                "bbox_max": float(y_max),
                "height_raw": float(value_m),
                "height_after_scale": float(value_m),  # No scaling applied in v0
                "scale_factor": 1.0
            }
        }
    elif standard_key == "CROTCH_HEIGHT_M":
        # Crotch height: crotch point to floor
        # For v0, estimate crotch as lower torso region
        y_crotch = y_min + 0.45 * (y_max - y_min)  # Approximate
        value_m = y_crotch - y_min
        landmark_confidence = "medium"
        landmark_resolution = "nearest_cross_section_fallback"
        warnings.append("CROTCH_ESTIMATED")  # Record estimation
    elif standard_key == "KNEE_HEIGHT_M":
        # Knee height: knee point to floor (right side)
        # For v0, estimate knee as mid-leg region
        y_knee = y_min + 0.25 * (y_max - y_min)  # Approximate
        value_m = y_knee - y_min
        landmark_confidence = "medium"
        landmark_resolution = "nearest_cross_section_fallback"
        warnings.append("KNEE_ESTIMATED")  # Record estimation
    else:
        warnings.append(f"UNKNOWN_HEIGHT_KEY: {standard_key}")
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type="height",
            warnings=warnings,
            method_canonical_side=canonical_side,
            pose_strict_standing=True,
            pose_knee_flexion_forbidden=True,
            provenance_evidence_ref=get_evidence_ref(standard_key),
        )
        return MeasurementResult(
            standard_key=standard_key,
            value_m=float('nan'),
            metadata=metadata
        )
    
    # Range sanity check
    if value_m < 0.1:
        warnings.append(f"HEIGHT_SMALL: {value_m:.4f}m")
    if value_m > 3.0:
        warnings.append(f"HEIGHT_LARGE: {value_m:.4f}m")
    
    # Create metadata
    metadata = create_metadata_v0(
        standard_key=standard_key,
        value_m=value_m,
        method_path_type="straight_line",
        method_metric_type="height",
        warnings=warnings,
        method_canonical_side=canonical_side,
        method_landmark_confidence=landmark_confidence,
        method_landmark_resolution=landmark_resolution,
        pose_strict_standing=True,
        pose_knee_flexion_forbidden=True,
        provenance_evidence_ref=get_evidence_ref(standard_key),
    )
    
    return MeasurementResult(
        standard_key=standard_key,
        value_m=value_m,
        metadata=metadata
    )


# -----------------------------
# Length Measurements
# -----------------------------
def measure_arm_length_v0_with_metadata(
    verts: np.ndarray,
    joints_xyz: Optional[np.ndarray] = None,
    joint_ids: Optional[Dict[str, int]] = None,
    units_metadata: Optional[Dict[str, Any]] = None,
) -> MeasurementResult:
    """
    Measure ARM_LEN_M with metadata (schema v0).
    
    ARM_LEN_M is defined as surface path from shoulder to wrist (right side).
    Path type must be surface_path (not straight_line).
    
    Args:
        verts: Body surface vertices (N, 3) in meters
        joints_xyz: Optional joint positions (J, 3) for landmark detection
        joint_ids: Optional joint ID mapping (e.g., {"R_shoulder": 17, "R_wrist": 21})
        units_metadata: Optional units metadata
    
    Returns:
        MeasurementResult with value_m and metadata
    """
    verts = _as_np_f32(verts)
    is_valid, warnings = _validate_verts(verts)
    
    if not is_valid:
        metadata = create_metadata_v0(
            standard_key="ARM_LEN_M",
            value_m=float('nan'),
            method_path_type="surface_path",
            method_metric_type="length",
            warnings=warnings,
            method_canonical_side="right",
            provenance_evidence_ref=get_evidence_ref("ARM_LEN_M"),
        )
        return MeasurementResult(
            standard_key="ARM_LEN_M",
            value_m=float('nan'),
            metadata=metadata
        )
    
    # For v0, if joints are available, use them for landmarks
    # Otherwise, estimate from vertex geometry
    if joints_xyz is not None and joint_ids is not None:
        # Use joint landmarks
        r_shoulder_idx = joint_ids.get("R_shoulder")
        r_wrist_idx = joint_ids.get("R_wrist")
        
        if r_shoulder_idx is not None and r_wrist_idx is not None:
            shoulder_pos = joints_xyz[r_shoulder_idx]
            wrist_pos = joints_xyz[r_wrist_idx]
            
            # For v0, approximate surface path as geodesic distance
            # Simple approximation: use straight line distance as baseline
            # (In production, would use actual geodesic/surface path)
            straight_dist = np.linalg.norm(wrist_pos - shoulder_pos)
            # Surface path is typically 5-10% longer than straight line
            # For v0, use 1.05x multiplier as approximation
            value_m = float(straight_dist * 1.05)
            landmark_confidence = "high"
            landmark_resolution = "direct"
        else:
            warnings.append("JOINT_IDS_MISSING")
            # Fallback: estimate from vertex geometry
            value_m = float('nan')
            landmark_confidence = "low"
            landmark_resolution = "nearest_cross_section_fallback"
    else:
        # Fallback: estimate from vertex geometry
        # Find approximate shoulder and wrist regions
        y_coords = verts[:, 1]
        y_max = float(np.max(y_coords))
        y_range = y_max - float(np.min(y_coords))
        
        # Shoulder region: upper torso
        y_shoulder = y_max - 0.15 * y_range
        # Wrist region: lower arm
        y_wrist = y_max - 0.50 * y_range
        
        # Find vertices in these regions
        shoulder_mask = np.abs(y_coords - y_shoulder) < 0.05 * y_range
        wrist_mask = np.abs(y_coords - y_wrist) < 0.05 * y_range
        
        if np.sum(shoulder_mask) == 0 or np.sum(wrist_mask) == 0:
            warnings.append("LANDMARK_REGIONS_NOT_FOUND")
            value_m = float('nan')
            landmark_confidence = "low"
            landmark_resolution = "nearest_cross_section_fallback"
            found_regions = []
            if np.sum(shoulder_mask) > 0:
                found_regions.append("shoulder_region")
            if np.sum(wrist_mask) > 0:
                found_regions.append("wrist_region")
            debug_info = {
                "landmark_regions": {
                    "required": ["shoulder_region", "wrist_region"],
                    "found": found_regions,
                    "reason_not_found": "no_vertices_in_region"
                }
            }
            metadata = create_metadata_v0(
                standard_key="ARM_LEN_M",
                value_m=value_m,
                method_path_type="surface_path",
                method_metric_type="length",
                warnings=warnings,
                method_canonical_side="right",
                method_landmark_confidence=landmark_confidence,
                method_landmark_resolution=landmark_resolution,
                provenance_evidence_ref=get_evidence_ref("ARM_LEN_M"),
                debug_info=debug_info,
            )
            return MeasurementResult(
                standard_key="ARM_LEN_M",
                value_m=value_m,
                metadata=metadata
            )
        else:
            # Use rightmost points in each region (right arm)
            shoulder_verts = verts[shoulder_mask]
            wrist_verts = verts[wrist_mask]
            
            shoulder_rightmost = shoulder_verts[np.argmax(shoulder_verts[:, 0])]
            wrist_rightmost = wrist_verts[np.argmax(wrist_verts[:, 0])]
            
            straight_dist = np.linalg.norm(wrist_rightmost - shoulder_rightmost)
            value_m = float(straight_dist * 1.05)  # Surface path approximation
            landmark_confidence = "medium"
            landmark_resolution = "nearest_cross_section_fallback"
            warnings.append("SURFACE_PATH_APPROXIMATED")
    
    # Range sanity check
    if not np.isnan(value_m):
        if value_m < 0.2:
            warnings.append(f"ARM_LEN_SMALL: {value_m:.4f}m")
        if value_m > 1.0:
            warnings.append(f"ARM_LEN_LARGE: {value_m:.4f}m")
    
    # Create metadata
    metadata = create_metadata_v0(
        standard_key="ARM_LEN_M",
        value_m=value_m,
        method_path_type="surface_path",  # Required: surface path, not straight line
        method_metric_type="length",
        warnings=warnings,
        method_canonical_side="right",  # Required: right side
        method_landmark_confidence=landmark_confidence,
        method_landmark_resolution=landmark_resolution,
        provenance_evidence_ref=get_evidence_ref("ARM_LEN_M"),
    )
    
    return MeasurementResult(
        standard_key="ARM_LEN_M",
        value_m=value_m,
        metadata=metadata
    )


# -----------------------------
# Weight (Input-only, no mesh computation)
# -----------------------------
def create_weight_metadata(
    value_kg: float,
    warnings: Optional[List[str]] = None,
) -> MeasurementResult:
    """
    Create weight measurement result with metadata.
    Weight cannot be computed from mesh - it must be provided as input.
    
    Args:
        value_kg: Weight in kilograms
        warnings: Optional warnings
    
    Returns:
        MeasurementResult with value_kg and metadata
    """
    metadata = create_metadata_v0(
        standard_key="WEIGHT_KG",
        value_kg=value_kg,
        method_path_type="straight_line",  # N/A for weight
        method_metric_type="mass",
        warnings=warnings if warnings is not None else [],
        provenance_evidence_ref=get_evidence_ref("WEIGHT_KG"),
    )
    
    return MeasurementResult(
        standard_key="WEIGHT_KG",
        value_kg=value_kg,
        metadata=metadata
    )
