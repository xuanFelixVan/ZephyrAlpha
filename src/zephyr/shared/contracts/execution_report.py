# ==== BEGIN CODGEN:CTR-P1-007 ====
from dataclasses import dataclass, field

from decimal import Decimal
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-06-25"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/execution_report.py

CTR-P1-007: ExecutionReport / 执行分析报告

L06 → L07 执行分析报告契约（TCA 输入）。

SSoT: cross_layer_contracts.yaml -> CTR-P1-007
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class ExecutionReport:
    actual_quantity: int
    broker_id: str
    commission: Decimal
    direction: str
    execution_end: str
    execution_start: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    intended_price: Decimal
    intended_quantity: int
    order_id: str
    slippage_bps: float
    symbol: str
    vwap_price: Decimal
    algo_type: str = "NONE"
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-007 ====



