# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.task_progress
# [DOMAIN] D-INFRA_OPS
# [DEPENDENCIES] zephyr.infra_ops.dashboard.components.gate_statistics
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
# [A_module] module_id=MOD-INF_task_progress | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# AI-generated: T-4-07 Task Progress Component
"""
TaskProgressComponent · 任务进度看板（4 进度）
======================================================
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PhaseProgress:
    phase: int
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks


@dataclass
class TaskProgressData:
    phases: list[PhaseProgress] = field(default_factory=list)
    total_tasks: int = 0
    total_completed: int = 0

    @property
    def overall_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.total_completed / self.total_tasks


def fetch_task_progress(task_repo: Any = None) -> TaskProgressData:
    data = TaskProgressData()
    for phase in range(5):
        pp = PhaseProgress(phase=phase)
        if task_repo is not None:
            try:
                tasks = task_repo.list_by_phase(phase)
                pp.total_tasks = len(tasks)
                pp.completed_tasks = sum(1 for t in tasks if t.status.value in ("COMPLETED", "VERIFIED"))
                pp.in_progress_tasks = sum(1 for t in tasks if t.status.value == "IN_PROGRESS")
                pp.failed_tasks = sum(1 for t in tasks if t.status.value == "FAILED")
                pp.pending_tasks = sum(1 for t in tasks if t.status.value == "PENDING")
            except Exception:
                pass
        data.phases.append(pp)
        data.total_tasks += pp.total_tasks
        data.total_completed += pp.completed_tasks
    return data


def render_task_progress(data: TaskProgressData) -> dict[str, Any]:
    return {
        "overall_rate": round(data.overall_rate, 4),
        "total_tasks": data.total_tasks,
        "total_completed": data.total_completed,
        "phases": [
            {
                "phase": pp.phase,
                "total": pp.total_tasks,
                "completed": pp.completed_tasks,
                "in_progress": pp.in_progress_tasks,
                "failed": pp.failed_tasks,
                "pending": pp.pending_tasks,
                "completion_rate": round(pp.completion_rate, 4),
            }
            for pp in data.phases
        ],
    }
