# shoulder_width_v112_policy.py
# Shoulder Width v1.1.2 Frozen Policy Parameters
# 
# This module provides the frozen policy configuration for Shoulder Width v1.1.2.
# DO NOT modify these values without proper versioning and documentation.

from core.measurements.shoulder_width_v112 import ShoulderWidthV112Config


def get_cfg() -> ShoulderWidthV112Config:
    """
    Get the frozen policy configuration for Shoulder Width v1.1.2.
    
    Frozen values (as per policy freeze):
    - r0_ratio: 0.26
    - r1_ratio: 0.18
    - cap_quantile: 0.94
    
    Returns:
        ShoulderWidthV112Config instance with frozen policy values
    """
    return ShoulderWidthV112Config(
        r0_ratio=0.26,
        r1_ratio=0.18,
        cap_quantile=0.94,
        # Other parameters use defaults from ShoulderWidthV112Config
    )
