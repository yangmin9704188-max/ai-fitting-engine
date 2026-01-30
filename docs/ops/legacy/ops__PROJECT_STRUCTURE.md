./
  - .cursorrules
  - .gitignore
  - 20F_data.xlsx
  - DB_GUIDE.md
  - EVIDENCE_VALIDATION_ENTRYPOINT_INVESTIGATION.md
  - Makefile
  - pending_review.json
  - README.md
  - REPO_STRUCTURE_GUIDE.md
  - run_convert_round24.py
  - run_convert_temp.py
  - SYNC_HUB.md
  - SYNC_HUB_FILE_INDEX.md
  - triggers.json
  - urement
  - VALIDATE_EVIDENCE_INVESTIGATION.md
  - 전체 프로젝트 누적 성과.txt

  core/
    - pose_policy.py

    measurements/
      - bust_underbust_v0.py
      - circumference_v0.py
      - core_measurements_v0.py
      - metadata_v0.py
      - read_me.txt
      - shoulder_width_v112.py
      - shoulder_width_v12.py

    persistence/

    policy/
      - shoulder_width_v112_policy.py
      - smart_mapper_policy.py
      - __init__.py

    smart_mapper/
      - smart_mapper_v001.py
      - __init__.py

  data/
    - ingestion.py
    - normalize_sizekorea_headers.py
    - README.md
    - regenerate_processed_m_standard.py

    column_map/
      - sizekorea_v0.json
      - sizekorea_v1.json
      - sizekorea_v2.json

    processed/
      - Reference Data.csv

      curated_v0/
        - curated_v0.parquet

      m_standard/
        - SizeKorea_20-29_Female_m.csv
        - SizeKorea_20-29_Female_provenance.json

      raw_normalized_v0/
        - 7th_data_normalized.csv
        - 8th_data_3d_normalized.csv
        - 8th_data_direct_normalized.csv

      SizeKorea_Final/
        - SizeKorea_20-29_Female.csv
        - SizeKorea_20-29_Male.csv
        - SizeKorea_30-39_Female.csv
        - SizeKorea_30-39_Male.csv
        - SizeKorea_40-49_Female.csv
        - SizeKorea_40-49_Male.csv
        - SizeKorea_50-59_Female.csv
        - SizeKorea_50-59_Male.csv

      step1_output/
        - init_betas_all.npy
        - init_betas_female.npy
        - init_betas_male.npy
        - targets_metadata.csv

    raw/

      scans_3d/
        - 6th_20F.obj
        - 6th_20M_data.xlsx
        - 6th_30M_data.xlsx
        - 6th_40M_data.xlsx
        - ORIGINAL_6th_20M.obj
        - ORIGINAL_6th_30M.obj
        - ORIGINAL_6th_40M.obj

      sizekorea_raw/
        - (1~2차년도) 2021년 8차 인체치수조사_최종보고서.pdf
        - 7th_data.csv
        - 7th_data.xlsx
        - 8th_data.xlsx
        - 8th_data_3d.csv
        - 8th_data_direct.csv

  db/
    - schema.sql

  docs/
    - architecture_final_plan.md
    - evidence_packer.md
    - evidence_schema_v1.md
    - MasterPlan.txt
    - review_loop_contract.md
    - stop_triggers.md

    archive/
      - ReadMe.txt
      - ReadMe1.txt
      - review_loop_contract.md
      - stop_triggers.md

      constitution/
        - delivery_modes.md
        - governance_policy.md
        - kpi_decomposition.md
        - quality_gates.md
        - README.md
        - releases.md
        - schema_contract.md
        - telemetry_schema.md

      prompts/
        - gemini_audit_prompt.md
        - gpt_v1_prompt.md
        - gpt_v3_prompt.md

      samples/
        - v3_execution_pack_sample.md

      sync/
        - CURRENT_STATE.md
        - SYNC HUB 2026-01-21.txt

      templates/
        - CURSOR_TASK_TEMPLATE.md

    contract/
      - measurement_coverage_v0.csv
      - measurement_coverage_v0_source.md
      - NPZ_CONTRACT.md
      - standard_keys.md
      - UNIT_STANDARD.md

    data/
      - curated_v0_arm_knee_trace.md
      - curated_v0_header_candidates.md
      - curated_v0_pipeline_guide.md
      - curated_v0_plan.md
      - curated_v0_warnings_schema.md

    judgments/
      - INDEX.md

      measurements/
        - CHEST_V0_JUDGMENT_20260121_R1.md
        - CIRCUMFERENCE_V0_JUDGMENT.md
        - HIP_V0_JUDGMENT_20260121_R1.md.txt
        - MEASUREMENTS_V0_BUNDLE_JUDGMENT_20260121_R1.md
        - THIGH_V0_JUDGMENT_20260121_R1.md.txt

      templates/
        - JUDGMENT_ENTRY_TEMPLATE.md

    ops/
      - baselines.json
      - BASELINE_UPDATE_RUNBOOK.md
      - COMMANDS.md
      - COMMIT_POLICY.md
      - cursor_prompt_header.md
      - INDEX.md
      - JUDGMENTS_POLICY.md
      - JUDGMENTS_RUNBOOK.md
      - OBSIDIAN_HOME.md
      - OBSIDIAN_SETUP.md
      - PROJECT_STRUCTURE.md
      - ROUND21_EXECUTION_GUIDE.md
      - ROUND24_EXECUTION_GUIDE.md
      - round_runbook.md
      - sizekorea_integration_checklist.md

      canvas/
        - PROJECT_MAP.canvas

      pr_bodies/
        - pr_body_local_artifacts_ignore_geo_v0.md
        - pr_body_ops_consolidate_pr_bodies.md
        - pr_body_ops_devex_round10_commands_autodoc.md
        - pr_body_ops_docs_measurements_consolidation_v1.md
        - pr_body_ops_obsidian_bootstrap.md
        - pr_body_ops_round_charter.md
        - pr_body_ops_sizekorea_integration_checklist.md
        - pr_body_round14.md
        - pr_body_round18_golden_s0_freeze.md
        - pr_body_round1_make_round_wrapper.md
        - pr_body_round1_postprocess.md
        - pr_body_round20.md
        - pr_body_round2_kpi_diff.md
        - pr_body_round2_pr_template_round_checklist.md
        - pr_body_round3_auto_prev_baseline.md
        - pr_body_round3_coverage_backlog.md
        - pr_body_round3_root_cleanup.md
        - pr_body_round4_round_registry.md
        - pr_body_round4_slim_coverage_backlog.md
        - pr_body_round5_kpi_diff.md
        - pr_body_round5_kpi_diff_signal_line.md
        - pr_body_round6_lineage_golden_registry.md
        - pr_body_round6_ops_lock_text_sensor.md
        - pr_body_round7b_visual_skip_artifacts.md
        - pr_body_round7_visual_provenance.md
        - pr_body_team_system_v0_2.md
        - pr_body_team_system_v0_3.md
        - pr_body_update_cursorrules.md
        - pr_body_validation_round24_s1_20f_obj_xlsx_metadata.md
        - pr_body_validation_round26_s1_baseline_proxy_coverage.md
        - pr_body_validation_round28_20m_xlsx_to_csv_metadata.md
        - pr_body_validation_round28_s1_20m_proxy_switch.md
        - pr_body_validation_round29_s1_skip_reasons.md
        - pr_body_validation_round30_s1_load_failed_diagnostics.md
        - pr_body_validation_round31_s1_loader_fallback_and_exceptions.md
        - pr_body_validation_round32_s1_skip_reasons_invariant.md
        - pr_body_validation_round33_s1_obj_loader_npz_verts.md
        - pr_body_validation_round34_s1_npz_kpi_wiring.md
        - pr_body_validation_round35_kpi_distribution_wiring.md
        - pr_body_validation_round36_circumference_debug.md
        - pr_body_validation_round37_circumference_path_fix.md
        - pr_body_validation_round38b_circ_perimeter_name_error_hotfix.md
        - pr_body_validation_round38_proxy_diversify_20m_30m_40m.md
        - pr_body_validation_round39_circ_convex_hull_perimeter.md
        - README.md

      templates/
        - adr_stub.md
        - baseline_candidate_stub.md
        - baseline_update_proposal.md
        - golden_candidate_stub.md
        - golden_registry_patch_stub.json
        - report_facts_stub.md
        - spec_stub.md

    policies/
      - INDEX.md
      - MEASUREMENTS_BUNDLE.md

      apose_normalization/
        - v1.1.md

      measurements/
        - bust.md
        - CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md
        - CONTRACT_INTERFACE_CHEST_V0.md
        - CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md
        - CONTRACT_INTERFACE_HIP_V0.md.txt
        - CONTRACT_INTERFACE_THIGH_V0.md.txt
        - contract_template.md
        - FREEZE_DECLARATION.md
        - GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md
        - GEOMETRIC_DESIGN_CHEST_V0.md
        - GEOMETRIC_DESIGN_HIP_V0.md.txt
        - GEOMETRIC_DESIGN_THIGH_V0.md.txt
        - hip.md
        - INDEX.md
        - README.md
        - SEMANTIC_DEFINITION_BUST_VNEXT.md
        - SEMANTIC_DEFINITION_CHEST_VNEXT.md
        - SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md
        - SEMANTIC_DEFINITION_HIP_VNEXT.md.txt
        - SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt
        - SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md
        - VALIDATION_FRAME_BUST_UNDERBUST_V0.md
        - VALIDATION_FRAME_CHEST_V0.md
        - VALIDATION_FRAME_CIRCUMFERENCE_V0.md
        - VALIDATION_FRAME_HIP_V0.md
        - VALIDATION_FRAME_HIP_V0.md.txt
        - VALIDATION_FRAME_THIGH_V0.md
        - VALIDATION_FRAME_THIGH_V0.md.txt
        - waist.md
        - 구현방법규칙.md

      validation/
        - curated_v0_realdata_gate_v0.md

    reports/
      - AN-v11-R1.md

    samples/
      - v3_execution_pack_sample.md

    semantic/
      - legacy_handling.md
      - measurement_semantics_v0.md
      - pose_normalization.md

      evidence/
        - sizekorea_measurement_methods_v0.md

    specs/

      data/
        - Data Classification & Cleaning Engine (curated_v0 v3).md
        - Golden Dataset & Facts Runner Engine.md

    sync/
      - CURRENT_STATE.md

    templates/
      - SYNC_HUB_TEMPLATE.md

    validation/
      - measurement_metadata_schema_v0.md

    verification/
      - coverage_backlog.md
      - curated_v0_gate_draft_v0.md
      - golden_real_data_freeze_v0.1.md
      - golden_registry.json
      - golden_registry_contract_v0.md
      - golden_s0_freeze_v0.md
      - kpi_diff_contract_v0.md
      - lineage_manifest_contract_v0.md
      - round_charter_template.md
      - round_ops_v0.md
      - round_registry.json
      - round_registry_contract_v0.md
      - visual_provenance_contract_v0.md

  engine/
    - README.md

  experiments/
    - read_me.txt

  logs/
    - observation.md

  models/

    smplx/
      - SMPLX_FEMALE.pkl
      - SMPLX_MALE.pkl
      - SMPLX_NEUTRAL.pkl

  pipelines/
    - build_curated_v0.py
    - smart_mapper_run.py
    - step1_execute.py
    - verify_policy.py

  reports/

    validation/
      - curated_v0_facts_round1.md
      - geo_v0_facts_round1.md
      - geo_v0_facts_round13_fastmode_normal1_runner.md
      - geo_v0_facts_round15_bust_verts_aligned_normal1.md
      - geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md
      - geo_v0_facts_round17_valid10_expanded.md
      - INDEX.md
      - round_registry.json

  tests/
    - test_8th_fallback_expected_unit.py
    - test_build_curated_v0.py
    - test_bust_underbust_v0_smoke.py
    - test_chest_v0_validation_contract.py
    - test_circumference_v0_smoke.py
    - test_circumference_v0_validation_contract.py
    - test_core_measurements_v0_smoke.py
    - test_db_artifacts_smoke.py
    - test_hip_v0_validation_contract.py
    - test_ingestion_canonicalization.py
    - test_thigh_v0_validation_contract.py
    - test_unit_fail_nan_only.py

  tools/
    - aggregate_warnings_v3.py
    - build_glossary_and_mapping.py
    - capture_session.py
    - check_db_status.py
    - convert_7th_xlsx_to_csv.py
    - coverage_backlog.py
    - db_upsert.py
    - execute_v3_pack.py
    - extract_context_sample_20cols.py
    - extract_stop_triggers.py
    - generate_trigger_from_force.py
    - golden_registry.py
    - inspect_raw_columns.py
    - judgments.py
    - kpi_diff.py
    - lineage.py
    - migrate_add_artifacts_table.py
    - observe_normalized_columns.py
    - observe_sizekorea_columns.py
    - pack_evidence.py
    - postprocess_round.py
    - README.md
    - reextract_raw_headers.py
    - render_ai_prompt.py
    - round_registry.py
    - sample_raw_data_units.py
    - set_baseline_run.py
    - stop_triggers.yaml
    - stop_trigger_notify.py
    - summarize_facts_kpi.py
    - sync_state.py
    - update_contract_from_table.py
    - validate_evidence.py
    - validate_observation.py
    - visual_provenance.py

    ops/
      - check_ops_lock.py
      - generate_commands_md.py

  verification/
    - README_VERIFICATION.md
    - read_me.txt
    - __init__.py

    datasets/
      - dummy_data.npz
      - export_golden_shoulder_npz.py
      - golden_shoulder_batched.npz

      golden/

        bust_underbust_v0/
          - create_real_data_golden.py
          - create_s0_dataset.py
          - golden_real_data_v0.npz
          - README_REAL_DATA_GOLDEN.md
          - s0_synthetic_cases.npz

        chest_v0/
          - create_s0_dataset.py
          - s0_synthetic_cases.npz

        circumference_v0/
          - create_s0_dataset.py
          - s0_synthetic_cases.npz

        core_measurements_v0/
          - create_real_data_golden.py
          - create_s0_dataset.py
          - extract_case_ids_manifest.py
          - golden_real_data_v0.case_ids.json
          - golden_real_data_v0.npz
          - s0_synthetic_cases.npz

        hip_v0/
          - create_s0_dataset.py
          - s0_synthetic_cases.npz

        s1_mesh_v0/
          - s1_manifest_v0.json

          meshes/
            - 6th_20M.obj
            - 6th_30M.obj
            - 6th_40M.obj

          metadata/

        shoulder_width/
          - golden_shoulder_v12_extended.npz

        thigh_v0/
          - create_s0_dataset.py
          - s0_synthetic_cases.npz

      runs/

        debug/
          - s0_circ_synth_trace_normal_1.json
          - s0_invariant_fail_20260125_041621.json
          - s0_invariant_fail_20260125_041645.json
          - s0_invariant_fail_20260125_042406.json
          - s0_invariant_fail_20260125_153029.json
          - s0_invariant_fail_20260125_153055.json
          - s0_invariant_fail_20260125_160941.json
          - s0_invariant_fail_20260125_161006.json
          - s0_invariant_fail_20260125_161017.json

    debug/
      - debug_shoulder_width_case2.py

      debug_output/
        - debug_arm_weights_left_armL_16_18_20.obj

    reports/
      - sweep_shoulder_v112.csv

      apose_v11/
        - case_10_debug.json
        - case_11_debug.json
        - case_12_debug.json
        - case_13_debug.json
        - case_14_debug.json
        - case_15_debug.json
        - case_16_debug.json
        - case_17_debug.json
        - case_18_debug.json
        - case_19_debug.json
        - case_1_debug.json
        - case_20_debug.json
        - case_2_debug.json
        - case_3_debug.json
        - case_4_debug.json
        - case_5_debug.json
        - case_6_debug.json
        - case_7_debug.json
        - case_8_debug.json
        - case_9_debug.json
        - verification_results.csv
        - verification_summary.json

      circumference_v0/
        - validation_results.csv
        - validation_summary.json

      shoulder_width_v112/
        - case_10_debug.json
        - case_1_debug.json
        - case_2_debug.json
        - case_3_debug.json
        - case_4_debug.json
        - case_5_debug.json
        - case_6_debug.json
        - case_7_debug.json
        - case_8_debug.json
        - case_9_debug.json
        - verification_results.csv
        - verification_summary.json

      smart_mapper_v001/
        - fail_reason_summary.md
        - verification_analysis.md
        - verification_results.csv
        - verification_summary.json

        case_10_debug/
          - measurement_error.json

        case_2_debug/
          - analysis_report.md
          - measurement_debug.json
          - measurement_error.json

        case_3_debug/
          - measurement_error.json

        case_4_debug/
          - measurement_error.json

        case_7_debug/
          - measurement_error.json

        case_8_debug/
          - measurement_error.json

    runners/
      - run_curated_v0_facts_round1.py
      - run_geo_v0_facts_round1.py
      - run_geo_v0_s1_facts.py
      - step2_verify_pose.py
      - sweep_shoulder_width_v112.py
      - verify_apose_v11.py
      - verify_chest_v0.py
      - verify_circumference_v0.py
      - verify_hip_v0.py
      - verify_policy.py
      - verify_shoulder_width_v112.py
      - verify_smart_mapper_v001.py
      - verify_thigh_v0.py
      - __init__.py

      shoulder_width/
        - example_configs_v113.json
        - README_V113_SWEEP.md
        - test_v12_prototype.py
        - verify_shoulder_width_v113_sweep.py
        - verify_shoulder_width_v12_regression.py
        - verify_shoulder_width_v12_sensitivity.py
        - __init__.py

      smart_mapper/
        - verify_smart_mapper_with_sw_v12.py

    runs/

      column_inventory/

        20260123_005102/
          - columns_by_file.json
          - columns_intersection.csv
          - columns_union.csv

        20260123_005209/
          - columns_by_file.json
          - columns_intersection.csv
          - columns_union.csv

        20260123_010225/
          - columns_by_file.json
          - columns_union.csv

        20260123_010332/
          - columns_by_file.json
          - columns_union.csv

        20260123_010549/
          - columns_by_file.json
          - columns_union.csv

      column_map/
        - sizekorea_v1_match_report.json
        - sizekorea_v2_match_report.json

      column_observation/
        - 7th_data_columns.txt
        - 8th_data_3d_columns.txt
        - 8th_data_direct_columns.txt
        - column_observation.json
        - normalized_column_observation.json

      context_samples/

        20260123_020900/
          - 7th_context_sample.csv
          - context_sample_manifest.json

        20260123_020916/
          - 8th_3d_context_sample.csv
          - 8th_direct_context_sample.csv
          - context_sample_manifest.json

      curated_v0/
        - 2026-01-23_run1.md
        - 2026-01-23_v2_run1.md
        - 2026-01-23_v3_run1.md
        - 2026-01-23_v3_run2.md
        - 2026-01-24_parsing_hardening_run1.md
        - 7th_xlsx_diagnosis.md
        - aggregation_v3.json
        - aggregation_v3_after_fix.json
        - aggregation_v3_after_update.json
        - aggregation_v3_contract_update.json
        - completeness_report.md
        - unit_fail_trace.md
        - unit_fail_trace_summary.md
        - warnings.jsonl
        - warnings_v2.jsonl
        - warnings_v3.jsonl
        - warnings_v3_after_fix.jsonl
        - warnings_v3_after_update.jsonl
        - warnings_v3_contract_update.jsonl
        - warnings_v3_weightkg_fix.jsonl

      facts/
        - _baseline.json

        bust_underbust/
          - facts_per_sample.csv
          - facts_summary.json

          20260122_2323_S0/
            - facts_per_sample.csv
            - facts_summary.json

          REAL_20260122_2331/
            - facts_per_sample.csv
            - facts_summary.json

        curated_v0/

          round20_20260125_164503/
            - curated_v0_facts_round1.md
            - facts_summary.json
            - kpi.json
            - KPI.md
            - KPI_DIFF.md
            - ROUND_CHARTER.md

          round20_20260125_164801/
            - curated_v0_facts_round1.md
            - facts_summary.json
            - kpi.json
            - KPI.md
            - KPI_DIFF.md
            - lineage.json
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round20_smoke/
            - curated_v0_facts_round1.md
            - facts_summary.json

          round20_smoke_final/
            - curated_v0_facts_round1.md
            - facts_summary.json

        geo_v0/

          my_manual_check/
            - facts_summary.json
            - geo_v0_facts_round1.md

          round10_s0_scale_proof/
            - facts_summary.json
            - geo_v0_facts_round10_s0_scale_proof.md

          round11_s0_scale_reopen_proof/
            - facts_summary.json
            - geo_v0_facts_round1.md

          round13_fastmode_normal1_runner/
            - facts_summary.json
            - geo_v0_facts_round1.md

          round15_bust_verts_aligned_normal1/
            - facts_summary.json
            - geo_v0_facts_round1.md
            - geo_v0_facts_round15_bust_verts_aligned_normal1.md

          round16_waist_hip_verts_aligned_normal1/
            - facts_summary.json
            - geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md

          round17_valid10_expanded/
            - facts_summary.json
            - geo_v0_facts_round17_valid10_expanded.md

          round1_20260125_033634/
            - facts_summary.json
            - geo_v0_facts_round7_slice_shared.md

          round1_20260125_034649/
            - facts_summary.json
            - geo_v0_facts_round8_height_debug.md

          round1_test/
            - facts_summary.json
            - geo_v0_facts_round1.md
            - geo_v0_facts_round2.md
            - geo_v0_facts_round3_waist_hip_fix.md
            - geo_v0_facts_round4_waist_hip_fix.md
            - geo_v0_facts_round5_waist_hip_fallback_working.md

          round6_s0_humanlike/
            - facts_summary.json
            - geo_v0_facts_round6_s0_humanlike.md

          round9_s0_scale_fix/
            - facts_summary.json
            - geo_v0_facts_round9_s0_scale_fix.md

        geo_v0_s1/

          round24_20260127_001836/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round25_20260127_003039/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round26_20260127_003950/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round28_20260127_014544/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round29_20260127_015214/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round30_20260127_015911/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round31_20260127_023009/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round32_20260127_024231/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round33_20260127_025731/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round34_20260127_031305/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round35_20260127_032300/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round36_20260127_033854/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round37b_20260127_040159/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round37_20260127_035236/

          round37_20260127_035329/

          round38b_20260127_042436/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round38_20260127_041945/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

          round39_20260127_043613/
            - facts_summary.json
            - KPI.md
            - KPI_DIFF.md
            - LINEAGE.md
            - PROMPT_SNAPSHOT.md
            - ROUND_CHARTER.md

            CANDIDATES/
              - BASELINE_CANDIDATE.md
              - BASELINE_UPDATE_PROPOSAL.md
              - GOLDEN_CANDIDATE.md
              - GOLDEN_REGISTRY_PATCH.json
              - GOLDEN_REGISTRY_PATCH_README.md

    tmp/
      - header_dump_7th.csv
      - header_dump_8th_3d.csv
      - header_dump_8th_direct.csv

    tools/
      - check_smplx_weights.py
      - convert_scan_xlsx_to_csv.py
      - export_golden_shoulder_v12_npz.py
      - inspect_golden_shoulder_npz.py
      - inspect_smplx_joints.py
      - run_bust_underbust_facts_v0.py
      - step0_make_dummy.py
      - summarize_sanity_checks.py

