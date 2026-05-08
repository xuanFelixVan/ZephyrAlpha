# ==== BEGIN CODGEN:CTR-P1-002 ====

from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/macro_factor_signal.py

CTR-P1-002: MacroFactorSignal / 宏观因子信号

L02 宏观因子信号契约。扩展 FactorSignal 以支持宏观经济维度。

SSoT: cross-layer-contracts.yaml → CTR-P1-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class MacroFactorSignal:
    factor_id: str
    as_of_date: str
    macro_regime: str
    signal_value: float
    data_source: str
    release_lag_days: int
    idempotency_key: str
    confidence: float = 1.0
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-002 ====
