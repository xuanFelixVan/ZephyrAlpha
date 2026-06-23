# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.identity.permission
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.identity.__init__
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.identity.permission
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.identity.permission
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.identity.permission"
# [A_module] module_id=MOD-INT_permission | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.identity.permission。"""

from zephyr.shared.contracts.identity.permission import *  # noqa: F401,F403
