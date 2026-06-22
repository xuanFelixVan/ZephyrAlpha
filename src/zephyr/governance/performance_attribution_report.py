# [A_module] module_id=MOD-PRT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-197 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.portfolio.core.performance_attribution_report
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# Re-export from shared SSoT — zephyr.shared.contracts.portfolio.performance_attribution_report
from zephyr.shared.contracts.portfolio.performance_attribution_report import PerformanceAttributionReport

__all__ = ["PerformanceAttributionReport"]
