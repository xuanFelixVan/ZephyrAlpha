# [A_test] module_id: SRC-TST-0286 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_agent_health_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_agent_health_monitor_root.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.agent_health_monitor import (
    AgentHealthMonitor,
    HealthState,
    HealthStatus,
    SLOConfig,
    SLOViolation,
)
from zephyr.orchestrator.agent_orchestrator import (
    AgentRole,
    OrchestrationResult,
    RouteDecision,
    RoutingStrategy,
)


def _make_result(
    success: bool = True,
    latency_ms: int = 100,
    token_used: int = 50,
    token_budget: int = 100,
    hallucination: dict | None = None,
) -> OrchestrationResult:
    return OrchestrationResult(
        task_id="T-TEST-001",
        route=RouteDecision(
            domain="D0",
            strategy=RoutingStrategy.CAPABILITY_MATCH,
            primary_role=AgentRole.ARCHITECT,
            capability_score=0.8,
        ),
        success=success,
        latency_ms=latency_ms,
        token_used=token_used,
        token_budget=token_budget,
        hallucination=hallucination,
    )


class TestAgentHealthMonitorInstantiation:
    def test_default_construction(self):
        mon = AgentHealthMonitor()
        assert mon.sample_count == 0

    def test_custom_window_size(self):
        mon = AgentHealthMonitor(window_size=50)
        assert mon.sample_count == 0

    def test_invalid_window_size_raises(self):
        with pytest.raises(ValueError, match="window_size must be >= 1"):
            AgentHealthMonitor(window_size=0)

    def test_negative_window_size_raises(self):
        with pytest.raises(ValueError, match="window_size must be >= 1"):
            AgentHealthMonitor(window_size=-5)

    def test_custom_slo_config(self):
        slo = SLOConfig(latency_p99_ms_hard=10000.0, error_rate_hard=0.1)
        mon = AgentHealthMonitor(slo_config=slo)
        assert mon._slo.latency_p99_ms_hard == 10000.0
        assert mon._slo.error_rate_hard == 0.1


class TestAgentHealthMonitorRecord:
    def test_record_single_result(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result())
        assert mon.sample_count == 1

    def test_record_multiple_results(self):
        mon = AgentHealthMonitor()
        for _ in range(10):
            mon.record(_make_result())
        assert mon.sample_count == 10

    def test_record_failed_result(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result(success=False))
        status = mon.evaluate()
        assert status.error_rate > 0.0

    def test_record_with_hallucination(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result(hallucination={"is_hallucination": True}))
        status = mon.evaluate()
        assert status.hallucination_rate == 1.0

    def test_record_without_hallucination(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result(hallucination={"is_hallucination": False}))
        status = mon.evaluate()
        assert status.hallucination_rate == 0.0

    def test_record_zero_token_budget(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result(token_budget=0, token_used=50))
        status = mon.evaluate()
        assert status.context_utilization == 0.0


class TestAgentHealthMonitorEvaluate:
    def test_healthy_when_no_violations(self):
        mon = AgentHealthMonitor()
        mon.record(_make_result(latency_ms=100, token_used=80, token_budget=100))
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY
        assert len(status.violations) == 0

    def test_degraded_on_soft_violation(self):
        slo = SLOConfig(
            latency_p99_ms_hard=5000.0,
            latency_p99_ms_soft=100.0,
            error_rate_hard=0.5,
            error_rate_soft=0.01,
        )
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(latency_ms=200, success=True))
        status = mon.evaluate()
        assert status.state == HealthState.DEGRADED
        assert any(v.severity == "soft" for v in status.violations)

    def test_unhealthy_on_hard_violation(self):
        slo = SLOConfig(
            latency_p99_ms_hard=50.0,
            latency_p99_ms_soft=30.0,
        )
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(latency_ms=200))
        status = mon.evaluate()
        assert status.state == HealthState.UNHEALTHY
        assert any(v.severity == "hard" for v in status.violations)

    def test_evaluate_empty_window(self):
        mon = AgentHealthMonitor()
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY
        assert status.sample_count == 0
        assert status.latency_p99_ms == 0.0
        assert status.error_rate == 0.0

    def test_evaluate_error_rate_hard_violation(self):
        slo = SLOConfig(error_rate_hard=0.01, error_rate_soft=0.005)
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(success=False))
        status = mon.evaluate()
        assert status.state == HealthState.UNHEALTHY

    def test_evaluate_hallucination_rate_hard_violation(self):
        slo = SLOConfig(hallucination_rate_hard=0.01, hallucination_rate_soft=0.005)
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(hallucination={"is_hallucination": True}))
        status = mon.evaluate()
        assert status.state == HealthState.UNHEALTHY

    def test_violation_contains_metric_and_threshold(self):
        slo = SLOConfig(latency_p99_ms_hard=50.0)
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(latency_ms=200))
        status = mon.evaluate()
        assert len(status.violations) >= 1
        v = status.violations[0]
        assert v.metric == "latency_p99_ms"
        assert v.threshold == 50.0
        assert v.value > 50.0


class TestAgentHealthMonitorReset:
    def test_reset_clears_all_data(self):
        mon = AgentHealthMonitor()
        for _ in range(5):
            mon.record(_make_result())
        assert mon.sample_count == 5
        mon.reset()
        assert mon.sample_count == 0

    def test_evaluate_after_reset_is_healthy(self):
        slo = SLOConfig(latency_p99_ms_hard=50.0)
        mon = AgentHealthMonitor(slo_config=slo)
        mon.record(_make_result(latency_ms=200))
        mon.reset()
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY


class TestAgentHealthMonitorPercentile:
    def test_percentile_empty(self):
        assert AgentHealthMonitor._percentile([], 99) == 0.0

    def test_percentile_single_value(self):
        assert AgentHealthMonitor._percentile([42.0], 99) == 42.0

    def test_percentile_multiple_values(self):
        values = [float(i) for i in range(1, 101)]
        result = AgentHealthMonitor._percentile(values, 99)
        assert result >= 90.0


class TestSLOConfig:
    def test_default_values(self):
        slo = SLOConfig()
        assert slo.latency_p99_ms_hard == 5000.0
        assert slo.latency_p99_ms_soft == 3000.0
        assert slo.error_rate_hard == 0.05
        assert slo.error_rate_soft == 0.03
        assert slo.throughput_per_min_hard == 10.0
        assert slo.throughput_per_min_soft == 15.0
        assert slo.hallucination_rate_hard == 0.10
        assert slo.hallucination_rate_soft == 0.07
        assert slo.context_utilization_hard == 0.60
        assert slo.context_utilization_soft == 0.70

    def test_custom_values(self):
        slo = SLOConfig(latency_p99_ms_hard=9999.0, error_rate_soft=0.01)
        assert slo.latency_p99_ms_hard == 9999.0
        assert slo.error_rate_soft == 0.01


class TestSLOViolation:
    def test_creation(self):
        v = SLOViolation(metric="latency_p99_ms", value=6000.0, threshold=5000.0, severity="hard")
        assert v.metric == "latency_p99_ms"
        assert v.value == 6000.0
        assert v.threshold == 5000.0
        assert v.severity == "hard"


class TestHealthStatus:
    def test_default_values(self):
        status = HealthStatus(state=HealthState.HEALTHY)
        assert status.state == HealthState.HEALTHY
        assert status.violations == []
        assert status.latency_p99_ms == 0.0
        assert status.error_rate == 0.0
        assert status.sample_count == 0

    def test_with_violations(self):
        v = SLOViolation(metric="error_rate", value=0.1, threshold=0.05, severity="hard")
        status = HealthStatus(state=HealthState.UNHEALTHY, violations=[v], sample_count=5)
        assert len(status.violations) == 1
        assert status.sample_count == 5
