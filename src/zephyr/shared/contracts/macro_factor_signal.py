# ==== BEGIN CODGEN:CTR-P1-002 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.macro_factor_signal
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
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/macro_factor_signal.py

CTR-P1-002: MacroFactorSignal / 宏观因子信号

D_FACTOR 宏观因子信号契约。扩展 FactorSignal 以支持宏观经济维度。

SSoT: cross_layer_contracts.yaml -> CTR-P1-002
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class MacroFactorSignal:
    as_of_date: str
    data_source: str
    factor_id: str
    idempotency_key: str
    macro_regime: str
    release_lag_days: int
    signal_value: float
    confidence: float = 1.0
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-002 ====











