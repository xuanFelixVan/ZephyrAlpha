# [A_test] module_id: SRC-TST-0162 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-319 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_agent_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Agent 端到端测试 (T-3-12)
=========================
覆盖：AgentRouter 路由（6 角色 × 10 域）、Orchestrator 编排、
Health Monitor 集成、幻觉检测 post-hook、端到端通过率 ≥ 80%。

最少测试：15 条。
"""

from __future__ import annotations

from typing import Any

import pytest

pytestmark = pytest.mark.e2e

from zephyr.orchestrator.agent_health_monitor import AgentHealthMonitor, HealthState
from zephyr.orchestrator.agent_orchestrator import (
    AgentOrchestrator,
    AgentProfile,
    AgentRole,
    AgentRouter,
    OrchestrationResult,
    RouteDecision,
    RoutingStrategy,
)


def _ok_invoker(log: list[tuple[str, dict[str, Any]]]):
    def _invoke(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        log.append((tool_name, arguments))
        return {"ok": True, "tool": tool_name}

    return _invoke


def _failing_invoker(_name: str, _args: dict[str, Any]) -> dict[str, Any]:
    raise RuntimeError("backend down")


def _cove_pass(claim: str, context: Any = None) -> dict[str, Any]:
    return {"is_hallucination": False, "confidence": 0.95, "risk_level": "L"}


def _cove_fail(claim: str, context: Any = None) -> dict[str, Any]:
    return {"is_hallucination": True, "confidence": 0.3, "risk_level": "H"}


MAPPING = {
    "325": [("task_manager.get_task", {"task_id": "T-3-10"})],
    "344": [("knowledge_base.search", {"q": "CoVe"})],
    "999": [("sentinel.run_scan", {})],
}

# ---------------------------------------------------------------------------
# AgentRouter 路由测试（6 角色 × 10 域）
# ---------------------------------------------------------------------------


class TestAgentRouterRouting:
    def test_all_domains_route_to_some_role(self) -> None:
        router = AgentRouter()
        domains = [f"D{i}" for i in range(10)]
        for d in domains:
            decision = router.route(d)
            assert decision.primary_role in set(AgentRole)
            assert decision.capability_score >= 0.0

    def test_governance_domain_routes_to_governor(self) -> None:
        router = AgentRouter()
        decision = router.route("D6")
        assert decision.primary_role == AgentRole.GOVERNOR

    def test_research_domain_routes_to_researcher(self) -> None:
        router = AgentRouter()
        decision = router.route("D3")
        assert decision.primary_role == AgentRole.RESEARCHER

    def test_all_six_roles_covered(self) -> None:
        router = AgentRouter()
        roles_seen = set()
        for d in [f"D{i}" for i in range(10)]:
            decision = router.route(d, strategy=RoutingStrategy.FALLBACK_CHAIN)
            roles_seen.add(decision.primary_role)
            roles_seen.update(decision.fallback_roles)
        assert roles_seen == set(AgentRole)

    def test_load_balance_with_pool(self) -> None:
        router = AgentRouter()
        for i in range(6):
            role = list(AgentRole)[i]
            router.register(
                AgentProfile(
                    agent_id=f"agent-{i}",
                    role=role,
                    current_load=i,
                    max_load=5,
                )
            )
        decision = router.route("D6", strategy=RoutingStrategy.LOAD_BALANCE)
        assert decision.primary_agent_id is not None

    def test_specialist_first_forces_role(self) -> None:
        router = AgentRouter()
        decision = router.route(
            "D9",
            strategy=RoutingStrategy.SPECIALIST_FIRST,
            required_role=AgentRole.ARCHITECT,
        )
        assert decision.primary_role == AgentRole.ARCHITECT


# ---------------------------------------------------------------------------
# Orchestrator 编排测试（directive → MCP tool chain）
# ---------------------------------------------------------------------------


class TestOrchestratorE2E:
    def test_full_directive_chain_success(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker(calls),
            directive_mapping=MAPPING,
        )
        res = orch.orchestrate(domain="D2", directive_chain="325+344+999")
        assert res.success is True
        assert len(res.tool_calls) == 3
        assert [c.tool_name for c in res.tool_calls] == [
            "task_manager.get_task",
            "knowledge_base.search",
            "sentinel.run_scan",
        ]

    def test_partial_chain_failure(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_failing_invoker,
            directive_mapping=MAPPING,
        )
        res = orch.orchestrate(domain="D0", directive_chain="325+344")
        assert res.success is False
        assert res.tool_calls[0].success is False

    def test_empty_directive_chain(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
        )
        res = orch.orchestrate(domain="D0", directive_chain="")
        assert res.tool_calls == []
        assert res.success is True

    def test_unmapped_directive_in_chain(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
        )
        res = orch.orchestrate(domain="D0", directive_chain="325+404")
        assert res.success is False
        assert any("unmapped_directive" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Health Monitor 集成测试
# ---------------------------------------------------------------------------


class TestHealthMonitorIntegration:
    def test_orchestrator_feeds_health_monitor(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
        )
        for _ in range(5):
            orch.orchestrate(domain="D0", directive_chain="999")
        snap = orch.monitor.snapshot()
        assert snap.window_size == 5
        assert snap.healthy is True

    def test_agent_health_monitor_integration(self) -> None:
        ahm = AgentHealthMonitor(window_size=10)
        for _ in range(10):
            result = OrchestrationResult(
                task_id="T-E2E",
                route=RouteDecision(
                    domain="D0",
                    strategy=RoutingStrategy.CAPABILITY_MATCH,
                    primary_role=AgentRole.GOVERNOR,
                    capability_score=0.9,
                ),
                success=True,
                latency_ms=100,
                token_used=6000,
                token_budget=8000,
            )
            ahm.record(result)
        status = ahm.evaluate()
        assert status.state in (HealthState.HEALTHY, HealthState.DEGRADED)

    def test_degraded_state_detected(self) -> None:
        ahm = AgentHealthMonitor(window_size=10)
        for _ in range(5):
            result = OrchestrationResult(
                task_id="T-E2E",
                route=RouteDecision(
                    domain="D0",
                    strategy=RoutingStrategy.CAPABILITY_MATCH,
                    primary_role=AgentRole.GOVERNOR,
                    capability_score=0.9,
                ),
                success=True,
                latency_ms=3500,
                token_used=5000,
                token_budget=8000,
            )
            ahm.record(result)
        status = ahm.evaluate()
        assert status.state == HealthState.DEGRADED


# ---------------------------------------------------------------------------
# 幻觉检测 post-hook 测试
# ---------------------------------------------------------------------------


class TestHallucinationPostHook:
    def test_cove_pass_chain_succeeds(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
            hallucination_caller=_cove_pass,
        )
        res = orch.orchestrate(domain="D6", directive_chain="325", claim="Valid claim")
        assert res.hallucination is not None
        assert res.hallucination["is_hallucination"] is False
        assert res.success is True

    def test_cove_fail_chain_fails(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
            hallucination_caller=_cove_fail,
        )
        res = orch.orchestrate(domain="D6", directive_chain="325", claim="Suspicious claim")
        assert res.hallucination is not None
        assert res.hallucination["is_hallucination"] is True
        assert res.success is False

    def test_no_cove_no_hallucination_field(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
        )
        res = orch.orchestrate(domain="D0", directive_chain="999", claim="test")
        assert res.hallucination is None
        assert res.success is True


# ---------------------------------------------------------------------------
# 端到端通过率测试
# ---------------------------------------------------------------------------


class TestE2EPassRate:
    def test_overall_pass_rate_above_80_percent(self) -> None:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker([]),
            directive_mapping=MAPPING,
            hallucination_caller=_cove_pass,
        )
        total = 20
        passed = 0
        for i in range(total):
            res = orch.orchestrate(
                domain=f"D{i % 10}",
                directive_chain="325",
                claim=f"claim-{i}",
            )
            if res.success:
                passed += 1
        rate = passed / total
        assert rate >= 0.80
