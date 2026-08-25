# [BLUEPRINT] MOD-AU-011 | docs/03_modules/_domain_autonomy_core/t0_trader_agent/blueprint.md | §test
# [A_test] module_id: MOD-AU-011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""T0TraderAgent 单元测试 (MOD-AU-011, MVP)。

覆盖: 角色卡族卡模式（底仓不变/无下单语义边界）/ 判定阶梯（无信号 SKIP /
次数限额 SKIP / 价差不足 SKIP / 无可卖底仓 REJECT / EXECUTE 截断留痕）/
T+1 可卖硬约束（卖出腿 ≤ sellable）/ ctx 与配置 Fail-Closed /
requires_risk_check 恒真 / EXECUTE 风控前置+执行外发双审计 /
回调异常不阻断 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.agents.t0_trader_agent import (
    AGENT_CARD,
    ROLE,
    InvalidT0ConstraintsError,
    InvalidT0ContextError,
    T0Constraints,
    T0Context,
    T0Decision,
    T0TraderAgent,
)


def _ctx(**kw) -> T0Context:
    base = {
        "symbol": "600519.SH",
        "base_position": 1000,
        "sellable_qty": 1000,
        "t0_signal": "T卖",
        "expected_edge_bp": 60.0,
        "trades_done_today": 0,
        "proposed_qty": 500,
    }
    base.update(kw)
    return T0Context(**base)


def _agent(**kw) -> T0TraderAgent:
    return T0TraderAgent(**kw)


# ── 角色卡 ───────────────────────────────────────────────────────────────────


class TestAgentCard:
    def test_role(self) -> None:
        assert ROLE == "t0_trader"
        assert AGENT_CARD["role"] == ROLE

    def test_hard_boundaries(self) -> None:
        boundaries = AGENT_CARD["autonomyBoundaries"]
        assert any("底仓" in item for item in boundaries["immutable"])
        assert any("下单" in item or "执行" in item for item in boundaries["immutable"])
        assert any("风控" in item for item in boundaries["human_gated"])

    def test_agent_exposes_card(self) -> None:
        agent = _agent()
        assert agent.ROLE == ROLE
        assert agent.AGENT_CARD is AGENT_CARD


# ── 输入 Fail-Closed ─────────────────────────────────────────────────────────


class TestInputValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            {"symbol": ""},
            {"base_position": -1},
            {"sellable_qty": -1},
            {"t0_signal": "买入"},
            {"expected_edge_bp": -1.0},
            {"trades_done_today": -1},
            {"proposed_qty": 0},
            {"proposed_qty": -100},
        ],
    )
    def test_invalid_context_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidT0ContextError):
            _ctx(**kw)

    @pytest.mark.parametrize(
        "kw",
        [
            {"min_edge_bp": 0.0},
            {"min_edge_bp": -5.0},
            {"max_trades_per_day": 0},
            {"max_qty_per_leg": 0},
        ],
    )
    def test_invalid_constraints_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidT0ConstraintsError):
            T0Constraints(**kw)

    def test_frozen(self) -> None:
        ctx = _ctx()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.symbol = "x"  # type: ignore[misc]


# ── 判定阶梯 ─────────────────────────────────────────────────────────────────


class TestDecide:
    def test_skip_no_signal(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(t0_signal=None))
        assert a.decision is T0Decision.SKIP
        assert a.requires_risk_check is True

    def test_skip_trade_limit(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(trades_done_today=3))
        assert a.decision is T0Decision.SKIP
        assert any("次数" in r for r in a.reasons)

    def test_skip_edge_too_small(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(expected_edge_bp=10.0))
        assert a.decision is T0Decision.SKIP
        assert any("价差" in r for r in a.reasons)

    def test_reject_no_sellable(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(t0_signal="T卖", sellable_qty=0))
        assert a.decision is T0Decision.REJECT
        assert any("T+1" in r or "可卖" in r for r in a.reasons)

    def test_execute_sell_full(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(t0_signal="T卖", proposed_qty=500))
        assert a.decision is T0Decision.EXECUTE
        assert a.direction == "T卖"
        assert a.suggested_qty == 500

    def test_execute_sell_capped_by_sellable(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx(t0_signal="T卖", sellable_qty=300, proposed_qty=500))
        assert a.decision is T0Decision.EXECUTE
        assert a.suggested_qty == 300
        assert any("截断" in r for r in a.reasons)

    def test_execute_capped_by_leg_limit(self) -> None:
        agent = _agent(constraints=T0Constraints(max_qty_per_leg=200))
        a = agent.decide(_ctx(t0_signal="T买", proposed_qty=500))
        assert a.decision is T0Decision.EXECUTE
        assert a.suggested_qty == 200

    def test_execute_buy_ignores_sellable(self) -> None:
        agent = _agent()
        # 正T 先买腿不吃可卖约束（卖出腿才吃 T+1）
        a = agent.decide(_ctx(t0_signal="T买", sellable_qty=0, proposed_qty=100))
        assert a.decision is T0Decision.EXECUTE
        assert a.suggested_qty == 100

    def test_base_position_invariant_in_reasons(self) -> None:
        agent = _agent()
        a = agent.decide(_ctx())
        assert a.decision is T0Decision.EXECUTE
        assert any("底仓" in r for r in a.reasons)


# ── act 编排 ─────────────────────────────────────────────────────────────────


class TestAct:
    def test_execute_signals_and_hands_off(self) -> None:
        risk_calls: list[dict] = []
        exec_calls: list[dict] = []
        agent = _agent(risk_check_trigger=risk_calls.append, execution_sink=exec_calls.append)
        action = agent.act(_ctx())
        assert action.advice.decision is T0Decision.EXECUTE
        assert action.risk_check_signaled is True
        assert action.execution_handed_off is True
        assert len(risk_calls) == 1
        assert len(exec_calls) == 1
        assert exec_calls[0]["symbol"] == "600519.SH"
        kinds = [r["record_type"] for r in action.audit_records]
        assert "T0_DECISION" in kinds
        assert "T0_EXECUTION" in kinds

    def test_skip_no_execution(self) -> None:
        risk_calls: list[dict] = []
        exec_calls: list[dict] = []
        agent = _agent(risk_check_trigger=risk_calls.append, execution_sink=exec_calls.append)
        action = agent.act(_ctx(t0_signal=None))
        assert action.advice.decision is T0Decision.SKIP
        assert action.execution_handed_off is False
        assert risk_calls == []
        assert exec_calls == []

    def test_reject_no_execution(self) -> None:
        exec_calls: list[dict] = []
        agent = _agent(execution_sink=exec_calls.append)
        action = agent.act(_ctx(t0_signal="T卖", sellable_qty=0))
        assert action.advice.decision is T0Decision.REJECT
        assert action.execution_handed_off is False
        assert exec_calls == []

    def test_callback_exceptions_tolerated(self) -> None:
        def _boom(_payload) -> None:
            raise RuntimeError("down")

        agent = _agent(risk_check_trigger=_boom, execution_sink=_boom)
        action = agent.act(_ctx())
        assert action.advice.decision is T0Decision.EXECUTE
        assert action.risk_check_signaled is False
        assert action.execution_handed_off is False
        assert any(r["record_type"] == "T0_EXECUTION" for r in action.audit_records)

    def test_advice_always_requires_risk_check(self) -> None:
        agent = _agent()
        for kw in ({"t0_signal": None}, {"trades_done_today": 3}, {}):
            assert agent.decide(_ctx(**kw)).requires_risk_check is True
