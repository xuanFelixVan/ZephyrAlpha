# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.enums.order_enums
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.__init__; zephyr.trading.trading_contracts.execution.order; F53 订单生命周期（BrokerOrderState 九态桥消费方，待 F53 落地接线——G41-2a 交界件）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 枚举值MUST不变(BUY="BUY"等)——序列化/DB列映射依赖值; __str__返回value用于日志统一
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/compliance/test_manipulation_realtime_monitor.py; tests/compliance/test_runtime_wiring.py; tests/ex_core/adapters/test_okx_broker.py; tests/ex_core/test_aggregate_root_manager.py; tests/ex_core/test_async_fill_dispatcher.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 42 个测试）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
OrderSide/OrderStatus/OrderType — 交易枚举真源 (5.152 #1 修复)

从 zephyr.trading.trading_contracts.execution.order 下沉到 shared 层。
枚举值保持不变，序列化/DB映射零影响。

# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/enums/order_enums.yaml
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class OrderSide(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class BrokerOrderState(Enum):
    """券商柜台九态词表（TDM-E-L4-10 判据口径，QMT 风格）。

    G41-2 映射桥（2026-09-27 zc-lane-t-20260927，全流通战役 F41 卷）：
    TDM 判据面订单生命周期走九态（New/Accepted/Suspended/PendingCancel 四态为
    码面 7 态所无），本枚举=九态→内部 OrderStatus(7) 的唯一映射真源（F53 订单
    生命周期交界件）。只读语义收口，不改任何下单/成交路径。
    """

    def __str__(self) -> str:
        return self.value

    NEW = "NEW"  # 待报（本地已收、未达柜台）
    ACCEPTED = "ACCEPTED"  # 已报（柜台受理）
    PARTIAL = "PARTIAL"  # 部分成交
    FILLED = "FILLED"  # 全部成交
    CANCELLED = "CANCELLED"  # 已撤
    REJECTED = "REJECTED"  # 废单
    EXPIRED = "EXPIRED"  # 已失效/过期
    SUSPENDED = "SUSPENDED"  # 暂停（标的停牌等，委托挂起不可成交）
    PENDING_CANCEL = "PENDING_CANCEL"  # 已报待撤（撤单指令在途未确认）


#: 九态→内部 7 态映射真源（封闭表，逐格显式禁隐式）。
#: 收口策略：内部 7 态无 SUSPENDED/PENDING_CANCEL——SUSPENDED（停牌挂起）与
#: PENDING_CANCEL（待撤）的委托在柜台侧均仍存活（可回内场成交/撤回确认），
#: 故均归 SUBMITTED 工作态；终态语义（FILLED/CANCELLED/REJECTED/EXPIRED）不变。
BROKER_STATE_TO_ORDER_STATUS: Final[dict[BrokerOrderState, OrderStatus]] = {
    BrokerOrderState.NEW: OrderStatus.PENDING,
    BrokerOrderState.ACCEPTED: OrderStatus.SUBMITTED,
    BrokerOrderState.PARTIAL: OrderStatus.PARTIAL,
    BrokerOrderState.FILLED: OrderStatus.FILLED,
    BrokerOrderState.CANCELLED: OrderStatus.CANCELLED,
    BrokerOrderState.REJECTED: OrderStatus.REJECTED,
    BrokerOrderState.EXPIRED: OrderStatus.EXPIRED,
    BrokerOrderState.SUSPENDED: OrderStatus.SUBMITTED,
    BrokerOrderState.PENDING_CANCEL: OrderStatus.SUBMITTED,
}


def map_broker_state_to_order_status(state: BrokerOrderState | str) -> OrderStatus:
    """券商九态 → 内部 7 态（G41-2a 桥层；未知态 fail-closed ValueError）。

    Args:
        state: BrokerOrderState 成员或其 value 字符串（"PENDING_CANCEL" 等）。

    Raises:
        ValueError: 未知态（禁隐式吞掉——九态词表收口必须显式扩表）。
    """
    try:
        member = state if isinstance(state, BrokerOrderState) else BrokerOrderState(str(state).upper())
    except ValueError as exc:
        raise ValueError(f"未知券商订单态（九态词表外）: {state!r}") from exc
    return BROKER_STATE_TO_ORDER_STATUS[member]
