# [A_test] module_id: SRC-TST-1014 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fle_dogfood_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.health.fle_dogfood_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fle_dogfood_monitor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.health.fle_dogfood_monitor import (
    FLEDogfoodMonitor,
    FLESelfHealth,
)


class TestFLESelfHealthEnum:
    def test_healthy_value(self):
        assert FLESelfHealth.HEALTHY.value == "HEALTHY"

    def test_degraded_value(self):
        assert FLESelfHealth.DEGRADED.value == "DEGRADED"

    def test_sick_value(self):
        assert FLESelfHealth.SICK.value == "SICK"

    def test_critical_value(self):
        assert FLESelfHealth.CRITICAL.value == "CRITICAL"

    def test_all_states_count(self):
        assert len(FLESelfHealth) == 4


class TestFLEDogfoodMonitorInstantiation:
    def test_default_params(self):
        mon = FLEDogfoodMonitor()
        assert mon.max_consecutive_missed_cycles == 3
        assert mon.max_self_diagnosis_latency_ms == 10000.0
        assert mon.max_metric_gap_seconds == 120.0
        assert mon.self_metrics == {}
        assert mon.missed_cycles == 0
        assert mon.self_health == FLESelfHealth.HEALTHY
        assert mon.dogfood_events == []

    def test_custom_params(self):
        mon = FLEDogfoodMonitor(max_consecutive_missed_cycles=5, max_metric_gap_seconds=300.0)
        assert mon.max_consecutive_missed_cycles == 5
        assert mon.max_metric_gap_seconds == 300.0


class TestRecordSelfMetric:
    def test_record_new_metric(self):
        mon = FLEDogfoodMonitor()
        mon.record_self_metric("detection_latency_ms", 150.0)
        assert "detection_latency_ms" in mon.self_metrics
        assert mon.self_metrics["detection_latency_ms"] == [150.0]

    def test_record_appends_to_existing(self):
        mon = FLEDogfoodMonitor()
        mon.record_self_metric("latency", 100.0)
        mon.record_self_metric("latency", 200.0)
        assert mon.self_metrics["latency"] == [100.0, 200.0]

    def test_capped_at_100_entries(self):
        mon = FLEDogfoodMonitor()
        for i in range(150):
            mon.record_self_metric("latency", float(i))
        assert len(mon.self_metrics["latency"]) == 100

    def test_multiple_metrics_independent(self):
        mon = FLEDogfoodMonitor()
        mon.record_self_metric("latency", 100.0)
        mon.record_self_metric("errors", 1.0)
        assert len(mon.self_metrics) == 2


class TestSelfCheck:
    def test_first_check_returns_healthy(self):
        mon = FLEDogfoodMonitor()
        result = mon.self_check()
        assert result["self_health"] == FLESelfHealth.HEALTHY.value
        assert result["issues"] == []

    def test_result_has_required_keys(self):
        mon = FLEDogfoodMonitor()
        result = mon.self_check()
        assert "self_health" in result
        assert "issues" in result
        assert "missed_cycles" in result
        assert "recommendation" in result

    def test_healthy_recommendation_is_continue(self):
        mon = FLEDogfoodMonitor()
        result = mon.self_check()
        assert result["recommendation"] == "continue"

    def test_unhealthy_records_dogfood_event(self):
        mon = FLEDogfoodMonitor(max_consecutive_missed_cycles=0)
        mon.missed_cycles = 5
        result = mon.self_check()
        if result["self_health"] != FLESelfHealth.HEALTHY.value:
            assert len(mon.dogfood_events) >= 1


class TestGetSelfMetricSummary:
    def test_empty_metrics(self):
        mon = FLEDogfoodMonitor()
        summary = mon.get_self_metric_summary()
        assert summary == {}

    def test_single_metric_summary(self):
        mon = FLEDogfoodMonitor()
        mon.record_self_metric("latency", 100.0)
        mon.record_self_metric("latency", 200.0)
        summary = mon.get_self_metric_summary()
        assert "latency" in summary
        assert summary["latency"]["latest"] == 200.0
        assert summary["latency"]["mean"] == 150.0
        assert summary["latency"]["count"] == 2

    def test_summary_keys(self):
        mon = FLEDogfoodMonitor()
        mon.record_self_metric("latency", 100.0)
        summary = mon.get_self_metric_summary()
        assert "latest" in summary["latency"]
        assert "mean" in summary["latency"]
        assert "count" in summary["latency"]


class TestGetSelfSLOCompliance:
    def test_healthy_compliance(self):
        mon = FLEDogfoodMonitor()
        result = mon.get_self_slo_compliance()
        assert result["healthy"] is True
        assert result["last_health"] == FLESelfHealth.HEALTHY.value

    def test_result_has_required_keys(self):
        mon = FLEDogfoodMonitor()
        result = mon.get_self_slo_compliance()
        assert "uptime_percent" in result
        assert "degradation_events" in result
        assert "last_health" in result
        assert "healthy" in result

    def test_uptime_percent_range(self):
        mon = FLEDogfoodMonitor()
        result = mon.get_self_slo_compliance()
        assert 0.0 <= result["uptime_percent"] <= 100.0
