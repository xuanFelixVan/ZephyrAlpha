# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.risk.risk_metrics
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core; pf_core; ops; l10-compliance
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.risk.risk_metrics
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.risk.risk_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_risk_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.risk.risk_metrics。"""
from zephyr.trading.trading_contracts.risk.risk_metrics import *  # noqa: F401,F403
