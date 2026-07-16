# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.enums.order_enums
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.__init__; zephyr.trading.trading_contracts.execution.order
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 枚举值MUST不变(BUY="BUY"等)——序列化/DB列映射依赖值; __str__返回value用于日志统一
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/contracts/test_order_enums.py
# [A_module] module_id=MOD-SHR_order_enums | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""OrderSide/OrderStatus/OrderType — 交易枚举真源 (5.152 #1 修复)

从 zephyr.trading.trading_contracts.execution.order 下沉到 shared 层。
枚举值保持不变，序列化/DB映射零影响。
"""
from __future__ import annotations

from enum import Enum


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
