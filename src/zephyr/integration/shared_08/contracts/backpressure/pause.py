# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.backpressure.pause
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.__init__; zephyr.integration.shared_08.contracts.core.trace_context
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.backpressure.pause
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.backpressure.pause
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.backpressure.pause import BackpressurePause"
# [A_module] module_id=MOD-INT_pause | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.backpressure.pause。"""
from zephyr.shared.contracts.backpressure.pause import *  # noqa: F401,F403
