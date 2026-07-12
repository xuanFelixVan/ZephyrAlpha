# [A_test] module_id: SRC-TST-1854 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-482 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_audit_schema
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/db/audit_schema.py
=========================================
覆盖矩阵：
  AuditQuery:
    - 初始化（auto_init=True / False）× 2
    - query_audit_for_session × 1
    - query_compensation_events（空表）× 1
    - query_schema_drift × 1
    - query_task_status_history × 1
    - query_recent_sessions_audit（空表）× 1

Task: MOD-INF-012 | Safety: M
"""

import pytest

from zephyr.gov_audit.audit_schema import AuditQuery


@pytest.fixture
def aq(tmp_path):
    db_path = tmp_path / "test_audit.db"
    return AuditQuery(db_path, auto_init=True)


class TestAuditQueryInit:
    def test_init_with_auto_init(self, tmp_path):
        db_path = tmp_path / "aq_init.db"
        aq = AuditQuery(db_path, auto_init=True)
        assert db_path.exists()

    def test_init_without_auto_init(self, tmp_path):
        db_path = tmp_path / "aq_no_init.db"
        aq = AuditQuery(db_path, auto_init=False)
        conn = aq._get_conn()
        assert conn is not None
        conn.close()


class TestAuditQueryTrail:
    def test_query_audit_for_session_empty(self, aq):
        results = aq.query_audit_for_session("nonexistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_query_audit_for_session_with_data(self, aq):
        conn = aq._get_conn()
        try:
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, phase, execution_model,"
                " safety_level, created_at, updated_at, session_id)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "TA-001",
                    "OPS",
                    1,
                    "审计测试任务",
                    "COMPLETED",
                    1,
                    "deepseek",
                    "M",
                    "2026-05-06T12:00:00Z",
                    "2026-05-06T12:00:00Z",
                    "session-test",
                ),
            )
            conn.execute(
                "INSERT INTO events (event_id, event_type, payload, task_id, session_id, created_at)"
                " VALUES (?,?,?,?,?,?)",
                ("evt-001", "task_event", '{"step":"verify"}', "TA-001", "session-test", "2026-05-06T12:00:00Z"),
            )
            conn.commit()
        finally:
            conn.close()

        results = aq.query_audit_for_session("session-test")
        assert len(results) >= 1

    def test_query_task_status_history_empty(self, aq):
        results = aq.query_task_status_history("no-such-task")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_query_task_status_history_with_event(self, aq):
        conn = aq._get_conn()
        try:
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, phase, execution_model,"
                " safety_level, created_at, updated_at, session_id)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "TH-001",
                    "OPS",
                    1,
                    "历史测试任务",
                    "IN_PROGRESS",
                    1,
                    "deepseek",
                    "M",
                    "2026-05-06T12:00:00Z",
                    "2026-05-06T12:00:00Z",
                    "sess-h",
                ),
            )
            conn.execute(
                "INSERT INTO events (event_id, event_type, payload, task_id, session_id, created_at)"
                " VALUES (?,?,?,?,?,?)",
                ("evt-h1", "state_transition", '{"task_id":"TH-001"}', "TH-001", "sess-h", "2026-05-06T12:00:00Z"),
            )
            conn.commit()
        finally:
            conn.close()

        results = aq.query_task_status_history("TH-001")
        assert len(results) >= 1


class TestAuditQueryCompensation:
    def test_query_compensation_events_empty(self, aq):
        results = aq.query_compensation_events()
        assert isinstance(results, list)


class TestAuditQuerySchema:
    def test_query_schema_drift(self, aq):
        drift = aq.query_schema_drift()
        assert "current_version" in drift
        assert "registered_max_version" in drift
        assert "is_latest" in drift
        assert "migrations_applied" in drift
        assert isinstance(drift["migrations"], list)


class TestAuditQuerySessions:
    def test_query_recent_sessions_audit_empty(self, aq):
        results = aq.query_recent_sessions_audit(limit=5)
        assert isinstance(results, list)

    def test_query_recent_sessions_audit_with_data(self, aq):
        conn = aq._get_conn()
        try:
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, phase, execution_model,"
                " safety_level, created_at, updated_at, session_id)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "TS-001",
                    "OPS",
                    1,
                    "审计会话任务1",
                    "COMPLETED",
                    3,
                    "deepseek",
                    "M",
                    "2026-05-06T12:00:00Z",
                    "2026-05-06T12:00:00Z",
                    "sess-audit",
                ),
            )
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, phase, execution_model,"
                " safety_level, created_at, updated_at, session_id)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "TS-002",
                    "OPS",
                    2,
                    "审计会话任务2",
                    "VERIFIED",
                    3,
                    "deepseek",
                    "M",
                    "2026-05-06T12:00:00Z",
                    "2026-05-06T12:00:00Z",
                    "sess-audit",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        results = aq.query_recent_sessions_audit(limit=5)
        assert len(results) >= 1
        row = results[0]
        assert "session_id" in row
        assert "total_tasks" in row
