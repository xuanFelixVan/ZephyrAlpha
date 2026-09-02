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

from typing import Any

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


class TestTaskGateDispatch:
    """task_gate dispatch 硬门（06号文 §2.1 可选钩子，默认 None 零行为变化）。

    钩子契约 (model_id, capability) -> (bool, reason)；deny 按既有降级语义：
    回退过门候选，全部不过门则 selected=None 阻断标记（对齐 decision_engine
    缺省/异常的 model=None 兜底语义），拦截原因一律入 reasons 留痕。
    """

    def _router(self, gate, model: str | None = "m1") -> LlmAgentRouter:
        return LlmAgentRouter(
            _config(),
            decision_engine=lambda req: {"model": model, "provider": "ollama"},
            task_gate=gate,
        )

    def test_default_no_gate_zero_change(self) -> None:
        router = LlmAgentRouter(_config(), decision_engine=lambda req: {"model": "m1", "provider": "ollama"})
        dec = router.route(RouteRequest(task_type="code_fix", candidates=["m1"], period="post_close"))
        assert dec.selected_model == "m1"
        assert not any("task_gate" in r for r in dec.reasons)

    def test_gate_allow_passes_selected_and_task_type(self) -> None:
        calls: list = []

        def gate(model_id: str, capability: str) -> tuple:
            calls.append((model_id, capability))
            return (True, "ok")

        dec = self._router(gate).route(RouteRequest(task_type="code_fix", candidates=["m1"], period="post_close"))
        assert dec.selected_model == "m1"
        assert calls == [("m1", "code_fix")]

    def test_gate_deny_falls_back_to_allowed_candidate(self) -> None:
        def gate(model_id: str, capability: str) -> tuple:
            return (False, "low_accuracy: x") if model_id == "m1" else (True, "ok")

        dec = self._router(gate).route(RouteRequest(task_type="code_fix", candidates=["m1", "m2"], period="post_close"))
        assert dec.selected_model == "m2"  # 回退过门候选
        assert any("task_gate 拦截(m1)" in r for r in dec.reasons)

    def test_gate_deny_all_returns_blocked_marker(self) -> None:
        router = self._router(lambda m, c: (False, "no_passport"))
        dec = router.route(RouteRequest(task_type="code_fix", candidates=["m1", "m2"], period="post_close"))
        assert dec.selected_model is None  # 阻断标记：无过门候选
        assert any("task_gate 阻断" in r for r in dec.reasons)

    def test_gate_exception_fail_closed(self) -> None:
        def bad(model_id: str, capability: str) -> tuple:
            raise RuntimeError("gate down")

        dec = self._router(bad).route(RouteRequest(task_type="code_fix", candidates=["m1"], period="post_close"))
        assert dec.selected_model is None  # 钩子异常 fail-closed 按拦截处理，不抛出
        assert any("task_gate 异常" in r for r in dec.reasons)

    def test_gate_not_called_when_no_model_selected(self) -> None:
        calls: list = []

        def gate(model_id: str, capability: str) -> tuple:
            calls.append((model_id, capability))
            return (True, "ok")

        dec = self._router(gate, model=None).route(
            RouteRequest(task_type="code_fix", candidates=["m1"], period="post_close")
        )
        assert dec.selected_model is None  # 静态兜底无模型 -> 门控不适用
        assert calls == []
