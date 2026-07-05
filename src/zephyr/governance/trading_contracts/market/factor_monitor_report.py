# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.market.factor_monitor_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] factor; pf_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.market.factor_monitor_report
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.market.factor_monitor_report
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_factor_monitor_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.market.factor_monitor_report。"""
from zephyr.trading.trading_contracts.market.factor_monitor_report import *  # noqa: F401,F403
