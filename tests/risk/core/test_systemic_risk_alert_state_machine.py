# [BLUEPRINT] MOD-RK-34 | docs/03_modules/_domain_risk/systemic_risk_alert_state_machine/blueprint.md | §test
# [MODULE] tests.risk.core.test_systemic_risk_alert_state_machine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.systemic_risk_alert_state_machine
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_systemic_risk_alert_state_machine.py
# [A_test] module_id: MOD-RK-34 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-34 单元测试: SystemicRiskAlertStateMachine — 系统性风险分级预警 5 级状态机。

覆盖: 五级阈值边界（绿/黄/橙/红/黑）、取最严级、指令映射（scale/reduce/close_only/
清仓/熔断标记）、连续 2 日亏判定、触发理由全量不短路、迁移历史只追加、非法输入
与畸形阈值 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.risk.core.systemic_risk_alert_state_machine import (
    InvalidSystemicAlertInputError,
    RiskDirective,
    RiskLevel,
    SystemicRiskAlertConfig,
    SystemicRiskAlertStateMachine,
    SystemicRiskAssessment,
)


def _assess(
    machine: SystemicRiskAlertStateMachine,
    *,
    var95_pct: float = 0.01,
    cvar_pct: float = 0.015,
    daily_pnl_pct: float = 0.0,
    prev_day_pnl_pct: float = 0.0,
    liquidity_crisis: bool = False,
) -> SystemicRiskAssessment:
    return machine.assess(
        var95_pct=var95_pct,
        cvar_pct=cvar_pct,
        daily_pnl_pct=daily_pnl_pct,
        prev_day_pnl_pct=prev_day_pnl_pct,
        liquidity_crisis=liquidity_crisis,
    )


class TestConfigValidation:
    def test_var_bands_must_be_monotone(self):
        with pytest.raises(InvalidSystemicAlertInputError):
            SystemicRiskAlertConfig(var_yellow_min=0.04, var_orange_min=0.03)

    def test_loss_thresholds_must_be_negative(self):
        with pytest.raises(InvalidSystemicAlertInputError):
            SystemicRiskAlertConfig(daily_loss_orange=0.02)

    def test_cvar_black_must_exceed_var_bands(self):
        with pytest.raises(InvalidSystemicAlertInputError):
            SystemicRiskAlertConfig(cvar_black_min=0.03)


class TestLevelClassification:
    def test_green_when_all_normal(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, var95_pct=0.015, cvar_pct=0.02, daily_pnl_pct=0.005)
        assert a.level is RiskLevel.GREEN
        assert a.directive.new_position_scale == 1.0
        assert a.directive.reduce_pct == 0.0
        assert not a.directive.close_only
        assert not a.directive.trigger_kill_switch
        assert not a.directive.liquidate_all

    def test_yellow_on_var_band(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, var95_pct=0.03)
        assert a.level is RiskLevel.YELLOW
        assert a.directive.new_position_scale == 0.5
        assert a.directive.reduce_pct == 0.0

    def test_yellow_on_consecutive_two_day_loss(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, daily_pnl_pct=-0.012, prev_day_pnl_pct=-0.015)
        assert a.level is RiskLevel.YELLOW

    def test_single_day_loss_alone_not_yellow(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, daily_pnl_pct=-0.015, prev_day_pnl_pct=0.01)
        assert a.level is RiskLevel.GREEN

    def test_orange_on_var_band(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, var95_pct=0.05)
        assert a.level is RiskLevel.ORANGE
        assert a.directive.new_position_scale == 0.0
        assert a.directive.reduce_pct == pytest.approx(0.30)

    def test_orange_on_daily_loss(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, daily_pnl_pct=-0.025)
        assert a.level is RiskLevel.ORANGE

    def test_red_on_var_band(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, var95_pct=0.07)
        assert a.level is RiskLevel.RED
        assert a.directive.reduce_pct == pytest.approx(0.50)
        assert a.directive.close_only

    def test_red_on_daily_loss(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, daily_pnl_pct=-0.045)
        assert a.level is RiskLevel.RED

    def test_black_on_cvar(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, cvar_pct=0.11)
        assert a.level is RiskLevel.BLACK
        assert a.directive.liquidate_all
        assert a.directive.trigger_kill_switch
        assert a.directive.reduce_pct == pytest.approx(1.0)

    def test_black_on_liquidity_crisis(self):
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, liquidity_crisis=True)
        assert a.level is RiskLevel.BLACK

    def test_severity_max_wins(self):
        # 同时命中黄（VaR 3%）与红（单日亏 4.5%）→ 取红
        m = SystemicRiskAlertStateMachine()
        a = _assess(m, var95_pct=0.03, daily_pnl_pct=-0.045)
        assert a.level is RiskLevel.RED

    def test_reasons_recorded_without_short_circuit(self):
        # 黑（CVaR）+ 红（单日亏）+ 黄（连续两日亏）→ 理由须含多条
        m = SystemicRiskAlertStateMachine()
        a = _assess(
            m,
            cvar_pct=0.12,
            daily_pnl_pct=-0.045,
            prev_day_pnl_pct=-0.02,
        )
        assert a.level is RiskLevel.BLACK
        assert len(a.reasons) >= 3


class TestBoundary:
    @pytest.mark.parametrize(
        ("var", "expected"),
        [
            (0.0199, RiskLevel.GREEN),
            (0.02, RiskLevel.YELLOW),
            (0.0399, RiskLevel.YELLOW),
            (0.04, RiskLevel.ORANGE),
            (0.0599, RiskLevel.ORANGE),
            (0.06, RiskLevel.RED),
        ],
    )
    def test_var_band_edges(self, var: float, expected: RiskLevel):
        m = SystemicRiskAlertStateMachine()
        assert _assess(m, var95_pct=var).level is expected

    def test_cvar_black_edge(self):
        m = SystemicRiskAlertStateMachine()
        assert _assess(m, cvar_pct=0.0999).level is RiskLevel.GREEN
        m2 = SystemicRiskAlertStateMachine()
        assert _assess(m2, cvar_pct=0.10).level is RiskLevel.BLACK


class TestStateMachineHistory:
    def test_transitions_are_appended(self):
        m = SystemicRiskAlertStateMachine()
        _assess(m, var95_pct=0.01)  # 初态即 GREEN，同级不入历史
        _assess(m, var95_pct=0.05)
        _assess(m, cvar_pct=0.12)
        history = m.transition_history()
        assert [h[1] for h in history] == [
            RiskLevel.ORANGE,
            RiskLevel.BLACK,
        ]
        assert m.current_level is RiskLevel.BLACK

    def test_repeated_same_level_not_duplicated(self):
        m = SystemicRiskAlertStateMachine()
        _assess(m, var95_pct=0.05)
        _assess(m, var95_pct=0.055)
        assert len(m.transition_history()) == 1


class TestInputValidation:
    def test_non_finite_rejected(self):
        m = SystemicRiskAlertStateMachine()
        with pytest.raises(InvalidSystemicAlertInputError):
            _assess(m, var95_pct=float("nan"))
        with pytest.raises(InvalidSystemicAlertInputError):
            _assess(m, cvar_pct=float("inf"))
        with pytest.raises(InvalidSystemicAlertInputError):
            _assess(m, daily_pnl_pct=float("nan"))
