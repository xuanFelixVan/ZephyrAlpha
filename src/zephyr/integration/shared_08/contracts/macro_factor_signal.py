# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared_08.contracts.macro_factor_signal
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests.integration.test_phase_f_layers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# ==== BEGIN CODGEN:CTR-P1-002 ====
from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/macro_factor_signal.py

CTR-P1-002: MacroFactorSignal / 宏观因子信号

L02 宏观因子信号契约。扩展 FactorSignal 以支持宏观经济维度。

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
    idempotency_key: str
    idempotency_key: str
    macro_regime: str
    release_lag_days: int
    signal_value: float
    confidence: float = 1.0
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-002 ====
