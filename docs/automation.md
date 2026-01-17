# Automation Status & Recommendations

## Overview

This document describes the current state of automation in the AI Fitting Engine project, guidelines for when to recommend new automation, and day-to-day operating routines.

## Automation Status (Factory Runtime)

### ✅ Currently Automated

**1. Stop Trigger & Slack Notifications**
- **Workflow**: `.github/workflows/stop-trigger-slack.yml`
- **Trigger**: PR events (opened, synchronize, reopened) + `workflow_dispatch`
- **Function**: Extracts stop triggers from evidence files (`execution_report.md`, `pending_review.json`) or uses `triggers.json`. Sends Slack notifications when any stop trigger is `true`.
- **Policy**: `tools/stop_triggers.yaml` (Policy-as-Data)
- **Output**: `stop_report.md` (artifact), Slack message (3-line summary + links)
- **Documentation**: `docs/stop_triggers.md`

**2. Evidence Schema Validation**
- **Workflow**: `.github/workflows/evidence.yml`
- **Trigger**: PR events with `artifacts/**/runs/**` changes
- **Function**: Validates Evidence Package schema v1.0 (manifest.json, metrics.json, summary.md). Applies PASS/FAIL rules (delta, delta_pct, fail_rate thresholds).
- **Skip Conditions**: Infra-only PRs (`.github/**, tools/**, docs/**` only), no runs changed
- **Script**: `tools/validate_evidence.py`
- **Schema**: `docs/evidence_schema_v1.md`

**3. Infra-Only PR Detection**
- **Function**: Automatically skips evidence validation for infrastructure-only changes
- **Allowlist**: `.github/**, tools/**, docs/**`
- **Implementation**: Path-based detection in `evidence-check` workflow

**4. Local Evidence Packing**
- **Script**: `tools/pack_evidence.py`
- **Function**: Generates Evidence Package from local experiment results
- **Output**: `artifacts/<task>/<policy_version>/runs/<run_id>/` with manifest.json, metrics.json, summary.md
- **Documentation**: `docs/evidence_packer.md`

### ❌ Not Yet Automated

- Policy version tagging (manual tag creation required)
- Regression threshold adjustment (requires manual PR review)
- Evidence Package archival (old runs are kept in git, no archival policy)
- Automated policy comparison reports (requires manual execution of verification runners)
- Multi-run batch validation (validate_evidence.py handles one PR at a time)

## When to Recommend Automation (Auto-Advice Script)

### Recommendation Criteria (Cost Priority)

**Tier 1: Zero-Cost Automation (Always Recommend)**
- Repetitive manual steps that can be replaced by existing GitHub Actions / scripts
- Documentation updates that are generated from code/config
- Format validation or schema checking

**Tier 2: Low-Cost Automation (< $10/month)**
- Lightweight API calls (e.g., Slack webhooks, GitHub API)
- Simple file generation or transformation
- Basic cron jobs or scheduled workflows

**Tier 3: Medium-Cost Automation ($10-50/month)**
- Require cost-benefit analysis
- Examples: Cloud compute for batch validation, third-party SaaS integrations
- Should justify ROI with time savings or quality improvements

**Tier 4: High-Cost Automation (> $50/month)**
- Only recommend if critical for scalability or quality
- Requires explicit approval and budget allocation

### Decision Matrix

| Scenario | Manual Effort | Frequency | Recommend? | Priority |
|----------|--------------|-----------|------------|----------|
| PR description format check | 2 min | Every PR | ✅ Yes (Tier 1) | High |
| Manual tag creation after policy release | 5 min | Every release | ✅ Yes (Tier 1) | Medium |
| Evidence Package archival | 10 min | Monthly | ⚠️ Maybe (Tier 2) | Low |
| Automated policy comparison reports | 30 min | Weekly | ❌ No (Tier 4) | Low |

### Automation Request Process

1. **Identify the Repetitive Task**
   - Document current manual steps
   - Estimate time per execution and frequency
   - Calculate monthly time cost

2. **Assess Feasibility**
   - Can it be done with existing tools? (GitHub Actions, Python scripts)
   - What dependencies are needed? (APIs, cloud resources)
   - What is the implementation cost? (development time)

3. **Create Issue/PR**
   - Label: `enhancement` / `automation`
   - Include cost tier, ROI estimate, implementation sketch
   - Link to this document

4. **Implementation**
   - Follow YAML minimalism principle (logic in Python, not inline bash)
   - Add documentation (docs/*.md)
   - Test with workflow_dispatch before enabling on PR events

## Day-to-Day Operating Routine (Hybrid Routine)

### Before Starting Work

1. **Check Current Branch**: `git status`
2. **Sync with Main**: `git pull origin main`
3. **Create Feature Branch**: `git checkout -b feat/feature-name` or `fix/issue-name`

### During Development

1. **Run Local Tests**: Execute relevant verification scripts if applicable
2. **Commit Frequently**: Atomic commits with clear messages
3. **Check Workflow Status**: Monitor GitHub Actions if workflows are affected

### Before PR

1. **Generate Evidence Package** (if applicable):
   ```bash
   python tools/pack_evidence.py \
     --task <task> --policy_version <version> --run_id <id> \
     --primary_value <value> --baseline_ref <ref> --baseline_primary_value <value>
   ```

2. **Verify Infra Changes**: If changing `.github/**, tools/**, docs/**`, ensure no unintended evidence validation runs

3. **Check Stop Triggers**: Ensure `triggers.json` or evidence files are correct if modifying policy/measurement logic

### After PR Creation

1. **Monitor Checks**: 
   - `evidence-check`: Should pass if artifacts are valid
   - `stop-trigger-slack`: Should not fire unless stop triggers are true

2. **Review Slack Notifications**: If stop triggers fired, address the issues before merging

3. **Wait for Approval**: PRs require review before merging to `main`

### After Merge

1. **Tag Policy Releases** (if applicable):
   ```bash
   git tag -a <policy_name>_<version> -m "Release <policy_name> v<version>"
   git push origin <policy_name>_<version>
   ```

2. **Update Documentation**: If automation or workflows changed, update `docs/automation.md`

## Tagging Policy

### Policy Version Tags

**Format**: `<policy_name>_v<major>.<minor>`

**Examples**:
- `shoulder_width_v1.2`
- `smart_mapper_v0.1`
- `apose_v1.1`

**When to Tag**:
- When a policy is marked as `Frozen` (see Policy Lifecycle in `ReadMe.txt`)
- When releasing a new policy version for production use
- When establishing a baseline for regression testing

**Tag Creation**:
```bash
git tag -a <policy_name>_v<version> -m "Release <policy_name> v<version>"
git push origin <policy_name>_v<version>
```

### Workflow Version Tags

**Format**: `infra/<workflow-name>-v<version>`

**Examples**:
- `infra/stop-trigger-python-v1.1`
- `infra/stop-report-evidence-v1.0`
- `infra/evidence-schema-v1.0`

**When to Tag**:
- After stabilizing a workflow or automation script
- After refactoring that changes behavior significantly
- When documenting a stable state for rollback purposes

**Tag Creation**:
```bash
git tag -a infra/<workflow-name>-v<version> -m "Stable <workflow-name> v<version>"
git push origin infra/<workflow-name>-v<version>
```

### Evidence Run Tags (Optional)

Evidence runs are identified by `run_id` in their manifest.json, not by git tags. Tags are only used for:
- Policy versions (baselines for regression)
- Workflow versions (automation stability)

## Maintenance Guidelines

### Weekly

- Review GitHub Actions workflow runs for failures
- Check for outdated dependencies in `requirements*.txt`

### Monthly

- Archive old evidence runs (if archival policy is established)
- Review automation documentation for accuracy
- Assess new automation opportunities (use Auto-Advice criteria)

### Quarterly

- Review cost of any paid automation (Tier 3+)
- Update tagging policy if project structure changes
- Consolidate or deprecate unused workflows

## References

- Stop Triggers: `docs/stop_triggers.md`
- Evidence Schema: `docs/evidence_schema_v1.md`
- Evidence Packer: `docs/evidence_packer.md`
- Project Constitution: `ReadMe.txt`
