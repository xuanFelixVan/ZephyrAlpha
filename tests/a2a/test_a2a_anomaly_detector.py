# [A_test] module_id: MOD-GOV_a2a_anomaly_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_anomaly_detector
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector",
    reason="a2a_anomaly_detector module not available",
)


class TestA2AAnomalyDetector:
    def test_instantiation(self):
        obj = mod.A2AAnomalyDetector()
        assert obj is not None

    def test_instantiation_custom_params(self):
        obj = mod.A2AAnomalyDetector(baseline_window=50, min_samples_before_detect=3)
        assert obj is not None

    def test_record_and_get_baseline(self):
        obj = mod.A2AAnomalyDetector(min_samples_before_detect=2)
        obj.record("agent1", "latency", 100.0)
        obj.record("agent1", "latency", 200.0)
        obj.record("agent1", "latency", 150.0)
        baseline = obj.get_baseline("agent1", "latency")
        assert baseline is not None

    def test_record_batch(self):
        obj = mod.A2AAnomalyDetector(min_samples_before_detect=2)
        values = {mod.MetricKey.TASK_RATE: 10.0, mod.MetricKey.ERROR_RATE: 20.0}
        obj.record_batch("agent1", values)

    def test_get_baseline_stats(self):
        obj = mod.A2AAnomalyDetector(min_samples_before_detect=2)
        obj.record("agent1", mod.MetricKey.TASK_RATE, 100.0)
        obj.record("agent1", mod.MetricKey.TASK_RATE, 200.0)
        stats = obj.get_baseline_stats("agent1")
        assert isinstance(stats, dict)

    def test_is_anomaly(self):
        obj = mod.A2AAnomalyDetector(min_samples_before_detect=2)
        obj.record("agent1", mod.MetricKey.TASK_RATE, 100.0)
        obj.record("agent1", mod.MetricKey.TASK_RATE, 100.0)
        record = mod.AnomalyRecord(
            agent_id="agent1",
            metric=mod.MetricKey.TASK_RATE,
            level=mod.AnomalyLevel.NORMAL,
            z_score=0.0,
            current_value=100.0,
            baseline_mean=100.0,
            baseline_std=0.0,
            timestamp=0.0,
        )
        result = obj.is_anomaly([record])
        assert isinstance(result, bool)

    def test_anomaly_summary(self):
        obj = mod.A2AAnomalyDetector(min_samples_before_detect=2)
        records = [
            mod.AnomalyRecord(
                agent_id="a1",
                metric=mod.MetricKey.TASK_RATE,
                level=mod.AnomalyLevel.NORMAL,
                z_score=0.0,
                current_value=100.0,
                baseline_mean=100.0,
                baseline_std=0.0,
                timestamp=0.0,
            )
        ]
        summary = obj.anomaly_summary(records)
        assert isinstance(summary, dict)


class TestMetricBaseline:
    def test_update_and_mean(self):
        bl = mod.MetricBaseline()
        bl.update(10.0)
        bl.update(20.0)
        assert bl.mean > 0

    def test_std(self):
        bl = mod.MetricBaseline()
        bl.update(10.0)
        bl.update(20.0)
        assert bl.std >= 0

    def test_z_score(self):
        bl = mod.MetricBaseline()
        bl.update(10.0)
        bl.update(20.0)
        z = bl.z_score(15.0)
        assert isinstance(z, float)
