# [BLUEPRINT] SRC-199 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.trading.trading_contracts.portfolio.contracts.performance_attribution_report
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.portfolio.contracts.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-P1-009 ====
from dataclasses import dataclass, field

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/performance_attribution_report.py

CTR-P1-009: PerformanceAttributionReport / 绩效归因报告

D_REPORTING → D_FRONTEND/D_GOV_ENFORCEMENT 绩效归因报告契约。

SSoT: cross_layer_contracts.yaml → CTR-P1-009
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class PerformanceAttributionReport:
    portfolio_id: str
    period_start: str
    period_end: str
    total_return: float
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    transaction_cost_drag: float
    idempotency_key: str
    factor_contributions: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-009 ====
