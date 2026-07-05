# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.governance.observability_governance.analytics_base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.reporting.analytics_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; canonical at zephyr.reporting.analytics_base
# [MODIFY-GUARD] truth source at zephyr.reporting.analytics_base
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_analytics_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: analytics_base canonical at zephyr.reporting.analytics_base.

收敛双源——reporting.analytics_base 为真源（蓝图 MOD-L07-001 submodule_path=src/zephyr/reporting），
本模块仅 re-export 以保持向后兼容。
"""

from zephyr.reporting.analytics_base import AttributionEngineBase, TCAEngineBase

__all__ = ["AttributionEngineBase", "TCAEngineBase"]
