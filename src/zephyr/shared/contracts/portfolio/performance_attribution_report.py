# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.portfolio.performance_attribution_report
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.performance_attribution_report
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; canonical at zephyr.shared.contracts.performance_attribution_report
# [MODIFY-GUARD] truth source at zephyr.shared.contracts.performance_attribution_report
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已收敛至 zephyr.shared.contracts.performance_attribution_report.

CTR-P1-009 契约 physical_path 指向 shared/contracts/performance_attribution_report.py（canonical），
本文件仅 re-export 以保持向后兼容。
"""

from zephyr.shared.contracts.performance_attribution_report import *  # noqa: F401,F403
