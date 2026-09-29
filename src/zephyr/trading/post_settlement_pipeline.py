# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_trading/blueprint.md
# [MODULE] zephyr.trading.post_settlement_pipeline
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.event_bus(事件触发腿,延迟 import); zephyr.data.trading_calendar(交易日回推,延迟 import)
# [CONSUMERS] 调度层(data scheduler APScheduler / trading work_dag, 54号§2.4缺口#2接线入口); SettlementReconciler; DailyAuditor; boot_hooks._subscribe_eventbus_consumers(F62 事件腿); 装配批经 register_sweep_deps 注入日终 sweep 依赖
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 盘后15:30硬时点(54号§3.3,A股T+1结算); 函数级注册不挂生产APScheduler任务; 对账不一致必告警(不静默); 步骤异常捕获落结果不逃逸调度器; 幂等(同trade_date重跑由下游幂等保证); 事件触发腿 subscribe_eventbus 幂等订阅且同 trade_date 进程内去重(重放零副作用,F62 违宪整改); sweep 依赖未装配=UNWIRED 显式落状态不伪跑
# [MODIFY-GUARD] 54_reconciliation_attribution.md §2.4/§3.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPostSettlementInputError(ZA-TR-0021)
# [TESTS] tests/trading/test_post_settlement_pipeline.py
# [TTL] permanent
"""
D_TRADING — 盘后结算对账调度接线入口（54 号 §2.4 横向缺口 #2）。

"盘后结算对账每日 15:30 自动触发"此前是文档约定（54 号 §7 开放问题：
APScheduler / work_dag / conductor 均无 settlement/reconciliation 任务）。
本模块提供函数级接线入口：
  - build_post_settlement_jobs()：任务规格声明（15:30 cron + 交易日过滤语义），
    供调度层注册——本模块**不实际挂 APScheduler 生产任务**（施工口径：函数级）。
  - run_post_settlement_pipeline()：15:30 触发执行入口，串联
    SettlementReconciler（MOD-TRADING-003）→ DailyAuditor 日终审计，
    对账不一致/步骤异常必告警（不静默），异常捕获落步骤状态不逃逸调度器。

事件触发腿（F62 违宪整改，2026-09-29 夜战 SW5）：
  宪法 §9.3 reconciler 必须事件触发、禁 cron/Timer。SettlementReconciler 现网
  唯一自动触发腿 = Windows 计划任务 ZephyrAlpha_PostSettlement 周时钟（Mon-Fri
  15:30 wall-clock）→ 本模块新增事件链对齐（premarket_checker 同款模式）：
    - 订阅 ``post_settlement.recon.requested``（幂等订阅），处理器跑
      run_daily_end_sweep 幂等日终 sweep：同 trade_date 进程内去重，
      事件重放零副作用；完成后发布 ``post_settlement.recon.swept``。
    - sweep 依赖（QMT 会话/Fills 读取/DailyAuditor 包装）经
      register_sweep_deps() 由装配批注入；未装配 → 状态 UNWIRED
      显式落事件不伪跑（Fail-Silent 禁止语义同 premarket UNWIRED）。
    - boot_hooks._subscribe_eventbus_consumers 统一挂载。
  计划任务退役 = schtasks 任务级变更 = Owner 门位（99_skipped_for_owner #23
  先例），过渡期时钟腿与事件腿并存安全：CLI 幂等 + sweep 去重双保险。

设计真源：54_reconciliation_attribution §2.4 缺口 #2 / §3.3 三层对账 15:30 硬时点。

# [ALGO_FLOW] external: docs/03_modules/_domain_trading/algo_flow/post_settlement_pipeline.yaml
"""

from __future__ import annotations

import datetime
import logging
import threading
from dataclasses import dataclass, field
from typing import Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

#: 盘后结算对账 cron（A 股 T+1：15:00 收盘，15:30 结算单就绪硬时点——54 号 §3.3）
POST_SETTLEMENT_CRON: Final[str] = "30 15 * * *"

#: 事件触发腿 topic（F62：请求 / 完成回执，premarket.check.* 同款命名法）
TOPIC_RECON_REQUESTED: Final[str] = "post_settlement.recon.requested"
TOPIC_RECON_SWEPT: Final[str] = "post_settlement.recon.swept"


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


# ── 事件触发腿：幂等日终 sweep（F62 违宪整改，2026-09-29） ─────────────────────


@dataclass(frozen=True)
class SweepDeps:
    """日终 sweep 依赖装配单（装配批构造；None 腿=该步 SKIPPED，语义同流水线）。"""

    reconcile_fn: Callable[[str], object] | None = None
    audit_fn: Callable[[str], object] | None = None
    alert_sink: Callable[[str, str], None] | None = None


_sweep_lock = threading.Lock()
_registered_sweep_deps: SweepDeps | None = None
_sweep_done: dict[str, PostSettlementRunResult] = {}
_subscribed = False
_sweep_handler: Callable[[object], None] | None = None
_MAX_LOOKBACK_DAYS = 14


def register_sweep_deps(deps: SweepDeps | None) -> None:
    """注册/注销日终 sweep 依赖（运行时装配批注入；None=注销回 UNWIRED 态）。"""
    global _registered_sweep_deps
    if deps is not None and not isinstance(deps, SweepDeps):
        raise InvalidPostSettlementInputError(
            "deps 须为 SweepDeps 或 None",
            details={"deps_type": type(deps).__name__},
        )
    with _sweep_lock:
        _registered_sweep_deps = deps


def _resolve_recent_trading_date(today: datetime.date | None = None) -> str:
    """最近交易日回推（含今天，盘后语义；与 run_post_settlement.py CLI 同口径）。"""
    from zephyr.data.trading_calendar import is_trading_day

    day = today or datetime.date.today()
    for _ in range(_MAX_LOOKBACK_DAYS):
        if is_trading_day(day):
            return day.isoformat()
        day -= datetime.timedelta(days=1)
    raise InvalidPostSettlementInputError(
        f"最近 {_MAX_LOOKBACK_DAYS} 天内无交易日（回推基准={day}）——交易日历异常"
    )


def run_daily_end_sweep(
    trade_date: str | None = None,
    *,
    deps: SweepDeps | None = None,
    force: bool = False,
) -> tuple[PostSettlementRunResult, str]:
    """幂等日终 sweep：同 trade_date 进程内去重，重放返回首次结果（零副作用）。

    Args:
        trade_date: 结算日 YYYY-MM-DD；None=最近交易日回推（is_trading_day 同 CLI 口径）。
        deps: 显式依赖；None=取 register_sweep_deps 注册的装配（仍无=UNWIRED 不伪跑）。
        force: True 时忽略去重重跑（审计/修复场景逃生，默认 False）。

    Returns:
        (PostSettlementRunResult, status)，status ∈ OK/REPLAYED/UNWIRED；
        UNWIRED 时结果为全 SKIPPED 占位（流水线未被调用，零副作用）。
    """
    resolved = trade_date or _resolve_recent_trading_date()
    with _sweep_lock:
        if not force and resolved in _sweep_done:
            return _sweep_done[resolved], "REPLAYED"
        effective = deps if deps is not None else _registered_sweep_deps
        if effective is None:
            placeholder = PostSettlementRunResult(
                trade_date=resolved,
                reconcile_status="UNWIRED",
                audit_status="UNWIRED",
                errors=(),
            )
            return placeholder, "UNWIRED"
        result = run_post_settlement_pipeline(
            resolved,
            reconcile_fn=effective.reconcile_fn,
            audit_fn=effective.audit_fn,
            alert_sink=effective.alert_sink,
        )
        _sweep_done[resolved] = result
        return result, "OK"


def reset_sweep_state() -> None:
    """清空进程内去重与装配（测试隔离专用；生产勿调）。

    同时从共享总线退订事件处理器——防跨测试文件残留 handler 叠加双跑。
    """
    global _registered_sweep_deps, _subscribed, _sweep_handler
    with _sweep_lock:
        _registered_sweep_deps = None
        _sweep_done.clear()
        if _sweep_handler is not None:
            try:
                from zephyr.shared.event_bus import bus

                bus.unsubscribe(TOPIC_RECON_REQUESTED, _sweep_handler)
            except Exception:  # noqa: BLE001 —— 测试清理不外抛
                _logger.debug("sweep handler unsubscribe failed (ignored)", exc_info=True)
            _sweep_handler = None
        _subscribed = False


def subscribe_eventbus() -> None:
    """订阅 post_settlement.recon.requested（幂等；boot_hooks 统一调用，F62 事件腿）。"""
    global _subscribed, _sweep_handler
    with _sweep_lock:
        if _subscribed:
            _logger.debug("post_settlement_pipeline already subscribed, skipping (idempotent)")
            return
        _subscribed = True

    from zephyr.shared.event_bus import bus

    def _on_recon_requested(event: object) -> None:
        payload = getattr(event, "payload", None) or {}
        raw_date = payload.get("trade_date")
        try:
            result, status = run_daily_end_sweep(
                raw_date if isinstance(raw_date, str) and raw_date.strip() else None
            )
        except Exception as exc:  # noqa: BLE001 —— 事件处理器异常不逃逸总线
            _logger.error("POST_SETTLEMENT_SWEEP_ERROR trade_date=%s %r", raw_date, exc)
            bus.emit(TOPIC_RECON_SWEPT, {**payload, "status": "ERROR", "error": repr(exc)})
            return
        bus.emit(
            TOPIC_RECON_SWEPT,
            {
                **payload,
                "trade_date": result.trade_date,
                "status": status,
                "reconcile_status": result.reconcile_status,
                "audit_status": result.audit_status,
                "errors": list(result.errors),
            },
        )

    bus.subscribe(TOPIC_RECON_REQUESTED, _on_recon_requested)
    _sweep_handler = _on_recon_requested
    _logger.info("post_settlement_pipeline: subscribed %s (F62 event leg)", TOPIC_RECON_REQUESTED)


__all__ = [
    "POST_SETTLEMENT_CRON",
    "InvalidPostSettlementInputError",
    "PostSettlementJobSpec",
    "PostSettlementRunResult",
    "SweepDeps",
    "build_post_settlement_jobs",
    "register_sweep_deps",
    "reset_sweep_state",
    "run_daily_end_sweep",
    "run_post_settlement_pipeline",
    "subscribe_eventbus",
]
