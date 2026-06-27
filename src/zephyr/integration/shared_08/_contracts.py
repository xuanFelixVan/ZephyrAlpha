# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.integration.shared_08._contracts
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.approval_types; zephyr.integration.shared_08.contracts.core.enforcer; zephyr.integration.shared_08.contracts.core.runtime_plane_tag; zephyr.integration.shared_08.contracts.core.timestamp; zephyr.integration.shared_08.contracts.rollback_types
# [CONSUMERS] zephyr.shared.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"
# [A_module] module_id=MOD-INT__contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""_contracts — 契约 re-export 桥接层。

从 contracts 子包 re-export 符号，保持 zephyr.shared 向后兼容。
"""

from zephyr.integration.shared_08.contracts.approval_types import ApprovalRequest
from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.core.timestamp import (
    Timestamp,
    ensure_utc,
    utcnow,
)
from zephyr.integration.shared_08.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)

__all__ = [
    "COLD_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "HOT_PATH_ACTIVATED",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "ApprovalRequest",
    "ContractViolationError",
    "EnforcementMode",
    "RollbackResult",
    "RollbackStatus",
    "RuntimePlane",
    "Timestamp",
    "ValidationResult",
    "enforce",
    "enforce_input",
    "enforce_output",
    "ensure_utc",
    "utcnow",
]
