# ==== BEGIN CODGEN:CTR-P1-011 ====
from dataclasses import dataclass, field

from datetime import datetime, timezone
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-06-25"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_metrics.py

CTR-P1-011: RiskMetricsReport / 风险指标报告

L04 → 下游风险指标报告契约。包含VaR、CVaR、回撤等风险指标的计算结果。

SSoT: cross_layer_contracts.yaml -> CTR-P1-011
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class RiskMetricsReport:
    as_of_date: datetime
    beta: float
    calculation_method: str
    confidence_level: float
    current_drawdown: float
    cvar_1d_95: float
    cvar_1d_99: float
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    lookback_period: int
    max_drawdown: float
    portfolio_id: str
    sharpe_ratio: float
    sortino_ratio: float
    var_1d_95: float
    var_1d_99: float
    volatility_1d: float
    volatility_1m: float
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-011 ====



