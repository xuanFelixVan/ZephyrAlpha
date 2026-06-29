# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared_08.contracts.position
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.core.trace_context
# [CONSUMERS] tests.integration.test_e2e_pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# ==== BEGIN CODGEN:CTR-006 ====
from dataclasses import dataclass, field
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
ZephyrAlpha — shared/contracts/position.py

CTR-006: PositionSnapshot / 持仓快照

持仓快照。不可变，代表某一时刻的完整持仓状态。

SSoT: cross_layer_contracts.yaml -> CTR-006
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要查询或记录当前持仓时，MUST 使用 PositionSnapshot 类型。 PositionSnapshot 是不可变对象（frozen=true），代表某一时刻的完整持仓状态。 holdings 是 {symbol: quantity} 的映射，quantity 使用 Decimal 类型。 market_values 是 {symbol: market_value} 的映射，market_value 使用 Decimal 类型。 total_market_value + cash = 组合总资产。 gross_leverage 用于风控监控和 L11 策略决策。 快照由 L06 OMS 或 L07 Analytics 产生，由 L04 Risk Monitor 和 L11 Strategic Decision 消费。 注意：holdings 和 market_values 虽然是 Dict，但持有的是引用——跨层传递时建议做 deep copy 防护。
"""


@dataclass(frozen=True)
class PositionSnapshot:
    as_of_timestamp: datetime
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    portfolio_id: str
    cash: Decimal = Decimal("0")
    gross_leverage: float = 1.0
    holdings: dict[str, Decimal] = field(default_factory=dict)
    market_values: dict[str, Decimal] = field(default_factory=dict)
    schema_version: str = "1.0"
    total_market_value: Decimal = Decimal("0")
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-006 ====
