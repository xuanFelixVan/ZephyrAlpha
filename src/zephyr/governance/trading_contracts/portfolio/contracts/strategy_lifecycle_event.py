# [BLUEPRINT] SRC-009 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.governance.trading_contracts.portfolio.contracts.strategy_lifecycle_event
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.portfolio.strategy_lifecycle_event
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_strategy_lifecycle_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event。"""
from zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event import *  # noqa: F401,F403
