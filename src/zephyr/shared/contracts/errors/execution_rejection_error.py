from __future__ import annotations

from dataclasses import dataclass

from zephyr.shared.contracts.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/execution_rejection_error.py

CTR-ERR-005: ExecutionRejectionError / 执行拒绝错误

L06 订单执行过程中被券商或市场拒绝时抛出的错误。

SSoT: cross-layer-contracts.yaml → CTR-ERR-005
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L06 的订单被券商/交易所拒绝时，MUST 抛出 ExecutionRejectionError。 拒绝原因通过 rejection_source（BROKER / EXCHANGE / CIRCUIT_BREAKER / INTERNAL）和 rejection_reason 字段精确标识。 L05 可以根据此错误决定是否重新生成订单（如降低数量、改用 LIMIT 单）。 如果 rejection_reason 为 market_circuit_breaker，不要重试——等待下一周期。
"""


@dataclass(frozen=True)
class ExecutionRejectionError:
    error_id: str
    order_id: str
    symbol: str
    rejection_source: str
    rejection_reason: str
    recovery_hint: str
    schema_version: str = "1.0"
    broker_message: Optional[str] = None
    trace_context: Optional[TraceContext] = None
