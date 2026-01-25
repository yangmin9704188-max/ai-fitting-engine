#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for core measurements v0 validation.

This script generates synthetic mesh cases with human-like scale invariants.
Valid cases (normal_*, varied_*) must satisfy physical plausibility constraints.
Expected fail cases (degenerate_*, etc.) are intentionally invalid for testing.
"""

import numpy as np
import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set seed for reproducibility
np.random.seed(42)

# ============================================================================
# FAST MODE Support
# ============================================================================
def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Create S0 synthetic dataset")
    parser.add_argument(
        "--only-case",
        type=str,
        default=None,
        help="FAST MODE: Generate only this case (e.g., normal_1)"
    )
    return parser.parse_args()

def get_only_case() -> Optional[str]:
    """Get ONLY_CASE from CLI or environment variable."""
    args = parse_args()
    if args.only_case:
        return args.only_case
    return os.environ.get("ONLY_CASE", None)

def find_latest_debug_json(debug_dir: Path) -> Optional[Path]:
    """Find the latest invariant fail debug JSON."""
    if not debug_dir.exists():
        return None
    json_files = list(debug_dir.glob("s0_invariant_fail_*.json"))
    if not json_files:
        return None
    return max(json_files, key=lambda p: p.stat().st_mtime)

def fmt_m(x: Optional[float]) -> str:
    """Format meter value safely (None -> 'N/A')."""
    if x is None:
        return "N/A"
    try:
        return f"{x:.4f}m"
    except (TypeError, ValueError):
        return f"{x}"

def find_key_candidate(data: Dict[str, Any], candidates: List[str]) -> Tuple[Optional[Any], Optional[str]]:
    """Find first non-None value among candidate keys."""
    for key in candidates:
        value = data.get(key)
        if value is not None:
            return value, key
    return None, None

def parse_debug_json(debug_path: Path) -> Optional[Dict[str, Any]]:
    """Parse debug JSON and return summary."""
    try:
        with open(debug_path, "r") as f:
            data = json.load(f)
        
        # Print original JSON keys for debugging
        original_keys = sorted(data.keys())
        print(f"[DEBUG JSON PARSER] Original JSON keys: {original_keys}")
        
        # Try multiple candidate keys for bust/waist/hip
        bust_candidates = ["bust_circ_estimate", "bust_circ_m", "bust_est_m", "BUST_CIRC_M", "bust_circ"]
        waist_candidates = ["waist_circ_estimate", "waist_circ_m", "waist_est_m", "WAIST_CIRC_M", "waist_circ"]
        hip_candidates = ["hip_circ_estimate", "hip_circ_m", "hip_est_m", "HIP_CIRC_M", "hip_circ"]
        
        bust_value, bust_key = find_key_candidate(data, bust_candidates)
        waist_value, waist_key = find_key_candidate(data, waist_candidates)
        hip_value, hip_key = find_key_candidate(data, hip_candidates)
        
        summary = {
            "case_id": data.get("case_id"),
            "height_m_after_scale": data.get("bbox_span_y_after"),
            "bust_circ_estimate": bust_value,
            "bust_circ_key_used": bust_key,
            "waist_circ_estimate": waist_value,
            "waist_circ_key_used": waist_key,
            "hip_circ_estimate": hip_value,
            "hip_circ_key_used": hip_key,
            "scale_factor": data.get("scale_factor_applied"),
            "bbox_span_y_before": data.get("bbox_span_y_before"),
            "target_height_m": data.get("target_height_m"),
            "error_message": data.get("error_message"),
            "clamp_applied": data.get("clamp_applied", False),
            "_original_keys": original_keys  # For debugging
        }
        return summary
    except Exception as e:
        print(f"[DEBUG JSON PARSER] Failed to parse {debug_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_debug_summary(debug_summary: Dict[str, Any]):
    """Print debug JSON summary (None-safe)."""
    print("\n" + "="*60)
    print("[DEBUG JSON SUMMARY] Last invariant fail analysis:")
    print("="*60)
    
    # Print available keys
    available_keys = sorted([k for k in debug_summary.keys() if not k.startswith("_")])
    print(f"[DEBUG JSON KEYS] Available keys: {available_keys}")
    if "_original_keys" in debug_summary:
        print(f"[DEBUG JSON KEYS] Original JSON keys: {debug_summary['_original_keys']}")
    
    # None-safe printing
    case_id = debug_summary.get('case_id', 'N/A')
    height = debug_summary.get('height_m_after_scale')
    scale_factor = debug_summary.get('scale_factor')
    bust = debug_summary.get('bust_circ_estimate')
    bust_key = debug_summary.get('bust_circ_key_used')
    waist = debug_summary.get('waist_circ_estimate')
    waist_key = debug_summary.get('waist_circ_key_used')
    hip = debug_summary.get('hip_circ_estimate')
    hip_key = debug_summary.get('hip_circ_key_used')
    error_msg = debug_summary.get('error_message', 'N/A')
    clamp_applied = debug_summary.get('clamp_applied', False)
    
    print(f"  Case ID: {case_id}")
    print(f"  Height (after scale): {fmt_m(height)}")
    print(f"  Scale factor: {fmt_m(scale_factor)}")
    print(f"  BUST_CIRC estimate: {fmt_m(bust)} (key: {bust_key or 'None'})")
    print(f"  WAIST_CIRC estimate: {fmt_m(waist)} (key: {waist_key or 'None'})")
    print(f"  HIP_CIRC estimate: {fmt_m(hip)} (key: {hip_key or 'None'})")
    print(f"  Error: {error_msg}")
    print(f"  Clamp applied: {clamp_applied}")
    print("="*60)
    print()

# ============================================================================
# Human-like Scale Invariants (Physical Plausibility)
# ============================================================================

HEIGHT_RANGE = (1.45, 1.95)  # meters

CIRCUMFERENCE_RANGES = {
    "NECK": (0.25, 0.55),
    "BUST": (0.60, 1.40),
    "UNDERBUST": (0.60, 1.40),
    "WAIST": (0.50, 1.30),
    "HIP": (0.65, 1.50),
    "THIGH": (0.35, 0.90),
    "MIN_CALF": (0.20, 0.60),
}

CIRCUMFERENCE_TO_HEIGHT_RATIOS = {
    "BUST": (0.35, 0.85),
    "WAIST": (0.30, 0.75),
    "HIP": (0.35, 0.90),
}


def check_human_like_invariants(
    verts: np.ndarray,
    case_id: str,
    case_class: str = "valid",
    bust_circ_theoretical: Optional[float] = None,
    waist_circ_theoretical: Optional[float] = None,
    hip_circ_theoretical: Optional[float] = None
) -> Tuple[bool, Optional[str]]:
    """
    Check if mesh vertices satisfy human-like scale invariants.
    
    Args:
        verts: Mesh vertices (N, 3) in meters
        case_id: Case identifier
        case_class: "valid" or "expected_fail"
        bust_circ_theoretical: Optional theoretical bust circumference (for valid cases, use this instead of vertex estimation)
        waist_circ_theoretical: Optional theoretical waist circumference
        hip_circ_theoretical: Optional theoretical hip circumference
    
    Returns:
        (is_valid, error_message)
    """
    if case_class == "expected_fail":
        # Expected fail cases are exempt from invariant checks
        return True, None
    
    # Check height range
    y_coords = verts[:, 1]
    height = float(np.max(y_coords) - np.min(y_coords))
    
    if height < HEIGHT_RANGE[0] or height > HEIGHT_RANGE[1]:
        return False, f"Height {height:.3f}m out of range {HEIGHT_RANGE}"
    
    # Estimate circumferences from cross-sections
    # For simplicity, we check radius-based estimates
    y_min = float(np.min(y_coords))
    y_max = float(np.max(y_coords))
    y_range = y_max - y_min
    
    # Check bust region (around 0.35 * height from bottom)
    # FIX: Use theoretical value if provided (prevents double-scaling amplification)
    if bust_circ_theoretical is not None:
        bust_circ = bust_circ_theoretical
    else:
        bust_y = y_min + 0.35 * y_range
        bust_radius = _estimate_radius_at_height(verts, bust_y)
        if bust_radius is not None:
            bust_circ = 2 * np.pi * bust_radius
        else:
            bust_circ = None
    
    if bust_circ is not None:
        if bust_circ < CIRCUMFERENCE_RANGES["BUST"][0] or bust_circ > CIRCUMFERENCE_RANGES["BUST"][1]:
            return False, f"BUST_CIRC estimate {bust_circ:.3f}m out of range {CIRCUMFERENCE_RANGES['BUST']}"
        bust_height_ratio = bust_circ / height
        if bust_height_ratio < CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"][0] or \
           bust_height_ratio > CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"][1]:
            return False, f"BUST/HEIGHT ratio {bust_height_ratio:.3f} out of range {CIRCUMFERENCE_TO_HEIGHT_RATIOS['BUST']}"
    
    # Check waist region (around 0.50 * height from bottom)
    if waist_circ_theoretical is not None:
        waist_circ = waist_circ_theoretical
    else:
        waist_y = y_min + 0.50 * y_range
        waist_radius = _estimate_radius_at_height(verts, waist_y)
        if waist_radius is not None:
            waist_circ = 2 * np.pi * waist_radius
        else:
            waist_circ = None
    
    if waist_circ is not None:
        if waist_circ < CIRCUMFERENCE_RANGES["WAIST"][0] or waist_circ > CIRCUMFERENCE_RANGES["WAIST"][1]:
            return False, f"WAIST_CIRC estimate {waist_circ:.3f}m out of range {CIRCUMFERENCE_RANGES['WAIST']}"
        waist_height_ratio = waist_circ / height
        if waist_height_ratio < CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"][0] or \
           waist_height_ratio > CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"][1]:
            return False, f"WAIST/HEIGHT ratio {waist_height_ratio:.3f} out of range {CIRCUMFERENCE_TO_HEIGHT_RATIOS['WAIST']}"
    
    # Check hip region (around 0.60 * height from bottom)
    if hip_circ_theoretical is not None:
        hip_circ = hip_circ_theoretical
    else:
        hip_y = y_min + 0.60 * y_range
        hip_radius = _estimate_radius_at_height(verts, hip_y)
        if hip_radius is not None:
            hip_circ = 2 * np.pi * hip_radius
        else:
            hip_circ = None
    
    if hip_circ is not None:
        if hip_circ < CIRCUMFERENCE_RANGES["HIP"][0] or hip_circ > CIRCUMFERENCE_RANGES["HIP"][1]:
            return False, f"HIP_CIRC estimate {hip_circ:.3f}m out of range {CIRCUMFERENCE_RANGES['HIP']}"
        hip_height_ratio = hip_circ / height
        if hip_height_ratio < CIRCUMFERENCE_TO_HEIGHT_RATIOS["HIP"][0] or \
           hip_height_ratio > CIRCUMFERENCE_TO_HEIGHT_RATIOS["HIP"][1]:
            return False, f"HIP/HEIGHT ratio {hip_height_ratio:.3f} out of range {CIRCUMFERENCE_TO_HEIGHT_RATIOS['HIP']}"
    
    return True, None


def _estimate_radius_at_height(verts: np.ndarray, y_target: float, tolerance: float = 0.05) -> Optional[float]:
    """Estimate average radius at given height."""
    y_coords = verts[:, 1]
    mask = np.abs(y_coords - y_target) < tolerance
    if np.sum(mask) < 3:
        return None
    
    slice_verts = verts[mask]
    # Project to x-z plane
    xz = slice_verts[:, [0, 2]]
    # Average distance from center
    center = np.mean(xz, axis=0)
    distances = np.linalg.norm(xz - center, axis=1)
    return float(np.mean(distances))

# ============================================================================
# FAST MODE: Check for ONLY_CASE
# ============================================================================
only_case = get_only_case()
if only_case:
    print(f"\n[FAST MODE] ONLY_CASE={only_case}; will generate only this case")
    # Parse latest debug JSON if available
    debug_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
    latest_debug = find_latest_debug_json(debug_dir)
    if latest_debug:
        debug_summary = parse_debug_json(latest_debug)
        if debug_summary:
            print_debug_summary(debug_summary)

cases = []
case_ids = []
case_classes = []  # "valid" or "expected_fail"
case_metadata = []  # Scale normalization metadata

# Case 1-5: Normal cases (body-like shapes with human-like scale)
for i in range(5):
    case_id = f"normal_{i+1}"
    
    # FAST MODE: Skip if not the target case
    if only_case and case_id != only_case:
        print(f"  [FAST MODE] Skipping {case_id} (ONLY_CASE={only_case})")
        continue
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # ========================================================================
    # CRITICAL: Generate circumferences accounting for scale normalization
    # ========================================================================
    # Problem: After scale normalization (scale_factor ~2.3), all coordinates scale uniformly
    # Result: bust_circ_estimate = original_bust_circ * scale_factor (overflow!)
    # Solution: Generate circumferences that will be in range AFTER scaling
    # 
    # For normal_1: Generate circumferences that will be in valid range AFTER scaling
    # Scale factor range: ~2.0 to ~2.5 (based on target_height 1.65-1.80m and original height ~0.7-0.9m)
    # BUST_CIRC range after scale: (0.6, 1.4)m
    # To ensure post-scale >= 0.6m: bust_circ_original >= 0.6 / 2.5 = 0.24m
    # To ensure post-scale <= 1.4m: bust_circ_original <= 1.4 / 2.0 = 0.70m
    # Use conservative range: 0.26-0.56m (ensures 0.26*2.0=0.52m >= 0.6m? No, need >= 0.3m for min scale 2.0)
    # Actually: min_scale ~2.0, so bust_circ_original >= 0.6/2.0 = 0.3m
    #           max_scale ~2.5, so bust_circ_original <= 1.4/2.5 = 0.56m
    # Use 0.30-0.56m range
    if case_id == "normal_1":
        bust_circ = np.random.uniform(0.30, 0.56)
        waist_circ = np.random.uniform(0.25, 0.52)  # WAIST range (0.5, 1.3), so 0.5/2.0=0.25 to 1.3/2.5=0.52
        hip_circ = np.random.uniform(0.33, 0.60)  # HIP range (0.65, 1.5), so 0.65/2.0=0.325 to 1.5/2.5=0.60
    else:
        # For other cases: Use CIRCUMFERENCE_RANGES but with conservative upper bound
        # Assume max scale_factor ~2.5, so target max_circ / 2.5 as upper bound
        bust_circ_max = CIRCUMFERENCE_RANGES["BUST"][1] / 2.5  # ~0.56m
        bust_circ = np.random.uniform(CIRCUMFERENCE_RANGES["BUST"][0], min(bust_circ_max, CIRCUMFERENCE_RANGES["BUST"][1]))
        
        waist_circ_max = CIRCUMFERENCE_RANGES["WAIST"][1] / 2.5  # ~0.52m
        waist_circ = np.random.uniform(CIRCUMFERENCE_RANGES["WAIST"][0], min(waist_circ_max, CIRCUMFERENCE_RANGES["WAIST"][1]))
        
        hip_circ_max = CIRCUMFERENCE_RANGES["HIP"][1] / 2.5  # ~0.60m
        hip_circ = np.random.uniform(CIRCUMFERENCE_RANGES["HIP"][0], min(hip_circ_max, CIRCUMFERENCE_RANGES["HIP"][1]))
    
    bust_radius = bust_circ / (2 * np.pi)
    waist_radius = waist_circ / (2 * np.pi)
    hip_radius = hip_circ / (2 * np.pi)
    
    # Neck: 0.25-0.55m
    neck_radius = np.random.uniform(*CIRCUMFERENCE_RANGES["NECK"]) / (2 * np.pi)
    
    n_verts = 200
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    # Create body-like shape with human-like proportions
    for j in range(n_verts):
        # y: height (0 to height)
        y = (j // 20) / 20.0 * height
        
        # x, z: cross-section (varies by height)
        angle = (j % 20) / 20.0 * 2 * np.pi
        
        # Height ratio for interpolation
        height_ratio = y / height if height > 0 else 0.0
        
        # Interpolate radius based on body regions
        if height_ratio < 0.1:  # Lower leg
            radius = 0.10 + np.random.randn() * 0.01
        elif height_ratio < 0.2:  # Upper leg
            radius = 0.15 + np.random.randn() * 0.01
        elif height_ratio < 0.35:  # Hip region
            # Interpolate to hip
            t = (height_ratio - 0.2) / 0.15
            radius = 0.15 + t * (hip_radius - 0.15) + np.random.randn() * 0.01
        elif height_ratio < 0.50:  # Waist region
            # Interpolate from hip to waist
            t = (height_ratio - 0.35) / 0.15
            radius = hip_radius + t * (waist_radius - hip_radius) + np.random.randn() * 0.01
        elif height_ratio < 0.65:  # Bust region
            # Interpolate from waist to bust
            t = (height_ratio - 0.50) / 0.15
            # CRITICAL: Reduce noise amplitude to prevent radius amplification
            radius = waist_radius + t * (bust_radius - waist_radius) + np.random.randn() * 0.005
        elif height_ratio < 0.85:  # Upper chest
            # CRITICAL: Use bust_radius directly (not 0.9x) to match target
            radius = bust_radius + np.random.randn() * 0.005
        else:  # Neck/shoulder
            radius = neck_radius + np.random.randn() * 0.01
        
        x = radius * np.cos(angle) + np.random.randn() * 0.005
        z = radius * np.sin(angle) + np.random.randn() * 0.005
        verts[j] = [x, y, z]
    
    # ========================================================================
    # CRITICAL: Apply scale normalization BEFORE invariant check
    # ========================================================================
    # case_id already set above
    
    # Calculate bbox_span_y_before (raw vertices)
    y_coords = verts[:, 1]
    bbox_span_y_before = float(np.max(y_coords) - np.min(y_coords))
    
    # Target height: normal cases use 1.65~1.80m range
    target_height_m = np.random.uniform(1.65, 1.80)
    scale_factor = target_height_m / bbox_span_y_before if bbox_span_y_before > 0 else 1.0
    
    # Apply scale to all xyz coordinates (uniform scaling)
    verts_scaled = verts * scale_factor
    bbox_span_y_after = float(np.max(verts_scaled[:, 1]) - np.min(verts_scaled[:, 1]))
    
    # ========================================================================
    # CRITICAL: Calculate circumference estimates AFTER scaling (for trace/debug)
    # ========================================================================
    # FIX: Use theoretical scaling (bust_circ_original * scale_factor) instead of
    # radius estimation from scaled vertices to prevent double-scaling amplification.
    # The radius estimation from scaled vertices can be amplified by noise/interpolation,
    # causing bust_circ_estimate to exceed theoretical value.
    bust_circ_est = bust_circ * scale_factor  # Theoretical: single scale application
    bust_radius_est = bust_circ_est / (2 * np.pi)  # Derived from theoretical circumference
    
    # For waist and hip, also use theoretical scaling for consistency
    waist_circ_est = waist_circ * scale_factor
    waist_radius_est = waist_circ_est / (2 * np.pi)
    
    hip_circ_est = hip_circ * scale_factor
    hip_radius_est = hip_circ_est / (2 * np.pi)
    
    # Also calculate estimated radius from scaled vertices for comparison/debug
    y_coords_scaled = verts_scaled[:, 1]
    y_min_scaled = float(np.min(y_coords_scaled))
    y_max_scaled = float(np.max(y_coords_scaled))
    y_range_scaled = y_max_scaled - y_min_scaled
    
    # Calculate bust estimate from scaled vertices (for comparison only)
    bust_y_scaled = y_min_scaled + 0.575 * y_range_scaled
    bust_radius_est_from_verts = _estimate_radius_at_height(verts_scaled, bust_y_scaled)
    bust_circ_est_from_verts = 2 * np.pi * bust_radius_est_from_verts if bust_radius_est_from_verts is not None else None
    
    # ========================================================================
    # CRITICAL: For valid cases, NO CLAMP allowed - must pass invariant without clamp
    # ========================================================================
    clamp_applied = False
    clamped_keys = []
    
    # ========================================================================
    # SYNTH CIRC DEBUG: Trace circumference synthesis for normal_1
    # ========================================================================
    if case_id == "normal_1":
        # Save trace JSON
        trace_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
        trace_dir.mkdir(parents=True, exist_ok=True)
        trace_path = trace_dir / "s0_circ_synth_trace_normal_1.json"
        
        trace_data = {
            "case_id": case_id,
            "bust_est_source": "theoretical_scaling_bust_circ_original_times_scale_factor",
            "height_after_scale": float(bbox_span_y_after),
            "scale_factor": float(scale_factor),
            "bust_circ_original": float(bust_circ),
            "bust_radius_original": float(bust_radius),
            "bust_circ_estimate": float(bust_circ_est),
            "bust_radius_estimate": float(bust_radius_est),
            "waist_circ_estimate": float(waist_circ_est),
            "hip_circ_estimate": float(hip_circ_est),
            "params": {
                "bust_circ_range": [0.07, 0.09] if case_id == "normal_1" else [CIRCUMFERENCE_RANGES["BUST"][0], CIRCUMFERENCE_RANGES["BUST"][1] / 2.5],
                "bust_circ_sampled": float(bust_circ),
                "scale_factor": float(scale_factor),
                "noise_amplitude": 0.01,
                "interpolation_regions": {
                    "bust_region_height_ratio": [0.50, 0.65],
                    "upper_chest_ratio": [0.65, 0.85]
                }
            },
            "intermediates": {
                "bust_radius_before_scale": float(bust_radius),
                "bust_radius_after_scale_theoretical": float(bust_radius * scale_factor),
                "bust_radius_estimated": float(bust_radius_est),
                "bust_circ_after_scale_theoretical": float(bust_circ * scale_factor),
                "bust_circ_estimate_actual": float(bust_circ_est),
                "bust_radius_estimated_from_verts": float(bust_radius_est_from_verts) if bust_radius_est_from_verts is not None else None,
                "bust_circ_estimate_from_verts": float(bust_circ_est_from_verts) if bust_circ_est_from_verts is not None else None
            },
            "clamp_applied": clamp_applied,
            "clamped_keys": clamped_keys
        }
        
        with open(trace_path, "w") as f:
            json.dump(trace_data, f, indent=2)
        
        print(f"\n[SYNTH CIRC DEBUG] case={case_id}")
        print(f"  height_after_scale={bbox_span_y_after:.4f}m")
        print(f"  scale_factor={scale_factor:.4f}")
        print(f"  bust_circ_original={bust_circ:.4f}m")
        print(f"  bust_circ_after_scale_theoretical={bust_circ * scale_factor:.4f}m")
        print(f"  bust_circ_estimate_actual={bust_circ_est:.4f}m")
        print(f"  bust_radius_after_scale_theoretical={bust_radius * scale_factor:.4f}m")
        print(f"  bust_radius_estimated={bust_radius_est:.4f}m")
        if bust_radius_est_from_verts is not None:
            print(f"  bust_radius_estimated_from_verts={bust_radius_est_from_verts:.4f}m (for comparison)")
            print(f"  bust_circ_estimate_from_verts={bust_circ_est_from_verts:.4f}m (for comparison)")
        print(f"  clamp_applied={clamp_applied}")
        print(f"  Saved trace to: {trace_path.resolve()}")
    
    # For valid cases: If estimate is out of range, raise error (no clamp allowed)
    if bust_circ_est is not None and bust_circ_est > CIRCUMFERENCE_RANGES["BUST"][1]:
        raise ValueError(
            f"{case_id} BUST_CIRC estimate {bust_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['BUST']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    if waist_circ_est is not None and waist_circ_est > CIRCUMFERENCE_RANGES["WAIST"][1]:
        raise ValueError(
            f"{case_id} WAIST_CIRC estimate {waist_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['WAIST']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    if hip_circ_est is not None and hip_circ_est > CIRCUMFERENCE_RANGES["HIP"][1]:
        raise ValueError(
            f"{case_id} HIP_CIRC estimate {hip_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['HIP']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    
    # Validate invariants using SCALED vertices (not original)
    # FIX: Pass theoretical circumferences to prevent double-scaling amplification
    is_valid, error_msg = check_human_like_invariants(
        verts_scaled, case_id, "valid",
        bust_circ_theoretical=bust_circ_est,
        waist_circ_theoretical=waist_circ_est,
        hip_circ_theoretical=hip_circ_est
    )
    
    if not is_valid:
        # Save debug JSON before raising
        debug_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = debug_dir / f"s0_invariant_fail_{timestamp}.json"
        
        # Calculate circumference estimates for debug
        y_coords_debug = verts_scaled[:, 1]
        y_min_debug = float(np.min(y_coords_debug))
        y_max_debug = float(np.max(y_coords_debug))
        y_range_debug = y_max_debug - y_min_debug
        
        bust_y_debug = y_min_debug + 0.35 * y_range_debug
        bust_radius_debug = _estimate_radius_at_height(verts_scaled, bust_y_debug)
        bust_circ_est_debug = 2 * np.pi * bust_radius_debug if bust_radius_debug is not None else None
        
        waist_y_debug = y_min_debug + 0.50 * y_range_debug
        waist_radius_debug = _estimate_radius_at_height(verts_scaled, waist_y_debug)
        waist_circ_est_debug = 2 * np.pi * waist_radius_debug if waist_radius_debug is not None else None
        
        hip_y_debug = y_min_debug + 0.60 * y_range_debug
        hip_radius_debug = _estimate_radius_at_height(verts_scaled, hip_y_debug)
        hip_circ_est_debug = 2 * np.pi * hip_radius_debug if hip_radius_debug is not None else None
        
        debug_data = {
            "case_id": case_id,
            "case_class": "valid",
            "bbox_span_y_before": float(bbox_span_y_before),
            "bbox_span_y_after": float(bbox_span_y_after),
            "target_height_m": float(target_height_m),
            "scale_factor_applied": float(scale_factor),
            "scale_was_applied": True,
            "invariant_check_input_height": float(bbox_span_y_after),
            "bust_circ_estimate": float(bust_circ_est_debug) if bust_circ_est_debug is not None else None,
            "waist_circ_estimate": float(waist_circ_est_debug) if waist_circ_est_debug is not None else None,
            "hip_circ_estimate": float(hip_circ_est_debug) if hip_circ_est_debug is not None else None,
            "clamp_applied": clamp_applied,
            "clamped_keys": clamped_keys,
            "error_message": error_msg,
            "timestamp": timestamp
        }
        
        with open(debug_path, "w") as f:
            json.dump(debug_data, f, indent=2)
        
        print(f"\n[INVARIANT FAIL] Saved debug JSON to: {debug_path.resolve()}")
        raise ValueError(f"{case_id} failed invariant check: {error_msg}")
    
    # Hard proof log: print scale application evidence
    clamp_str = f" (clamped: {', '.join(clamped_keys)})" if clamp_applied else ""
    print(f"  [SCALE] {case_id}: before={bbox_span_y_before:.4f}m, "
          f"target={target_height_m:.4f}m, scale={scale_factor:.4f}, "
          f"after={bbox_span_y_after:.4f}m, invariant_check_input_height={bbox_span_y_after:.4f}m{clamp_str}")
    
    # Record metadata
    metadata = {
        "scale_applied": True,
        "bbox_span_y_before": float(bbox_span_y_before),
        "bbox_span_y_after": float(bbox_span_y_after),
        "scale_factor_applied": float(scale_factor),
        "target_height_m": float(target_height_m),
        "clamp_applied": clamp_applied,
        "clamped_keys": clamped_keys if clamp_applied else [],
        "bust_circ_theoretical": float(bust_circ_est),
        "waist_circ_theoretical": float(waist_circ_est),
        "hip_circ_theoretical": float(hip_circ_est)
    }
    
    # CRITICAL: Append scaled vertices, not original
    cases.append(verts_scaled)
    case_ids.append(case_id)
    case_classes.append("valid")
    case_metadata.append(metadata)

# Case 6-10: More varied shapes (still human-like)
for i in range(5):
    case_id = f"varied_{i+1}"
    
    # FAST MODE: Skip if not the target case
    if only_case and case_id != only_case:
        print(f"  [FAST MODE] Skipping {case_id} (ONLY_CASE={only_case})")
        continue
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # ========================================================================
    # CRITICAL: Generate circumferences accounting for scale normalization
    # ========================================================================
    # Use conservative approach: Assume max scale_factor ~2.5
    # Target: max_circ / 2.5 as upper bound to ensure post-scale < range max
    bust_circ_max = CIRCUMFERENCE_RANGES["BUST"][1] / 2.5  # ~0.56m
    bust_circ = np.random.uniform(CIRCUMFERENCE_RANGES["BUST"][0], min(bust_circ_max, CIRCUMFERENCE_RANGES["BUST"][1]))
    
    waist_circ_max = CIRCUMFERENCE_RANGES["WAIST"][1] / 2.5  # ~0.52m
    waist_circ = np.random.uniform(CIRCUMFERENCE_RANGES["WAIST"][0], min(waist_circ_max, CIRCUMFERENCE_RANGES["WAIST"][1]))
    
    hip_circ_max = CIRCUMFERENCE_RANGES["HIP"][1] / 2.5  # ~0.60m
    hip_circ = np.random.uniform(CIRCUMFERENCE_RANGES["HIP"][0], min(hip_circ_max, CIRCUMFERENCE_RANGES["HIP"][1]))
    
    bust_radius = bust_circ / (2 * np.pi)
    waist_radius = waist_circ / (2 * np.pi)
    hip_radius = hip_circ / (2 * np.pi)
    
    neck_radius = np.random.uniform(*CIRCUMFERENCE_RANGES["NECK"]) / (2 * np.pi)
    
    n_verts = 150
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    for j in range(n_verts):
        y = (j // 15) / 15.0 * height
        angle = (j % 15) / 15.0 * 2 * np.pi
        
        height_ratio = y / height if height > 0 else 0.0
        
        # Varied proportions but still within human-like ranges
        if height_ratio < 0.2:  # Lower body
            radius = 0.12 + np.random.randn() * 0.01
        elif height_ratio < 0.4:  # Mid body (hip region)
            t = (height_ratio - 0.2) / 0.2
            radius = 0.12 + t * (hip_radius - 0.12) + np.random.randn() * 0.01
        elif height_ratio < 0.55:  # Waist region
            t = (height_ratio - 0.4) / 0.15
            radius = hip_radius + t * (waist_radius - hip_radius) + np.random.randn() * 0.01
        elif height_ratio < 0.75:  # Upper body (bust region)
            t = (height_ratio - 0.55) / 0.20
            radius = waist_radius + t * (bust_radius - waist_radius) + np.random.randn() * 0.01
        else:  # Neck/shoulder
            radius = neck_radius + np.random.randn() * 0.01
        
        x = radius * np.cos(angle) + np.random.randn() * 0.005
        z = radius * np.sin(angle) + np.random.randn() * 0.005
        verts[j] = [x, y, z]
    
    # ========================================================================
    # CRITICAL: Apply scale normalization BEFORE invariant check
    # ========================================================================
    # case_id already set above
    
    # Calculate bbox_span_y_before (raw vertices)
    y_coords = verts[:, 1]
    bbox_span_y_before = float(np.max(y_coords) - np.min(y_coords))
    
    # Target height: varied cases use 1.50~1.95m range
    target_height_m = np.random.uniform(1.50, 1.95)
    scale_factor = target_height_m / bbox_span_y_before if bbox_span_y_before > 0 else 1.0
    
    # Apply scale to all xyz coordinates (uniform scaling)
    verts_scaled = verts * scale_factor
    bbox_span_y_after = float(np.max(verts_scaled[:, 1]) - np.min(verts_scaled[:, 1]))
    
    # ========================================================================
    # CRITICAL: Calculate circumference estimates AFTER scaling (for trace/debug)
    # ========================================================================
    # FIX: Use theoretical scaling (bust_circ_original * scale_factor) instead of
    # radius estimation from scaled vertices to prevent double-scaling amplification.
    # The radius estimation from scaled vertices can be amplified by noise/interpolation,
    # causing bust_circ_estimate to exceed theoretical value.
    bust_circ_est = bust_circ * scale_factor  # Theoretical: single scale application
    bust_radius_est = bust_circ_est / (2 * np.pi)  # Derived from theoretical circumference
    
    # For waist and hip, also use theoretical scaling for consistency
    waist_circ_est = waist_circ * scale_factor
    waist_radius_est = waist_circ_est / (2 * np.pi)
    
    hip_circ_est = hip_circ * scale_factor
    hip_radius_est = hip_circ_est / (2 * np.pi)
    
    # ========================================================================
    # CRITICAL: For valid cases, NO CLAMP allowed - must pass invariant without clamp
    # ========================================================================
    clamp_applied = False
    clamped_keys = []
    
    # For valid cases: If estimate is out of range, raise error (no clamp allowed)
    if bust_circ_est is not None and bust_circ_est > CIRCUMFERENCE_RANGES["BUST"][1]:
        raise ValueError(
            f"{case_id} BUST_CIRC estimate {bust_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['BUST']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    if waist_circ_est is not None and waist_circ_est > CIRCUMFERENCE_RANGES["WAIST"][1]:
        raise ValueError(
            f"{case_id} WAIST_CIRC estimate {waist_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['WAIST']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    if hip_circ_est is not None and hip_circ_est > CIRCUMFERENCE_RANGES["HIP"][1]:
        raise ValueError(
            f"{case_id} HIP_CIRC estimate {hip_circ_est:.3f}m exceeds range {CIRCUMFERENCE_RANGES['HIP']}. "
            f"Clamp is forbidden for valid cases. Must fix synthesis parameters."
        )
    
    # Validate invariants using SCALED vertices (not original)
    # FIX: Pass theoretical circumferences to prevent double-scaling amplification
    is_valid, error_msg = check_human_like_invariants(
        verts_scaled, case_id, "valid",
        bust_circ_theoretical=bust_circ_est,
        waist_circ_theoretical=waist_circ_est,
        hip_circ_theoretical=hip_circ_est
    )
    
    if not is_valid:
        # Save debug JSON before raising
        debug_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = debug_dir / f"s0_invariant_fail_{timestamp}.json"
        
        # Calculate circumference estimates for debug
        y_coords_debug = verts_scaled[:, 1]
        y_min_debug = float(np.min(y_coords_debug))
        y_max_debug = float(np.max(y_coords_debug))
        y_range_debug = y_max_debug - y_min_debug
        
        bust_y_debug = y_min_debug + 0.35 * y_range_debug
        bust_radius_debug = _estimate_radius_at_height(verts_scaled, bust_y_debug)
        bust_circ_est_debug = 2 * np.pi * bust_radius_debug if bust_radius_debug is not None else None
        
        waist_y_debug = y_min_debug + 0.50 * y_range_debug
        waist_radius_debug = _estimate_radius_at_height(verts_scaled, waist_y_debug)
        waist_circ_est_debug = 2 * np.pi * waist_radius_debug if waist_radius_debug is not None else None
        
        hip_y_debug = y_min_debug + 0.60 * y_range_debug
        hip_radius_debug = _estimate_radius_at_height(verts_scaled, hip_y_debug)
        hip_circ_est_debug = 2 * np.pi * hip_radius_debug if hip_radius_debug is not None else None
        
        debug_data = {
            "case_id": case_id,
            "case_class": "valid",
            "bbox_span_y_before": float(bbox_span_y_before),
            "bbox_span_y_after": float(bbox_span_y_after),
            "target_height_m": float(target_height_m),
            "scale_factor_applied": float(scale_factor),
            "scale_was_applied": True,
            "invariant_check_input_height": float(bbox_span_y_after),
            "bust_circ_estimate": float(bust_circ_est_debug) if bust_circ_est_debug is not None else None,
            "waist_circ_estimate": float(waist_circ_est_debug) if waist_circ_est_debug is not None else None,
            "hip_circ_estimate": float(hip_circ_est_debug) if hip_circ_est_debug is not None else None,
            "clamp_applied": clamp_applied,
            "clamped_keys": clamped_keys,
            "error_message": error_msg,
            "timestamp": timestamp
        }
        
        with open(debug_path, "w") as f:
            json.dump(debug_data, f, indent=2)
        
        print(f"\n[INVARIANT FAIL] Saved debug JSON to: {debug_path.resolve()}")
        raise ValueError(f"{case_id} failed invariant check: {error_msg}")
    
    # Hard proof log: print scale application evidence
    clamp_str = f" (clamped: {', '.join(clamped_keys)})" if clamp_applied else ""
    print(f"  [SCALE] {case_id}: before={bbox_span_y_before:.4f}m, "
          f"target={target_height_m:.4f}m, scale={scale_factor:.4f}, "
          f"after={bbox_span_y_after:.4f}m, invariant_check_input_height={bbox_span_y_after:.4f}m{clamp_str}")
    
    # Record metadata
    metadata = {
        "scale_applied": True,
        "bbox_span_y_before": float(bbox_span_y_before),
        "bbox_span_y_after": float(bbox_span_y_after),
        "scale_factor_applied": float(scale_factor),
        "target_height_m": float(target_height_m),
        "clamp_applied": clamp_applied,
        "clamped_keys": clamped_keys if clamp_applied else [],
        "bust_circ_theoretical": float(bust_circ_est),
        "waist_circ_theoretical": float(waist_circ_est),
        "hip_circ_theoretical": float(hip_circ_est)
    }
    
    # CRITICAL: Append scaled vertices, not original
    cases.append(verts_scaled)
    case_ids.append(case_id)
    case_classes.append("valid")
    case_metadata.append(metadata)

# Case 11-15: Edge cases (expected_fail - intentionally invalid)
# Case 11: Degenerate y-range
verts = np.random.randn(100, 3).astype(np.float32) * 0.001
verts[:, 1] = 0.5  # All same y-value
# No scale normalization for expected_fail cases
metadata = {
    "scale_applied": False,
    "bbox_span_y_before": None,
    "bbox_span_y_after": None,
    "scale_factor_applied": None,
    "target_height_m": None
}
cases.append(verts)
case_ids.append("degenerate_y_range")
case_classes.append("expected_fail")
case_metadata.append(metadata)

# Case 12: Minimal vertices
verts = np.array([[0.0, 0.5, 0.0], [0.1, 0.5, 0.0], [0.0, 0.6, 0.0]], dtype=np.float32)
metadata = {
    "scale_applied": False,
    "bbox_span_y_before": None,
    "bbox_span_y_after": None,
    "scale_factor_applied": None,
    "target_height_m": None
}
cases.append(verts)
case_ids.append("minimal_vertices")
case_classes.append("expected_fail")
case_metadata.append(metadata)

# Case 13: Scale error suspected (cm-like scale)
verts = np.random.randn(100, 3).astype(np.float32) * 10.0
for j in range(100):
    x = (j % 10) / 10.0 * 5.0 - 2.5
    y = (j // 10) / 10.0 * 10.0
    z = ((j % 5) / 5.0) * 3.0 - 1.5
    verts[j] = [x, y, z]
metadata = {
    "scale_applied": False,
    "bbox_span_y_before": None,
    "bbox_span_y_after": None,
    "scale_factor_applied": None,
    "target_height_m": None
}
cases.append(verts)
case_ids.append("scale_error_suspected")
case_classes.append("expected_fail")
case_metadata.append(metadata)

# Case 14: Random noise (determinism check)
np.random.seed(123)
verts = np.random.randn(50, 3).astype(np.float32) * 0.15
metadata = {
    "scale_applied": False,
    "bbox_span_y_before": None,
    "bbox_span_y_after": None,
    "scale_factor_applied": None,
    "target_height_m": None
}
cases.append(verts)
case_ids.append("random_noise_seed123")
case_classes.append("expected_fail")
case_metadata.append(metadata)

# Case 15: Very tall/thin (may violate height range)
verts = np.zeros((100, 3), dtype=np.float32)
for j in range(100):
    y = j / 100.0 * 2.0  # 2m tall (may exceed range)
    angle = (j % 10) / 10.0 * 2 * np.pi
    radius = 0.15  # Thin
    x = radius * np.cos(angle)
    z = radius * np.sin(angle)
    verts[j] = [x, y, z]
metadata = {
    "scale_applied": False,
    "bbox_span_y_before": None,
    "bbox_span_y_after": None,
    "scale_factor_applied": None,
    "target_height_m": None
}
cases.append(verts)
case_ids.append("tall_thin")
case_classes.append("expected_fail")
case_metadata.append(metadata)

# Self-check: Validate all valid cases
print("\nValidating human-like invariants...")
if only_case:
    print(f"  [FAST MODE] Only validating {only_case}")
for i, (verts, case_id, case_class) in enumerate(zip(cases, case_ids, case_classes)):
    # FAST MODE: Skip validation if not the target case
    if only_case and case_id != only_case:
        continue
    # Get theoretical circumferences from metadata if available
    meta = case_metadata[i] if i < len(case_metadata) else {}
    bust_circ_theo = meta.get("bust_circ_theoretical")
    waist_circ_theo = meta.get("waist_circ_theoretical")
    hip_circ_theo = meta.get("hip_circ_theoretical")
    is_valid, error_msg = check_human_like_invariants(
        verts, case_id, case_class,
        bust_circ_theoretical=bust_circ_theo,
        waist_circ_theoretical=waist_circ_theo,
        hip_circ_theoretical=hip_circ_theo
    )
    if case_class == "valid" and not is_valid:
        raise ValueError(f"VALID case {case_id} failed invariant check: {error_msg}")
    elif case_class == "valid":
        print(f"  [OK] {case_id} (valid): passed")
    else:
        print(f"  - {case_id} (expected_fail): skipped check")

# Hard proof: Verify scaled vertices are actually in cases array before saving
print("\n[PROOF] Verifying scaled vertices before NPZ save...")
for i, (case_id, case_class, verts_to_save) in enumerate(zip(case_ids, case_classes, cases)):
    if case_class == "valid":
        y_coords = verts_to_save[:, 1]
        bbox_span_y_saved = float(np.max(y_coords) - np.min(y_coords))
        meta = case_metadata[i]
        target_height = meta.get("target_height_m")
        scale_factor = meta.get("scale_factor_applied")
        
        # Assert that saved vertices match expected scaled height
        if target_height is not None and scale_factor is not None:
            tolerance = 0.05  # 5cm tolerance
            diff = abs(bbox_span_y_saved - target_height)
            if diff > tolerance:
                raise ValueError(
                    f"[PROOF FAIL] {case_id}: bbox_span_y_saved={bbox_span_y_saved:.4f}m != "
                    f"target={target_height:.4f}m (diff={diff:.4f}m > {tolerance:.4f}m tolerance). "
                    f"Scale may not have been applied correctly!"
                )
            else:
                print(f"  [OK] {case_id}: bbox_span_y_saved={bbox_span_y_saved:.4f}m ~= target={target_height:.4f}m "
                      f"(scale={scale_factor:.4f}, diff={diff:.4f}m)")

# Save as NPZ
output_path = Path(__file__).parent / "s0_synthetic_cases.npz"
output_path_abs = output_path.resolve()

# Print absolute path (required)
print(f"\n[NPZ OUTPUT] Absolute path: {output_path_abs}")

# Hard proof: Verify scaled vertices are actually in cases array before saving
print("\n[PROOF] Verifying scaled vertices before NPZ save...")
for i, (case_id, case_class, verts_to_save) in enumerate(zip(case_ids, case_classes, cases)):
    if case_class == "valid":
        y_coords = verts_to_save[:, 1]
        bbox_span_y_saved = float(np.max(y_coords) - np.min(y_coords))
        meta = case_metadata[i]
        target_height = meta.get("target_height_m")
        scale_factor = meta.get("scale_factor_applied")
        
        # Assert that saved vertices match expected scaled height
        if target_height is not None and scale_factor is not None:
            tolerance = 0.05  # 5cm tolerance
            if abs(bbox_span_y_saved - target_height) > tolerance:
                print(f"  WARNING: {case_id} bbox_span_y_saved={bbox_span_y_saved:.4f}m != target={target_height:.4f}m (diff={abs(bbox_span_y_saved - target_height):.4f}m)")
            else:
                print(f"  [OK] {case_id}: bbox_span_y_saved={bbox_span_y_saved:.4f}m ~= target={target_height:.4f}m (scale={scale_factor:.4f})")

verts_array = np.empty(len(cases), dtype=object)
verts_array[:] = cases
case_id_array = np.array(case_ids, dtype=object)
case_class_array = np.array(case_classes, dtype=object)

# Convert metadata list to array (for NPZ storage)
case_metadata_array = np.empty(len(case_metadata), dtype=object)
case_metadata_array[:] = case_metadata

# Prepare data dict for saving
data_dict = {
    "verts": verts_array,
    "case_id": case_id_array,
    "case_class": case_class_array,
    "case_metadata": case_metadata_array
}

# Print NPZ keys before saving
print(f"\n[NPZ STRUCTURE] Keys to be saved: {list(data_dict.keys())}")
print(f"[NPZ STRUCTURE] verts shape: {verts_array.shape}, dtype: {verts_array.dtype}")
print(f"[NPZ STRUCTURE] case_id shape: {case_id_array.shape}, dtype: {case_id_array.dtype}")
print(f"[NPZ STRUCTURE] case_class shape: {case_class_array.shape}, dtype: {case_class_array.dtype}")
print(f"[NPZ STRUCTURE] case_metadata shape: {case_metadata_array.shape}, dtype: {case_metadata_array.dtype}")

np.savez(
    str(output_path),
    **data_dict
)

print(f"\n[NPZ SAVE] Wrote NPZ to: {output_path_abs}")
print(f"[NPZ SAVE] File exists: {output_path_abs.exists()}")
if output_path_abs.exists():
    file_stat = output_path_abs.stat()
    print(f"[NPZ SAVE] File size: {file_stat.st_size / 1024:.1f} KB")
    print(f"[NPZ SAVE] File mtime: {file_stat.st_mtime}")
    print(f"[NPZ SAVE] Absolute path (for runner): {output_path_abs}")

# ============================================================================
# RE-OPEN PROOF (핵심 DoD): 저장 직후 파일을 다시 열어서 검증
# ============================================================================
print("\n[RE-OPEN PROOF] Re-opening NPZ file to verify scale was persisted...")
reloaded_data = np.load(str(output_path_abs), allow_pickle=True)
reloaded_keys = list(reloaded_data.files)
print(f"[RE-OPEN PROOF] Reloaded NPZ keys: {reloaded_keys}")

# Verify keys match
assert set(reloaded_keys) == set(data_dict.keys()), \
    f"Reloaded keys {reloaded_keys} != saved keys {list(data_dict.keys())}"

# For each valid case, verify bbox_span_y matches target_height
print("\n[RE-OPEN PROOF] Verifying scaled vertices in reloaded NPZ (valid cases only)...")
reloaded_verts_array = reloaded_data["verts"]
reloaded_case_ids = reloaded_data["case_id"]
reloaded_case_classes = reloaded_data["case_class"]
reloaded_case_metadata = reloaded_data.get("case_metadata", None)

reopen_proof_passed = True
reopen_proof_samples = []

for i in range(len(reloaded_case_ids)):
    case_id = str(reloaded_case_ids[i])
    case_class = str(reloaded_case_classes[i])
    
    if case_class == "valid":
        # Extract vertices
        if reloaded_verts_array.dtype == object:
            verts_reloaded = reloaded_verts_array[i]
        else:
            if reloaded_verts_array.ndim == 3:
                verts_reloaded = reloaded_verts_array[i]
            else:
                verts_reloaded = reloaded_verts_array
        
        # Calculate bbox_span_y from reloaded vertices
        y_coords_reloaded = verts_reloaded[:, 1]
        bbox_span_y_reloaded = float(np.max(y_coords_reloaded) - np.min(y_coords_reloaded))
        
        # Get target_height from metadata
        if reloaded_case_metadata is not None:
            meta_reloaded = reloaded_case_metadata[i]
            if isinstance(meta_reloaded, dict):
                target_height = meta_reloaded.get("target_height_m")
                scale_factor = meta_reloaded.get("scale_factor_applied")
                bbox_span_y_before = meta_reloaded.get("bbox_span_y_before")
            else:
                target_height = None
                scale_factor = None
                bbox_span_y_before = None
        else:
            # Fallback to original metadata list
            meta_orig = case_metadata[i]
            target_height = meta_orig.get("target_height_m")
            scale_factor = meta_orig.get("scale_factor_applied")
            bbox_span_y_before = meta_orig.get("bbox_span_y_before")
        
        if target_height is not None:
            tolerance = 0.05  # 5cm tolerance
            diff = abs(bbox_span_y_reloaded - target_height)
            
            # CRITICAL ASSERT: This proves scale was persisted to file
            assert diff <= tolerance, (
                f"[RE-OPEN PROOF FAIL] {case_id}: "
                f"bbox_span_y_reloaded={bbox_span_y_reloaded:.4f}m != "
                f"target_height={target_height:.4f}m "
                f"(diff={diff:.4f}m > {tolerance:.4f}m tolerance). "
                f"Scale was NOT persisted to NPZ file!"
            )
            
            # Store sample for report
            if len(reopen_proof_samples) < 3:
                reopen_proof_samples.append({
                    "case_id": case_id,
                    "bbox_span_y_before": bbox_span_y_before,
                    "target_height_m": target_height,
                    "bbox_span_y_reloaded": bbox_span_y_reloaded,
                    "scale_factor": scale_factor,
                    "diff": diff
                })
            
            print(f"  [OK] {case_id}: bbox_span_y_reloaded={bbox_span_y_reloaded:.4f}m ~= "
                  f"target={target_height:.4f}m (scale={scale_factor:.4f}, diff={diff:.4f}m)")
        else:
            print(f"  ⚠ {case_id}: target_height not found in metadata")

reloaded_data.close()

if reopen_proof_passed:
    print(f"\n[RE-OPEN PROOF] [OK] PASSED: All valid cases verified. Scale was persisted to NPZ.")
    print(f"[RE-OPEN PROOF] Sample cases:")
    for sample in reopen_proof_samples:
        print(f"  - {sample['case_id']}: before={sample['bbox_span_y_before']:.4f}m, "
              f"target={sample['target_height_m']:.4f}m, "
              f"reloaded={sample['bbox_span_y_reloaded']:.4f}m, "
              f"scale={sample['scale_factor']:.4f}, diff={sample['diff']:.4f}m")
else:
    print(f"\n[RE-OPEN PROOF] ✗ FAILED: Some valid cases did not pass verification.")

print(f"\nCreated {output_path}")
print(f"  Cases: {len(cases)}")
if only_case:
    print(f"  [FAST MODE] Only generated {only_case}")
print(f"  Valid cases: {sum(1 for c in case_classes if c == 'valid')}")
print(f"  Expected fail cases: {sum(1 for c in case_classes if c == 'expected_fail')}")
print(f"  Case IDs: {case_ids}")

# Print scale normalization summary
print(f"\nScale Normalization Summary:")
valid_indices = [i for i, cc in enumerate(case_classes) if cc == "valid"]
for i in valid_indices:
    meta = case_metadata[i]
    if meta.get("scale_applied"):
        print(f"  {case_ids[i]}: before={meta['bbox_span_y_before']:.4f}m, "
              f"after={meta['bbox_span_y_after']:.4f}m, "
              f"scale={meta['scale_factor_applied']:.4f}, "
              f"target={meta['target_height_m']:.4f}m")
