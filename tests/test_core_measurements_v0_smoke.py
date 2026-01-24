# test_core_measurements_v0_smoke.py
# Smoke test for core_measurements_v0.py
# Purpose: Basic functionality test with sample mesh

from __future__ import annotations
import numpy as np
import json
from core.measurements.core_measurements_v0 import (
    measure_circumference_v0_with_metadata,
    measure_width_depth_v0_with_metadata,
    measure_height_v0_with_metadata,
    measure_arm_length_v0_with_metadata,
    create_weight_metadata,
)


def create_dummy_mesh() -> np.ndarray:
    """
    Create a simple dummy mesh for testing.
    Returns vertices (N, 3) in meters.
    """
    # Simple cylinder-like shape for torso
    n_points = 100
    theta = np.linspace(0, 2 * np.pi, n_points)
    y_values = np.linspace(0.0, 1.7, 20)  # 1.7m height
    
    verts = []
    for y in y_values:
        radius = 0.3 - 0.1 * (y - 0.85) ** 2  # Waist-like shape
        for t in theta:
            x = radius * np.cos(t)
            z = radius * np.sin(t)
            verts.append([x, y, z])
    
    return np.array(verts, dtype=np.float32)


def test_circumference_group():
    """Test circumference measurements."""
    verts = create_dummy_mesh()
    
    keys = [
        "NECK_CIRC_M",
        "BUST_CIRC_M",
        "UNDERBUST_CIRC_M",
        "WAIST_CIRC_M",
        "HIP_CIRC_M",
        "THIGH_CIRC_M",
        "MIN_CALF_CIRC_M",
    ]
    
    print("=== Circumference Group Test ===")
    for key in keys:
        result = measure_circumference_v0_with_metadata(verts, key)
        print(f"{key}: value={result.value_m:.4f}m, warnings={len(result.metadata['warnings'])}")
        # Verify metadata structure
        assert "standard_key" in result.metadata
        assert "value_m" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"]["path_type"] == "closed_curve"
        assert result.metadata["method"]["metric_type"] == "circumference"
        assert result.metadata["search"]["band_scan_used"] == False
        assert result.metadata["search"]["band_scan_limit_mm"] == 10


def test_width_depth_group():
    """Test width/depth measurements."""
    verts = create_dummy_mesh()
    
    keys = [
        "CHEST_WIDTH_M",
        "CHEST_DEPTH_M",
        "WAIST_WIDTH_M",
        "WAIST_DEPTH_M",
        "HIP_WIDTH_M",
        "HIP_DEPTH_M",
    ]
    
    print("\n=== Width/Depth Group Test ===")
    for key in keys:
        result = measure_width_depth_v0_with_metadata(verts, key, proxy_used=False)
        print(f"{key}: value={result.value_m:.4f}m, warnings={len(result.metadata['warnings'])}")
        # Verify metadata structure
        assert "standard_key" in result.metadata
        assert "value_m" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"]["path_type"] == "straight_line"
        assert result.metadata["method"]["metric_type"] in ["width", "depth"]
        assert result.metadata["method"]["fixed_cross_section_required"] == True


def test_height_group():
    """Test height measurements."""
    verts = create_dummy_mesh()
    
    keys = ["HEIGHT_M", "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M"]
    
    print("\n=== Height Group Test ===")
    for key in keys:
        result = measure_height_v0_with_metadata(verts, key)
        print(f"{key}: value={result.value_m:.4f}m, warnings={len(result.metadata['warnings'])}")
        # Verify metadata structure
        assert "standard_key" in result.metadata
        assert "value_m" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"]["path_type"] == "straight_line"
        assert result.metadata["method"]["metric_type"] == "height"
        assert result.metadata["pose"]["strict_standing"] == True
        assert result.metadata["pose"]["knee_flexion_forbidden"] == True


def test_arm_length():
    """Test ARM_LEN_M measurement."""
    verts = create_dummy_mesh()
    
    # Create dummy joints for testing
    joints_xyz = np.array([
        [0.0, 1.5, 0.0],  # shoulder
        [0.0, 1.0, 0.0],  # elbow
        [0.0, 0.5, 0.0],  # wrist
    ], dtype=np.float32)
    joint_ids = {"R_shoulder": 0, "R_wrist": 2}
    
    result = measure_arm_length_v0_with_metadata(verts, joints_xyz, joint_ids)
    print(f"\nARM_LEN_M: value={result.value_m:.4f}m, warnings={len(result.metadata['warnings'])}")
    # Verify metadata structure
    assert result.metadata["standard_key"] == "ARM_LEN_M"
    assert "value_m" in result.metadata
    assert result.metadata["method"]["path_type"] == "surface_path"  # Required
    assert result.metadata["method"]["metric_type"] == "length"
    assert result.metadata["method"]["canonical_side"] == "right"  # Required


def test_weight():
    """Test WEIGHT_KG metadata creation."""
    result = create_weight_metadata(70.0)
    print(f"\nWEIGHT_KG: value={result.value_kg:.2f}kg")
    # Verify metadata structure
    assert result.metadata["standard_key"] == "WEIGHT_KG"
    assert "value_kg" in result.metadata
    assert result.metadata["unit"] == "kg"
    assert result.metadata["method"]["metric_type"] == "mass"


if __name__ == "__main__":
    print("Running smoke tests for core_measurements_v0...")
    try:
        test_circumference_group()
        test_width_depth_group()
        test_height_group()
        test_arm_length()
        test_weight()
        print("\n✓ All smoke tests passed")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
