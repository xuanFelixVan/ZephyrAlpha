# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.pf_core.strategy_portfolio
# [DOMAIN] D-PF_ALLOC
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-RES_strategy_portfolio | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

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
