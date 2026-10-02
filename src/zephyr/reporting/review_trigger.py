# [BLUEPRINT] MOD-RPT-038 | docs/03_modules/_domain_reporting/review_trigger/blueprint.md | §
# [MODULE] zephyr.reporting.review_trigger
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.review_orchestrator; zephyr.reporting.report_publisher; zephyr.reporting.report_archive_sink; zephyr.reporting.risk_report_engine; zephyr.risk.core.daily_auditor; zephyr.shared.contracts.risk_dashboard_snapshot; zephyr.shared.contracts.risk_metrics
# [CONSUMERS] 日终事件宿主（run_post_settlement/骨架体检班/api_server 侧班——三选一 Owner 待裁）+ CLI 手动触发（python -m zephyr.reporting.review_trigger）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 事件驱动零定时器（禁 cron/Timer/计划任务——触发宿主由调用方事件决定）; 上游输入缺口显式标注（空持仓/空成交/零净值最小输入，同 run_post_settlement 先例，不伪装完整审计）; 归档经 ReportPublisher+JsonlArchiveSink 落盘 data/reports/; 触发函数可注入编排器（Fake 友好）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidReviewInputError(ZA-RPT-0027, re-export)；trading_date 非法抛 ValueError
# [TESTS] tests/reporting/test_review_trigger.py
# [A_module] module_id=MOD-RPT-038 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: D_REPORTING 复盘链事件触发入口（MOD-RPT-038），编排既有件零新造分析——与晨报摘要器/通知路由等命中件不同域不同对象，命中系翻译册大白话 token 撞词非第二真源

"""
D_REPORTING — Review Trigger (复盘链事件触发入口，MOD-RPT-038)

F115 R1 触发链薄刀：review_orchestrator.py:48 铁律"run_daily/run_weekly/run_monthly
由调用方在日终/周末/月末事件触发"——而**该调用方全仓不存在**（90 册 grep 穷尽复证）。
本模块补最薄一刀：一个可独立验收的**触发面**——

  - trigger_daily_review(): 缺失的"调用方"函数。组装最小 AuditRequest + 契约
    快照/指标（上游持仓/净值/限额真源未接线——空输入显式标注，同
    scripts/tasks/run/run_post_settlement.py _build_audit_fn 先例，不伪装完整审计），
    驱动真实 ReviewOrchestrator.run_daily 全链（审计→日摘要→归档）；
  - build_default_orchestrator(): 真实依赖装配（DailyAuditor + RiskReportEngine +
    ReportPublisher+JsonlArchiveSink→data/reports/ 归档落盘）；
  - CLI: python -m zephyr.reporting.review_trigger --trading-date YYYY-MM-DD
    ——一次性事件入口（人工/运维/宿主侧班均可调），零定时器零计划任务。

不重复建设边界：晨报摘要=strategy_pipeline.morning_digest（建议包承接面，
在途袋领地）；本模块=报告域复盘链触发面，零交集。

R1 触发宿主三选一（F74 汇总器/骨架体检班/api_server 侧班）为 Owner 待裁项——
本模块宿主中立：选定后宿主只需调用 trigger_daily_review() 一行接线。

SSoT: depgraph MOD-RPT-038 | blueprint.md | 90 册 R1 断点 + 04 册 §四-1

# [ALGO_FLOW] external: docs/03_modules/_domain_reporting/algo_flow/review_trigger.yaml
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Final

from zephyr.reporting.report_archive_sink import JsonlArchiveSink
from zephyr.reporting.report_publisher import ReportPublisher
from zephyr.reporting.review_orchestrator import (
    DailyReviewResult,
    InvalidReviewInputError,
    ReviewOrchestrator,
)
from zephyr.reporting.risk_report_engine import RiskReportEngine
from zephyr.risk.core.daily_auditor import AuditRequest, DailyAuditor
from zephyr.shared.contracts.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.contracts.risk_metrics import RiskMetricsReport

_logger = logging.getLogger(__name__)

#: 模拟盘组合默认 ID（与 scripts/tasks/run/run_post_settlement.py 同一口径）
_PAPER_PORTFOLIO_ID: Final = "PAPER-DEFAULT"


def build_default_orchestrator(archive_path: str | Path | None = None) -> ReviewOrchestrator:
    """真实依赖装配——DailyAuditor+RiskReportEngine+ReportPublisher(挂 JsonlArchiveSink)。

    Args:
        archive_path: 归档落盘路径（None=默认 data/reports/report_archive.jsonl）。
    """
    sink = JsonlArchiveSink(archive_path) if archive_path is not None else JsonlArchiveSink()
    publisher = ReportPublisher(archive_sink=sink)
    return ReviewOrchestrator(
        auditor=DailyAuditor(),
        report_engine=RiskReportEngine(),
        publisher=publisher,
    )


def _build_minimal_snapshot(portfolio_id: str, trading_date: str) -> RiskDashboardSnapshot:
    """最小契约快照（上游风险仪表盘真源未接线——零值显式标注，不伪装真实读数）。"""
    return RiskDashboardSnapshot(
        gross_leverage=0.0,
        idempotency_key=f"daily-review-{portfolio_id}-{trading_date}",
        max_drawdown_current=0.0,
        overall_risk_score=0.0,
        portfolio_id=portfolio_id,
        portfolio_var_1d=0.0,
        snapshot_time=datetime.now(UTC).isoformat(),
        top_position_concentration=0.0,
        active_alerts=[],
    )


def _build_minimal_metrics(portfolio_id: str, trading_date: str) -> RiskMetricsReport:
    """最小契约指标（上游风险指标真源未接线——零值显式标注，不伪装真实读数）。"""
    return RiskMetricsReport(
        as_of_date=datetime.now(UTC),
        beta=0.0,
        calculation_method="upstream_gap_minimal",
        confidence_level=0.95,
        current_drawdown=0.0,
        cvar_1d_95=0.0,
        cvar_1d_99=0.0,
        idempotency_key=f"daily-metrics-{portfolio_id}-{trading_date}",
        lookback_period=0,
        max_drawdown=0.0,
        portfolio_id=portfolio_id,
        sharpe_ratio=0.0,
        sortino_ratio=0.0,
        var_1d_95=0.0,
        var_1d_99=0.0,
        volatility_1d=0.0,
        volatility_1m=0.0,
    )


def trigger_daily_review(
    trading_date: str,
    *,
    orchestrator: ReviewOrchestrator | None = None,
    portfolio_id: str = _PAPER_PORTFOLIO_ID,
    publish: bool = True,
) -> DailyReviewResult:
    """日复盘触发入口——缺失的"日终事件调用方"（R1 薄刀主面）。

    组装最小输入（空持仓/空成交/零净值 + 零值契约快照/指标，上游缺口显式标注）
    驱动 ReviewOrchestrator.run_daily 真实全链：DailyAuditor 五件套审计→日度风险
    摘要→ReportPublisher 归档（默认装配挂 JsonlArchiveSink 落盘 data/reports/）。

    Args:
        trading_date: 交易日（YYYY-MM-DD）。
        orchestrator: 注入编排器（None=build_default_orchestrator 真实装配）。
        portfolio_id: 组合 ID。
        publish: 是否归档发布（False=只算不落库）。

    Returns:
        DailyReviewResult: 日复盘产物（human_attention 非空=人需要看的 FAIL/WARN 项）。

    Raises:
        ValueError: trading_date 非 YYYY-MM-DD。
        InvalidReviewInputError: 编排输入非法。
    """
    parsed = date.fromisoformat(trading_date)  # 非法格式 ValueError 原样上抛
    orch = orchestrator if orchestrator is not None else build_default_orchestrator()
    request = AuditRequest(
        trading_date=parsed,
        portfolio_id=portfolio_id,
        positions_prev=[],
        positions_now=[],
        fills=[],
        nav=0.0,
        consumptions=[],
    )
    result = orch.run_daily(
        trading_date,
        request,
        _build_minimal_snapshot(portfolio_id, trading_date),
        _build_minimal_metrics(portfolio_id, trading_date),
        publish=publish,
    )
    _logger.info(
        "review_trigger 日复盘触发完成: date=%s portfolio=%s archive=%s",
        trading_date,
        portfolio_id,
        result.archived_report.archive_id if result.archived_report else "(未归档)",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 一次性事件入口（零定时器）：python -m zephyr.reporting.review_trigger ..."""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.reporting.review_trigger",
        description="F115 R1 触发链薄刀——日复盘一次性事件触发（真实全链审计→摘要→归档落盘）",
    )
    parser.add_argument("--trading-date", required=True, help="交易日 YYYY-MM-DD")
    parser.add_argument("--portfolio-id", default=_PAPER_PORTFOLIO_ID, help="组合 ID（默认模拟盘）")
    parser.add_argument("--archive-path", default=None, help="归档落盘路径（默认 data/reports/report_archive.jsonl）")
    parser.add_argument("--no-publish", action="store_true", help="只算不归档（dry 面）")
    args = parser.parse_args(argv)

    try:
        orchestrator = (
            build_default_orchestrator(archive_path=Path(args.archive_path)) if args.archive_path is not None else None
        )
        result = trigger_daily_review(
            args.trading_date,
            orchestrator=orchestrator,
            portfolio_id=args.portfolio_id,
            publish=not args.no_publish,
        )
    except (ValueError, InvalidReviewInputError) as exc:
        print(f"[review_trigger] FAIL: {exc}")
        return 1
    archived = result.archived_report
    print(
        f"[review_trigger] OK date={result.trading_date} "
        f"audit={result.audit_report.overall_status.value} "
        f"risk={result.daily_summary.risk_level.value} "
        f"待人看={len(result.human_attention)} "
        f"archive={archived.archive_id if archived else '(未归档)'}"
    )
    for item in result.human_attention:
        print(f"  [ATTENTION] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
