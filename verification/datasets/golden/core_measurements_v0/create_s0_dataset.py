#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for core measurements v0 validation.

This script generates synthetic mesh cases with human-like scale invariants.
Valid cases (normal_*, varied_*) must satisfy physical plausibility constraints.
Expected fail cases (degenerate_*, etc.) are intentionally invalid for testing.
"""

import numpy as np
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

# Case 1-5: Normal cases (body-like shapes with human-like scale)
for i in range(5):
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # Generate human-like circumferences
    # Bust: 0.35-0.85 of height
    bust_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"])
    bust_radius = bust_circ / (2 * np.pi)
    
    # Waist: 0.30-0.75 of height
    waist_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"])
    waist_radius = waist_circ / (2 * np.pi)
    
    # Hip: 0.35-0.90 of height
    hip_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["HIP"])
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
    
    # Validate invariants
    is_valid, error_msg = check_human_like_invariants(verts, f"normal_{i+1}", "valid")
    if not is_valid:
        raise ValueError(f"normal_{i+1} failed invariant check: {error_msg}")
    
    cases.append(verts)
    case_ids.append(f"normal_{i+1}")
    case_classes.append("valid")

# Case 6-10: More varied shapes (still human-like)
for i in range(5):
    # Generate human-like height
    height = np.random.uniform(HEIGHT_RANGE[0], HEIGHT_RANGE[1])
    
    # Generate varied but still human-like proportions
    bust_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["BUST"])
    bust_radius = bust_circ / (2 * np.pi)
    
    waist_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["WAIST"])
    waist_radius = waist_circ / (2 * np.pi)
    
    hip_circ = height * np.random.uniform(*CIRCUMFERENCE_TO_HEIGHT_RATIOS["HIP"])
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
    
    # Validate invariants
    is_valid, error_msg = check_human_like_invariants(verts, f"varied_{i+1}", "valid")
    if not is_valid:
        raise ValueError(f"varied_{i+1} failed invariant check: {error_msg}")
    
    cases.append(verts)
    case_ids.append(f"varied_{i+1}")
    case_classes.append("valid")

# Case 11-15: Edge cases (expected_fail - intentionally invalid)
# Case 11: Degenerate y-range
verts = np.random.randn(100, 3).astype(np.float32) * 0.001
verts[:, 1] = 0.5  # All same y-value
cases.append(verts)
case_ids.append("degenerate_y_range")
case_classes.append("expected_fail")

# Case 12: Minimal vertices
verts = np.array([[0.0, 0.5, 0.0], [0.1, 0.5, 0.0], [0.0, 0.6, 0.0]], dtype=np.float32)
cases.append(verts)
case_ids.append("minimal_vertices")
case_classes.append("expected_fail")

# Case 13: Scale error suspected (cm-like scale)
verts = np.random.randn(100, 3).astype(np.float32) * 10.0
for j in range(100):
    x = (j % 10) / 10.0 * 5.0 - 2.5
    y = (j // 10) / 10.0 * 10.0
    z = ((j % 5) / 5.0) * 3.0 - 1.5
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("scale_error_suspected")
case_classes.append("expected_fail")

# Case 14: Random noise (determinism check)
np.random.seed(123)
verts = np.random.randn(50, 3).astype(np.float32) * 0.15
cases.append(verts)
case_ids.append("random_noise_seed123")
case_classes.append("expected_fail")

# Case 15: Very tall/thin (may violate height range)
verts = np.zeros((100, 3), dtype=np.float32)
for j in range(100):
    y = j / 100.0 * 2.0  # 2m tall (may exceed range)
    angle = (j % 10) / 10.0 * 2 * np.pi
    radius = 0.15  # Thin
    x = radius * np.cos(angle)
    z = radius * np.sin(angle)
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("tall_thin")
case_classes.append("expected_fail")

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

# Save as NPZ
output_path = Path(__file__).parent / "s0_synthetic_cases.npz"
verts_array = np.empty(len(cases), dtype=object)
verts_array[:] = cases
case_id_array = np.array(case_ids, dtype=object)
case_class_array = np.array(case_classes, dtype=object)
np.savez(
    str(output_path),
    verts=verts_array,
    case_id=case_id_array,
    case_class=case_class_array
)

print(f"\nCreated {output_path}")
print(f"  Cases: {len(cases)}")
print(f"  Valid cases: {sum(1 for c in case_classes if c == 'valid')}")
print(f"  Expected fail cases: {sum(1 for c in case_classes if c == 'expected_fail')}")
print(f"  Case IDs: {case_ids}")
