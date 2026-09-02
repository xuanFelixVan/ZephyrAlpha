# [A_test] module_id: MOD-PLAN-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-013 | 待统筹登记 | 缺口总账 GAP-F-03 + 45号 §4 W4
# [MODULE] tests.plan_engine.test_trading_debate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""TradingDebate (MOD-PLAN-013) 施工验证测试。

覆盖：
- 四角色链：牛/熊研究员各 1~3 条论点（越界 fail-closed）→ agent_debate 辩论裁决
  → 交易员综合（可降半档）→ 风控通过/否决。
- 默认规则交易员：辩论不一致（OVERRIDE）→ 降半档 DOWNSIZE ×0.8；一致 AGREE → EXECUTE ×1.0。
- 默认规则风控：D3 fake_ratio>0.6 且进攻方案 → 自动 VETO（45号 W4 硬规则）；
  非进攻方案不触发；fake_ratio 缺失不触发。
- 终局合成：风控 VETO → SIT_OUT + red_flag；否则承交易员 decision/scale。
- 自定义 trader_fn/risk_fn 注入位生效。
- 契约：TradingDebateResult.to_dict JSON 可序列化；DebateContext 非法 fail-closed。
全程内存构造，无 DB 无 LLM 真连。
"""

from __future__ import annotations

import json

import pytest

from zephyr.plan_engine.trading_debate import (
    DECISION_DOWNSIZE,
    DECISION_EXECUTE,
    DECISION_SIT_OUT,
    VERDICT_PASS,
    VERDICT_VETO,
    DebateContext,
    RiskVerdict,
    RoleArgument,
    TraderSynthesis,
    TradingDebateResult,
    run_trading_debate,
)

TRADE_DATE = "2026-08-24"


def _ctx(**over) -> DebateContext:
    base = dict(
        trade_date=TRADE_DATE,
        scenario="FLAT_OPEN_REAL_UP",
        stance="NORMAL",
        is_offensive=True,
        fake_ratio=None,
        channels={"technical": "均线多头", "news": "政策催化", "sentiment": "情绪升温", "fundamental": "业绩稳"},
    )
    base.update(over)
    return DebateContext(**base)


def _bull() -> RoleArgument:
    return RoleArgument(
        role="BULL_RESEARCHER", points=("主线资金持续流入", "龙头三板打开空间", "竞价放量确认"), confidence=0.7
    )


def _bear() -> RoleArgument:
    return RoleArgument(role="BEAR_RESEARCHER", points=("连板高位分歧加大", "外围隔夜走弱"), confidence=0.6)


# ── 输入校验（fail-closed）──


def test_context_trade_date_invalid() -> None:
    with pytest.raises(ValueError):
        _ctx(trade_date="20260824")


def test_context_scenario_empty() -> None:
    with pytest.raises(ValueError):
        _ctx(scenario="  ")


def test_role_argument_empty_points() -> None:
    with pytest.raises(ValueError):
        RoleArgument(role="BULL_RESEARCHER", points=())


def test_role_argument_too_many_points() -> None:
    with pytest.raises(ValueError):
        RoleArgument(role="BULL_RESEARCHER", points=("a", "b", "c", "d"))


def test_role_argument_unknown_role() -> None:
    with pytest.raises(ValueError):
        RoleArgument(role="SPECTATOR", points=("a",))


# ── 默认规则链路 ──


def test_default_chain_agree_executes() -> None:
    # 牛熊论点完全一致 → AGREE → 交易员 EXECUTE ×1.0 → 风控 PASS
    same = RoleArgument(role="BEAR_RESEARCHER", points=_bull().points, confidence=0.6)
    result = run_trading_debate(_ctx(), _bull(), same)
    assert result.debate_verdict == "AGREE"
    assert result.trader.decision == DECISION_EXECUTE
    assert result.trader.scale == pytest.approx(1.0)
    assert result.risk.verdict == VERDICT_PASS
    assert result.final_outcome == DECISION_EXECUTE
    assert result.final_scale == pytest.approx(1.0)
    assert result.red_flag is False


def test_default_chain_disagree_downsizes_half_notch() -> None:
    result = run_trading_debate(_ctx(), _bull(), _bear())
    assert result.debate_verdict == "OVERRIDE"
    assert result.trader.decision == DECISION_DOWNSIZE
    assert result.trader.scale == pytest.approx(0.8)  # 降半档 -20%（44号 §9.6）
    assert result.risk.verdict == VERDICT_PASS
    assert result.final_outcome == DECISION_DOWNSIZE


def test_risk_auto_veto_on_fake_auction_offensive() -> None:
    # D3 fake_ratio>0.6 且进攻方案 → 风控自动否决（45号 W4：虚假申报否决全部进攻方案）
    result = run_trading_debate(_ctx(fake_ratio=0.75, is_offensive=True), _bull(), _bear())
    assert result.risk.verdict == VERDICT_VETO
    assert any("fake_ratio" in r for r in result.risk.reasons)
    assert result.final_outcome == DECISION_SIT_OUT
    assert result.red_flag is True
    assert result.final_scale == pytest.approx(0.0)


def test_risk_no_veto_when_not_offensive() -> None:
    result = run_trading_debate(_ctx(fake_ratio=0.75, is_offensive=False), _bull(), _bear())
    assert result.risk.verdict == VERDICT_PASS


def test_risk_no_veto_at_threshold_boundary() -> None:
    # 阈值边界：fake_ratio=0.6 不触发（>0.6 才作废，44号 §9.11 口径）
    result = run_trading_debate(_ctx(fake_ratio=0.6, is_offensive=True), _bull(), _bear())
    assert result.risk.verdict == VERDICT_PASS


def test_risk_no_veto_when_fake_ratio_missing() -> None:
    result = run_trading_debate(_ctx(fake_ratio=None, is_offensive=True), _bull(), _bear())
    assert result.risk.verdict == VERDICT_PASS


# ── 注入位 ──


def test_custom_trader_fn() -> None:
    def _trader(ctx: DebateContext, bull: RoleArgument, bear: RoleArgument, verdict: str) -> TraderSynthesis:
        return TraderSynthesis(decision=DECISION_SIT_OUT, scale=0.0, rationale="自定义交易员：情绪过热观望")

    result = run_trading_debate(_ctx(), _bull(), _bear(), trader_fn=_trader)
    assert result.trader.decision == DECISION_SIT_OUT
    assert result.final_outcome == DECISION_SIT_OUT
    assert "情绪过热" in result.trader.rationale


def test_custom_risk_fn() -> None:
    def _risk(ctx: DebateContext, trader: TraderSynthesis) -> RiskVerdict:
        return RiskVerdict(verdict=VERDICT_VETO, reasons=["自定义风控：组合敞口超限"])

    result = run_trading_debate(_ctx(), _bull(), _bear(), risk_fn=_risk)
    assert result.risk.verdict == VERDICT_VETO
    assert result.final_outcome == DECISION_SIT_OUT
    assert result.red_flag is True


def test_trader_fn_invalid_return_fail_closed() -> None:
    def _bad(ctx: DebateContext, bull: RoleArgument, bear: RoleArgument, verdict: str) -> TraderSynthesis:
        return TraderSynthesis(decision="Yolo", scale=1.0, rationale="x")

    with pytest.raises(ValueError):
        run_trading_debate(_ctx(), _bull(), _bear(), trader_fn=_bad)


# ── 契约 ──


def test_result_to_dict_json_serializable() -> None:
    result = run_trading_debate(_ctx(), _bull(), _bear())
    payload = result.to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["trade_date"] == TRADE_DATE
    assert payload["scenario"] == "FLAT_OPEN_REAL_UP"
    assert payload["bull"]["role"] == "BULL_RESEARCHER"
    assert payload["bear"]["role"] == "BEAR_RESEARCHER"
    assert payload["debate_verdict"] in {"AGREE", "OVERRIDE", "A_SUPERIOR", "B_SUPERIOR"}


def test_result_is_frozen_dataclass() -> None:
    result = run_trading_debate(_ctx(), _bull(), _bear())
    assert isinstance(result, TradingDebateResult)
    with pytest.raises(AttributeError):
        result.final_outcome = DECISION_EXECUTE  # type: ignore[misc]
