# [A_test] module_id: SRC-TST-1963 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-580 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.telemetry.test_l12_telemetry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
L12 — System Telemetry Phase D 覆盖
=====================================

验证 ContractMetricsCollector 全功能：
SLA 测量 / 漂移检测 / 违规记录 / 统计聚合。

Phase D | Safety: LOW（框架验证，无外部 IO）
"""

from zephyr.infrastructure.system_telemetry.contract_metrics import (
    ContractMetricsCollector,
    DriftAlert,
    SlaRecord,
    get_contract_metrics,
)


class TestSlaRecord:
    def test_sla_record_passed(self):
        r = SlaRecord(
            contract_id="CTR-001",
            trace_id="trace-abc",
            latency_us=500,
            start_span_id="s1",
            end_span_id="s2",
            passed=True,
        )
        assert r.passed is True
        assert r.latency_us == 500
        assert r.contract_id == "CTR-001"

    def test_sla_record_failed(self):
        r = SlaRecord(
            contract_id="CTR-001",
            trace_id="trace-abc",
            latency_us=99999,
            start_span_id="s1",
            end_span_id="s2",
            passed=False,
        )
        assert r.passed is False


class TestDriftAlert:
    def test_drift_alert_creation(self):
        alert = DriftAlert(
            contract_id="CTR-003",
            field_name="signal_value",
            statistic="z_score",
            current_value=10.5,
            baseline_value=5.0,
            deviation_pct=50.0,
        )
        assert alert.contract_id == "CTR-003"
        assert alert.field_name == "signal_value"
        assert alert.deviation_pct == 50.0


class TestContractMetricsCollector:
    def test_measure_sla_passed(self):
        c = ContractMetricsCollector()
        r = c.measure_sla("CTR-001", "trace-1", latency_us=100, sla_p99_us=200)
        assert r.passed is True
        assert r.latency_us == 100

    def test_measure_sla_violated(self):
        c = ContractMetricsCollector()
        r = c.measure_sla("CTR-001", "trace-2", latency_us=500, sla_p99_us=200)
        assert r.passed is False

    def test_measure_sla_exact_boundary(self):
        c = ContractMetricsCollector()
        r = c.measure_sla("CTR-001", "trace-3", latency_us=200, sla_p99_us=200)
        assert r.passed is True  # <= 200

    def test_measure_sla_returns_record_always(self):
        c = ContractMetricsCollector()
        r = c.measure_sla("CTR-001", "trace-4", latency_us=100, sla_p99_us=200)
        assert isinstance(r, SlaRecord)
        assert r.trace_id == "trace-4"

    def test_detect_drift_no_baseline(self):
        c = ContractMetricsCollector()
        alert = c.detect_contract_drift("CTR-003", "signal_value", 10.0)
        assert alert is None

    def test_detect_drift_below_threshold(self):
        c = ContractMetricsCollector()
        alert = c.detect_contract_drift(
            "CTR-003",
            "signal_value",
            5.5,
            baseline_median=5.0,
            baseline_std=1.0,
        )
        assert alert is None  # z = 0.5 < 5.0

    def test_detect_drift_above_threshold(self):
        c = ContractMetricsCollector()
        alert = c.detect_contract_drift(
            "CTR-003",
            "signal_value",
            50.0,
            baseline_median=5.0,
            baseline_std=1.0,
        )
        assert alert is not None
        assert alert.contract_id == "CTR-003"
        assert alert.field_name == "signal_value"

    def test_record_violation_single(self):
        c = ContractMetricsCollector()
        c.record_violation("CTR-001")
        stats = c.get_stats()
        assert stats["total_violations"] == 1

    def test_record_violation_multiple(self):
        c = ContractMetricsCollector()
        for _ in range(5):
            c.record_violation("CTR-001")
        stats = c.get_stats()
        assert stats["total_violations"] == 5

    def test_get_stats_initial_clean(self):
        c = ContractMetricsCollector()
        stats = c.get_stats()
        assert stats["sla_p99_pass_rate_100"] == 0.0
        assert stats["total_violations"] == 0
        assert stats["active_drift_alerts"] == 0

    def test_enable_and_measure_with_buffer(self):
        c = ContractMetricsCollector()
        c.enable()
        for i in range(110):
            c.measure_sla("CTR-001", f"trace-{i}", latency_us=100, sla_p99_us=200)
        stats = c.get_stats()
        assert stats["sla_p99_pass_rate_100"] == 100.0

    def test_enable_and_measure_mixed(self):
        c = ContractMetricsCollector()
        c.enable()
        for i in range(100):
            latency = 100 if i < 80 else 999
            c.measure_sla("CTR-MIX", f"trace-{i}", latency_us=latency, sla_p99_us=200)
        stats = c.get_stats()
        assert stats["sla_p99_pass_rate_100"] < 100.0


class TestGlobalCollector:
    def test_get_contract_metrics_singleton(self):
        cm1 = get_contract_metrics()
        cm2 = get_contract_metrics()
        assert cm1 is cm2

    def test_get_contract_metrics_initial_clean(self):
        cm = get_contract_metrics()
        stats = cm.get_stats()
        assert stats["total_violations"] >= 0


class TestL12TelemetryStreamsPhase1:
    """metrics/logs/traces/ai_behavior/archive Phase 1 最小导出冒烟。"""

    def test_emit_ai_behavior_event_no_throw(self):
        from zephyr.infrastructure.system_telemetry.ai_behavior import emit_ai_behavior_event

        emit_ai_behavior_event("hallucination_probe", {"rate": 0.01})

    def test_structured_log_record_stub(self):
        from zephyr.infrastructure.system_telemetry.logs import log_record_stub

        rec = log_record_stub("INFO", "hello", layer="l12")
        assert rec["level"] == "INFO"
        assert rec["labels"]["layer"] == "l12"

    def test_noop_span_context_manager(self):
        from zephyr.infrastructure.system_telemetry.traces import noop_span

        with noop_span("op"):
            pass

    def test_archive_batch_id_format(self):
        from zephyr.infrastructure.system_telemetry.archive import next_archive_batch_id

        bid = next_archive_batch_id("tst")
        assert bid.startswith("tst-")
        assert len(bid) > 8
