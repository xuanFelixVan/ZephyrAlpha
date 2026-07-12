# [A_test] module_id: SRC-TST-1913 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-532 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_agent_health_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for agent_health_monitor.py (T-3-11)
=================================================
覆盖：三态健康判定 + 5 项 SLO + 与 agent_orchestrator 集成。

最少测试：10 条。
"""

import pytest

from zephyr.orchestrator.agent_health_monitor import (
    AgentHealthMonitor,
    HealthState,
    SLOConfig,
)
from zephyr.orchestrator.agent_orchestrator import (
    AgentRole,
    OrchestrationResult,
    RouteDecision,
    RoutingStrategy,
)


def _make_result(
    *,
    success: bool = True,
    latency_ms: int = 100,
    is_hallu: bool = False,
    token_used: int = 5000,
    token_budget: int = 8000,
    task_id: str = "T-3-11-TEST",
) -> OrchestrationResult:
    return OrchestrationResult(
        task_id=task_id,
        route=RouteDecision(
            domain="D0",
            strategy=RoutingStrategy.CAPABILITY_MATCH,
            primary_role=AgentRole.GOVERNOR,
            capability_score=0.9,
        ),
        tool_calls=[],
        claim="",
        hallucination={"is_hallucination": True} if is_hallu else None,
        success=success,
        latency_ms=latency_ms,
        token_used=token_used,
        token_budget=token_budget,
        errors=[],
    )


class TestHealthState:
    def test_three_states_exist(self) -> None:
        assert HealthState.HEALTHY.value == "HEALTHY"
        assert HealthState.DEGRADED.value == "DEGRADED"
        assert HealthState.UNHEALTHY.value == "UNHEALTHY"


class TestSLOConfig:
    def test_default_thresholds(self) -> None:
        cfg = SLOConfig()
        assert cfg.latency_p99_ms_hard == 5000.0
        assert cfg.error_rate_hard == 0.05
        assert cfg.throughput_per_min_hard == 10.0
        assert cfg.hallucination_rate_hard == 0.10
        assert cfg.context_utilization_hard == 0.60

    def test_custom_override(self) -> None:
        cfg = SLOConfig(latency_p99_ms_hard=8000.0, error_rate_soft=0.02)
        assert cfg.latency_p99_ms_hard == 8000.0
        assert cfg.error_rate_soft == 0.02


class TestAgentHealthMonitor:
    def test_empty_monitor_is_healthy(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY
        assert status.sample_count == 0

    def test_all_slo_pass_healthy(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        for _ in range(10):
            mon.record(_make_result(success=True, latency_ms=100, token_used=6000, token_budget=8000))
        status = mon.evaluate()
        assert status.state in (HealthState.HEALTHY, HealthState.DEGRADED)
        assert all(v.severity == "soft" for v in status.violations)

    def test_hard_latency_violation_unhealthy(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        mon.record(_make_result(latency_ms=6000))
        status = mon.evaluate()
        assert status.state == HealthState.UNHEALTHY
        assert any(v.metric == "latency_p99_ms" and v.severity == "hard" for v in status.violations)

    def test_soft_latency_violation_degraded(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        mon.record(_make_result(latency_ms=3500))
        status = mon.evaluate()
        assert status.state == HealthState.DEGRADED
        assert any(v.metric == "latency_p99_ms" and v.severity == "soft" for v in status.violations)

    def test_hard_error_rate_unhealthy(self) -> None:
        mon = AgentHealthMonitor(window_size=20)
        for _ in range(18):
            mon.record(_make_result(success=True))
        for _ in range(2):
            mon.record(_make_result(success=False))
        status = mon.evaluate()
        assert status.error_rate == pytest.approx(0.10)
        assert status.state == HealthState.UNHEALTHY

    def test_hallucination_rate_violation(self) -> None:
        mon = AgentHealthMonitor(window_size=20)
        for _ in range(17):
            mon.record(_make_result(is_hallu=False))
        for _ in range(3):
            mon.record(_make_result(is_hallu=True))
        status = mon.evaluate()
        assert status.hallucination_rate == pytest.approx(0.15)
        assert status.state == HealthState.UNHEALTHY

    def test_context_utilization_low_unhealthy(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        for _ in range(10):
            mon.record(_make_result(token_used=100, token_budget=8000))
        status = mon.evaluate()
        assert status.context_utilization < 0.60
        assert status.state == HealthState.UNHEALTHY

    def test_reset_clears_state(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        mon.record(_make_result(success=False, latency_ms=9999))
        mon.reset()
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY
        assert status.sample_count == 0

    def test_window_size_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentHealthMonitor(window_size=0)

    def test_integration_with_orchestrator_result(self) -> None:
        mon = AgentHealthMonitor(window_size=10)
        result = _make_result(
            success=True,
            latency_ms=200,
            token_used=6000,
            token_budget=8000,
        )
        mon.record(result)
        status = mon.evaluate()
        assert status.state == HealthState.HEALTHY
        assert status.latency_p99_ms == 200.0
        assert status.context_utilization == pytest.approx(0.75)
