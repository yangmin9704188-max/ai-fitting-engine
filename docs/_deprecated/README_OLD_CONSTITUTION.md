> ⚠️ DEPRECATED
> 본 문서는 2026-XX-XX 기준으로 더 이상 유효하지 않음.
> 현재 유효한 헌법은 docs/constitution/architecture_final_plan.md 를 참조할 것.


# AI Virtual Fitting Engine

Internal Project Constitution & Operating Manual

> **Note**: This README provides an overview. For detailed documentation, see `ReadMe.txt` (constitution) and `docs/` directory.

## Quick Links

- **Project Constitution**: [`ReadMe.txt`](ReadMe.txt) - Hard KPIs, governance, design philosophy
- **Automation Status**: [`docs/automation.md`](docs/automation.md) - Current automation, recommendations, operating routine
- **Stop Triggers**: [`docs/stop_triggers.md`](docs/stop_triggers.md) - Stop trigger definitions and Slack notifications
- **Evidence Schema**: [`docs/evidence_schema_v1.md`](docs/evidence_schema_v1.md) - Evidence Package schema v1.0
- **Evidence Packer**: [`docs/evidence_packer.md`](docs/evidence_packer.md) - Local experiment packaging CLI

## Hard KPIs

All technical and policy decisions prioritize these KPIs:

- **Cost**: < 10원 per inference (cloud/GPU/rendering included)
- **Latency**: 10-30 seconds end-to-end
- **Quality**: B2B commerce-level images, explainable body measurements

## Automation Status

**Currently Automated:**
- ✅ Stop Trigger detection and Slack notifications
- ✅ Evidence Package schema validation (v1.0)
- ✅ Infra-only PR detection (auto-skip validation)
- ✅ Local evidence packing CLI (`tools/pack_evidence.py`)

**Not Yet Automated:**
- ❌ Policy version tagging
- ❌ Evidence Package archival
- ❌ Automated policy comparison reports

See [`docs/automation.md`](docs/automation.md) for details on automation recommendations, day-to-day operating routine, and tagging policy.

## Getting Started

### Local Development

1. Clone repository
2. Install dependencies (see `requirements*.txt` if available)
3. Run local experiments and package results:
   ```bash
   python tools/pack_evidence.py \
     --task <task> --policy_version <version> --run_id <id> \
     --primary_value <value> --baseline_ref <ref> --baseline_primary_value <value>
   ```

### Creating a PR

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes and commit
3. If modifying `.github/**, tools/**, docs/**` only: Evidence validation will be skipped automatically
4. If adding/modifying `artifacts/**/runs/**`: Evidence schema v1.0 validation will run
5. Create PR on GitHub
6. Monitor checks: `evidence-check`, `stop-trigger-slack`

### Workflow Behavior

- **Infra-only PRs** (`.github/**, tools/**, docs/**`): Evidence validation skipped
- **Evidence runs changed** (`artifacts/**/runs/**`): Schema v1.0 validation runs automatically
- **Stop triggers true**: Slack notification sent (3-line summary + links)

## Project Structure

```
├── core/              # Core measurement/policy logic (🔒 sealed)
├── pipelines/         # Execution pipelines
├── verification/      # Verification/regression tests
├── tools/             # Utilities (pack_evidence.py, validate_evidence.py, etc.)
├── docs/              # Documentation
├── artifacts/         # Evidence packages (artifacts/<task>/<version>/runs/<run_id>/)
└── .github/workflows/ # CI/CD workflows
```

## Governance

**Single-Owner Model** (1-person development environment):

| Role | Agent | Responsibility |
|------|-------|----------------|
| Owner | Human | Final decisions, document approval, Git commits/tags |
| Planner | GPT | Policy design, reports, commit/tag requests |
| Advisor | Gemini | Secondary review, logical counterarguments |
| Executor | Cursor | Code implementation, experiments, artifacts |

**Principles:**
- LLMs don't decide; Humans don't infer
- Git is the Source of Truth

## License & Scope

This is an **internal-only** project constitution. Optimized for LLM comprehension, reproducibility, and governance — not for external communication.
