# [A_module] module_id=MOD-INT_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-162 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.core.registry
# [INVARIANTS] contract_purity: re-export only; impl in zephyr.integration.shared_08.contract_versions
# [MODIFY-GUARD] zephyr.integration.shared_08.contract_versions
# [CONSUMERS] zephyr.integration.shared_08.contracts.__init__; zephyr.integration.shared_08._contracts
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.registry import ContractRegistry, ContractMeta, VersionMismatchError, VersionTransition, get_registry, reset_registry"

from zephyr.integration.shared_08.contract_versions import (
    ContractMeta,
    ContractRegistry,
    VersionMismatchError,
    VersionTransition,
    get_registry,
    reset_registry,
)

__all__ = [
    "ContractMeta",
    "ContractRegistry",
    "VersionMismatchError",
    "VersionTransition",
    "get_registry",
    "reset_registry",
]
