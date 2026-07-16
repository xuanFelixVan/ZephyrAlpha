# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.order
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.order
# [CONSUMERS] pf_core; ex_core; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016-order | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: Order 真源在 zephyr.shared.contracts.order（CTR-004 codegen）

治本修复: 原文件重复定义 Order 类（多真源），且 TraceContext 未 import（NameError bug）。
改为 re-export shared 层真源，消除多真源 + bug。
SSoT: cross_layer_contracts.yaml -> CTR-004 (codegen 生成 shared/contracts/order.py)
"""
from __future__ import annotations

# 5.152 #1 修复: 枚举真源下沉到 shared 层，消除 shared→trading 违规依赖
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType

# 治本修复: Order 真源 re-export（消除多真源 + TraceContext import bug）
from zephyr.shared.contracts.order import Order

__all__ = ["OrderSide", "OrderStatus", "OrderType", "Order"]
