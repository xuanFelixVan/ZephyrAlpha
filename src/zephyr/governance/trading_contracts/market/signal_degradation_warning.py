# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.execution.trading.trading_contracts.market.signal_degradation_warning
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] signal; risk; pf_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.market.signal_degradation_warning
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.market.signal_degradation_warning
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_signal_degradation_warning | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.market.signal_degradation_warning。"""
from zephyr.trading.trading_contracts.market.signal_degradation_warning import *  # noqa: F401,F403
