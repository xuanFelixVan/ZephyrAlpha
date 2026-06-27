# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.external.ext_004
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.external.__init__
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.external.ext_004
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.external.ext_004
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.external.ext_004"
# [A_module] module_id=MOD-INT_ext_004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.external.ext_004。"""

from zephyr.shared.contracts.external.ext_004 import *  # noqa: F401,F403
