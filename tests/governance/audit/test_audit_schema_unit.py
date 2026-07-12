# [A_test] module_id: SRC-TST-1977 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-594 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_audit_schema
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""T-DB-002: test_audit_schema.py — AuditQuery 单元测试
Phase experimental, P1, 1.5h
"""


import os
import tempfile
from pathlib import Path

import pytest

from zephyr.gov_audit.audit_schema import AuditQuery
from zephyr.governance.persistence.sqlite_schema import init_db


@pytest.fixture
def tmp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_audit_")
    os.close(fd)
    yield Path(path)
    for ext in ("", "-wal", "-shm"):
        p = Path(str(path) + ext)
        if p.exists():
            p.unlink()


@pytest.fixture
def audit_query(tmp_db_path):
    init_db(tmp_db_path)
    return AuditQuery(db_path=tmp_db_path, auto_init=False)


class TestAuditQueryInit:
    def test_init_with_auto_init(self, tmp_db_path):
        aq = AuditQuery(db_path=tmp_db_path, auto_init=True)
        assert tmp_db_path.exists()

    def test_init_without_auto_init(self, tmp_db_path):
        init_db(tmp_db_path)
        aq = AuditQuery(db_path=tmp_db_path, auto_init=False)
        assert tmp_db_path.exists()


class TestQueryCompensationEvents:
    def test_returns_empty_list_when_no_events(self, audit_query):
        events = audit_query.query_compensation_events()
        assert isinstance(events, list)
        assert len(events) == 0

    def test_returns_list_of_dicts(self, audit_query):
        events = audit_query.query_compensation_events()
        for ev in events:
            assert "event_id" in ev
            assert "event_type" in ev


class TestQuerySchemaDrift:
    def test_returns_drift_report(self, audit_query):
        report = audit_query.query_schema_drift()
        assert "current_version" in report
        assert "registered_max_version" in report
        assert "is_latest" in report
        assert "migrations" in report

    def test_is_latest_when_no_pending(self, audit_query):
        report = audit_query.query_schema_drift()
        assert report["is_latest"] is True


class TestQueryTaskStatusHistory:
    def test_returns_empty_for_nonexistent_task(self, audit_query):
        history = audit_query.query_task_status_history("NONEXIST-TASK-9999")
        assert isinstance(history, list)
        assert len(history) == 0


class TestQueryRecentSessionsAudit:
    def test_returns_empty_when_no_sessions(self, audit_query):
        sessions = audit_query.query_recent_sessions_audit()
        assert isinstance(sessions, list)
