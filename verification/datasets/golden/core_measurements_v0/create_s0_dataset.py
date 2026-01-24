#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for core measurements v0 validation.

This script generates synthetic mesh cases with human-like scale invariants.
Valid cases (normal_*, varied_*) must satisfy physical plausibility constraints.
Expected fail cases (degenerate_*, etc.) are intentionally invalid for testing.
"""

import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Set seed for reproducibility
np.random.seed(42)

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
    case_class: str = "valid"
) -> Tuple[bool, Optional[str]]:
    """
    Check if mesh vertices satisfy human-like scale invariants.
    
    Args:
        verts: Mesh vertices (N, 3) in meters
        case_id: Case identifier
        case_class: "valid" or "expected_fail"
    
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
    bust_y = y_min + 0.35 * y_range
    bust_radius = _estimate_radius_at_height(verts, bust_y)
    if bust_radius is not None:
        bust_circ = 2 * np.pi * bust_radius
        if bust_circ < CIRCUMFERENCE_RANGES["BUST"][0] or bust_circ > CIRCUMFERENCE_RANGES["BUST"][1]:
            return False, f"BUST_CIRC estimate {bust_circ:.3f}m out of range {CIRCUMFERENCE_RANGES['BUST']}"
        bust_height_ratio = bust_circ / height
        if bust_height_ratio < CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"][0] or \
           bust_height_ratio > CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"][1]:
            return False, f"BUST/HEIGHT ratio {bust_height_ratio:.3f} out of range {CIRCUMFERENCE_TO_HEIGHT_RATIOS['BUST']}"
    
    # Check waist region (around 0.50 * height from bottom)
    waist_y = y_min + 0.50 * y_range
    waist_radius = _estimate_radius_at_height(verts, waist_y)
    if waist_radius is not None:
        waist_circ = 2 * np.pi * waist_radius
        if waist_circ < CIRCUMFERENCE_RANGES["WAIST"][0] or waist_circ > CIRCUMFERENCE_RANGES["WAIST"][1]:
            return False, f"WAIST_CIRC estimate {waist_circ:.3f}m out of range {CIRCUMFERENCE_RANGES['WAIST']}"
        waist_height_ratio = waist_circ / height
        if waist_height_ratio < CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"][0] or \
           waist_height_ratio > CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"][1]:
            return False, f"WAIST/HEIGHT ratio {waist_height_ratio:.3f} out of range {CIRCUMFERENCE_TO_HEIGHT_RATIOS['WAIST']}"
    
    # Check hip region (around 0.60 * height from bottom)
    hip_y = y_min + 0.60 * y_range
    hip_radius = _estimate_radius_at_height(verts, hip_y)
    if hip_radius is not None:
        hip_circ = 2 * np.pi * hip_radius
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

cases = []
case_ids = []
case_classes = []  # "valid" or "expected_fail"
case_metadata = []  # Scale normalization metadata

# Case 1-5: Normal cases (body-like shapes with human-like scale)
for i in range(5):
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # ========================================================================
    # CRITICAL: Generate circumferences using CIRCUMFERENCE_RANGES directly
    # to avoid scale-induced overflow (e.g., bust_circ > 1.4m after scaling)
    # ========================================================================
    # Use CIRCUMFERENCE_RANGES directly (not height-based ratios)
    # This ensures circumferences stay within human-like ranges even after scaling
    bust_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["BUST"])
    bust_radius = bust_circ / (2 * np.pi)
    
    waist_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["WAIST"])
    waist_radius = waist_circ / (2 * np.pi)
    
    hip_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["HIP"])
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
            radius = waist_radius + t * (bust_radius - waist_radius) + np.random.randn() * 0.01
        elif height_ratio < 0.85:  # Upper chest
            radius = bust_radius * 0.9 + np.random.randn() * 0.01
        else:  # Neck/shoulder
            radius = neck_radius + np.random.randn() * 0.01
        
        x = radius * np.cos(angle) + np.random.randn() * 0.005
        z = radius * np.sin(angle) + np.random.randn() * 0.005
        verts[j] = [x, y, z]
    
    # ========================================================================
    # CRITICAL: Apply scale normalization BEFORE invariant check
    # ========================================================================
    case_id = f"normal_{i+1}"
    
    # Calculate bbox_span_y_before (raw vertices)
    y_coords = verts[:, 1]
    bbox_span_y_before = float(np.max(y_coords) - np.min(y_coords))
    
    # Target height: normal cases use 1.65~1.80m range
    target_height_m = np.random.uniform(1.65, 1.80)
    scale_factor = target_height_m / bbox_span_y_before if bbox_span_y_before > 0 else 1.0
    
    # Apply scale to all xyz coordinates (uniform scaling)
    verts_scaled = verts * scale_factor
    bbox_span_y_after = float(np.max(verts_scaled[:, 1]) - np.min(verts_scaled[:, 1]))
    
    # Validate invariants using SCALED vertices (not original)
    is_valid, error_msg = check_human_like_invariants(verts_scaled, case_id, "valid")
    
    if not is_valid:
        # Save debug JSON before raising
        debug_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = debug_dir / f"s0_invariant_fail_{timestamp}.json"
        
        debug_data = {
            "case_id": case_id,
            "case_class": "valid",
            "bbox_span_y_before": float(bbox_span_y_before),
            "bbox_span_y_after": float(bbox_span_y_after),
            "target_height_m": float(target_height_m),
            "scale_factor_applied": float(scale_factor),
            "scale_was_applied": True,
            "invariant_check_input_height": float(bbox_span_y_after),
            "error_message": error_msg,
            "timestamp": timestamp
        }
        
        with open(debug_path, "w") as f:
            json.dump(debug_data, f, indent=2)
        
        print(f"\n[INVARIANT FAIL] Saved debug JSON to: {debug_path.resolve()}")
        raise ValueError(f"{case_id} failed invariant check: {error_msg}")
    
    # Hard proof log: print scale application evidence
    print(f"  [SCALE] {case_id}: before={bbox_span_y_before:.4f}m, "
          f"target={target_height_m:.4f}m, scale={scale_factor:.4f}, "
          f"after={bbox_span_y_after:.4f}m, invariant_check_input_height={bbox_span_y_after:.4f}m")
    
    # Record metadata
    metadata = {
        "scale_applied": True,
        "bbox_span_y_before": float(bbox_span_y_before),
        "bbox_span_y_after": float(bbox_span_y_after),
        "scale_factor_applied": float(scale_factor),
        "target_height_m": float(target_height_m)
    }
    
    # CRITICAL: Append scaled vertices, not original
    cases.append(verts_scaled)
    case_ids.append(case_id)
    case_classes.append("valid")
    case_metadata.append(metadata)

# Case 6-10: More varied shapes (still human-like)
for i in range(5):
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # ========================================================================
    # CRITICAL: Generate circumferences using CIRCUMFERENCE_RANGES directly
    # to avoid scale-induced overflow (e.g., bust_circ > 1.4m after scaling)
    # ========================================================================
    # Use CIRCUMFERENCE_RANGES directly (not height-based ratios)
    # This ensures circumferences stay within human-like ranges even after scaling
    bust_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["BUST"])
    bust_radius = bust_circ / (2 * np.pi)
    
    waist_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["WAIST"])
    waist_radius = waist_circ / (2 * np.pi)
    
    hip_circ = np.random.uniform(*CIRCUMFERENCE_RANGES["HIP"])
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
    case_id = f"varied_{i+1}"
    
    # Calculate bbox_span_y_before (raw vertices)
    y_coords = verts[:, 1]
    bbox_span_y_before = float(np.max(y_coords) - np.min(y_coords))
    
    # Target height: varied cases use 1.50~1.95m range
    target_height_m = np.random.uniform(1.50, 1.95)
    scale_factor = target_height_m / bbox_span_y_before if bbox_span_y_before > 0 else 1.0
    
    # Apply scale to all xyz coordinates (uniform scaling)
    verts_scaled = verts * scale_factor
    bbox_span_y_after = float(np.max(verts_scaled[:, 1]) - np.min(verts_scaled[:, 1]))
    
    # Validate invariants using SCALED vertices (not original)
    is_valid, error_msg = check_human_like_invariants(verts_scaled, case_id, "valid")
    
    if not is_valid:
        # Save debug JSON before raising
        debug_dir = Path(__file__).parent.parent.parent / "runs" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = debug_dir / f"s0_invariant_fail_{timestamp}.json"
        
        debug_data = {
            "case_id": case_id,
            "case_class": "valid",
            "bbox_span_y_before": float(bbox_span_y_before),
            "bbox_span_y_after": float(bbox_span_y_after),
            "target_height_m": float(target_height_m),
            "scale_factor_applied": float(scale_factor),
            "scale_was_applied": True,
            "invariant_check_input_height": float(bbox_span_y_after),
            "error_message": error_msg,
            "timestamp": timestamp
        }
        
        with open(debug_path, "w") as f:
            json.dump(debug_data, f, indent=2)
        
        print(f"\n[INVARIANT FAIL] Saved debug JSON to: {debug_path.resolve()}")
        raise ValueError(f"{case_id} failed invariant check: {error_msg}")
    
    # Hard proof log: print scale application evidence
    print(f"  [SCALE] {case_id}: before={bbox_span_y_before:.4f}m, "
          f"target={target_height_m:.4f}m, scale={scale_factor:.4f}, "
          f"after={bbox_span_y_after:.4f}m, invariant_check_input_height={bbox_span_y_after:.4f}m")
    
    # Record metadata
    metadata = {
        "scale_applied": True,
        "bbox_span_y_before": float(bbox_span_y_before),
        "bbox_span_y_after": float(bbox_span_y_after),
        "scale_factor_applied": float(scale_factor),
        "target_height_m": float(target_height_m)
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
for i, (verts, case_id, case_class) in enumerate(zip(cases, case_ids, case_classes)):
    is_valid, error_msg = check_human_like_invariants(verts, case_id, case_class)
    if case_class == "valid" and not is_valid:
        raise ValueError(f"VALID case {case_id} failed invariant check: {error_msg}")
    elif case_class == "valid":
        print(f"  ✓ {case_id} (valid): passed")
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
                print(f"  ✓ {case_id}: bbox_span_y_saved={bbox_span_y_saved:.4f}m ≈ target={target_height:.4f}m "
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
                print(f"  ✓ {case_id}: bbox_span_y_saved={bbox_span_y_saved:.4f}m ≈ target={target_height:.4f}m (scale={scale_factor:.4f})")

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
            
            print(f"  ✓ {case_id}: bbox_span_y_reloaded={bbox_span_y_reloaded:.4f}m ≈ "
                  f"target={target_height:.4f}m (scale={scale_factor:.4f}, diff={diff:.4f}m)")
        else:
            print(f"  ⚠ {case_id}: target_height not found in metadata")

reloaded_data.close()

if reopen_proof_passed:
    print(f"\n[RE-OPEN PROOF] ✓ PASSED: All valid cases verified. Scale was persisted to NPZ.")
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
