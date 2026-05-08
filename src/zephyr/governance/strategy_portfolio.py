from __future__ import annotations

from enum import Enum

class StrategyMethod(str, Enum):
    ONE_OVER_N = "1/N"
    RISK_PARITY = "RiskParity"
    KELLY = "Kelly"
    MAX_DD_LIMIT = "MaxDDLimit"

class RetirementTrigger(str, Enum):
    SHARPE_12M_NEGATIVE = "Sharpe 12m < 0"
    CALMAR_12M_LOW = "Calmar 12m < 0.3"
    SIX_MONTH_NEGATIVE = "6-month consecutive negative"

def estimate_capacity(max_vol: float, signal_decay: float, liq_util: float, impact_ratio: float) -> float:
    return min(signal_decay, liq_util * impact_ratio) * max(10_000_000, max_vol)
