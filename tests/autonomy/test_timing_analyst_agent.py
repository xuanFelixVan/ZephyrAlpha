# [BLUEPRINT] MOD-AU-010 | docs/03_modules/_domain_autonomy_core/timing_analyst_agent/blueprint.md | §test
# [A_test] module_id: MOD-AU-010 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TimingAnalystAgent 单元测试 (MOD-AU-010, MVP)。

覆盖: 角色卡族卡模式（风控前置 human_gated）/ 判定阶梯七分支（volatile
 HOLD/减仓 / 破减仓线 REDUCE+SLICED / T卖联动 REDUCE+LIMIT / 强共振
 OPEN+MARKET / 共振 OPEN+LIMIT / 无共振 ADD+SLICED / 其余 HOLD）/ ctx 与
配置 Fail-Closed / requires_risk_check 恒真 / 非 HOLD 风控前置信号 /
回调异常不阻断 / 双审计记录 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.agents.timing_analyst_agent import (
    AGENT_CARD,
    ROLE,
    ExecutionStyle,
    InvalidTimingAnalystConfigError,
    InvalidTimingContextError,
    TimingAction,
    TimingAnalystAgent,
    TimingAnalystThresholds,
    TimingContext,
)


def _ctx(**kw) -> TimingContext:
    base = {"regime_state": "trending", "forecast_score": 0.1, "t0_signal": None}
    base.update(kw)
    return TimingContext(**base)


def _agent(**kw) -> TimingAnalystAgent:
    return TimingAnalystAgent(**kw)


# ── 角色卡 ───────────────────────────────────────────────────────────────────


class TestAgentCard:
    def test_role(self) -> None:
        assert ROLE == "timing_analyst"
        assert AGENT_CARD["role"] == ROLE

    def test_risk_gate_boundary(self) -> None:
        boundaries = AGENT_CARD["autonomyBoundaries"]
        assert any("风控" in item for item in boundaries["human_gated"])
        assert any("下单" in item for item in boundaries["immutable"])

    def test_agent_exposes_card(self) -> None:
        agent = _agent()
        assert agent.ROLE == ROLE
        assert agent.AGENT_CARD is AGENT_CARD


# ── 输入 Fail-Closed ─────────────────────────────────────────────────────────


class TestInputValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            {"regime_state": "chaos"},
            {"regime_state": ""},
            {"forecast_score": 1.5},
            {"forecast_score": -1.5},
            {"t0_signal": "买入"},
            {"t0_signal": "T"},
        ],
    )
    def test_invalid_context_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidTimingContextError):
            _ctx(**kw)

    @pytest.mark.parametrize(
        "kw",
        [
            {"open_threshold": 0.0},
            {"open_threshold": 1.5},
            {"strong_open_threshold": 0.2},  # strong ≤ open 非法
            {"reduce_threshold": 0.0},
            {"reduce_threshold": -1.5},
        ],
    )
    def test_invalid_config_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidTimingAnalystConfigError):
            TimingAnalystThresholds(**kw)

    def test_frozen(self) -> None:
        ctx = _ctx()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.regime_state = "range"  # type: ignore[misc]


# ── 判定阶梯 ─────────────────────────────────────────────────────────────────


class TestAdvise:
    def test_volatile_hold(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(regime_state="volatile", forecast_score=0.1))
        assert a.action is TimingAction.HOLD
        assert a.requires_risk_check is True

    def test_volatile_reduce(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(regime_state="volatile", forecast_score=-0.5))
        assert a.action is TimingAction.REDUCE
        assert a.execution_style is ExecutionStyle.SLICED

    def test_reduce_on_breach(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=-0.4))
        assert a.action is TimingAction.REDUCE
        assert a.execution_style is ExecutionStyle.SLICED

    def test_t_sell_linkage(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=0.0, t0_signal="T卖"))
        assert a.action is TimingAction.REDUCE
        assert a.execution_style is ExecutionStyle.LIMIT

    def test_strong_open_market(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=0.7, t0_signal="T买"))
        assert a.action is TimingAction.OPEN
        assert a.execution_style is ExecutionStyle.MARKET

    def test_open_limit_on_resonance(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=0.4, t0_signal="T买"))
        assert a.action is TimingAction.OPEN
        assert a.execution_style is ExecutionStyle.LIMIT

    def test_add_sliced_without_resonance(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=0.4))
        assert a.action is TimingAction.ADD
        assert a.execution_style is ExecutionStyle.SLICED

    def test_hold_default(self) -> None:
        agent = _agent()
        a = agent.advise(_ctx(forecast_score=0.1))
        assert a.action is TimingAction.HOLD
        assert a.reasons

    def test_t_sell_ignored_when_strong_forecast(self) -> None:
        agent = _agent()
        # forecast ≥ 开仓线时 T卖 不触发联动减仓（分支3不命中），走强开/共振分支
        a = agent.advise(_ctx(forecast_score=0.4, t0_signal="T卖"))
        assert a.action is TimingAction.ADD


# ── act 编排 ─────────────────────────────────────────────────────────────────


class TestAct:
    def test_non_hold_signals_risk_check(self) -> None:
        calls: list[dict] = []
        agent = _agent(risk_check_trigger=calls.append)
        action = agent.act(_ctx(forecast_score=0.4, t0_signal="T买"))
        assert action.advice.action is TimingAction.OPEN
        assert action.risk_check_signaled is True
        assert len(calls) == 1
        assert calls[0]["action"] == "OPEN"

    def test_hold_no_risk_check_signal(self) -> None:
        calls: list[dict] = []
        agent = _agent(risk_check_trigger=calls.append)
        action = agent.act(_ctx(forecast_score=0.1))
        assert action.advice.action is TimingAction.HOLD
        assert action.risk_check_signaled is False
        assert calls == []

    def test_dual_audit_records(self) -> None:
        agent = _agent()
        action = agent.act(_ctx(forecast_score=-0.4))
        kinds = [r["record_type"] for r in action.audit_records]
        assert "TIMING_ADVICE" in kinds
        assert "TIMING_RISK_CHECK" in kinds

    def test_advice_always_requires_risk_check(self) -> None:
        agent = _agent()
        for kw in ({"forecast_score": 0.1}, {"forecast_score": -0.5}, {"forecast_score": 0.7, "t0_signal": "T买"}):
            assert agent.advise(_ctx(**kw)).requires_risk_check is True

    def test_callback_exception_tolerated(self) -> None:
        def _boom(_payload) -> None:
            raise RuntimeError("down")

        agent = _agent(risk_check_trigger=_boom)
        action = agent.act(_ctx(forecast_score=0.4, t0_signal="T买"))
        assert action.advice.action is TimingAction.OPEN
        assert action.risk_check_signaled is False  # 异常如实记 False
        assert any(r["record_type"] == "TIMING_RISK_CHECK" for r in action.audit_records)
