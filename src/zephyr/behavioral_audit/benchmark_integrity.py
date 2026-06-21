# [A_module] module_id=MOD-SEC_benchmark_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.benchmark_integrity
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/

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
