# ==== BEGIN CODGEN:CTR-P1-001 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.factor_monitor_report
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

from typing import Optional
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/factor_monitor_report.py

CTR-P1-001: FactorMonitorReport / 因子有效性监控报告

D_FACTOR -> D_REPORTING 因子有效性监控报告。定期评估已注册因子的预测有效性。

SSoT: cross_layer_contracts.yaml -> CTR-P1-001
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class FactorMonitorReport:
    decay_alert: bool
    evaluation_date: str
    factor_id: str
    ic_ir: float
    ic_mean: float
    ic_std: float
    idempotency_key: str
    is_effective: bool
    rank_ic: float
    evaluation_window: int = 63
    half_life_days: Optional[int] = None
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-001 ====











