# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.enforcer
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contract_enforcer
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.enforcer
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.enforcer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.enforcer import ContractViolationError, EnforcementMode, enforce, enforce_input, enforce_output"
# [A_module] module_id=MOD-INT_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.enforcer。"""
from zephyr.shared.contracts.core.enforcer import *  # noqa: F401,F403
