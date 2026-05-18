# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_anomaly
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: AnomalyDetector"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector import (
    A2AAnomalyDetector,
    MetricKey,
    AnomalyLevel,
)


def test_record_no_anomaly_with_few_samples():
    ad = A2AAnomalyDetector(min_samples_before_detect=5)
    result = ad.record("a1", MetricKey.TASK_RATE, 5.0)
    assert result is None


def test_record_detects_anomaly_after_baseline():
    ad = A2AAnomalyDetector(min_samples_before_detect=3)
    for _ in range(10):
        ad.record("a1", MetricKey.TASK_RATE, 5.0)
    result = ad.record("a1", MetricKey.TASK_RATE, 500.0)
    assert result is not None
    assert result.level in (AnomalyLevel.ELEVATED, AnomalyLevel.HIGH, AnomalyLevel.CRITICAL)


def test_record_normal_value_no_alert():
    ad = A2AAnomalyDetector(min_samples_before_detect=3)
    for _ in range(10):
        ad.record("a1", MetricKey.TASK_RATE, 10.0)
    result = ad.record("a1", MetricKey.TASK_RATE, 10.0)
    assert result is None


def test_record_batch():
    ad = A2AAnomalyDetector(min_samples_before_detect=3)
    for _ in range(10):
        ad.record_batch("a1", {
            MetricKey.TASK_RATE: 10.0,
            MetricKey.ERROR_RATE: 0.01,
        })
    anomalies = ad.record_batch("a1", {
        MetricKey.TASK_RATE: 1000.0,
        MetricKey.ERROR_RATE: 0.01,
    })
    assert len(anomalies) >= 1


def test_get_baseline():
    ad = A2AAnomalyDetector()
    ad.record("a1", MetricKey.TASK_RATE, 5.0)
    bl = ad.get_baseline("a1", MetricKey.TASK_RATE)
    assert bl is not None
    assert bl.mean == 5.0


def test_get_baseline_stats():
    ad = A2AAnomalyDetector()
    ad.record("a1", MetricKey.TASK_RATE, 5.0)
    stats = ad.get_baseline_stats("a1")
    assert "task_rate" in stats


def test_is_anomaly():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector import AnomalyRecord
    assert not A2AAnomalyDetector.is_anomaly([])
    assert A2AAnomalyDetector.is_anomaly([AnomalyRecord(
        agent_id="a", metric=MetricKey.TASK_RATE,
        level=AnomalyLevel.ELEVATED, z_score=2.5,
        current_value=100, baseline_mean=10, baseline_std=5,
        timestamp=0,
    )])
