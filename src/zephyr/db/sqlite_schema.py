"""
SQLite 元数据层 Schema DDL + 初始化（T-1-02）
==============================================
依据：ADR-0030（SQLite 作为 Phase 1 元数据层）

物理路径：data/zalpha_metadata.db
Safety  : M（DDL 定义，init_db 幂等执行）

表结构
------
1. tasks                 — 任务登记表（10 状态流转 + namespace 分类）
2. task_files            — 任务-文件 N:N 映射表（#21 裁定）
3. events                — 事件流（DeferredQueue 消费）
4. knowledge             — KE 索引
5. gates                 — 门禁运行记录
6. circuit_breaker_state — CBG 模块间熔断状态（T-V2-005 Phase 1b）

视图
----
event_log       — tasks × events JOIN（CLI 审计视图）
v_active_tasks  — 活跃任务快照（IN_PROGRESS + READY + RETRY）
v_recent_sessions — 最近 10 个 session 的完成情况

PRAGMA 基线（ADR-0030 §4.3）
-------------------------------
  journal_mode = WAL
  synchronous = NORMAL
  foreign_keys = ON
  busy_timeout = 5000
  temp_store = MEMORY

用法
----
    from zephyr.db.sqlite_schema import init_db, get_db_connection, DB_PATH

    init_db()              # 幂等，可重复调用
    conn = get_db_connection()   # 返回配置好 PRAGMA 的连接
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zephyr.shared.paths import DB_PATH

# ---------------------------------------------------------------------------
# DDL — tasks 表
# ---------------------------------------------------------------------------

_DDL_TASKS = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id          TEXT    PRIMARY KEY
                             CHECK(task_id GLOB '[A-Z][A-Z]*-[0-9]*'),
    namespace        TEXT    NOT NULL CHECK(namespace IN ('ADR','CP','KE','STD','DW','SRC','OPS')),
    seq              INTEGER NOT NULL CHECK(seq >= 1),
    title            TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'PENDING'
                             CHECK(status IN (
                                 'PENDING','IN_PROGRESS','COMPLETED','VERIFIED',
                                 'FAILED','BLOCKED','WAITING','READY','RETRY','CANCELLED'
                             )),
    priority         TEXT    NOT NULL DEFAULT 'P2'
                             CHECK(priority IN ('P0','P1','P2','P3')),
    phase            INTEGER NOT NULL CHECK(phase >= 0 AND phase <= 9),
    execution_model  TEXT    NOT NULL,
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
    files_in_scope   TEXT    NOT NULL DEFAULT '[]',   -- JSON 数组
    deliverables     TEXT    NOT NULL DEFAULT '[]',   -- JSON 数组
    acceptance       TEXT    NOT NULL DEFAULT '[]',   -- JSON 数组
    depends_on       TEXT    NOT NULL DEFAULT '[]',   -- JSON 数组
    tags             TEXT    NOT NULL DEFAULT '[]',   -- JSON 数组
    session_id       TEXT,
    waiting_for      TEXT,
    ready_at         TEXT,                            -- ISO 8601
    completed_at     TEXT,                            -- ISO 8601
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL
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
                         'manual_event','metric_event','state_transition'
                     )),
    payload     TEXT NOT NULL DEFAULT '{}',   -- JSON
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
    tags                TEXT NOT NULL DEFAULT '[]',   -- JSON 数组
    summary             TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — gates 表
# ---------------------------------------------------------------------------

_DDL_GATES = """
CREATE TABLE IF NOT EXISTS gates (
    gate_run_id  TEXT PRIMARY KEY,
    gate_id      TEXT NOT NULL,
    passed       INTEGER NOT NULL CHECK(passed IN (0,1)),
    details      TEXT NOT NULL DEFAULT '{}',   -- JSON
    artifact_path TEXT,
    session_id   TEXT,
    task_id      TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
    created_at   TEXT NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — circuit_breaker_state 表（T-V2-005 Phase 1b CBG）
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
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now')),
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
# DDL — 索引（ADR-0030 §4.2）
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tasks_status    ON tasks(status)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_phase     ON tasks(phase)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_namespace ON tasks(namespace)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_session   ON tasks(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_type     ON events(event_type)",
    "CREATE INDEX IF NOT EXISTS idx_events_task     ON events(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_created  ON events(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_gates_gate_id   ON gates(gate_id)",
    "CREATE INDEX IF NOT EXISTS idx_gates_session   ON gates(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_cat   ON knowledge(category)",
    "CREATE INDEX IF NOT EXISTS idx_cb_state        ON circuit_breaker_state(state)",
    "CREATE INDEX IF NOT EXISTS idx_cb_caller       ON circuit_breaker_state(caller_module)",
    "CREATE INDEX IF NOT EXISTS idx_tf_task         ON task_files(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_tf_file         ON task_files(file_path)",
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
GROUP BY session_id
ORDER BY last_update DESC
LIMIT 10
"""

# ---------------------------------------------------------------------------
# PRAGMA 配置
# ---------------------------------------------------------------------------

_PRAGMAS = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = NORMAL",
    "PRAGMA foreign_keys = ON",
    "PRAGMA busy_timeout = 5000",
    "PRAGMA temp_store = MEMORY",
]


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    """对连接应用 ADR-0030 §4.3 PRAGMA 基线。"""
    for pragma in _PRAGMAS:
        conn.execute(pragma)


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------


def get_db_connection(
    db_path: Optional[Path | str] = None,
    *,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """
    返回配置好 PRAGMA 的 SQLite 连接。

    参数
    ----
    db_path
        数据库文件路径，默认 DB_PATH（``docs/09_audit/state/zalpha_metadata.db``）。
    check_same_thread
        传给 sqlite3.connect；默认 False 允许跨线程读（单 Writer 假设下安全）。
    timeout
        busy 等待超时（秒），默认 30s。

    返回
    ----
    sqlite3.Connection
        row_factory 已设为 sqlite3.Row，可按列名索引。
    """
    resolved: Path = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(
        str(resolved),
        isolation_level=None,  # 手动控制 BEGIN / COMMIT
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


def init_db(
    db_path: Optional[Path | str] = None,
    *,
    echo: bool = False,
) -> Path:
    """
    幂等初始化数据库（CREATE TABLE/INDEX/VIEW IF NOT EXISTS）。

    可安全重复调用：已存在的表不会被覆盖或截断。

    参数
    ----
    db_path
        数据库文件路径，默认 DB_PATH。
    echo
        为 True 时将 DDL 语句打印到 stdout（调试用）。

    返回
    ----
    Path
        数据库文件的绝对路径。
    """
    resolved: Path = Path(db_path) if db_path is not None else DB_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)

    ddl_statements = [
        _DDL_TASKS,
        _DDL_TASK_FILES,
        _DDL_EVENTS,
        _DDL_KNOWLEDGE,
        _DDL_GATES,
        _DDL_CIRCUIT_BREAKER_STATE,
        *_DDL_INDEXES,
        _DDL_VIEW_EVENT_LOG,
        _DDL_VIEW_ACTIVE_TASKS,
        _DDL_VIEW_RECENT_SESSIONS,
    ]

    conn = sqlite3.connect(str(resolved))
    try:
        _apply_pragmas(conn)
        conn.execute("BEGIN")
        for stmt in ddl_statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            if echo:
                print(f"[sqlite_schema] {stmt[:80]}…")
            conn.execute(stmt)
        conn.execute("COMMIT")
        _migrate_namespace_and_seq(conn)
        _migrate_v2_fields(conn)
        _migrate_knowledge_status(conn)
        _migrate_circuit_breaker_state(conn)
        _migrate_taskcard_columns(conn)
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()

    return resolved.resolve()


def _migrate_namespace_and_seq(conn: sqlite3.Connection) -> None:
    """#21 裁定：幂等添加 namespace + seq 列到 tasks 表，创建 task_files 表。"""
    cursor = conn.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in cursor.fetchall()}
    if "namespace" not in columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN namespace TEXT NOT NULL DEFAULT 'OPS' "
            "CHECK(namespace IN ('ADR','CP','KE','STD','DW','SRC','OPS'))"
        )
    if "seq" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN seq INTEGER NOT NULL DEFAULT 0 CHECK(seq >= 1)")
    conn.execute(_DDL_TASK_FILES.strip())
    existing_indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
    if "idx_tf_task" not in existing_indexes:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tf_task ON task_files(task_id)")
    if "idx_tf_file" not in existing_indexes:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tf_file ON task_files(file_path)")


def _migrate_v2_fields(conn: sqlite3.Connection) -> None:
    """#12 裁定：幂等添加 v2.0 新字段 + name→title 重命名 + 重建依赖视图。"""
    cursor = conn.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in cursor.fetchall()}
    if "name" in columns and "title" not in columns:
        conn.execute("ALTER TABLE tasks RENAME COLUMN name TO title")
    if "priority" not in columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'P2' "
            "CHECK(priority IN ('P0','P1','P2','P3'))"
        )
    if "model_rationale" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN model_rationale TEXT")
    if "actual_hours" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN actual_hours REAL CHECK(actual_hours IS NULL OR actual_hours >= 0)")
    if "files_in_scope" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN files_in_scope TEXT NOT NULL DEFAULT '[]'")
    if "tags" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'")
    if "completed_at" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
    _rebuild_views(conn)


def _rebuild_views(conn: sqlite3.Connection) -> None:
    """销毁并重建全部视图——防止 RENAME COLUMN 后视图引用旧列名导致崩溃。"""
    conn.execute("DROP VIEW IF EXISTS event_log")
    conn.execute("DROP VIEW IF EXISTS v_active_tasks")
    conn.execute("DROP VIEW IF EXISTS v_recent_sessions")
    conn.execute(_DDL_VIEW_EVENT_LOG.strip())
    conn.execute(_DDL_VIEW_ACTIVE_TASKS.strip())
    conn.execute(_DDL_VIEW_RECENT_SESSIONS.strip())


def _migrate_knowledge_status(conn: sqlite3.Connection) -> None:
    """T-2-11-A: 幂等添加 status 列到 knowledge 表。"""
    cursor = conn.execute("PRAGMA table_info(knowledge)")
    columns = {row[1] for row in cursor.fetchall()}
    if "status" not in columns:
        conn.execute(
            "ALTER TABLE knowledge ADD COLUMN status TEXT NOT NULL DEFAULT 'DRAFT' "
            "CHECK(status IN ("
            "'DRAFT','SUBMITTED','REVIEWED','ACCEPTED','INDEXED',"
            "'VERIFIED','REJECTED','DEPRECATED','ARCHIVED','SUPERSEDED'"
            "))"
        )


def _migrate_circuit_breaker_state(conn: sqlite3.Connection) -> None:
    """T-V2-005: 幂等创建 circuit_breaker_state 表及配套索引。

    已存在时不重建（CREATE TABLE/INDEX IF NOT EXISTS 语义）。
    """
    conn.execute(_DDL_CIRCUIT_BREAKER_STATE.strip())
    existing_indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
    if "idx_cb_state" not in existing_indexes:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cb_state " "ON circuit_breaker_state(state)")
    if "idx_cb_caller" not in existing_indexes:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cb_caller " "ON circuit_breaker_state(caller_module)")


def _migrate_taskcard_columns(conn: sqlite3.Connection) -> None:
    """MOD-INF-006 v0.3.0：幂等添加 TaskCard 24 个扩展列到 tasks 表。

    消除 SQLite + .md 双轨 SSoT 分裂——TaskCard 的 52 字段现在在一个表里。
    对标 ITIL SACM：每个 CI 只有一个 Canonical SSoT。
    """
    cursor = conn.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in cursor.fetchall()}

    _taskcard_new_columns = [
        ("source_blueprint", "TEXT NOT NULL DEFAULT ''"),
        ("source_section", "TEXT NOT NULL DEFAULT ''"),
        ("description", "TEXT NOT NULL DEFAULT ''"),
        ("upstream_files", "TEXT NOT NULL DEFAULT '[]'"),
        ("downstream_outputs", "TEXT NOT NULL DEFAULT '[]'"),
        ("allowed_touch", "TEXT NOT NULL DEFAULT '[]'"),
        ("forbidden_touch", "TEXT NOT NULL DEFAULT '[]'"),
        ("applicable_rules", "TEXT NOT NULL DEFAULT '[]'"),
        ("context_assembly_manifest", "TEXT NOT NULL DEFAULT '[]'"),
        ("rollback_instructions", "TEXT NOT NULL DEFAULT ''"),
        ("estimated_tokens", "INTEGER NOT NULL DEFAULT 0"),
        ("timeout_minutes", "INTEGER NOT NULL DEFAULT 0"),
        ("completed_gates", "TEXT NOT NULL DEFAULT '[]'"),
        ("blocked_gates", "TEXT NOT NULL DEFAULT '{}'"),
        ("assigned_pipeline", "TEXT NOT NULL DEFAULT ''"),
        ("pipeline_modules", "TEXT NOT NULL DEFAULT '[]'"),
        ("blocked_by", "TEXT NOT NULL DEFAULT '[]'"),
        ("artifact_paths", "TEXT NOT NULL DEFAULT '[]'"),
        ("audit_findings", "TEXT NOT NULL DEFAULT '[]'"),
        ("ke_entries", "TEXT NOT NULL DEFAULT '[]'"),
        ("ai_autonomy_level", "TEXT NOT NULL DEFAULT 'supervised'"),
        ("autonomy_checklist", "TEXT NOT NULL DEFAULT '[]'"),
        ("construction_status", "TEXT NOT NULL DEFAULT 'pending'"),
        ("verification_status", "TEXT NOT NULL DEFAULT 'unverified'"),
    ]

    for col_name, col_def in _taskcard_new_columns:
        if col_name not in columns:
            conn.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}")


def table_names(db_path: Optional[Path | str] = None) -> list[str]:
    """返回数据库中所有表名（不含视图）。"""
    resolved = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def view_names(db_path: Optional[Path | str] = None) -> list[str]:
    """返回数据库中所有视图名。"""
    resolved = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI 入口（便于直接运行 python -m zephyr.db.sqlite_schema 初始化）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    db = init_db(echo=True)
    tables = table_names(db)
    views = view_names(db)
    print(f"\n✅ 初始化完成：{db}")
    print(f"   表（{len(tables)} 个）：{', '.join(tables)}")
    print(f"   视图（{len(views)} 个）：{', '.join(views)}")
    sys.exit(0)
