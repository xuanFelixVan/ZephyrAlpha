# [A_test] module_id: SRC-TST-0289 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_agent_orchestrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_agent_orchestrator_root.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.orchestrator.agent_orchestrator import (
    AgentOrchestrator,
    AgentProfile,
    AgentRole,
    AgentRouter,
    HealthMonitor,
    OrchestrationResult,
    RouteDecision,
    RoutingStrategy,
    SLOSnapshot,
    ToolCallRecord,
)


class TestAgentRole:
    def test_all_roles_exist(self):
        assert AgentRole.ARCHITECT.value == "architect"
        assert AgentRole.IMPLEMENTER.value == "implementer"
        assert AgentRole.REVIEWER.value == "reviewer"
        assert AgentRole.GOVERNOR.value == "governor"
        assert AgentRole.RESEARCHER.value == "researcher"
        assert AgentRole.OPERATOR.value == "operator"

    def test_role_count(self):
        assert len(AgentRole) == 6


class TestRoutingStrategy:
    def test_all_strategies_exist(self):
        assert RoutingStrategy.CAPABILITY_MATCH.value == "capability_match"
        assert RoutingStrategy.LOAD_BALANCE.value == "load_balance"
        assert RoutingStrategy.SPECIALIST_FIRST.value == "specialist_first"
        assert RoutingStrategy.FALLBACK_CHAIN.value == "fallback_chain"

    def test_strategy_count(self):
        assert len(RoutingStrategy) == 4


class TestAgentProfile:
    def test_default_construction(self):
        p = AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT)
        assert p.agent_id == "a1"
        assert p.role == AgentRole.ARCHITECT
        assert p.current_load == 0
        assert p.max_load == 5
        assert p.healthy is True

    def test_utilization_zero_load(self):
        p = AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=0, max_load=5)
        assert p.utilization == 0.0

    def test_utilization_full_load(self):
        p = AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=5, max_load=5)
        assert p.utilization == 1.0

    def test_utilization_partial(self):
        p = AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=2, max_load=5)
        assert p.utilization == pytest.approx(0.4)

    def test_invalid_agent_id_raises(self):
        with pytest.raises(Exception):
            AgentProfile(agent_id="", role=AgentRole.ARCHITECT)


class TestAgentRouterInstantiation:
    def test_default_construction(self):
        router = AgentRouter()
        assert router.pool_size == 0

    def test_with_agent_pool(self):
        pool = [
            AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT),
            AgentProfile(agent_id="a2", role=AgentRole.IMPLEMENTER),
        ]
        router = AgentRouter(agent_pool=pool)
        assert router.pool_size == 2


class TestAgentRouterRegister:
    def test_register_new_agent(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT))
        assert router.pool_size == 1

    def test_register_replaces_existing(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=0))
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=3))
        assert router.pool_size == 1


class TestAgentRouterUpdateLoad:
    def test_update_load_increase(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=1))
        router.update_load("a1", delta=2)
        agents = [a for a in router._pool if a.agent_id == "a1"]
        assert agents[0].current_load == 3

    def test_update_load_decrease(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=3))
        router.update_load("a1", delta=-2)
        agents = [a for a in router._pool if a.agent_id == "a1"]
        assert agents[0].current_load == 1

    def test_update_load_floor_zero(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=0))
        router.update_load("a1", delta=-5)
        agents = [a for a in router._pool if a.agent_id == "a1"]
        assert agents[0].current_load == 0

    def test_update_load_nonexistent_agent(self):
        router = AgentRouter()
        router.update_load("nonexistent", delta=1)
        assert router.pool_size == 0


class TestAgentRouterScore:
    def test_known_role_domain(self):
        router = AgentRouter()
        score = router.score(AgentRole.ARCHITECT, "D2")
        assert score == 1.0

    def test_unknown_domain(self):
        router = AgentRouter()
        score = router.score(AgentRole.ARCHITECT, "DX")
        assert score == 0.0

    def test_zero_capability(self):
        router = AgentRouter()
        score = router.score(AgentRole.OPERATOR, "D2")
        assert score == 0.2


class TestAgentRouterRoute:
    def test_capability_match(self):
        router = AgentRouter()
        decision = router.route("D2", strategy=RoutingStrategy.CAPABILITY_MATCH)
        assert decision.domain == "D2"
        assert decision.strategy == RoutingStrategy.CAPABILITY_MATCH
        assert decision.primary_role == AgentRole.ARCHITECT
        assert decision.capability_score == 1.0

    def test_fallback_chain(self):
        router = AgentRouter()
        decision = router.route("D2", strategy=RoutingStrategy.FALLBACK_CHAIN)
        assert decision.strategy == RoutingStrategy.FALLBACK_CHAIN
        assert len(decision.fallback_roles) == 5

    def test_specialist_first(self):
        router = AgentRouter()
        decision = router.route("D2", strategy=RoutingStrategy.SPECIALIST_FIRST, required_role=AgentRole.REVIEWER)
        assert decision.primary_role == AgentRole.REVIEWER

    def test_specialist_first_requires_role(self):
        router = AgentRouter()
        with pytest.raises(ValueError, match="specialist_first"):
            router.route("D2", strategy=RoutingStrategy.SPECIALIST_FIRST)

    def test_load_balance_with_pool(self):
        router = AgentRouter()
        router.register(AgentProfile(agent_id="a1", role=AgentRole.ARCHITECT, current_load=0, max_load=5))
        decision = router.route("D2", strategy=RoutingStrategy.LOAD_BALANCE)
        assert decision.strategy == RoutingStrategy.LOAD_BALANCE
        assert decision.primary_agent_id == "a1"

    def test_load_balance_no_pool(self):
        router = AgentRouter()
        decision = router.route("D2", strategy=RoutingStrategy.LOAD_BALANCE)
        assert decision.primary_agent_id is None

    def test_unknown_domain_returns_zero_score(self):
        router = AgentRouter()
        decision = router.route("D99", strategy=RoutingStrategy.CAPABILITY_MATCH)
        assert decision.capability_score == 0.0


class TestHealthMonitorInstantiation:
    def test_default_construction(self):
        hm = HealthMonitor()
        assert hm.sample_count == 0

    def test_invalid_window_size(self):
        with pytest.raises(ValueError, match="window_size"):
            HealthMonitor(window_size=0)


class TestHealthMonitorRecordAndSnapshot:
    def test_record_and_snapshot(self):
        hm = HealthMonitor()
        result = OrchestrationResult(
            task_id="T-1",
            route=RouteDecision(
                domain="D0",
                strategy=RoutingStrategy.CAPABILITY_MATCH,
                primary_role=AgentRole.ARCHITECT,
                capability_score=0.8,
            ),
            success=True,
            latency_ms=100,
            token_used=80,
            token_budget=100,
        )
        hm.record(result)
        snap = hm.snapshot()
        assert isinstance(snap, SLOSnapshot)
        assert snap.window_size == 1
        assert snap.error_rate == 0.0

    def test_snapshot_empty(self):
        hm = HealthMonitor()
        snap = hm.snapshot()
        assert snap.latency_p99_ms == 0.0
        assert snap.healthy is True

    def test_reset(self):
        hm = HealthMonitor()
        result = OrchestrationResult(
            task_id="T-1",
            route=RouteDecision(
                domain="D0",
                strategy=RoutingStrategy.CAPABILITY_MATCH,
                primary_role=AgentRole.ARCHITECT,
                capability_score=0.8,
            ),
            success=True,
            latency_ms=100,
        )
        hm.record(result)
        hm.reset()
        assert hm.sample_count == 0


class TestAgentOrchestratorInstantiation:
    def test_default_construction(self):
        router = AgentRouter()
        orch = AgentOrchestrator(router, sanitize_llm_context=False)
        assert orch.router is router
        assert orch.monitor is not None

    def test_with_custom_monitor(self):
        router = AgentRouter()
        monitor = HealthMonitor()
        orch = AgentOrchestrator(router, monitor=monitor, sanitize_llm_context=False)
        assert orch.monitor is monitor


class TestAgentOrchestratorOrchestrate:
    def test_orchestrate_no_invoker_no_mapping(self):
        router = AgentRouter()
        orch = AgentOrchestrator(router, sanitize_llm_context=False)
        result = orch.orchestrate(domain="D2", directive_chain="325+344")
        assert isinstance(result, OrchestrationResult)
        assert result.success is False

    def test_orchestrate_empty_directive_chain(self):
        router = AgentRouter()
        orch = AgentOrchestrator(router, sanitize_llm_context=False)
        result = orch.orchestrate(domain="D2", directive_chain="")
        assert result.success is True
        assert len(result.tool_calls) == 0

    @patch.object(AgentOrchestrator, "_lsg_scan_agent_action", return_value=None)
    def test_orchestrate_with_tool_invoker(self, _mock_lsg):
        router = AgentRouter()
        invoker = lambda tool_name, arguments: {"status": "ok"}
        orch = AgentOrchestrator(
            router,
            tool_invoker=invoker,
            directive_mapping={"325": [("tool_a", {"arg": 1})]},
            sanitize_llm_context=False,
        )
        result = orch.orchestrate(domain="D2", directive_chain="325")
        assert result.success is True
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].success is True

    def test_orchestrate_with_hallucination_caller(self):
        router = AgentRouter()
        cove = lambda claim, context=None: {"is_hallucination": False}
        orch = AgentOrchestrator(
            router,
            hallucination_caller=cove,
            sanitize_llm_context=False,
        )
        result = orch.orchestrate(domain="D2", directive_chain="", claim="test claim")
        assert result.hallucination is not None
        assert result.hallucination["is_hallucination"] is False

    def test_orchestrate_hallucination_makes_result_fail(self):
        router = AgentRouter()
        cove = lambda claim, context=None: {"is_hallucination": True}
        orch = AgentOrchestrator(
            router,
            hallucination_caller=cove,
            sanitize_llm_context=False,
        )
        result = orch.orchestrate(domain="D2", directive_chain="", claim="bad claim")
        assert result.success is False

    def test_orchestrate_custom_task_id(self):
        router = AgentRouter()
        orch = AgentOrchestrator(router, sanitize_llm_context=False)
        result = orch.orchestrate(domain="D2", directive_chain="", task_id="CUSTOM-ID")
        assert result.task_id == "CUSTOM-ID"

    def test_orchestrate_tool_exception_handled(self):
        router = AgentRouter()

        def failing_invoker(tool_name, arguments):
            raise RuntimeError("tool crashed")

        orch = AgentOrchestrator(
            router,
            tool_invoker=failing_invoker,
            directive_mapping={"325": [("tool_a", {})]},
            sanitize_llm_context=False,
        )
        result = orch.orchestrate(domain="D2", directive_chain="325")
        assert result.success is False
        assert len(result.errors) > 0


class TestRouteDecision:
    def test_construction(self):
        rd = RouteDecision(
            domain="D0",
            strategy=RoutingStrategy.CAPABILITY_MATCH,
            primary_role=AgentRole.ARCHITECT,
            capability_score=0.8,
        )
        assert rd.domain == "D0"
        assert rd.primary_agent_id is None
        assert rd.fallback_roles == []


class TestToolCallRecord:
    def test_successful_call(self):
        rec = ToolCallRecord(
            directive="325",
            tool_name="tool_a",
            success=True,
            latency_ms=50,
        )
        assert rec.success is True
        assert rec.error is None

    def test_failed_call(self):
        rec = ToolCallRecord(
            directive="325",
            tool_name="tool_a",
            success=False,
            latency_ms=10,
            error="timeout",
        )
        assert rec.success is False
        assert rec.error == "timeout"
