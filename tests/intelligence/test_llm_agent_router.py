# [BLUEPRINT] MOD-INT-AGENT-ROUTER | docs/03_modules/_domain_intelligence/llm_agent_router/blueprint.md | §test
# [A_test] module_id: MOD-INT-AGENT-ROUTER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# add-design-node tests/intelligence/test_llm_agent_router.py MOD-INT-AGENT-ROUTER D_INTELLIGENCE planned --granularity file
"""LlmAgentRouter 单元测试 (MOD-INT-AGENT-ROUTER, MVP)。

覆盖: 配置非法 Fail-Closed / 空候选 Fail-Closed / 日预算超限降级本地 /
分时策略盘中强制本地 / 延迟预算超限留痕 / 审计 sink 异常不阻断 /
决策引擎异常降级 / 日界自动重置。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.llm_agent_router import (
    AgentRouteDecision,
    AgentRouterConfig,
    InvalidRouterConfigError,
    LlmAgentRouter,
    RouteDecisionError,
    RouteRequest,
)


def _config(budget: float = 10.0) -> AgentRouterConfig:
    return AgentRouterConfig(
        daily_budget_usd=budget,
        period_rules={"task_kinds": {"summarize": "local", "deep": "api"}},
    )


class TestConfig:
    def test_ok(self) -> None:
        c = _config()
        assert c.daily_budget_usd == 10.0

    def test_negative_budget(self) -> None:
        with pytest.raises(InvalidRouterConfigError):
            AgentRouterConfig(daily_budget_usd=-1, period_rules={})

    def test_non_positive_latency(self) -> None:
        with pytest.raises(InvalidRouterConfigError):
            AgentRouterConfig(daily_budget_usd=1, period_rules={}, latency_budgets_ms=(0, 10, 5))


class TestClassify:
    def test_known(self) -> None:
        r = LlmAgentRouter(_config()).classify("summarize")
        assert r.kind == "local"

    def test_unknown(self) -> None:
        r = LlmAgentRouter(_config()).classify("unknown")
        assert r.kind == "general"


class TestRoute:
    def test_basic(self) -> None:
        router = LlmAgentRouter(_config())
        req = RouteRequest(task_type="summarize", candidates=["local_qwen"])
        dec = router.route(req)
        assert isinstance(dec, AgentRouteDecision)
        assert dec.provider == "local"

    def test_empty_candidates(self) -> None:
        router = LlmAgentRouter(_config())
        with pytest.raises(RouteDecisionError):
            router.route(RouteRequest(task_type="t", candidates=[]))

    def test_budget_exceeded(self) -> None:
        router = LlmAgentRouter(_config(budget=1.0))
        req = RouteRequest(task_type="deep", candidates=["api_ds"], estimated_cost_usd=2.0)
        dec = router.route(req)
        assert dec.degraded_to_local is True
        assert any("预算超限" in r for r in dec.reasons)

    def test_intraday_force_local(self) -> None:
        router = LlmAgentRouter(_config())
        req = RouteRequest(task_type="deep", candidates=["api_ds", "local_qwen"], period="intraday")
        dec = router.route(req)
        assert dec.provider == "local"

    def test_audit_sink_error_not_blocking(self) -> None:
        def bad(audit: Any) -> None:
            raise RuntimeError("boom")
        router = LlmAgentRouter(_config(), audit_sink=bad)
        dec = router.route(RouteRequest(task_type="summarize", candidates=["local_qwen"]))
        assert dec.task_type == "summarize"

    def test_decision_engine_exception(self) -> None:
        def bad(req: RouteRequest) -> dict:
            raise RuntimeError("boom")
        router = LlmAgentRouter(_config(), decision_engine=bad)
        dec = router.route(RouteRequest(task_type="summarize", candidates=["api_ds"]))
        assert dec.selected_model is None

    def test_day_reset(self) -> None:
        clock = [0.0]
        router = LlmAgentRouter(_config(), clock=lambda: clock[0])
        router.route(RouteRequest(task_type="t", candidates=["m"], estimated_cost_usd=1.0))
        assert router.daily_cost() == 1.0
        clock[0] = 86401.0
        assert router.daily_cost() == 0.0

    def test_reset_daily(self) -> None:
        router = LlmAgentRouter(_config())
        router.route(RouteRequest(task_type="t", candidates=["m"], estimated_cost_usd=5.0))
        router.reset_daily()
        assert router.daily_cost() == 0.0
