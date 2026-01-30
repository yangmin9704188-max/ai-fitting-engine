# REFERENCE_INVENTORY_v1
STATUS: CANONICAL (ops evidence report)
Last updated: 2026-01-30

---

## Scope

- **Scanned for references FROM**: contracts/, docs/, tools/, modules/, core/, root files (README.md, .cursorrules, CLAUDE.md, SYNC_HUB.md, Makefile, SYNC_HUB_FILE_INDEX.md, REPO_STRUCTURE_GUIDE.md)
- **Excluded from scan**: verification/, exports/, .git/, __pycache__/, .venv/
- **Inventoried items**: All docs, contracts, root misc files, and key code directories
- **Reference types counted**: Markdown links, literal path strings, Python imports, subprocess/CLI calls, .cursorrules mentions
- **Missing input**: docs/legacy/LEGACY_INDEX.md (does not exist); docs/ops/MASTER_PLAN.md (referenced in CLAUDE.md but file does not exist on disk)

---

## Classification Table

### Root-Level Files

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| SYNC_HUB.md | file | KEEP | Ops constitution; SSoT Pack v1 sec 3.1 canonical | 27 | CLAUDE.md: literal path; .cursorrules: mention; docs/ops/GUARDRAILS.md: literal path | — | NO | — | HIGH |
| SYNC_HUB_FILE_INDEX.md | file | NEEDS-STUB | Operational file index; not in SSoT Pack; refs from ops docs | 4 | REPO_STRUCTURE_GUIDE.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; README.md: literal path | docs/legacy/ops_old/SYNC_HUB_FILE_INDEX.md | YES | SSOT_PACK_v1 + docs/ops/INDEX.md | HIGH |
| DB_GUIDE.md | file | KEEP | Database guide; referenced from ops INDEX with markdown link | 4 | docs/ops/INDEX.md: markdown link; REPO_STRUCTURE_GUIDE.md: literal path; SYNC_HUB_FILE_INDEX.md: literal path | — | NO | — | HIGH |
| REPO_STRUCTURE_GUIDE.md | file | NEEDS-STUB | Not SSoT; 2 refs from ops docs only | 2 | docs/ops/PROJECT_STRUCTURE.md: literal path; docs/ops/pr_bodies/pr_body_round3_root_cleanup.md: literal path | docs/legacy/ops_old/REPO_STRUCTURE_GUIDE.md | YES | docs/ops/PROJECT_STRUCTURE.md | MEDIUM |
| EVIDENCE_VALIDATION_ENTRYPOINT_INVESTIGATION.md | file | NEEDS-STUB | Investigation note; refs from inventory files only | 3 | SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/notes_old/EVIDENCE_VALIDATION_ENTRYPOINT_INVESTIGATION.md | YES | — | MEDIUM |
| VALIDATE_EVIDENCE_INVESTIGATION.md | file | NEEDS-STUB | Investigation note; refs from inventory files only | 3 | SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/notes_old/VALIDATE_EVIDENCE_INVESTIGATION.md | YES | — | MEDIUM |
| REPO_FILES.txt | file | SAFE-MOVE | Auto-generated file listing; 0 inbound refs | 0 | — | docs/legacy/misc_old/REPO_FILES.txt | NO | — | LOW |
| 전체 프로젝트 누적 성과.txt | file | NEEDS-STUB | Legacy note; 1 ref from file index | 1 | SYNC_HUB_FILE_INDEX.md: literal path | docs/legacy/notes_old/전체_프로젝트_누적_성과.txt | YES | — | MEDIUM |
| create_round60_manifest.py | file | NEEDS-STUB | One-off script; 1 ref from listing only | 1 | REPO_FILES.txt: literal path | docs/legacy/misc_old/create_round60_manifest.py | YES | — | MEDIUM |
| run_convert_round24.py | file | NEEDS-STUB | One-off conversion script; 2 refs | 2 | REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path | docs/legacy/misc_old/run_convert_round24.py | YES | — | MEDIUM |
| run_convert_temp.py | file | NEEDS-STUB | One-off conversion script; 2 refs | 2 | docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/misc_old/run_convert_temp.py | YES | — | MEDIUM |
| pending_review.json | file | KEEP | CI integration (.github/workflows/evidence.yml); 14 refs from tools and docs | 14 | .github/workflows/evidence.yml: shell conditional; tools/capture_session.py: Python code; docs/review_loop_contract.md: literal path | — | NO | — | HIGH |
| triggers.json | file | KEEP | Active tool integration; 9 refs from Python tools | 9 | tools/stop_trigger_notify.py: Python code; tools/generate_trigger_from_force.py: Python code; tools/extract_stop_triggers.py: literal path | — | NO | — | HIGH |

### contracts/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| contracts/interface_ledger_v0.md | file | KEEP | SSoT contract (.cursorrules table); 16 refs across agents/tools/modules | 16 | .cursorrules: SSoT table entry; modules/fitting/README.md: canonical ref; tools/append_progress_event_v0.py: CLI help | — | NO | — | HIGH |
| contracts/port_readiness_checklist_v0.md | file | KEEP | SSoT contract (.cursorrules table); 6 refs | 6 | .cursorrules: SSoT table entry; docs/ops/dashboard/EXPORT_CONTRACT_v0.md: SSoT ref; docs/ops/dashboard/VERIFICATION_REPORT.md: ref | — | NO | — | HIGH |
| contracts/port_event_note_template_v0.md | file | KEEP | SSoT contract (.cursorrules table); 4 refs | 4 | .cursorrules: SSoT table entry; contracts/port_readiness_checklist_v0.md: related doc; contracts/VERIFICATION_REPORT.md: scope header | — | NO | — | HIGH |
| contracts/CANONICALIZATION_PLAN.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/CANONICALIZATION_PLAN.md | NO | — | LOW |
| contracts/CHANGESET_REPORT.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/CHANGESET_REPORT.md | NO | — | LOW |
| contracts/CONSISTENCY_CHECK.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/CONSISTENCY_CHECK.md | NO | — | LOW |
| contracts/CONSISTENCY_REPORT.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/CONSISTENCY_REPORT.md | NO | — | LOW |
| contracts/DOC_MAP.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/DOC_MAP.md | NO | — | LOW |
| contracts/FINAL_CHECKLIST.md | file | SAFE-MOVE | 0 inbound refs; one-time audit artifact | 0 | — | docs/legacy/contracts_old/FINAL_CHECKLIST.md | NO | — | LOW |
| contracts/PATCH_BLOCKS.md | file | NEEDS-STUB | 1 ref from sibling VERIFICATION_REPORT | 1 | contracts/VERIFICATION_REPORT.md: inline "see PATCH_BLOCKS.md" | docs/legacy/contracts_old/PATCH_BLOCKS.md | YES | — | MEDIUM |
| contracts/VERIFICATION_REPORT.md | file | SAFE-MOVE | 0 inbound refs from outside; one-time audit artifact | 0 | — | docs/legacy/contracts_old/VERIFICATION_REPORT.md | NO | — | LOW |

### docs/ SSoT, Architecture, Sync, Plans

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/ssot/SSOT_PACK_v1.md | file | KEEP | SSoT Pack v1 declaration; canonical root authority | 2 | .cursorrules: structural rule; docs/ops/DIRECTORY_CHARTER_v1.md: SSoT member | — | NO | — | MEDIUM |
| docs/architecture/LAYERS_v1.md | file | KEEP | Architecture SSoT; 18 refs across CLAUDE.md, .cursorrules, SYNC_HUB | 18 | CLAUDE.md: SSoT ref; SYNC_HUB.md: SSoT ref; docs/ops/GUARDRAILS.md: protected file | — | NO | — | HIGH |
| docs/architecture/DoD_CHECKLISTS_v1.md | file | KEEP | Evidence-first DoD; 7 refs | 7 | README.md: link; docs/ops/GUARDRAILS.md: protected file; docs/architecture/LAYERS_v1.md: link | — | NO | — | HIGH |
| docs/sync/CURRENT_STATE.md | file | KEEP | State log canonical; 21 refs from CI, agents, docs | 21 | CLAUDE.md: SSoT ref; .cursorrules: SSoT Touch Lock; .github/workflows/guard-sync-state.yml: CI gate | — | NO | — | HIGH |
| docs/plans/Body_Module_Plan_v1.md | file | KEEP | SSoT Pack S1; canonical module plan | 1 | docs/ssot/SSOT_PACK_v1.md: SSoT registry | — | NO | — | MEDIUM |
| docs/plans/fitting_module_plan_v1.md | file | KEEP | SSoT Pack S2; canonical module plan | 1 | docs/ssot/SSOT_PACK_v1.md: SSoT registry | — | NO | — | MEDIUM |
| docs/plans/garment_Product Contract v0.9-revC.md | file | KEEP | SSoT Pack S3; canonical garment contract | 1 | docs/ssot/SSOT_PACK_v1.md: SSoT registry | — | NO | — | MEDIUM |

### docs/contract/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/contract/standard_keys.md | file | KEEP | Standard keys dictionary; 12 refs from CLAUDE.md, SYNC_HUB, code | 12 | CLAUDE.md: Key Documents; SYNC_HUB.md: SSoT ref; pipelines/build_curated_v0.py: code comment | — | NO | — | HIGH |
| docs/contract/UNIT_STANDARD.md | file | KEEP | Unit standard definition; 8 refs | 8 | SYNC_HUB.md: SSoT ref; docs/contract/NPZ_CONTRACT.md: link; docs/policies/measurements/README.md: link | — | NO | — | HIGH |
| docs/contract/NPZ_CONTRACT.md | file | KEEP | NPZ format contract; 2 refs | 2 | REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/contract/measurement_coverage_v0_source.md | file | KEEP | Coverage v0 source doc; 2 refs | 2 | REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |

### docs/semantic/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/semantic/measurement_semantics_v0.md | file | KEEP | Core semantic definitions; 12 refs from code and docs | 12 | core/measurements/core_measurements_v0.py: code comment; SYNC_HUB.md: SSoT ref; docs/policies/measurements/INDEX.md: link | — | NO | — | HIGH |
| docs/semantic/evidence/sizekorea_measurement_methods_v0.md | file | KEEP | SizeKorea evidence base; 9 refs | 9 | docs/semantic/measurement_semantics_v0.md: evidence link; core/measurements/metadata_v0.py: code path; docs/policies/measurements/INDEX.md: link | — | NO | — | HIGH |
| docs/semantic/pose_normalization.md | file | KEEP | Pose normalization definition; 7 refs | 7 | docs/semantic/measurement_semantics_v0.md: link; docs/validation/measurement_metadata_schema_v0.md: link; REPO_STRUCTURE_GUIDE.md: link | — | NO | — | HIGH |
| docs/semantic/legacy_handling.md | file | KEEP | Legacy handling guidance; 5 refs | 5 | docs/sync/CURRENT_STATE.md: state log; docs/ops/pr_bodies/pr_body_ops_consolidate_pr_bodies.md: PR body; REPO_STRUCTURE_GUIDE.md: link | — | NO | — | HIGH |

### docs/data/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/data/curated_v0_plan.md | file | KEEP | Pipeline contract; code-referenced | 4 | pipelines/build_curated_v0.py: code comment "Contract: docs/data/curated_v0_plan.md"; docs/ops/sizekorea_integration_checklist.md: link; REPO_FILES.txt: literal path | — | NO | — | HIGH |
| docs/data/curated_v0_warnings_schema.md | file | KEEP | Warnings schema for pipeline; 4 refs | 4 | docs/sync/CURRENT_STATE.md: state log; docs/ops/sizekorea_integration_checklist.md: link; REPO_FILES.txt: literal path | — | NO | — | HIGH |
| docs/data/curated_v0_arm_knee_trace.md | file | NEEDS-STUB | Debug trace doc; 2 refs from state log and tree | 2 | docs/sync/CURRENT_STATE.md: state log; docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/notes_old/curated_v0_arm_knee_trace.md | YES | — | MEDIUM |
| docs/data/curated_v0_header_candidates.md | file | NEEDS-STUB | Planning artifact; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/plans_old/curated_v0_header_candidates.md | YES | — | MEDIUM |
| docs/data/curated_v0_pipeline_guide.md | file | NEEDS-STUB | Pipeline guide; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/ops_old/curated_v0_pipeline_guide.md | YES | — | MEDIUM |

### docs/reports/ and docs/specs/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/reports/AN-v11-R1.md | file | NEEDS-STUB | Analysis report; 4 refs (tool example, indexes) | 4 | tools/db_upsert.py: code example; SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path | docs/legacy/reports_old/AN-v11-R1.md | YES | — | HIGH |
| docs/specs/data/Golden Dataset & Facts Runner Engine.md | file | NEEDS-STUB | Spec doc; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/plans_old/Golden_Dataset_Facts_Runner_Engine.md | YES | — | MEDIUM |
| docs/specs/data/Data Classification & Cleaning Engine (curated_v0 v3).md | file | NEEDS-STUB | Spec doc; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/plans_old/Data_Classification_Cleaning_Engine_v3.md | YES | — | MEDIUM |

### docs/ Root-Level Files

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/LEGACY_MAP.md | file | KEEP | Legacy migration guide; 2 refs from README + modules/README | 2 | README.md: markdown link; modules/README.md: markdown link | — | NO | — | MEDIUM |
| docs/evidence_packer.md | file | NEEDS-STUB | Evidence packer doc; 3 refs (inventory only) | 3 | SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/ops_old/evidence_packer.md | YES | — | MEDIUM |
| docs/evidence_schema_v1.md | file | NEEDS-STUB | Evidence schema; 4 refs (inventory + investigation) | 4 | SYNC_HUB_FILE_INDEX.md: literal path; VALIDATE_EVIDENCE_INVESTIGATION.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path | docs/legacy/ops_old/evidence_schema_v1.md | YES | — | HIGH |
| docs/review_loop_contract.md | file | NEEDS-STUB | Review loop contract; 4 refs (inventory files) | 4 | SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/contracts_old/review_loop_contract.md | YES | — | HIGH |
| docs/stop_triggers.md | file | NEEDS-STUB | Stop trigger definitions; 7 refs from archive docs and review contract | 7 | docs/archive/review_loop_contract.md: literal path; docs/review_loop_contract.md: literal path; docs/archive/prompts/gpt_v3_prompt.md: literal path | docs/legacy/ops_old/stop_triggers.md | YES | — | HIGH |
| docs/samples/v3_execution_pack_sample.md | file | NEEDS-STUB | Sample doc; 3 refs (inventory only) | 3 | SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/misc_old/v3_execution_pack_sample.md | YES | — | MEDIUM |
| docs/templates/SYNC_HUB_TEMPLATE.md | file | NEEDS-STUB | SYNC_HUB template; 2 refs | 2 | docs/ops/PROJECT_STRUCTURE.md: literal path; REPO_FILES.txt: literal path | docs/legacy/ops_old/SYNC_HUB_TEMPLATE.md | YES | docs/ops/INDEX.md (ops template section) | MEDIUM |

### docs/ops/ Core

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/ops/DIRECTORY_CHARTER_v1.md | file | KEEP | Directory governance; .cursorrules mandate + SSoT Pack member | 2 | .cursorrules: line 4 structural rule; docs/ssot/SSOT_PACK_v1.md: conflict resolution order | — | NO | — | MEDIUM |
| docs/ops/INDEX.md | file | KEEP | Central ops index; 18 refs from CLAUDE.md, .cursorrules, PR bodies | 18 | CLAUDE.md: narrative mention; .cursorrules: Pre-Read list; docs/ops/GUARDRAILS.md: link | — | NO | — | HIGH |
| docs/ops/GUARDRAILS.md | file | KEEP | Merge blockers/enforcement; 10 refs | 10 | CLAUDE.md: Key Documents; .cursorrules: SSoT table; modules/README.md: rules link | — | NO | — | HIGH |
| docs/ops/COMMANDS.md | file | KEEP | Commands reference; CI freshness check | 5 | .github/workflows/commands-docs-check.yml: CI check; tools/ops/generate_commands_md.py: generator target; docs/ops/OPS_PLANE.md: link | — | NO | — | HIGH |
| docs/ops/COMMIT_POLICY.md | file | KEEP | Commit policy; 5 refs from judgment/baseline docs | 5 | docs/ops/JUDGMENTS_POLICY.md: cross-link; docs/ops/JUDGMENTS_RUNBOOK.md: Related Docs; docs/ops/INDEX.md: policy link | — | NO | — | HIGH |
| docs/ops/OPS_PLANE.md | file | KEEP | Ops plane charter; 5 refs | 5 | contracts/DOC_MAP.md: table entry; docs/architecture/LAYERS_v1.md: charter link; docs/ops/GUARDRAILS.md: protected file | — | NO | — | HIGH |
| docs/ops/PROJECT_DASHBOARD.md | file | KEEP | Dashboard target; 5 refs from tools and dashboard docs | 5 | tools/render_dashboard_v0.py: rendering target; docs/ops/dashboard/VERIFICATION_REPORT.md: audit target; docs/ops/dashboard/PATCH_BLOCKS.md: patch target | — | NO | — | HIGH |
| docs/ops/BACKFILL_POLICY.md | file | KEEP | Tier 0/1/2 backfill policy; 4 refs | 4 | docs/architecture/LAYERS_v1.md: link; docs/architecture/DoD_CHECKLISTS_v1.md: evidence ref; docs/LEGACY_MAP.md: link | — | NO | — | HIGH |
| docs/ops/BACKFILL_LOG.md | file | KEEP | Tier2 backfill execution log; 11 refs | 11 | docs/ops/BACKFILL_POLICY.md: Tier2 mandate; tools/ops/check_change_boundaries.py: protected file; docs/architecture/LAYERS_v1.md: link | — | NO | — | HIGH |
| docs/ops/round_runbook.md | file | KEEP | Round execution runbook; 4 refs | 4 | docs/ops/INDEX.md: runbook listing; docs/sync/CURRENT_STATE.md: file tree; docs/ops/pr_bodies/pr_body_round1_make_round_wrapper.md: ref | — | NO | — | HIGH |
| docs/ops/BASELINE_UPDATE_RUNBOOK.md | file | KEEP | Baseline update procedure; 4 refs | 4 | docs/ops/JUDGMENTS_POLICY.md: cross-link; docs/ops/JUDGMENTS_RUNBOOK.md: Related Docs; docs/ops/templates/baseline_update_proposal.md: ref | — | NO | — | HIGH |
| docs/ops/JUDGMENTS_POLICY.md | file | KEEP | Judgment archive policy; 4 refs | 4 | docs/ops/INDEX.md: policy link; docs/judgments/INDEX.md: policy link; docs/ops/JUDGMENTS_RUNBOOK.md: Related Docs | — | NO | — | HIGH |
| docs/ops/JUDGMENTS_RUNBOOK.md | file | KEEP | Judgment execution procedure; 4 refs | 4 | docs/ops/INDEX.md: Runbook link; docs/judgments/INDEX.md: Runbook link; docs/ops/JUDGMENTS_POLICY.md: Related Docs | — | NO | — | HIGH |
| docs/ops/OBSIDIAN_HOME.md | file | KEEP | Obsidian navigation entry point; 4 refs | 4 | docs/ops/OBSIDIAN_SETUP.md: setup instructions; docs/ops/INDEX.md: Home link; docs/ops/pr_bodies/pr_body_ops_obsidian_bootstrap.md: ref | — | NO | — | HIGH |
| docs/ops/OBSIDIAN_SETUP.md | file | KEEP | Obsidian setup guide; 3 refs | 3 | docs/ops/INDEX.md: Setup Guide link; docs/ops/pr_bodies/pr_body_ops_obsidian_bootstrap.md: ref; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/ops/cursor_prompt_header.md | file | KEEP | Cursor AI prompt header; 9 refs from .cursorrules and ops docs | 9 | .cursorrules: Pre-Read file list; docs/ops/OPS_PLANE.md: doc listing; docs/sync/CURRENT_STATE.md: file tree | — | NO | — | HIGH |
| docs/ops/sizekorea_integration_checklist.md | file | KEEP | Integration checklist; 5 refs | 5 | docs/ops/OBSIDIAN_HOME.md: checklist link; docs/ops/OBSIDIAN_SETUP.md: description; docs/ops/pr_bodies/pr_body_ops_sizekorea_integration_checklist.md: PR ref | — | NO | — | HIGH |
| docs/ops/PROJECT_STRUCTURE.md | file | SAFE-MOVE | 0 inbound refs from outside; only self-references | 0 | — | docs/legacy/ops_old/PROJECT_STRUCTURE.md | NO | docs/ops/INDEX.md (central ops index) | LOW |
| docs/ops/ROUND21_EXECUTION_GUIDE.md | file | NEEDS-STUB | Round-specific guide; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/ops_old/ROUND21_EXECUTION_GUIDE.md | YES | — | MEDIUM |
| docs/ops/ROUND24_EXECUTION_GUIDE.md | file | NEEDS-STUB | Round-specific guide; 1 ref from tree only | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | docs/legacy/ops_old/ROUND24_EXECUTION_GUIDE.md | YES | — | MEDIUM |

### docs/ops/dashboard/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/ops/dashboard/EXPORT_CONTRACT_v0.md | file | KEEP | Dashboard export contract; 6 refs from tools and dashboard docs | 6 | tools/append_progress_event_v0.py: docstring; tools/ingest_round_progress_events_v0.py: docstring; tools/render_dashboard_v0.py: code path | — | NO | — | HIGH |
| docs/ops/dashboard/PLAN_v0.yaml | file | KEEP | Dashboard plan data; 6 refs from tools and docs | 6 | tools/render_dashboard_v0.py: code path; tools/append_progress_event_v0.py: CLI help; docs/ops/PROJECT_DASHBOARD.md: data source | — | NO | — | HIGH |
| docs/ops/dashboard/LAB_SOURCES_v0.yaml | file | KEEP | Lab sources data; 5 refs from tools and docs | 5 | tools/render_dashboard_v0.py: code path; docs/ops/dashboard/EXPORT_CONTRACT_v0.md: schema ref; docs/ops/PROJECT_DASHBOARD.md: data source | — | NO | — | HIGH |
| docs/ops/dashboard/FINAL_LINT_CHECKLIST.md | file | SAFE-MOVE | 0 inbound refs; one-time lint report | 0 | — | docs/legacy/ops_old/FINAL_LINT_CHECKLIST.md | NO | — | LOW |
| docs/ops/dashboard/VERIFICATION_REPORT.md | file | SAFE-MOVE | 0 inbound refs; one-time verification output | 0 | — | docs/legacy/reports_old/dashboard_VERIFICATION_REPORT.md | NO | — | LOW |
| docs/ops/dashboard/PATCH_BLOCKS.md | file | NEEDS-STUB | 1 ref from contracts/VERIFICATION_REPORT.md | 1 | contracts/VERIFICATION_REPORT.md: inline "see PATCH_BLOCKS.md" | docs/legacy/ops_old/dashboard_PATCH_BLOCKS.md | YES | — | MEDIUM |

### docs/ops/templates/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/ops/templates/adr_stub.md | file | KEEP | ADR template; linked from ops INDEX | 2 | docs/ops/INDEX.md: template listing link; docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/ops/templates/report_facts_stub.md | file | KEEP | Facts report template; linked from ops INDEX | 2 | docs/ops/INDEX.md: template listing link; docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/ops/templates/spec_stub.md | file | KEEP | Spec template; linked from ops INDEX | 2 | docs/ops/INDEX.md: template listing link; docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/ops/templates/baseline_candidate_stub.md | file | KEEP | Baseline candidate template; operational | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/ops/templates/golden_candidate_stub.md | file | KEEP | Golden candidate template; operational | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/ops/templates/baseline_update_proposal.md | file | KEEP | Baseline update proposal template; operational | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |

### docs/ops/rounds/ and docs/ops/pr_bodies/ (Grouped)

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/ops/rounds/README.md | file | KEEP | Rounds directory guide; GUARDRAILS protected | 4 | docs/ops/GUARDRAILS.md: protected file list; docs/ops/INDEX.md: link; contracts/CHANGESET_REPORT.md: scope table | — | NO | — | HIGH |
| docs/ops/rounds/ROUND_TEMPLATE.md | file | KEEP | Round template; 1 ref from LEGACY_MAP | 1 | docs/LEGACY_MAP.md: link ref | — | NO | — | MEDIUM |
| docs/ops/rounds/round40-71.md | dir | KEEP | Operational round records (30 files); append-only history | N/A | (individual round files cross-reference each other and operational docs) | — | NO | — | HIGH |
| docs/ops/pr_bodies/ | dir | KEEP | PR body archive (40+ files); historical PR records | N/A | (PR body files reference ops docs, verification docs, and each other) | — | NO | — | HIGH |

### docs/verification/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/verification/golden_s0_freeze_v0.md | file | KEEP | Golden S0 freeze contract; 9 refs | 9 | SYNC_HUB.md: reference; docs/ops/COMMIT_POLICY.md: link; docs/ops/INDEX.md: link | — | NO | — | HIGH |
| docs/verification/curated_v0_gate_draft_v0.md | file | KEEP | Curated v0 gate draft; 6 refs | 6 | docs/ops/COMMIT_POLICY.md: link; docs/sync/CURRENT_STATE.md: file tree; docs/policies/validation/curated_v0_realdata_gate_v0.md: link | — | NO | — | HIGH |
| docs/verification/kpi_diff_contract_v0.md | file | KEEP | KPI diff contract; 4 refs | 4 | docs/ops/COMMIT_POLICY.md: link; docs/sync/CURRENT_STATE.md: file tree; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | HIGH |
| docs/verification/round_registry_contract_v0.md | file | KEEP | Round registry contract; 4 refs | 4 | docs/ops/COMMIT_POLICY.md: link; docs/sync/CURRENT_STATE.md: file tree; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | HIGH |
| docs/verification/lineage_manifest_contract_v0.md | file | KEEP | Lineage manifest contract; 3 refs | 3 | docs/ops/COMMIT_POLICY.md: link; docs/ops/PROJECT_STRUCTURE.md: tree; docs/ops/pr_bodies/pr_body_round6_lineage_golden_registry.md: PR scope | — | NO | — | MEDIUM |
| docs/verification/round_charter_template.md | file | KEEP | Round charter template; 3 refs | 3 | REPO_STRUCTURE_GUIDE.md: description; docs/ops/PROJECT_STRUCTURE.md: tree; docs/ops/pr_bodies/pr_body_ops_round_charter.md: PR scope | — | NO | — | MEDIUM |
| docs/verification/round_ops_v0.md | file | KEEP | Round operations doc; 3 refs | 3 | REPO_STRUCTURE_GUIDE.md: description; docs/ops/PROJECT_STRUCTURE.md: tree; docs/ops/pr_bodies/pr_body_team_system_v0_2.md: PR scope | — | NO | — | MEDIUM |
| docs/verification/visual_provenance_contract_v0.md | file | KEEP | Visual provenance contract; 3 refs | 3 | docs/ops/PROJECT_STRUCTURE.md: tree; docs/ops/pr_bodies/pr_body_round7_visual_provenance.md: PR scope; docs/ops/pr_bodies/pr_body_round7b_visual_skip_artifacts.md: policy ref | — | NO | — | MEDIUM |
| docs/verification/golden_registry_contract_v0.md | file | KEEP | Golden registry contract; 2 refs | 2 | docs/ops/PROJECT_STRUCTURE.md: tree; docs/ops/pr_bodies/pr_body_round6_lineage_golden_registry.md: PR scope | — | NO | — | MEDIUM |

### docs/validation/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/validation/measurement_metadata_schema_v0.md | file | KEEP | Measurement metadata schema; code-referenced | 3 | core/measurements/metadata_v0.py: docstring contract ref; core/measurements/core_measurements_v0.py: header comment ref; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |

### docs/policies/ (Active Measurement Policy Framework)

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/policies/INDEX.md | file | KEEP | Policy registry; 1 ref | 1 | SYNC_HUB_FILE_INDEX.md: file index | — | NO | — | MEDIUM |
| docs/policies/MEASUREMENTS_BUNDLE.md | file | KEEP | Measurement policy bundle; 1 ref | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/policies/measurements/CONTRACT_INTERFACE_CHEST_V0.md | file | KEEP | Chest contract interface; 8 refs from code, tests, bundle | 8 | DB_GUIDE.md: file_path example; tests/test_db_artifacts_smoke.py: layer inference test; docs/policies/MEASUREMENTS_BUNDLE.md: contract anchor | — | NO | — | HIGH |
| docs/policies/measurements/SEMANTIC_DEFINITION_BUST_VNEXT.md | file | KEEP | Bust semantic definition; 8 refs from code and policy docs | 8 | core/measurements/bust_underbust_v0.py: code comment; docs/policies/measurements/CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md: semantic anchor; docs/policies/measurements/GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md: semantic anchor | — | NO | — | HIGH |
| docs/policies/measurements/SEMANTIC_DEFINITION_CHEST_VNEXT.md | file | KEEP | Chest semantic definition; 8 refs | 8 | DB_GUIDE.md: file_path example; tests/test_db_artifacts_smoke.py: layer inference test; docs/policies/MEASUREMENTS_BUNDLE.md: semantic anchor | — | NO | — | HIGH |
| docs/policies/measurements/CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md | file | KEEP | Bust/underbust contract interface; 7 refs from code and docs | 7 | core/measurements/bust_underbust_v0.py: code comment; docs/sync/CURRENT_STATE.md: change log; docs/policies/measurements/GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md: contract anchor | — | NO | — | HIGH |
| docs/policies/measurements/SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md | file | KEEP | Underbust semantic definition; 6 refs | 6 | core/measurements/bust_underbust_v0.py: code comment; docs/policies/measurements/CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md: semantic anchor; docs/policies/measurements/INDEX.md: SoT table | — | NO | — | HIGH |
| docs/policies/measurements/SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md | file | KEEP | Circumference semantic definition; 5 refs | 5 | docs/policies/MEASUREMENTS_BUNDLE.md: semantic anchor; docs/policies/measurements/CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md: semantic anchor; docs/policies/measurements/INDEX.md: SoT table | — | NO | — | HIGH |
| docs/policies/measurements/CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md | file | KEEP | Circumference contract interface; 5 refs | 5 | docs/policies/MEASUREMENTS_BUNDLE.md: contract anchor; docs/policies/measurements/INDEX.md: SoT table; docs/policies/measurements/README.md: link | — | NO | — | HIGH |
| docs/policies/measurements/GEOMETRIC_DESIGN_CHEST_V0.md | file | KEEP | Chest geometric design; 5 refs from code, tests, bundle | 5 | DB_GUIDE.md: file_path example; tests/test_db_artifacts_smoke.py: layer inference test; docs/policies/MEASUREMENTS_BUNDLE.md: bundle ref | — | NO | — | HIGH |
| docs/policies/measurements/VALIDATION_FRAME_HIP_V0.md | file | KEEP | Hip validation frame; 4 refs | 4 | docs/policies/measurements/INDEX.md: SoT table; docs/ops/PROJECT_STRUCTURE.md: tree; SYNC_HUB_FILE_INDEX.md: index | — | NO | — | HIGH |
| docs/policies/measurements/VALIDATION_FRAME_THIGH_V0.md | file | KEEP | Thigh validation frame; 4 refs | 4 | docs/policies/measurements/INDEX.md: SoT table; docs/ops/PROJECT_STRUCTURE.md: tree; SYNC_HUB_FILE_INDEX.md: index | — | NO | — | HIGH |
| docs/policies/measurements/VALIDATION_FRAME_CHEST_V0.md | file | KEEP | Chest validation frame; 3 refs | 3 | docs/policies/measurements/INDEX.md: SoT table; docs/ops/PROJECT_STRUCTURE.md: tree; SYNC_HUB_FILE_INDEX.md: index | — | NO | — | MEDIUM |
| docs/policies/measurements/VALIDATION_FRAME_CIRCUMFERENCE_V0.md | file | KEEP | Circumference validation frame; 3 refs | 3 | docs/policies/measurements/INDEX.md: SoT table; docs/ops/PROJECT_STRUCTURE.md: tree; SYNC_HUB_FILE_INDEX.md: index | — | NO | — | MEDIUM |
| docs/policies/measurements/GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md | file | KEEP | Bust/underbust geometric design; 3 refs | 3 | docs/policies/measurements/README.md: link; docs/policies/measurements/INDEX.md: SoT table; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/policies/measurements/VALIDATION_FRAME_BUST_UNDERBUST_V0.md | file | KEEP | Bust/underbust validation frame; 3 refs | 3 | docs/policies/measurements/INDEX.md: SoT table; docs/policies/measurements/README.md: link; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/policies/apose_normalization/v1.1.md | file | KEEP | A-pose normalization policy; 3 refs | 3 | docs/policies/INDEX.md: policy registry; SYNC_HUB_FILE_INDEX.md: index; tools/db_upsert.py: CLI example | — | NO | — | MEDIUM |
| docs/policies/measurements/contract_template.md | file | KEEP | Measurement contract template; 2 refs | 2 | SYNC_HUB_FILE_INDEX.md: index; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/policies/measurements/구현방법규칙.md | file | KEEP | Implementation rules; 1 ref | 1 | SYNC_HUB_FILE_INDEX.md: index | — | NO | — | MEDIUM |

### docs/judgments/

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/judgments/INDEX.md | file | KEEP | Judgment index; linked from ops INDEX | 2 | docs/ops/INDEX.md: link; docs/ops/JUDGMENTS_POLICY.md: link | — | NO | — | MEDIUM |
| docs/judgments/measurements/CHEST_V0_JUDGMENT_20260121_R1.md | file | KEEP | Judgment record; 3 refs | 3 | DB_GUIDE.md: file_path example; SYNC_HUB_FILE_INDEX.md: index; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/judgments/measurements/CIRCUMFERENCE_V0_JUDGMENT.md | file | KEEP | Judgment record; 2 refs | 2 | SYNC_HUB_FILE_INDEX.md: index; docs/ops/PROJECT_STRUCTURE.md: tree | — | NO | — | MEDIUM |
| docs/judgments/measurements/MEASUREMENTS_V0_BUNDLE_JUDGMENT_20260121_R1.md | file | KEEP | Bundle judgment record; 1 ref | 1 | docs/ops/PROJECT_STRUCTURE.md: tree listing | — | NO | — | MEDIUM |
| docs/judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md | file | KEEP | Judgment entry template; linked from ops INDEX | 1 | docs/ops/INDEX.md: template link | — | NO | — | MEDIUM |

### docs/archive/ (Already Archived)

| item_path | item_type | classification | why_facts | inbound_refs_count | inbound_refs_samples | proposed_new_path | stub_required | replaced_by | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| docs/archive/constitution/delivery_modes.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/plans_old/delivery_modes.md | YES | — | MEDIUM |
| docs/archive/constitution/README.md | file | NEEDS-STUB | Already archived; 2 refs from inventory files | 2 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path | docs/legacy/plans_old/constitution_README.md | YES | — | MEDIUM |
| docs/archive/constitution/governance_policy.md | file | NEEDS-STUB | Already archived; 4 refs (3 inventory + 1 sibling README) | 4 | docs/archive/constitution/README.md: relative link; SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/plans_old/governance_policy.md | YES | — | HIGH |
| docs/archive/constitution/kpi_decomposition.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/plans_old/kpi_decomposition.md | YES | — | MEDIUM |
| docs/archive/constitution/quality_gates.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/plans_old/quality_gates.md | YES | — | MEDIUM |
| docs/archive/constitution/releases.md | file | NEEDS-STUB | Already archived; 2 refs from inventory files | 2 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path | docs/legacy/plans_old/releases.md | YES | — | MEDIUM |
| docs/archive/constitution/schema_contract.md | file | NEEDS-STUB | Already archived; 4 refs (3 inventory + 1 sibling README) | 4 | docs/archive/constitution/README.md: relative link; SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/contracts_old/schema_contract.md | YES | — | HIGH |
| docs/archive/constitution/telemetry_schema.md | file | NEEDS-STUB | Already archived; 4 refs (3 inventory + 1 sibling README) | 4 | docs/archive/constitution/README.md: relative link; SYNC_HUB_FILE_INDEX.md: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/plans_old/telemetry_schema.md | YES | — | HIGH |
| docs/archive/prompts/gemini_audit_prompt.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/misc_old/gemini_audit_prompt.md | YES | — | MEDIUM |
| docs/archive/prompts/gpt_v1_prompt.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/misc_old/gpt_v1_prompt.md | YES | — | MEDIUM |
| docs/archive/prompts/gpt_v3_prompt.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/misc_old/gpt_v3_prompt.md | YES | — | MEDIUM |
| docs/archive/review_loop_contract.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/contracts_old/archive_review_loop_contract.md | YES | — | MEDIUM |
| docs/archive/samples/v3_execution_pack_sample.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/misc_old/archive_v3_execution_pack_sample.md | YES | — | MEDIUM |
| docs/archive/stop_triggers.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/ops_old/archive_stop_triggers.md | YES | — | MEDIUM |
| docs/archive/sync/CURRENT_STATE.md | file | NEEDS-STUB | Already archived; 2 refs from inventory files | 2 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path | docs/legacy/ops_old/archive_CURRENT_STATE.md | YES | docs/sync/CURRENT_STATE.md | MEDIUM |
| docs/archive/templates/CURSOR_TASK_TEMPLATE.md | file | NEEDS-STUB | Already archived; 3 refs from inventory files | 3 | SYNC_HUB_FILE_INDEX.md: literal path; REPO_FILES.txt: literal path; docs/ops/PROJECT_STRUCTURE.md: tree | docs/legacy/misc_old/CURSOR_TASK_TEMPLATE.md | YES | — | MEDIUM |

---

## Summary Counts

| Classification | Count |
|---|---|
| **KEEP** | 89 |
| **SAFE-MOVE** | 11 |
| **NEEDS-STUB** | 40 |
| **Total inventoried** | 140 |

---

## Top Risks

Items with HIGH risk_level (inbound_refs_count >= 4) that are NOT classified as KEEP. These require careful handling in Round 3/4 moves.

| # | item_path | inbound_refs_count | why_risky |
|---|---|---|---|
| 1 | docs/stop_triggers.md | 7 | Referenced by review_loop_contract, archive prompts, and archive docs; active reference chain |
| 2 | SYNC_HUB_FILE_INDEX.md | 4 | Operational file index referenced by REPO_STRUCTURE_GUIDE and ops docs; moving would break index lookups |
| 3 | docs/evidence_schema_v1.md | 4 | Referenced by VALIDATE_EVIDENCE_INVESTIGATION.md and inventory files; part of evidence validation chain |
| 4 | docs/review_loop_contract.md | 4 | Referenced by inventory files; has archive duplicate at docs/archive/review_loop_contract.md |
| 5 | docs/reports/AN-v11-R1.md | 4 | Referenced by tools/db_upsert.py as code example; inventory files |
| 6 | docs/archive/constitution/governance_policy.md | 4 | Cross-referenced by sibling docs/archive/constitution/README.md; inventory files |
| 7 | docs/archive/constitution/schema_contract.md | 4 | Cross-referenced by sibling docs/archive/constitution/README.md; inventory files |
| 8 | docs/archive/constitution/telemetry_schema.md | 4 | Cross-referenced by sibling docs/archive/constitution/README.md; inventory files |

**Note**: All 8 HIGH-risk non-KEEP items have references primarily from inventory/listing files (SYNC_HUB_FILE_INDEX.md, REPO_FILES.txt, PROJECT_STRUCTURE.md) or from other legacy/archive documents. The functional risk of moving these items is LOW in practice, but stubs are required per the inbound reference facts.

---

## Missing Input Files (Facts)

- `docs/legacy/LEGACY_INDEX.md` — Does not exist. Expected by SSoT_PACK_v1 sec 5 for legacy lineage mapping.
- `docs/ops/MASTER_PLAN.md` — Does not exist on disk. Referenced in CLAUDE.md Key Documents section (dangling pointer).
- `docs/plans/unlock/unlock_conditions_u1_u2.md` (SSoT Pack S4) — Does not exist at declared canonical path.
- `docs/plans/phase/phase_plan_unlock_driven.md` (SSoT Pack S5) — Does not exist at declared canonical path.

---

End of REFERENCE_INVENTORY_v1
