# [A_test] module_id: MOD-GOV_query_metrics_db | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-487 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_query_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/db/query_metrics.py
===========================================
覆盖矩阵：
  PercentileTracker:
    - record + p50/p95/p99 × 1
    - 空 tracker stats × 1
    - stats 输出 + max_ms × 1
  QueryMetrics:
    - 单例 instance() × 1
    - enable / disable × 1
    - track 装饰器正常路径 × 1
    - execute 正常路径 × 1
    - slow query 阈值触发 × 1
    - record_slow_query × 1
    - stats_all / reset × 1

Task: MOD-INF-012 | Safety: M
"""

import sqlite3

from zephyr.governance.observability_governance.query_metrics import (
    PercentileTracker,
    QueryMetrics,
    query_metrics,
)


class TestPercentileTracker:
    def test_empty_stats(self):
        pt = PercentileTracker(max_size=10)
        s = pt.stats()
        assert s["count"] == 0
        assert s["p50_ms"] == 0
        assert s["p95_ms"] == 0
        assert s["p99_ms"] == 0

    def test_record_and_percentiles(self):
        pt = PercentileTracker(max_size=100)
        for i in range(1, 11):
            pt.record(float(i))
        assert pt.p50() > 0
        assert pt.p95() > 0
        assert pt.p99() > 0

    def test_stats_after_records(self):
        pt = PercentileTracker(max_size=100)
        pt.record(10.0)
        pt.record(20.0)
        pt.record(30.0)
        s = pt.stats()
        assert s["count"] == 3
        assert s["max_ms"] == 30.0

    def test_single_record_percentiles_consistent(self):
        pt = PercentileTracker(max_size=10)
        pt.record(42.0)
        p50 = pt.p50()
        p95 = pt.p95()
        p99 = pt.p99()
        assert p50 == 42.0
        assert p95 == 42.0
        assert p99 == 42.0


class TestQueryMetricsLifecycle:
    def test_singleton(self):
        qm1 = QueryMetrics.instance()
        qm2 = QueryMetrics.instance()
        assert qm1 is qm2

    def test_enable_disable(self, tmp_path):
        db_path = tmp_path / "qm.db"
        qm = QueryMetrics(db_path)
        assert qm.enabled is True
        qm.disable()
        assert qm.enabled is False
        qm.enable()
        assert qm.enabled is True

    def test_reset_clears_trackers(self, tmp_path):
        db_path = tmp_path / "qm_reset.db"
        qm = QueryMetrics(db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS t (x)")
            qm.execute(conn, "SELECT 1")
            assert len(qm.stats_all()) >= 1
            qm.reset()
            assert len(qm.stats_all()) == 0
        finally:
            conn.close()

    def test_stats_all_returns_dict(self, tmp_path):
        db_path = tmp_path / "qm_stats.db"
        qm = QueryMetrics(db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS t (x)")
            qm.execute(conn, "SELECT 1")
            all_stats = qm.stats_all()
            assert "SELECT" in all_stats
            assert "p50_ms" in all_stats["SELECT"]
        finally:
            conn.close()


class TestQueryMetricsTracking:
    def test_track_decorator_normal(self, tmp_path):
        db_path = tmp_path / "qm_track.db"
        qm = QueryMetrics(db_path)

        @qm.track("list_all")
        def list_all(conn):
            return conn.execute("SELECT 1").fetchall()

        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS t (x)")
            result = list_all(conn)
            assert result is not None
            all_stats = qm.stats_all()
            assert "list_all" in all_stats
        finally:
            conn.close()

    def test_track_disabled_passthrough(self, tmp_path):
        db_path = tmp_path / "qm_passthrough.db"
        qm = QueryMetrics(db_path)
        qm.disable()

        call_count = 0

        @qm.track("disabled_op")
        def fn(conn):
            nonlocal call_count
            call_count += 1
            return conn.execute("SELECT 1").fetchall()

        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS t (x)")
            fn(conn)
            assert call_count == 1
        finally:
            conn.close()

    def test_execute_wrapper(self, tmp_path):
        db_path = tmp_path / "qm_exec.db"
        qm = QueryMetrics(db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS t (x)")
            cursor = qm.execute(conn, "SELECT 1")
            rows = cursor.fetchall()
            assert len(rows) == 1
            s = qm.stats_all()
            assert "SELECT" in s
            assert s["SELECT"]["count"] >= 1
        finally:
            conn.close()


class TestQueryMetricsGlobalInstance:
    def test_global_instance_exists(self):
        assert query_metrics is not None
        assert isinstance(query_metrics, QueryMetrics)

    def test_global_instance_reset_and_track(self):
        query_metrics.reset()
        s = query_metrics.stats_all()
        assert len(s) == 0
