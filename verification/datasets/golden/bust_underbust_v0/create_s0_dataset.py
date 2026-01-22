#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for bust/underbust v0 validation."""

import numpy as np
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

cases = []
case_ids = []

# Case 1-2: Normal cases (box/cylinder-like) - UNDERBUST and BUST
for i in range(2):
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for j in range(n_verts):
        x = (j % 10) / 10.0 * 0.5 - 0.25  # meters
        y = (j // 10) / 10.0 * 1.0 + i * 0.1  # meters
        z = ((j % 5) / 5.0) * 0.3 - 0.15  # meters
        verts[j] = [x, y, z]
    cases.append(verts)
    case_ids.append(f"normal_{i+1}")

# Case 3: Degenerate y-range (very small)
verts = np.random.randn(100, 3).astype(np.float32) * 0.001  # Very small range (meters)
verts[:, 1] = 0.5  # All same y-value (degenerate)
cases.append(verts)
case_ids.append("degenerate_y_range")

# Case 4: Minimal vertices (1-2 vertices)
verts = np.array([[0.0, 0.5, 0.0], [0.1, 0.5, 0.0]], dtype=np.float32)  # meters
cases.append(verts)
case_ids.append("minimal_vertices")

# Case 5: Scale error suspected (cm-like scale) - intentionally *100 to simulate cm units
# This will trigger UNIT_FAIL / PERIMETER_LARGE warnings (fact recording only, no judgment)
n_verts = 100
verts = np.zeros((n_verts, 3), dtype=np.float32)
for j in range(n_verts):
    # Generate normal meter-scale coordinates
    x = (j % 10) / 10.0 * 0.5 - 0.25  # meters
    y = (j // 10) / 10.0 * 1.0  # meters
    z = ((j % 5) / 5.0) * 0.3 - 0.15  # meters
    # Multiply by 100 to simulate cm-scale (intentional unit error for warning reproduction)
    verts[j] = [x * 100.0, y * 100.0, z * 100.0]
cases.append(verts)
case_ids.append("scale_error_suspected")

# Case 6: Random noise (determinism check, seed fixed)
np.random.seed(123)
verts = np.random.randn(50, 3).astype(np.float32) * 0.15  # meters
cases.append(verts)
case_ids.append("random_noise_seed123")

# Case 7: Male case (Δ ≈ 0 expected) - cylindrical, minimal bust-underbust difference
n_verts = 100
verts = np.zeros((n_verts, 3), dtype=np.float32)
for j in range(n_verts):
    # Cylindrical shape with minimal variation
    angle = (j % 20) / 20.0 * 2 * np.pi
    radius = 0.15  # meters (constant radius)
    x = radius * np.cos(angle)
    y = (j // 20) / 5.0 * 1.0  # meters
    z = radius * np.sin(angle)
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("male_delta_zero")

# Convert to batched format: (N, V, 3)
max_verts = max(v.shape[0] for v in cases)
verts_batched = np.zeros((len(cases), max_verts, 3), dtype=np.float32)
for i, v in enumerate(cases):
    verts_batched[i, :v.shape[0], :] = v

# Save as NPZ with meta keys
output_path = Path(__file__).parent / "s0_synthetic_cases.npz"
np.savez(
    str(output_path),
    verts=verts_batched.astype(np.float32),
    case_id=np.array(case_ids, dtype=object),
    meta_unit=np.array("m", dtype=object),
    schema_version=np.array("bust_underbust_v0_s0@1", dtype=object)
)

print(f"Created {output_path}")
print(f"  Cases: {len(cases)}")
print(f"  Case IDs: {case_ids}")
print(f"  Verts shape: {verts_batched.shape}")
print(f"  meta_unit: m")
print(f"  schema_version: bust_underbust_v0_s0@1")
