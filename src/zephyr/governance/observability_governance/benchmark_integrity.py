# [BLUEPRINT] SRC-051 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.benchmark_integrity
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.governance.observability_governance.__init__
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
# [A_module] module_id=MOD-GOV_benchmark_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum


class IntegrityDim(str, Enum):
    MARKET_COVERAGE = "MARKET_COVERAGE"
    FACTOR_CONSISTENCY = "FACTOR_CONSISTENCY"
    BACKTEST_STABILITY = "BACKTEST_STABILITY"
    HFT_FIDELITY = "HFT_FIDELITY"


PIT_MAX_DELAY_MINUTES: int = 15
HEALTH_CHECK_INTERVAL: dict[str, str] = {
    "monthly": "所有dim+grid自动run",
    "quarterly": "full2016-2024 re-run vs Sept→bias report",
}
