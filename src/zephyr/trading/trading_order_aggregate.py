# [BLUEPRINT] MOD-TRADING-009 | docs/03_modules/_domain_trading/trading_order_aggregate/blueprint.md
# [MODULE] zephyr.trading.trading_order_aggregate
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 交易运营编排层（运行时装配批）; MOD-TRADING-010 SettlementRecord 聚合（FILLED→SETTLING 联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] order_id唯一; idempotency_key幂等(同键重复注册返回既有聚合不回退状态); 运营状态机非法转换Fail-Closed; OrderDomainEvent frozen不可变; events append-only只增不改; event_sink异常不阻断聚合; occurred_at由调用方注入(不读墙钟)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TradingOrderAggregateError(ZA-TR-0025); InvalidTradingOrderInputError; DuplicateOrderIdError; InvalidOrderTransitionError
# [TESTS] tests/trading/test_trading_order_aggregate.py
# [A_module] module_id=MOD-TRADING-009 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: register(order_id/idempotency_key/symbol/side/quantity)——运营订单注册请求; idempotency_key 幂等键
# I2: transition(order_id/to_status/occurred_at/note)——状态迁移请求(执行段结果/结算事件由编排层翻译后驱动)
# F1: TradingOrderBook.register()——幂等注册: 同 idempotency_key 返回既有聚合; order_id 冲突异键 Fail-Closed
# F2: TradingOrderBook.transition()——状态机校验(VALID_TRANSITIONS)→迁移→产出 OrderDomainEvent→event_sink 发布
# A1: 非法转换/终态再迁移→InvalidOrderTransitionError(Fail-Closed); sink 异常仅日志不阻断
# O1: TradingOrder 聚合根(只读快照) + OrderDomainEvent 领域事件流(append-only, 可 replay 重建)
# [/ALGO_FLOW]
"""D_TRADING — TradingOrder 订单核心聚合（AGG-TRD-01，D-TRADING §0）。

交易运营域 OMS 侧订单聚合根（DDD）。与既有件边界：
  - ex_core/order_manager（MOD-L06-001）：执行段状态机（PENDING→SUBMITTED→
    PARTIAL→FILLED/CANCELLED）+合规双闸+券商路由——本件**不重复**执行段，
    仅消费其执行结果快照推进运营段状态。
  - trading_contracts/execution/order（MOD-INF-016）：CTR-004 Order 契约——
    本件聚合根为运营叙事层，不重复定义契约。
  - settlement_reconciliation（MOD-TRADING-003）：交易级对账引擎——本件
    SETTLING→SETTLED→RECONCILED 段由对账/结算事件驱动（编排层翻译）。

运营全生命周期：RECEIVED→DISPATCHED→EXECUTING→FILLED→SETTLING→SETTLED→
RECONCILED；支路 REJECTED/CANCELLED 终态。幂等键保证同指令重复注册不双建；
每次迁移产出不可变 OrderDomainEvent 经注入式 event_sink 发布（缺失/异常不
阻断，仅落聚合内事件日志）；事件 append-only 支持 replay 重建。

设计真源：docs/03_modules/_domain_trading/trading_order_aggregate/blueprint.md
（B6-08087 / CAND-TRD-009，AUD-DRAFT-001-DIGEST P1 波 W-P1-23）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import Enum, auto
from typing import Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class TradingOrderAggregateError(ZephyrBaseError):
    """TradingOrder 聚合基类异常。"""

    error_code = "ZA-TR-0025"


class InvalidTradingOrderInputError(TradingOrderAggregateError):
    """聚合输入非法——空 order_id/idempotency_key、未知订单、非正数量。"""

    error_code = "ZA-TR-0026"


class DuplicateOrderIdError(TradingOrderAggregateError):
    """order_id 冲突（幂等键不同）——Fail-Closed 拒绝双建。"""

    error_code = "ZA-TR-0027"


class InvalidOrderTransitionError(TradingOrderAggregateError):
    """非法状态迁移（含终态再迁移）——Fail-Closed。"""

    error_code = "ZA-TR-0028"


class TradingOrderStatus(Enum):
    """运营全生命周期状态（与 EX 执行段状态机粒度正交）。"""

    RECEIVED = auto()
    DISPATCHED = auto()
    EXECUTING = auto()
    FILLED = auto()
    SETTLING = auto()
    SETTLED = auto()
    RECONCILED = auto()
    REJECTED = auto()
    CANCELLED = auto()


#: 运营状态机合法迁移表（终态：RECONCILED/REJECTED/CANCELLED）
VALID_TRANSITIONS: Final[dict[TradingOrderStatus, frozenset[TradingOrderStatus]]] = {
    TradingOrderStatus.RECEIVED: frozenset(
        {TradingOrderStatus.DISPATCHED, TradingOrderStatus.REJECTED, TradingOrderStatus.CANCELLED}
    ),
    TradingOrderStatus.DISPATCHED: frozenset(
        {TradingOrderStatus.EXECUTING, TradingOrderStatus.REJECTED, TradingOrderStatus.CANCELLED}
    ),
    TradingOrderStatus.EXECUTING: frozenset({TradingOrderStatus.FILLED, TradingOrderStatus.CANCELLED}),
    TradingOrderStatus.FILLED: frozenset({TradingOrderStatus.SETTLING}),
    TradingOrderStatus.SETTLING: frozenset({TradingOrderStatus.SETTLED}),
    TradingOrderStatus.SETTLED: frozenset({TradingOrderStatus.RECONCILED}),
    TradingOrderStatus.RECONCILED: frozenset(),
    TradingOrderStatus.REJECTED: frozenset(),
    TradingOrderStatus.CANCELLED: frozenset(),
}


@dataclass(frozen=True)
class OrderDomainEvent:
    """订单领域事件（不可变；occurred_at 由调用方注入，聚合不读墙钟）。"""

    order_id: str
    from_status: TradingOrderStatus
    to_status: TradingOrderStatus
    occurred_at: str
    note: str = ""
    schema_version: str = "1.0"


@dataclass(frozen=True)
class TradingOrder:
    """TradingOrder 聚合根只读快照（迁移经 TradingOrderBook 产新快照）。"""

    order_id: str
    idempotency_key: str
    symbol: str
    side: str
    quantity: Decimal
    status: TradingOrderStatus = TradingOrderStatus.RECEIVED
    events: tuple[OrderDomainEvent, ...] = field(default_factory=tuple)
    schema_version: str = "1.0"


class TradingOrderBook:
    """TradingOrder 聚合注册表（簿）——幂等注册 + 状态机迁移 + 事件发布。

    event_sink：注入式领域事件出口（装配批接事件总线）；缺失仅落聚合内
    事件日志，sink 异常不阻断聚合（不静默——记 WARNING 日志）。
    """

    def __init__(self, event_sink: Callable[[OrderDomainEvent], None] | None = None) -> None:
        self._event_sink = event_sink
        self._orders: dict[str, TradingOrder] = {}
        self._by_idempotency_key: dict[str, str] = {}

    def register(
        self,
        *,
        order_id: str,
        idempotency_key: str,
        symbol: str,
        side: str,
        quantity: Decimal,
    ) -> TradingOrder:
        """幂等注册：同 idempotency_key 返回既有聚合（不回退状态）。"""
        if not order_id or not idempotency_key:
            raise InvalidTradingOrderInputError("order_id/idempotency_key 不能为空")
        if not isinstance(quantity, Decimal) or quantity <= 0:
            raise InvalidTradingOrderInputError("quantity 必须为正 Decimal")
        existing_id = self._by_idempotency_key.get(idempotency_key)
        if existing_id is not None:
            return self._orders[existing_id]
        if order_id in self._orders:
            raise DuplicateOrderIdError(f"order_id 冲突（幂等键不同）: {order_id}")
        order = TradingOrder(
            order_id=order_id,
            idempotency_key=idempotency_key,
            symbol=symbol,
            side=side,
            quantity=quantity,
        )
        self._orders[order_id] = order
        self._by_idempotency_key[idempotency_key] = order_id
        return order

    def transition(
        self,
        order_id: str,
        to_status: TradingOrderStatus,
        occurred_at: str,
        note: str = "",
    ) -> TradingOrder:
        """状态迁移：非法转换 Fail-Closed；成功产出领域事件并发布。"""
        order = self._orders.get(order_id)
        if order is None:
            raise InvalidTradingOrderInputError(f"未知订单: {order_id}")
        if not occurred_at:
            raise InvalidTradingOrderInputError("occurred_at 不能为空（调用方注入）")
        if to_status not in VALID_TRANSITIONS[order.status]:
            raise InvalidOrderTransitionError(
                f"非法状态迁移: {order.status.name} -> {to_status.name} (order_id={order_id})"
            )
        event = OrderDomainEvent(
            order_id=order_id,
            from_status=order.status,
            to_status=to_status,
            occurred_at=occurred_at,
            note=note,
        )
        migrated = replace(order, status=to_status, events=order.events + (event,))
        self._orders[order_id] = migrated
        self._publish(event)
        return migrated

    def get(self, order_id: str) -> TradingOrder | None:
        """按 order_id 取聚合快照（不存在返回 None）。"""
        return self._orders.get(order_id)

    def events_of(self, order_id: str) -> tuple[OrderDomainEvent, ...]:
        """聚合事件流（append-only；replay 可重建状态）。"""
        order = self._orders.get(order_id)
        return order.events if order is not None else ()

    def _publish(self, event: OrderDomainEvent) -> None:
        if self._event_sink is None:
            return
        try:
            self._event_sink(event)
        except Exception:  # noqa: BLE001 — sink 异常不阻断聚合（记日志不静默）
            _logger.warning("order event_sink 异常（不阻断聚合）: order_id=%s", event.order_id, exc_info=True)


__all__ = [
    "DuplicateOrderIdError",
    "InvalidOrderTransitionError",
    "InvalidTradingOrderInputError",
    "OrderDomainEvent",
    "TradingOrder",
    "TradingOrderAggregateError",
    "TradingOrderBook",
    "TradingOrderStatus",
    "VALID_TRANSITIONS",
]

#: 包门面再导出别名（scaffold 注册约定）
TradingOrderAggregate = TradingOrderBook
