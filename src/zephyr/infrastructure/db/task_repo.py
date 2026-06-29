# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §task-system
# [MODULE] zephyr.infrastructure.db.task_repo
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.persistence.task_repo
# [CONSUMERS] Backward-compatible import path for legacy consumers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Re-export wrapper only; authoritative implementation at zephyr.data.persistence.task_repo
# [MODIFY-GUARD] Do not add logic here; all changes must go to zephyr.data.persistence.task_repo
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] Delegates to zephyr.data.persistence.task_repo
# [TESTS] tests/test_mcp_task_claim.py; tests/test_boot_hooks_unlock.py
# [A_module] module_id=MOD-INF_task_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Backward-compatible re-export wrapper.

Authoritative implementation: zephyr.data.persistence.task_repo
This module re-exports all public names for legacy import paths.
New code should import from zephyr.governance.persistence.task_repo directly.
"""

from zephyr.governance.persistence.task_repo import *  # noqa: F403
from zephyr.governance.persistence.task_repo import (  # noqa: F401 — explicit re-exports for type checkers
    CIRCULAR_ACCEPTANCE_ROUNDS,
    CircularAcceptanceError,
    GateResult,
    GateViolationError,
    InvalidTransitionError,
    P0InflationFrozenError,
    P0InflationWarning,
    RejectedUpgradeCoolingOffError,
    RootCauseRequiredError,
    SyncVerificationError,
    TaskNotFoundError,
    TaskRepository,
    TaskRepositoryError,
    UnclaimedOperationError,
    allowed_transitions,
    is_terminal,
    search,
)
