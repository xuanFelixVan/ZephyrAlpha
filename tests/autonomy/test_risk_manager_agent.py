# [BLUEPRINT] MOD-AU-007 | docs/03_modules/_domain_autonomy_core/risk_manager_agent/blueprint.md | §test
# [A_test] module_id: MOD-AU-007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RiskManagerAgent 单元测试 (MOD-AU-007, MVP)。

覆盖: 判定阶梯（已熔断 NONE / 硬越限 KILL_SWITCH 主因映射 / 预警带 REDUCE / 正常 NONE）/
act 建议+执行双审计记录 / 触发仅经确定性校验路径（硬越限且未激活）/ 回调与 sink
异常不阻断 / 状态与配置 Fail-Closed 校验 / 复盘说明文本 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.agents.risk_manager_agent import (
    AGENT_CARD,
    ROLE,
    CircuitBreakerAdvice,
    CircuitBreakerLevel,
    InvalidRiskEngineStateError,
    InvalidRiskManagerConfigError,
    RiskEngineState,
    RiskManagerAgent,
    RiskManagerThresholds,
)


def _state(**kw) -> RiskEngineState:
    base = {
        "limits_breached": (),
        "current_drawdown": 0.02,
        "max_drawdown_limit": 0.05,
        "var_95": 0.01,
        "var_limit": 0.03,
        "kill_switch_active": False,
    }
    base.update(kw)
    return RiskEngineState(**base)


# ── 角色卡 ───────────────────────────────────────────────────────────────────


def test_agent_card_shape() -> None:
    assert ROLE == "risk_manager"
    assert AGENT_CARD["role"] == ROLE
    assert AGENT_CARD["autonomyBoundaries"]["immutable"], "硬熔断须 immutable（确定性代码执行）"
    assert AGENT_CARD["autonomyBoundaries"]["human_gated"], "熔断触发须 human_gated"


# ── 判定阶梯 ─────────────────────────────────────────────────────────────────


def test_assess_normal_none() -> None:
    agent = RiskManagerAgent()
    advice = agent.assess(_state())
    assert advice.level is CircuitBreakerLevel.NONE
    assert advice.recommended_kill_switch_level is None


def test_assess_already_active_none() -> None:
    agent = RiskManagerAgent()
    advice = agent.assess(_state(kill_switch_active=True, limits_breached=("pos",)))
    assert advice.level is CircuitBreakerLevel.NONE
    assert "已熔断" in advice.reasons[0]


def test_assess_drawdown_breach_kill_switch_daily_loss() -> None:
    agent = RiskManagerAgent()
    advice = agent.assess(_state(current_drawdown=0.051))
    assert advice.level is CircuitBreakerLevel.KILL_SWITCH
    assert advice.recommended_kill_switch_level == "DAILY_LOSS"


def test_assess_limits_breach_kill_switch_position_limit() -> None:
    agent = RiskManagerAgent()
    advice = agent.assess(_state(limits_breached=("single_weight",)))
    assert advice.level is CircuitBreakerLevel.KILL_SWITCH
    assert advice.recommended_kill_switch_level == "POSITION_LIMIT"


def test_assess_var_breach_kill_switch_circuit_breaker() -> None:
    agent = RiskManagerAgent()
    advice = agent.assess(_state(var_95=0.031))
    assert advice.level is CircuitBreakerLevel.KILL_SWITCH
    assert advice.recommended_kill_switch_level == "CIRCUIT_BREAKER"


def test_assess_warn_band_reduce() -> None:
    agent = RiskManagerAgent(RiskManagerThresholds(warn_ratio=0.8))
    advice = agent.assess(_state(current_drawdown=0.041))  # 0.8*0.05=0.04 以上未破
    assert advice.level is CircuitBreakerLevel.REDUCE
    assert advice.recommended_kill_switch_level is None


def test_assess_var_warn_band_reduce() -> None:
    agent = RiskManagerAgent(RiskManagerThresholds(warn_ratio=0.8))
    advice = agent.assess(_state(var_95=0.025))  # 0.8*0.03=0.024 以上未破
    assert advice.level is CircuitBreakerLevel.REDUCE


# ── act：触发与双审计 ─────────────────────────────────────────────────────────


def test_act_triggers_only_on_hard_breach_and_inactive() -> None:
    triggered: list[tuple[str, dict]] = []
    agent = RiskManagerAgent(kill_switch_trigger=lambda lvl, payload: triggered.append((lvl, payload)))
    action = agent.act(_state(current_drawdown=0.06))
    assert action.advice.level is CircuitBreakerLevel.KILL_SWITCH
    assert action.triggered is True
    assert triggered[0][0] == "DAILY_LOSS"


def test_act_no_trigger_when_already_active() -> None:
    triggered: list = []
    agent = RiskManagerAgent(kill_switch_trigger=lambda lvl, payload: triggered.append(lvl))
    action = agent.act(_state(kill_switch_active=True, current_drawdown=0.06))
    assert action.triggered is False
    assert triggered == []


def test_act_no_trigger_on_reduce() -> None:
    triggered: list = []
    agent = RiskManagerAgent(kill_switch_trigger=lambda lvl, payload: triggered.append(lvl))
    action = agent.act(_state(current_drawdown=0.041))
    assert action.triggered is False
    assert triggered == []


def test_act_writes_advice_and_execution_audit_records() -> None:
    audits: list[dict] = []
    agent = RiskManagerAgent(
        kill_switch_trigger=lambda lvl, payload: None,
        audit_sink=audits.append,
    )
    agent.act(_state(current_drawdown=0.06))
    types = [a["record_type"] for a in audits]
    assert "RISK_MANAGER_ADVICE" in types
    assert "RISK_MANAGER_EXECUTION" in types
    assert len(audits) == 2


def test_act_advice_only_audit_when_no_trigger() -> None:
    audits: list[dict] = []
    agent = RiskManagerAgent(audit_sink=audits.append)
    agent.act(_state())
    assert [a["record_type"] for a in audits] == ["RISK_MANAGER_ADVICE"]


def test_trigger_exception_does_not_break_action() -> None:
    def _boom(lvl, payload) -> None:
        raise RuntimeError("kill switch down")

    agent = RiskManagerAgent(kill_switch_trigger=_boom)
    action = agent.act(_state(current_drawdown=0.06))
    assert action.advice.level is CircuitBreakerLevel.KILL_SWITCH
    assert action.triggered is False  # 触发失败如实标记


def test_audit_sink_exception_does_not_break_action() -> None:
    def _boom(_rec) -> None:
        raise RuntimeError("audit down")

    agent = RiskManagerAgent(audit_sink=_boom)
    action = agent.act(_state(current_drawdown=0.06))
    assert action.advice.level is CircuitBreakerLevel.KILL_SWITCH


def test_action_audit_records_embedded() -> None:
    agent = RiskManagerAgent()
    action = agent.act(_state(current_drawdown=0.06))
    assert action.audit_records[0]["record_type"] == "RISK_MANAGER_ADVICE"


# ── 复盘说明 ─────────────────────────────────────────────────────────────────


def test_review_text_contains_key_facts() -> None:
    agent = RiskManagerAgent()
    state = _state(current_drawdown=0.06)
    advice = agent.assess(state)
    text = agent.review(state, advice)
    assert "回撤" in text
    assert "KILL_SWITCH" in text
    assert "DAILY_LOSS" in text


# ── Fail-Closed 校验 ─────────────────────────────────────────────────────────


@pytest.mark.parametrize("warn_ratio", [0.0, -0.1, 1.0, 1.5])
def test_invalid_warn_ratio_rejected(warn_ratio: float) -> None:
    with pytest.raises(InvalidRiskManagerConfigError):
        RiskManagerThresholds(warn_ratio=warn_ratio)


@pytest.mark.parametrize(
    "kw",
    [
        {"current_drawdown": -0.01},
        {"max_drawdown_limit": 0.0},
        {"max_drawdown_limit": -0.05},
        {"var_95": -0.01},
        {"var_limit": 0.0},
    ],
)
def test_invalid_state_rejected(kw) -> None:
    with pytest.raises(InvalidRiskEngineStateError):
        _state(**kw)


# ── frozen 不可变 ────────────────────────────────────────────────────────────


def test_state_and_advice_frozen() -> None:
    state = _state()
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.current_drawdown = 0.5  # type: ignore[misc]
    advice: CircuitBreakerAdvice = RiskManagerAgent().assess(state)
    with pytest.raises(dataclasses.FrozenInstanceError):
        advice.level = CircuitBreakerLevel.NONE  # type: ignore[misc]
