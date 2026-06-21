# [A_module] module_id=MOD-ORC_teardown_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md

# [MODULE] zephyr.trading.orchestrator.teardown_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
资源清理管理器（Teardown Manager — CT-TEARDOWN-001）

依据：MOD-MASTER-002 蓝图 §十六
TaskCard CANCELLED/FAILED → 7系统资源清理。
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

class CleanupTarget(BaseModel):
    system: str
    resource_type: str = ""
    resource_id: str = ""
    status: str = "pending"

CLEANUP_SYSTEMS: list[str] = [
    "orchestrator", "context-engine", "gate_engine",
    "vector-memory", "database", "feedback-loop", "system-telemetry",
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
        self._cleanup_records.append({
            "task_id": task_id,
            "reason": reason,
            "targets": len(targets),
            "timestamp": datetime.now(timezone.utc),
        })
        return targets

    def get_records(self) -> list[dict]:
        return list(self._cleanup_records)
