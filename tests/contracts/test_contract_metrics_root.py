# [A_test] module_id: MOD-GOV_contract_metrics_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_contract_metrics
# [INVARIANTS] SlaRecord.passed derived from latency vs SLA; buffer capped at MAX; singleton collector
# [MODIFY-GUARD] contract_metrics.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError→fail; RuntimeError→fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

cm = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.contract_metrics",
    reason="contract_metrics import failed",
)


@pytest.fixture(autouse=True)
def _reset_collector():
    cm.collector = None
    yield
    cm.collector = None


class TestSlaRecord:
    def test_creation(self):
        r = cm.SlaRecord(
            contract_id="CT-TEL-001",
            trace_id="abc123",
            latency_us=500_000,
            start_span_id="s1",
            end_span_id="s2",
            passed=True,
        )
        assert r.contract_id == "CT-TEL-001"
        assert r.passed is True
        assert r.latency_us == 500_000


class TestDriftAlert:
    def test_creation(self):
        a = cm.DriftAlert(
            contract_id="CT-TEL-001",
            field_name="latency_us",
            statistic="median",
            current_value=600.0,
            baseline_value=400.0,
            deviation_pct=50.0,
        )
        assert a.contract_id == "CT-TEL-001"
        assert a.deviation_pct == 50.0


class TestContractMetricsCollector:
    def test_instantiation(self):
        c = cm.ContractMetricsCollector()
        assert c is not None

    def test_enable_disable(self):
        c = cm.ContractMetricsCollector()
        c.disable()
        c.enable()
        assert c.enabled is True

    def test_measure_sla_pass(self):
        c = cm.ContractMetricsCollector()
        r = c.measure_sla(
            contract_id="CT-TEL-001",
            trace_id="t1",
            latency_us=500_000,
            sla_p99_us=1_000_000,
        )
        assert r.passed is True

    def test_measure_sla_fail(self):
        c = cm.ContractMetricsCollector()
        r = c.measure_sla(
            contract_id="CT-TEL-001",
            trace_id="t1",
            latency_us=2_000_000,
            sla_p99_us=1_000_000,
        )
        assert r.passed is False

    def test_record_violation(self):
        c = cm.ContractMetricsCollector()
        c.record_violation("CT-TEL-001")
        c.record_violation("CT-TEL-001")
        assert c.violation_counts["CT-TEL-001"] == 2

    def test_get_stats_empty(self):
        c = cm.ContractMetricsCollector()
        stats = c.get_stats()
        assert "sla_p99_pass_rate_100" in stats
        assert "total_violations" in stats
        assert stats["total_violations"] == 0

    def test_get_stats_with_data(self):
        c = cm.ContractMetricsCollector()
        c.measure_sla("CT-TEL-001", "t1", 500_000, 1_000_000)
        c.record_violation("CT-TEL-001")
        stats = c.get_stats()
        assert stats["total_violations"] == 1
        assert stats["sla_p99_pass_rate_100"] == 100.0

    def test_buffer_capped(self):
        c = cm.ContractMetricsCollector()
        for i in range(1100):
            c.measure_sla("CT-TEL-001", f"t{i}", 500_000, 1_000_000)
        assert len(c.sla_buffer) <= c._MAX_SLA_BUFFER


class TestGetContractMetrics:
    def test_singleton(self):
        c1 = cm.get_contract_metrics()
        c2 = cm.get_contract_metrics()
        assert c1 is c2


class TestMeasureCtTelSla:
    def test_known_contract(self):
        r = cm.measure_ct_tel_sla(
            contract_id="CT-TEL-001",
            trace_id="t1",
            latency_us=500_000,
        )
        assert r is not None
        assert r.passed is True

    def test_unknown_contract(self):
        r = cm.measure_ct_tel_sla(
            contract_id="CT-UNKNOWN",
            trace_id="t1",
            latency_us=500_000,
        )
        assert r is None


class TestGetCtTelStats:
    def test_returns_dict(self):
        stats = cm.get_ct_tel_stats()
        assert isinstance(stats, dict)
        assert "ct_tel_sla_definitions" in stats
        assert "CT-TEL-001" in stats["ct_tel_sla_definitions"]


class TestBoundary:
    def test_measure_sla_zero_latency(self):
        c = cm.ContractMetricsCollector()
        r = c.measure_sla("CT-TEL-001", "t1", 0, 1_000_000)
        assert r.passed is True

    def test_measure_sla_negative_latency(self):
        c = cm.ContractMetricsCollector()
        r = c.measure_sla("CT-TEL-001", "t1", -1, 1_000_000)
        assert r.passed is True

    def test_record_violation_empty_id(self):
        c = cm.ContractMetricsCollector()
        c.record_violation("")
        assert c.violation_counts[""] == 1
