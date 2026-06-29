# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.infrastructure.db.query
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.__init__
# [CONSUMERS] task_repo;pipeline;audit
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读查询; 不修改任务状态; QueryMixin 无副作用
# [MODIFY-GUARD] task_repo.py 组合入口; base_repo.py _row_to_taskcard
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] QueryError;TaskNotFoundError
# [TESTS] tests/db/
# [A_module] module_id=MOD-INF_query | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""[BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md

query — 查询方法 Mixin（从 task_repo.py 拆分，SRC-0066）

=========================================================

本模块包含 TaskRepository 的所有查询逻辑：

- QueryMixin（list_by_* / query_tasks / search / count 等查询方法）

Safety : H（查询方法涉及任务管道核心数据访问）

"""

from __future__ import annotations

import fnmatch
import logging

logger = logging.getLogger(__name__)


from zephyr.infrastructure.db.base_repo import _row_to_taskcard
from zephyr.shared.task_types import TaskNamespace, TaskStatus

__all__ = ["QueryMixin"]


class QueryMixin:
    """查询方法 mixin — 供 TaskRepository 继承。



    需要宿主类提供:

    - self._conn: sqlite3.Connection

    - self._lock: threading.RLock

    """

    # ------------------------------------------------------------------

    # READ

    # ------------------------------------------------------------------

    def get(self, task_id: str):
        """按 task_id 查询有效任务（默认排除软删除行），不存在返回 None。"""

        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0",
            (task_id,),
        )

        row = cursor.fetchone()

        return _row_to_taskcard(row) if row else None

    def get_or_raise(self, task_id: str):
        """按 task_id 查询，不存在抛 TaskNotFoundError。"""

        from zephyr.infrastructure.db.base_repo import TaskNotFoundError

        task = self.get(task_id)

        if task is None:
            raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

        return task

    # ------------------------------------------------------------------

    # LIST 查询

    # ------------------------------------------------------------------

    def list_by_status(self, status: TaskStatus | str):
        """查询指定状态的所有任务（按 phase ASC, updated_at DESC 排序）。"""

        if isinstance(status, str):
            status = TaskStatus(status)

        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE status = ? AND is_deleted = 0 ORDER BY phase ASC, updated_at DESC",
            (status.value,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_phase(self, phase: int):
        """查询指定 Phase 的所有任务（按 status ASC, task_id ASC 排序）。"""

        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE phase = ? AND is_deleted = 0 ORDER BY status ASC, task_id ASC",
            (phase,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_session(self, session_id: str):
        """查询指定 session_id 的所有任务。"""

        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE session_id = ? AND is_deleted = 0 ORDER BY updated_at DESC",
            (session_id,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def query_tasks(
        self,
        *,
        phase: int | None = None,
        status: TaskStatus | str | None = None,
        session_id: str | None = None,
        file_path_glob: str | None = None,
        limit: int = 50,
    ):
        """复合条件列表（``task_manager.list_tasks`` / tool-contracts.yaml）。"""

        clauses = ["is_deleted = 0"]

        params: list[object] = []

        if phase is not None:
            clauses.append("phase = ?")

            params.append(phase)

        if status is not None:
            st = status.value if isinstance(status, TaskStatus) else str(status)

            clauses.append("status = ?")

            params.append(st)

        if session_id is not None:
            clauses.append("session_id = ?")

            params.append(session_id)

        where_sql = " AND ".join(clauses)

        cap = min(max(limit, 1), 500)

        fetch_limit = min(cap * 20, 2000) if file_path_glob else cap

        sql = f"SELECT * FROM tasks WHERE {where_sql} ORDER BY updated_at DESC LIMIT ?"

        params.append(fetch_limit)

        cursor = self._conn.execute(sql, tuple(params))

        tasks = [_row_to_taskcard(r) for r in cursor.fetchall()]

        if not file_path_glob:
            return tasks[:cap]

        matched: list = []

        for t in tasks:
            for r in self._conn.execute(
                "SELECT file_path FROM task_files WHERE task_id = ?",
                (t.task_id,),
            ):
                if fnmatch.fnmatch(r["file_path"], file_path_glob):
                    matched.append(t)

                    break

            if len(matched) >= cap:
                break

        return matched[:cap]

    def list_by_namespace(self, namespace: TaskNamespace | str):
        """查询指定命名空间的所有任务（按 seq ASC 排序）。"""

        if isinstance(namespace, TaskNamespace):
            namespace = namespace.value

        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE namespace = ? AND is_deleted = 0 ORDER BY seq ASC",
            (namespace,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_active(self):
        """查询活跃任务（IN_PROGRESS / READY / RETRY / WAITING），排除已删除。"""

        cursor = self._conn.execute(
            """

            SELECT * FROM tasks

            WHERE status IN ('IN_PROGRESS','READY','RETRY','WAITING')

              AND is_deleted = 0

            ORDER BY phase ASC, updated_at DESC

            """
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def count_by_status(self) -> dict[str, int]:
        """按状态统计任务数量（排除已删除）。"""

        cursor = self._conn.execute("SELECT status, COUNT(*) AS cnt FROM tasks WHERE is_deleted = 0 GROUP BY status")

        return {row["status"]: row["cnt"] for row in cursor.fetchall()}

    # ------------------------------------------------------------------

    # JSON1 查询（SH-DB-001 v2.0）

    # ------------------------------------------------------------------

    def list_by_dependency(self, dependency_task_id: str):
        """查询所有依赖给定 task_id 的任务（利用 JSON1 扩展遍历 depends_on JSON 数组）。"""

        cursor = self._conn.execute(
            """

            SELECT * FROM tasks

            WHERE is_deleted = 0

              AND json_valid(depends_on)

              AND EXISTS (

                  SELECT 1 FROM json_each(depends_on)

                  WHERE value = ?

              )

            ORDER BY phase ASC, updated_at DESC

            """,
            (dependency_task_id,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_tag(self, tag: str):
        """查询所有包含指定 tag 的任务（利用 JSON1 扩展遍历 tags JSON 数组）。"""

        cursor = self._conn.execute(
            """

            SELECT * FROM tasks

            WHERE is_deleted = 0

              AND json_valid(tags)

              AND EXISTS (

                  SELECT 1 FROM json_each(tags)

                  WHERE value = ?

              )

            ORDER BY phase ASC, updated_at DESC

            """,
            (tag,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_blocked_by(self, blocker_task_id: str):
        """查询所有被给定 task_id 阻塞的任务（利用 JSON1 扩展遍历 blocked_by JSON 数组）。"""

        cursor = self._conn.execute(
            """

            SELECT * FROM tasks

            WHERE is_deleted = 0

              AND json_valid(blocked_by)

              AND EXISTS (

                  SELECT 1 FROM json_each(blocked_by)

                  WHERE value = ?

              )

            ORDER BY phase ASC, updated_at DESC

            """,
            (blocker_task_id,),
        )

        return [_row_to_taskcard(r) for r in cursor.fetchall()]
