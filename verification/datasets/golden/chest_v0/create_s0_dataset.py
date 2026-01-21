#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for chest v0 validation."""

import numpy as np
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

cases = []
case_ids = []

# Case 1-2: Normal cases (box/cylinder-like)
for i in range(2):
    n_verts = 100
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    for j in range(n_verts):
        x = (j % 10) / 10.0 * 0.5 - 0.25
        y = (j // 10) / 10.0 * 1.0 + i * 0.1
        z = ((j % 5) / 5.0) * 0.3 - 0.15
        verts[j] = [x, y, z]
    cases.append(verts)
    case_ids.append(f"normal_{i+1}")

# Case 3: Degenerate y-range (very small)
verts = np.random.randn(100, 3).astype(np.float32) * 0.001  # Very small range
verts[:, 1] = 0.5  # All same y-value (degenerate)
cases.append(verts)
case_ids.append("degenerate_y_range")

# Case 4: Minimal vertices (1-2 vertices)
verts = np.array([[0.0, 0.5, 0.0], [0.1, 0.5, 0.0]], dtype=np.float32)
cases.append(verts)
case_ids.append("minimal_vertices")

# Case 5: Scale error suspected (cm-like scale, 10x larger)
verts = np.random.randn(100, 3).astype(np.float32) * 10.0  # 10x scale (cm-like)
for j in range(100):
    x = (j % 10) / 10.0 * 5.0 - 2.5
    y = (j // 10) / 10.0 * 10.0
    z = ((j % 5) / 5.0) * 3.0 - 1.5
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("scale_error_suspected")

# Case 6: Random noise (determinism check, seed fixed)
np.random.seed(123)
verts = np.random.randn(50, 3).astype(np.float32) * 0.15
cases.append(verts)
case_ids.append("random_noise_seed123")

# Save as NPZ (use object array for variable-length arrays)
output_path = Path(__file__).parent / "s0_synthetic_cases.npz"
# Convert to object array to handle variable shapes
verts_array = np.empty(len(cases), dtype=object)
verts_array[:] = cases
case_id_array = np.array(case_ids, dtype=object)
np.savez(str(output_path), verts=verts_array, case_id=case_id_array)

print(f"Created {output_path}")
print(f"  Cases: {len(cases)}")
print(f"  Case IDs: {case_ids}")
