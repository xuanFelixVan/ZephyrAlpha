# [A_test] module_id: MOD-GOV_test_survival_line_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.risk.core.test_survival_line_monitor
# [TESTS] src/zephyr/risk/core/survival_line_monitor.py
# [TTL] task_bound
"""90 号 Phase2 项（#16 系统级成功指标）：生存线监控已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §16（v2.0.0 修订采纳）——
  ① 生存线：滚动 12 个月超额>0 且 MaxDD<15% 且 Sharpe≥0.8；
     失败指标：连续 6 个月亏损 / 回撤>25%（与 4 级 Protocol Level4 一致）；
  ② 健康/卓越线暂缓定死（实盘 6-12 月校准）——配置占位不启用。
"""

from __future__ import annotations

from zephyr.risk.core.survival_line_monitor import (
    HealthExcellenceConfig,
    SurvivalInput,
    SurvivalLineConfig,
    SurvivalStatus,
    evaluate_survival_line,
)

_GOOD = SurvivalInput(
    excess_return_12m=0.05, max_drawdown=0.10, sharpe=1.2, consecutive_loss_months=0
)


class TestSurvivalLine:
    def test_all_good_is_ok(self):
        res = evaluate_survival_line(_GOOD)
        assert res.status == SurvivalStatus.OK
        assert res.breaches == []

    def test_sharpe_below_08_breach(self):
        res = evaluate_survival_line(SurvivalInput(0.05, 0.10, 0.7, 0))
        assert res.status == SurvivalStatus.SURVIVAL_BREACH
        assert any("Sharpe" in b for b in res.breaches)

    def test_maxdd_at_15pct_breach(self):
        res = evaluate_survival_line(SurvivalInput(0.05, 0.15, 1.2, 0))
        assert res.status == SurvivalStatus.SURVIVAL_BREACH

    def test_zero_excess_breach(self):
        """超额必须 >0（=0 即破生存线）。"""
        res = evaluate_survival_line(SurvivalInput(0.0, 0.10, 1.2, 0))
        assert res.status == SurvivalStatus.SURVIVAL_BREACH

    def test_six_consecutive_loss_months_failure(self):
        res = evaluate_survival_line(SurvivalInput(0.05, 0.10, 1.2, 6))
        assert res.status == SurvivalStatus.FAILURE

    def test_drawdown_over_25pct_failure(self):
        """回撤>25% 与 4 级 Protocol Level4 一致。"""
        res = evaluate_survival_line(SurvivalInput(0.05, 0.26, 1.2, 0))
        assert res.status == SurvivalStatus.FAILURE

    def test_failure_precedence_over_breach(self):
        """失败指标优先于生存线突破。"""
        res = evaluate_survival_line(SurvivalInput(-0.01, 0.30, 0.5, 7))
        assert res.status == SurvivalStatus.FAILURE

    def test_custom_config(self):
        cfg = SurvivalLineConfig(sharpe_min=1.0)
        res = evaluate_survival_line(SurvivalInput(0.05, 0.10, 0.9, 0), cfg)
        assert res.status == SurvivalStatus.SURVIVAL_BREACH


class TestHealthExcellencePlaceholder:
    def test_disabled_by_default(self):
        """健康/卓越线配置占位：默认不启用（实盘 6-12 月校准后启用）。"""
        cfg = HealthExcellenceConfig()
        assert cfg.enabled is False
