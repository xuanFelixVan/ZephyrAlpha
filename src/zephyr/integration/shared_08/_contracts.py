# [A_module] module_id=MOD-INT__contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._contracts
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [CONSUMERS] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"

from zephyr.integration.shared_08.contracts.approval_types import ApprovalRequest
from zephyr.integration.shared_08.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.integration.shared_08.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.integration.shared_08.contracts.core.timestamp import Timestamp, ensure_utc, utcnow
from zephyr.integration.shared_08.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)
