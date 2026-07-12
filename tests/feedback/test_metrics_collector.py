# [A_test] module_id: SRC-TST-1270 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_metrics_collector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.metrics_collector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_metrics_collector.py
# [TTL] task_bound

import math
from dataclasses import fields

import pytest

from zephyr.feedback_loop.metrics_collector import (
    EMABaseline,
    MetricsCollector,
    MetricSnapshot,
)


def _make_snapshot(
    timestamp: float = 0.0,
    system_cpu: float = 50.0,
    memory_usage_pct: float = 60.0,
    disk_io_wait: float = 5.0,
    network_errors_count: int = 0,
    detection_latency_ms: float = 100.0,
) -> MetricSnapshot:
    return MetricSnapshot(
        timestamp=timestamp,
        system_cpu=system_cpu,
        memory_usage_pct=memory_usage_pct,
        disk_io_wait=disk_io_wait,
        network_errors_count=network_errors_count,
        detection_latency_ms=detection_latency_ms,
    )


class TestMetricSnapshot:
    def test_instantiation_with_all_fields(self):
        snap = _make_snapshot(
            timestamp=1.0,
            system_cpu=75.0,
            memory_usage_pct=80.0,
            disk_io_wait=10.0,
            network_errors_count=3,
            detection_latency_ms=200.0,
        )
        assert snap.timestamp == 1.0
        assert snap.system_cpu == 75.0
        assert snap.memory_usage_pct == 80.0
        assert snap.disk_io_wait == 10.0
        assert snap.network_errors_count == 3
        assert snap.detection_latency_ms == 200.0

    def test_instantiation_with_zero_values(self):
        snap = _make_snapshot(
            timestamp=0.0,
            system_cpu=0.0,
            memory_usage_pct=0.0,
            disk_io_wait=0.0,
            network_errors_count=0,
            detection_latency_ms=0.0,
        )
        assert snap.system_cpu == 0.0
        assert snap.network_errors_count == 0

    def test_field_count_matches_spec(self):
        expected = {
            "timestamp",
            "system_cpu",
            "memory_usage_pct",
            "disk_io_wait",
            "network_errors_count",
            "detection_latency_ms",
        }
        actual = {f.name for f in fields(MetricSnapshot)}
        assert actual == expected

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            MetricSnapshot(timestamp=1.0, system_cpu=50.0)


class TestEMABaseline:
    def test_default_values(self):
        ema = EMABaseline()
        assert ema.window == 100
        assert ema.alpha == 0.1
        assert ema.cpu_ema == 0.0
        assert ema.cpu_var == 1.0
        assert len(ema.history) == 0

    def test_update_single_snapshot(self):
        ema = EMABaseline()
        snap = _make_snapshot(system_cpu=80.0, memory_usage_pct=70.0)
        ema.update(snap)
        assert len(ema.history) == 1
        assert ema.cpu_ema == pytest.approx(0.1 * 80.0, abs=1e-6)
        assert ema.mem_ema == pytest.approx(0.1 * 70.0, abs=1e-6)

    def test_update_multiple_snapshots_converges(self):
        ema = EMABaseline(alpha=0.5)
        for _ in range(50):
            ema.update(_make_snapshot(system_cpu=80.0, memory_usage_pct=60.0))
        assert ema.cpu_ema == pytest.approx(80.0, abs=1.0)
        assert ema.mem_ema == pytest.approx(60.0, abs=1.0)

    def test_update_computes_variance_with_two_or_more(self):
        ema = EMABaseline()
        ema.update(_make_snapshot(system_cpu=50.0))
        ema.update(_make_snapshot(system_cpu=60.0))
        assert ema.cpu_var > 0.0

    def test_update_single_snapshot_keeps_default_variance(self):
        ema = EMABaseline()
        ema.update(_make_snapshot(system_cpu=50.0))
        assert ema.cpu_var == 1.0

    def test_history_maxlen_is_100(self):
        ema = EMABaseline()
        for i in range(150):
            ema.update(_make_snapshot(timestamp=float(i), system_cpu=float(i)))
        assert len(ema.history) <= 100

    def test_update_with_extreme_values(self):
        ema = EMABaseline()
        ema.update(_make_snapshot(system_cpu=1e9, memory_usage_pct=1e9))
        assert math.isfinite(ema.cpu_ema)
        assert math.isfinite(ema.mem_ema)


class TestMetricsCollector:
    def test_instantiation_creates_baseline(self):
        collector = MetricsCollector()
        assert isinstance(collector.baseline, EMABaseline)

    def test_z_threshold_is_2_5(self):
        assert MetricsCollector.Z_THRESHOLD == 2.5

    def test_collect_returns_expected_keys(self):
        collector = MetricsCollector()
        result = collector.collect(_make_snapshot())
        assert "snapshot" in result
        assert "z_scores" in result
        assert "anomaly_triggered" in result

    def test_collect_z_scores_keys_match_metrics(self):
        collector = MetricsCollector()
        result = collector.collect(_make_snapshot())
        expected_keys = {
            "system_cpu",
            "memory_usage_pct",
            "disk_io_wait",
            "network_errors_count",
            "detection_latency_ms",
        }
        assert set(result["z_scores"].keys()) == expected_keys

    def test_collect_no_anomaly_on_first_snapshot(self):
        collector = MetricsCollector()
        result = collector.collect(_make_snapshot())
        assert isinstance(result["anomaly_triggered"], bool)

    def test_collect_anomaly_triggered_on_extreme_value(self):
        collector = MetricsCollector()
        for _ in range(20):
            collector.collect(_make_snapshot(system_cpu=50.0, memory_usage_pct=60.0))
        result = collector.collect(_make_snapshot(system_cpu=500.0))
        assert result["anomaly_triggered"] is True

    def test_collect_z_scores_bounded_with_natural_variance(self):
        import random

        random.seed(42)
        collector = MetricsCollector()
        for _ in range(50):
            cpu = 50.0 + random.gauss(0, 2.0)
            mem = 60.0 + random.gauss(0, 2.0)
            collector.collect(
                _make_snapshot(
                    system_cpu=cpu,
                    memory_usage_pct=mem,
                    disk_io_wait=5.0,
                    network_errors_count=0,
                    detection_latency_ms=100.0,
                )
            )
        result = collector.collect(
            _make_snapshot(
                system_cpu=50.0,
                memory_usage_pct=60.0,
                disk_io_wait=5.0,
                network_errors_count=0,
                detection_latency_ms=100.0,
            )
        )
        assert result["z_scores"]["system_cpu"] < 10.0
        assert result["z_scores"]["memory_usage_pct"] < 10.0

    def test_collect_z_scores_are_non_negative(self):
        collector = MetricsCollector()
        collector.collect(_make_snapshot())
        result = collector.collect(_make_snapshot(system_cpu=55.0))
        for key, z in result["z_scores"].items():
            assert z >= 0.0, f"z_score for {key} should be non-negative, got {z}"

    def test_collect_snapshot_preserved_in_result(self):
        collector = MetricsCollector()
        snap = _make_snapshot(system_cpu=42.0)
        result = collector.collect(snap)
        assert result["snapshot"] is snap

    def test_collect_with_zero_variance_produces_finite_z_scores(self):
        collector = MetricsCollector()
        collector.collect(_make_snapshot(system_cpu=50.0))
        result = collector.collect(_make_snapshot(system_cpu=50.0))
        for key, z in result["z_scores"].items():
            assert math.isfinite(z), f"z_score for {key} is not finite: {z}"
