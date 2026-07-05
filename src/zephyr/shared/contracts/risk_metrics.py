# ==== BEGIN CODGEN:CTR-P1-011 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.risk_metrics
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

from datetime import datetime, timezone
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_metrics.py

CTR-P1-011: RiskMetricsReport / 风险指标报告

D_RISK → 下游风险指标报告契约。包含VaR、CVaR、回撤等风险指标的计算结果。

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











