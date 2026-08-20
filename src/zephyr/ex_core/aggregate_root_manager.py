# [BLUEPRINT] MOD-EX-049 | docs/03_modules/_domain_execution_core/aggregate_root_manager/blueprint.md
# [MODULE] zephyr.ex_core.aggregate_root_manager
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.fill_handler; zephyr.ex_core.position_tracker.tracker; zephyr.ex_core.repository_interface; zephyr.shared.contracts.order; zephyr.shared.contracts.fill; zephyr.shared.contracts.position
# [CONSUMERS] D_EX_CORE域内模块 ; Saga编排器 (阶段2集成)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Facade不含业务计算; process_fill调用顺序固定(FillHandler→PositionTracker→repo.save); OrderState不可变
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AggregateManagerError(ZA-EX-049-01)
# [TESTS] tests/ex_core/test_aggregate_root_manager.py
# [A_module] module_id=MOD-EX-049 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(Facade模式天然聚合下游API),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""

D_EX_CORE — Aggregate Root Manager (执行域聚合根管理器)

执行域的总调度台——把订单仓储、成交处理、持仓跟踪三个独立组件拧成一股绳。
作为 Facade（门面模式）整合 FillHandler、PositionTracker 和 Repository，
提供统一的执行域操作入口。

上层（Saga编排器/Fill处理器）只需调一个方法，它就自动完成
"更新订单状态→记录成交→更新持仓→持久化"的全链路操作。

核心定位：
  - 不替代 FillHandler/PositionTracker/Repository 的任何逻辑
  - 只负责"调用顺序 + 持久化边界"，不包含业务计算
  - 所有组件通过构造函数注入，可替换为 mock（便于测试/扩展）

设计真源: D-EX-CORE-49 "Order/Position生命周期协调层"
蓝图: docs/03_modules/_domain_execution_core/aggregate_root_manager/blueprint.md
SSoT: depgraph MOD-EX-049

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 订单创建参数
#   fields: symbol + strategy_id + side + order_type + quantity(Decimal) + limit_price
#   code: create_order() L157-165
# - id: I2
#   name: 成交回报 Fill + 委托订单 Order
#   fields: fill(fill_id/fill_price/filled_quantity/commission) + order(就地更新)
#   code: process_fill(fill, order) L203
# 层: 算法
# - id: A1
#   name_zh: ① 订单创建+持久化
#   name_en: ExecutionAggregateManager.create_order
#   intro: 生成UUID订单号构造PENDING状态Order并写入仓储
#   desc: uuid4生成order_id → 构造Order(PENDING) → order_repo.save 持久化
#   inputs: I1
#   outputs: 新建 Order（状态PENDING，已持久化）
#   invariant: quantity 全程 Decimal 禁止 float
# - id: A2
#   name_zh: ② 成交全链路编排
#   name_en: ExecutionAggregateManager.process_fill
#   intro: 一笔成交自动完成更新订单成交状态、更新持仓、持久化三步
#   desc: 固定顺序 FillHandler.process_fill(累积/均价/状态) → PositionTracker.apply_fill(持仓/现金) → order_repo.save
#   inputs: I2
#   outputs: FillSummary 成交汇总
#   invariant: 调用顺序固定 FillHandler→PositionTracker→repo.save；Facade不含业务计算
# - id: A3
#   name_zh: ③ 状态查询与快照持久化
#   name_en: get_order_state / save_position_snapshot
#   intro: 一次性查订单完整状态，或把当前持仓快照写入快照仓储
#   desc: repo.get + fill_handler.get_summary 组装 OrderState；未注入快照仓储则抛 AggregateManagerError
#   inputs: A1 A2
#   outputs: OrderState / PositionSnapshot
# 层: 输出
# - id: O1
#   name_zh: 订单及完整状态 Order/OrderState
#   name_en: Order / OrderState
#   intro: 订单本体加成交汇总的不可变快照，供上层一次性查询
#   downstream: D_EX_CORE域内模块；Saga编排器 MOD-EX-057（阶段2集成）
# - id: O2
#   name_zh: 成交汇总 FillSummary
#   name_en: FillSummary
#   intro: 总量/已成交/剩余/均价/笔数/佣金的成交快照
#   invariant: frozen 不可变
#   downstream: D_EX_CORE域内模块
# - id: O3
#   name_zh: 持仓快照 PositionSnapshot
#   name_en: PositionSnapshot
#   intro: CTR-006持仓契约快照，可持久化到快照仓储
#   downstream: D_RISK / D_REPORTING / D_ML（CTR-006消费域）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A1 --> O1
# A2 --> O1
# A2 --> O2
# A3 --> O1
# A3 --> O3
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final

from zephyr.ex_core.fill_handler import FillHandler, FillSummary
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.repository_interface import (
    OrderRepository,
    PositionSnapshotRepository,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "OrderState",
    "ExecutionAggregateManager",
    "AggregateManagerError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AggregateManagerError(ZephyrBaseError):
    """聚合根管理器异常基类。"""

    error_code = "ZA-EX-049-01"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OrderState:
    """订单完整状态——不可变快照。

    聚合订单本体 (Order) 与成交汇总 (FillSummary)，供上层一次性查询。
    注意 Order 本身是可变对象（CTR-004 frozen=false），OrderState 的
    frozen 仅约束字段引用不可重新赋值，不约束 Order 内部状态。
    """

    order: Order
    fill_summary: FillSummary | None


# ──────────────────────────────────────────────────────────────────────────────
# ExecutionAggregateManager
# ──────────────────────────────────────────────────────────────────────────────


class ExecutionAggregateManager:
    """执行域聚合根管理器——协调 Order/Position 生命周期。

    作为 Facade（门面模式）整合 FillHandler、PositionTracker 和 Repository，
    提供统一的执行域操作入口。

    用法::

        mgr = ExecutionAggregateManager(
            order_repo=InMemoryOrderRepository(),
            position_tracker=PositionTracker(initial_cash=Decimal("1000000")),
        )

        # 创建订单（自动持久化）
        order = mgr.create_order("600000", "strat-1", OrderSide.BUY,
                                 OrderType.LIMIT, Decimal("100"), Decimal("10.00"))

        # 订单提交到券商后（status→SUBMITTED，由上层 OrderManager 负责）
        # 收到成交回报时调用全链路处理
        mgr.process_fill(fill, order)
        # → FillHandler 更新成交累积/均价/状态
        # → PositionTracker 更新持仓/现金
        # → order_repo 持久化

        # 一次性查询订单完整状态
        state = mgr.get_order_state(order.order_id)
        # state.order, state.fill_summary

    职责边界（阶段1）:
      - create_order: 构造 Order + 持久化
      - process_fill: FillHandler→PositionTracker→repo.save 全链路
      - 查询: get_order/get_order_state/get_position_snapshot/get_open_orders
      - 持仓快照持久化: save_position_snapshot（需注入 position_snapshot_repo）

    不包含（阶段2扩展）:
      - submit_order（提交到券商，属 OrderManager 职责）
      - 事务/锁（多线程并发场景）
      - 跨聚合根的事件发布
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        position_tracker: PositionTracker,
        fill_handler: FillHandler | None = None,
        position_snapshot_repo: PositionSnapshotRepository | None = None,
    ) -> None:
        self._order_repo = order_repo
        self._position_tracker = position_tracker
        # 不注入则内部创建独立实例（避免与外部共享状态）
        self._fill_handler = fill_handler or FillHandler()
        self._position_snapshot_repo = position_snapshot_repo

    # ── 订单创建 ──────────────────────────────────────────────────────────

    def create_order(
        self,
        symbol: str,
        strategy_id: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        limit_price: Decimal | None = None,
    ) -> Order:
        """创建订单并持久化到仓储。

        Args:
            symbol: 标的代码。
            strategy_id: 策略 ID。
            side: 买卖方向。
            order_type: 订单类型（LIMIT/MARKET）。
            quantity: 委托数量（Decimal，禁止 float）。
            limit_price: 限价（限价单必填，市价单为 None）。

        Returns:
            新建的 Order 对象（状态 PENDING，已持久化到仓储）。
        """
        order_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        order = Order(
            order_id=order_id,
            symbol=symbol,
            strategy_id=strategy_id,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
            idempotency_key=str(uuid.uuid4()),
        )
        self._order_repo.save(order)
        logger.info(
            "订单创建: order_id=%s symbol=%s side=%s qty=%s type=%s",
            order_id,
            symbol,
            side,
            quantity,
            order_type,
        )
        return order

    # ── 成交全链路 ──────────────────────────────────────────────────────────

    def process_fill(self, fill: Fill, order: Order) -> FillSummary:
        """成交全链路处理——FillHandler→PositionTracker→repo.save。

        调用顺序固定（不变量）：
          1. FillHandler.process_fill — 更新订单成交累积/加权均价/状态
          2. PositionTracker.apply_fill — 更新持仓数量/均价/现金
          3. order_repo.save — 持久化更新后的订单

        注意：order 需处于可接受成交的状态（SUBMITTED/PARTIAL）。
        PENDING 状态的订单，FillHandler 仅记警告不抛异常，状态不变
        但成交数量仍会累积（详见 FillHandler._try_transition）。

        Args:
            fill: 成交回报（CTR-005，不可变）。
            order: 对应订单（CTR-004，将被 FillHandler 就地更新）。
                需与 fill.order_id 一致，否则 FillHandler 抛 OrderNotFoundError。

        Returns:
            FillSummary: 成交汇总快照。
        """
        # 1. 成交处理（更新 order 的 filled_quantity/avg_fill_price/status）
        summary = self._fill_handler.process_fill(fill, order)

        # 2. 持仓更新（需 order.side，因 Fill 契约无 side 字段）
        self._position_tracker.apply_fill(fill, order.side)

        # 3. 持久化订单
        self._order_repo.save(order)

        logger.info(
            "成交全链路完成: order_id=%s filled=%s/%s status=%s",
            order.order_id,
            order.filled_quantity,
            order.quantity,
            order.status,
        )
        return summary

    # ── 查询 ──────────────────────────────────────────────────────────────

    def get_order(self, order_id: str) -> Order | None:
        """按 order_id 查询订单，不存在返回 None。"""
        return self._order_repo.get(order_id)

    def get_order_state(self, order_id: str) -> OrderState | None:
        """获取订单完整状态——order + fill_summary。

        Args:
            order_id: 订单 ID。

        Returns:
            OrderState（不可变），订单不存在返回 None。
        """
        order = self._order_repo.get(order_id)
        if order is None:
            return None
        fill_summary = self._fill_handler.get_summary(order_id)
        return OrderState(order=order, fill_summary=fill_summary)

    def get_open_orders(self) -> list[Order]:
        """查询所有开放订单（PENDING/SUBMITTED/PARTIAL）。"""
        return self._order_repo.get_open_orders()

    def get_position_snapshot(self) -> PositionSnapshot:
        """获取当前持仓快照（委托 PositionTracker，CTR-006）。"""
        return self._position_tracker.get_positions()

    # ── 持仓快照持久化 ──────────────────────────────────────────────────────

    def save_position_snapshot(self) -> PositionSnapshot:
        """持久化当前持仓快照。

        如未注入 position_snapshot_repo，抛 AggregateManagerError。

        Returns:
            已持久化的 PositionSnapshot。
        """
        if self._position_snapshot_repo is None:
            raise AggregateManagerError("未注入 position_snapshot_repo，无法持久化持仓快照")
        snapshot = self._position_tracker.get_positions()
        self._position_snapshot_repo.save(snapshot)
        logger.info(
            "持仓快照已持久化: portfolio_id=%s cash=%s holdings=%d",
            snapshot.portfolio_id,
            snapshot.cash,
            len(snapshot.holdings),
        )
        return snapshot
