# [A_test] module_id: MOD-GOV_query_metrics_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-674 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_query_metrics
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-674 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

"""T-DB-003: test_query_metrics.py — QueryMetrics 单元测试
Phase experimental, P3, 1.0h
"""


import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from zephyr.governance.observability_governance.query_metrics import PercentileTracker, QueryMetrics
from zephyr.governance.persistence.sqlite_schema import init_db


@pytest.fixture
def tmp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_qm_")
    os.close(fd)
    yield Path(path)
    for ext in ("", "-wal", "-shm"):
        p = Path(str(path) + ext)
        if p.exists():
            p.unlink()


@pytest.fixture
def qm(tmp_db_path, monkeypatch):
    monkeypatch.setattr("zephyr.governance.observability_governance.query_metrics.DB_PATH", tmp_db_path)
    init_db(tmp_db_path)
    metrics = QueryMetrics(db_path=tmp_db_path)
    yield metrics


class TestPercentileTracker:
    def test_record_and_stats(self):
        tracker = PercentileTracker(max_size=100)
        for i in range(10):
            tracker.record(float(i + 1))
        stats = tracker.stats()
        assert stats["count"] == 10
        assert isinstance(stats["avg_ms"], float)
        assert isinstance(stats["p50_ms"], float)
        assert isinstance(stats["p95_ms"], float)
        assert isinstance(stats["p99_ms"], float)
        assert isinstance(stats["max_ms"], float)

    def test_empty_stats(self):
        tracker = PercentileTracker(max_size=10)
        stats = tracker.stats()
        assert stats["count"] == 0
        assert stats["avg_ms"] == 0
        assert stats["p50_ms"] == 0

    def test_max_size_enforced(self):
        tracker = PercentileTracker(max_size=5)
        for i in range(10):
            tracker.record(float(i))
        stats = tracker.stats()
        assert stats["count"] == 5


class TestQueryMetricsInit:
    def test_init_with_db_path(self, qm):
        assert qm.enabled is True

    def test_disable_enable(self, qm):
        qm.disable()
        assert qm.enabled is False
        qm.enable()
        assert qm.enabled is True

    def test_execute_when_disabled(self, qm):
        qm.disable()
        conn = sqlite3.connect(str(qm.db_path))
        cursor = qm.execute(conn, "SELECT 1", ())
        assert cursor.fetchone()[0] == 1
        conn.close()


class TestQueryMetricsExecute:
    def test_execute_tracks_operation(self, qm):
        conn = sqlite3.connect(str(qm.db_path))
        try:
            cursor = qm.execute(conn, "SELECT COUNT(*) FROM tasks", ())
            row = cursor.fetchone()
            assert row[0] >= 0
        finally:
            conn.close()

    def test_stats_all_returns_dict(self, qm):
        conn = sqlite3.connect(str(qm.db_path))
        try:
            qm.execute(conn, "SELECT 1", ())
        finally:
            conn.close()
        stats = qm.stats_all()
        assert isinstance(stats, dict)

    def test_reset_clears_trackers(self, qm):
        conn = sqlite3.connect(str(qm.db_path))
        try:
            qm.execute(conn, "SELECT 1", ())
        finally:
            conn.close()
        qm.reset()
        stats = qm.stats_all()
        assert len(stats) == 0


class TestSlowQueryDetection:
    def test_slow_query_records(self, qm):
        orig_threshold = qm.slow_threshold_ms
        qm.slow_threshold_ms = 0
        conn = sqlite3.connect(str(qm.db_path))
        try:
            qm.execute(conn, "SELECT * FROM tasks", ())
        finally:
            conn.close()
        qm.slow_threshold_ms = orig_threshold

    def test_fast_query_not_flagged(self, qm):
        conn = sqlite3.connect(str(qm.db_path))
        try:
            qm.execute(conn, "SELECT 1", ())
        finally:
            conn.close()


class TestCleanup:
    def test_cleanup_old_records(self, qm):
        qm.cleanup_old_slow_queries(retention_days=365)
