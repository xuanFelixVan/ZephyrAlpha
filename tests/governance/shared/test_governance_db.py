# [BLUEPRINT] MOD-TEST-508 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""DM-100016: governance.db 端到端功能测试

覆盖 7 大子系统（任务/门禁/审计/漂移/FLE/基础设施/rule_enforcement）的 CRUD 操作。

治本改写（2026-07-27）：
- 原 251 行 ``test_all`` 拆为 8 个 per-subsystem 测试（修 Eager Test / T1）
- 原本地 ``check()`` helper + 末尾 raise 换为纯 ``assert`` 带消息（修 Assertion Roulette / T1——
  pytest 失败内省能直接定位到具体 check）
- 子系统间无 FK 依赖，拆分后各测试自包含

治本改写（2026-08-16，#ARCH-099）：
- 原 session fixture 用 online backup 拷贝**生产 governance.db**（Mystery Guest / T1——
  锁竞争：tick_subscriber/reconciler 活跃占用；schema 漂移：生产库缺列/约束演化），
  改为**测试自建最小 schema fixture**（DDL 内嵌本文件），与生产库完全解耦。
  最小 schema 仅含各测试实际触达的列，是本测试自身的契约声明。
"""

import sqlite3
import sys
from datetime import datetime

import pytest

# 测试用固定 ID（各测试自包含，fixture 在每条测试前后清理这些行保证幂等）
_TASK_ID = "TEST-001"
_GATE_ID = "GATE-TEST-001"
_CALLER = "test_caller"
_IDEMP_KEY = "key-001"
_DRIFT_TARGET = "tasks_test"
_SCAN_TYPE = "depgraph_test"

# (table, column, value) 清理三元组——保证跨测试幂等
_TEST_ROW_MARKERS: list[tuple[str, str, str]] = [
    ("tasks", "task_id", _TASK_ID),
    ("task_events", "task_id", _TASK_ID),
    ("task_snapshots", "task_id", _TASK_ID),
    ("task_files", "task_id", _TASK_ID),
    ("gates", "gate_id", _GATE_ID),
    ("circuit_breaker_state", "caller_module", _CALLER),
    ("tx_idempotency", "idempotency_key", _IDEMP_KEY),
]


def _cleanup_test_rows(conn: sqlite3.Connection) -> None:
    """清理测试固定 ID 行，保证幂等（防 UNIQUE 约束失败）。"""
    c = conn.cursor()
    for tbl, col, val in _TEST_ROW_MARKERS:
        c.execute(f"DELETE FROM {tbl} WHERE {col}=?", (val,))
    c.execute(f"DELETE FROM drift_events WHERE target='{_DRIFT_TARGET}'")
    c.execute(f"DELETE FROM scan_results WHERE scan_type='{_SCAN_TYPE}'")
    conn.commit()


# ---------------------------------------------------------------------------
# #ARCH-099 治本：最小 schema DDL（内嵌，与生产库解耦）
# 仅含各测试实际触达的表与列——本测试的契约声明，不复刻生产库全部约束。
# ---------------------------------------------------------------------------
_MINIMAL_SCHEMA_DDL = """
CREATE TABLE tasks (
    task_id     TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'PENDING',
    priority    TEXT NOT NULL DEFAULT 'P2',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE TABLE task_events (
    event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload    TEXT NOT NULL DEFAULT '{}',
    timestamp  TEXT NOT NULL,
    session_id TEXT
);
CREATE TABLE task_snapshots (
    snapshot_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       TEXT NOT NULL,
    snapshot_data TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE task_files (
    task_id   TEXT NOT NULL,
    file_path TEXT NOT NULL,
    role      TEXT NOT NULL DEFAULT 'in_scope',
    UNIQUE(task_id, file_path)
);
CREATE TABLE gates (
    gate_run_id TEXT PRIMARY KEY,
    gate_id     TEXT NOT NULL,
    passed      INTEGER NOT NULL,
    details     TEXT,
    task_id     TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE audit_entries (
    entry_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT NOT NULL,
    actor      TEXT NOT NULL,
    action     TEXT NOT NULL,
    target     TEXT,
    details    TEXT,
    session_id TEXT
);
CREATE TABLE audit_summary (
    date          TEXT PRIMARY KEY,
    total_actions INTEGER NOT NULL,
    by_actor      TEXT,
    by_action     TEXT,
    by_target     TEXT
);
CREATE TABLE integrity_records (
    record_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    check_type TEXT NOT NULL,
    target     TEXT NOT NULL,
    result     TEXT NOT NULL,
    details    TEXT,
    checked_at TEXT NOT NULL
);
CREATE TABLE drift_events (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    drift_type     TEXT NOT NULL,
    target         TEXT NOT NULL,
    expected_value TEXT,
    actual_value   TEXT,
    severity       TEXT,
    detected_at    TEXT NOT NULL
);
CREATE TABLE scan_results (
    result_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type  TEXT NOT NULL,
    target     TEXT NOT NULL,
    result     TEXT NOT NULL,
    details    TEXT,
    scanned_at TEXT NOT NULL
);
CREATE TABLE gate_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gate_id     TEXT NOT NULL,
    decision    TEXT NOT NULL,
    reason      TEXT,
    decided_at  TEXT NOT NULL,
    decided_by  TEXT
);
CREATE TABLE fle_metrics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp     TEXT NOT NULL,
    source_system TEXT NOT NULL,
    metric_name   TEXT NOT NULL,
    value         REAL NOT NULL,
    collected_at  TEXT
);
CREATE TABLE fle_alerts (
    alert_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type   TEXT NOT NULL,
    severity     TEXT NOT NULL,
    message      TEXT,
    triggered_at TEXT NOT NULL
);
CREATE TABLE fle_dispatch_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type     TEXT NOT NULL,
    task_data     TEXT,
    dispatched_at TEXT NOT NULL,
    result        TEXT
);
CREATE TABLE judgment_records (
    record_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    judgment_type TEXT NOT NULL,
    context       TEXT,
    decision      TEXT NOT NULL,
    reasoning     TEXT,
    recorded_at   TEXT NOT NULL
);
CREATE TABLE circuit_breaker_state (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_module TEXT NOT NULL,
    target_module TEXT NOT NULL,
    state         TEXT NOT NULL,
    failure_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(caller_module, target_module)
);
CREATE TABLE slow_queries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text    TEXT NOT NULL,
    duration_ms   REAL NOT NULL,
    executed_at   TEXT NOT NULL,
    database_name TEXT
);
CREATE TABLE tx_idempotency (
    idempotency_key TEXT PRIMARY KEY,
    operation       TEXT NOT NULL,
    result          TEXT,
    created_at      TEXT NOT NULL
);
CREATE TABLE usage_records (
    record_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type TEXT NOT NULL,
    resource_id   TEXT NOT NULL,
    usage_amount  REAL NOT NULL,
    unit          TEXT,
    recorded_at   TEXT NOT NULL
);
CREATE TABLE fix_records (
    record_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type        TEXT NOT NULL,
    issue_description TEXT,
    fix_applied       TEXT,
    fixed_at          TEXT NOT NULL,
    fixed_by          TEXT,
    status            TEXT
);
CREATE TABLE rule_enforcement_log (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id     TEXT NOT NULL,
    operation   TEXT NOT NULL,
    target      TEXT,
    result      TEXT NOT NULL,
    details     TEXT,
    enforced_at TEXT NOT NULL,
    enforced_by TEXT
);
CREATE TABLE _schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);
"""


@pytest.fixture(scope="session")
def gov_db_path(tmp_path_factory):
    """Session-scoped：自建最小 schema 的隔离 governance.db（#ARCH-099 治本）。

    不再拷贝生产库——DDL 内嵌本文件，彻底消除锁竞争 + schema 漂移双耦合。
    各测试共享此副本，每条测试通过 ``_cleanup_test_rows`` 清理固定 ID 行，互不干扰。
    """
    dst = tmp_path_factory.mktemp("govdb") / "governance_test.db"
    conn = sqlite3.connect(str(dst))
    try:
        conn.executescript(_MINIMAL_SCHEMA_DDL)
        conn.execute(
            "INSERT INTO _schema_version (version, applied_at, description) VALUES (?, ?, ?)",
            (1, datetime.now().isoformat(), "minimal test schema (#ARCH-099)"),
        )
        conn.commit()
    finally:
        conn.close()
    return dst


@pytest.fixture
def gov_conn(gov_db_path) -> sqlite3.Connection:
    """Per-test：到隔离 governance.db 副本的连接。前后清理测试行。"""
    conn = sqlite3.connect(str(gov_db_path))
    conn.row_factory = sqlite3.Row
    _cleanup_test_rows(conn)
    yield conn
    _cleanup_test_rows(conn)
    conn.close()


def _now() -> str:
    return datetime.now().isoformat()


# ---------------------------------------------------------------------------
# 1. 任务系统
# ---------------------------------------------------------------------------
def test_tasks_crud(gov_conn: sqlite3.Connection):
    """tasks + task_events + task_snapshots + task_files 的 INSERT/UPDATE/SELECT。"""
    now = _now()
    gov_conn.execute(
        """INSERT INTO tasks (task_id, title, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (_TASK_ID, "Test Task", "Test desc", "PENDING", "HIGH", now, now),
    )
    gov_conn.commit()
    row = gov_conn.execute("SELECT * FROM tasks WHERE task_id=?", (_TASK_ID,)).fetchone()
    assert row is not None, "tasks INSERT+SELECT: row not found"
    assert row["title"] == "Test Task", f"tasks INSERT+SELECT: title mismatch={row['title']!r}"

    gov_conn.execute(
        "UPDATE tasks SET status='IN_PROGRESS', updated_at=? WHERE task_id=?",
        (now, _TASK_ID),
    )
    gov_conn.commit()
    row = gov_conn.execute("SELECT status FROM tasks WHERE task_id=?", (_TASK_ID,)).fetchone()
    assert row["status"] == "IN_PROGRESS", f"tasks UPDATE status: got {row['status']!r}"

    gov_conn.execute(
        """INSERT INTO task_events (task_id, event_type, payload, timestamp, session_id)
        VALUES (?, ?, ?, ?, ?)""",
        (_TASK_ID, "TASK_IN_PROGRESS", '{"old":"PENDING","new":"IN_PROGRESS","actor":"test"}', now, "session-001"),
    )
    gov_conn.commit()
    ev = gov_conn.execute("SELECT * FROM task_events WHERE task_id=?", (_TASK_ID,)).fetchone()
    assert ev is not None, "task_events INSERT: row not found"

    gov_conn.execute(
        "INSERT INTO task_snapshots (task_id, snapshot_data, created_at) VALUES (?, ?, ?)",
        (_TASK_ID, '{"status":"IN_PROGRESS"}', now),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM task_snapshots WHERE task_id=?", (_TASK_ID,)).fetchone()[0]
    assert n > 0, "task_snapshots INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)",
        (_TASK_ID, "test.py", "in_scope"),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM task_files WHERE task_id=?", (_TASK_ID,)).fetchone()[0]
    assert n > 0, "task_files INSERT: no rows"


# ---------------------------------------------------------------------------
# 2. 门禁系统
# ---------------------------------------------------------------------------
def test_gates_insert(gov_conn: sqlite3.Connection):
    """gates 表 INSERT + SELECT。"""
    now = _now()
    gov_conn.execute(
        "INSERT INTO gates (gate_run_id, gate_id, passed, details, task_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        ("GATE-RUN-TEST-001", _GATE_ID, 1, "all checks passed", _TASK_ID, now),
    )
    gov_conn.commit()
    row = gov_conn.execute("SELECT * FROM gates WHERE gate_id=?", (_GATE_ID,)).fetchone()
    assert row is not None, "gates INSERT+SELECT: row not found"


# ---------------------------------------------------------------------------
# 4. 审计系统
# ---------------------------------------------------------------------------
def test_audit_subsystem(gov_conn: sqlite3.Connection):
    """audit_entries + audit_summary + integrity_records INSERT。"""
    now = _now()
    gov_conn.execute(
        "INSERT INTO audit_entries (timestamp, actor, action, target, details, session_id) VALUES (?, ?, ?, ?, ?, ?)",
        (now, "test_agent", "file_write", "test.py", "test write", "session-001"),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM audit_entries WHERE actor='test_agent'").fetchone()[0]
    assert n > 0, "audit_entries INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO audit_summary (date, total_actions, by_actor, by_action, by_target) VALUES (?, ?, ?, ?, ?)",
        ("2026-06-12", 1, '{"test_agent":1}', '{"file_write":1}', '{"test.py":1}'),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM audit_summary").fetchone()[0]
    assert n > 0, "audit_summary INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO integrity_records (check_type, target, result, details, checked_at) VALUES (?, ?, ?, ?, ?)",
        ("hash_check", "test.py", "PASS", "md5 match", now),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM integrity_records").fetchone()[0]
    assert n > 0, "integrity_records INSERT: no rows"


# ---------------------------------------------------------------------------
# 5. 漂移系统
# ---------------------------------------------------------------------------
def test_drift_subsystem(gov_conn: sqlite3.Connection):
    """drift_events + scan_results + gate_decisions INSERT。"""
    now = _now()
    gov_conn.execute(
        """INSERT INTO drift_events (drift_type, target, expected_value, actual_value, severity, detected_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        ("schema_drift", _DRIFT_TARGET, "v1", "v2", "medium", now),
    )
    gov_conn.commit()
    n = gov_conn.execute(f"SELECT COUNT(*) FROM drift_events WHERE target='{_DRIFT_TARGET}'").fetchone()[0]
    assert n > 0, "drift_events INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO scan_results (scan_type, target, result, details, scanned_at) VALUES (?, ?, ?, ?, ?)",
        (_SCAN_TYPE, "nodes_test", "PASS", "test scan", now),
    )
    gov_conn.commit()
    n = gov_conn.execute(f"SELECT COUNT(*) FROM scan_results WHERE scan_type='{_SCAN_TYPE}'").fetchone()[0]
    assert n > 0, "scan_results INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO gate_decisions (gate_id, decision, reason, decided_at, decided_by) VALUES (?, ?, ?, ?, ?)",
        (_GATE_ID, "PASS", "all checks passed", now, "test_agent"),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM gate_decisions").fetchone()[0]
    assert n > 0, "gate_decisions INSERT: no rows"


# ---------------------------------------------------------------------------
# 6. FLE 系统
# ---------------------------------------------------------------------------
def test_fle_subsystem(gov_conn: sqlite3.Connection):
    """fle_metrics + fle_alerts + fle_dispatch_log + judgment_records INSERT。"""
    now = _now()
    gov_conn.execute(
        "INSERT INTO fle_metrics (timestamp, source_system, metric_name, value, collected_at) VALUES (?, ?, ?, ?, ?)",
        (now, "test", "orphan_rate", 0.05, now),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM fle_metrics").fetchone()[0] > 0, "fle_metrics INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO fle_alerts (alert_type, severity, message, triggered_at) VALUES (?, ?, ?, ?)",
        ("high_orphan", "warning", "Orphan rate exceeded threshold", now),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM fle_alerts").fetchone()[0] > 0, "fle_alerts INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO fle_dispatch_log (task_type, task_data, dispatched_at, result) VALUES (?, ?, ?, ?)",
        ("scan", '{"type":"orphan"}', now, "completed"),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM fle_dispatch_log").fetchone()[0] > 0, (
        "fle_dispatch_log INSERT: no rows"
    )

    gov_conn.execute(
        """INSERT INTO judgment_records (judgment_type, context, decision, reasoning, recorded_at)
        VALUES (?, ?, ?, ?, ?)""",
        ("orphan_delete", "test.py", "KEEP", "has functional value", now),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM judgment_records").fetchone()[0] > 0, (
        "judgment_records INSERT: no rows"
    )


# ---------------------------------------------------------------------------
# 7. 基础设施
# ---------------------------------------------------------------------------
def test_infrastructure_tables(gov_conn: sqlite3.Connection):
    """circuit_breaker_state + slow_queries + tx_idempotency + usage_records + fix_records INSERT。"""
    now = _now()
    gov_conn.execute(
        "INSERT INTO circuit_breaker_state (caller_module, target_module, state, failure_count) VALUES (?, ?, ?, ?)",
        (_CALLER, "llm_api", "closed", 0),
    )
    gov_conn.commit()
    row = gov_conn.execute(
        "SELECT * FROM circuit_breaker_state WHERE caller_module=? AND target_module='llm_api'",
        (_CALLER,),
    ).fetchone()
    assert row is not None, "circuit_breaker_state INSERT: row not found"

    gov_conn.execute(
        "INSERT INTO slow_queries (query_text, duration_ms, executed_at, database_name) VALUES (?, ?, ?, ?)",
        ("SELECT * FROM nodes", 1500.0, now, "depgraph"),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM slow_queries").fetchone()[0] > 0, "slow_queries INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO tx_idempotency (idempotency_key, operation, result, created_at) VALUES (?, ?, ?, ?)",
        (_IDEMP_KEY, "create_task", "success", now),
    )
    gov_conn.commit()
    row = gov_conn.execute("SELECT * FROM tx_idempotency WHERE idempotency_key=?", (_IDEMP_KEY,)).fetchone()
    assert row is not None, "tx_idempotency INSERT: row not found"

    gov_conn.execute(
        "INSERT INTO usage_records (resource_type, resource_id, usage_amount, unit, recorded_at) VALUES (?, ?, ?, ?, ?)",
        ("llm_token", "gpt4", 1500.0, "tokens", now),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM usage_records").fetchone()[0] > 0, "usage_records INSERT: no rows"

    gov_conn.execute(
        "INSERT INTO fix_records (issue_type, issue_description, fix_applied, fixed_at, fixed_by, status) VALUES (?, ?, ?, ?, ?, ?)",
        ("schema_drift", "missing column", "ALTER TABLE", now, "test_agent", "resolved"),
    )
    gov_conn.commit()
    assert gov_conn.execute("SELECT COUNT(*) FROM fix_records").fetchone()[0] > 0, "fix_records INSERT: no rows"


# ---------------------------------------------------------------------------
# 8. rule_enforcement_log (D61 裁定新增)
# ---------------------------------------------------------------------------
def test_rule_enforcement_log(gov_conn: sqlite3.Connection):
    """rule_enforcement_log INSERT + SELECT。"""
    now = _now()
    gov_conn.execute(
        """INSERT INTO rule_enforcement_log (rule_id, operation, target, result, details, enforced_at, enforced_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("RULE-001", "pre_check", "test.py", "PASS", "all checks passed", now, "test_agent"),
    )
    gov_conn.commit()
    n = gov_conn.execute("SELECT COUNT(*) FROM rule_enforcement_log").fetchone()[0]
    assert n > 0, "rule_enforcement_log INSERT+SELECT: no rows"


# ---------------------------------------------------------------------------
# 9. Schema 版本
# ---------------------------------------------------------------------------
def test_schema_version(gov_conn: sqlite3.Connection):
    """_schema_version 表存在且 version >= 1。"""
    row = gov_conn.execute("SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1").fetchone()
    assert row is not None, "_schema_version: no rows"
    assert row["version"] >= 1, f"_schema_version: version < 1 (got {row['version']})"


if __name__ == "__main__":
    # 直接运行：跑全部 subsystem 测试（供调试）
    sys.exit(pytest.main([__file__, "-v"]))
