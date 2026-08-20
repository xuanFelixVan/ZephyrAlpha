# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_trading/blueprint.md
# [MODULE] zephyr.trading.post_settlement_pipeline
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 调度层(data scheduler APScheduler / trading work_dag, 54号§2.4缺口#2接线入口); SettlementReconciler; DailyAuditor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 盘后15:30硬时点(54号§3.3,A股T+1结算); 函数级注册不挂生产APScheduler任务; 对账不一致必告警(不静默); 步骤异常捕获落结果不逃逸调度器; 幂等(同trade_date重跑由下游幂等保证)
# [MODIFY-GUARD] 54_reconciliation_attribution.md §2.4/§3.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPostSettlementInputError(ZA-TR-0021)
# [TESTS] tests/trading/test_post_settlement_pipeline.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: trade_date(结算日 YYYY-MM-DD) + reconcile_fn(结算对账可调用, 注入) + audit_fn(日终审计可调用, 可选注入) + alert_sink(告警出口, 可选注入)
# F1: build_post_settlement_jobs()——返回盘后 15:30 任务规格(cron=30 15 * * *, trading_day_only=True), 调度层按规格注册(本模块不实际挂任务)
# F2: run_post_settlement_pipeline(trade_date, ...)——15:30 触发入口: 结算对账→(不一致告警)→日终审计, 逐步捕获异常落步骤状态
# A1: 对账不一致/步骤异常→alert_sink(trade_date, message) 告警; alert_sink 缺失仅日志(不阻断链路)
# O1: PostSettlementRunResult(trade_date/reconcile_status/audit_status/errors)——调度层与复盘链路消费
# [/ALGO_FLOW]
"""D_TRADING — 盘后结算对账调度接线入口（54 号 §2.4 横向缺口 #2）。

"盘后结算对账每日 15:30 自动触发"此前是文档约定（54 号 §7 开放问题：
APScheduler / work_dag / conductor 均无 settlement/reconciliation 任务）。
本模块提供函数级接线入口：
  - build_post_settlement_jobs()：任务规格声明（15:30 cron + 交易日过滤语义），
    供调度层注册——本模块**不实际挂 APScheduler 生产任务**（施工口径：函数级）。
  - run_post_settlement_pipeline()：15:30 触发执行入口，串联
    SettlementReconciler（MOD-TRADING-003）→ DailyAuditor 日终审计，
    对账不一致/步骤异常必告警（不静默），异常捕获落步骤状态不逃逸调度器。

设计真源：54_reconciliation_attribution §2.4 缺口 #2 / §3.3 三层对账 15:30 硬时点。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

#: 盘后结算对账 cron（A 股 T+1：15:00 收盘，15:30 结算单就绪硬时点——54 号 §3.3）
POST_SETTLEMENT_CRON: Final[str] = "30 15 * * *"


class InvalidPostSettlementInputError(ZephyrBaseError):
    """盘后流水线输入非法——空结算日/缺 reconcile_fn 等。"""

    error_code = "ZA-TR-0021"


@dataclass(frozen=True)
class PostSettlementJobSpec:
    """盘后任务调度规格（声明式；调度层据此注册 cron 任务）。"""

    job_id: str
    cron_expression: str
    trading_day_only: bool
    entrypoint: str  # 调度层回调入口（dotted path）
    description: str
    schema_version: str = "1.0"


@dataclass(frozen=True)
class PostSettlementRunResult:
    """一次盘后流水线执行结果。"""

    trade_date: str
    reconcile_status: str  # OK / DRIFT / ERROR / SKIPPED
    audit_status: str  # OK / ERROR / SKIPPED
    errors: tuple[str, ...] = field(default_factory=tuple)
    schema_version: str = "1.0"


def build_post_settlement_jobs() -> tuple[PostSettlementJobSpec, ...]:
    """盘后 15:30 任务规格（调度注册函数级入口）。

    返回结算对账 + 日终审计两个任务规格；调度层（data scheduler APScheduler /
    trading work_dag）按规格注册并注入实例化 callable。trading_day_only=True
    语义：非 A 股交易日由调度层跳过（复用 data scheduler 既有 trading_day 过滤）。
    """
    return (
        PostSettlementJobSpec(
            job_id="post_settlement_reconcile",
            cron_expression=POST_SETTLEMENT_CRON,
            trading_day_only=True,
            entrypoint="zephyr.trading.post_settlement_pipeline.run_post_settlement_pipeline",
            description="盘后 15:30 结算对账（SettlementReconciler，MOD-TRADING-003；54 号 §3.3 三层对账硬时点）",
        ),
        PostSettlementJobSpec(
            job_id="post_settlement_daily_audit",
            cron_expression=POST_SETTLEMENT_CRON,
            trading_day_only=True,
            entrypoint="zephyr.trading.post_settlement_pipeline.run_post_settlement_pipeline",
            description="盘后 15:30 日终审计（DailyAuditor 五件套，55 号 §3.1C；随对账同窗口串联）",
        ),
    )


def run_post_settlement_pipeline(
    trade_date: str,
    *,
    reconcile_fn: Callable[[str], object] | None = None,
    audit_fn: Callable[[str], object] | None = None,
    alert_sink: Callable[[str, str], None] | None = None,
) -> PostSettlementRunResult:
    """盘后 15:30 触发执行入口（对账 → 审计串联）。

    Args:
        trade_date: 结算日（YYYY-MM-DD）。
        reconcile_fn: 结算对账可调用（trade_date → ReconciliationResult 或含
            matched/drifts 属性的对象）；None=该步 SKIPPED。
        audit_fn: 日终审计可调用（trade_date → DailyAuditReport）；None=SKIPPED。
        alert_sink: 告警出口 callable(trade_date, message)；None=仅日志。

    Returns:
        PostSettlementRunResult：各步骤状态 + 异常清单。
        步骤异常被捕获落 errors + alert（盘后任务异常不逃逸调度器）。
    """
    if not trade_date or not trade_date.strip():
        raise InvalidPostSettlementInputError(
            "trade_date 不能为空（YYYY-MM-DD）",
            details={"trade_date": trade_date},
        )

    errors: list[str] = []

    def _alert(message: str) -> None:
        _logger.error("盘后流水线告警: date=%s %s", trade_date, message)
        if alert_sink is not None:
            try:
                alert_sink(trade_date, message)
            except Exception:  # noqa: BLE001 —— 告警出口失败不阻断主链路
                _logger.exception("alert_sink 调用失败（已吞没，不阻断）: date=%s", trade_date)

    # ── 步骤 1：结算对账 ──
    reconcile_status = "SKIPPED"
    if reconcile_fn is not None:
        try:
            result = reconcile_fn(trade_date)
            matched = getattr(result, "matched", None)
            if matched is False:
                reconcile_status = "DRIFT"
                drift_count = len(getattr(result, "drifts", ()) or ())
                _alert(f"结算对账不一致：drift {drift_count} 笔（54 号 §3.3 差异即对账误差）")
            else:
                reconcile_status = "OK"
        except Exception as exc:  # noqa: BLE001 —— 捕获落状态，不逃逸调度器
            reconcile_status = "ERROR"
            errors.append(f"reconcile_fn 异常: {exc!r}")
            _alert(f"结算对账步骤异常：{exc!r}")

    # ── 步骤 2：日终审计 ──
    audit_status = "SKIPPED"
    if audit_fn is not None:
        try:
            audit_fn(trade_date)
            audit_status = "OK"
        except Exception as exc:  # noqa: BLE001
            audit_status = "ERROR"
            errors.append(f"audit_fn 异常: {exc!r}")
            _alert(f"日终审计步骤异常：{exc!r}")

    return PostSettlementRunResult(
        trade_date=trade_date,
        reconcile_status=reconcile_status,
        audit_status=audit_status,
        errors=tuple(errors),
    )


__all__ = [
    "POST_SETTLEMENT_CRON",
    "InvalidPostSettlementInputError",
    "PostSettlementJobSpec",
    "PostSettlementRunResult",
    "build_post_settlement_jobs",
    "run_post_settlement_pipeline",
]
