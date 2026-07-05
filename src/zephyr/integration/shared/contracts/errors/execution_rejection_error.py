# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared.contracts.errors.execution_rejection_error
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS] zephyr.integration.shared.contracts.errors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-ERR-005 ====
from dataclasses import dataclass

from zephyr.shared.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/execution_rejection_error.py

CTR-ERR-005: ExecutionRejectionError / 执行拒绝错误

D_EXECUTION_CORE 订单执行过程中被券商或市场拒绝时抛出的错误。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-005
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_EXECUTION_CORE 的订单被券商/交易所拒绝时，MUST 抛出 ExecutionRejectionError。 拒绝原因通过 rejection_source（BROKER / EXCHANGE / CIRCUIT_BREAKER / INTERNAL）和 rejection_reason 字段精确标识。 D_PORTFOLIO_CORE 可以根据此错误决定是否重新生成订单（如降低数量、改用 LIMIT 单）。 如果 rejection_reason 为 market_circuit_breaker，不要重试——等待下一周期。
"""


@dataclass(frozen=True)
class ExecutionRejectionError:
    error_id: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    order_id: str
    recovery_hint: str
    rejection_reason: str
    rejection_source: str
    symbol: str
    broker_message: str | None = None
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-ERR-005 ====
