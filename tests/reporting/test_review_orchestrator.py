# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md
# [MODULE] tests.reporting.test_review_orchestrator
# [DOMAIN] D_REPORTING
# [INVARIANTS] 事件驱动零定时器;日复盘人只看 FAIL 项;周复盘四段固定模板;ReportPublisher 唯一出口;退役扫描只聚合不改状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidReviewInputError
# [TESTS] self
# [A_module] module_id=MOD-RPT-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-009 Review Orchestrator 单元测试（55 号 G26 §3.6）.

覆盖:
  - 日复盘：PASS → 人无需看；FAIL → human_attention 提取 IssueRecord
  - 周复盘：四段固定模板渲染 + 偏离表 + action items sink + TRADING_REVIEW 归档
  - 月复盘：MonthlyRiskGovernance + 退役判据扫描聚合
  - 边界：空日度序列拒绝；可选依赖未注入降级不阻断
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from zephyr.governance.lifecycle_governance.strategy_retirement_evaluator import (
    StrategyRetirementEvaluator,
)
from zephyr.reporting.report_publisher import ReportPublisher, ReportSource
from zephyr.reporting.review_orchestrator import (
    WEEKLY_REVIEW_SECTIONS,
    InvalidReviewInputError,
    ReviewOrchestrator,
)
from zephyr.reporting.risk_report_engine import (
    DailyRiskSummary,
    RiskLevel,
    RiskReportEngine,
)
from zephyr.risk.core.daily_auditor import (
    AuditStatus,
    IssueRecord,
    IssueSeverity,
)
from zephyr.risk.core.strategy_deviation_monitor import StrategyDeviationMonitor


def _daily_summary(date: str, score: float = 0.4, alerts: int = 0) -> DailyRiskSummary:
    return DailyRiskSummary(
        report_id=f"DRS-{date}",
        report_date=date,
        portfolio_id="PF-1",
        risk_level=RiskLevel.MEDIUM,
        var_1d_95=0.02,
        var_1d_99=0.03,
        cvar_1d_95=0.025,
        cvar_1d_99=0.035,
        current_drawdown=-0.05,
        max_drawdown=-0.08,
        gross_leverage=1.2,
        top_position_concentration=0.15,
        overall_risk_score=score,
        sharpe_ratio=1.1,
        sortino_ratio=1.3,
        beta=0.9,
        volatility_1d=0.018,
        sector_concentrations={"tech": 0.3},
        active_alerts=[],
        alert_count=alerts,
        generated_at=datetime(2026, 8, 15, 15, 0, tzinfo=UTC),
    )


def _audit_report(status: AuditStatus, issues=()):
    return SimpleNamespace(overall_status=status, issues=list(issues))


class _FakeAuditor:
    def __init__(self, report):
        self._report = report

    def audit(self, request):
        return self._report


class _FakeEngine:
    """generate_daily 打桩；weekly/monthly 委托真实引擎（聚合逻辑真实覆盖）。"""

    def __init__(self):
        self._real = RiskReportEngine()

    def generate_daily(self, snapshot, metrics):
        return _daily_summary("2026-08-14")

    def generate_weekly(self, daily_summaries):
        return self._real.generate_weekly(daily_summaries)

    def generate_monthly(self, daily_summaries):
        return self._real.generate_monthly(daily_summaries)


def _orchestrator(audit_status=AuditStatus.PASS, issues=(), **kwargs):
    publisher = kwargs.pop("publisher", ReportPublisher())
    orchestrator = ReviewOrchestrator(
        auditor=_FakeAuditor(_audit_report(audit_status, issues)),
        report_engine=_FakeEngine(),
        publisher=publisher,
        **kwargs,
    )
    return orchestrator, publisher


class TestDailyReview:
    def test_pass_no_human_attention(self):
        orch, publisher = _orchestrator()
        result = orch.run_daily("2026-08-14", object(), None, None)
        assert result.audit_report.overall_status is AuditStatus.PASS
        assert result.human_attention == ()
        assert result.archived_report is not None
        assert result.archived_report.source is ReportSource.RISK
        assert result.archived_report.report_type == "daily_risk_review"

    def test_fail_extracts_issues(self):
        issue = IssueRecord(
            issue_id="ISS-1",
            category="PNL_RECONCILIATION",
            severity=IssueSeverity.HIGH,
            description="PnL 对账差 0.3%",
        )
        orch, _ = _orchestrator(audit_status=AuditStatus.FAIL, issues=[issue])
        result = orch.run_daily("2026-08-14", object(), None, None)
        assert len(result.human_attention) == 1
        assert "PnL 对账差" in result.human_attention[0]
        assert "HIGH" in result.human_attention[0]

    def test_deviation_snapshot_attached(self):
        monitor = StrategyDeviationMonitor()
        bt = [0.01] * 10
        monitor.evaluate("STR-A", [0.003] * 10, bt)  # RETIRE 档
        orch, _ = _orchestrator(deviation_monitor=monitor)
        result = orch.run_daily("2026-08-14", object(), None, None)
        assert result.deviation_verdicts["STR-A"].action.value == "retire"
        assert result.archived_report.content["deviation_actions"] == {"STR-A": "retire"}


class TestWeeklyReview:
    def test_four_sections_fixed_template(self):
        orch, publisher = _orchestrator()
        dailies = [_daily_summary(f"2026-08-{d:02d}", score=0.4) for d in range(10, 15)]
        result = orch.run_weekly(
            "2026-W33",
            dailies,
            pnl_attribution="本周盈亏 +1.2%，归因：打板因子贡献 0.8%",
            alert_events=["RED: 数据链路中断 3 分钟"],
            threshold_changes=["THD-DEVIATION-003 相关下限 0.5（待裁定）"],
            action_items=["排查 STR-A 偏离"],
        )
        md = result.markdown
        for i, section in enumerate(WEEKLY_REVIEW_SECTIONS, start=1):
            assert f"## {i}. {section}" in md
        assert "打板因子贡献" in md
        assert "数据链路中断" in md
        assert "THD-DEVIATION-003" in md
        assert "- [ ] 排查 STR-A 偏离" in md
        archived = result.archived_report
        assert archived is not None
        assert archived.source is ReportSource.TRADING_REVIEW
        assert archived.report_type == "weekly_review"
        assert archived.content["markdown"] == md

    def test_deviation_table_rendered(self):
        monitor = StrategyDeviationMonitor()
        monitor.evaluate("STR-B", [0.003] * 10, [0.01] * 10)
        orch, _ = _orchestrator(deviation_monitor=monitor)
        dailies = [_daily_summary(f"2026-08-{d:02d}") for d in range(10, 15)]
        result = orch.run_weekly("2026-W33", dailies)
        assert "| STR-B |" in result.markdown
        assert "retire" in result.markdown

    def test_action_item_sink_called(self):
        sink_calls = []
        orch, _ = _orchestrator(action_item_sink=sink_calls.append)
        dailies = [_daily_summary(f"2026-08-{d:02d}") for d in range(10, 15)]
        orch.run_weekly("2026-W33", dailies, action_items=["任务甲", "任务乙"])
        assert sink_calls == ["任务甲", "任务乙"]

    def test_empty_summaries_rejected(self):
        orch, _ = _orchestrator()
        with pytest.raises(InvalidReviewInputError):
            orch.run_weekly("2026-W33", [])


class TestMonthlyReview:
    def test_monthly_with_retirement_scan(self):
        publisher = ReportPublisher()
        evaluator = StrategyRetirementEvaluator(publisher=publisher)
        orch, _ = _orchestrator(publisher=publisher, retirement_evaluator=evaluator)
        dailies = [_daily_summary(f"2026-08-{d:02d}") for d in range(1, 15)]
        result = orch.run_monthly(
            "2026-08",
            dailies,
            retirement_inputs=[
                {
                    "strategy_id": "STR-A",
                    "live_returns": [0.0] * 80,
                    "benchmark_returns": [0.01] * 80,  # 滚动 20 日跑输 >5% → 触发
                    "publish": True,
                },
                {
                    "strategy_id": "STR-B",
                    "live_returns": [0.001] * 80,
                    "benchmark_returns": [0.001] * 80,  # 无触发
                    "publish": True,
                },
            ],
        )
        assert result.retirement_report_count == 1
        assert result.retirement_strategy_ids == ("STR-A",)
        assert result.archived_report is not None
        assert result.archived_report.report_type == "monthly_review"
        # 退役评估报告本身也经 TRADING_REVIEW 归档（评审制产物）
        retirement_reports = publisher.list_by_type("strategy_retirement_evaluation")
        assert len(retirement_reports) == 1
        assert retirement_reports[0].content["status"] == "pending_human_review"

    def test_retirement_inputs_without_evaluator_degrades(self):
        orch, _ = _orchestrator()
        dailies = [_daily_summary(f"2026-08-{d:02d}") for d in range(1, 15)]
        result = orch.run_monthly(
            "2026-08",
            dailies,
            retirement_inputs=[{"strategy_id": "STR-A", "live_returns": [0.0] * 80, "benchmark_returns": [0.01] * 80}],
        )
        assert result.retirement_report_count == 0

    def test_empty_summaries_rejected(self):
        orch, _ = _orchestrator()
        with pytest.raises(InvalidReviewInputError):
            orch.run_monthly("2026-08", [])
