# [BLUEPRINT] MOD-EX-056 | docs/03_modules/_domain_execution_core/position_reconciler/blueprint.md
# [MODULE] zephyr.ex_core.position_reconciler
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.position; zephyr.ex_core.position_tracker.tracker
# [CONSUMERS] zephyr.ex_core.trading_session; zephyr.governance.adapters.simulation_broker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only数量比较; DriftItem/ReconcileResult frozen不可变; 冻结集每次reconcile全量重算(非累加); on_drift异常不阻断reconcile; reconcile纯读不修改source状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_position_reconciler.py
# [A_module] module_id=MOD-EX-056 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EXECUTION_CORE — 盘中持仓对账器 (Position Reconciler)

定期比对"系统账"（PositionTracker，靠成交回报累计）与"外部账"（Broker 的
get_positions 查询），差异 > tolerance → 告警 + 冻结该标的交易；恢复一致 → 解冻。

设计真源: D:/临时工作区/依赖图/08-D-EX-CORE-执行核心域.md §1 D-EX-CORE-56
蓝图: docs/03_modules/_domain_execution_core/position_reconciler/blueprint.md

核心职责（阶段1）:
  - 双源持仓比对（PositionTracker vs Broker，均通过 PositionSource 协议）
  - 差异检测（逐标的比较 quantity，diff > tolerance 记为 drift）
  - 冻结/解冻管理（有 drift 的标的冻结；恢复一致后解冻）
  - 告警回调（on_drift，解耦告警通道）

阶段2扩展（本次不实现，见蓝图 §3）:
  - 定时调度（每5分钟）/ miniQMT 实盘源 / D-L1 降级 / 对账历史持久化 / 恢复后强制对账 / 现金对账

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 系统账持仓快照（PositionTracker）
#   fields: PositionSnapshot.holdings（symbol→Decimal数量，靠成交回报累计）
#   code: system_source.get_positions() L146；PositionSource协议 L48-55
# - id: I2
#   name: 外部账持仓快照（Broker）
#   fields: PositionSnapshot.holdings（券商 get_positions 查询结果）
#   code: broker_source.get_positions() L147
# - id: I3
#   name: 对账容差 tolerance
#   fields: Decimal，默认0（零容差）
#   code: __init__ L124-136
# 层: 算法
# - id: A1
#   name_zh: ① 双源持仓对账
#   name_en: PositionReconciler.reconcile
#   intro: 逐标的比系统账和外部账数量，差异超容差记drift并冻结该标的
#   desc: 取两源symbol并集 → diff=system_qty-broker_qty → |diff|>tolerance 记 DriftItem → 冻结集全量重算=当前drift标的集（恢复一致即解冻）→ matched=False 触发 on_drift 告警（异常不阻断）
#   inputs: I1 I2 I3
#   outputs: ReconcileResult
#   invariant: Decimal-only数量比较；冻结集每次全量重算非累加；reconcile纯读不改source状态
# - id: A2
#   name_zh: ② 冻结状态管理
#   name_en: is_frozen / frozen_symbols / unfreeze
#   intro: 交易线程下单前查标的是否被冻结，也支持人工手动解冻
#   desc: threading.Lock 保护冻结集读写；unfreeze手动解冻后下次reconcile若仍有drift会重新冻结
#   inputs: A1
#   outputs: bool / frozenset[str]
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: 是否一致+差异项列表+冻结集+本次新增冻结/解冻的不可变结果
#   invariant: frozen 不可变
#   downstream: trading_session（D_EX_CORE）；simulation_broker（D_GOVERNANCE adapters）
# - id: O2
#   name_zh: 冻结标的集
#   name_en: frozen_symbols
#   intro: 有未解决持仓差异的标的集合，下单前检查拦截用
#   downstream: ExecutionEngine 下单前检查（D_EX_CORE域内）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A1 --> O1
# A2 --> O2
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from threading import Lock
from typing import Callable, Protocol

from zephyr.shared.contracts.position import PositionSnapshot

_logger = logging.getLogger(__name__)


class PositionSource(Protocol):
    """持仓数据源协议 — 任何能产出 PositionSnapshot (CTR-006) 的对象。

    PositionTracker 和 SimulationBroker 均已满足此协议（鸭子类型），
    无需显式继承。reconcile() 只读不修改 source 状态。
    """

    def get_positions(self) -> PositionSnapshot: ...


@dataclass(frozen=True)
class DriftItem:
    """单个标的的差异记录（不可变）。

    Attributes:
        symbol: 标的代码
        system_qty: 系统账（PositionTracker）的数量
        broker_qty: 外部账（Broker）的数量
        diff: system_qty - broker_qty
    """

    symbol: str
    system_qty: Decimal
    broker_qty: Decimal
    diff: Decimal


@dataclass(frozen=True)
class ReconcileResult:
    """一次对账的结果（不可变）。

    Attributes:
        timestamp: 对账时刻
        matched: True=两源完全一致（drifts 为空）
        drifts: 差异项元组（空 tuple = 一致）
        frozen_symbols: 对账后仍冻结的标的集（= 当前 drift 标的）
        newly_frozen: 本次新增冻结的标的
        newly_unfrozen: 本次解冻的标的
    """

    timestamp: datetime
    matched: bool
    drifts: tuple[DriftItem, ...]
    frozen_symbols: frozenset[str]
    newly_frozen: frozenset[str]
    newly_unfrozen: frozenset[str]


class PositionReconciler:
    """盘中持仓对账器 (D-EX-CORE-56)。

    定期比对系统账（PositionTracker）与外部账（Broker）的 holdings，
    差异 > tolerance → 冻结该标的 + 触发 on_drift 告警；恢复一致 → 自动解冻。

    Usage:
        tracker = PositionTracker(...)
        broker = SimulationBroker(...)   # 或 miniQMT 适配器（阶段2）
        reconciler = PositionReconciler(
            system_source=tracker,
            broker_source=broker,
            tolerance=Decimal("0"),
            on_drift=lambda r: alert_service.send(r),
        )

        result = reconciler.reconcile()
        if not result.matched:
            # result.drifts, result.frozen_symbols ...
        # 下单前检查
        if reconciler.is_frozen("600000.SH"):
            raise FrozenSymbolError("600000.SH 持仓未对账，禁止交易")

    Thread Safety:
        冻结集读写加 threading.Lock。reconcile() 可在定时线程调用，
        is_frozen() 可在交易线程并发调用。
    """

    def __init__(
        self,
        system_source: PositionSource,
        broker_source: PositionSource,
        tolerance: Decimal = Decimal("0"),
        on_drift: Callable[[ReconcileResult], None] | None = None,
    ) -> None:
        self._system = system_source
        self._broker = broker_source
        self._tolerance = tolerance
        self._on_drift = on_drift
        self._frozen: set[str] = set()
        self._lock = Lock()

    def reconcile(self) -> ReconcileResult:
        """执行一次对账：比较两源 holdings，更新冻结集，返回结果。

        - 取两源 holdings 的 symbol 并集
        - 逐标的: diff = system_qty - broker_qty; abs(diff) > tolerance → DriftItem
        - 冻结集全量重算: = 当前 drift 标的集（有差异即冻结，无差异即解冻）
        - matched=False 时触发 on_drift 回调（异常被 catch + log，不阻断对账）
        """
        system_snap = self._system.get_positions()
        broker_snap = self._broker.get_positions()
        system_h: dict[str, Decimal] = system_snap.holdings
        broker_h: dict[str, Decimal] = broker_snap.holdings

        all_symbols = set(system_h) | set(broker_h)
        drifts: list[DriftItem] = []
        for symbol in all_symbols:
            sys_qty = system_h.get(symbol, Decimal("0"))
            brk_qty = broker_h.get(symbol, Decimal("0"))
            diff = sys_qty - brk_qty
            if abs(diff) > self._tolerance:
                drifts.append(DriftItem(symbol, sys_qty, brk_qty, diff))

        drift_symbols = {d.symbol for d in drifts}
        with self._lock:
            newly_frozen = drift_symbols - self._frozen
            newly_unfrozen = self._frozen - drift_symbols
            # 冻结集全量重算 = 当前 drift 标的（非累加）
            self._frozen = drift_symbols
            current_frozen = frozenset(self._frozen)

        result = ReconcileResult(
            timestamp=datetime.now(UTC),
            matched=len(drifts) == 0,
            drifts=tuple(drifts),
            frozen_symbols=current_frozen,
            newly_frozen=frozenset(newly_frozen),
            newly_unfrozen=frozenset(newly_unfrozen),
        )

        if not result.matched:
            _logger.warning(
                "持仓对账发现差异: drifts=%d newly_frozen=%s newly_unfrozen=%s",
                len(drifts),
                sorted(result.newly_frozen),
                sorted(result.newly_unfrozen),
            )
            if self._on_drift is not None:
                try:
                    self._on_drift(result)
                except Exception:  # noqa: BLE001 — 告警通道故障不阻断对账主流程
                    _logger.exception("on_drift 回调异常（已忽略，不影响对账结果）")

        return result

    def is_frozen(self, symbol: str) -> bool:
        """该标的是否被冻结（有未解决的持仓差异）。供 ExecutionEngine 下单前检查。"""
        with self._lock:
            return symbol in self._frozen

    @property
    def frozen_symbols(self) -> frozenset[str]:
        """当前冻结标的集（只读副本）。"""
        with self._lock:
            return frozenset(self._frozen)

    def unfreeze(self, symbol: str) -> None:
        """手动解冻某标的（人工干预或恢复后强制）。

        注意: 下次 reconcile 若该标的仍有 drift，会重新冻结。
        """
        with self._lock:
            self._frozen.discard(symbol)
        _logger.info("手动解冻标的: %s", symbol)


__all__ = ["PositionSource", "DriftItem", "ReconcileResult", "PositionReconciler"]
