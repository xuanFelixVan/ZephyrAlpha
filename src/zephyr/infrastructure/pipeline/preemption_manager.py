# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.preemption_manager
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.__init__; zephyr.governance.persistence.task_repo
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
# [A_module] module_id=MOD-INF_preemption_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
PreemptionManager -- 优先级抢占管理器
======================================
对标 K8s Priority Preemption.

P0/P1 任务可抢占 P2/P3 任务。被抢占的任务迁移到 WAITING 状态,
高优先级任务完成后可 resume.

通过依赖注入解耦外部系统:
- task_repo: 用于查询活跃任务和修改任务状态
- dispatched_ids / active_dispatches: 内存幂等集 (通过引用传递)
- re_dispatch_callback: 重新分发被抢占任务的回调函数

SRC-0027: 从 PipelineOrchestrator 提取.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from zephyr.infrastructure.pipeline.models import PreemptionRecord
from zephyr.shared.io.serialization import filter_dataclass_fields
from zephyr.shared.schema.task_types import TaskStatus

if TYPE_CHECKING:
    from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.utils.time_utils import now_utc


class PreemptionManager:
    """优先级抢占管理器.

    通过依赖注入完全解耦 PipelineOrchestrator:
    - ``task_repo``: 用于 list/get/transition 任务状态
    - ``dispatched_ids``: PO 的 ``_dispatched_ids`` 集合 (引用传递, 直接修改)
    - ``active_dispatches``: PO 的 ``_active_dispatches`` 集合 (引用传递, 直接修改)
    - ``re_dispatch_callback``: 重新分发任务回调, 等价于 ``lambda task: po.dispatch(task)``
    """

    _PREEMPTIBLE_PRIORITIES: ClassVar[frozenset[str]] = frozenset({"P3", "P2"})

    def __init__(
        self,
        task_repo: TaskRepository | None,
        dispatched_ids: set[str],
        active_dispatches: set[str],
        re_dispatch_callback: Callable[..., Any],
        priority_cutoff: str = "P2",
    ) -> None:
        self._task_repo = task_repo
        self._dispatched_ids = dispatched_ids
        self._active_dispatches = active_dispatches
        self._re_dispatch = re_dispatch_callback
        self._priority_cutoff = priority_cutoff
        self._preempt_log: dict[str, PreemptionRecord] = {}

    # ------------------------------------------------------------------
    # 蓝图接口
    # ------------------------------------------------------------------

    def should_preempt(self, new_priority: str, current_priority: str) -> bool:
        """静态抢占判定: P0/P1 可抢占 P2/P3.

        Returns
        -------
        bool
            True 如果 new_priority 可抢占 current_priority.
        """
        new = str(new_priority or "").upper().strip()
        cur = str(current_priority or "").upper().strip()
        return new in ("P0", "P1") and cur in self._PREEMPTIBLE_PRIORITIES

    def preempt(self, task_card: object) -> list[PreemptionRecord]:
        """检查并执行优先级抢占.

        仅当 task_card 优先级为 P0/P1 时才执行抢占逻辑.
        查询所有 IN_PROGRESS 的低优先级任务 (P2/P3),
        将其迁移到 WAITING 状态并从幂等集中移除.

        Parameters
        ----------
        task_card : Any
            具有 ``task_id`` 和 ``priority`` 属性的任务卡片.

        Returns
        -------
        list[PreemptionRecord]
            被抢占任务的记录列表.
        """
        if self._task_repo is None:
            return []

        pri_raw = getattr(task_card.priority, "value", task_card.priority)
        pri = str(pri_raw or "").upper().strip()
        if pri not in ("P0", "P1"):
            return []

        records: list[PreemptionRecord] = []
        try:
            preemptible = self._task_repo.list(
                status=TaskStatus.IN_PROGRESS,
                limit=50,
            )
        except (TypeError, AttributeError):
            return []

        for t in preemptible:
            tp_raw = getattr(getattr(t, "priority", None), "value", getattr(t, "priority", ""))
            tp = str(tp_raw or "").upper().strip()
            if tp not in self._PREEMPTIBLE_PRIORITIES:
                continue

            try:
                self._task_repo.transition(
                    t.task_id,
                    TaskStatus.WAITING,
                    waiting_for=f"pipeline_preempted:{task_card.task_id}",
                )
            except Exception:
                continue

            self._dispatched_ids.discard(t.task_id)
            self._active_dispatches.discard(t.task_id)

            record = PreemptionRecord(
                preempted_task_id=t.task_id,
                preempted_by_task_id=task_card.task_id,
                preempted_priority=tp,
            )
            self._preempt_log[t.task_id] = record
            records.append(record)

        return records

    def resume_preempted(self, completed_task_id: str) -> list[Any]:
        """完成高优先级任务后, 恢复被其抢占的低优先级任务并重新 dispatch.

        Parameters
        ----------
        completed_task_id : str
            刚完成的高优先级任务 ID.

        Returns
        -------
        list[Any]
            重新 dispatch 的结果列表 (类型取决于 re_dispatch_callback 返回值).
        """
        results: list[Any] = []
        if self._task_repo is None:
            return results

        for tid, record in list(self._preempt_log.items()):
            if record.preempted_by_task_id != completed_task_id:
                continue
            if record.resumed_at is not None:
                continue

            task = self._task_repo.get(tid)
            if task is None:
                continue
            try:
                if task.status == TaskStatus.WAITING:
                    self._task_repo.transition(tid, TaskStatus.READY)
                elif task.status == TaskStatus.READY:
                    pass
                else:
                    continue
                task = self._task_repo.get(tid)
            except Exception:
                continue
            if task is None:
                continue

            self._dispatched_ids.discard(tid)
            self._active_dispatches.discard(tid)

            result = self._re_dispatch(task)
            record.resumed_at = now_utc().isoformat()
            results.append(result)

        return results

    # ------------------------------------------------------------------
    # 状态持久化
    # ------------------------------------------------------------------

    def save_state(self) -> dict:
        """导出抢占状态 (供 PO 的 save_state 合并使用)."""
        return {
            "preempt_log": {k: v.model_dump() for k, v in self._preempt_log.items()},
            "priority_cutoff": self._priority_cutoff,
        }

    def load_state(self, state: dict) -> None:
        """从持久化字典恢复抢占状态。"""
        preempt_raw = state.get("preempt_log", {})
        self._preempt_log = {tid: PreemptionRecord(**filter_dataclass_fields(PreemptionRecord, data)) for tid, data in preempt_raw.items()}
        self._priority_cutoff = state.get("priority_cutoff", "P2")

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def log(self) -> dict[str, PreemptionRecord]:
        """抢占日志只读副本。"""
        return dict(self._preempt_log)

    @property
    def priority_cutoff(self) -> str:
        """当前优先级截断值。"""
        return self._priority_cutoff

    @property
    def active_count(self) -> int:
        """活跃抢占数 (``resumed_at`` 为 None 的记录数)."""
        return sum(1 for r in self._preempt_log.values() if r.resumed_at is None)
