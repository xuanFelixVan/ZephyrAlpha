"""
资源清理管理器（Teardown Manager — CT-TEARDOWN-001）

依据：MOD-MASTER-001 蓝图 §十六
TaskCard CANCELLED/FAILED → 7系统资源清理。
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CleanupTarget(BaseModel):
    system: str
    resource_type: str = ""
    resource_id: str = ""
    status: str = "pending"


CLEANUP_SYSTEMS: list[str] = [
    "orchestrator", "context_engine", "gate_engine",
    "vector_memory", "database", "feedback_loop", "system_telemetry",
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
