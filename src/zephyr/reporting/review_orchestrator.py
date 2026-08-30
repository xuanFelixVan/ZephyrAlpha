# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md | §
# [MODULE] zephyr.reporting.review_orchestrator
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.risk.core.daily_auditor; zephyr.reporting.risk_report_engine; zephyr.reporting.report_publisher; zephyr.risk.core.strategy_deviation_monitor (可选); zephyr.governance.lifecycle_governance.strategy_retirement_evaluator (可选)
# [CONSUMERS] 调用方(日终/周末/月末事件驱动的复盘触发)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件驱动零定时器(禁 cron/Timer);日复盘机器自动+人只看 FAIL 项;周复盘四段模板固定(盈亏归因/偏离告警/阈值变更/action items);ReportPublisher 唯一归档出口;评审制=退役扫描只聚合报告不改策略状态
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidReviewInputError
# [TESTS] tests/reporting/test_review_orchestrator.py
# [A_module] module_id=MOD-RPT-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_REPORTING — Review Orchestrator (MOD-RPT-009)

复盘编排器——日/周/月三频复盘链路的编排与归档（55 号 G26 §3.6 决策落地）。

组装缺口（非从零实现）：DailyAuditor 五件套 / RiskReportEngine 四类报告 /
ReportPublisher 归档均已 production，缺的是「把它们串成人能用的复盘闭环」。
本模块只做编排不新造分析：

  频率分层（55 号 §3.6 决策，自动化分层化解三频过重）:
    日复盘 = 机器自动——DailyAuditor.audit + generate_daily，人只看 FAIL 项
    周复盘 = 人读——WeeklyRiskDeep + 四段式周报复盘（唯一固定议程）
    月复盘 = 轻量治理汇总——MonthlyRiskGovernance + 策略退役判据扫描聚合

  周复盘四段模板（55 号 §3.6 决策五，固定结构）:
    ①本周盈亏与归因（54 号对账归因链路供给，调用方传入）
    ②偏离与告警事件（MOD-RK-23 偏离 verdict 快照 + 告警事件清单）
    ③阈值与参数变更（调用方传入变更清单——阈值真源 alert_threshold_registry）
    ④下周 action items（产出经 action_item_sink 进 IncidentManager/候选库，调用方接线）

事件驱动铁律：本模块无定时器/无 daemon——run_daily/run_weekly/run_monthly
由调用方在日终/周末/月末事件（如 DailyAuditor 完成、交易日历事件）触发。

SSoT: depgraph MOD-RPT-009 | blueprint.md §3 | 55 号 §3.6

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: auditor 参数
#   fields: 参数 auditor（无注解）
#   code: review_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: report_engine 参数
#   fields: 参数 report_engine（无注解）
#   code: review_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: publisher 参数
#   fields: 参数 publisher（无注解）
#   code: review_orchestrator.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: deviation_monitor 参数
#   fields: 参数 deviation_monitor（无注解）
#   code: review_orchestrator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReviewOrchestrator
#   name_en: ReviewOrchestrator
#   intro: 复盘编排器（55 号 §3.6）：串联 daily→weekly→monthly 链路并归档。
#   desc: 复盘编排器（55 号 §3.6）：串联 daily→weekly→monthly 链路并归档。 全部依赖构造注入（Fake 友好）；deviation_monitor / ret…；公共方法（定义序）: run_dai…
#   inputs: auditor report_engine publisher deviation_monitor retirement_evaluato…
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ReviewOrchestrator
#   downstream: 调用方(日终/周末/月末事件驱动的复盘触发)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Final, Sequence

from zephyr.reporting.report_publisher import (
    ArchivedReport,
    ReportPublisher,
    ReportSource,
)
from zephyr.reporting.risk_report_engine import (
    DailyRiskSummary,
    MonthlyRiskGovernance,
    RiskReportEngine,
    WeeklyRiskDeep,
)
from zephyr.risk.core.daily_auditor import (
    AuditRequest,
    AuditStatus,
    DailyAuditor,
    DailyAuditReport,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)


class InvalidReviewInputError(ZephyrBaseError):
    """复盘编排输入非法。"""

    error_code = "ZA-RPT-0027"


#: 周复盘四段固定标题（55 号 §3.6 决策；人工维护模板资产见 blueprint 同目录 weekly_review_template.md）
WEEKLY_REVIEW_SECTIONS: tuple[str, ...] = (
    "本周盈亏与归因",
    "偏离与告警事件",
    "阈值与参数变更",
    "下周 action items",
)


@dataclass(frozen=True)
class DailyReviewResult:
    """日复盘产物（机器自动；human_attention 非空 = 人需要看的 FAIL/WARN 项）。"""

    trading_date: str
    audit_report: DailyAuditReport
    daily_summary: DailyRiskSummary
    human_attention: tuple[str, ...]
    deviation_verdicts: dict
    archived_report: ArchivedReport | None


@dataclass(frozen=True)
class WeeklyReviewResult:
    """周复盘产物（人读；markdown = 四段式复盘文档）。"""

    period: str
    weekly_deep: WeeklyRiskDeep
    markdown: str
    action_items: tuple[str, ...]
    archived_report: ArchivedReport | None


@dataclass(frozen=True)
class MonthlyReviewResult:
    """月复盘产物（轻量治理汇总 + 退役判据扫描聚合）。"""

    month: str
    monthly_governance: MonthlyRiskGovernance
    retirement_report_count: int
    retirement_strategy_ids: tuple[str, ...]
    archived_report: ArchivedReport | None


class ReviewOrchestrator:
    """复盘编排器（55 号 §3.6）：串联 daily→weekly→monthly 链路并归档。

    全部依赖构造注入（Fake 友好）；deviation_monitor / retirement_evaluator 可选——
    未注入时对应段落留空标注，不阻断主链路。
    """

    def __init__(
        self,
        auditor: DailyAuditor,
        report_engine: RiskReportEngine,
        publisher: ReportPublisher,
        deviation_monitor=None,
        retirement_evaluator=None,
        action_item_sink: Callable[[str], None] | None = None,
    ) -> None:
        self._auditor = auditor
        self._engine = report_engine
        self._publisher = publisher
        self._deviation_monitor = deviation_monitor
        self._retirement_evaluator = retirement_evaluator
        self._action_item_sink = action_item_sink

    # ── 日复盘（机器自动，人只看 FAIL 项）──

    def run_daily(
        self,
        trading_date: str,
        audit_request: AuditRequest,
        snapshot,
        metrics,
        *,
        publish: bool = True,
    ) -> DailyReviewResult:
        """日终复盘：DailyAuditor 五件套 + DailyRiskSummary + 归档。

        human_attention: overall_status != PASS 时的待人看清单（issues + 摘要），
        PASS 时为空（55 号 §3.6：人只看 FAIL 项——告警驱动）。
        """
        audit_report = self._auditor.audit(audit_request)
        daily_summary = self._engine.generate_daily(snapshot, metrics)

        human_attention: tuple[str, ...] = ()
        if audit_report.overall_status is not AuditStatus.PASS:
            human_attention = tuple(
                f"[{issue.severity.value}] {issue.category}: {issue.description}" for issue in audit_report.issues
            ) or (f"日终审计 {audit_report.overall_status.value}（无 IssueRecord 明细）",)

        verdicts = self._deviation_monitor.get_latest_verdicts() if self._deviation_monitor is not None else {}
        archived = None
        if publish:
            archived = self._publisher.publish(
                report_id=f"DAILY-REVIEW-{daily_summary.portfolio_id}-{trading_date}",
                source=ReportSource.RISK,
                report_type="daily_risk_review",
                content={
                    "trading_date": trading_date,
                    "portfolio_id": daily_summary.portfolio_id,
                    "audit_status": audit_report.overall_status.value,
                    "audit_report_id": getattr(audit_report, "report_id", ""),
                    "daily_summary_report_id": daily_summary.report_id,
                    "risk_level": daily_summary.risk_level.value,
                    "overall_risk_score": daily_summary.overall_risk_score,
                    "current_drawdown": daily_summary.current_drawdown,
                    "alert_count": daily_summary.alert_count,
                    "human_attention": list(human_attention),
                    "deviation_actions": {sid: v.action.value for sid, v in verdicts.items()},
                },
            )
        logger.info(
            "日复盘完成 %s: audit=%s risk=%s 待人看=%d",
            trading_date,
            audit_report.overall_status.value,
            daily_summary.risk_level.value,
            len(human_attention),
        )
        return DailyReviewResult(
            trading_date=trading_date,
            audit_report=audit_report,
            daily_summary=daily_summary,
            human_attention=human_attention,
            deviation_verdicts=verdicts,
            archived_report=archived,
        )

    # ── 周复盘（人读，四段式模板）──

    def run_weekly(
        self,
        period: str,
        daily_summaries: Sequence[DailyRiskSummary],
        *,
        pnl_attribution: str | None = None,
        alert_events: Sequence[str] = (),
        threshold_changes: Sequence[str] = (),
        action_items: Sequence[str] = (),
        publish: bool = True,
    ) -> WeeklyReviewResult:
        """周复盘：WeeklyRiskDeep + 四段式 markdown + 归档（TRADING_REVIEW 源）。

        Args:
            period: 周区间（如 2026-W33 / 2026-08-10~2026-08-14）
            daily_summaries: 本周 DailyRiskSummary 序列（非空）
            pnl_attribution: ①段内容（54 号对账归因链路供给，人可读文本）
            alert_events: ②段补充告警事件清单
            threshold_changes: ③段阈值/参数变更清单（真源 alert_threshold_registry）
            action_items: ④段下周行动项（经 action_item_sink 外送 IncidentManager/候选库）
        """
        if not daily_summaries:
            raise InvalidReviewInputError("daily_summaries 不可为空")
        weekly_deep = self._engine.generate_weekly(list(daily_summaries))
        markdown = self._render_weekly_markdown(
            period=period,
            weekly_deep=weekly_deep,
            pnl_attribution=pnl_attribution,
            alert_events=tuple(alert_events),
            threshold_changes=tuple(threshold_changes),
            action_items=tuple(action_items),
        )
        for item in action_items:
            if self._action_item_sink is not None:
                try:
                    self._action_item_sink(item)
                except Exception:  # noqa: BLE001 — action item 外送失败不阻断复盘归档
                    logger.exception("action_item_sink 异常（已隔离）: %s", item)
        archived = None
        if publish:
            archived = self._publisher.publish(
                report_id=f"WEEKLY-REVIEW-{weekly_deep.portfolio_id}-{weekly_deep.week_end}",
                source=ReportSource.TRADING_REVIEW,
                report_type="weekly_review",
                content={
                    "period": period,
                    "portfolio_id": weekly_deep.portfolio_id,
                    "week_start": weekly_deep.week_start,
                    "week_end": weekly_deep.week_end,
                    "avg_risk_score": weekly_deep.avg_risk_score,
                    "max_drawdown": weekly_deep.max_drawdown,
                    "alert_total": weekly_deep.alert_total,
                    "trend_direction": weekly_deep.trend_direction.value,
                    "action_items": list(action_items),
                    "markdown": markdown,
                },
            )
        logger.info("周复盘完成 %s: 行动项 %d 条", period, len(action_items))
        return WeeklyReviewResult(
            period=period,
            weekly_deep=weekly_deep,
            markdown=markdown,
            action_items=tuple(action_items),
            archived_report=archived,
        )

    def _render_weekly_markdown(
        self,
        *,
        period: str,
        weekly_deep: WeeklyRiskDeep,
        pnl_attribution: str | None,
        alert_events: tuple[str, ...],
        threshold_changes: tuple[str, ...],
        action_items: tuple[str, ...],
    ) -> str:
        """四段式周复盘文档渲染（模板结构固定=55 号 §3.6 决策五）。"""
        verdicts = self._deviation_monitor.get_latest_verdicts() if self._deviation_monitor is not None else {}
        lines: list[str] = [
            f"# 周复盘 {period}",
            "",
            f"> 风险概览：日均评分 {weekly_deep.avg_risk_score:.3f} / 最大回撤 "
            f"{weekly_deep.max_drawdown:.2%} / 告警 {weekly_deep.alert_total} 条 / "
            f"趋势 {weekly_deep.trend_direction.value}",
            "",
            f"## 1. {WEEKLY_REVIEW_SECTIONS[0]}",
            "",
            pnl_attribution or "（本周盈亏与归因数据未供给——54 号链路接线后自动填充）",
            "",
            f"## 2. {WEEKLY_REVIEW_SECTIONS[1]}",
            "",
        ]
        if verdicts:
            lines.append("| 策略 | 偏离度 | 日收益相关 | 动作 |")
            lines.append("|---|---|---|---|")
            for sid, v in sorted(verdicts.items()):
                deviation = f"{v.cum_relative_deviation:.2%}" if v.cum_relative_deviation is not None else "NA"
                corr = f"{v.daily_return_correlation:.3f}" if v.daily_return_correlation is not None else "NA"
                flag = "（相关破下限）" if v.correlation_below_floor else ""
                lines.append(f"| {sid} | {deviation} | {corr} | {v.action.value}{flag} |")
        else:
            lines.append("（无偏离度量数据——首批策略上线后由 MOD-RK-23 供给）")
        lines.append("")
        if alert_events:
            lines.extend(f"- {e}" for e in alert_events)
        else:
            lines.append("- 本周无新增告警事件")
        lines += ["", f"## 3. {WEEKLY_REVIEW_SECTIONS[2]}", ""]
        if threshold_changes:
            lines.extend(f"- {c}" for c in threshold_changes)
        else:
            lines.append("- 本周无阈值/参数变更（阈值真源：alert_threshold_registry.yaml）")
        lines += ["", f"## 4. {WEEKLY_REVIEW_SECTIONS[3]}", ""]
        if action_items:
            lines.extend(f"- [ ] {a}" for a in action_items)
        else:
            lines.append("- 无")
        lines.append("")
        return "\n".join(lines)

    # ── 月复盘（轻量治理汇总 + 退役判据扫描）──

    def run_monthly(
        self,
        month: str,
        daily_summaries: Sequence[DailyRiskSummary],
        *,
        retirement_inputs: Sequence[dict] = (),
        publish: bool = True,
    ) -> MonthlyReviewResult:
        """月复盘：MonthlyRiskGovernance + 退役判据扫描聚合 + 归档。

        Args:
            month: 月份（YYYY-MM）
            daily_summaries: 本月 DailyRiskSummary 序列（非空）
            retirement_inputs: 退役扫描输入（每项为 StrategyRetirementEvaluator.evaluate
                的关键字参数 dict；需构造时注入 retirement_evaluator 才执行扫描）
        """
        if not daily_summaries:
            raise InvalidReviewInputError("daily_summaries 不可为空")
        monthly = self._engine.generate_monthly(list(daily_summaries))

        retirement_reports: list = []
        if retirement_inputs and self._retirement_evaluator is not None:
            # lazy import：retirement_evaluator 顶层 import zephyr.reporting.report_publisher
            # 会触发本包 __init__，顶层再引回即循环——故延迟到调用点（A.14.8 单点豁免）
            from zephyr.governance.lifecycle_governance.strategy_retirement_evaluator import (
                RetirementEvalInput,
            )

            for kwargs in retirement_inputs:
                report = self._retirement_evaluator.evaluate(RetirementEvalInput(**kwargs))
                if report is not None:
                    retirement_reports.append(report)
        elif retirement_inputs:
            logger.warning("retirement_inputs 非空但未注入 retirement_evaluator，退役扫描跳过")

        archived = None
        if publish:
            archived = self._publisher.publish(
                report_id=f"MONTHLY-REVIEW-{monthly.portfolio_id}-{month}",
                source=ReportSource.TRADING_REVIEW,
                report_type="monthly_review",
                content={
                    "month": month,
                    "portfolio_id": monthly.portfolio_id,
                    "trading_days": monthly.trading_days,
                    "avg_risk_score": monthly.avg_risk_score,
                    "max_drawdown": monthly.max_drawdown,
                    "total_alerts": monthly.total_alerts,
                    "high_risk_days": monthly.high_risk_days,
                    "critical_risk_days": monthly.critical_risk_days,
                    "retirement_report_ids": [r.report_id for r in retirement_reports],
                    "retirement_strategy_ids": [r.strategy_id for r in retirement_reports],
                },
            )
        logger.info("月复盘完成 %s: 退役评估报告 %d 份", month, len(retirement_reports))
        return MonthlyReviewResult(
            month=month,
            monthly_governance=monthly,
            retirement_report_count=len(retirement_reports),
            retirement_strategy_ids=tuple(r.strategy_id for r in retirement_reports),
            archived_report=archived,
        )


__all__: Final = [
    "DailyReviewResult",
    "InvalidReviewInputError",
    "MonthlyReviewResult",
    "ReviewOrchestrator",
    "WEEKLY_REVIEW_SECTIONS",
    "WeeklyReviewResult",
]
