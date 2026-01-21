# SYNC\_STATE

**Guard ref**: [.github/workflows/ci-guard-sync-state.yml](../../.github/workflows/ci-guard-sync-state.yml) - Official definition of guard-sync-state CI rule.

snapshot:
id:
status: candidate
last\_change: code
version\_keys:
snapshot: false
semantic: false
geometry\_impl: false
dataset: false

pipeline:
position: rd | local\_validation | promotion | release\_hold | production
position: local\_validation
active\_runbook:
- DB/metadata pipeline updated: artifacts table added for 5-Layer indexing
- Migration script with auto-backup: tools/migrate_add_artifacts_table.py
- db_upsert.py enhanced: artifacts upsert with layer inference, section_id/method_tag in extra_json
- Smoke test added: tests/test_db_artifacts_smoke.py

signals:
validation:
status: pass | warning | fail
uncertainty\_trend: up | stable | down

status: warning

uncertainty\_trend: stable
cost:
pure: up | stable | down
egress: up | stable | down
cost\_model\_version:
latency: up | stable | down

decision:
promotion: not\_reviewed | deferred | eligible | blocked
release: not\_started | hold | released
authority: rd\_lead+ops\_lead
artifacts:
adr:
validation\_report:

constraints:
technical:
- HIP measurement function (core/measurements/hip\_v0.py) not yet implemented
- CHEST measurement function (core/measurements/chest\_v0.py) not yet implemented
operational:
-

## allowed\_actions:

## forbidden\_actions:

last\_update:
date: 2026-01-21
trigger: artifacts_db_indexing

changed\_paths:

* verification/runners/verify\_circumference\_v0.py
* verification/runners/verify\_chest\_v0.py
* verification/runners/verify\_hip\_v0.py
* verification/datasets/golden/circumference\_v0/
* verification/datasets/golden/chest\_v0/
* verification/datasets/golden/hip\_v0/
* tests/test\_circumference\_v0\_validation\_contract.py
* tests/test\_chest\_v0\_validation\_contract.py
* tests/test\_hip\_v0\_validation\_contract.py
* docs/policies/measurements/VALIDATION\_FRAME\_CIRCUMFERENCE\_V0.md
* docs/policies/measurements/VALIDATION\_FRAME\_CHEST\_V0.md
* docs/policies/measurements/VALIDATION\_FRAME\_HIP\_V0.md
