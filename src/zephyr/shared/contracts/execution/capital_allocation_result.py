from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-003 ====

from dataclasses import dataclass, field

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/capital_allocation_result.py

CTR-P1-003: CapitalAllocationResult / 资本配置结果

L03 → L05 资本配置结果契约。多策略资本分配的中间产物。

SSoT: cross-layer-contracts.yaml → CTR-P1-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class CapitalAllocationResult:
    allocation_date: str
    total_allocated_weight: float
    allocation_method: str
    idempotency_key: str
    strategy_allocations: dict[str, float] = field(default_factory=dict)
    rebalance_threshold: float = 0.05
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-003 ====
