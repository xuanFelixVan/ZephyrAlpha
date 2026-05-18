# [BLUEPRINT] MOD-INF-012 | 03_modules/_cross_layer/database/blueprint.md | §

# [MODULE] zephyr.db.sqlite_schema

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + MOD-INF-012 v2.0）
======================================================================
依据：ADR-0030（SQLite 作为 experimental 元数据层）

物理路径：data/zalpha_metadata.db
Safety  : M（DDL 定义，init_db 幂等执行）

表结构
------
1. tasks                 — 任务登记表（10 状态流转 + namespace 分类）
2. task_files            — 任务-文件 N:N 映射表（#21 裁定）
3. events                — 事件流（DeferredQueue 消费）
4. knowledge             — KE 索引
5. gates                 — 门禁运行记录
6. circuit_breaker_state — CBG 模块间熔断状态（T-V2-005 experimental）
7. _schema_version       — Schema 版本追踪（MOD-INF-012 v2.0 新增）
8. slow_queries          — 慢查询记录（MOD-INF-012 v2.0 新增）
9. tx_idempotency        — ATM 事务幂等去重表（MOD-INF-012 v2.0 新增）

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
  wal_autocheckpoint = 4096

用法
----
    from zephyr.db.sqlite_schema import init_db, get_db_connection, DB_PATH

    init_db()              # 幂等，可重复调用
    conn = get_db_connection()   # 返回配置好 PRAGMA 的连接
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root from {current}")


DB_PATH: Path = _find_repo_root() / "data" / "zalpha_metadata.db"

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
    files_in_scope   TEXT    NOT NULL DEFAULT '[]',
    deliverables     TEXT    NOT NULL DEFAULT '[]',
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
CREATE TABLE IF NOT EXISTS gates (
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
# DDL — _schema_version 表（MOD-INF-012 v2.0：Schema 版本追踪）
# ---------------------------------------------------------------------------

_DDL_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS _schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT    NOT NULL,
    description TEXT    NOT NULL
)
"""

# ---------------------------------------------------------------------------
# DDL — slow_queries 表（MOD-INF-012 v2.0：慢查询记录）
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
# DDL — tx_idempotency 表（MOD-INF-012 v2.0：ATM 事务幂等去重）
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
# DDL — 索引（ADR-0030 §4.2）
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
    "CREATE INDEX IF NOT EXISTS idx_gates_gate_id      ON gates(gate_id)",
    "CREATE INDEX IF NOT EXISTS idx_gates_session      ON gates(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_cat      ON knowledge(category)",
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
# PRAGMA 配置
# ---------------------------------------------------------------------------

_PRAGMAS = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = NORMAL",
    "PRAGMA foreign_keys = ON",
    "PRAGMA busy_timeout = 5000",
    "PRAGMA temp_store = MEMORY",
    "PRAGMA wal_autocheckpoint = 4096",
]


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    """对连接应用 ADR-0030 §4.3 PRAGMA 基线。"""
    for pragma in _PRAGMAS:
        conn.execute(pragma)


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------


def get_db_connection(
    db_path: Path | str | None = None,
    *,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """
    返回配置好 PRAGMA 的 SQLite 连接。

    参数
    ----
    db_path
        数据库文件路径，默认 DB_PATH。
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
        isolation_level=None,
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


# ---------------------------------------------------------------------------
# 版本化迁移框架（MOD-INF-012 v2.0）
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
            "CHECK(namespace IN ('ADR','CP','KE','STD','DW','SRC','OPS'))",
            "ALTER TABLE tasks ADD COLUMN seq INTEGER NOT NULL DEFAULT 0 CHECK(seq >= 1)",
            _DDL_TASK_FILES,
            "CREATE INDEX IF NOT EXISTS idx_tf_task ON task_files(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_tf_file ON task_files(file_path)",
        ],
    ),
    (
        3,
        "v2 fields: priority + model_rationale + actual_hours + files_in_scope + tags + completed_at + name→title (#12)",
        [
            "ALTER TABLE tasks RENAME COLUMN name TO title",
            "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'P2' "
            "CHECK(priority IN ('P0','P1','P2','P3'))",
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
        "TaskCard 24 extension columns (MOD-INF-006 v0.3.0)",
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
        "MOD-INF-012 v2.0: _schema_version + slow_queries + tx_idempotency + wal_autocheckpoint",
        [
            _DDL_SCHEMA_VERSION,
            _DDL_SLOW_QUERIES,
            _DDL_TX_IDEMPOTENCY,
            "CREATE INDEX IF NOT EXISTS idx_tasks_is_deleted ON tasks(is_deleted)",
        ],
    ),
    (
        8,
        "MOD-INF-012 v2.0: soft delete columns on tasks",
        [
            "ALTER TABLE tasks ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0 CHECK(is_deleted IN (0,1))",
            "ALTER TABLE tasks ADD COLUMN deleted_at TEXT",
        ],
    ),
    (
        9,
        "MOD-INF-006 v0.3.2: schema_version column + fix default value drift (B29+B35)",
        [
            "ALTER TABLE tasks ADD COLUMN schema_version TEXT NOT NULL DEFAULT '0.3.2'",
            "UPDATE tasks SET estimated_tokens = 8000 WHERE estimated_tokens = 0 OR estimated_tokens < 500",
            "UPDATE tasks SET timeout_minutes = 30 WHERE timeout_minutes = 0 OR timeout_minutes < 5",
            "UPDATE tasks SET execution_model = 'deepseek' WHERE execution_model NOT IN ('deepseek','glm','claude','kimi','qwen')",
        ],
    ),
    (
        10,
        "MOD-INF-006 v0.3.3: P4 priority + approval_required/rejection_cooldown (B53+B55)",
        [
            "ALTER TABLE tasks ADD COLUMN approval_required INTEGER NOT NULL DEFAULT 0 CHECK(approval_required IN (0,1))",
            "ALTER TABLE tasks ADD COLUMN rejection_cooldown_until TEXT",
            "ALTER TABLE tasks ADD COLUMN priority_proposed TEXT",
        ],
    ),
    (
        11,
        "MOD-INF-006 v0.3.4: block_sessions_count for escalation governance (B56)",
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
            """CREATE TABLE gates_v15 (
                gate_run_id TEXT PRIMARY KEY,
                gate_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK(passed IN (0,1)),
                details TEXT NOT NULL DEFAULT '{}',
                artifact_path TEXT,
                session_id TEXT,
                task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            )""",
            "INSERT OR IGNORE INTO gates_v15 SELECT * FROM gates",
            "DROP TABLE IF EXISTS gates",
            "ALTER TABLE gates_v15 RENAME TO gates",
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
            "CREATE INDEX IF NOT EXISTS idx_gates_gate_id ON gates(gate_id)",
            "CREATE INDEX IF NOT EXISTS idx_gates_session ON gates(session_id)",
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
]


def _get_current_version(conn: sqlite3.Connection) -> int:
    """返回当前数据库的 schema 版本（未初始化则返回 0）。"""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_schema_version'")
    if cursor.fetchone() is None:
        # _schema_version 表不存在 → 可能是旧数据库（已有表但无版本记录）
        # 检查核心表 tasks 是否存在来判断
        task_cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if task_cursor.fetchone() is not None:
            # 旧数据库：有 tasks 表但没有 _schema_version → 标记为 v6（最后一个旧迁移）
            return -6
        return 0
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
    row = cursor.fetchone()
    return row[0] if row else 0


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
            )
            if any(p in msg for p in benign):
                continue
            raise RuntimeError(f"Migration v{version} statement #{i}: {exc}\n" f"  SQL: {stmt[:200]}") from exc
    conn.execute(
        "INSERT OR IGNORE INTO _schema_version (version, applied_at, description) " "VALUES (?, ?, ?)",
        (version, now, description),
    )

    fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_violations:
        violations_str = "; ".join(str(v) for v in fk_violations[:5])
        raise RuntimeError(
            f"Migration v{version} FK integrity violation: {len(fk_violations)} row(s) — {violations_str}"
        )


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
    resolved: Path = Path(db_path) if db_path is not None else DB_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(resolved))
    try:
        _apply_pragmas(conn)

        # 步骤 1：先创建 _schema_version 表自身（以便后续迁移使用）
        conn.execute(_DDL_SCHEMA_VERSION.strip())

        # 步骤 2：检测当前版本
        current = _get_current_version(conn)

        if echo:
            print(f"[sqlite_schema] current version: {current}")

        # 步骤 3：处理旧数据库（有表但无 _schema_version）
        if current < 0:
            # current == -6 表示 v6 之前的迁移已通过 IF NOT EXISTS 完成
            bootstrapped = abs(current)
            if echo:
                print(f"[sqlite_schema] bootstrapping legacy DB → marking v1–v{abs(current)} as applied")
            from datetime import UTC, datetime

            now = datetime.now(UTC).isoformat()
            for v, desc, _ in _MIGRATIONS:
                if v <= bootstrapped:
                    conn.execute(
                        "INSERT OR IGNORE INTO _schema_version (version, applied_at, description) " "VALUES (?, ?, ?)",
                        (v, now, desc + " [bootstrap: legacy DB]"),
                    )
            current = bootstrapped

        # 步骤 4：只执行缺失的迁移版本
        conn.execute("BEGIN")
        try:
            for version, description, statements in _MIGRATIONS:
                if version <= current:
                    continue
                if echo:
                    print(f"[sqlite_schema] executing migration v{version}: {description}")
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
    resolved = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def view_names(db_path: Path | str | None = None) -> list[str]:
    """返回数据库中所有视图名。"""
    resolved = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(resolved))
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def schema_version(db_path: Path | str | None = None) -> int:
    """返回当前数据库的 schema 版本（供外部诊断）。"""
    resolved = Path(db_path) if db_path is not None else DB_PATH
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
    resolved = Path(db_path) if db_path is not None else DB_PATH
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
        pending.append({
            "version": version,
            "description": description,
            "status": status,
            "statement_count": len(statements),
            "ddl_preview": ddl_preview,
        })
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
# CLI 入口
# ---------------------------------------------------------------------------

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
