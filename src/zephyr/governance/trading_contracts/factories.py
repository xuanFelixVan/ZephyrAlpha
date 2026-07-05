# [BLUEPRINT] MOD-TRADING-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.factories
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.order; zephyr.trading.trading_contracts.market.factor_signal; zephyr.trading.trading_contracts.market.synthesized_signal; zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot; zephyr.trading.trading_contracts.risk.risk_limits; zephyr.trading.trading_contracts.risk.risk_metrics; zephyr.shared.contracts.core.factories
# [CONSUMERS] shared/contracts/core/factories.py(已迁移)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.factories
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.factories
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError: 参数越界
# [TESTS] tests/test_trading_contracts_factories.py
# [A_module] module_id=MOD-EXE_factories | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.factories。"""
from zephyr.trading.trading_contracts.factories import *  # noqa: F401,F403
