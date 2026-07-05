# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.execution.model_serving_request
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] l11-ml-platform
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.execution.model_serving_request
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.execution.model_serving_request
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_model_serving_request | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.execution.model_serving_request。"""
from zephyr.trading.trading_contracts.execution.model_serving_request import *  # noqa: F401,F403
