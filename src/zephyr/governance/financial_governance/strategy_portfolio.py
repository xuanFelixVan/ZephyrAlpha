# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.strategy_portfolio
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_strategy_portfolio | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
