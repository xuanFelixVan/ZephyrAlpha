# [A_module] module_id=MOD-INT_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-160 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.core.enforcer
# [INVARIANTS] contract_purity: re-export only; impl in zephyr.integration.shared_08.contract_enforcer
# [MODIFY-GUARD] zephyr.integration.shared_08.contract_enforcer
# [CONSUMERS] zephyr.integration.shared_08.contracts.__init__; zephyr.integration.shared_08._contracts
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.enforcer import ContractViolationError, EnforcementMode, enforce, enforce_input, enforce_output"

from zephyr.integration.shared_08.contract_enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)

__all__ = [
    "ContractViolationError",
    "EnforcementMode",
    "enforce",
    "enforce_input",
    "enforce_output",
]