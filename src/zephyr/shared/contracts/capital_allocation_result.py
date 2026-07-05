# ==== BEGIN CODGEN:CTR-P1-003 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.capital_allocation_result
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

from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/capital_allocation_result.py

CTR-P1-003: CapitalAllocationResult / 资本配置结果

D_SIGNAL → D_PORTFOLIO_CORE 资本配置结果契约。多策略资本分配的中间产物。

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
    total_allocated_weight: float
    rebalance_threshold: float = 0.05
    schema_version: str = "1.0"
    strategy_allocations: Dict[str, float] = field(default_factory=dict)

# ==== END CODGEN:CTR-P1-003 ====











