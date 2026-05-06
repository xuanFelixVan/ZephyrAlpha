

# ==== BEGIN CODGEN:CTR-P1-001 ====

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/factor_monitor_report.py

CTR-P1-001: FactorMonitorReport / 因子有效性监控报告

L02 → L07 因子有效性监控报告。定期评估已注册因子的预测有效性。

SSoT: cross-layer-contracts.yaml → CTR-P1-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class FactorMonitorReport:
    factor_id: str
    evaluation_date: str
    ic_mean: float
    ic_std: float
    ic_ir: float
    rank_ic: float
    is_effective: bool
    decay_alert: bool
    idempotency_key: str
    evaluation_window: int = 63
    schema_version: str = "1.0"
    half_life_days: Optional[int] = None

# ==== END CODGEN:CTR-P1-001 ====



