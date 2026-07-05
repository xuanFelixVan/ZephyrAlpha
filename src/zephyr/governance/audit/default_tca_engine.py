# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.governance.audit.default_tca_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.reporting.default_tca_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; canonical at zephyr.reporting.default_tca_engine
# [MODIFY-GUARD] truth source at zephyr.reporting.default_tca_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_default_tca_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: default_tca_engine canonical at zephyr.reporting.default_tca_engine.

收敛双定义——reporting.default_tca_engine 为真源（蓝图 MOD-L07-001），
本模块仅 re-export 以保持向后兼容。
"""

from zephyr.reporting.default_tca_engine import DefaultTCAEngine

__all__ = ["DefaultTCAEngine"]
