# [A_test] module_id: SRC-TST-1018 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_metrics_collector
# [INVARIANTS] MetricsCollector uses SQLite; record returns metric_id; query returns list[dict]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import time

import pytest

from zephyr.feedback_loop.metrics_collector import MetricsCollector, MetricType


class TestMetricsCollectorInstantiation:
    def test_default_in_memory(self):
        mc = MetricsCollector()
        assert mc._db_path == ":memory:"

    def test_custom_db_path(self):
        mc = MetricsCollector(db_path=":memory:")
        assert mc._db_path == ":memory:"


class TestMetricsCollectorRecord:
    def test_record_returns_id(self):
        mc = MetricsCollector()
        mid = mc.record(MetricType.TASK_DURATION_MS, 150.0)
        assert isinstance(mid, str)
        assert len(mid) > 0

    def test_record_with_tags(self):
        mc = MetricsCollector()
        mid = mc.record(MetricType.TASK_COUNT, 5, tags={"phase": 1})
        assert isinstance(mid, str)

    def test_record_zero_value(self):
        mc = MetricsCollector()
        mid = mc.record(MetricType.FAILURE_RATE, 0.0)
        assert isinstance(mid, str)

    def test_record_negative_value(self):
        mc = MetricsCollector()
        mid = mc.record(MetricType.TOKEN_COST_USD, -1.0)
        assert isinstance(mid, str)


class TestMetricsCollectorBulkRecord:
    def test_bulk_record(self):
        mc = MetricsCollector()
        records = [
            {"metric_type": MetricType.TASK_COUNT, "value": 5, "tags": {"phase": 1}},
            {"metric_type": MetricType.FAILURE_RATE, "value": 0.1},
        ]
        ids = mc.bulk_record(records)
        assert len(ids) == 2

    def test_bulk_record_empty(self):
        mc = MetricsCollector()
        ids = mc.bulk_record([])
        assert ids == []

    def test_bulk_record_string_metric_type(self):
        mc = MetricsCollector()
        records = [
            {"metric_type": "task_duration_ms", "value": 100.0},
        ]
        ids = mc.bulk_record(records)
        assert len(ids) == 1


class TestMetricsCollectorQuery:
    def test_query_all(self):
        mc = MetricsCollector()
        mc.record(MetricType.TASK_DURATION_MS, 100.0)
        mc.record(MetricType.TASK_COUNT, 5)
        results = mc.query()
        assert len(results) == 2

    def test_query_by_type(self):
        mc = MetricsCollector()
        mc.record(MetricType.TASK_DURATION_MS, 100.0)
        mc.record(MetricType.TASK_COUNT, 5)
        results = mc.query(metric_type=MetricType.TASK_COUNT)
        assert len(results) == 1
        assert results[0]["metric_type"] == "task_count"

    def test_query_with_time_range(self):
        mc = MetricsCollector()
        t0 = time.time()
        mc.record(MetricType.TASK_DURATION_MS, 100.0)
        results = mc.query(since=t0 - 1, until=t0 + 10)
        assert len(results) >= 1

    def test_query_empty_db(self):
        mc = MetricsCollector()
        results = mc.query()
        assert results == []


class TestMetricsCollectorAggregate:
    def test_aggregate_basic(self):
        mc = MetricsCollector()
        mc.record(MetricType.TASK_DURATION_MS, 100.0)
        mc.record(MetricType.TASK_DURATION_MS, 200.0)
        agg = mc.aggregate(MetricType.TASK_DURATION_MS)
        assert agg["count"] == 2
        assert agg["total"] == pytest.approx(300.0)
        assert agg["average"] == pytest.approx(150.0)
        assert agg["min"] == pytest.approx(100.0)
        assert agg["max"] == pytest.approx(200.0)

    def test_aggregate_empty(self):
        mc = MetricsCollector()
        agg = mc.aggregate(MetricType.FAILURE_RATE)
        assert agg["count"] == 0
        assert agg["total"] == 0.0


class TestMetricsCollectorClose:
    def test_close(self):
        mc = MetricsCollector()
        mc.close()
        assert mc._conn is None

    def test_double_close(self):
        mc = MetricsCollector()
        mc.close()
        mc.close()
        assert mc._conn is None


class TestMetricType:
    def test_all_members(self):
        expected = {
            "TASK_DURATION_MS",
            "TOKEN_COST_USD",
            "TASK_COUNT",
            "FAILURE_RATE",
            "SESSION_ELAPSED_MS",
        }
        actual = {m.name for m in MetricType}
        assert actual == expected

    def test_is_string_enum(self):
        assert isinstance(MetricType.TASK_DURATION_MS, str)
