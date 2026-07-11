from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.teardown_manager
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_teardown_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
资源清理管理器（Teardown Manager — CT-TEARDOWN-001）

依据：MOD-MASTER-002 蓝图 §十六
TaskCard CANCELLED/FAILED -> 7系统资源清理。
"""

from datetime import UTC, datetime

from pydantic import BaseModel


class CleanupTarget(BaseModel):
    system: str
    resource_type: str = ""
    resource_id: str = ""
    status: str = "pending"


CLEANUP_SYSTEMS: Final[list[str]] = [
    "orchestrator",
    "context-engine",
    "gate_engine",
    "vector-memory",
    "database",
    "feedback-loop",
    "system-telemetry",
]


class TeardownManager:
    def __init__(self):
        self._cleanup_records: list[dict] = []

    def teardown(self, task_id: str, reason: str) -> list[CleanupTarget]:
        targets: list[CleanupTarget] = []
        for system in CLEANUP_SYSTEMS:
            target = CleanupTarget(
                system=system,
                resource_type="task_context",
                resource_id=task_id,
                status="cleaned",
            )
            targets.append(target)
        self._cleanup_records.append(
            {
                "task_id": task_id,
                "reason": reason,
                "targets": len(targets),
                "timestamp": datetime.now(UTC),
            }
        )
        return targets

    def get_records(self) -> list[dict]:
        return list(self._cleanup_records)
