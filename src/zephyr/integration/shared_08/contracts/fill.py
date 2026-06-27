# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared_08.contracts.fill
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.core.trace_context
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# ==== BEGIN CODGEN:CTR-005 ====
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/fill.py

CTR-005: Fill / 成交回报

L06 → L07 核心数据契约。单次成交回报（不可变）。

SSoT: cross_layer_contracts.yaml -> CTR-005
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L06 中记录成交或在 L07 中分析成交时，MUST 使用 Fill 类型。 Fill 是不可变对象（frozen=true），一旦创建不得修改。 fill_id 是全局唯一 ID，order_id 关联 CTR-004 Order。 fill_price 和 filled_quantity 使用 Decimal 类型，禁止 float。 slippage 为可选项，计算方式为 (fill_price - decision_price) / decision_price，用于 TCA 分析。 佣金 commission 从券商回报中提取，保留券商原始精度。 每个 Order 可能对应多个 Fill（部分成交场景）。
"""


@dataclass(frozen=True)
class Fill:
    fill_id: str
    fill_price: Decimal
    fill_timestamp: datetime
    filled_quantity: Decimal
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    order_id: str
    strategy_id: str
    symbol: str
    broker_fill_id: str | None = None
    commission: Decimal = Decimal("0")
    schema_version: str = "1.0"
    slippage: Decimal | None = None
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-005 ====
