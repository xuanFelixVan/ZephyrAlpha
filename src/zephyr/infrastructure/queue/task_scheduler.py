# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.queue.task_scheduler
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_task_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Task Scheduler — 任务调度器。

依据：
    蓝图 MOD-TASK_SYSTEM §6.13.2 + v0.6.0
    任务卡 TASK-INF-0123
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT


class ScheduleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    schedule_id: str
    task_id: str
    scheduled_at: str
    started_at: str = ""
    completed_at: str = ""
    status: ScheduleStatus = ScheduleStatus.PENDING
    assigned_model: str = "deepseek"
    assigned_pipeline: str = "A"
    estimated_tokens: int = 0
    timeout_minutes: int = 60


@dataclass
class ScheduleResult:
    total_scheduled: int
    started: int
    completed: int
    failed: int
    tasks: list[ScheduledTask]


class TaskScheduler:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or (REPO_ROOT / "data" / "queue")
        self._schedule_path = self._data_dir / "schedules.jsonl"
        self._tasks: dict[str, ScheduledTask] = {}

    def schedule(self, task_id: str, estimated_tokens: int = 0) -> ScheduledTask:
        scheduled = ScheduledTask(
            schedule_id=f"SCHED-{task_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            task_id=task_id,
            scheduled_at=datetime.now(UTC).isoformat(),
            estimated_tokens=estimated_tokens,
        )

        self._tasks[scheduled.schedule_id] = scheduled
        self._persist_task(scheduled)

        return scheduled

    def start(self, schedule_id: str) -> ScheduledTask | None:
        task = self._tasks.get(schedule_id)
        if task:
            task.status = ScheduleStatus.RUNNING
            task.started_at = datetime.now(UTC).isoformat()
            self._persist_task(task)
        return task

    def complete(self, schedule_id: str) -> ScheduledTask | None:
        task = self._tasks.get(schedule_id)
        if task:
            task.status = ScheduleStatus.COMPLETED
            task.completed_at = datetime.now(UTC).isoformat()
            self._persist_task(task)
        return task

    def fail(self, schedule_id: str) -> ScheduledTask | None:
        task = self._tasks.get(schedule_id)
        if task:
            task.status = ScheduleStatus.FAILED
            task.completed_at = datetime.now(UTC).isoformat()
            self._persist_task(task)
        return task

    def cancel(self, schedule_id: str) -> ScheduledTask | None:
        task = self._tasks.get(schedule_id)
        if task:
            task.status = ScheduleStatus.CANCELLED
            self._persist_task(task)
        return task

    def get_pending(self) -> list[ScheduledTask]:
        return [t for t in self._tasks.values() if t.status == ScheduleStatus.PENDING]

    def get_stats(self) -> dict[str, int]:
        stats: dict[str, int] = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
        for task in self._tasks.values():
            stats[task.status.value] += 1
        return stats

    def _persist_task(self, task: ScheduledTask) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._schedule_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "schedule_id": task.schedule_id,
                        "task_id": task.task_id,
                        "scheduled_at": task.scheduled_at,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "status": task.status.value,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
