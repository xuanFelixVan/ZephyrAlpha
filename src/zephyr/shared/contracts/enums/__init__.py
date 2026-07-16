# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.enums
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.contracts.order; zephyr.trading.trading_contracts.execution.order
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 跨切面枚举真源——被 shared/trading/governance 三层消费，MUST定义在shared层
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/contracts/test_order_enums.py
# [A_module] module_id=MOD-SHR_order_enums | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""shared/contracts/enums — 跨切面交易枚举真源 (5.152 #1 修复)

原位置: zephyr.trading.trading_contracts.execution.order (trading层)
问题: shared/contracts/order.py (codegen) 反向 import trading 层枚举 → 违反分层
修复: 枚举下沉到 shared 层，trading/governance 通过 re-export 引用
"""
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType

__all__ = ["OrderSide", "OrderStatus", "OrderType"]
