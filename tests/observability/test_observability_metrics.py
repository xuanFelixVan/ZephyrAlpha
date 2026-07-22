# [A_test] module_id: MOD-GOV_observability_metrics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_observability_metrics

# [INVARIANTS] Counter只增;Gauge可设任意值;Histogram观察值追加;prometheus_text格式合规

# [MODIFY-GUARD] metrics.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_observability_metrics.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.observability.metrics import (
    MetricsRegistry,
    MetricType,
    get_registry,
)


@pytest.fixture(autouse=True)
def _fresh_registry():
    reg = get_registry()
    reg.reset()
    yield
    reg.reset()


class TestMetricType:
    def test_members(self):
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"


class TestMetricsRegistryCounter:
    def test_inc_new_counter(self):
        reg = MetricsRegistry()
        reg.inc("requests_total")
        snap = reg.snapshot()
        assert any(s.name == "requests_total" and s.value == 1.0 for s in snap)

    def test_inc_increments(self):
        reg = MetricsRegistry()
        reg.inc("req")
        reg.inc("req")
        snap = reg.snapshot()
        assert any(s.name == "req" and s.value == 2.0 for s in snap)

    def test_inc_with_labels(self):
        reg = MetricsRegistry()
        reg.inc("req", {"method": "GET"})
        reg.inc("req", {"method": "POST"})
        snap = reg.snapshot()
        get_snap = [s for s in snap if s.name == "req" and s.labels.get("method") == "GET"]
        post_snap = [s for s in snap if s.name == "req" and s.labels.get("method") == "POST"]
        assert len(get_snap) == 1
        assert len(post_snap) == 1


class TestMetricsRegistryGauge:
    def test_set_gauge(self):
        reg = MetricsRegistry()
        reg.set_gauge("temperature", 23.5)
        snap = reg.snapshot()
        assert any(s.name == "temperature" and s.value == 23.5 for s in snap)

    def test_overwrite_gauge(self):
        reg = MetricsRegistry()
        reg.set_gauge("temp", 20.0)
        reg.set_gauge("temp", 25.0)
        snap = reg.snapshot()
        assert any(s.name == "temp" and s.value == 25.0 for s in snap)


class TestMetricsRegistryHistogram:
    def test_observe(self):
        reg = MetricsRegistry()
        reg.observe("latency", 0.5)
        reg.observe("latency", 1.5)
        snap = reg.snapshot()
        count_snap = [s for s in snap if s.name == "latency_count"]
        sum_snap = [s for s in snap if s.name == "latency_sum"]
        assert len(count_snap) == 1
        assert count_snap[0].value == 2.0
        assert len(sum_snap) == 1
        assert abs(sum_snap[0].value - 2.0) < 0.01

    def test_observe_with_labels(self):
        reg = MetricsRegistry()
        reg.observe("latency", 0.1, {"endpoint": "/api"})
        snap = reg.snapshot()
        labeled = [s for s in snap if s.labels.get("endpoint") == "/api"]
        assert len(labeled) >= 1


class TestMetricsRegistryPrometheusText:
    def test_counter_output(self):
        reg = MetricsRegistry()
        reg.inc("test_counter")
        text = reg.prometheus_text()
        assert "test_counter" in text
        assert "1" in text

    def test_gauge_output(self):
        reg = MetricsRegistry()
        reg.set_gauge("test_gauge", 42.0)
        text = reg.prometheus_text()
        assert "test_gauge" in text
        assert "42" in text

    def test_histogram_output(self):
        reg = MetricsRegistry()
        reg.observe("test_hist", 0.5)
        text = reg.prometheus_text()
        assert "test_hist_count" in text
        assert "test_hist_sum" in text
        assert "test_hist_bucket" in text


class TestMetricsRegistryMeasure:
    def test_timing_context(self):
        reg = MetricsRegistry()
        with reg.measure("duration"):
            pass
        snap = reg.snapshot()
        count_snap = [s for s in snap if s.name == "duration_count"]
        assert len(count_snap) == 1
        assert count_snap[0].value == 1.0


class TestMetricsRegistryReset:
    def test_reset_clears_all(self):
        reg = MetricsRegistry()
        reg.inc("counter")
        reg.set_gauge("gauge", 1.0)
        reg.observe("hist", 0.5)
        reg.reset()
        assert reg.snapshot() == []


class TestGetRegistry:
    def test_returns_same_instance(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2
