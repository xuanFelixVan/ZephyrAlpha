# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.benchmark_integrity
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_benchmark_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


class IntegrityDim(str, Enum):
    MARKET_COVERAGE = "MARKET_COVERAGE"
    FACTOR_CONSISTENCY = "FACTOR_CONSISTENCY"
    BACKTEST_STABILITY = "BACKTEST_STABILITY"
    HFT_FIDELITY = "HFT_FIDELITY"


PIT_MAX_DELAY_MINUTES: Final[int] = 15
HEALTH_CHECK_INTERVAL: Final[dict[str, str]] = {
    "monthly": "所有dim+grid自动run",
    "quarterly": "full2016-2024 re-run vs Sept->bias report",
}
