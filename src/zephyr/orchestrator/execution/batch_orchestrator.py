# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.batch_orchestrator
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.contracts.orchestration_protocol; zephyr.shared.contracts.task_repository_protocol; zephyr.shared.models
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
# [A_module] module_id=MOD-ORC_batch_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""BatchOrchestrator — 多 Worker 批量任务协调器（MOD-INF-016）

SQLite 原子 claim（UPDATE ... RETURNING）+ DAG 依赖感知 + 超时回收。

设计原则
--------
- 零外部依赖：SQLite 即 Broker + Lock + Checkpoint
- 原子认领：UPDATE ... RETURNING 保证 13 个 AI 对话不重复抢任务
- 依赖感知：depends_on 未满足的任务自动过滤
- 自愈：超时未完成的 IN_PROGRESS 任务自动回收到 READY

Usage（每个 TRAE AI 对话侧）::

    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.trading.orchestrator.execution.batch_orchestrator import BatchOrchestrator

    repo = TaskRepository(DB_PATH)
    bo = BatchOrchestrator(repo, batch_id="construction-20260507",
                           worker_id="session-20260507-001")

    bo.recover_stale_claims()          # 回收死任务

    while (card := bo.claim_next()):
        print(f"  Claimed: {card.task_id} — {card.title}")
        try:
            # ... 施工逻辑 ...
            bo.mark_done(card.task_id)
        except Exception as e:
            bo.mark_failed(card.task_id, str(e))

    print(bo.progress())    # -> {'READY': 0, 'IN_PROGRESS': 0,
                            #    'COMPLETED': 943, 'FAILED': 2, 'TOTAL': 945}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.shared.foundation.models import TaskCard



@dataclass
class BatchProgress:
    batch_id: str
    ready: int = 0
    in_progress: int = 0
    completed: int = 0
    failed: int = 0
    total: int = 0
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def pct_done(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.completed + self.failed) / self.total * 100, 1)

    def __str__(self) -> str:
        return (
            f"[{self.batch_id}] {self.completed}/{self.total} ({self.pct_done}%)"
            f" | {self.in_progress} IN_PROGRESS | {self.failed} FAILED"
            f" | {self.ready} READY"
        )


class BatchOrchestrator:  # 5.143.3 修复: 移除Protocol显式继承, Protocol应为结构化子类型不应继承
    """多 Worker 批量任务协调器。

    每个 AI session 创建一个实例，共享同一个 SQLite 数据库。
    """

    def __init__(
        self,
        repo: TaskRepositoryProtocol,
        batch_id: str,
        worker_id: str,
        *,
        stale_timeout_minutes: int = 30,
    ) -> None:
        self._repo = repo
        self.batch_id = batch_id
        self.worker_id = worker_id
        self._stale_timeout = stale_timeout_minutes

    def claim_next(self) -> TaskCard | None:
        """原子认领下一个依赖已满足的 READY 任务。

        先回收超时任务，再认领。
        返回 None 表示无可认领任务。
        """
        self.recover_stale_claims()
        return self._repo.claim_next(self.batch_id, self.worker_id)

    def mark_done(self, task_id: str) -> None:
        self._repo.transition(task_id, "COMPLETED")

    def mark_failed(self, task_id: str, reason: str = "") -> None:
        self._repo.transition(task_id, "FAILED")

    def recover_stale_claims(self) -> int:
        """释放超时未完成的 IN_PROGRESS 任务 -> 回到 READY。"""
        return self._repo.recover_stale_claims(self.batch_id, self._stale_timeout)

    def progress(self) -> BatchProgress:
        """返回批量进度快照。"""
        raw = self._repo.batch_progress(self.batch_id)
        return BatchProgress(
            batch_id=self.batch_id,
            ready=raw["READY"],
            in_progress=raw["IN_PROGRESS"],
            completed=raw["COMPLETED"],
            failed=raw["FAILED"],
            total=raw["TOTAL"],
        )
