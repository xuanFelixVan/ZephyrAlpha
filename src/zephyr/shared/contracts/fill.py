# ==== BEGIN CODGEN:CTR-005 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.fill
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/fill.py

CTR-005: Fill / 成交回报

D_EXECUTION_CORE → D_REPORTING 核心数据契约。单次成交回报（不可变）。

SSoT: cross_layer_contracts.yaml -> CTR-005
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 D_EXECUTION_CORE 中记录成交或在 D_REPORTING 中分析成交时，MUST 使用 Fill 类型。 Fill 是不可变对象（frozen=true），一旦创建不得修改。 fill_id 是全局唯一 ID，order_id 关联 CTR-004 Order。 fill_price 和 filled_quantity 使用 Decimal 类型，禁止 float。 slippage 为可选项，计算方式为 (fill_price - decision_price) / decision_price，用于 TCA 分析。 佣金 commission 从券商回报中提取，保留券商原始精度。 每个 Order 可能对应多个 Fill（部分成交场景）。
"""

@dataclass(frozen=True)
class Fill:
    fill_id: str
    fill_price: Decimal
    fill_timestamp: datetime
    filled_quantity: Decimal
    idempotency_key: str
    order_id: str
    strategy_id: str
    symbol: str
    broker_fill_id: Optional[str] = None
    commission: Decimal = Decimal("0")
    schema_version: str = "1.0"
    slippage: Optional[Decimal] = None
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-005 ====








