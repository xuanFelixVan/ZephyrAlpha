# ==== BEGIN CODGEN:CTR-P1-007 ====

from dataclasses import dataclass
from decimal import Decimal

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/execution_report.py

CTR-P1-007: ExecutionReport / 执行分析报告

L06 → L07 执行分析报告契约（TCA 输入）。

SSoT: cross-layer-contracts.yaml → CTR-P1-007
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class ExecutionReport:
    order_id: str
    symbol: str
    direction: str
    intended_quantity: int
    actual_quantity: int
    intended_price: Decimal
    vwap_price: Decimal
    slippage_bps: float
    commission: Decimal
    execution_start: str
    execution_end: str
    broker_id: str
    idempotency_key: str
    algo_type: str = "NONE"
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-007 ====
