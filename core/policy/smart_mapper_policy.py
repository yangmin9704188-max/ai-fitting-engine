# smart_mapper_policy.py
# Smart Mapper v0.1 Policy Parameters (FROZEN)
# 
# Policy sources:
# - A-Pose Normalization: core.pose_policy.PoseNormalizer (FROZEN v1.1)
# - Shoulder Width v1.1.2: core.measurements.shoulder_width_v112 (FROZEN)
#   Note: Measurement policy parameters are NOT duplicated here.
#   Smart Mapper uses measurement function API results only.

from dataclasses import dataclass


@dataclass(frozen=True)
class SmartMapperPolicy:
    """
    Smart Mapper v0.1 Policy Parameters
    
    DO NOT modify these values without:
    1. Updating version tag
    2. Running regression tests
    3. Documenting changes
    
    Note: This policy contains ONLY Smart Mapper runtime parameters.
    Measurement policy parameters (e.g., shoulder width r0/r1/cap) are
    NOT duplicated here. Smart Mapper uses measurement function API
    results (width values) only.
    """
    
    # Optimization Policy
    max_iter: int = 50
    tol_loss: float = 1e-5  # Early stopping: loss improvement threshold (adjusted for loss scale)
    tol_beta: float = 1e-4  # Early stopping: ||Δbeta|| threshold (adjusted for beta scale)
    
    # Loss weights
    weight_measurement: float = 1.0  # Shoulder width measurement loss
    weight_anchor: float = 0.1  # ||beta - beta_init||^2
    weight_beta_mag: float = 0.01  # ||beta||^2
    
    # Beta initialization
    bmi_ref: float = 22.0
    beta0_scale: float = 0.04
    beta0_clip: float = 0.5


# Global policy instance (FROZEN)
SMART_MAPPER_POLICY = SmartMapperPolicy()
