# [BLUEPRINT] MOD-L06-003 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.eod_reconciliation
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.position_reconciler(PositionReconciler/DriftItem 复用不重复实现); zephyr.ex_core.position_tracker.tracker; zephyr.ex_core.order_manager; zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批(盘后 15:30 任务链/日终调度接线)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] Decimal-only金额数量比较; EodReconcileResult frozen不可变; 持仓对账委托PositionReconciler不重复实现; align_to_broker默认False(报告态,dry-run语义); 对齐须显式开启且输入齐备否则Fail-Closed; expire幂等(终态跳过); alert_sink异常吞没不阻断; 同输入必同输出(clock注入)
# [MODIFY-GUARD] 40_execution_broker.md §6.1 gap 10
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EodReconciliationError(ZA-EX-0023)
# [TESTS] tests/ex_core/test_eod_reconciliation.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: trade_date(交易日 YYYY-MM-DD) + broker_cash(券商端资金, 可选) + broker_settled_holdings(券商端日终交割持仓, 可选)
# I2: PositionReconciler(系统账 vs 券商账双源持仓对账, 注入) + OrderManager(未成交订单归档, 注入) + PositionTracker(系统现金/T+1对齐目标, 注入)
# F1: run_eod(trade_date, ...)——盘后全量对账一次执行
# A1: 持仓全量对账——委托 PositionReconciler.reconcile()(差异冻结/解冻语义复用盘中件)
# A2: 资金核对——系统现金(PositionTracker.cash) vs 券商端资金, |diff|>cash_tolerance 记资金差异
# A3: 未成交订单日终转 EXPIRED——OrderManager.expire_open_orders()(交易所日终自动作废的本地台账归档)
# A4: T+1 可用更新——align_to_broker=True 时以券商端交割持仓+资金为权威 rebuild_from_broker(T+1 交割确认后系统账对齐; 默认 False 仅报告不动账)
# O1: EodReconcileResult(positions_matched/cash_diff/expired_order_ids/t1_aligned/matched)——调用方留痕+告警路由
# [/ALGO_FLOW]
"""D_EX_CORE — 盘后全量对账（40 号 §6.1 gap 10 Phase 2，PositionReconciler 扩展）。

40 号 §6.1 gap 10：券商对账单 vs 系统持仓 vs 资金三方核对、T+1 可用更新、
未成交订单日终转 EXPIRED。查重分工：交易/持仓/资金三方流水级收口（含费用
逐笔+台账跟进）已由 D_TRADING ThreeWayReconEngine（MOD-TRADING-013，
production）承载，本件不重复实现流水级匹配——本件是执行域账户级日终对账：

  | 步骤 | 语义 | 实现 |
  |---|---|---|
  | ① 持仓全量对账 | 系统账 vs 券商账日终快照 | 委托 PositionReconciler（盘中件复用） |
  | ② 资金核对 | 系统现金 vs 券商端资金，容差比对 | 本件（账户级） |
  | ③ 未成交订单归档 | 日终未成交委托转 EXPIRED | OrderManager.expire_open_orders |
  | ④ T+1 可用更新 | 交割确认后以券商为权威对齐系统账 | rebuild_from_broker（显式开启） |

工程裁定：默认报告态（dry-run 语义）——④以券商为准动账属资金安全操作，
须装配层显式 align_to_broker=True 且券商端交割持仓齐备，否则 Fail-Closed。
本模块不挂调度、不接真实券商通道，全部数据源注入。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Callable

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_reconciler import DriftItem, PositionReconciler
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class EodReconciliationError(ZephyrBaseError):
    """盘后全量对账输入非法——空交易日/负容差/对齐输入不齐备等（Fail-Closed）。"""

    error_code = "ZA-EX-0023"


@dataclass(frozen=True)
class EodReconcileResult:
    """一次盘后全量对账结果（不可变）。

    Attributes:
        trade_date: 交易日（YYYY-MM-DD）
        timestamp: 对账执行时刻
        positions_matched: 持仓双源是否一致（委托 PositionReconciler 结果）
        position_drifts: 持仓差异项（空 tuple = 一致）
        frozen_symbols: 对账后仍冻结的标的集
        cash_checked: 是否执行了资金核对（broker_cash 未注入=False）
        cash_system: 系统账现金（未核对为 None）
        cash_broker: 券商端资金（未核对为 None）
        cash_diff: cash_system - cash_broker（未核对为 None）
        cash_matched: 资金是否在容差内一致（未核对为 None）
        expired_order_ids: 本次日终归档 EXPIRED 的订单
        t1_aligned: 是否执行了 T+1 以券商为准对齐（默认 False=仅报告）
        matched: 总体一致（持仓一致 且 资金一致或未核对）
    """

    trade_date: str
    timestamp: datetime
    positions_matched: bool
    position_drifts: tuple[DriftItem, ...]
    frozen_symbols: frozenset[str]
    cash_checked: bool
    cash_system: Decimal | None
    cash_broker: Decimal | None
    cash_diff: Decimal | None
    cash_matched: bool | None
    expired_order_ids: tuple[str, ...]
    t1_aligned: bool
    matched: bool


class EodReconciler:
    """盘后全量对账器（40 号 §6.1 gap 10 Phase 2）。

    Args:
        position_reconciler: 持仓双源对账器（系统账 vs 券商账，注入即生效）。
        order_manager: 订单管理器（日终未成交订单转 EXPIRED；None=跳过归档）。
        position_tracker: 持仓跟踪器（系统现金真源 + T+1 对齐目标；
            None=资金核对与 T+1 对齐不可用，传入 broker_cash 将 Fail-Closed）。
        cash_tolerance: 资金核对容差（Decimal >= 0，默认 0.01 元分位）。
        clock: 时钟注入（测试可控；默认 UTC now）。
        alert_sink: 告警出口 callable(EodReconcileResult)，不一致时触发；
            None=仅日志；异常吞没不阻断。
    """

    def __init__(
        self,
        *,
        position_reconciler: PositionReconciler,
        order_manager: OrderManager | None = None,
        position_tracker: PositionTracker | None = None,
        cash_tolerance: Decimal = Decimal("0.01"),
        clock: Callable[[], datetime] | None = None,
        alert_sink: Callable[[EodReconcileResult], None] | None = None,
    ) -> None:
        if position_reconciler is None:
            raise EodReconciliationError("position_reconciler 缺失（持仓对账唯一委托真源）", details={})
        if not isinstance(cash_tolerance, Decimal) or cash_tolerance < 0:
            raise EodReconciliationError(
                "cash_tolerance 非法（须为非负 Decimal）",
                details={"cash_tolerance": repr(cash_tolerance)},
            )
        self._reconciler = position_reconciler
        self._order_manager = order_manager
        self._tracker = position_tracker
        self._cash_tolerance = cash_tolerance
        self._clock = clock or (lambda: datetime.now(UTC))
        self._alert_sink = alert_sink

    def run_eod(
        self,
        *,
        trade_date: str,
        broker_cash: Decimal | None = None,
        broker_settled_holdings: dict[str, dict[str, object]] | None = None,
        align_to_broker: bool = False,
    ) -> EodReconcileResult:
        """执行一次盘后全量对账（持仓 + 资金 + 订单归档 + 可选 T+1 对齐）。

        Args:
            trade_date: 交易日（YYYY-MM-DD，非空）。
            broker_cash: 券商端日终资金（None=跳过资金核对）。
            broker_settled_holdings: 券商端日终交割持仓（仅 align_to_broker
                时消费，格式同 PositionTracker.rebuild_from_broker）。
            align_to_broker: T+1 可用更新开关——True=以券商端交割持仓+资金
                为权重建仓对齐系统账（资金安全操作，默认 False 仅报告）。

        Raises:
            EodReconciliationError: trade_date 空 / broker_cash 已注入但
                position_tracker 缺失 / align_to_broker 输入不齐备。
        """
        if not trade_date:
            raise EodReconciliationError("trade_date 为空", details={})
        if broker_cash is not None and self._tracker is None:
            raise EodReconciliationError(
                "broker_cash 已注入但 position_tracker 缺失，拒绝资金核对（Fail-Closed 不臆造）",
                details={"trade_date": trade_date},
            )
        if align_to_broker and (broker_settled_holdings is None or self._tracker is None):
            raise EodReconciliationError(
                "align_to_broker 须券商端交割持仓与 position_tracker 齐备（Fail-Closed）",
                details={
                    "trade_date": trade_date,
                    "has_holdings": broker_settled_holdings is not None,
                    "has_tracker": self._tracker is not None,
                },
            )

        # ① 持仓全量对账（委托 PositionReconciler，冻结/解冻语义复用）
        position_result = self._reconciler.reconcile()

        # ② 资金核对（系统账现金 vs 券商端资金，账户级）
        cash_checked = broker_cash is not None
        cash_system: Decimal | None = None
        cash_diff: Decimal | None = None
        cash_matched: bool | None = None
        if cash_checked:
            cash_system = self._tracker.cash  # type: ignore[union-attr] — 上方已 Fail-Closed
            cash_diff = cash_system - broker_cash
            cash_matched = abs(cash_diff) <= self._cash_tolerance
            if not cash_matched:
                _logger.warning(
                    "盘后资金核对差异: trade_date=%s system=%s broker=%s diff=%s",
                    trade_date,
                    cash_system,
                    broker_cash,
                    cash_diff,
                )

        # ③ 未成交订单日终转 EXPIRED（交易所日终自动作废的本地台账归档）
        expired_order_ids: tuple[str, ...] = ()
        if self._order_manager is not None:
            expired = self._order_manager.expire_open_orders()
            expired_order_ids = tuple(o.order_id for o in expired)
            if expired_order_ids:
                _logger.info(
                    "日终未成交订单归档 EXPIRED: trade_date=%s count=%d",
                    trade_date,
                    len(expired_order_ids),
                )

        # ④ T+1 可用更新（显式开启才动账：交割确认后以券商为权威对齐系统账）
        t1_aligned = False
        if align_to_broker:
            self._tracker.rebuild_from_broker(  # type: ignore[union-attr] — 上方已 Fail-Closed
                broker_settled_holdings,  # type: ignore[arg-type]
                cash=broker_cash,
            )
            t1_aligned = True
            _logger.info(
                "T+1 可用更新（以券商为准对齐）: trade_date=%s symbols=%d",
                trade_date,
                len(broker_settled_holdings or {}),
            )

        matched = position_result.matched and cash_matched is not False
        result = EodReconcileResult(
            trade_date=trade_date,
            timestamp=self._clock(),
            positions_matched=position_result.matched,
            position_drifts=position_result.drifts,
            frozen_symbols=position_result.frozen_symbols,
            cash_checked=cash_checked,
            cash_system=cash_system,
            cash_broker=broker_cash,
            cash_diff=cash_diff,
            cash_matched=cash_matched,
            expired_order_ids=expired_order_ids,
            t1_aligned=t1_aligned,
            matched=matched,
        )
        if not matched:
            _logger.warning(
                "盘后全量对账不一致: trade_date=%s positions_matched=%s cash_matched=%s",
                trade_date,
                position_result.matched,
                cash_matched,
            )
            if self._alert_sink is not None:
                try:
                    self._alert_sink(result)
                except Exception:  # noqa: BLE001 — 告警 best-effort 不阻断对账
                    _logger.exception("alert_sink 调用失败（已吞没）")
        return result


__all__ = [
    "EodReconciliationError",
    "EodReconcileResult",
    "EodReconciler",
]
