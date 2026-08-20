# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.lifecycle.test_strategy_retirement_evaluator
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 评审制铁律=只生成报告+人工裁定，永不自动退役;阈值真源=alert_threshold_registry(fail-closed);偏离值外部供给不重算
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRetirementInputError;RetirementConfigError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Strategy Retirement Evaluator 单元测试（55 号 G26 §3.5 双判据+评审制）.

覆盖:
  - 五判据逐一触发（滚动跑输/滚动 Sharpe/回撤漂移/偏离/逻辑失效）
  - 无触发 → None；样本不足跳过不误报
  - 评审制不变量：status 恒 pending_human_review，无任何策略状态写接口
  - ReportPublisher TRADING_REVIEW 归档 + 内容结构
  - fail-closed：注册表缺失 → RetirementConfigError
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from zephyr.governance.lifecycle_governance.strategy_retirement_evaluator import (
    InvalidRetirementInputError,
    RetirementConfigError,
    RetirementCriterion,
    RetirementEvalInput,
    StrategyRetirementEvaluator,
)
from zephyr.reporting.report_publisher import ReportPublisher, ReportSource

NOW = datetime(2026, 8, 15, 15, 0, 0)


def _steady(n: int, r: float) -> list[float]:
    return [r] * n


def _inp(strategy_id: str, live, bench, **kw) -> RetirementEvalInput:
    kw.setdefault("now", NOW)
    kw.setdefault("publish", False)
    return RetirementEvalInput(
        strategy_id=strategy_id,
        live_returns=live,
        benchmark_returns=bench,
        **kw,
    )


class TestThresholdLoading:
    def test_thresholds_match_registry(self):
        ev = StrategyRetirementEvaluator()
        th = ev.thresholds
        assert th["underperformance_gap"] == 0.05
        assert th["sharpe_floor"] == 0.0
        assert th["drawdown_drift_multiplier"] == 1.5
        assert th["deviation_retire"] == 0.50

    def test_missing_registry_fail_closed(self, tmp_path: Path):
        with pytest.raises(RetirementConfigError):
            StrategyRetirementEvaluator(registry_path=tmp_path / "nope.yaml")


class TestCriteria:
    def test_no_trigger_returns_none(self):
        ev = StrategyRetirementEvaluator()
        report = ev.evaluate(_inp("STR-A", _steady(80, 0.001), _steady(80, 0.001)))
        assert report is None

    def test_rolling_underperformance_trigger(self):
        ev = StrategyRetirementEvaluator()
        live = _steady(80, 0.0)  # 20 日累计 0%
        bench = _steady(80, 0.01)  # 20 日累计约 22%，跑输 >5%
        report = ev.evaluate(_inp("STR-A", live, bench))
        assert report is not None
        criteria = {t.criterion for t in report.triggered}
        assert RetirementCriterion.ROLLING_UNDERPERFORMANCE in criteria

    def test_rolling_sharpe_negative_trigger(self):
        ev = StrategyRetirementEvaluator()
        live = [-0.005, -0.003, -0.004, -0.002] * 20  # 80 日持续阴跌
        bench = _steady(80, 0.0)
        report = ev.evaluate(_inp("STR-A", live, bench))
        assert report is not None
        criteria = {t.criterion for t in report.triggered}
        assert RetirementCriterion.ROLLING_SHARPE_NEGATIVE in criteria
        assert report.metrics["rolling_sharpe"] < 0

    def test_drawdown_drift_trigger(self):
        ev = StrategyRetirementEvaluator()
        live = _steady(10, 0.01) + _steady(10, -0.02)  # 先涨后急跌，当前回撤约 18%
        bench = _steady(20, 0.0)
        report = ev.evaluate(_inp("STR-A", live, bench, historical_max_drawdown=0.10))
        assert report is not None
        criteria = {t.criterion for t in report.triggered}
        assert RetirementCriterion.DRAWDOWN_DRIFT in criteria
        assert report.metrics["current_drawdown"] > 0.15

    def test_backtest_live_deviation_trigger(self):
        ev = StrategyRetirementEvaluator()
        report = ev.evaluate(_inp("STR-A", _steady(30, 0.001), _steady(30, 0.001), backtest_live_deviation=0.62))
        assert report is not None
        criteria = {t.criterion for t in report.triggered}
        assert RetirementCriterion.BACKTEST_LIVE_DEVIATION in criteria

    def test_alpha_falsified_trigger(self):
        ev = StrategyRetirementEvaluator()
        report = ev.evaluate(
            _inp(
                "STR-A",
                _steady(30, 0.001),
                _steady(30, 0.001),
                alpha_falsified=True,
                falsified_factors=("FCT-MOM-001",),
            )
        )
        assert report is not None
        criteria = {t.criterion for t in report.triggered}
        assert RetirementCriterion.ALPHA_FALSIFIED in criteria
        assert report.falsified_factors == ("FCT-MOM-001",)

    def test_insufficient_window_skips_criterion(self):
        """样本不足窗口的判据跳过（不产生误报）。"""
        ev = StrategyRetirementEvaluator()
        live = _steady(10, 0.0)  # < 20 日窗口
        bench = _steady(10, 0.05)  # 10 日暴升——若误判会触发跑输
        assert ev.evaluate(_inp("STR-A", live, bench)) is None

    def test_review_only_invariant(self):
        """评审制铁律：报告 status 恒 pending_human_review，无任何自动退役字段。"""
        ev = StrategyRetirementEvaluator()
        report = ev.evaluate(_inp("STR-A", _steady(80, 0.0), _steady(80, 0.01)))
        assert report is not None
        assert report.status == "pending_human_review"
        assert report.recommendation == "retire_review"
        assert not hasattr(report, "auto_retire")

    def test_empty_input_rejected(self):
        ev = StrategyRetirementEvaluator()
        with pytest.raises(InvalidRetirementInputError):
            ev.evaluate(_inp("STR-A", [], []))


class TestPublishIntegration:
    def test_report_archived_via_trading_review(self):
        publisher = ReportPublisher()
        ev = StrategyRetirementEvaluator(publisher=publisher)
        report = ev.evaluate(_inp("STR-A", _steady(80, 0.0), _steady(80, 0.01), publish=True))
        assert report is not None
        archived_list = publisher.list_by_type("strategy_retirement_evaluation")
        assert len(archived_list) == 1
        archived = archived_list[0]
        assert archived.report_id == report.report_id
        assert archived.source is ReportSource.TRADING_REVIEW
        assert archived.content["status"] == "pending_human_review"
        assert archived.content["strategy_id"] == "STR-A"
        assert len(archived.content["triggered"]) >= 1

    def test_no_trigger_no_archive(self):
        publisher = ReportPublisher()
        ev = StrategyRetirementEvaluator(publisher=publisher)
        result = ev.evaluate(_inp("STR-A", _steady(80, 0.001), _steady(80, 0.001), publish=True))
        assert result is None
        assert publisher.list_by_source(ReportSource.TRADING_REVIEW) == []
