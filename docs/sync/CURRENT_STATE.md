# SYNC_STATE

snapshot:
  id:
  status: candidate
  last_change: code
  version_keys:
    snapshot: false
    semantic: false
    geometry_impl: false
    dataset: false

pipeline:
  position: rd | local_validation | promotion | release_hold | production
  active_runbook:

signals:
  validation:
    status: pass | warning | fail
    uncertainty_trend: up | stable | down
  cost:
    pure: up | stable | down
    egress: up | stable | down
    cost_model_version:
  latency: up | stable | down

decision:
  promotion: not_reviewed | deferred | eligible | blocked
  release: not_started | hold | released
  authority: rd_lead+ops_lead
  artifacts:
    adr:
    validation_report:

constraints:
  technical:
    - HIP measurement function (core/measurements/hip_v0.py) not yet implemented
    - CHEST measurement function (core/measurements/chest_v0.py) not yet implemented
  operational:
    -

allowed_actions:
  -
forbidden_actions:
  -

last_update:
  date: 2026-01-21
  trigger: validation_frame_additions

changed_paths:
  - verification/runners/verify_circumference_v0.py
  - verification/runners/verify_chest_v0.py
  - verification/runners/verify_hip_v0.py
  - verification/datasets/golden/circumference_v0/
  - verification/datasets/golden/chest_v0/
  - verification/datasets/golden/hip_v0/
  - tests/test_circumference_v0_validation_contract.py
  - tests/test_chest_v0_validation_contract.py
  - tests/test_hip_v0_validation_contract.py
  - docs/policies/measurements/VALIDATION_FRAME_CIRCUMFERENCE_V0.md
  - docs/policies/measurements/VALIDATION_FRAME_CHEST_V0.md
  - docs/policies/measurements/VALIDATION_FRAME_HIP_V0.md
