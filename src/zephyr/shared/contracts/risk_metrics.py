from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_metrics.py

CTR-P1-011: RiskMetricsReport / 风险指标报告

L04 → 下游风险指标报告契约。包含VaR、CVaR、回撤等风险指标的计算结果。

SSoT: cross-layer-contracts.yaml → CTR-P1-011
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class RiskMetricsReport:
    portfolio_id: str
    as_of_date: datetime
    var_1d_95: float
    var_1d_99: float
    cvar_1d_95: float
    cvar_1d_99: float
    max_drawdown: float
    current_drawdown: float
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    volatility_1d: float
    volatility_1m: float
    calculation_method: str
    confidence_level: float
    lookback_period: int
    schema_version: str = "1.0"
