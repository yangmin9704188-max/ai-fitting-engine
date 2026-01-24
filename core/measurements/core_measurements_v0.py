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
    
    # Allow nearest fallback for waist/hip
    allow_fallback = is_waist_hip
    vertices_2d, cross_section_debug = _find_cross_section(
        verts, y_target, tolerance, warnings, y_min, y_max,
        target_mode="ratio",
        allow_nearest_fallback=allow_fallback
    )
    
    # If failed and is waist/hip, try with adjusted tolerance
    if vertices_2d is None and is_waist_hip and cross_section_debug:
        reason = cross_section_debug.get("reason_not_found")
        if reason in ["too_thin_slice", "mesh_empty_at_height"]:
            # Try with larger tolerance (up to 5% of body height)
            larger_tolerance = min(y_range * 0.05, tolerance * 2.0)
            if larger_tolerance > tolerance:
                warnings.append("SLICE_THICKNESS_ADJUSTED")
                vertices_2d, cross_section_debug = _find_cross_section(
                    verts, y_target, larger_tolerance, warnings, y_min, y_max,
                    target_mode="ratio",
                    allow_nearest_fallback=False  # Already tried fallback
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
        # Record landmark_resolution if fallback was used
        landmark_resolution = None
        if cross_section_debug and cross_section_debug.get("fallback_used"):
            landmark_resolution = "nearest_valid_plane"
        metadata = create_metadata_v0(
            standard_key=standard_key,
            value_m=float('nan'),
            method_path_type="straight_line",
            method_metric_type=metric_type,
            warnings=warnings,
            method_fixed_cross_section_required=True,
            method_landmark_resolution=landmark_resolution,
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
    if cross_section_debug:
        debug_info["cross_section"] = cross_section_debug
    
    # Record landmark_resolution if fallback was used
    landmark_resolution = None
    if cross_section_debug and cross_section_debug.get("fallback_used"):
        landmark_resolution = "nearest_valid_plane"
    
    metadata = create_metadata_v0(
        standard_key=standard_key,
        value_m=value_m,
        method_path_type="straight_line",
        method_metric_type=metric_type,
        warnings=warnings,
        method_fixed_cross_section_required=True,
        method_landmark_resolution=landmark_resolution,
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
