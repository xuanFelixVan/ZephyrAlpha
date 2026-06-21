# [A_module] module_id=MOD-INT_capital_allocation_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# ==== BEGIN CODGEN:CTR-P1-003 ====
from dataclasses import dataclass, field

from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/capital_allocation_result.py

CTR-P1-003: CapitalAllocationResult / 资本配置结果

L03 → L05 资本配置结果契约。多策略资本分配的中间产物。

SSoT: cross_layer_contracts.yaml -> CTR-P1-003
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class CapitalAllocationResult:
    allocation_date: str
    allocation_method: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    total_allocated_weight: float
    rebalance_threshold: float = 0.05
    schema_version: str = "1.0"
    strategy_allocations: Dict[str, float] = field(default_factory=dict)

# ==== END CODGEN:CTR-P1-003 ====















































































































































































