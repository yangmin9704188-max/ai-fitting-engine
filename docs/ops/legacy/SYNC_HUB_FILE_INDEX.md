# Repository File Index

이 문서는 자동 생성된 레포지토리 스냅샷이며,  
여기에 없는 파일은 존재하지 않는 것으로 간주한다.

---

## Directory Structure (Depth 3-4)

```
.
├── artifacts/
│   ├── pose_debug/
│   ├── runs/
│   │   └── smart_mapper/
│   ├── sample_task/
│   │   └── v0/
│   ├── shoulder_width/
│   │   ├── v1.1.3/
│   │   ├── v1.2/
│   │   └── v1.2_prototype/
│   └── verification/
│       └── smart_mapper_sw_v12/
├── core/
│   ├── measurements/
│   │   ├── circumference_v0.py
│   │   ├── read_me.txt
│   │   ├── shoulder_width_v112.py
│   │   └── shoulder_width_v12.py
│   ├── persistence/
│   ├── policy/
│   │   ├── __init__.py
│   │   ├── shoulder_width_v112_policy.py
│   │   └── smart_mapper_policy.py
│   ├── pose_policy.py
│   └── smart_mapper/
│       ├── __init__.py
│       └── smart_mapper_v001.py
├── data/
│   ├── processed/
│   └── raw/
├── db/
│   └── schema.sql
├── docs/
│   ├── archive/
│   │   ├── constitution/
│   │   │   ├── delivery_modes.md
│   │   │   ├── governance_policy.md
│   │   │   ├── kpi_decomposition.md
│   │   │   ├── quality_gates.md
│   │   │   ├── README.md
│   │   │   ├── releases.md
│   │   │   ├── schema_contract.md
│   │   │   └── telemetry_schema.md
│   │   ├── prompts/
│   │   │   ├── gemini_audit_prompt.md
│   │   │   ├── gpt_v1_prompt.md
│   │   │   └── gpt_v3_prompt.md
│   │   ├── samples/
│   │   │   └── v3_execution_pack_sample.md
│   │   ├── sync/
│   │   │   └── CURRENT_STATE.md
│   │   ├── templates/
│   │   │   └── CURSOR_TASK_TEMPLATE.md
│   │   ├── ReadMe.txt
│   │   ├── ReadMe1.txt
│   │   ├── review_loop_contract.md
│   │   └── stop_triggers.md
│   ├── judgments/
│   │   └── measurements/
│   │       ├── CHEST_V0_JUDGMENT_20260121_R1.md
│   │       ├── CIRCUMFERENCE_V0_JUDGMENT.md
│   │       ├── HIP_V0_JUDGMENT_20260121_R1.md.txt
│   │       ├── SYNC HUB 2026-01-21.txt
│   │       └── THIGH_V0_JUDGMENT_20260121_R1.md.txt
│   ├── policies/
│   │   ├── apose_normalization/
│   │   │   └── v1.1.md
│   │   ├── measurements/
│   │   │   ├── bust.md
│   │   │   ├── CONTRACT_INTERFACE_CHEST_V0.md
│   │   │   ├── CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md
│   │   │   ├── CONTRACT_INTERFACE_HIP_V0.md.txt
│   │   │   ├── CONTRACT_INTERFACE_THIGH_V0.md.txt
│   │   │   ├── contract_template.md
│   │   │   ├── FREEZE_DECLARATION.md
│   │   │   ├── GEOMETRIC_DESIGN_CHEST_V0.md
│   │   │   ├── GEOMETRIC_DESIGN_HIP_V0.md.txt
│   │   │   ├── GEOMETRIC_DESIGN_THIGH_V0.md.txt
│   │   │   ├── hip.md
│   │   │   ├── README.md
│   │   │   ├── SEMANTIC_DEFINITION_CHEST_VNEXT.md
│   │   │   ├── SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md
│   │   │   ├── SEMANTIC_DEFINITION_HIP_VNEXT.md.txt
│   │   │   ├── SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt
│   │   │   ├── VALIDATION_FRAME_CHEST_V0.md
│   │   │   ├── VALIDATION_FRAME_CIRCUMFERENCE_V0.md
│   │   │   ├── VALIDATION_FRAME_HIP_V0.md
│   │   │   ├── VALIDATION_FRAME_THIGH_V0.md
│   │   │   ├── waist.md
│   │   │   └── 구현방법규칙.md
│   │   └── INDEX.md
│   ├── reports/
│   │   └── AN-v11-R1.md
│   ├── runs/
│   │   └── apose_nomalization/
│   │       └── 2026-01-16_run_001/
│   ├── samples/
│   │   └── v3_execution_pack_sample.md
│   ├── sync/
│   │   └── CURRENT_STATE.md
│   ├── architecture_final_plan.md
│   ├── evidence_packer.md
│   ├── evidence_schema_v1.md
│   ├── review_loop_contract.md
│   └── stop_triggers.md
├── engine/
│   └── README.md
├── experiments/
│   └── read_me.txt
├── logs/
│   └── observation.md
├── models/
│   └── smplx/
├── pipelines/
│   ├── smart_mapper_run.py
│   ├── step1_execute.py
│   └── verify_policy.py
├── tests/
│   ├── test_chest_v0_validation_contract.py
│   ├── test_circumference_v0_smoke.py
│   ├── test_circumference_v0_validation_contract.py
│   ├── test_hip_v0_validation_contract.py
│   └── test_thigh_v0_validation_contract.py
├── tools/
│   ├── capture_session.py
│   ├── check_db_status.py
│   ├── db_upsert.py
│   ├── execute_v3_pack.py
│   ├── extract_stop_triggers.py
│   ├── generate_trigger_from_force.py
│   ├── pack_evidence.py
│   ├── README.md
│   ├── render_ai_prompt.py
│   ├── stop_trigger_notify.py
│   ├── stop_triggers.yaml
│   ├── sync_state.py
│   ├── validate_evidence.py
│   └── validate_observation.py
├── verification/
│   ├── datasets/
│   │   ├── dummy_data.npz
│   │   ├── export_golden_shoulder_npz.py
│   │   ├── golden/
│   │   │   ├── chest_v0/
│   │   │   │   ├── create_s0_dataset.py
│   │   │   │   └── s0_synthetic_cases.npz
│   │   │   ├── circumference_v0/
│   │   │   │   ├── create_s0_dataset.py
│   │   │   │   └── s0_synthetic_cases.npz
│   │   │   ├── hip_v0/
│   │   │   │   ├── create_s0_dataset.py
│   │   │   │   └── s0_synthetic_cases.npz
│   │   │   ├── shoulder_width/
│   │   │   │   └── golden_shoulder_v12_extended.npz
│   │   │   └── thigh_v0/
│   │   │       ├── create_s0_dataset.py
│   │   │       └── s0_synthetic_cases.npz
│   │   └── golden_shoulder_batched.npz
│   ├── debug/
│   │   ├── debug_output/
│   │   │   └── debug_arm_weights_left_armL_16_18_20.obj
│   │   └── debug_shoulder_width_case2.py
│   ├── reports/
│   │   ├── apose_v11/
│   │   ├── shoulder_width_v112/
│   │   │   ├── case_1_debug.json
│   │   │   ├── case_10_debug.json
│   │   │   ├── case_2_debug.json
│   │   │   ├── case_3_debug.json
│   │   │   ├── case_4_debug.json
│   │   │   ├── case_5_debug.json
│   │   │   ├── case_6_debug.json
│   │   │   ├── case_7_debug.json
│   │   │   ├── case_8_debug.json
│   │   │   ├── case_9_debug.json
│   │   │   ├── verification_results.csv
│   │   │   └── verification_summary.json
│   │   ├── smart_mapper_v001/
│   │   └── sweep_shoulder_v112.csv
│   ├── runners/
│   │   ├── shoulder_width/
│   │   ├── smart_mapper/
│   │   │   └── verify_smart_mapper_with_sw_v12.py
│   │   ├── step2_verify_pose.py
│   │   ├── sweep_shoulder_width_v112.py
│   │   ├── verify_apose_v11.py
│   │   ├── verify_chest_v0.py
│   │   ├── verify_circumference_v0.py
│   │   ├── verify_hip_v0.py
│   │   ├── verify_policy.py
│   │   ├── verify_shoulder_width_v112.py
│   │   ├── verify_smart_mapper_v001.py
│   │   └── verify_thigh_v0.py
│   ├── tools/
│   │   ├── check_smplx_weights.py
│   │   ├── export_golden_shoulder_v12_npz.py
│   │   ├── inspect_golden_shoulder_npz.py
│   │   ├── inspect_smplx_joints.py
│   │   ├── step0_make_dummy.py
│   │   └── summarize_sanity_checks.py
│   ├── read_me.txt
│   └── README_VERIFICATION.md
├── .cursorrules
├── .gitignore
├── DB_GUIDE.md
├── EVIDENCE_VALIDATION_ENTRYPOINT_INVESTIGATION.md
├── Makefile
├── pending_review.json
├── README.md
├── SYNC_HUB.md
├── SYNC_HUB_FILE_INDEX.md
├── triggers.json
├── VALIDATE_EVIDENCE_INVESTIGATION.md
├── 전체 프로젝트 누적 성과.txt
└── 표준화용어_인체 공학 표준화 용어.xls
```

---

## Docs Directory Files

### Root Level
- `docs/architecture_final_plan.md`
- `docs/evidence_packer.md`
- `docs/evidence_schema_v1.md`
- `docs/review_loop_contract.md`
- `docs/stop_triggers.md`

### docs/archive/
- `docs/archive/ReadMe.txt`
- `docs/archive/ReadMe1.txt`
- `docs/archive/review_loop_contract.md`
- `docs/archive/stop_triggers.md`

#### docs/archive/constitution/
- `docs/archive/constitution/delivery_modes.md`
- `docs/archive/constitution/governance_policy.md`
- `docs/archive/constitution/kpi_decomposition.md`
- `docs/archive/constitution/quality_gates.md`
- `docs/archive/constitution/README.md`
- `docs/archive/constitution/releases.md`
- `docs/archive/constitution/schema_contract.md`
- `docs/archive/constitution/telemetry_schema.md`

#### docs/archive/prompts/
- `docs/archive/prompts/gemini_audit_prompt.md`
- `docs/archive/prompts/gpt_v1_prompt.md`
- `docs/archive/prompts/gpt_v3_prompt.md`

#### docs/archive/samples/
- `docs/archive/samples/v3_execution_pack_sample.md`

#### docs/archive/sync/
- `docs/archive/sync/CURRENT_STATE.md`

#### docs/archive/templates/
- `docs/archive/templates/CURSOR_TASK_TEMPLATE.md`

### docs/policies/
- `docs/policies/INDEX.md`

#### docs/policies/apose_normalization/
- `docs/policies/apose_normalization/v1.1.md`

#### docs/policies/measurements/
- `docs/policies/measurements/bust.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_CHEST_V0.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_HIP_V0.md.txt`
- `docs/policies/measurements/CONTRACT_INTERFACE_THIGH_V0.md.txt`
- `docs/policies/measurements/contract_template.md`
- `docs/policies/measurements/FREEZE_DECLARATION.md`
- `docs/policies/measurements/GEOMETRIC_DESIGN_CHEST_V0.md`
- `docs/policies/measurements/GEOMETRIC_DESIGN_HIP_V0.md.txt`
- `docs/policies/measurements/GEOMETRIC_DESIGN_THIGH_V0.md.txt`
- `docs/policies/measurements/hip.md`
- `docs/policies/measurements/README.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_CHEST_VNEXT.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_HIP_VNEXT.md.txt`
- `docs/policies/measurements/SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt`
- `docs/policies/measurements/VALIDATION_FRAME_CHEST_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_CIRCUMFERENCE_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_HIP_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_THIGH_V0.md`
- `docs/policies/measurements/waist.md`
- `docs/policies/measurements/구현방법규칙.md`

### docs/reports/
- `docs/reports/AN-v11-R1.md`

### docs/runs/
- `docs/runs/apose_nomalization/2026-01-16_run_001/`

### docs/samples/
- `docs/samples/v3_execution_pack_sample.md`

### docs/judgments/
- `docs/judgments/measurements/CHEST_V0_JUDGMENT_20260121_R1.md`
- `docs/judgments/measurements/CIRCUMFERENCE_V0_JUDGMENT.md`
- `docs/judgments/measurements/HIP_V0_JUDGMENT_20260121_R1.md.txt`
- `docs/judgments/measurements/SYNC HUB 2026-01-21.txt`
- `docs/judgments/measurements/THIGH_V0_JUDGMENT_20260121_R1.md.txt`

### docs/sync/
- `docs/sync/CURRENT_STATE.md`

---

## Policies Documents

### Policy Documents
- `docs/policies/apose_normalization/v1.1.md`
- `docs/policies/INDEX.md`

### Measurements Documents
- `docs/policies/measurements/bust.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_CHEST_V0.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md`
- `docs/policies/measurements/CONTRACT_INTERFACE_HIP_V0.md.txt`
- `docs/policies/measurements/CONTRACT_INTERFACE_THIGH_V0.md.txt`
- `docs/policies/measurements/contract_template.md`
- `docs/policies/measurements/FREEZE_DECLARATION.md`
- `docs/policies/measurements/GEOMETRIC_DESIGN_CHEST_V0.md`
- `docs/policies/measurements/GEOMETRIC_DESIGN_HIP_V0.md.txt`
- `docs/policies/measurements/GEOMETRIC_DESIGN_THIGH_V0.md.txt`
- `docs/policies/measurements/hip.md`
- `docs/policies/measurements/README.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_CHEST_VNEXT.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md`
- `docs/policies/measurements/SEMANTIC_DEFINITION_HIP_VNEXT.md.txt`
- `docs/policies/measurements/SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt`
- `docs/policies/measurements/VALIDATION_FRAME_CHEST_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_CIRCUMFERENCE_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_HIP_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_THIGH_V0.md`
- `docs/policies/measurements/waist.md`
- `docs/policies/measurements/구현방법규칙.md`

---

## Contract Documents (Doc Type: Contract)

다음 문서들은 파일 헤더에 "Doc Type: Contract"로 명시되어 있다:

- `docs/policies/measurements/bust.md`
- `docs/policies/measurements/contract_template.md`
- `docs/policies/measurements/FREEZE_DECLARATION.md`
- `docs/policies/measurements/hip.md`
- `docs/policies/measurements/README.md`
- `docs/policies/measurements/VALIDATION_FRAME_CHEST_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_CIRCUMFERENCE_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_HIP_V0.md`
- `docs/policies/measurements/VALIDATION_FRAME_THIGH_V0.md`
- `docs/policies/measurements/waist.md`

---

## Measurements Documents

### Semantic Layer Contracts
- `docs/policies/measurements/README.md` (Body Measurement Meta-Policy v1.3)
- `docs/policies/measurements/bust.md`
- `docs/policies/measurements/waist.md`
- `docs/policies/measurements/hip.md`

### Interface Layer Contracts
- `docs/policies/measurements/FREEZE_DECLARATION.md`

### Templates
- `docs/policies/measurements/contract_template.md`

### Other
- `docs/policies/measurements/구현방법규칙.md`

---

## Core Implementation Files

### core/measurements/
- `core/measurements/circumference_v0.py`
- `core/measurements/read_me.txt`
- `core/measurements/shoulder_width_v112.py`
- `core/measurements/shoulder_width_v12.py`

### core/policy/
- `core/policy/__init__.py`
- `core/policy/shoulder_width_v112_policy.py`
- `core/policy/smart_mapper_policy.py`

### core/smart_mapper/
- `core/smart_mapper/__init__.py`
- `core/smart_mapper/smart_mapper_v001.py`

### core/
- `core/pose_policy.py`

---

## Tools

- `tools/capture_session.py`
- `tools/check_db_status.py`
- `tools/db_upsert.py`
- `tools/execute_v3_pack.py`
- `tools/extract_stop_triggers.py`
- `tools/generate_trigger_from_force.py`
- `tools/pack_evidence.py`
- `tools/README.md`
- `tools/render_ai_prompt.py`
- `tools/stop_trigger_notify.py`
- `tools/stop_triggers.yaml`
- `tools/sync_state.py`
- `tools/validate_evidence.py`
- `tools/validate_observation.py`

---

## Pipelines

- `pipelines/smart_mapper_run.py`
- `pipelines/step1_execute.py`
- `pipelines/verify_policy.py`

---

## Verification

### Verification Runners
- `verification/runners/verify_apose_v11.py`
- `verification/runners/verify_chest_v0.py`
- `verification/runners/verify_circumference_v0.py`
- `verification/runners/verify_hip_v0.py`
- `verification/runners/verify_policy.py`
- `verification/runners/verify_shoulder_width_v112.py`
- `verification/runners/verify_smart_mapper_v001.py`
- `verification/runners/verify_thigh_v0.py`
- `verification/runners/step2_verify_pose.py`
- `verification/runners/sweep_shoulder_width_v112.py`

### Verification Tools
- `verification/tools/check_smplx_weights.py`
- `verification/tools/export_golden_shoulder_v12_npz.py`
- `verification/tools/inspect_golden_shoulder_npz.py`
- `verification/tools/inspect_smplx_joints.py`
- `verification/tools/step0_make_dummy.py`
- `verification/tools/summarize_sanity_checks.py`

### Verification Documentation
- `verification/read_me.txt`
- `verification/README_VERIFICATION.md`

---

## Database

- `db/schema.sql`

---

## Root Level Files

### Configuration Files
- `.cursorrules`
- `.gitignore`
- `Makefile`
- `pending_review.json`
- `triggers.json`

### Documentation Files
- `DB_GUIDE.md`
- `EVIDENCE_VALIDATION_ENTRYPOINT_INVESTIGATION.md`
- `README.md`
- `SYNC_HUB.md`
- `SYNC_HUB_FILE_INDEX.md`
- `VALIDATE_EVIDENCE_INVESTIGATION.md`
- `전체 프로젝트 누적 성과.txt`
- `표준화용어_인체 공학 표준화 용어.xls`

---

*Generated: 2026-01-24*
