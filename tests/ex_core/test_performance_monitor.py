# [BLUEPRINT] MOD-EX-036 | docs/03_modules/MOD-EX-036/
# [MODULE] tests.ex_core.test_performance_monitor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/ex_core/test_performance_monitor.py -q
# [TTL] permanent

"""执行核心性能监控器（MOD-EX-036）单元测试——滑动窗口统计/p95/阈值告警。"""

from __future__ import annotations

import pytest

from zephyr.ex_core.performance_monitor import (
    InvalidPerformanceInputError,
    MetricStats,
    PerformanceMonitor,
)


class TestRecordAndStats:
    def test_record_and_basic_stats(self):
        m = PerformanceMonitor()
        for v in (10.0, 20.0, 30.0):
            m.record("order_submit_latency_ms", v)
        stats = m.stats("order_submit_latency_ms")
        assert isinstance(stats, MetricStats)
        assert stats.count == 3
        assert stats.mean == pytest.approx(20.0)
        assert stats.min == 10.0
        assert stats.max == 30.0

    def test_p95_with_window(self):
        m = PerformanceMonitor(window_size=100)
        for i in range(1, 101):
            m.record("fill_latency_ms", float(i))
        stats = m.stats("fill_latency_ms")
        assert stats.count == 100
        assert stats.p95 == pytest.approx(95.0, abs=1.0)

    def test_window_size_evicts_oldest(self):
        m = PerformanceMonitor(window_size=5)
        for i in range(10):
            m.record("x", float(i))
        stats = m.stats("x")
        assert stats.count == 5
        assert stats.min == 5.0
        assert stats.max == 9.0

    def test_stats_unknown_metric_returns_empty(self):
        m = PerformanceMonitor()
        stats = m.stats("nope")
        assert stats.count == 0
        assert stats.mean == 0.0

    def test_metric_names_listed(self):
        m = PerformanceMonitor()
        m.record("a", 1.0)
        m.record("b", 2.0)
        assert m.metrics() == ["a", "b"]


class TestValidation:
    def test_negative_value_rejected(self):
        m = PerformanceMonitor()
        with pytest.raises(InvalidPerformanceInputError):
            m.record("x", -1.0)

    def test_empty_metric_rejected(self):
        m = PerformanceMonitor()
        with pytest.raises(InvalidPerformanceInputError):
            m.record("", 1.0)

    def test_non_finite_value_rejected(self):
        m = PerformanceMonitor()
        with pytest.raises(InvalidPerformanceInputError):
            m.record("x", float("nan"))
        with pytest.raises(InvalidPerformanceInputError):
            m.record("x", float("inf"))

    def test_invalid_window_size_rejected(self):
        with pytest.raises(InvalidPerformanceInputError):
            PerformanceMonitor(window_size=0)

    def test_invalid_threshold_rejected(self):
        m = PerformanceMonitor()
        with pytest.raises(InvalidPerformanceInputError):
            m.set_threshold("x", -5.0)
        with pytest.raises(InvalidPerformanceInputError):
            m.set_threshold("", 5.0)


class TestAlerts:
    def test_threshold_breach_reported(self):
        m = PerformanceMonitor()
        m.set_threshold("order_submit_latency_ms", 100.0)
        m.record("order_submit_latency_ms", 50.0)
        m.record("order_submit_latency_ms", 150.0)
        breaches = m.check_alerts()
        assert len(breaches) == 1
        assert breaches[0]["metric"] == "order_submit_latency_ms"
        assert breaches[0]["value"] == 150.0
        assert breaches[0]["threshold"] == 100.0

    def test_no_breach_when_under_threshold(self):
        m = PerformanceMonitor()
        m.set_threshold("x", 100.0)
        m.record("x", 10.0)
        assert m.check_alerts() == []

    def test_alerter_callback_invoked(self):
        seen: list[dict] = []
        m = PerformanceMonitor(alerter=seen.append)
        m.set_threshold("x", 10.0)
        m.record("x", 20.0)
        m.check_alerts()
        assert len(seen) == 1
        assert seen[0]["metric"] == "x"

    def test_snapshot_contains_stats_and_thresholds(self):
        m = PerformanceMonitor()
        m.set_threshold("x", 10.0)
        m.record("x", 1.0)
        snap = m.snapshot()
        assert "x" in snap["metrics"]
        assert snap["metrics"]["x"]["count"] == 1
        assert snap["thresholds"]["x"] == 10.0

    def test_error_code(self):
        assert InvalidPerformanceInputError.error_code == "ZA-EX-0022"
