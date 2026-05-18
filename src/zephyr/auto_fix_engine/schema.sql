-- Auto Fix Engine Schema — MOD-INF-031
-- [BLUEPRINT] MOD-INF-031 | 03_modules/_cross_layer/auto-fix-engine/blueprint.md | §4.2

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS fix_actions (
    action_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'l1_rule',
    status TEXT NOT NULL DEFAULT 'pending',
    target TEXT NOT NULL,
    before_text TEXT DEFAULT '',
    after_text TEXT DEFAULT '',
    metadata_json TEXT DEFAULT '{}',
    audit_trail_id TEXT DEFAULT '',
    timestamp TEXT NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'high',
    attempts INTEGER NOT NULL DEFAULT 1,
    retry_count INTEGER NOT NULL DEFAULT 0,
    model TEXT DEFAULT '',
    context_sources_json TEXT DEFAULT '[]',
    token_cost INTEGER NOT NULL DEFAULT 0,
    verified INTEGER NOT NULL DEFAULT 0,
    escalated INTEGER NOT NULL DEFAULT 0,
    sandbox_verified INTEGER NOT NULL DEFAULT 0,
    fingerprint TEXT NOT NULL,
    blast_radius_json TEXT DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_fix_actions_status ON fix_actions(status);
CREATE INDEX IF NOT EXISTS idx_fix_actions_type ON fix_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_fix_actions_target ON fix_actions(target);
CREATE INDEX IF NOT EXISTS idx_fix_actions_fingerprint ON fix_actions(fingerprint);
CREATE INDEX IF NOT EXISTS idx_fix_actions_timestamp ON fix_actions(timestamp);

CREATE TABLE IF NOT EXISTS fix_history (
    fix_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    before_hash TEXT DEFAULT '',
    after_hash TEXT DEFAULT '',
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 0,
    verifier TEXT DEFAULT '',
    revert_possible INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_fix_history_target ON fix_history(target);
CREATE INDEX IF NOT EXISTS idx_fix_history_timestamp ON fix_history(timestamp);

CREATE TABLE IF NOT EXISTS fix_dead_letters (
    dead_letter_id TEXT PRIMARY KEY,
    original_fix_json TEXT NOT NULL,
    failure_reason TEXT DEFAULT '',
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_retry TEXT NOT NULL,
    escalated INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dead_letters_retry ON fix_dead_letters(retry_count);
CREATE INDEX IF NOT EXISTS idx_dead_letters_escalated ON fix_dead_letters(escalated);

CREATE TABLE IF NOT EXISTS fix_idempotency (
    fingerprint TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    result_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_idempotency_expires ON fix_idempotency(expires_at);

CREATE TABLE IF NOT EXISTS fix_budget_consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT NOT NULL,
    level TEXT NOT NULL,
    cost INTEGER NOT NULL DEFAULT 1,
    tokens INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL,
    session_id TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_budget_timestamp ON fix_budget_consumption(timestamp);
CREATE INDEX IF NOT EXISTS idx_budget_session ON fix_budget_consumption(session_id);

CREATE TABLE IF NOT EXISTS fix_compliance (
    compliance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fix_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    before_hash TEXT DEFAULT '',
    after_hash TEXT DEFAULT '',
    timestamp TEXT NOT NULL,
    actor TEXT DEFAULT 'auto_fix_engine',
    confidence TEXT DEFAULT '',
    rbac_decision TEXT DEFAULT '',
    validation_result TEXT DEFAULT '',
    audit_trail_id TEXT DEFAULT '',
    tamper_proof_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_compliance_fix_id ON fix_compliance(fix_id);
CREATE INDEX IF NOT EXISTS idx_compliance_timestamp ON fix_compliance(timestamp);

CREATE TABLE IF NOT EXISTS fix_patterns (
    pattern_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    dimension TEXT NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 1,
    success_rate REAL NOT NULL DEFAULT 0.0,
    last_seen TEXT NOT NULL,
    pattern_data TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_patterns_dimension ON fix_patterns(dimension);
CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON fix_patterns(frequency DESC);
