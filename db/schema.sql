-- SQLite schema for AI Fitting Engine metadata
-- Purpose: State/search/aggregation metadata only
-- Full documents are stored in Git, not DB

-- 1. policies: Policy metadata
CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('draft', 'candidate', 'frozen', 'archived', 'deprecated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    frozen_at TIMESTAMP,
    frozen_git_tag TEXT,
    frozen_commit_sha TEXT,
    base_commit TEXT,
    UNIQUE(name, version)
);

-- 2. experiments: Experiment metadata
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT NOT NULL UNIQUE,
    policy_id INTEGER,
    run_id TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_json TEXT,
    FOREIGN KEY (policy_id) REFERENCES policies(id)
);

-- 3. reports: Report metadata
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,
    report_type TEXT,
    result TEXT CHECK(result IN ('PASS', 'FAIL', 'PARTIAL')),
    gate_failed TEXT,
    evaluated_policy_commit TEXT,
    verification_tool_commit TEXT,
    artifacts_path TEXT,
    dataset TEXT,
    metrics_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);

-- 4. policy_changes: Policy change history
CREATE TABLE IF NOT EXISTS policy_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    change_type TEXT,
    from_version TEXT,
    to_version TEXT,
    commit_sha TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policy_id) REFERENCES policies(id)
);

-- 5. specs: Specification metadata
CREATE TABLE IF NOT EXISTS specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_type TEXT,
    related_policy_id INTEGER,
    git_commit TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (related_policy_id) REFERENCES policies(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status);
CREATE INDEX IF NOT EXISTS idx_experiments_policy_id ON experiments(policy_id);
CREATE INDEX IF NOT EXISTS idx_experiments_experiment_id ON experiments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_reports_experiment_id ON reports(experiment_id);
CREATE INDEX IF NOT EXISTS idx_reports_result ON reports(result);
CREATE INDEX IF NOT EXISTS idx_policy_changes_policy_id ON policy_changes(policy_id);
CREATE INDEX IF NOT EXISTS idx_specs_policy_id ON specs(related_policy_id);
