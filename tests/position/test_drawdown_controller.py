# [BLUEPRINT] MOD-POS-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""DrawdownController 单元测试 (MOD-POS-008)。"""

from __future__ import annotations

import pytest

from zephyr.position.core.drawdown_controller import (
    BlackSwanMode,
    BlackSwanSignal,
    DrawdownController,
    DrawdownControllerConfig,
    DrawdownInfo,
    DrawdownResponse,
    InvalidDrawdownControlError,
    SystemicRiskLevel,
    StopLossType,
    StrategyPnl,
    VarCvarMetrics,
)

# 无回撤基线
NO_DD = DrawdownInfo(drawdown_pct=0.0, peak_nav=1.0, current_nav=1.0, recovered_pct=0.0)
# 回撤 8% 未回补
DD_8 = DrawdownInfo(drawdown_pct=-0.08, peak_nav=1.10, current_nav=1.012, recovered_pct=0.0)


# ── 系统性风险 5 级 ────────────────────────────────────────────────────────────


def test_green_level_normal():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.01, cvar_95=0.015))
    assert resp.risk_level == SystemicRiskLevel.GREEN
    assert resp.position_cap == pytest.approx(1.0)
    assert resp.allow_new_position is True
    assert resp.only_close is False


def test_yellow_level_new_position_halved():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.03, cvar_95=0.04))
    assert resp.risk_level == SystemicRiskLevel.YELLOW
    assert resp.position_cap == pytest.approx(0.5)
    assert resp.allow_new_position is True


def test_orange_level_no_new_and_reduce_to_cap_50():
    """橙级: 禁止新开 + 减仓至上限 50%。P1-4 裁定 (2026-08-16): cap 0.7→0.5 恢复单调——
    原 0.7 致 YELLOW(0.5)→ORANGE(0.7) 风险升级上限反而放宽 (非单调倒挂)。
    函数名勘正 (2026-08-18 AI-R3 复审): 原 reduce_30 滞留旧值语义。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.05, cvar_95=0.06))
    assert resp.risk_level == SystemicRiskLevel.ORANGE
    assert resp.position_cap == pytest.approx(0.5)
    assert resp.allow_new_position is False
    assert resp.only_close is False


def test_risk_level_cap_monotone_non_increasing():
    """P1-4 红队实证: 5 级仓位上限按严重度单调非增 (GREEN→BLACK)。"""
    order = (
        SystemicRiskLevel.GREEN,
        SystemicRiskLevel.YELLOW,
        SystemicRiskLevel.ORANGE,
        SystemicRiskLevel.RED,
        SystemicRiskLevel.BLACK,
    )
    caps = [lvl.position_cap for lvl in order]
    assert caps == sorted(caps, reverse=True), f"仓位上限非单调: {caps}"


def test_red_level_reduce_50_only_close():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.07, cvar_95=0.08))
    assert resp.risk_level == SystemicRiskLevel.RED
    assert resp.position_cap == pytest.approx(0.5)
    assert resp.allow_new_position is False
    assert resp.only_close is True


def test_black_level_cvar_clear_all():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.09, cvar_95=0.12))
    assert resp.risk_level == SystemicRiskLevel.BLACK
    assert resp.position_cap == pytest.approx(0.0)
    assert resp.reduce_ratio == pytest.approx(1.0)
    assert resp.only_close is True


def test_cvar_takes_priority_over_var():
    """CVaR>10%(黑)优先于 VaR 级别判定。"""
    ctrl = DrawdownController()
    # VaR=0.03(黄) 但 CVaR=0.12(黑) → 黑
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.03, cvar_95=0.12))
    assert resp.risk_level == SystemicRiskLevel.BLACK


def test_boundary_var_yellow_threshold():
    """VaR 恰好等于阈值不触发(严格大于)。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(var_95=0.02, cvar_95=0.025))
    assert resp.risk_level == SystemicRiskLevel.GREEN


# ── 策略级止损 ──────────────────────────────────────────────────────────────────


def test_soft_stop_triggered():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        strategy_pnls=[StrategyPnl("alpha1", -0.06)],
    )
    assert len(resp.strategy_stops) == 1
    assert resp.strategy_stops[0].stop_type == StopLossType.SOFT
    assert resp.strategy_stops[0].strategy_id == "alpha1"


def test_hard_stop_triggered():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        strategy_pnls=[StrategyPnl("beta1", -0.12)],
    )
    assert resp.strategy_stops[0].stop_type == StopLossType.HARD


def test_no_stop_below_threshold():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        strategy_pnls=[StrategyPnl("gamma1", -0.03)],
    )
    assert resp.strategy_stops[0].stop_type == StopLossType.NONE
    assert resp.strategy_stops[0].triggered is False


def test_multiple_strategies_independent_stops():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        strategy_pnls=[
            StrategyPnl("s1", -0.03),  # NONE
            StrategyPnl("s2", -0.06),  # SOFT
            StrategyPnl("s3", -0.11),  # HARD
        ],
    )
    stops = {s.strategy_id: s.stop_type for s in resp.strategy_stops}
    assert stops == {"s1": StopLossType.NONE, "s2": StopLossType.SOFT, "s3": StopLossType.HARD}


def test_soft_threshold_boundary():
    """回撤恰好等于 soft 阈值不触发(严格大于)。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD, VarCvarMetrics(0.01, 0.015), strategy_pnls=[StrategyPnl("s", -0.05)]
    )
    assert resp.strategy_stops[0].stop_type == StopLossType.NONE


# ── 黑天鹅 7 模式 ──────────────────────────────────────────────────────────────


def test_no_black_swan():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(0.01, 0.015))
    assert resp.black_swan_modes == frozenset()
    assert resp.kill_switch_advised is False


def test_single_black_swan_mode():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
    )
    assert BlackSwanMode.BS003_VOLATILITY in resp.black_swan_modes
    assert resp.position_cap == pytest.approx(0.5)  # 仓位减半
    assert resp.kill_switch_advised is False


def test_bs001_liquidity_cap_5pct():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS001_LIQUIDITY})),
    )
    assert resp.position_cap == pytest.approx(0.05)


def test_bs007_explicit_systemic_kill_switch():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS007_SYSTEMIC})),
    )
    assert resp.kill_switch_advised is True
    assert resp.position_cap == pytest.approx(0.0)


def test_multiple_bs_modes_trigger_systemic():
    """2 个 BS 模式同触发 → BS-007 系统性风险 → Kill Switch 建议。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(
            frozenset({BlackSwanMode.BS001_LIQUIDITY, BlackSwanMode.BS003_VOLATILITY})
        ),
    )
    assert resp.kill_switch_advised is True
    assert resp.position_cap == pytest.approx(0.0)


def test_black_swan_overrides_risk_level():
    """黑天鹅(取严)覆盖系统性风险级别 cap。"""
    ctrl = DrawdownController()
    # VaR=0.01(绿, cap=1.0) 但 BS-003(仓位减半, cap=0.5)
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
    )
    assert resp.position_cap == pytest.approx(0.5)


# ── 回撤回补恢复 ────────────────────────────────────────────────────────────────


def test_no_recovery_below_trigger():
    """回补 < 50% 不触发恢复(系数 1.0, 由风险级别主导)。"""
    ctrl = DrawdownController()
    dd = DrawdownInfo(drawdown_pct=-0.10, peak_nav=1.10, current_nav=1.05, recovered_pct=0.3)
    resp = ctrl.evaluate(dd, VarCvarMetrics(0.01, 0.015))
    assert resp.recovery_factor == pytest.approx(1.0)


def test_recovery_triggered_step_25():
    """回补 50% → 恢复系数 0.5(2 步 × 0.25)。"""
    ctrl = DrawdownController()
    dd = DrawdownInfo(drawdown_pct=-0.10, peak_nav=1.10, current_nav=1.075, recovered_pct=0.50)
    resp = ctrl.evaluate(dd, VarCvarMetrics(0.01, 0.015))
    assert resp.recovery_factor == pytest.approx(0.5)


def test_recovery_full_when_completely_recovered():
    """回补 100% → 恢复系数 1.0。"""
    ctrl = DrawdownController()
    dd = DrawdownInfo(drawdown_pct=-0.10, peak_nav=1.10, current_nav=1.10, recovered_pct=1.0)
    resp = ctrl.evaluate(dd, VarCvarMetrics(0.01, 0.015))
    assert resp.recovery_factor == pytest.approx(1.0)


def test_recovery_caps_position():
    """恢复系数与风险级别 cap 相乘。"""
    ctrl = DrawdownController()
    dd = DrawdownInfo(drawdown_pct=-0.10, peak_nav=1.10, current_nav=1.075, recovered_pct=0.50)
    # VaR=0.03(黄, cap=0.5) × recovery 0.5 = 0.25
    resp = ctrl.evaluate(dd, VarCvarMetrics(0.03, 0.035))
    assert resp.recovery_factor == pytest.approx(0.5)
    assert resp.position_cap == pytest.approx(0.25)


def test_no_drawdown_full_recovery():
    """无回撤 → 恢复系数 1.0。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(NO_DD, VarCvarMetrics(0.01, 0.015))
    assert resp.recovery_factor == pytest.approx(1.0)


# ── 取最严 ──────────────────────────────────────────────────────────────────────


def test_take_strictest_black_swan_vs_risk():
    """黑天鹅 cap <= 风险级别 cap → 取黑天鹅。"""
    ctrl = DrawdownController()
    # VaR=0.05(橙, cap=0.5, P1-4 修正后) vs BS-003(cap=0.5) → 0.5
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.05, 0.055),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
    )
    assert resp.position_cap == pytest.approx(0.5)


def test_kill_switch_zeroes_cap():
    """Kill Switch 建议 → cap=0(覆盖一切)。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),  # 绿
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS007_SYSTEMIC})),
    )
    assert resp.kill_switch_advised is True
    assert resp.position_cap == pytest.approx(0.0)


# ── 不覆盖风控熔断语义 ──────────────────────────────────────────────────────────


def test_does_not_trigger_kill_switch_directly():
    """POS-008 只产出 Kill Switch 建议, 不直接触发(委托 stop_loss)。"""
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.12, 0.15),  # 黑级清仓
    )
    # 黑级清仓但不建议 Kill Switch(KS 只由 BS-007 触发)
    assert resp.risk_level == SystemicRiskLevel.BLACK
    assert resp.kill_switch_advised is False
    assert resp.position_cap == pytest.approx(0.0)


def test_kill_switch_only_from_bs007():
    """Kill Switch 建议只来自 BS-007, 不来自黑级。"""
    ctrl = DrawdownController()
    resp_black = ctrl.evaluate(NO_DD, VarCvarMetrics(0.12, 0.15))
    resp_bs007 = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS007_SYSTEMIC})),
    )
    assert resp_black.kill_switch_advised is False
    assert resp_bs007.kill_switch_advised is True


# ── 输入校验 ────────────────────────────────────────────────────────────────────


def test_positive_drawdown_raises():
    ctrl = DrawdownController()
    with pytest.raises(InvalidDrawdownControlError):
        ctrl.evaluate(
            DrawdownInfo(0.05, 1.0, 1.05), VarCvarMetrics(0.01, 0.015)
        )


def test_drawdown_below_minus_one_raises():
    ctrl = DrawdownController()
    with pytest.raises(InvalidDrawdownControlError):
        ctrl.evaluate(
            DrawdownInfo(-1.5, 1.0, -0.5), VarCvarMetrics(0.01, 0.015)
        )


def test_negative_var_raises():
    ctrl = DrawdownController()
    with pytest.raises(InvalidDrawdownControlError):
        ctrl.evaluate(NO_DD, VarCvarMetrics(-0.01, 0.015))


def test_cvar_less_than_var_raises():
    ctrl = DrawdownController()
    with pytest.raises(InvalidDrawdownControlError):
        ctrl.evaluate(NO_DD, VarCvarMetrics(0.05, 0.03))


def test_non_positive_peak_nav_raises():
    ctrl = DrawdownController()
    with pytest.raises(InvalidDrawdownControlError):
        ctrl.evaluate(
            DrawdownInfo(-0.05, 0.0, 0.0), VarCvarMetrics(0.01, 0.015)
        )


# ── 构造器校验 ──────────────────────────────────────────────────────────────────


def test_soft_must_be_less_than_hard():
    with pytest.raises(InvalidDrawdownControlError):
        DrawdownController(
            DrawdownControllerConfig(soft_stop_threshold=0.10, hard_stop_threshold=0.05)
        )


def test_thresholds_must_be_positive():
    with pytest.raises(InvalidDrawdownControlError):
        DrawdownController(
            DrawdownControllerConfig(soft_stop_threshold=0, hard_stop_threshold=0.10)
        )


def test_var_thresholds_ordered():
    with pytest.raises(InvalidDrawdownControlError):
        DrawdownController(
            DrawdownControllerConfig(var_yellow=0.06, var_orange=0.04, var_red=0.02)
        )


def test_custom_thresholds_used():
    ctrl = DrawdownController(
        DrawdownControllerConfig(soft_stop_threshold=0.03, hard_stop_threshold=0.08)
    )
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        strategy_pnls=[StrategyPnl("s", -0.04)],  # > 0.03 自定义 soft
    )
    assert resp.strategy_stops[0].stop_type == StopLossType.SOFT


# ── 动作列表 ────────────────────────────────────────────────────────────────────


def test_actions_populated():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        DD_8,
        VarCvarMetrics(0.05, 0.055),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
        strategy_pnls=[StrategyPnl("s1", -0.06)],
    )
    assert len(resp.actions) > 0
    assert any("橙级" in a for a in resp.actions)
    assert any("Soft Stop" in a for a in resp.actions)
    assert any("BS003" in a for a in resp.actions)


def test_kill_switch_action_present():
    ctrl = DrawdownController()
    resp = ctrl.evaluate(
        NO_DD,
        VarCvarMetrics(0.01, 0.015),
        black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS007_SYSTEMIC})),
    )
    assert any("Kill Switch" in a for a in resp.actions)
