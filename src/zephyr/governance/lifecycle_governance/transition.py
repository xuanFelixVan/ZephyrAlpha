# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
# [MODULE] zephyr.governance.lifecycle_governance.transition
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.base_repo; zephyr.gov_enforcement.rule_enforcement.task_types; zephyr.gov_enforcement.rule_enforcement.gate_types.__init__; zephyr.governance.ops_governance.event_hook
# [CONSUMERS] task_repo;pipeline
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _ALLOWED_TRANSITIONS 唯一转换表; 状态机不可绕过; 依赖重算幂等
# [MODIFY-GUARD] base_repo.py 状态机表; task_repo.py 组合入口
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError;DependencyError
# [TESTS] tests/db/
# [A_module] module_id=MOD-DAT_transition | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md

transition — 状态机转换 Mixin（从 task_repo.py 拆分，SRC-0066）

===============================================================

本模块包含 TaskRepository 的状态机转换逻辑：

- TransitionMixin（transition() + _recalculate_dependent_status()）

Safety : H（状态机错误会影响整个任务流水线）

"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


from zephyr.governance.persistence.base_repo import (
    InvalidTransitionError,
    TaskNotFoundError,
    _is_valid_transition,
    _row_to_taskcard,
    now_iso,
)
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus

__all__ = ["GateResult", "GateViolationError", "TransitionMixin"]


# Re-export GateViolationError / GateResult for backward compat

from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult, GateViolationError

# PENDING -> IN_PROGRESS 转换时触发的门禁 ID

_STARTUP_GATE_ID = "G1"


class TransitionMixin:
    """状态机转换 mixin — 供 TaskRepository 继承。



    需要宿主类提供:

    - self._should_evaluate_gate(gate_id: str) -> bool

    - self._gate_engine: GateEngine | None

    - self._conn: sqlite3.Connection

    - self._lock: threading.RLock

    - self._write_tx() -> Iterator[sqlite3.Connection]

    - self._fetch_row(conn, task_id) -> sqlite3.Row | None

    - self._record_event(conn, event_type, payload, task_id=None, session_id=None)

    """

    # ------------------------------------------------------------------

    # TRANSITION（状态机）

    # ------------------------------------------------------------------

    def transition(
        self,
        task_id: str,
        to_status: TaskStatus | str,
        *,
        session_id: str | None = None,
        waiting_for: str | None = None,
        note: str | None = None,
    ):
        """

        执行状态机转换。



        参数

        ----

        task_id   : str           目标任务 ID

        to_status : TaskStatus    目标状态

        session_id : str | None   当前 session ID（写入 events）

        waiting_for : str | None  WAITING 状态时填写等待原因

        note : str | None         本次转换的备注（写入 events payload）



        异常

        ----

        TaskNotFoundError      — task_id 不存在

        InvalidTransitionError — 非法状态转换



        返回

        ----

        Task

            转换后重新读取的 Task 对象。

        """

        if isinstance(to_status, str):
            to_status = TaskStatus(to_status)

        try:
            with self._write_tx() as conn:
                row = self._fetch_row(conn, task_id)

                if row is None:
                    raise TaskNotFoundError("任务不存在")

                # G1 门禁检查在写事务内执行，与状态转换原子落盘

                # GateEngine 接受外部 conn，不再管理独立事务

                self._evaluate_transition_gate(conn, row, to_status)

                from_status = TaskStatus(row["status"])

                if not _is_valid_transition(from_status, to_status):
                    raise InvalidTransitionError(
                        f"非法转换 {from_status.value} -> {to_status.value}（task_id={task_id!r}）"
                    )

                self._apply_status_update(conn, task_id, to_status, session_id, waiting_for)

                self._record_event(
                    conn,
                    "state_transition",
                    {
                        "from": from_status.value,
                        "to": to_status.value,
                        "task_id": task_id,
                        "note": note or "",
                    },
                    task_id=task_id,
                    session_id=session_id,
                )

                self._recalculate_dependent_status(conn, task_id, to_status)

                updated_row = self._fetch_row(conn, task_id)

        except GateViolationError as exc:
            # 写事务 ROLLBACK 会撤销同 conn 下的 gates INSERT；用独立连接再写一条，保证失败可审计。

            if self._gate_engine is not None:
                self._gate_engine._persist_result(exc.result, conn=None)

            raise

        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.3 修复: assert->if/raise

        from zephyr.governance.ops_governance.event_hook import TransitionEvent, hook_registry

        hook_registry.fire(
            TransitionEvent(
                task_id=task_id,
                from_status=from_status.value,
                to_status=to_status.value,
                note=note or "",
                session_id=session_id,
            )
        )

        return _row_to_taskcard(updated_row)

    def _evaluate_transition_gate(self, conn, row, to_status):
        """评估 PENDING->IN_PROGRESS (G1) 与 *->COMPLETED (G7) 门禁。

        门禁未启用或不适用时直接返回；评估未通过时抛出 GateViolationError，
        由 transition() 的 except 块统一持久化失败结果。
        """
        if not self._enable_gate or self._gate_engine is None:
            return

        if to_status == TaskStatus.IN_PROGRESS:
            gate_id = _STARTUP_GATE_ID
        elif to_status == TaskStatus.COMPLETED:
            gate_id = "G7"
        else:
            return

        task_obj = _row_to_taskcard(row)

        gate_result = self._gate_engine.evaluate(task_obj, gate_id, conn=conn)

        if not gate_result.passed:
            raise GateViolationError(gate_result)

    def _apply_status_update(self, conn, task_id, to_status, session_id, waiting_for):
        """落盘状态转换 UPDATE，按目标状态设置 ready_at / completed_at / block_sessions_count。"""
        now = now_iso()

        set_ready_at = to_status == TaskStatus.READY

        set_completed_at = to_status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)

        increment_block_count = to_status == TaskStatus.BLOCKED

        conn.execute(
            """
            UPDATE tasks
            SET status = ?, session_id = COALESCE(?, session_id),
                waiting_for = ?,
                ready_at = CASE WHEN ? THEN ? ELSE ready_at END,
                completed_at = CASE WHEN ? THEN COALESCE(completed_at, ?) ELSE completed_at END,
                block_sessions_count = CASE WHEN ? THEN block_sessions_count + 1 ELSE block_sessions_count END,
                updated_at = ?
            WHERE task_id = ?
            """,
            (
                to_status.value,
                session_id,
                waiting_for,
                1 if set_ready_at else 0,
                now if set_ready_at else None,
                1 if set_completed_at else 0,
                now if set_completed_at else None,
                1 if increment_block_count else 0,
                now,
                task_id,
            ),
        )

    def _recalculate_dependent_status(
        self,
        conn,
        changed_task_id: str,
        new_status: TaskStatus,
    ) -> None:
        """当子任务状态变更时，重算依赖它的父任务状态。



        规则（蓝图 MOD-TASK_SYSTEM 盲点#1）：

        - 所有子任务 COMPLETED/VERIFIED -> 父任务 READY（解锁继续施工）

        - 任一子任务 FAILED/CANCELLED -> 父任务 BLOCKED

        - 否则不改变父任务状态

        """

        if new_status not in (
            TaskStatus.COMPLETED,
            TaskStatus.VERIFIED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ):
            return

        cursor = conn.execute(
            "SELECT task_id FROM tasks WHERE is_deleted = 0 AND depends_on LIKE ?",
            (f"%{changed_task_id}%",),
        )

        parent_rows = cursor.fetchall()

        for parent_row in parent_rows:
            parent_task_id = parent_row["task_id"]

            parent = _row_to_taskcard(self._fetch_row(conn, parent_task_id))

            if parent is None or not parent.depends_on:
                continue

            child_statuses: list[TaskStatus] = []

            all_resolved = True

            any_failed = False

            for dep_id in parent.depends_on:
                child_row = self._fetch_row(conn, dep_id)

                if child_row is None:
                    continue

                child_status = TaskStatus(child_row["status"])

                child_statuses.append(child_status)

                if child_status not in (TaskStatus.COMPLETED, TaskStatus.VERIFIED):
                    all_resolved = False

                if child_status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
                    any_failed = True

            if not child_statuses:
                continue

            parent_status = TaskStatus(parent.status.value)

            if all_resolved and parent_status in (TaskStatus.BLOCKED, TaskStatus.WAITING, TaskStatus.PENDING):
                conn.execute(
                    "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                    (TaskStatus.READY.value, now_iso(), parent_task_id),
                )

                self._record_event(
                    conn,
                    "state_transition",
                    {
                        "from": parent_status.value,
                        "to": TaskStatus.READY.value,
                        "task_id": parent_task_id,
                        "note": f"所有子任务已完成（触发者: {changed_task_id}）",
                    },
                    task_id=parent_task_id,
                )

            elif any_failed and parent_status not in (TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.VERIFIED):
                conn.execute(
                    "UPDATE tasks SET status = ?, updated_at = ?, block_sessions_count = block_sessions_count + 1 WHERE task_id = ?",
                    (TaskStatus.BLOCKED.value, now_iso(), parent_task_id),
                )

                self._record_event(
                    conn,
                    "state_transition",
                    {
                        "from": parent_status.value,
                        "to": TaskStatus.BLOCKED.value,
                        "task_id": parent_task_id,
                        "note": f"子任务失败触发阻塞（触发者: {changed_task_id}）",
                    },
                    task_id=parent_task_id,
                )
