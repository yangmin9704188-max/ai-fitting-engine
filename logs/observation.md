```yaml
policy_name: Shoulder Width v1.2
version: v1.2
measurement: shoulder_width
run_id: "20260117_153136"
state_intent: frozen_gate_regression
verification_tool_path: verification/runners/shoulder_width/verify_shoulder_width_v12_regression.py
artifacts:
  run_dir: artifacts/shoulder_width/v1.2/regression/20260117_153136_PASS
provenance:
  command: py -m verification.runners.shoulder_width.verify_shoulder_width_v12_regression --npz verification/datasets/golden/shoulder_width/golden_shoulder_v12_extended.npz
gates:
  fallback_0: true
  exception_0: true
  arm_exclusion_applied: true
  cfg_hash_stable: true
  status: PASS
```

## Summary

Shoulder Width v1.2 regression verification completed successfully.

### Status: PASS

All success criteria met:
- fallback=0: PASS
- exception=0: PASS
- arm_exclusion_applied: PASS
- cfg_hash_stable: PASS

### Statistics

- Total frames: 200
- Valid frames: 200
- Measured SW: mean=0.419472m, std=0.018607m
- Ratio (measured/joint): mean=1.3001, range=[1.2204, 1.3874]
- Arm exclusion: mean count=1343

### Artifacts

- wiring_proof.json
- regression_results.csv
- regression_summary.json
- worst_cases.json
- manifest.json
