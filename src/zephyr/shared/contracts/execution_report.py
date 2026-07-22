# ==== BEGIN CODGEN:CTR-P1-007 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.execution_report
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

from decimal import Decimal
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/execution_report.py

CTR-P1-007: ExecutionReport / 执行分析报告

D_EXECUTION_CORE -> D_REPORTING 执行分析报告契约（TCA 输入）。

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
    intended_price: Decimal
    intended_quantity: int
    order_id: str
    slippage_bps: float
    symbol: str
    vwap_price: Decimal
    algo_type: str = "NONE"
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-007 ====











