# [BLUEPRINT] MOD-EX-001 | docs/03_modules/_domain_execution_core/fill_handler/blueprint.md
# [MODULE] zephyr.ex_core.fill_handler
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] D_EX_CORE域内模块 ; Fill Processor (D-EX-CORE-08, 阶段2)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fill_id幂等; filled_quantity单调递增; Decimal全程计算; FillSummary不可变; 状态转换遵循VALID_TRANSITIONS
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DuplicateFillError(ZA-EX-001-01); InvalidFillError(ZA-EX-001-02); OrderNotFoundError(ZA-EX-001-03)
# [TESTS] tests/ex_core/test_fill_handler.py
# [A_module] module_id=MOD-EX-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_EX_CORE — Fill Handler (部分成交处理器)

D_EX_CORE 域的成交回报处理器——接收 Fill（CTR-005），累积到对应 Order（CTR-004），
更新已成交数量、加权均价、佣金，并驱动成交相关状态转换（SUBMITTED→PARTIAL→FILLED）。

从 OrderManager._on_fill() 拆出的独立模块，提供更丰富的成交查询能力
（FillSummary / 剩余量 / 成交历史）和 fill_id 幂等保证。

设计真源: D-EX-CORE-48 "部分成交状态更新与后续处理"
蓝图: docs/03_modules/_domain_execution_core/fill_handler/blueprint.md
SSoT: depgraph MOD-EX-001
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderStatus
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "FillSummary",
    "FillHandler",
    "DuplicateFillError",
    "InvalidFillError",
    "OrderNotFoundError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class DuplicateFillError(ZephyrBaseError):
    """重复处理同一 fill_id 的成交（幂等拦截，非致命）。"""

    error_code = "ZA-EX-001-01"


class InvalidFillError(ZephyrBaseError):
    """成交回报数据非法（零数量/负数等）。"""

    error_code = "ZA-EX-001-02"


class OrderNotFoundError(ZephyrBaseError):
    """成交回报对应的订单不存在。"""

    error_code = "ZA-EX-001-03"


# ──────────────────────────────────────────────────────────────────────────────
# 成交相关状态转换规则（与 OrderManager.VALID_TRANSITIONS 对齐）
# ──────────────────────────────────────────────────────────────────────────────

_FILL_TRANSITIONS: Final[dict[OrderStatus, set[OrderStatus]]] = {
    OrderStatus.PENDING: set(),  # PENDING 不接受成交（需先 SUBMITTED）
    OrderStatus.SUBMITTED: {OrderStatus.PARTIAL, OrderStatus.FILLED},
    OrderStatus.PARTIAL: {OrderStatus.FILLED},  # PARTIAL→PARTIAL 无需转换
    OrderStatus.FILLED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
    OrderStatus.EXPIRED: set(),
}


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FillSummary:
    """成交汇总——不可变快照。

    描述一笔订单的成交状态：总量、已成交、剩余、均价、笔数、佣金。
    每次 process_fill 后生成新实例。
    """

    order_id: str
    total_quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal
    avg_fill_price: Decimal | None
    fill_count: int
    total_commission: Decimal
    is_complete: bool
    last_fill_timestamp: datetime | None


# ──────────────────────────────────────────────────────────────────────────────
# FillHandler
# ──────────────────────────────────────────────────────────────────────────────


class FillHandler:
    """部分成交处理器——Fill 累积+加权均价+状态转换+查询。

    用法::

        handler = FillHandler()
        summary = handler.process_fill(fill, order)
        # order.filled_quantity / avg_fill_price 已更新
        # summary 包含完整成交汇总
        remaining = handler.get_remaining(order.order_id)
    """

    def __init__(self) -> None:
        self._fills: dict[str, list[Fill]] = defaultdict(list)
        self._processed_fill_ids: set[str] = set()
        self._summaries: dict[str, FillSummary] = {}
        self._callbacks: list[Callable[[Fill, FillSummary], None]] = []

    # ── 核心处理 ──────────────────────────────────────────────────────────

    def process_fill(self, fill: Fill, order: Order) -> FillSummary:
        """处理一笔成交——更新订单成交状态，返回成交汇总。

        幂等: 同一 fill_id 重复调用不会重复累积，返回上次缓存的 summary。
        状态转换: 根据累积量判断 SUBMITTED→PARTIAL / →FILLED。
        就地更新: order 对象的 filled_quantity / avg_fill_price / status / updated_at 被修改。

        Args:
            fill: 成交回报（CTR-005，不可变）。
            order: 委托指令（CTR-004，可变——就地更新）。

        Returns:
            FillSummary: 成交汇总快照。

        Raises:
            InvalidFillError: 成交数量 <= 0。
            OrderNotFoundError: fill.order_id 与 order.order_id 不匹配。
        """
        # ── 校验 ──
        if fill.filled_quantity <= 0:
            raise InvalidFillError(
                f"成交数量必须 > 0, 实际={fill.filled_quantity} (fill_id={fill.fill_id})"
            )
        if fill.order_id != order.order_id:
            raise OrderNotFoundError(
                f"成交回报 order_id={fill.order_id} 与传入订单 order_id={order.order_id} 不匹配"
            )

        # ── 幂等检查 ──
        if fill.fill_id in self._processed_fill_ids:
            logger.debug("幂等拦截: fill_id=%s 已处理，跳过", fill.fill_id)
            cached = self._summaries.get(order.order_id)
            if cached is not None:
                return cached

        # ── 记录成交 ──
        self._fills[order.order_id].append(fill)
        self._processed_fill_ids.add(fill.fill_id)

        # ── 累积计算 ──
        old_filled = order.filled_quantity or Decimal("0")
        new_filled = old_filled + fill.filled_quantity

        # 加权均价
        old_avg = order.avg_fill_price or Decimal("0")
        if old_filled > 0:
            new_avg = (
                old_avg * old_filled + fill.fill_price * fill.filled_quantity
            ) / new_filled
        else:
            new_avg = fill.fill_price

        # 更新 Order 字段（就地修改）
        order.filled_quantity = new_filled
        order.avg_fill_price = new_avg
        order.updated_at = datetime.now(UTC)

        # ── 状态转换 ──
        total_qty = order.quantity
        if new_filled >= total_qty:
            self._try_transition(order, OrderStatus.FILLED)
        elif new_filled > 0:
            # SUBMITTED→PARTIAL 或 PARTIAL 保持
            if order.status != OrderStatus.PARTIAL:
                self._try_transition(order, OrderStatus.PARTIAL)

        # over-fill 警告
        if new_filled > total_qty:
            logger.warning(
                "成交超量: order_id=%s total=%s filled=%s (over=%s)",
                order.order_id, total_qty, new_filled, new_filled - total_qty,
            )

        # ── 计算佣金 ──
        total_commission = sum(
            (f.commission for f in self._fills[order.order_id]),
            start=Decimal("0"),
        )

        # ── 构建 FillSummary ──
        fills = self._fills[order.order_id]
        summary = FillSummary(
            order_id=order.order_id,
            total_quantity=total_qty,
            filled_quantity=new_filled,
            remaining_quantity=max(total_qty - new_filled, Decimal("0")),
            avg_fill_price=new_avg if new_filled > 0 else None,
            fill_count=len(fills),
            total_commission=total_commission,
            is_complete=new_filled >= total_qty,
            last_fill_timestamp=fill.fill_timestamp,
        )
        self._summaries[order.order_id] = summary

        logger.info(
            "成交处理: order_id=%s fill_id=%s qty=%s filled=%s/%s avg=%s "
            "commission=%s status=%s",
            order.order_id, fill.fill_id, fill.filled_quantity,
            new_filled, total_qty, new_avg, total_commission, order.status,
        )

        # ── 通知回调 ──
        for cb in self._callbacks:
            try:
                cb(fill, summary)
            except Exception:  # noqa: BLE001 — 回调失败不阻断处理
                logger.warning(
                    "成交回调异常: %s <- %s",
                    order.order_id, cb.__qualname__, exc_info=True,
                )

        return summary

    # ── 查询 ──────────────────────────────────────────────────────────────

    def get_summary(self, order_id: str) -> FillSummary | None:
        """获取订单的成交汇总（无成交返回 None）。"""
        return self._summaries.get(order_id)

    def get_fills(self, order_id: str) -> list[Fill]:
        """获取订单的成交历史（按处理顺序）。"""
        return list(self._fills.get(order_id, []))

    def get_remaining(self, order_id: str) -> Decimal | None:
        """获取订单的剩余未成交数量（无记录返回 None）。"""
        summary = self._summaries.get(order_id)
        if summary is None:
            return None
        return summary.remaining_quantity

    # ── 回调 ──────────────────────────────────────────────────────────────

    def register_callback(
        self, callback: Callable[[Fill, FillSummary], None]
    ) -> None:
        """注册成交回调——每次 process_fill 后同步调用。"""
        self._callbacks.append(callback)

    # ── 统计 ──────────────────────────────────────────────────────────────

    @property
    def order_count(self) -> int:
        """有成交记录的订单数量。"""
        return len(self._fills)

    @property
    def total_fill_count(self) -> int:
        """总成交笔数。"""
        return sum(len(fills) for fills in self._fills.values())

    # ── 内部 ──────────────────────────────────────────────────────────────

    def _try_transition(self, order: Order, target: OrderStatus) -> None:
        """尝试状态转换，非法转换记录日志但不抛异常。

        与 OrderManager._transition_status 不同——FillHandler 不阻断
        非法转换（可能由并发填充导致），仅记录警告。
        """
        if order.status == target:
            return  # 已在目标状态
        allowed = _FILL_TRANSITIONS.get(order.status, set())
        if target not in allowed:
            logger.warning(
                "状态转换跳过: %s -> %s 不在合法路径 (order_id=%s)",
                order.status, target, order.order_id,
            )
            return
        order.status = target
        order.updated_at = datetime.now(UTC)
