# Standard Measurement Keys Dictionary

**Single Source of Truth**: This file is the authoritative dictionary for all standard measurement keys used in the AI Fitting Engine project.

## Standard Keys

| standard_key | meaning | unit | related_measurement_key |
|-------------|---------|------|------------------------|
| UNDERBUST_CIRC_M | 구조/흉곽/밑가슴 둘레 | meters | UNDERBUST |
| BUST_CIRC_M | 볼륨/젖가슴 최대 둘레 | meters | BUST |
| HIP_CIRC_M | 골반 둘레 | meters | HIP |
| THIGH_CIRC_M | 허벅지 둘레 | meters | THIGH |
| WAIST_CIRC_M | 허리 둘레 | meters | WAIST |
| CIRCUMFERENCE_CIRC_M | 둘레 측정 (범용) | meters | CIRCUMFERENCE |

## Notes

- All keys use `_CIRC_M` suffix to indicate circumference measurement in meters.
- `related_measurement_key` is the domain token (UNDERBUST, BUST, etc.) used in artifacts DB, not the full standard_key.
- Legacy CHEST keys are deprecated. Use UNDERBUST_CIRC_M / BUST_CIRC_M instead.
