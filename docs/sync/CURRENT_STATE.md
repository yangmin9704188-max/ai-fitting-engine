# SYNC_STATE

snapshot:
  id:
  status: candidate | hold | released
  last_change: code | weight | config | dataset
  version_keys:
    snapshot: true | false
    semantic: true | false
    geometry_impl: true | false
    dataset: true | false

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
    -
  operational:
    -

allowed_actions:
  -
forbidden_actions:
  -

last_update:
  date: 2026-01-19
  trigger: conflict_resolved_and_deleted
