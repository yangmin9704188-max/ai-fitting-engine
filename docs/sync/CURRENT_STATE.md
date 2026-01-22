# SYNC\_STATE

**Guard ref**: [.github/workflows/guard-sync-state.yml](../../.github/workflows/guard-sync-state.yml) - Official definition of guard-sync-state CI rule.

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
- bust/underbust geometric v0 엔트리포인트 추가 (core/measurements/bust_underbust_v0.py)
- contract violation = NaN+warnings 정책을 테스트로 봉인 (tests/test_bust_underbust_v0_smoke.py)
- UNDERBUST verts-based 측정 v0 heuristic 구현 (NOT_IMPLEMENTED 경고 제거, 실패 시 warnings 태그로 사실 기록)
- perimeter 계산을 polar angle sorting 기반으로 안정화 (unordered slice points에서도 의미 있는 circumference 산출)
- smoke test로 unordered ring 회귀 봉인
- facts-only runner 추가 (verification/tools/run_bust_underbust_facts_v0.py): 무판정 통계 기록, NaN rate/warnings 빈도/co-occurrence 집계, JSON+CSV 출력
- NPZ loader가 object-array verts/case_id를 지원하도록 안정화 (스키마 불일치 시 크래시 대신 0케이스 summary 기록 후 정상 종료, out_dir 자동 생성)

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
- UNDERBUST verts-based measurement uses v0 heuristic (y-axis slicing, median perimeter selection)
operational:
-

## allowed\_actions:

## forbidden\_actions:

last\_update:
date: 2026-01-22
trigger: underbust_verts_geometric_v0_impl

changed\_paths:

* .github/workflows/guard-sync-state.yml (renamed from ci-guard-sync-state.yml)
* core/measurements/bust_underbust_v0.py
* tests/test_bust_underbust_v0_smoke.py
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
