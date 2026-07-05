# [BLUEPRINT] SRC-197 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.governance.performance_attribution_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.portfolio.performance_attribution_report
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from shared SSoT — canonical at zephyr.shared.contracts.performance_attribution_report
# (CTR-P1-009 physical_path = src/zephyr/shared/contracts/performance_attribution_report.py)
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport

__all__ = ["PerformanceAttributionReport"]
