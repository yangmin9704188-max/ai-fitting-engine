#!/usr/bin/env python3
"""Create s0_synthetic_cases.npz dataset for core measurements v0 validation."""

import numpy as np
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

cases = []
case_ids = []

# Case 1-5: Normal cases (body-like shapes)
for i in range(5):
    n_verts = 200
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    # Create body-like shape
    for j in range(n_verts):
        # y: height (0 to 1.7m)
        y = (j // 20) / 20.0 * 1.7
        
        # x, z: cross-section (varies by height)
        angle = (j % 20) / 20.0 * 2 * np.pi
        # Waist is narrower, bust/hip wider
        if 0.4 <= y <= 0.6:  # Waist region
            radius = 0.25 + np.random.randn() * 0.02
        elif 0.3 <= y <= 0.5:  # Bust region
            radius = 0.35 + np.random.randn() * 0.02
        elif 0.5 <= y <= 0.7:  # Hip region
            radius = 0.40 + np.random.randn() * 0.02
        else:
            radius = 0.20 + np.random.randn() * 0.02
        
        x = radius * np.cos(angle) + np.random.randn() * 0.01
        z = radius * np.sin(angle) + np.random.randn() * 0.01
        verts[j] = [x, y, z]
    
    cases.append(verts)
    case_ids.append(f"normal_{i+1}")

# Case 6-10: More varied shapes
for i in range(5):
    n_verts = 150
    verts = np.zeros((n_verts, 3), dtype=np.float32)
    
    for j in range(n_verts):
        y = (j // 15) / 15.0 * 1.6
        angle = (j % 15) / 15.0 * 2 * np.pi
        
        # Different body proportions
        if y < 0.3:  # Lower body
            radius = 0.30 + np.random.randn() * 0.03
        elif y < 0.5:  # Mid body
            radius = 0.28 + np.random.randn() * 0.02
        elif y < 0.7:  # Upper body
            radius = 0.32 + np.random.randn() * 0.02
        else:  # Neck/shoulder
            radius = 0.15 + np.random.randn() * 0.01
        
        x = radius * np.cos(angle) + np.random.randn() * 0.01
        z = radius * np.sin(angle) + np.random.randn() * 0.01
        verts[j] = [x, y, z]
    
    cases.append(verts)
    case_ids.append(f"varied_{i+1}")

# Case 11-15: Edge cases
# Case 11: Degenerate y-range
verts = np.random.randn(100, 3).astype(np.float32) * 0.001
verts[:, 1] = 0.5  # All same y-value
cases.append(verts)
case_ids.append("degenerate_y_range")

# Case 12: Minimal vertices
verts = np.array([[0.0, 0.5, 0.0], [0.1, 0.5, 0.0], [0.0, 0.6, 0.0]], dtype=np.float32)
cases.append(verts)
case_ids.append("minimal_vertices")

# Case 13: Scale error suspected (cm-like scale)
verts = np.random.randn(100, 3).astype(np.float32) * 10.0
for j in range(100):
    x = (j % 10) / 10.0 * 5.0 - 2.5
    y = (j // 10) / 10.0 * 10.0
    z = ((j % 5) / 5.0) * 3.0 - 1.5
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("scale_error_suspected")

# Case 14: Random noise (determinism check)
np.random.seed(123)
verts = np.random.randn(50, 3).astype(np.float32) * 0.15
cases.append(verts)
case_ids.append("random_noise_seed123")

# Case 15: Very tall/thin
verts = np.zeros((100, 3), dtype=np.float32)
for j in range(100):
    y = j / 100.0 * 2.0  # 2m tall
    angle = (j % 10) / 10.0 * 2 * np.pi
    radius = 0.15  # Thin
    x = radius * np.cos(angle)
    z = radius * np.sin(angle)
    verts[j] = [x, y, z]
cases.append(verts)
case_ids.append("tall_thin")

# Save as NPZ
output_path = Path(__file__).parent / "s0_synthetic_cases.npz"
verts_array = np.empty(len(cases), dtype=object)
verts_array[:] = cases
case_id_array = np.array(case_ids, dtype=object)
np.savez(str(output_path), verts=verts_array, case_id=case_id_array)

print(f"Created {output_path}")
print(f"  Cases: {len(cases)}")
print(f"  Case IDs: {case_ids}")
