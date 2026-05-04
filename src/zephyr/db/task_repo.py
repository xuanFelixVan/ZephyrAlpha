"""
TaskRepository — 任务登记表 CRUD + 状态机（T-1-04）
====================================================
依据：ADR-0030（SQLite 元数据层）+ ADR-0040（Pydantic v2 契约）

Safety : H（基础设施核心，状态机错误会影响整个任务流水线）

功能
----
- create / get / update / delete CRUD
- 状态机转换（10 状态）+ 非法转换拒绝
- 每次状态转换自动写 events 表（state_transition 事件）
- 按 phase / status / session_id 列表查询
- 批量 upsert（Phase 0 补录用）

状态转换表（合法路径，#13 裁定：对齐 Jira/ITIL 标准）
---------------------
  PENDING     → IN_PROGRESS, BLOCKED, CANCELLED
  IN_PROGRESS → COMPLETED, FAILED, BLOCKED, WAITING
  COMPLETED   → VERIFIED, IN_PROGRESS
  VERIFIED    → （终态，无出边）
  FAILED      → RETRY, CANCELLED
  BLOCKED     → READY, CANCELLED
  WAITING     → READY, CANCELLED
  READY       → IN_PROGRESS, CANCELLED
  RETRY       → IN_PROGRESS, FAILED
  CANCELLED   → （终态，无出边）

  注 1：COMPLETED → IN_PROGRESS 为验证失败返工路径（替代原 COMPLETED → CANCELLED）。
  依据：Jira/ServiceNow/Linear/Azure DevOps 均不允许 COMPLETED → CANCELLED 直转；
  ITIL v4 / ISO 10006 / CMMI 要求验证不通过走纠正措施循环（返回执行）。
  注 2：RETRY → FAILED 为重试失败路径（替代原 RETRY → CANCELLED）。
  取消只能从 FAILED 发起（FAILED → CANCELLED），RETRY 不直接取消。
  依据：Jira/ServiceNow 要求重试失败先回到 FAILED 状态再决定取消，保持审计轨迹。

线程安全
--------
单实例使用 threading.RLock 串行化写操作；读操作直接执行（WAL 允许并发读）。
与 ADR-0030 §4.5 "单 Writer 假设"一致。
"""
from __future__ import annotations

import json
import sqlite3
from threading import RLock
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from zephyr.db.sqlite_schema import DB_PATH, get_db_connection, init_db
from zephyr.gates.gate_engine import (
    GATES_DIR,
    GateEngine,
    GateResult,
    GateViolationError,
)
from zephyr.core.models import TaskCard
from zephyr.shared.schemas import Priority, SafetyLevel, Task, TaskNamespace, TaskStatus
from zephyr.shared.time_utils import now_iso

__all__ = [
    "TaskRepository",
    "TaskNotFoundError",
    "InvalidTransitionError",
    "TaskRepositoryError",
    "GateViolationError",
    "GateResult",
]

# PENDING → IN_PROGRESS 转换时触发的门禁 ID
_STARTUP_GATE_ID = "G1"

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class TaskRepositoryError(RuntimeError):
    """TaskRepository 基础异常。"""


class TaskNotFoundError(TaskRepositoryError):
    """task_id 不存在。"""


class InvalidTransitionError(TaskRepositoryError):
    """非法状态转换。"""


# ---------------------------------------------------------------------------
# 状态机转换表
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.PENDING: frozenset({
        TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED,
    }),
    TaskStatus.IN_PROGRESS: frozenset({
        TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.BLOCKED, TaskStatus.WAITING,
    }),
    TaskStatus.COMPLETED: frozenset({
        TaskStatus.VERIFIED, TaskStatus.IN_PROGRESS,
    }),
    TaskStatus.VERIFIED: frozenset(),        # 终态
    TaskStatus.FAILED: frozenset({
        TaskStatus.RETRY, TaskStatus.CANCELLED,
    }),
    TaskStatus.BLOCKED: frozenset({
        TaskStatus.READY, TaskStatus.CANCELLED,
    }),
    TaskStatus.WAITING: frozenset({
        TaskStatus.READY, TaskStatus.CANCELLED,
    }),
    TaskStatus.READY: frozenset({
        TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED,
    }),
    TaskStatus.RETRY: frozenset({
        TaskStatus.IN_PROGRESS, TaskStatus.FAILED,
    }),
    TaskStatus.CANCELLED: frozenset(),       # 终态
}


def _is_valid_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    return to_status in _ALLOWED_TRANSITIONS.get(from_status, frozenset())


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

_UTC = timezone.utc


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。"""
    return datetime.now(_UTC).isoformat()


def _new_id(prefix: str = "") -> str:
    """生成带可选前缀的 UUID4 字符串。"""
    uid = str(uuid.uuid4())
    return f"{prefix}{uid}" if prefix else uid


def _row_to_taskcard(row: sqlite3.Row) -> TaskCard:
    """将 sqlite3.Row 转换为 TaskCard Pydantic 模型（含全部 52 字段）。"""
    d = dict(row)
    _json_array_fields = (
        "files_in_scope", "deliverables", "acceptance", "depends_on", "tags",
        "upstream_files", "downstream_outputs", "allowed_touch", "forbidden_touch",
        "applicable_rules", "context_assembly_manifest", "completed_gates",
        "pipeline_modules", "blocked_by", "artifact_paths", "audit_findings",
        "ke_entries", "autonomy_checklist",
    )
    for field in _json_array_fields:
        raw = d.get(field, "[]")
        d[field] = json.loads(raw) if isinstance(raw, str) else raw

    _json_dict_fields = ("blocked_gates",)
    for field in _json_dict_fields:
        raw = d.get(field, "{}")
        d[field] = json.loads(raw) if isinstance(raw, str) else raw

    d["idempotent"] = bool(d.get("idempotent", 0))
    if "name" in d and "title" not in d:
        d["title"] = d.pop("name")

    if not d.get("source_blueprint", "").strip():
        d["source_blueprint"] = "unknown"
    if not d.get("source_section", "").strip():
        d["source_section"] = "unknown"
    if len(d.get("description", "") or "") < 10:
        d["description"] = d.get("title", "Untitled") + " — 自动恢复描述字段"
    if d.get("estimated_tokens", 0) < 500:
        d["estimated_tokens"] = 500
    if d.get("timeout_minutes", 0) < 5:
        d["timeout_minutes"] = 5

    return TaskCard.model_validate(d)


# ---------------------------------------------------------------------------
# TaskRepository
# ---------------------------------------------------------------------------


class TaskRepository:
    """
    任务登记表的 CRUD + 状态机入口。

    参数
    ----
    db_path
        SQLite 数据库路径；默认使用 DB_PATH。
    auto_init
        为 True 时在首次连接时调用 ``init_db()``（默认 True）。

    线程模型
    --------
    内部持有一个 ``threading.RLock``，写操作（create/update/transition/delete）
    在锁内执行；读操作（get/list_*）不加锁（WAL 允许并发读）。
    """

    def __init__(
        self,
        db_path: Optional[Path | str] = None,
        *,
        auto_init: bool = True,
        gate_dir: Optional[Path | str] = None,
        project_root: Optional[Path | str] = None,
        enable_gate: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._lock = RLock()
        if auto_init:
            init_db(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)
        self._enable_gate = enable_gate
        if enable_gate:
            self._gate_engine: Optional[GateEngine] = GateEngine(
                gate_dir=gate_dir if gate_dir is not None else GATES_DIR,
                db_path=self._db_path,
                project_root=project_root,
                auto_init=False,  # init_db 已在上方完成
            )
        else:
            self._gate_engine = None

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    def close(self) -> None:
        """关闭底层 SQLite 连接（及 GateEngine 连接）。"""
        if self._gate_engine is not None:
            self._gate_engine.close()
        self._conn.close()

    def __enter__(self) -> "TaskRepository":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    @contextmanager
    def _write_tx(self) -> Iterator[sqlite3.Connection]:
        """写事务上下文：BEGIN IMMEDIATE → yield → COMMIT / ROLLBACK。"""
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

    # ------------------------------------------------------------------
    # 内部：events 写入
    # ------------------------------------------------------------------

    def _record_event(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        payload: dict[str, object],
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """在同一事务连接中写入 events 表。"""
        conn.execute(
            """
            INSERT INTO events
                (event_id, event_type, payload, task_id, session_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                _new_id("ev-"),
                event_type,
                json.dumps(payload, ensure_ascii=False),
                task_id,
                session_id,
                now_iso(),
            ),
        )

    # ------------------------------------------------------------------
    # 内部：tasks 行读取
    # ------------------------------------------------------------------

    def _fetch_row(
        self, conn: sqlite3.Connection, task_id: str
    ) -> Optional[sqlite3.Row]:
        cursor = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        result: Optional[sqlite3.Row] = cursor.fetchone()
        return result

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(self, task: Task, *, files: Optional[list[dict[str, str]]] = None) -> TaskCard:
        """
        插入新任务。task_id 已存在时抛 sqlite3.IntegrityError。

        参数
        ----
        task : Task
            Pydantic 模型实例（必须通过校验）。
        files : list[dict] | None
            任务-文件映射列表，每项含 file_path 和 role（primary/in_scope/output）。

        返回
        ----
        TaskCard
            插入后从 DB 重新读取的 TaskCard 对象（时间戳已规范化）。
        """
        with self._write_tx() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    task_id, namespace, seq, title, status, priority, phase,
                    execution_model, model_rationale, fallback_model,
                    safety_level, directive, idempotent, classification,
                    evolution_policy, estimate_hours, actual_hours,
                    files_in_scope, deliverables, acceptance,
                    depends_on, tags, session_id, waiting_for, ready_at,
                    completed_at, created_at, updated_at,
                    source_blueprint, source_section, description,
                    upstream_files, downstream_outputs, allowed_touch,
                    forbidden_touch, applicable_rules, context_assembly_manifest,
                    rollback_instructions, estimated_tokens, timeout_minutes,
                    completed_gates, blocked_gates, assigned_pipeline,
                    pipeline_modules, blocked_by, artifact_paths,
                    audit_findings, ke_entries, ai_autonomy_level,
                    autonomy_checklist, construction_status, verification_status
                ) VALUES (
                    :task_id, :namespace, :seq, :title, :status, :priority, :phase,
                    :execution_model, :model_rationale, :fallback_model,
                    :safety_level, :directive, :idempotent, :classification,
                    :evolution_policy, :estimate_hours, :actual_hours,
                    :files_in_scope, :deliverables, :acceptance,
                    :depends_on, :tags, :session_id, :waiting_for, :ready_at,
                    :completed_at, :created_at, :updated_at,
                    :source_blueprint, :source_section, :description,
                    :upstream_files, :downstream_outputs, :allowed_touch,
                    :forbidden_touch, :applicable_rules, :context_assembly_manifest,
                    :rollback_instructions, :estimated_tokens, :timeout_minutes,
                    :completed_gates, :blocked_gates, :assigned_pipeline,
                    :pipeline_modules, :blocked_by, :artifact_paths,
                    :audit_findings, :ke_entries, :ai_autonomy_level,
                    :autonomy_checklist, :construction_status, :verification_status
                )
                """,
                {
                    "task_id": task.task_id,
                    "namespace": task.namespace.value,
                    "seq": task.seq,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "phase": task.phase,
                    "execution_model": task.execution_model,
                    "model_rationale": task.model_rationale,
                    "fallback_model": task.fallback_model,
                    "safety_level": task.safety_level.value,
                    "directive": task.directive,
                    "idempotent": int(task.idempotent),
                    "classification": task.classification.value,
                    "evolution_policy": task.evolution_policy.value,
                    "estimate_hours": task.estimate_hours,
                    "actual_hours": task.actual_hours,
                    "files_in_scope": json.dumps(task.files_in_scope, ensure_ascii=False),
                    "deliverables": json.dumps(task.deliverables, ensure_ascii=False),
                    "acceptance": json.dumps(task.acceptance, ensure_ascii=False),
                    "depends_on": json.dumps(task.depends_on, ensure_ascii=False),
                    "tags": json.dumps(task.tags, ensure_ascii=False),
                    "session_id": task.session_id,
                    "waiting_for": task.waiting_for,
                    "ready_at": task.ready_at.isoformat() if task.ready_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "source_blueprint": getattr(task, "source_blueprint", ""),
                    "source_section": getattr(task, "source_section", ""),
                    "description": getattr(task, "description", ""),
                    "upstream_files": json.dumps(getattr(task, "upstream_files", []), ensure_ascii=False),
                    "downstream_outputs": json.dumps(getattr(task, "downstream_outputs", []), ensure_ascii=False),
                    "allowed_touch": json.dumps(getattr(task, "allowed_touch", []), ensure_ascii=False),
                    "forbidden_touch": json.dumps(getattr(task, "forbidden_touch", []), ensure_ascii=False),
                    "applicable_rules": json.dumps(getattr(task, "applicable_rules", []), ensure_ascii=False),
                    "context_assembly_manifest": json.dumps(getattr(task, "context_assembly_manifest", []), ensure_ascii=False),
                    "rollback_instructions": getattr(task, "rollback_instructions", ""),
                    "estimated_tokens": getattr(task, "estimated_tokens", 0),
                    "timeout_minutes": getattr(task, "timeout_minutes", 0),
                    "completed_gates": json.dumps(getattr(task, "completed_gates", []), ensure_ascii=False, default=str),
                    "blocked_gates": json.dumps(getattr(task, "blocked_gates", {}), ensure_ascii=False),
                    "assigned_pipeline": getattr(task, "assigned_pipeline", ""),
                    "pipeline_modules": json.dumps(getattr(task, "pipeline_modules", []), ensure_ascii=False),
                    "blocked_by": json.dumps(getattr(task, "blocked_by", []), ensure_ascii=False),
                    "artifact_paths": json.dumps(getattr(task, "artifact_paths", []), ensure_ascii=False),
                    "audit_findings": json.dumps(getattr(task, "audit_findings", []), ensure_ascii=False, default=str),
                    "ke_entries": json.dumps(getattr(task, "ke_entries", []), ensure_ascii=False),
                    "ai_autonomy_level": getattr(task, "ai_autonomy_level", "supervised"),
                    "autonomy_checklist": json.dumps(getattr(task, "autonomy_checklist", []), ensure_ascii=False),
                    "construction_status": getattr(task, "construction_status", "pending"),
                    "verification_status": getattr(task, "verification_status", "unverified"),
                },
            )
            if files:
                for f in files:
                    conn.execute(
                        "INSERT OR IGNORE INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)",
                        (task.task_id, f["file_path"], f.get("role", "in_scope")),
                    )
            self._record_event(
                conn,
                "task_event",
                {"action": "created", "task_id": task.task_id, "status": task.status.value},
                task_id=task.task_id,
                session_id=task.session_id,
            )
            row = self._fetch_row(conn, task.task_id)
        assert row is not None
        return _row_to_taskcard(row)

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get(self, task_id: str) -> Optional[TaskCard]:
        """按 task_id 查询，不存在返回 None。"""
        cursor = self._conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        return _row_to_taskcard(row) if row else None

    def get_or_raise(self, task_id: str) -> TaskCard:
        """按 task_id 查询，不存在抛 TaskNotFoundError。"""
        task = self.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"任务 {task_id!r} 不存在")
        return task

    # ------------------------------------------------------------------
    # UPDATE（通用字段更新，不触发状态机）
    # ------------------------------------------------------------------

    def update(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        session_id: Optional[str] = None,
        waiting_for: Optional[str] = None,
        estimate_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        deliverables: Optional[list[str]] = None,
        acceptance: Optional[list[str]] = None,
        files_in_scope: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        model_rationale: Optional[str] = None,
    ) -> TaskCard:
        """
        更新非状态字段。不触发状态机校验，也不写 state_transition 事件。
        状态转换请使用 ``transition()`` 方法。

        返回
        ----
        Task
            更新后重新读取的 Task 对象。
        """
        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

            updates: list[tuple[str, object]] = []
            if title is not None:
                updates.append(("title", title))
            if session_id is not None:
                updates.append(("session_id", session_id))
            if waiting_for is not None:
                updates.append(("waiting_for", waiting_for))
            if estimate_hours is not None:
                updates.append(("estimate_hours", estimate_hours))
            if actual_hours is not None:
                updates.append(("actual_hours", actual_hours))
            if deliverables is not None:
                updates.append(("deliverables", json.dumps(deliverables, ensure_ascii=False)))
            if acceptance is not None:
                updates.append(("acceptance", json.dumps(acceptance, ensure_ascii=False)))
            if files_in_scope is not None:
                updates.append(("files_in_scope", json.dumps(files_in_scope, ensure_ascii=False)))
            if tags is not None:
                updates.append(("tags", json.dumps(tags, ensure_ascii=False)))
            if model_rationale is not None:
                updates.append(("model_rationale", model_rationale))

            if not updates:
                return _row_to_taskcard(row)

            updates.append(("updated_at", now_iso()))
            set_clause = ", ".join(f"{col} = ?" for col, _ in updates)
            values = [v for _, v in updates]
            conn.execute(
                f"UPDATE tasks SET {set_clause} WHERE task_id = ?",  # noqa: S608
                (*values, task_id),
            )
            updated_row = self._fetch_row(conn, task_id)
        assert updated_row is not None
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # TRANSITION（状态机）
    # ------------------------------------------------------------------

    def transition(
        self,
        task_id: str,
        to_status: TaskStatus | str,
        *,
        session_id: Optional[str] = None,
        waiting_for: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Task:
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

        # G1 门禁检查在事务外执行，避免两个连接同时争抢 BEGIN IMMEDIATE
        # （GateEngine 持有独立 SQLite 连接，需先完成写入再开启 task_repo 事务）
        gate_result: Optional[GateResult] = None
        if (
            to_status == TaskStatus.IN_PROGRESS
            and self._enable_gate
            and self._gate_engine is not None
        ):
            # 先读任务对象（读操作不加锁）
            pre_conn = get_db_connection(self._db_path)
            pre_conn.row_factory = sqlite3.Row
            pre_row = pre_conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            pre_conn.close()
            if pre_row is not None:
                task_obj = _row_to_taskcard(pre_row)
                gate_result = self._gate_engine.evaluate(task_obj, _STARTUP_GATE_ID)
                if not gate_result.passed:
                    raise GateViolationError(gate_result)

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

            from_status = TaskStatus(row["status"])
            if not _is_valid_transition(from_status, to_status):
                raise InvalidTransitionError(
                    f"非法转换 {from_status.value} → {to_status.value}（task_id={task_id!r}）"
                )

            now = now_iso()
            set_ready_at = to_status == TaskStatus.READY
            set_completed_at = to_status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)
            conn.execute(
                """
                UPDATE tasks
                SET status = ?, session_id = COALESCE(?, session_id),
                    waiting_for = ?,
                    ready_at = CASE WHEN ? THEN ? ELSE ready_at END,
                    completed_at = CASE WHEN ? THEN COALESCE(completed_at, ?) ELSE completed_at END,
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
                    now,
                    task_id,
                ),
            )
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
            updated_row = self._fetch_row(conn, task_id)

        assert updated_row is not None
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, task_id: str) -> bool:
        """
        删除任务记录（级联 SET NULL events.task_id，级联删除 task_files）。

        返回
        ----
        bool
            True 表示成功删除；False 表示 task_id 不存在。
        """
        with self._write_tx() as conn:
            conn.execute("DELETE FROM task_files WHERE task_id = ?", (task_id,))
            cursor = conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            deleted = cursor.rowcount > 0
        return deleted

    # ------------------------------------------------------------------
    # LIST 查询
    # ------------------------------------------------------------------

    def list_by_status(self, status: TaskStatus | str) -> list[TaskCard]:
        """查询指定状态的所有任务（按 phase ASC, updated_at DESC 排序）。"""
        if isinstance(status, str):
            status = TaskStatus(status)
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY phase ASC, updated_at DESC",
            (status.value,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_phase(self, phase: int) -> list[TaskCard]:
        """查询指定 Phase 的所有任务（按 status ASC, task_id ASC 排序）。"""
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE phase = ? ORDER BY status ASC, task_id ASC",
            (phase,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_session(self, session_id: str) -> list[TaskCard]:
        """查询指定 session_id 的所有任务。"""
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE session_id = ? ORDER BY updated_at DESC",
            (session_id,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_namespace(self, namespace: TaskNamespace | str) -> list[Task]:
        """查询指定命名空间的所有任务（按 seq ASC 排序）。"""
        if isinstance(namespace, TaskNamespace):
            namespace = namespace.value
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE namespace = ? ORDER BY seq ASC",
            (namespace,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    # ------------------------------------------------------------------
    # task_files 读写（#21 裁定：N:N 映射）
    # ------------------------------------------------------------------

    def add_file(
        self, task_id: str, file_path: str, role: str = "in_scope"
    ) -> None:
        """为任务添加文件映射。role 可选 primary/in_scope/output。"""
        with self._write_tx() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)",
                (task_id, file_path, role),
            )

    def remove_file(self, task_id: str, file_path: str) -> None:
        """移除任务的文件映射。"""
        with self._write_tx() as conn:
            conn.execute(
                "DELETE FROM task_files WHERE task_id = ? AND file_path = ?",
                (task_id, file_path),
            )

    def get_files(self, task_id: str) -> list[dict[str, str]]:
        """获取任务的所有文件映射，返回 [{file_path, role}, ...]。"""
        cursor = self._conn.execute(
            "SELECT file_path, role FROM task_files WHERE task_id = ? ORDER BY role, file_path",
            (task_id,),
        )
        return [{"file_path": r["file_path"], "role": r["role"]} for r in cursor.fetchall()]

    def get_tasks_for_file(self, file_path: str) -> list[str]:
        """获取涉及指定文件的所有任务 ID。"""
        cursor = self._conn.execute(
            "SELECT task_id FROM task_files WHERE file_path = ? ORDER BY task_id",
            (file_path,),
        )
        return [r["task_id"] for r in cursor.fetchall()]

    def next_seq(self, namespace: TaskNamespace | str | None = None) -> int:
        """获取下一个序号。指定 namespace 时返回该命名空间内自增；否则返回全局最大值+1。"""
        if namespace is not None:
            if isinstance(namespace, TaskNamespace):
                namespace = namespace.value
            cursor = self._conn.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM tasks WHERE namespace = ?",
                (namespace,),
            )
        else:
            cursor = self._conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM tasks")
        return cursor.fetchone()["next_seq"]

    def list_active(self) -> list[Task]:
        """查询活跃任务（IN_PROGRESS / READY / RETRY / WAITING）。"""
        cursor = self._conn.execute(
            """
            SELECT * FROM tasks
            WHERE status IN ('IN_PROGRESS','READY','RETRY','WAITING')
            ORDER BY phase ASC, updated_at DESC
            """
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def count_by_status(self) -> dict[str, int]:
        """按状态统计任务数量。"""
        cursor = self._conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM tasks GROUP BY status"
        )
        return {row["status"]: row["cnt"] for row in cursor.fetchall()}

    # ------------------------------------------------------------------
    # UPSERT（Phase 0 批量补录）
    # ------------------------------------------------------------------

    def upsert(self, task: Task, *, files: Optional[list[dict[str, str]]] = None) -> Task:
        """
        INSERT OR REPLACE 语义：task_id 已存在则全量覆盖，否则新建。

        用于 Phase 0 任务补录（T-1-06）。
        """
        with self._write_tx() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    task_id, namespace, seq, title, status, priority, phase,
                    execution_model, model_rationale, fallback_model,
                    safety_level, directive, idempotent, classification,
                    evolution_policy, estimate_hours, actual_hours,
                    files_in_scope, deliverables, acceptance,
                    depends_on, tags, session_id, waiting_for, ready_at,
                    completed_at, created_at, updated_at,
                    source_blueprint, source_section, description,
                    upstream_files, downstream_outputs, allowed_touch,
                    forbidden_touch, applicable_rules, context_assembly_manifest,
                    rollback_instructions, estimated_tokens, timeout_minutes,
                    completed_gates, blocked_gates, assigned_pipeline,
                    pipeline_modules, blocked_by, artifact_paths,
                    audit_findings, ke_entries, ai_autonomy_level,
                    autonomy_checklist, construction_status, verification_status
                ) VALUES (
                    :task_id, :namespace, :seq, :title, :status, :priority, :phase,
                    :execution_model, :model_rationale, :fallback_model,
                    :safety_level, :directive, :idempotent, :classification,
                    :evolution_policy, :estimate_hours, :actual_hours,
                    :files_in_scope, :deliverables, :acceptance,
                    :depends_on, :tags, :session_id, :waiting_for, :ready_at,
                    :completed_at, :created_at, :updated_at,
                    :source_blueprint, :source_section, :description,
                    :upstream_files, :downstream_outputs, :allowed_touch,
                    :forbidden_touch, :applicable_rules, :context_assembly_manifest,
                    :rollback_instructions, :estimated_tokens, :timeout_minutes,
                    :completed_gates, :blocked_gates, :assigned_pipeline,
                    :pipeline_modules, :blocked_by, :artifact_paths,
                    :audit_findings, :ke_entries, :ai_autonomy_level,
                    :autonomy_checklist, :construction_status, :verification_status
                )
                """,
                {
                    "task_id": task.task_id,
                    "namespace": task.namespace.value,
                    "seq": task.seq,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "phase": task.phase,
                    "execution_model": task.execution_model,
                    "model_rationale": task.model_rationale,
                    "fallback_model": task.fallback_model,
                    "safety_level": task.safety_level.value,
                    "directive": task.directive,
                    "idempotent": int(task.idempotent),
                    "classification": task.classification.value,
                    "evolution_policy": task.evolution_policy.value,
                    "estimate_hours": task.estimate_hours,
                    "actual_hours": task.actual_hours,
                    "files_in_scope": json.dumps(task.files_in_scope, ensure_ascii=False),
                    "deliverables": json.dumps(task.deliverables, ensure_ascii=False),
                    "acceptance": json.dumps(task.acceptance, ensure_ascii=False),
                    "depends_on": json.dumps(task.depends_on, ensure_ascii=False),
                    "tags": json.dumps(task.tags, ensure_ascii=False),
                    "session_id": task.session_id,
                    "waiting_for": task.waiting_for,
                    "ready_at": task.ready_at.isoformat() if task.ready_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "source_blueprint": getattr(task, "source_blueprint", ""),
                    "source_section": getattr(task, "source_section", ""),
                    "description": getattr(task, "description", ""),
                    "upstream_files": json.dumps(getattr(task, "upstream_files", []), ensure_ascii=False),
                    "downstream_outputs": json.dumps(getattr(task, "downstream_outputs", []), ensure_ascii=False),
                    "allowed_touch": json.dumps(getattr(task, "allowed_touch", []), ensure_ascii=False),
                    "forbidden_touch": json.dumps(getattr(task, "forbidden_touch", []), ensure_ascii=False),
                    "applicable_rules": json.dumps(getattr(task, "applicable_rules", []), ensure_ascii=False),
                    "context_assembly_manifest": json.dumps(getattr(task, "context_assembly_manifest", []), ensure_ascii=False),
                    "rollback_instructions": getattr(task, "rollback_instructions", ""),
                    "estimated_tokens": getattr(task, "estimated_tokens", 0),
                    "timeout_minutes": getattr(task, "timeout_minutes", 0),
                    "completed_gates": json.dumps(getattr(task, "completed_gates", []), ensure_ascii=False, default=str),
                    "blocked_gates": json.dumps(getattr(task, "blocked_gates", {}), ensure_ascii=False),
                    "assigned_pipeline": getattr(task, "assigned_pipeline", ""),
                    "pipeline_modules": json.dumps(getattr(task, "pipeline_modules", []), ensure_ascii=False),
                    "blocked_by": json.dumps(getattr(task, "blocked_by", []), ensure_ascii=False),
                    "artifact_paths": json.dumps(getattr(task, "artifact_paths", []), ensure_ascii=False),
                    "audit_findings": json.dumps(getattr(task, "audit_findings", []), ensure_ascii=False, default=str),
                    "ke_entries": json.dumps(getattr(task, "ke_entries", []), ensure_ascii=False),
                    "ai_autonomy_level": getattr(task, "ai_autonomy_level", "supervised"),
                    "autonomy_checklist": json.dumps(getattr(task, "autonomy_checklist", []), ensure_ascii=False),
                    "construction_status": getattr(task, "construction_status", "pending"),
                    "verification_status": getattr(task, "verification_status", "unverified"),
                },
            )
            if files:
                conn.execute("DELETE FROM task_files WHERE task_id = ?", (task.task_id,))
                for f in files:
                    conn.execute(
                        "INSERT OR IGNORE INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)",
                        (task.task_id, f["file_path"], f.get("role", "in_scope")),
                    )
            row = self._fetch_row(conn, task.task_id)
        assert row is not None
        return _row_to_taskcard(row)


# ---------------------------------------------------------------------------
# 状态机查询助手（不依赖实例）
# ---------------------------------------------------------------------------


def allowed_transitions(status: TaskStatus | str) -> frozenset[TaskStatus]:
    """返回给定状态的合法目标状态集合。"""
    if isinstance(status, str):
        status = TaskStatus(status)
    return _ALLOWED_TRANSITIONS.get(status, frozenset())


def is_terminal(status: TaskStatus | str) -> bool:
    """判断是否为终态（VERIFIED / CANCELLED）。"""
    if isinstance(status, str):
        status = TaskStatus(status)
    return not _ALLOWED_TRANSITIONS.get(status, frozenset())
