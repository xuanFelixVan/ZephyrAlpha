# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §task-system
# [MODULE] zephyr.governance.persistence.sqlite_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_sqlite_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + SH-DB-001 v2.0）
======================================================================
依据：KBG-0030（SQLite 作为 experimental 元数据层）

物理路径：data/databases/governance.db
Safety  : M（DDL 定义，init_db 幂等执行）

表结构
------
 1. tasks                 — 任务登记表（10 状态流转 + namespace 分类）
 2. task_files            — 任务-文件 N:N 映射表（#21 裁定）
 3. events                — 事件流（DeferredQueue 消费）
 4. knowledge             — KE 索引
 5. gate_runs             — 门禁运行记录（5.18.14 改名，避免与 depgraph gates 同名异构）
 6. circuit_breaker_state — CBG 模块间熔断状态（T-V2-005 experimental）
 7. _schema_version       — Schema 版本追踪（SH-DB-001 v2.0 新增）
 8. slow_queries          — 慢查询记录（SH-DB-001 v2.0 新增）
 9. tx_idempotency        — ATM 事务幂等去重表（SH-DB-001 v2.0 新增）
10. task_events           — Event Sourcing 事件流（DW-0001，UUID PK + 灵活 event_type）
11. task_snapshots        — Event Sourcing 快照（DW-0005，加速 replay）

视图
----
event_log       — tasks × events JOIN（CLI 审计视图）
v_active_tasks  — 活跃任务快照（IN_PROGRESS + READY + RETRY）
v_recent_sessions — 最近 10 个 session 的完成情况

PRAGMA 基线（KBG-0030 §4.3）
-------------------------------
  journal_mode = WAL
  synchronous = NORMAL
  foreign_keys = ON
  busy_timeout = 5000
  temp_store = MEMORY
  wal_autocheckpoint = 4096

用法
----
    from zephyr.governance.persistence.sqlite_schema import init_db, get_db_connection
    from zephyr.shared.io.paths import DB_PATH  # SSoT 源

    init_db()              # 幂等，可重复调用
    conn = get_db_connection()   # 返回配置好 PRAGMA 的连接
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH as _DB_PATH  # 治本(2026-06-30): 别名阻断 re-export, 防止 IDE organize imports 自动加回 from sqlite_schema import DB_PATH

# ---------------------------------------------------------------------------
# DDL — tasks 表
# ---------------------------------------------------------------------------

_DDL_TASKS = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id          TEXT    PRIMARY KEY
                             CHECK(task_id GLOB '[A-Z][A-Z]*-[0-9]*'),
    namespace        TEXT    NOT NULL CHECK(namespace IN ('KBG','CP','KE','STD','DW','SRC','OPS','DM')),
    seq              INTEGER NOT NULL CHECK(seq >= 1),
    title            TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'PENDING'
                             CHECK(status IN (
                                 'PENDING','IN_PROGRESS','COMPLETED','VERIFIED',
                                 'FAILED','BLOCKED','WAITING','READY','RETRY','CANCELLED'
                             )),
    priority         TEXT    NOT NULL DEFAULT 'P2'
                             CHECK(priority IN ('P0','P1','P2','P3','P4')),
    phase            INTEGER NOT NULL CHECK(phase >= 0 AND phase <= 9),
    execution_model  TEXT    NOT NULL
                             CHECK(execution_model IN ('deepseek','glm','claude','kimi','qwen')),
    model_rationale  TEXT,
    fallback_model   TEXT,
    safety_level     TEXT    NOT NULL CHECK(safety_level IN ('L','M','H')),
    directive        TEXT    NOT NULL DEFAULT '',
    idempotent       INTEGER NOT NULL DEFAULT 0 CHECK(idempotent IN (0,1)),
    classification   TEXT    NOT NULL DEFAULT 'internal'
                             CHECK(classification IN ('public','internal','confidential')),
    evolution_policy TEXT    NOT NULL DEFAULT 'extendable'
                             CHECK(evolution_policy IN ('frozen','extendable','rewritable')),
    estimate_hours   REAL    NOT NULL DEFAULT 0 CHECK(estimate_hours >= 0),
    actual_hours     REAL    CHECK(actual_hours IS NULL OR actual_hours >= 0),
    files_in_scope   TEXT    NOT NULL DEFAULT '[]' CHECK(files_in_scope LIKE '[%'),
    deliverables     TEXT    NOT NULL DEFAULT '[]' CHECK(deliverables LIKE '[%'),
    acceptance       TEXT    NOT NULL DEFAULT '[]',
    depends_on       TEXT    NOT NULL DEFAULT '[]',
    tags             TEXT    NOT NULL DEFAULT '[]',
    session_id       TEXT,
    waiting_for      TEXT,
    ready_at         TEXT,
    completed_at     TEXT,
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL,
    is_deleted       INTEGER NOT NULL DEFAULT 0 CHECK(is_deleted IN (0,1)),
    deleted_at       TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — events 表
# ---------------------------------------------------------------------------

_DDL_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
    event_id    TEXT PRIMARY KEY,
    event_type  TEXT NOT NULL
                     CHECK(event_type IN (
                         'file_event','time_event','task_event',
                         'manual_event','metric_event','state_transition',
                         'compensation'
                     )),
    payload     TEXT NOT NULL DEFAULT '{}',
    task_id     TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
    session_id  TEXT,
    created_at  TEXT NOT NULL,
    processed_at TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — knowledge 表
# ---------------------------------------------------------------------------

_DDL_KNOWLEDGE = """
CREATE TABLE IF NOT EXISTS knowledge (
    ke_id               TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    category            TEXT NOT NULL DEFAULT 'general',
    source_file         TEXT NOT NULL,
    source_git_deleted  INTEGER NOT NULL DEFAULT 0 CHECK(source_git_deleted IN (0,1)),
    fingerprint_sha256  TEXT,
    tags                TEXT NOT NULL DEFAULT '[]',
    summary             TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — gates 表
# ---------------------------------------------------------------------------

_DDL_GATES = """
-- 5.18.14 治本（2026-07-01）：governance.db gates 改名 gate_runs，
-- 避免与 depgraph gates（11列 YAML SSoT 只读表）同名异构冲突。
CREATE TABLE IF NOT EXISTS gate_runs (
    gate_run_id  TEXT PRIMARY KEY,
    gate_id      TEXT NOT NULL,
    passed       INTEGER NOT NULL CHECK(passed IN (0,1)),
    details      TEXT NOT NULL DEFAULT '{}',
    artifact_path TEXT,
    session_id   TEXT,
    task_id      TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
    created_at   TEXT NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — circuit_breaker_state 表（T-V2-005 experimental CBG）
# ---------------------------------------------------------------------------

_DDL_CIRCUIT_BREAKER_STATE = """
CREATE TABLE IF NOT EXISTS circuit_breaker_state (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_module    TEXT    NOT NULL,
    target_module    TEXT    NOT NULL,
    state            TEXT    NOT NULL CHECK (state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    failure_count    INTEGER NOT NULL DEFAULT 0,
    last_failure_at  TEXT,
    opened_at        TEXT,
    reason           TEXT,
    created_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    UNIQUE(caller_module, target_module)
)
"""

# ---------------------------------------------------------------------------
# DDL — task_files 表（#21 裁定：N:N 映射）
# ---------------------------------------------------------------------------

_DDL_TASK_FILES = """
CREATE TABLE IF NOT EXISTS task_files (
    task_id     TEXT    NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    file_path   TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'in_scope'
                        CHECK(role IN ('primary', 'in_scope', 'output')),
    UNIQUE(task_id, file_path)
)
"""

# ---------------------------------------------------------------------------
# DDL — _schema_version 表（SH-DB-001 v2.0：Schema 版本追踪）
# ---------------------------------------------------------------------------

_DDL_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS _schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT    NOT NULL,
    description TEXT    NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — slow_queries 表（SH-DB-001 v2.0：慢查询记录）
# ---------------------------------------------------------------------------

_DDL_SLOW_QUERIES = """
CREATE TABLE IF NOT EXISTS slow_queries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    operation       TEXT    NOT NULL,
    duration_ms     REAL    NOT NULL,
    sql_preview     TEXT    NOT NULL,
    params_preview  TEXT,
    recorded_at     TEXT    NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — tx_idempotency 表（SH-DB-001 v2.0：ATM 事务幂等去重）
# ---------------------------------------------------------------------------

_DDL_TX_IDEMPOTENCY = """
CREATE TABLE IF NOT EXISTS tx_idempotency (
    tx_id           TEXT PRIMARY KEY,
    status          TEXT NOT NULL CHECK(status IN ('PREPARED','COMMITTED','ROLLED_BACK','COMPENSATED')),
    started_at      TEXT NOT NULL,
    committed_at    TEXT,
    rolled_back_at  TEXT,
    compensation_at TEXT,
    note            TEXT NOT NULL DEFAULT ''
)
"""

# ---------------------------------------------------------------------------
# DDL — task_events v2 表（DW-0001: Event Sourcing 事件流，UUID PK + 灵活 event_type）
# ---------------------------------------------------------------------------

_DDL_TASK_EVENTS_V2 = """
-- 5.18.6 治本（2026-07-02）：补回 v18 的 CHECK+UNIQUE 约束（v19 重建时丢失）
CREATE TABLE IF NOT EXISTS task_events (
    event_id    TEXT    PRIMARY KEY,
    task_id     TEXT    NOT NULL,
    event_type  TEXT    NOT NULL CHECK(event_type IN (
        'TASK_CREATED', 'TASK_CLAIMED', 'TASK_IN_PROGRESS',
        'TASK_COMPLETED', 'TASK_FAILED', 'TASK_RETRY_CREATED',
        'TASK_CLAIM_EXPIRED', 'TASK_CANCELLED',
        'TASK_ACCEPTANCE_UPDATED', 'TASK_POST_SYNC_UPDATED',
        'GATE_CREATED', 'GATE_CLAIMED', 'GATE_PASSED', 'GATE_FAILED'
    )),
    payload     TEXT    NOT NULL DEFAULT '{}',
    timestamp   TEXT    NOT NULL,
    session_id  TEXT,
    UNIQUE(event_type, task_id, timestamp)
)
"""

# ---------------------------------------------------------------------------
# DDL — FLE 时序指标表（CT-FLE-DB-001）
# ---------------------------------------------------------------------------

_DDL_FLE_METRICS = """
CREATE TABLE IF NOT EXISTS fle_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    source_system   TEXT    NOT NULL,
    metric_name     TEXT    NOT NULL,
    value           REAL    NOT NULL,
    unit            TEXT    DEFAULT 'count',
    tags_json       TEXT    DEFAULT '{}',
    window_avg      REAL,
    window_p99      REAL,
    window_count    INTEGER,
    collected_at    TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
)
"""

# ---------------------------------------------------------------------------
# DDL — FLE 告警事件表（CT-FLE-DB-001）
# ---------------------------------------------------------------------------

_DDL_FLE_ALERTS = """
CREATE TABLE IF NOT EXISTS fle_alerts (
    event_id        TEXT    PRIMARY KEY,
    severity        TEXT    NOT NULL CHECK(severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
    category        TEXT    NOT NULL,
    title           TEXT    NOT NULL,
    detail          TEXT,
    detected_at     TEXT    NOT NULL,
    metric_name     TEXT,
    current_value   REAL,
    threshold_value REAL,
    status          TEXT    DEFAULT 'PENDING' CHECK(status IN ('PENDING','DISPATCHED','RESOLVED','DISMISSED')),
    dispatched_at   TEXT,
    resolved_at     TEXT,
    created_at      TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
)
"""

# ---------------------------------------------------------------------------
# DDL — FLE 分派日志表（CT-FLE-DB-001）
# ---------------------------------------------------------------------------

_DDL_FLE_DISPATCH_LOG = """
CREATE TABLE IF NOT EXISTS fle_dispatch_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id        TEXT    NOT NULL REFERENCES fle_alerts(event_id) ON DELETE CASCADE,
    target_system   TEXT    NOT NULL,
    result          TEXT    NOT NULL,
    task_id         TEXT,
    error_message   TEXT,
    dispatched_at   TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
)
"""

# ---------------------------------------------------------------------------
# DDL — 任务卡审查记录表（task_001_batch_review_protocol 代码强制）
# ---------------------------------------------------------------------------

_DDL_TASK_REVIEWS = """
CREATE TABLE IF NOT EXISTS task_reviews (
    review_id       TEXT    PRIMARY KEY,
    task_id         TEXT    NOT NULL,
    review_round    INTEGER NOT NULL,
    dimension       TEXT    NOT NULL,
    issue_count     INTEGER NOT NULL DEFAULT 0,
    issues_json     TEXT    NOT NULL DEFAULT '[]',
    passed          INTEGER NOT NULL DEFAULT 0 CHECK(passed IN (0,1)),
    reviewer        TEXT    NOT NULL DEFAULT 'ai_session',
    session_id      TEXT,
    reviewed_at     TEXT    NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
)
"""

# ---------------------------------------------------------------------------
# DDL — 索引（KBG-0030 §4.2）
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tasks_status       ON tasks(status)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_phase        ON tasks(phase)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_namespace    ON tasks(namespace)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_session      ON tasks(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_is_deleted   ON tasks(is_deleted)",
    "CREATE INDEX IF NOT EXISTS idx_events_type        ON events(event_type)",
    "CREATE INDEX IF NOT EXISTS idx_events_task        ON events(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_created     ON events(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_gate_runs_gate_id  ON gate_runs(gate_id)",
    "CREATE INDEX IF NOT EXISTS idx_gate_runs_session  ON gate_runs(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_cat      ON knowledge(category)",
]

_DDL_INDEXES_FLE = [
    "CREATE INDEX IF NOT EXISTS idx_fle_metrics_ts      ON fle_metrics(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_fle_metrics_collected ON fle_metrics(collected_at)",
    "CREATE INDEX IF NOT EXISTS idx_fle_alerts_status   ON fle_alerts(status, detected_at)",
    "CREATE INDEX IF NOT EXISTS idx_fle_dispatch_event  ON fle_dispatch_log(event_id)",
]

# ---------------------------------------------------------------------------
# DDL — 视图
# ---------------------------------------------------------------------------

_DDL_VIEW_EVENT_LOG = """
CREATE VIEW IF NOT EXISTS event_log AS
SELECT
    e.event_id,
    e.event_type,
    e.payload,
    e.created_at    AS event_time,
    e.processed_at,
    e.session_id    AS event_session,
    t.task_id,
    t.title         AS task_name,
    t.status        AS task_status,
    t.phase
FROM events e
LEFT JOIN tasks t ON e.task_id = t.task_id
ORDER BY e.created_at DESC
"""

_DDL_VIEW_ACTIVE_TASKS = """
CREATE VIEW IF NOT EXISTS v_active_tasks AS
SELECT
    task_id,
    phase,
    title,
    status,
    execution_model,
    safety_level,
    estimate_hours,
    depends_on,
    session_id,
    created_at,
    updated_at
FROM tasks
WHERE status IN ('IN_PROGRESS', 'READY', 'RETRY', 'WAITING')
  AND is_deleted = 0
ORDER BY phase ASC, updated_at DESC
"""

_DDL_VIEW_RECENT_SESSIONS = """
CREATE VIEW IF NOT EXISTS v_recent_sessions AS
SELECT
    session_id,
    COUNT(*)                                                         AS total_tasks,
    SUM(CASE WHEN status = 'COMPLETED'   THEN 1 ELSE 0 END)         AS completed,
    SUM(CASE WHEN status = 'VERIFIED'    THEN 1 ELSE 0 END)         AS verified,
    SUM(CASE WHEN status = 'FAILED'      THEN 1 ELSE 0 END)         AS failed,
    SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END)         AS in_progress,
    MIN(created_at)                                                  AS session_start,
    MAX(updated_at)                                                  AS last_update
FROM tasks
WHERE session_id IS NOT NULL
  AND is_deleted = 0
GROUP BY session_id
ORDER BY last_update DESC
LIMIT 10
"""

# ---------------------------------------------------------------------------
# PRAGMA 配置 — re-export from SSoT (zephyr.shared.io.sqlite_factory)
# 治本(2026-07-06): get_db_connection/_apply_pragmas/_PRAGMAS 的 canonical 文件
# 已迁移到 shared/io/sqlite_factory.py，此处为 re-export shim 保持向后兼容。
# ---------------------------------------------------------------------------

from zephyr.shared.io.sqlite_factory import (  # noqa: E402
    _PRAGMAS,
    _apply_pragmas,
    get_db_connection,
)


# ---------------------------------------------------------------------------
# 版本化迁移框架（SH-DB-001 v2.0）
# ---------------------------------------------------------------------------

# 迁移注册表：(version, description, [DDL_statements])
# 新增迁移只需在此列表追加条目
_MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (
        1,
        "Initial schema: tasks + events + knowledge + gates + indexes + views",
        [
            _DDL_TASKS,
            _DDL_EVENTS,
            _DDL_KNOWLEDGE,
            _DDL_GATES,
            *_DDL_INDEXES,
            _DDL_VIEW_EVENT_LOG,
            _DDL_VIEW_ACTIVE_TASKS,
            _DDL_VIEW_RECENT_SESSIONS,
        ],
    ),
    (
        2,
        "task_files N:N mapping + namespace + seq columns (#21)",
        [
            "ALTER TABLE tasks ADD COLUMN namespace TEXT NOT NULL DEFAULT 'OPS' "
            "CHECK(namespace IN ('KBG','CP','KE','STD','DW','SRC','OPS','DM'))",
            "ALTER TABLE tasks ADD COLUMN seq INTEGER NOT NULL DEFAULT 1 CHECK(seq >= 1)",
            _DDL_TASK_FILES,
            "CREATE INDEX IF NOT EXISTS idx_tf_task ON task_files(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_tf_file ON task_files(file_path)",
        ],
    ),
    (
        3,
        "v2 fields: priority + model_rationale + actual_hours + files_in_scope + tags + completed_at + name->title (#12)",
        [
            "ALTER TABLE tasks RENAME COLUMN name TO title",
            "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'P2' CHECK(priority IN ('P0','P1','P2','P3'))",
            "ALTER TABLE tasks ADD COLUMN model_rationale TEXT",
            "ALTER TABLE tasks ADD COLUMN actual_hours REAL CHECK(actual_hours IS NULL OR actual_hours >= 0)",
            "ALTER TABLE tasks ADD COLUMN files_in_scope TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN completed_at TEXT",
        ],
    ),
    (
        4,
        "knowledge status column (T-2-11-A)",
        [
            "ALTER TABLE knowledge ADD COLUMN status TEXT NOT NULL DEFAULT 'DRAFT' "
            "CHECK(status IN ("
            "'DRAFT','SUBMITTED','REVIEWED','ACCEPTED','INDEXED',"
            "'VERIFIED','REJECTED','DEPRECATED','ARCHIVED','SUPERSEDED'"
            "))",
        ],
    ),
    (
        5,
        "circuit_breaker_state table (T-V2-005)",
        [
            _DDL_CIRCUIT_BREAKER_STATE,
            "CREATE INDEX IF NOT EXISTS idx_cb_state  ON circuit_breaker_state(state)",
            "CREATE INDEX IF NOT EXISTS idx_cb_caller ON circuit_breaker_state(caller_module)",
        ],
    ),
    (
        6,
        "TaskCard 24 extension columns (MOD-TASK_SYSTEM v0.3.0)",
        [
            "ALTER TABLE tasks ADD COLUMN source_blueprint TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE tasks ADD COLUMN source_section TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE tasks ADD COLUMN description TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE tasks ADD COLUMN upstream_files TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN downstream_outputs TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN allowed_touch TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN forbidden_touch TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN applicable_rules TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN context_assembly_manifest TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN rollback_instructions TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE tasks ADD COLUMN estimated_tokens INTEGER NOT NULL DEFAULT 8000",
            "ALTER TABLE tasks ADD COLUMN timeout_minutes INTEGER NOT NULL DEFAULT 30",
            "ALTER TABLE tasks ADD COLUMN completed_gates TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN blocked_gates TEXT NOT NULL DEFAULT '{}'",
            "ALTER TABLE tasks ADD COLUMN assigned_pipeline TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE tasks ADD COLUMN pipeline_modules TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN blocked_by TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN artifact_paths TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN audit_findings TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN ke_entries TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN ai_autonomy_level TEXT NOT NULL DEFAULT 'supervised'",
            "ALTER TABLE tasks ADD COLUMN autonomy_checklist TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN construction_status TEXT NOT NULL DEFAULT 'pending'",
            "ALTER TABLE tasks ADD COLUMN verification_status TEXT NOT NULL DEFAULT 'unverified'",
        ],
    ),
    (
        7,
        "SH-DB-001 v2.0: _schema_version + slow_queries + tx_idempotency + wal_autocheckpoint",
        [
            _DDL_SCHEMA_VERSION,
            _DDL_SLOW_QUERIES,
            _DDL_TX_IDEMPOTENCY,
            "CREATE INDEX IF NOT EXISTS idx_tasks_is_deleted ON tasks(is_deleted)",
        ],
    ),
    (
        8,
        "SH-DB-001 v2.0: soft delete columns on tasks",
        [
            "ALTER TABLE tasks ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0 CHECK(is_deleted IN (0,1))",
            "ALTER TABLE tasks ADD COLUMN deleted_at TEXT",
        ],
    ),
    (
        9,
        "MOD-TASK_SYSTEM v0.3.2: schema_version column + fix default value drift (B29+B35)",
        [
            "ALTER TABLE tasks ADD COLUMN schema_version TEXT NOT NULL DEFAULT '0.3.2'",
            "UPDATE tasks SET estimated_tokens = 8000 WHERE estimated_tokens = 0 OR estimated_tokens < 500",
            "UPDATE tasks SET timeout_minutes = 30 WHERE timeout_minutes = 0 OR timeout_minutes < 5",
            "UPDATE tasks SET execution_model = 'deepseek' WHERE execution_model NOT IN ('deepseek','glm','claude','kimi','qwen')",
        ],
    ),
    (
        10,
        "MOD-TASK_SYSTEM v0.3.3: P4 priority + approval_required/rejection_cooldown (B53+B55)",
        [
            "ALTER TABLE tasks ADD COLUMN approval_required INTEGER NOT NULL DEFAULT 0 CHECK(approval_required IN (0,1))",
            "ALTER TABLE tasks ADD COLUMN rejection_cooldown_until TEXT",
            "ALTER TABLE tasks ADD COLUMN priority_proposed TEXT",
        ],
    ),
    (
        11,
        "MOD-TASK_SYSTEM v0.3.4: block_sessions_count for escalation governance (B56)",
        [
            "ALTER TABLE tasks ADD COLUMN block_sessions_count INTEGER NOT NULL DEFAULT 0",
        ],
    ),
    (
        14,
        "AUDIT-07: 修复 CHECK 约束（P4 优先级 + 移除 SUSPENDED 状态）— no-op, DDL already correct",
        [],
    ),
    (
        15,
        "AUDIT-09: 修复 v14 重建 tasks 后的 FK 悬空（events/gates/task_files + views + indexes）",
        [
            "PRAGMA foreign_keys = OFF",
            "DROP VIEW IF EXISTS v_active_tasks",
            "DROP VIEW IF EXISTS v_recent_sessions",
            "DROP VIEW IF EXISTS event_log",
            """CREATE TABLE events_v15 (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL CHECK(event_type IN ('file_event','time_event','task_event','manual_event','metric_event','state_transition','compensation')),
                payload TEXT NOT NULL DEFAULT '{}',
                task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
                session_id TEXT,
                created_at TEXT NOT NULL,
                processed_at TEXT
            )""",
            "INSERT OR IGNORE INTO events_v15 SELECT * FROM events",
            "DROP TABLE IF EXISTS events",
            "ALTER TABLE events_v15 RENAME TO events",
            """CREATE TABLE gate_runs_v15 (
                gate_run_id TEXT PRIMARY KEY,
                gate_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK(passed IN (0,1)),
                details TEXT NOT NULL DEFAULT '{}',
                artifact_path TEXT,
                session_id TEXT,
                task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            )""",
            "INSERT OR IGNORE INTO gate_runs_v15 SELECT * FROM gate_runs",
            "DROP TABLE IF EXISTS gate_runs",
            "ALTER TABLE gate_runs_v15 RENAME TO gate_runs",
            """CREATE TABLE task_files_v15 (
                task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
                file_path TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'in_scope' CHECK(role IN ('primary','in_scope','output')),
                UNIQUE(task_id, file_path)
            )""",
            "INSERT OR IGNORE INTO task_files_v15 SELECT * FROM task_files",
            "DROP TABLE IF EXISTS task_files",
            "ALTER TABLE task_files_v15 RENAME TO task_files",
            _DDL_VIEW_EVENT_LOG,
            _DDL_VIEW_ACTIVE_TASKS,
            _DDL_VIEW_RECENT_SESSIONS,
            "CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_gate_runs_gate_id ON gate_runs(gate_id)",
            "CREATE INDEX IF NOT EXISTS idx_gate_runs_session ON gate_runs(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_tf_task ON task_files(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_tf_file ON task_files(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_phase ON tasks(phase)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_namespace ON tasks(namespace)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_session ON tasks(session_id)",
            "PRAGMA foreign_keys = ON",
        ],
    ),
    (
        16,
        "Multi-Worker Batch Coordination: batch_id + claimed_by + claimed_at columns (MOD-INF-016)",
        [
            "ALTER TABLE tasks ADD COLUMN batch_id TEXT",
            "ALTER TABLE tasks ADD COLUMN claimed_by TEXT",
            "ALTER TABLE tasks ADD COLUMN claimed_at TEXT",
            "CREATE INDEX IF NOT EXISTS idx_tasks_batch ON tasks(batch_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_claimed ON tasks(claimed_by, status)",
        ],
    ),
    (
        17,
        "TaskCard Dependency Enhancement: depgraph_nodes + depgraph_layer + dependency_type + dependency_rationale",
        [
            "ALTER TABLE tasks ADD COLUMN depgraph_nodes TEXT DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN depgraph_layer TEXT DEFAULT NULL",
            "ALTER TABLE tasks ADD COLUMN dependency_type TEXT DEFAULT 'hard'",
            "ALTER TABLE tasks ADD COLUMN dependency_rationale TEXT DEFAULT ''",
        ],
    ),
    (
        18,
        "Event Sourcing: task_events + task_snapshots tables (MOD-INF-012B v2.0)",
        [
            """CREATE TABLE IF NOT EXISTS task_events (
                event_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type   TEXT NOT NULL CHECK(event_type IN (
                    'TASK_CREATED', 'TASK_CLAIMED', 'TASK_IN_PROGRESS',
                    'TASK_COMPLETED', 'TASK_FAILED', 'TASK_RETRY_CREATED',
                    'TASK_CLAIM_EXPIRED', 'TASK_CANCELLED',
                    'TASK_ACCEPTANCE_UPDATED', 'TASK_POST_SYNC_UPDATED',
                    'GATE_CREATED', 'GATE_CLAIMED', 'GATE_PASSED', 'GATE_FAILED'
                )),
                task_id      TEXT NOT NULL,
                session_id   TEXT NOT NULL,
                payload      TEXT NOT NULL,
                created_at   TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(event_type, task_id, created_at)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_te_task ON task_events(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_te_session ON task_events(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_te_type ON task_events(event_type)",
            """CREATE TABLE IF NOT EXISTS task_snapshots (
                snapshot_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id       TEXT NOT NULL,
                snapshot_json TEXT NOT NULL,
                last_event_id INTEGER NOT NULL,
                created_at    TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(task_id, last_event_id)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_ts_task ON task_snapshots(task_id)",
        ],
    ),
    (
        19,
        "DW-0001: task_events v2 schema (UUID PK + flexible event_type + timestamp) + task_snapshots v2 (nullable last_event_id + last_event_timestamp, drop UNIQUE)",
        [
            "PRAGMA foreign_keys = OFF",
            "DROP TABLE IF EXISTS _task_events_v18_backup",
            "ALTER TABLE task_events RENAME TO _task_events_v18_backup",
            _DDL_TASK_EVENTS_V2,
            """INSERT INTO task_events (event_id, task_id, event_type, payload, timestamp, session_id)
               SELECT CAST(event_id AS TEXT), task_id, event_type,
                      COALESCE(payload, '{}'), created_at, session_id
               FROM _task_events_v18_backup""",
            "DROP TABLE _task_events_v18_backup",
            "CREATE INDEX IF NOT EXISTS idx_te_task_v2      ON task_events(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_te_timestamp_v2 ON task_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_te_type_v2      ON task_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_te_session_v2   ON task_events(session_id)",
            "DROP TABLE IF EXISTS _task_snapshots_v18_backup",
            "ALTER TABLE task_snapshots RENAME TO _task_snapshots_v18_backup",
            """CREATE TABLE IF NOT EXISTS task_snapshots (
                snapshot_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id              TEXT NOT NULL,
                snapshot_json        TEXT NOT NULL,
                last_event_id        INTEGER NOT NULL DEFAULT 0,
                last_event_timestamp TEXT,
                created_at           TEXT NOT NULL DEFAULT (datetime('now'))
            )""",
            """INSERT INTO task_snapshots (snapshot_id, task_id, snapshot_json, last_event_id, last_event_timestamp, created_at)
               SELECT snapshot_id, task_id, snapshot_json, last_event_id, NULL, created_at
               FROM _task_snapshots_v18_backup""",
            "DROP TABLE _task_snapshots_v18_backup",
            "CREATE INDEX IF NOT EXISTS idx_ts_task ON task_snapshots(task_id)",
            "PRAGMA foreign_keys = ON",
        ],
    ),
    (
        20,
        "requires_rb_check: Red-Blue Adversarial Validator selective activation (MOD-INF-030 §trigger)",
        [
            "ALTER TABLE tasks ADD COLUMN requires_rb_check INTEGER NOT NULL DEFAULT 0 CHECK(requires_rb_check IN (0,1))",
        ],
    ),
    (
        21,
        "DW-0010: 部分唯一索引 idx_te_one_claim_per_task — 每个 task 只能有一个 TASK_CLAIMED 事件（Event Sourcing 原子争抢）",
        [
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_te_one_claim_per_task ON task_events(task_id) WHERE event_type='TASK_CLAIMED'",
        ],
    ),
    (
        22,
        "CT-FLE-DB-001: FLE 持久化三表 — fle_metrics + fle_alerts + fle_dispatch_log",
        [
            _DDL_FLE_METRICS,
            _DDL_FLE_ALERTS,
            _DDL_FLE_DISPATCH_LOG,
            *_DDL_INDEXES_FLE,
        ],
    ),
    (
        23,
        "ADR->KBG: Update tasks.namespace CHECK constraint to replace KB 决策记录 with KBG",
        [
            # 5.18.7 治本（2026-07-02）：writable_schema hack 已移除。
            # _DDL_TASKS 在 v1 创建时已用 'KBG'（非 'KB 决策记录'），LIKE 模式不匹配->原 hack 在全新库上是 no-op。
            # 生产库已通过 hack 修改，版本号已登记不会重跑。约束由 _DDL_TASKS 保证。
        ],
    ),
    (
        24,
        "Task/TaskCard SSoT merge: add post_sync_standard, post_sync_specific, pipeline_task_type, target_layer, estimated_complexity, root_cause_analysis",
        [
            "ALTER TABLE tasks ADD COLUMN post_sync_standard TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN post_sync_specific TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN pipeline_task_type TEXT",
            "ALTER TABLE tasks ADD COLUMN target_layer TEXT",
            "ALTER TABLE tasks ADD COLUMN estimated_complexity TEXT",
            "ALTER TABLE tasks ADD COLUMN root_cause_analysis TEXT",
        ],
    ),
    (
        25,
        "Add DM namespace to tasks.namespace CHECK constraint for Domain Migration tasks",
        [
            # 5.18.7 治本（2026-07-02）：writable_schema hack 已移除。
            # _DDL_TASKS 在 v1 创建时已含 'DM'，LIKE 模式 `NOT LIKE '%DM%'` 不匹配->原 hack 在全新库上是 no-op。
            # 生产库已通过 hack 修改，版本号已登记不会重跑。约束由 _DDL_TASKS 保证。
        ],
    ),
    (
        26,
        "DM-407: blocked_by integrity triggers — validate JSON + reference existence + status consistency",
        [
            # 先关闭FK检查（数据库中已有events引用不存在tasks的悬空FK，不影响trigger创建）
            "PRAGMA foreign_keys = OFF",
            # Trigger 1: INSERT时校验blocked_by是有效JSON且引用的任务存在
            """CREATE TRIGGER IF NOT EXISTS validate_blocked_by_insert
                BEFORE INSERT ON tasks
                FOR EACH ROW
                WHEN NEW.blocked_by IS NOT NULL AND NEW.blocked_by != '[]' AND NEW.blocked_by != ''
                BEGIN
                    SELECT RAISE(ABORT, 'BLOCKED: blocked_by must be valid JSON array')
                    WHERE NOT json_valid(NEW.blocked_by);
                END""",
            # Trigger 2: UPDATE时校验blocked_by是有效JSON
            """CREATE TRIGGER IF NOT EXISTS validate_blocked_by_update
                BEFORE UPDATE ON tasks
                FOR EACH ROW
                WHEN NEW.blocked_by IS NOT NULL AND NEW.blocked_by != '[]' AND NEW.blocked_by != ''
                    AND NEW.blocked_by != OLD.blocked_by
                BEGIN
                    SELECT RAISE(ABORT, 'BLOCKED: blocked_by must be valid JSON array')
                    WHERE NOT json_valid(NEW.blocked_by);
                END""",
            # Trigger 3: UPDATE时校验blocked_by非空->status必须是BLOCKED
            """CREATE TRIGGER IF NOT EXISTS validate_blocked_by_status_consistency
                BEFORE UPDATE ON tasks
                FOR EACH ROW
                WHEN NEW.blocked_by IS NOT NULL AND NEW.blocked_by != '[]' AND NEW.blocked_by != ''
                    AND NEW.status != 'BLOCKED'
                    AND NEW.blocked_by != OLD.blocked_by
                BEGIN
                    SELECT RAISE(ABORT, 'BLOCKED: task with non-empty blocked_by must have status BLOCKED');
                END""",
            # Trigger 4: INSERT时校验blocked_by非空->status必须是BLOCKED
            """CREATE TRIGGER IF NOT EXISTS validate_blocked_by_status_insert
                BEFORE INSERT ON tasks
                FOR EACH ROW
                WHEN NEW.blocked_by IS NOT NULL AND NEW.blocked_by != '[]' AND NEW.blocked_by != ''
                    AND NEW.status != 'BLOCKED'
                BEGIN
                    SELECT RAISE(ABORT, 'BLOCKED: task with non-empty blocked_by must have status BLOCKED');
                END""",
            "PRAGMA foreign_keys = ON",
        ],
    ),
    (
        27,
        "DM-386: Add CHECK constraints on files_in_scope/deliverables to enforce JSON array format",
        [
            # 5.18.7 治本（2026-07-02）：writable_schema hack 已移除。
            # _DDL_TASKS 在 v1 创建时已含 CHECK(files_in_scope LIKE '[%') 和 CHECK(deliverables LIKE '[%')，
            # LIKE 模式 `NOT LIKE '%files_in_scope LIKE%'` 不匹配->原 hack 在全新库上是 no-op。
            # 生产库已通过 hack 修改，版本号已登记不会重跑。约束由 _DDL_TASKS 保证。
            # 保留 events 表 dangling task_id 清理（安全的数据维护操作，非 hack）：
            "UPDATE events SET task_id = NULL WHERE task_id IS NOT NULL AND task_id NOT IN (SELECT task_id FROM tasks)",
        ],
    ),
    (
        28,
        "DM-100267: Add 7 missing columns to tasks table + fix gate_decisions FK mismatch + clean tasks.domain_id orphans",
        [
            # 修复 tasks->domains FK 违规: 485行 domain_id 引用不存在的 domains，SET NULL 清理
            "UPDATE tasks SET domain_id = NULL WHERE domain_id IS NOT NULL AND domain_id NOT IN (SELECT domain_id FROM domains)",
            # 修复 gate_decisions FK mismatch: gates.gate_id 无 UNIQUE 约束（业务上可多次运行），
            # FK REFERENCES gates(gate_id) 非法。gate_decisions 表为空，安全重建移除 FK。
            "DROP TABLE IF EXISTS gate_decisions",
            "CREATE TABLE gate_decisions (decision_id INTEGER PRIMARY KEY AUTOINCREMENT, gate_id TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT, decided_at TEXT NOT NULL, decided_by TEXT)",
            # 补 tasks 表7个缺失列（DDL 已定义但 CREATE TABLE IF NOT EXISTS 对已存在表不生效）
            "ALTER TABLE tasks ADD COLUMN idempotent INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE tasks ADD COLUMN evolution_policy TEXT NOT NULL DEFAULT 'extendable'",
            "ALTER TABLE tasks ADD COLUMN estimate_hours REAL NOT NULL DEFAULT 0",
            "ALTER TABLE tasks ADD COLUMN session_id TEXT",
            "ALTER TABLE tasks ADD COLUMN waiting_for TEXT",
            "ALTER TABLE tasks ADD COLUMN depends_on TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE tasks ADD COLUMN ready_at TEXT",
        ],
    ),
    (
        29,
        "DM-200921: task_reviews table for task_001_batch_review_protocol enforcement",
        [
            _DDL_TASK_REVIEWS,
            "CREATE INDEX IF NOT EXISTS idx_task_reviews_task_id ON task_reviews(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_reviews_passed ON task_reviews(passed)",
        ],
    ),
    (
        30,
        "DM-P3001: Drop legacy tasks.domain_id column (遗留列清理)",
        [
            # v30 的核心逻辑由 _drop_tasks_domain_id() Python 函数执行（非纯 SQL statements），
            # 该函数在 init_db() 的 transaction 外调用（因 PRAGMA writable_schema 不能在
            # transaction 中使用）。statements 列表仅作文档说明，不会在 _run_migration 中执行。
            #
            # 执行步骤（_drop_tasks_domain_id 内）：
            # 1. 清理 events 表 dangling task_id（历史遗留脏数据：ON DELETE SET NULL 未生效）
            # 2. PRAGMA foreign_keys = OFF（避免 DROP COLUMN 表重建触发其他表 ON DELETE）
            # 3. PRAGMA writable_schema = ON -> 移除 tasks 的 FK(domain_id)->domains -> RESET
            # 4. ALTER TABLE tasks DROP COLUMN domain_id（FK 已移除，表重建不再报错）
            # 5. PRAGMA foreign_keys = ON（恢复 FK 检查）
            #
            # 全新库无 domain_id 列时，_drop_tasks_domain_id 是 no-op，仅登记版本号。
        ],
    ),
    (
        31,
        "5.18.6 治本: task_events v2 重建补 CHECK+UNIQUE 约束（v19 重建时丢失 v18 的 14 种 event_type 枚举约束和 UNIQUE(event_type,task_id,timestamp)）",
        [
            # SQLite 不支持 ALTER TABLE ADD CONSTRAINT，需表重建模式
            # 步骤：建备份 -> RENAME 旧表 -> 建新表（含 CHECK+UNIQUE）-> 复制数据（过滤脏数据）-> DROP 备份 -> 重建索引
            "PRAGMA foreign_keys = OFF",
            "DROP TABLE IF EXISTS _task_events_v31_backup",
            "ALTER TABLE task_events RENAME TO _task_events_v31_backup",
            _DDL_TASK_EVENTS_V2.replace(
                "CREATE TABLE IF NOT EXISTS task_events",
                "CREATE TABLE task_events",
            ),
            # 复制数据：过滤掉不符合 CHECK 约束的脏 event_type（防止 INSERT 失败）
            """INSERT INTO task_events (event_id, task_id, event_type, payload, timestamp, session_id)
               SELECT event_id, task_id, event_type, payload, timestamp, session_id
               FROM _task_events_v31_backup
               WHERE event_type IN (
                   'TASK_CREATED', 'TASK_CLAIMED', 'TASK_IN_PROGRESS',
                   'TASK_COMPLETED', 'TASK_FAILED', 'TASK_RETRY_CREATED',
                   'TASK_CLAIM_EXPIRED', 'TASK_CANCELLED',
                   'TASK_ACCEPTANCE_UPDATED', 'TASK_POST_SYNC_UPDATED',
                   'GATE_CREATED', 'GATE_CLAIMED', 'GATE_PASSED', 'GATE_FAILED'
               )""",
            "DROP TABLE _task_events_v31_backup",
            # 重建索引（DROP TABLE 已删除所有索引）
            "CREATE INDEX IF NOT EXISTS idx_te_task_v2      ON task_events(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_te_timestamp_v2 ON task_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_te_type_v2      ON task_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_te_session_v2   ON task_events(session_id)",
            # v21 的部分唯一索引需重建
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_te_one_claim_per_task ON task_events(task_id) WHERE event_type='TASK_CLAIMED'",
            "PRAGMA foreign_keys = ON",
        ],
    ),
    (
        32,
        "5.57.2+5.57.6 治本: task_events 增加 seq 单调序列号 + prev_hash 完整性链列",
        [
            "ALTER TABLE task_events ADD COLUMN seq INTEGER",
            "ALTER TABLE task_events ADD COLUMN prev_hash TEXT NOT NULL DEFAULT ''",
            "CREATE INDEX IF NOT EXISTS idx_te_seq ON task_events(seq)",
        ],
    ),
]


def _get_current_version(conn: sqlite3.Connection) -> int:
    """返回当前数据库的 schema 版本（未初始化则返回 0）。"""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_schema_version'")
    if cursor.fetchone() is None:
        # _schema_version 表不存在 -> 可能是旧数据库（已有表但无版本记录）
        # 检查核心表 tasks 是否存在来判断
        task_cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if task_cursor.fetchone() is not None:
            # 旧数据库：有 tasks 表但没有 _schema_version -> 标记为 v6（最后一个旧迁移）
            return -6
        return 0
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
    row = cursor.fetchone()
    return row[0] if row else 0


def _tasks_lacks_domain_id(conn: sqlite3.Connection) -> bool:
    """检查 tasks 表是否存在 domain_id 列。

    v28 statement #0 清洗 tasks.domain_id 脏数据，v30 表重建删除该遗留列。
    全新库的 tasks 表从未创建 domain_id 列，执行会抛 OperationalError。
    返回 True 表示当前库无 domain_id 列，应跳过相关语句。
    """
    cols = conn.execute("PRAGMA table_info(tasks)").fetchall()
    return not any(c[1] == "domain_id" for c in cols)


def _drop_tasks_domain_id(conn: sqlite3.Connection) -> None:
    """移除 tasks.domain_id 列及其 FK 约束（v30 迁移核心逻辑，必须在 transaction 外调用）。

    SQLite 的 ALTER TABLE DROP COLUMN 在有 FK 引用该列时会失败：
      "unknown column domain_id in foreign key definition"
    表重建方式（DROP TABLE + CREATE + RENAME）在 foreign_keys=ON 时会触发
    task_reviews 的 ON DELETE NO ACTION，导致 "FOREIGN KEY constraint failed"。

    方案：用 PRAGMA writable_schema 移除 FK 定义，然后 ALTER TABLE DROP COLUMN。
    PRAGMA writable_schema 不能在 transaction 中使用，故本函数必须在 BEGIN/COMMIT 外调用。
    """
    if _tasks_lacks_domain_id(conn):
        return  # 全新库无此列，跳过

    # 1. 清理 events 表的 dangling task_id（历史遗留脏数据：ON DELETE SET NULL 未生效）
    conn.execute(
        "UPDATE events SET task_id = NULL "
        "WHERE task_id IS NOT NULL AND task_id NOT IN (SELECT task_id FROM tasks)"
    )

    # 2. 关闭 FK 检查（避免 DROP COLUMN 内部表重建触发其他表的 ON DELETE）
    conn.execute("PRAGMA foreign_keys = OFF")

    # 3. 用 writable_schema 移除 tasks 的 FK(domain_id)->domains 约束
    conn.execute("PRAGMA writable_schema = ON")
    try:
        sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'"
        ).fetchone()[0]
        # 移除 FK 约束行（先尝试 "逗号+FK"，再尝试单独 "FK"）
        new_sql = re.sub(
            r',\s*\n\s*FOREIGN\s+KEY\s*\(\s*domain_id\s*\)\s+REFERENCES\s+domains\s*\(\s*domain_id\s*\)',
            '',
            sql,
        )
        new_sql = re.sub(
            r'\n\s*FOREIGN\s+KEY\s*\(\s*domain_id\s*\)\s+REFERENCES\s+domains\s*\(\s*domain_id\s*\)',
            '',
            new_sql,
        )
        conn.execute(
            "UPDATE sqlite_master SET sql = ? WHERE type='table' AND name='tasks'",
            (new_sql,),
        )
    finally:
        conn.execute("PRAGMA writable_schema = RESET")

    # 4. 现在 DROP COLUMN 应该能成功（FK 已从 schema 中移除）
    conn.execute("ALTER TABLE tasks DROP COLUMN domain_id")

    # 5. 重新开启 FK 检查
    conn.execute("PRAGMA foreign_keys = ON")


def _run_migration(
    conn: sqlite3.Connection,
    version: int,
    description: str,
    statements: list[str],
) -> None:
    """执行单个版本的迁移并登记到 _schema_version。"""
    from datetime import UTC, datetime

    now = datetime.now(UTC).isoformat()
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if not stmt:
            continue
        # v28 statement #0 是生产库脏数据清洗，全新库无 domain_id 列需跳过
        if version == 28 and i == 0 and _tasks_lacks_domain_id(conn):
            continue
        # v31 statement #4: 兼容 v18/v19 两版 task_events schema
        # v19 在某些旧库上标记 applied 却未执行 DDL，导致 task_events 仍是 v18 schema
        # （有 details 列，无 payload/session_id 列）。v31 INSERT 假设 v19 已成功（有 payload），
        # 旧库需动态替换为 details->payload、NULL->session_id
        if version == 31 and i == 4:
            backup_cols = {r[1] for r in conn.execute(
                "PRAGMA table_info(_task_events_v31_backup)"
            ).fetchall()}
            if "payload" not in backup_cols and "details" in backup_cols:
                stmt = """INSERT INTO task_events (event_id, task_id, event_type, payload, timestamp, session_id)
               SELECT event_id, task_id, event_type, COALESCE(details, '{}'), timestamp, NULL
               FROM _task_events_v31_backup
               WHERE event_type IN (
                   'TASK_CREATED', 'TASK_CLAIMED', 'TASK_IN_PROGRESS',
                   'TASK_COMPLETED', 'TASK_FAILED', 'TASK_RETRY_CREATED',
                   'TASK_CLAIM_EXPIRED', 'TASK_CANCELLED',
                   'TASK_ACCEPTANCE_UPDATED', 'TASK_POST_SYNC_UPDATED',
                   'GATE_CREATED', 'GATE_CLAIMED', 'GATE_PASSED', 'GATE_FAILED'
               )"""
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as exc:
            msg = str(exc).lower()
            benign = (
                "duplicate column name",
                "duplicate column",
                "already exists",
                "duplicate key name:",
                'no such column: "name"',
                "no such column: name",
                "no such table: gates",  # 5.18.14: v30 RENAME on fresh DB (gates->gate_runs)
            )
            if any(p in msg for p in benign):
                continue
            raise RuntimeError(f"Migration v{version} statement #{i}: {exc}\n  SQL: {stmt[:200]}") from exc  # noqa: MSG-EXPOSURE  # SQL 是版本控制迁移 DDL/DML 调试上下文非用户数据

    conn.execute(
        "INSERT OR IGNORE INTO _schema_version (version, applied_at, description) VALUES (?, ?, ?)",
        (version, now, description),
    )

    fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_violations:
        violations_str = "; ".join(str(v) for v in fk_violations[:5])
        raise RuntimeError(
            f"Migration v{version} FK integrity violation: {len(fk_violations)} row(s) — {violations_str}"
        )


def _log(echo: bool, message: str) -> None:
    if echo:
        print(message)


def init_db(
    db_path: Path | str | None = None,
    *,
    echo: bool = False,
) -> Path:
    """
    幂等初始化数据库（执行 DDL + 按需运行版本化迁移）。

    可安全重复调用：已存在的表和列不会被覆盖，已执行的迁移会被跳过。

    参数
    ----
    db_path
        数据库文件路径，默认 DB_PATH。
    echo
        为 True 时打印迁移日志到 stdout（调试用）。

    返回
    ----
    Path
        数据库文件的绝对路径。
    """
    resolved: Path = Path(db_path) if db_path is not None else _DB_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)

    # isolation_level=None: autocommit 模式，显式控制 transaction
    # 原因：v30 的 _drop_tasks_domain_id 需要在 transaction 外执行 PRAGMA writable_schema
    # 和 PRAGMA foreign_keys = OFF，deferred 模式会因 DML 隐式 BEGIN 导致 PRAGMA 失败
    conn = sqlite3.connect(str(resolved), isolation_level=None)
    try:
        _apply_pragmas(conn)

        # 步骤 1：先创建 _schema_version 表自身（以便后续迁移使用）
        conn.execute(_DDL_SCHEMA_VERSION.strip())

        # 步骤 2：检测当前版本
        current = _get_current_version(conn)

        _log(echo, f"[sqlite_schema] current version: {current}")

        # 步骤 3：处理旧数据库（有表但无 _schema_version）
        if current < 0:
            # current == -6 表示 v6 之前的迁移已通过 IF NOT EXISTS 完成
            bootstrapped = abs(current)
            _log(echo, f"[sqlite_schema] bootstrapping legacy DB -> marking v1–v{abs(current)} as applied")
            from datetime import UTC, datetime

            now = datetime.now(UTC).isoformat()
            for v, desc, _ in _MIGRATIONS:
                if v <= bootstrapped:
                    conn.execute(
                        "INSERT OR IGNORE INTO _schema_version (version, applied_at, description) VALUES (?, ?, ?)",
                        (v, now, desc + " [bootstrap: legacy DB]"),
                    )
            current = bootstrapped

        # 步骤 4：v30 特殊处理——必须在 transaction 外执行
        # 原因：_drop_tasks_domain_id 使用 PRAGMA writable_schema 移除 FK 定义，
        # 然后执行 ALTER TABLE DROP COLUMN（内部表重建）。
        # PRAGMA writable_schema 不能在 transaction 中使用，且表重建在 foreign_keys=ON
        # 时会触发 task_reviews 的 ON DELETE NO ACTION。故在 BEGIN 前单独执行。
        if current < 30 and not _tasks_lacks_domain_id(conn):
            _log(echo, "[sqlite_schema] executing migration v30 (pre-tx): DM-P3001")
            _drop_tasks_domain_id(conn)
            from datetime import UTC, datetime

            now = datetime.now(UTC).isoformat()
            conn.execute(
                "INSERT OR IGNORE INTO _schema_version (version, applied_at, description) "
                "VALUES (?, ?, ?)",
                (30, now, "DM-P3001: Drop legacy tasks.domain_id column (遗留列清理)"),
            )

        # 步骤 5：执行剩余迁移版本（v30 已在 transaction 外处理）
        conn.execute("BEGIN")
        try:
            for version, description, statements in _MIGRATIONS:
                if version <= current:
                    continue
                if version == 30:
                    # 全新库无 domain_id 列：_drop_tasks_domain_id 是 no-op，
                    # 但仍需登记版本号
                    if _tasks_lacks_domain_id(conn):
                        from datetime import UTC, datetime

                        now = datetime.now(UTC).isoformat()
                        conn.execute(
                            "INSERT OR IGNORE INTO _schema_version "
                            "(version, applied_at, description) VALUES (?, ?, ?)",
                            (30, now, description),
                        )
                    continue
                _log(echo, f"[sqlite_schema] executing migration v{version}: {description}")
                _run_migration(conn, version, description, statements)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    finally:
        conn.close()

    return resolved.resolve()


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def table_names(db_path: Path | str | None = None) -> list[str]:
    """返回数据库中所有表名（不含视图）。"""
    resolved = Path(db_path) if db_path is not None else _DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def view_names(db_path: Path | str | None = None) -> list[str]:
    """返回数据库中所有视图名。"""
    resolved = Path(db_path) if db_path is not None else _DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def schema_version(db_path: Path | str | None = None) -> int:
    """返回当前数据库的 schema 版本（供外部诊断）。"""
    resolved = Path(db_path) if db_path is not None else _DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        _apply_pragmas(conn)
        return _get_current_version(conn)
    finally:
        conn.close()


def migration_dry_run(
    db_path: Path | str | None = None,
    *,
    pending_only: bool = False,
) -> dict:
    """T-DB-008: 检查待执行迁移，返回迁移预览信息。

    参数
    ----
    pending_only
        True 时仅返回待执行的迁移；False 时返回全部注册迁移。
    db_path
        数据库文件路径，默认 DB_PATH。

    返回 dict{current_version, pending_migrations=[{version, description, ddl_preview},...]}。
    """
    resolved = Path(db_path) if db_path is not None else _DB_PATH
    current_ver = schema_version(resolved)
    if current_ver < 0:
        current_ver = abs(current_ver)
    pending = []
    for version, description, statements in _MIGRATIONS:
        if version <= current_ver:
            if pending_only:
                continue
            status = "applied"
        else:
            status = "pending"
        ddl_preview = [s[:120] + ("..." if len(s) > 120 else "") for s in statements[:3]]
        pending.append(
            {
                "version": version,
                "description": description,
                "status": status,
                "statement_count": len(statements),
                "ddl_preview": ddl_preview,
            }
        )
    result = {
        "current_version": current_ver,
        "registered_max_version": max((m[0] for m in _MIGRATIONS), default=0),
        "total_registered": len(_MIGRATIONS),
        "migrations": pending if pending_only else pending,
    }
    if pending_only:
        result["pending_count"] = len([m for m in pending if m["status"] == "pending"])
    return result


# ---------------------------------------------------------------------------
# SchemaManager — 表级幂等创建入口（DW-0001）
# ---------------------------------------------------------------------------


class SchemaManager:
    """Schema 级别管理器——提供表级幂等创建方法，供 EventStore/SnapshotManager 初始化时调用。"""

    @staticmethod
    def ensure_task_events_table(db_path: Path | str | None = None) -> None:
        """幂等确保 task_events 表存在（v2 schema: UUID PK + timestamp）。

        调用 init_db() 完成全部迁移后，task_events 表必然存在。
        本方法作为显式入口，供 EventStore 构造时调用以确保表就绪。
        """
        init_db(db_path)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(
    {
        "init_db",
        "get_db_connection",
        "table_names",
        "view_names",
        "schema_version",
        "migration_dry_run",
        "SchemaManager",
    }
)


def __getattr__(name: str):
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.governance.persistence.sqlite_schema",
            name,
        )
    raise AttributeError(f"module 'zephyr.governance.persistence.sqlite_schema' has no attribute {name!r}")


if __name__ == "__main__":
    import sys

    db = init_db(echo=True)
    tables = table_names(db)
    views = view_names(db)
    ver = schema_version(db)
    print(f"\n  初始化完成：{db}")
    print(f"  当前 Schema 版本：v{ver}")
    print(f"  表（{len(tables)} 个）：{', '.join(tables)}")
    print(f"  视图（{len(views)} 个）：{', '.join(views)}")
    sys.exit(0)
