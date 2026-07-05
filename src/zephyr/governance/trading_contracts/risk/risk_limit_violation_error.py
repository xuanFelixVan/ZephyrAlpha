# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.risk.risk_limit_violation_error
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.risk.risk_limit_violation_error
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.risk.risk_limit_violation_error
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_risk_limit_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.risk.risk_limit_violation_error。"""
from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import *  # noqa: F401,F403
