# [BLUEPRINT] SRC-007 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.execution.trading.trading_contracts.portfolio.contracts.money
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.instrument
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.portfolio.contracts.money
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.portfolio.contracts.money
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_money | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.portfolio.contracts.money。"""
from zephyr.trading.trading_contracts.portfolio.contracts.money import *  # noqa: F401,F403
