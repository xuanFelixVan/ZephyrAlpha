# [BLUEPRINT] MOD-EX-002 | docs/03_modules/_domain_execution_core/position_tracker/blueprint.md
# [MODULE] zephyr.ex_core.position_tracker.tracker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.position; zephyr.shared.contracts.enums.order_enums; zephyr.shared.state_store
# [CONSUMERS] zephyr.governance.adapters.simulation_broker; zephyr.ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额计算; PositionSnapshot frozen不可变; apply_fill需显式side(Fill契约无side字段); 配置dedup_store时同一fill_id最多入账一次(at-most-once)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_position_tracker.py; tests/ex_core/test_fill_id_dedup_persistence.py
# [A_module] module_id=MOD-EX-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EXECUTION_CORE — Position Tracker (持仓跟踪器)

从 SimulationBroker 拆出的独立持仓跟踪模块。每笔成交（Fill）驱动持仓更新，
任何时刻可产出 PositionSnapshot（CTR-006）供 D-RISK/D-PORTFOLIO/D-REPORTING 消费。

设计真源: D:/临时工作区/依赖图/08-D-EX-CORE-执行核心域.md §1 D-EX-CORE-04
蓝图: docs/03_modules/_domain_execution_core/position_tracker/blueprint.md

核心职责（阶段1）:
  - 维护 symbol → (quantity, avg_cost) 持仓状态
  - 维护 cash 余额（买入扣、卖出加）
  - 从 Fill 回调更新持仓（平均成本法）
  - 产出 PositionSnapshot (CTR-006)

阶段2扩展（本次不实现，见蓝图 §4）:
  - SQLite 持久化 / Redis 实时更新 / T+1 锁定 / FIFO-LIFO / unrealized_pnl

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill + 买卖方向 side
#   fields: fill(symbol/fill_price/filled_quantity/commission) + OrderSide（Fill契约无side字段需显式传入）
#   code: apply_fill(fill, side) L103
# - id: I2
#   name: 初始现金 initial_cash
#   fields: Decimal，默认 1000000；另有 portfolio_id
#   code: __init__ L70-80
# 层: 算法
# - id: A1
#   name_zh: ① 平均成本法持仓更新
#   name_en: PositionTracker.apply_fill
#   intro: 每笔成交按买卖方向更新持仓数量、平均成本和现金余额
#   desc: BUY: new_avg=(old_avg×old_qty+fill_price×fill_qty)/new_qty，cash-=qty×price+commission；SELL: qty减、avg_cost不变（成本锁定盈亏体现在现金端），cash+=qty×price-commission；threading.Lock保护；阶段1不做fill_id幂等去重
#   inputs: I1 I2
#   outputs: 内部持仓状态（holdings/avg_costs/cash）
#   invariant: Decimal-only金额计算；apply_fill需显式side
# - id: A2
#   name_zh: ② 持仓快照产出
#   name_en: PositionTracker.get_positions
#   intro: 把内部持仓状态打包成CTR-006不可变快照供跨域消费
#   desc: market_value=qty×avg_cost（阶段1用成本价非实时价）→ 过滤零持仓标的 → gross_leverage=total_mv/initial_cash → 构造 frozen PositionSnapshot
#   inputs: A1
#   outputs: PositionSnapshot（CTR-006）
#   invariant: PositionSnapshot frozen不可变
# 层: 输出
# - id: O1
#   name_zh: 持仓快照 PositionSnapshot（CTR-006）
#   name_en: PositionSnapshot
#   intro: 现金+持仓数量+市值+总杠杆的组合级快照，回测/模拟/实盘三态统一
#   invariant: frozen 不可变；零持仓标的不出现在holdings中
#   downstream: simulation_broker（D_GOVERNANCE adapters）；trading_session（D_EX_CORE）；D_RISK/D_REPORTING/D_ML（CTR-006消费域）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from threading import Lock

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.state_store import AppendOnlyDedupSet

_logger = logging.getLogger(__name__)


class PositionTracker:
    """持仓跟踪器 — Fill 回调驱动，产出 PositionSnapshot (CTR-006)。

    从 SimulationBroker 拆出，为回测/模拟/实盘三态提供统一的持仓跟踪逻辑。

    Usage:
        tracker = PositionTracker(initial_cash=Decimal("1000000"))

        # 应用成交（需显式传入 side，因 Fill 契约无 side 字段）
        tracker.apply_fill(fill, OrderSide.BUY)

        # 产出持仓快照
        snapshot = tracker.get_positions()
        # snapshot.holdings, snapshot.cash, snapshot.total_market_value ...

    Thread Safety:
        内部加 threading.Lock 保护持仓状态。可在多线程环境安全调用
        apply_fill / get_positions（如 TradingSession 定时调仓 + fill 回调并发）。
    """

    def __init__(
        self,
        initial_cash: Decimal = Decimal("1000000"),
        portfolio_id: str = "position_tracker",
        dedup_store: AppendOnlyDedupSet | None = None,
    ) -> None:
        """初始化持仓跟踪器。

        Args:
            initial_cash: 初始现金。
            portfolio_id: 组合标识。
            dedup_store: fill_id 持久化去重集（#ARCH-QUANT-002，Qwen P0-2①）。
                提供时 apply_fill 幂等（同一 fill_id 最多入账一次，重启存活），
                Saga 补偿 rollback-{fill_id} 确定性 ID 配本去重集实现真幂等。
                None=不去重（既有行为，幂等性由调用方保证）。
        """
        self._initial_cash = initial_cash
        self._cash = initial_cash
        self._portfolio_id = portfolio_id
        self._holdings: dict[str, Decimal] = {}
        self._avg_costs: dict[str, Decimal] = {}
        self._dedup_store = dedup_store
        self._lock = Lock()

    # ── Stage 4 公共化（只读 properties）──

    @property
    def cash(self) -> Decimal:
        """只读：当前现金余额。"""
        return self._cash

    @property
    def holdings(self) -> dict[str, Decimal]:
        """只读：持仓数量快照（返回副本，调用方修改不影响内部状态）。"""
        with self._lock:
            return dict(self._holdings)

    @property
    def avg_costs(self) -> dict[str, Decimal]:
        """只读：平均成本快照（返回副本）。"""
        with self._lock:
            return dict(self._avg_costs)

    # ── 核心方法 ──

    def apply_fill(self, fill: Fill, side: OrderSide) -> None:
        """应用成交——更新持仓数量、平均成本、现金。

        Args:
            fill: 成交回报（CTR-005，不可变）。使用 fill_price/filled_quantity/commission。
            side: 买卖方向（Fill 契约无 side 字段，需调用方从 Order 传入）。

        Note:
            配置 dedup_store 时同一 fill_id 最多入账一次（at-most-once，
            去重登记先行：重复/重放直接跳过，含重启后重放与 Saga 补偿
            rollback-{fill_id} 重试）；未配置时保持既有行为（不去重，
            幂等性由调用方保证）。
        """
        with self._lock:
            if self._dedup_store is not None and not self._dedup_store.add(fill.fill_id):
                _logger.warning(
                    "apply_fill 幂等拦截: fill_id=%s 已入账, 跳过 symbol=%s side=%s",
                    fill.fill_id,
                    fill.symbol,
                    side,
                )
                return

            symbol = fill.symbol
            fill_qty = fill.filled_quantity
            fill_price = fill.fill_price
            commission = fill.commission

            current_qty = self._holdings.get(symbol, Decimal("0"))
            current_avg = self._avg_costs.get(symbol, Decimal("0"))

            if side == OrderSide.BUY:
                new_qty = current_qty + fill_qty
                if new_qty != 0:
                    total_cost = (current_avg * current_qty) + (fill_price * fill_qty)
                    self._avg_costs[symbol] = total_cost / new_qty
                self._holdings[symbol] = new_qty
                self._cash -= fill_qty * fill_price + commission
            else:
                # SELL
                new_qty = current_qty - fill_qty
                # 卖出：avg_cost 不变（成本已锁定），盈亏在现金端实现
                if new_qty == 0:
                    self._avg_costs[symbol] = Decimal("0")
                # new_qty < 0（空头）时保留原 avg_cost
                self._holdings[symbol] = new_qty
                self._cash += fill_qty * fill_price - commission

            _logger.debug(
                "apply_fill: symbol=%s side=%s qty=%s price=%s cash=%s holding=%s",
                symbol,
                side,
                fill_qty,
                fill_price,
                self._cash,
                self._holdings[symbol],
            )

    def rebuild_from_broker(
        self,
        holdings: dict[str, dict[str, object]],
        today_fills: Iterable[Fill] = (),
        *,
        cash: Decimal | None = None,
    ) -> None:
        """以券商为准全量重建持仓账（Crash-only 启动恢复路径，#ARCH-QUANT-002）。

        供 AI-RWIRE-001 启动流程消费：进程重启后先调本方法以券商持仓
        全量重建 PositionTracker（Qwen P0-2②：以券商为准，防"空仓错觉下
        重复建仓"），重建完成前调用方应禁止下单（Fail-Closed 由调用方保证）。

        Args:
            holdings: 券商实时持仓，symbol → {"qty": int|float|str|Decimal,
                "avg_cost": float|str|Decimal}。qty==0 的标的不入账；
                此映射是重建后的唯一真源（覆盖式重建，清空既有持仓账）。
            today_fills: 当日已成交 Fill 序列（可选）。仅将其 fill_id 登记入
                持久化去重集（防重启后重放重复记账），不再改动持仓
                （持仓以 holdings 为准）；未配置 dedup_store 时忽略。
            cash: 券商资金余额（可选）。None=保留当前现金账不变。
        """
        with self._lock:
            self._holdings.clear()
            self._avg_costs.clear()

            for symbol, info in holdings.items():
                qty = Decimal(str(info.get("qty", 0)))
                if qty == 0:
                    continue
                avg_cost = Decimal(str(info.get("avg_cost", 0)))
                self._holdings[symbol] = qty
                self._avg_costs[symbol] = avg_cost

            if cash is not None:
                self._cash = cash

            fills = list(today_fills)
            registered_fills = 0
            if self._dedup_store is not None:
                for fill in fills:
                    if self._dedup_store.add(fill.fill_id):
                        registered_fills += 1

            _logger.info(
                "rebuild_from_broker: 以券商为准重建完成 holdings=%d cash=%s today_fills登记=%d/%d",
                len(self._holdings),
                self._cash,
                registered_fills,
                len(fills),
            )

    def get_positions(self) -> PositionSnapshot:
        """产出持仓快照（CTR-006），不可变 frozen dataclass。

        market_value 计算：阶段1用 qty × avg_cost（与 SimulationBroker 一致）。
        阶段2将改为 qty × 实时价（需 PriceProvider 注入）。
        """
        with self._lock:
            market_values: dict[str, Decimal] = {}
            for symbol, qty in self._holdings.items():
                avg_price = self._avg_costs.get(symbol, Decimal("0"))
                market_values[symbol] = qty * avg_price if avg_price > 0 else Decimal("0")

            total_mv = sum(market_values.values(), Decimal("0"))
            # 过滤零持仓（qty=0 的标的不出现在 holdings 中）
            active_holdings = {s: q for s, q in self._holdings.items() if q != 0}
            active_mv = {s: mv for s, mv in market_values.items() if self._holdings.get(s, Decimal("0")) != 0}

            return PositionSnapshot(
                as_of_timestamp=datetime.now(UTC),
                portfolio_id=self._portfolio_id,
                idempotency_key=str(uuid.uuid4()),
                cash=self._cash,
                gross_leverage=float(total_mv / self._initial_cash) if self._initial_cash > 0 else 0.0,
                holdings=active_holdings,
                market_values=active_mv,
                total_market_value=total_mv,
            )

    def reset(self) -> None:
        """重置到初始状态（测试用）。"""
        with self._lock:
            self._cash = self._initial_cash
            self._holdings.clear()
            self._avg_costs.clear()


__all__ = ["PositionTracker"]
