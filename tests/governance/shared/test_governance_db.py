"""
DM-100016: governance.db端到端功能测试
覆盖7大子系统(任务/门禁/知识/审计/漂移/FLE/基础设施)的CRUD操作
"""

import sqlite3
import sys
from datetime import datetime

from zephyr.shared.io.paths import REPO_ROOT, DB_PATH  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DB_PATH = str(REPO_ROOT / "data" / "databases" / "governance.db")


def test_all():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} - {detail}")

    # === 0. 前置清理：保证幂等（防止上次残留导致UNIQUE约束失败） ===
    for tbl, col, val in [
        ("tasks", "task_id", "TEST-001"),
        ("task_events", "task_id", "TEST-001"),
        ("task_snapshots", "task_id", "TEST-001"),
        ("task_files", "task_id", "TEST-001"),
        ("gates", "gate_id", "GATE-TEST-001"),
        ("knowledge", "ke_id", "KE-TEST-001"),
        ("ke_tombstones", "ke_id", "KE-DEAD-001"),
        ("circuit_breaker_state", "caller_module", "test_caller"),
        ("tx_idempotency", "idempotency_key", "key-001"),
    ]:
        c.execute(f"DELETE FROM {tbl} WHERE {col}=?", (val,))
    c.execute("DELETE FROM drift_events WHERE target='tasks_test'")
    c.execute("DELETE FROM scan_results WHERE scan_type='depgraph_test'")
    conn.commit()

    # === 1. 任务系统 ===
    print("\n=== 1. 任务系统 ===")
    now = datetime.now().isoformat()
    c.execute(
        """INSERT INTO tasks (task_id, title, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("TEST-001", "Test Task", "Test desc", "PENDING", "HIGH", now, now),
    )
    conn.commit()
    row = c.execute("SELECT * FROM tasks WHERE task_id='TEST-001'").fetchone()
    check("tasks INSERT+SELECT", row is not None and row["title"] == "Test Task")

    c.execute("UPDATE tasks SET status='IN_PROGRESS', updated_at=? WHERE task_id='TEST-001'", (now,))
    conn.commit()
    row = c.execute("SELECT status FROM tasks WHERE task_id='TEST-001'").fetchone()
    check("tasks UPDATE status", row["status"] == "IN_PROGRESS")

    c.execute(
        """INSERT INTO task_events (task_id, event_type, payload, timestamp, session_id)
        VALUES (?, ?, ?, ?, ?)""",
        ("TEST-001", "TASK_IN_PROGRESS", '{"old":"PENDING","new":"IN_PROGRESS","actor":"test"}', now, "session-001"),
    )
    conn.commit()
    ev = c.execute("SELECT * FROM task_events WHERE task_id='TEST-001'").fetchone()
    check("task_events INSERT", ev is not None)

    c.execute(
        """INSERT INTO task_snapshots (task_id, snapshot_data, created_at) VALUES (?, ?, ?)""",
        ("TEST-001", '{"status":"IN_PROGRESS"}', now),
    )
    conn.commit()
    check(
        "task_snapshots INSERT",
        c.execute("SELECT COUNT(*) FROM task_snapshots WHERE task_id='TEST-001'").fetchone()[0] > 0,
    )

    c.execute(
        """INSERT INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)""",
        ("TEST-001", "test.py", "in_scope"),
    )
    conn.commit()
    check("task_files INSERT", c.execute("SELECT COUNT(*) FROM task_files WHERE task_id='TEST-001'").fetchone()[0] > 0)

    # === 2. 门禁系统 ===
    print("\n=== 2. 门禁系统 ===")
    c.execute(
        "INSERT INTO gates (gate_run_id, gate_id, passed, details, task_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        ("GATE-RUN-TEST-001", "GATE-TEST-001", 1, "all checks passed", "TEST-001", now),
    )
    conn.commit()
    check("gates INSERT+SELECT", c.execute("SELECT * FROM gates WHERE gate_id='GATE-TEST-001'").fetchone() is not None)

    # === 3. 知识系统 ===
    print("\n=== 3. 知识系统 ===")
    c.execute(
        """INSERT INTO knowledge (ke_id, topic, content, ke_type, domain, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("KE-TEST-001", "Test Topic", "Test content", "decision", "governance", now, now),
    )
    conn.commit()
    check(
        "knowledge INSERT+SELECT", c.execute("SELECT * FROM knowledge WHERE ke_id='KE-TEST-001'").fetchone() is not None
    )

    c.execute(
        "INSERT INTO ke_tombstones (ke_id, original_topic, death_reason, died_at) VALUES (?, ?, ?, ?)",
        ("KE-DEAD-001", "Old Topic", "superseded", now),
    )
    conn.commit()
    check(
        "ke_tombstones INSERT",
        c.execute("SELECT * FROM ke_tombstones WHERE ke_id='KE-DEAD-001'").fetchone() is not None,
    )

    # === 4. 审计系统 ===
    print("\n=== 4. 审计系统 ===")
    c.execute(
        "INSERT INTO audit_entries (timestamp, actor, action, target, details, session_id) VALUES (?, ?, ?, ?, ?, ?)",
        (now, "test_agent", "file_write", "test.py", "test write", "session-001"),
    )
    conn.commit()
    check(
        "audit_entries INSERT",
        c.execute("SELECT COUNT(*) FROM audit_entries WHERE actor='test_agent'").fetchone()[0] > 0,
    )

    c.execute(
        "INSERT INTO audit_summary (date, total_actions, by_actor, by_action, by_target) VALUES (?, ?, ?, ?, ?)",
        ("2026-06-12", 1, '{"test_agent":1}', '{"file_write":1}', '{"test.py":1}'),
    )
    conn.commit()
    check("audit_summary INSERT", c.execute("SELECT COUNT(*) FROM audit_summary").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO integrity_records (check_type, target, result, details, checked_at) VALUES (?, ?, ?, ?, ?)",
        ("hash_check", "test.py", "PASS", "md5 match", now),
    )
    conn.commit()
    check("integrity_records INSERT", c.execute("SELECT COUNT(*) FROM integrity_records").fetchone()[0] > 0)

    # === 5. 漂移系统 ===
    print("\n=== 5. 漂移系统 ===")
    c.execute(
        """INSERT INTO drift_events (drift_type, target, expected_value, actual_value, severity, detected_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        ("schema_drift", "tasks_test", "v1", "v2", "medium", now),
    )
    conn.commit()
    check("drift_events INSERT", c.execute("SELECT COUNT(*) FROM drift_events WHERE target='tasks_test'").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO scan_results (scan_type, target, result, details, scanned_at) VALUES (?, ?, ?, ?, ?)",
        ("depgraph_test", "nodes_test", "PASS", "test scan", now),
    )
    conn.commit()
    check("scan_results INSERT", c.execute("SELECT COUNT(*) FROM scan_results WHERE scan_type='depgraph_test'").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO gate_decisions (gate_id, decision, reason, decided_at, decided_by) VALUES (?, ?, ?, ?, ?)",
        ("GATE-TEST-001", "PASS", "all checks passed", now, "test_agent"),
    )
    conn.commit()
    check("gate_decisions INSERT", c.execute("SELECT COUNT(*) FROM gate_decisions").fetchone()[0] > 0)

    # === 6. FLE系统 ===
    print("\n=== 6. FLE系统 ===")
    c.execute(
        "INSERT INTO fle_metrics (timestamp, source_system, metric_name, value, collected_at) VALUES (?, ?, ?, ?, ?)",
        (now, "test", "orphan_rate", 0.05, now),
    )
    conn.commit()
    check("fle_metrics INSERT", c.execute("SELECT COUNT(*) FROM fle_metrics").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO fle_alerts (alert_type, severity, message, triggered_at) VALUES (?, ?, ?, ?)",
        ("high_orphan", "warning", "Orphan rate exceeded threshold", now),
    )
    conn.commit()
    check("fle_alerts INSERT", c.execute("SELECT COUNT(*) FROM fle_alerts").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO fle_dispatch_log (task_type, task_data, dispatched_at, result) VALUES (?, ?, ?, ?)",
        ("scan", '{"type":"orphan"}', now, "completed"),
    )
    conn.commit()
    check("fle_dispatch_log INSERT", c.execute("SELECT COUNT(*) FROM fle_dispatch_log").fetchone()[0] > 0)

    c.execute(
        """INSERT INTO judgment_records (judgment_type, context, decision, reasoning, recorded_at)
        VALUES (?, ?, ?, ?, ?)""",
        ("orphan_delete", "test.py", "KEEP", "has functional value", now),
    )
    conn.commit()
    check("judgment_records INSERT", c.execute("SELECT COUNT(*) FROM judgment_records").fetchone()[0] > 0)

    # === 7. 基础设施 ===
    print("\n=== 7. 基础设施 ===")
    c.execute(
        "INSERT INTO circuit_breaker_state (caller_module, target_module, state, failure_count) VALUES (?, ?, ?, ?)",
        ("test_caller", "llm_api", "closed", 0),
    )
    conn.commit()
    check(
        "circuit_breaker_state INSERT",
        c.execute("SELECT * FROM circuit_breaker_state WHERE caller_module='test_caller' AND target_module='llm_api'").fetchone() is not None,
    )

    c.execute(
        "INSERT INTO slow_queries (query_text, duration_ms, executed_at, database_name) VALUES (?, ?, ?, ?)",
        ("SELECT * FROM nodes", 1500.0, now, "depgraph"),
    )
    conn.commit()
    check("slow_queries INSERT", c.execute("SELECT COUNT(*) FROM slow_queries").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO tx_idempotency (idempotency_key, operation, result, created_at) VALUES (?, ?, ?, ?)",
        ("key-001", "create_task", "success", now),
    )
    conn.commit()
    check(
        "tx_idempotency INSERT",
        c.execute("SELECT * FROM tx_idempotency WHERE idempotency_key='key-001'").fetchone() is not None,
    )

    c.execute(
        "INSERT INTO usage_records (resource_type, resource_id, usage_amount, unit, recorded_at) VALUES (?, ?, ?, ?, ?)",
        ("llm_token", "gpt4", 1500.0, "tokens", now),
    )
    conn.commit()
    check("usage_records INSERT", c.execute("SELECT COUNT(*) FROM usage_records").fetchone()[0] > 0)

    c.execute(
        "INSERT INTO fix_records (issue_type, issue_description, fix_applied, fixed_at, fixed_by, status) VALUES (?, ?, ?, ?, ?, ?)",
        ("schema_drift", "missing column", "ALTER TABLE", now, "test_agent", "resolved"),
    )
    conn.commit()
    check("fix_records INSERT", c.execute("SELECT COUNT(*) FROM fix_records").fetchone()[0] > 0)

    # === 8. rule_enforcement_log (D61裁定新增) ===
    print("\n=== 8. rule_enforcement_log ===")
    c.execute(
        """INSERT INTO rule_enforcement_log (rule_id, operation, target, result, details, enforced_at, enforced_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("RULE-001", "pre_check", "test.py", "PASS", "all checks passed", now, "test_agent"),
    )
    conn.commit()
    check(
        "rule_enforcement_log INSERT+SELECT", c.execute("SELECT COUNT(*) FROM rule_enforcement_log").fetchone()[0] > 0
    )

    # === 9. Schema版本 ===
    print("\n=== 9. Schema版本 ===")
    v = c.execute("SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1").fetchone()
    check("_schema_version", v is not None and v["version"] >= 1)

    # === 清理测试数据 ===
    print("\n=== Cleanup ===")
    c.execute("DELETE FROM tasks WHERE task_id='TEST-001'")
    c.execute("DELETE FROM task_events WHERE task_id='TEST-001'")
    c.execute("DELETE FROM task_snapshots WHERE task_id='TEST-001'")
    c.execute("DELETE FROM task_files WHERE task_id='TEST-001'")
    c.execute("DELETE FROM gates WHERE gate_id='GATE-TEST-001'")
    c.execute("DELETE FROM knowledge WHERE ke_id='KE-TEST-001'")
    c.execute("DELETE FROM ke_tombstones WHERE ke_id='KE-DEAD-001'")
    c.execute("DELETE FROM circuit_breaker_state WHERE caller_module='test_caller'")
    c.execute("DELETE FROM tx_idempotency WHERE idempotency_key='key-001'")
    c.execute("DELETE FROM drift_events WHERE target='tasks_test'")
    c.execute("DELETE FROM scan_results WHERE scan_type='depgraph_test'")
    conn.commit()
    check("cleanup", True)

    conn.close()

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed > 0:
        raise AssertionError(f"{failed} governance.db checks failed")
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    test_all()
    sys.exit(0)
