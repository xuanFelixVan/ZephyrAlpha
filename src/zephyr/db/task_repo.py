# [BLUEPRINT] MOD-INF-012 | 03_modules/_cross_layer/database/blueprint.md | §

# [MODULE] zephyr.db.task_repo

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
TaskRepository — 任务登记表 CRUD + 状态机（T-1-04）
====================================================
依据：ADR-0030（SQLite 元数据层）+ ADR-0040（Pydantic v2 契约）

根因约束（防再犯 PAUSED 类错误）
-------------------------------
``TaskStatus`` **仅允许**本文件 ``_ALLOWED_TRANSITIONS`` keys 与 SQLite
``tasks.status`` CHECK 中出现的取值。其它模块（如 pipeline 抢占）**禁止**
使用未在 ``TaskStatus`` 中声明的状态字面量；语义扩展须先改枚举 + DDL 迁移 + 本表。

Safety : H（基础设施核心，状态机错误会影响整个任务流水线）

功能
----
- create / get / update / delete CRUD
- 状态机转换（10 状态）+ 非法转换拒绝
- 每次状态转换自动写 events 表（state_transition 事件）
- 按 phase / status / session_id 列表查询
- 批量 upsert（scaffold 补录用）

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

import logging
logger = logging.getLogger(__name__)

import fnmatch
import json
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from zephyr.core.models import TaskCard
from zephyr.db.sqlite_schema import DB_PATH, get_db_connection, init_db
from zephyr.gates.gate_engine import (
    GATES_DIR,
    GateEngine,
)
from zephyr.gates.task_types import Task, TaskNamespace, TaskStatus
from zephyr.shared.contracts.gate import GateResult, GateViolationError
from zephyr.shared.schema.severity_types import Priority
from zephyr.shared.utils.time_utils import now_iso

__all__ = [
    "TaskRepository",
    "TaskNotFoundError",
    "InvalidTransitionError",
    "TaskRepositoryError",
    "RejectedUpgradeCoolingOffError",
    "P0InflationFrozenError",
    "P0InflationWarning",
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


class RejectedUpgradeCoolingOffError(TaskRepositoryError):
    """优先级升级被拒绝且仍在 48h 冷却期内。"""


class P0InflationFrozenError(TaskRepositoryError):
    """GOV-TASK-004 §2.5: P0 任务已达上限（5个），冻结新增 P0。"""


class P0InflationWarning(TaskRepositoryError):
    """GOV-TASK-004 §2.5: P0 任务 ≥3 个，新增 P0 需附带论证。"""


# ---------------------------------------------------------------------------
# 状态机转换表
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.PENDING: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.IN_PROGRESS: frozenset(
        {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.BLOCKED,
            TaskStatus.WAITING,
        }
    ),
    TaskStatus.COMPLETED: frozenset(
        {
            TaskStatus.VERIFIED,
            TaskStatus.IN_PROGRESS,
        }
    ),
    TaskStatus.VERIFIED: frozenset(),  # 终态
    TaskStatus.FAILED: frozenset(
        {
            TaskStatus.RETRY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.BLOCKED: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.WAITING: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.READY: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.RETRY: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.FAILED,
        }
    ),
    TaskStatus.CANCELLED: frozenset(),  # 终态
}


def _is_valid_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    return to_status in _ALLOWED_TRANSITIONS.get(from_status, frozenset())


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

_UTC = UTC


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。"""
    return datetime.now(_UTC).isoformat()


def _new_id(prefix: str = "") -> str:
    """生成带可选前缀的 UUID4 字符串。"""
    uid = str(uuid.uuid4())
    return f"{prefix}{uid}" if prefix else uid


def _row_to_taskcard(row: sqlite3.Row) -> TaskCard:
    """将 sqlite3.Row 转换为 TaskCard Pydantic 模型（含全部 62 字段）。"""
    d = dict(row)
    for _internal_col in ("batch_id", "claimed_by", "claimed_at"):
        d.pop(_internal_col, None)
    _json_array_fields = (
        "files_in_scope",
        "deliverables",
        "acceptance",
        "depends_on",
        "tags",
        "upstream_files",
        "downstream_outputs",
        "allowed_touch",
        "forbidden_touch",
        "applicable_rules",
        "context_assembly_manifest",
        "completed_gates",
        "pipeline_modules",
        "blocked_by",
        "artifact_paths",
        "audit_findings",
        "ke_entries",
        "autonomy_checklist",
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
    if d.get("estimated_tokens", 8000) < 500:
        d["estimated_tokens"] = 8000
    if d.get("timeout_minutes", 30) < 5:
        d["timeout_minutes"] = 30

    schema_ver = d.get("schema_version", "")
    if schema_ver and schema_ver != "0.3.2":
        import warnings

        warnings.warn(
            f"TaskCard {d.get('task_id','?')} schema_version={schema_ver} 与当前 0.3.2 不匹配，"
            f"可能缺少新增字段（autonomy_checklist 等），数据完整性未经验证。",
            UserWarning,
            stacklevel=2,
        )

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
        db_path: Path | str | None = None,
        *,
        auto_init: bool = True,
        gate_dir: Path | str | None = None,
        project_root: Path | str | None = None,
        enable_gate: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._lock = RLock()
        if auto_init:
            init_db(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)
        self._enable_gate = enable_gate
        if enable_gate:
            self._gate_engine: GateEngine | None = GateEngine(
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

    def __enter__(self) -> TaskRepository:
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
        task_id: str | None = None,
        session_id: str | None = None,
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

    def _fetch_row(self, conn: sqlite3.Connection, task_id: str) -> sqlite3.Row | None:
        cursor = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        result: sqlite3.Row | None = cursor.fetchone()
        return result

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(self, task: Task, *, files: list[dict[str, str]] | None = None, allow_direct_create: bool = False) -> TaskCard:
        """
        插入新任务。task_id 已存在时抛 sqlite3.IntegrityError。

        参数
        ----
        task : Task
            Pydantic 模型实例（必须通过校验）。
        files : list[dict] | None
            任务-文件映射列表，每项含 file_path 和 role（primary/in_scope/output）。
        allow_direct_create : bool
            逃生门：仅 Owner 审批场景允许绕过 RULE-ZERO-TASK。默认 False。

        返回
        ----
        TaskCard
            插入后从 DB 重新读取的 TaskCard 对象（时间戳已规范化）。
        """
        source_bp = getattr(task, "source_blueprint", "") or ""
        if not allow_direct_create and (not source_bp.strip() or source_bp.strip().lower() == "unknown"):
            raise ValueError(
                f"RULE-ZERO-TASK 违规: 任务 {task.task_id!r} 的 source_blueprint 为空或 'unknown'。"
                f"建卡唯一合法路径 = BlueprintDecomposer.decompose(blueprint_path)（MOD-INF-006）。"
                f"直接 TaskRepository.create() 建卡违反 RULE-ZERO-TASK。"
                f"如需 Owner 审批绕过，请传 allow_direct_create=True。"
            )
        with self._write_tx() as conn:
            if task.priority == Priority.P0:
                p0_count = self._count_p0_tasks(conn)
                if p0_count >= 5:
                    raise P0InflationFrozenError(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（已达上限 5），"
                        f"冻结新增 P0。请将优先级降为 P1 或等待 Owner 手动解除冻结"
                    )
                if p0_count >= 3:
                    import warnings

                    warnings.warn(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（≥3 黄色警戒），"
                        f"新增 P0 任务 {task.task_id!r} 必须附带'为什么必须 P0 而非 P1 / 能不能拆成 P1+P2'的论证段落",
                        UserWarning,
                        stacklevel=2,
                    )
            if self._enable_gate and self._gate_engine is not None:
                gate_result = self._gate_engine.evaluate(task, "G0", conn=conn)
                if not gate_result.passed:
                    raise GateViolationError(gate_result)
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
                    autonomy_checklist, construction_status, verification_status,
                    schema_version, approval_required, priority_proposed,
                    rejection_cooldown_until
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
                    :autonomy_checklist, :construction_status, :verification_status,
                    :schema_version, :approval_required, :priority_proposed,
                    :rejection_cooldown_until
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
                    "context_assembly_manifest": json.dumps(
                        getattr(task, "context_assembly_manifest", []), ensure_ascii=False
                    ),
                    "rollback_instructions": getattr(task, "rollback_instructions", ""),
                    "estimated_tokens": getattr(task, "estimated_tokens", 8000),
                    "timeout_minutes": getattr(task, "timeout_minutes", 30),
                    "completed_gates": json.dumps(
                        getattr(task, "completed_gates", []), ensure_ascii=False, default=str
                    ),
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
                    "schema_version": "0.3.2",
                    "approval_required": int(getattr(task, "approval_required", False)),
                    "priority_proposed": getattr(task, "priority_proposed", None),
                    "rejection_cooldown_until": getattr(task, "rejection_cooldown_until", None),
                    "block_sessions_count": getattr(task, "block_sessions_count", 0),
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

    def get(self, task_id: str) -> TaskCard | None:
        """按 task_id 查询有效任务（默认排除软删除行），不存在返回 None。"""
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0",
            (task_id,),
        )
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
        title: str | None = None,
        session_id: str | None = None,
        waiting_for: str | None = None,
        estimate_hours: float | None = None,
        actual_hours: float | None = None,
        deliverables: list[str] | None = None,
        acceptance: list[str] | None = None,
        files_in_scope: list[str] | None = None,
        tags: list[str] | None = None,
        model_rationale: str | None = None,
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
                f"UPDATE tasks SET {set_clause} WHERE task_id = ?",
                (*values, task_id),
            )
            updated_row = self._fetch_row(conn, task_id)

        assert updated_row is not None
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # PRIORITY GOVERNANCE（GOV-TASK-004 §2.4+§2.5）
    # ------------------------------------------------------------------

    def _count_p0_tasks(self, conn: sqlite3.Connection) -> int:
        """统计当前活跃 P0 任务数（排除终态 CANCELLED/VERIFIED 和软删除）。"""
        row = conn.execute(
            "SELECT COUNT(*) FROM tasks "
            "WHERE priority = 'P0' AND status NOT IN ('CANCELLED','VERIFIED') AND is_deleted = 0"
        ).fetchone()
        return row[0] if row else 0

    def propose_priority_upgrade(
        self,
        task_id: str,
        proposed_priority: str,
    ) -> TaskCard:
        """AI 提议优先级升级（P4→P3→P2→P1→P0）。

        规则（GOV-TASK-004 §2.4）：
        - 设置为 approval_required=True + priority_proposed=目标值
        - 不直接修改 priority 字段
        - 若已有拒绝且在 48h 冷却期内，抛出 RejectedUpgradeCoolingOffError
        - 降级（如 P1→P2）直接生效，不走审批
        """
        from zephyr.shared.schema.severity_types import Priority as P

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

            current_p = row["priority"]
            proposed_p = getattr(P, proposed_priority, proposed_priority)
            if isinstance(proposed_p, P):
                proposed_p = proposed_p.value

            if current_p == proposed_p:
                return _row_to_taskcard(row)

            current_idx = {Priority.P0.value: 0, Priority.P1.value: 1, Priority.P2.value: 2, Priority.P3.value: 3, Priority.P4.value: 4}.get(current_p, 9)
            proposed_idx = {Priority.P0.value: 0, Priority.P1.value: 1, Priority.P2.value: 2, Priority.P3.value: 3, Priority.P4.value: 4}.get(proposed_p, 9)

            if proposed_idx >= current_idx:
                conn.execute(
                    "UPDATE tasks SET priority = ?, updated_at = ? WHERE task_id = ?",
                    (proposed_p, now_iso(), task_id),
                )
                updated_row = self._fetch_row(conn, task_id)
                return _row_to_taskcard(updated_row)

            current_approval = row["approval_required"]
            if current_approval:
                if row["priority_proposed"] and row["priority_proposed"] != proposed_p:
                    conn.execute(
                        "UPDATE tasks SET priority_proposed = ?, updated_at = ? WHERE task_id = ?",
                        (proposed_p, now_iso(), task_id),
                    )
                    updated_row = self._fetch_row(conn, task_id)
                    return _row_to_taskcard(updated_row)
                return _row_to_taskcard(row)

            cooldown_until = row["rejection_cooldown_until"]
            if cooldown_until:
                from datetime import datetime as dt

                try:
                    cooldown_dt = dt.fromisoformat(cooldown_until)
                    if cooldown_dt > dt.now(UTC):
                        raise RejectedUpgradeCoolingOffError(
                            f"优先级升级被拒绝且仍在冷却期（至 {cooldown_until}），" f"请等待冷却期结束后重新提议"
                        )
                except (ValueError, TypeError):
                    pass

            if proposed_p == "P0":
                p0_count = self._count_p0_tasks(conn)
                if p0_count >= 5:
                    raise P0InflationFrozenError(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（已达上限 5），"
                        f"冻结升级为 P0。请保持当前优先级或等待 Owner 手动解除冻结"
                    )
                if p0_count >= 3:
                    import warnings

                    warnings.warn(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（≥3 黄色警戒），"
                        f"任务 {task_id!r} 升级为 P0 必须附带'为什么必须 P0 而非 P1 / 能不能拆成 P1+P2'的论证段落",
                        UserWarning,
                        stacklevel=2,
                    )

            conn.execute(
                "UPDATE tasks SET approval_required = 1, priority_proposed = ?, updated_at = ? WHERE task_id = ?",
                (proposed_p, now_iso(), task_id),
            )

            conn.execute(
                """INSERT INTO events (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'task_event', ?, ?, ?)""",
                (
                    f"ev-{task_id}-priority-{proposed_p}",
                    json.dumps(
                        {
                            "event_subtype": "priority_upgrade_proposed",
                            "current": current_p,
                            "proposed": proposed_p,
                            "action": "awaiting_owner_approval",
                        },
                        ensure_ascii=False,
                    ),
                    task_id,
                    now_iso(),
                ),
            )

            updated_row = self._fetch_row(conn, task_id)
        assert updated_row is not None
        return _row_to_taskcard(updated_row)

    def approve_priority_upgrade(self, task_id: str) -> TaskCard:
        """Owner 批准优先级升级。将 priority_proposed → priority，清除 approval 标记。"""
        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

            if not row["approval_required"]:
                return _row_to_taskcard(row)

            approved_p = row["priority_proposed"] or row["priority"]
            conn.execute(
                "UPDATE tasks SET priority = ?, approval_required = 0, priority_proposed = NULL, rejection_cooldown_until = NULL, updated_at = ? WHERE task_id = ?",
                (approved_p, now_iso(), task_id),
            )

            conn.execute(
                """INSERT INTO events (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'task_event', ?, ?, ?)""",
                (
                    f"ev-{task_id}-approved-{approved_p}",
                    json.dumps({"event_subtype": "priority_upgrade_approved", "approved": approved_p, "action": "owner_approved"}, ensure_ascii=False),
                    task_id,
                    now_iso(),
                ),
            )

            updated_row = self._fetch_row(conn, task_id)
        assert updated_row is not None
        return _row_to_taskcard(updated_row)

    def reject_priority_upgrade(self, task_id: str) -> TaskCard:
        """Owner 拒绝优先级升级。设置 48h 冷却期。"""
        from datetime import datetime as dt
        from datetime import timedelta as td

        cooldown = (dt.now(UTC) + td(hours=48)).isoformat()

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

            conn.execute(
                "UPDATE tasks SET approval_required = 0, priority_proposed = NULL, rejection_cooldown_until = ?, updated_at = ? WHERE task_id = ?",
                (cooldown, now_iso(), task_id),
            )

            conn.execute(
                """INSERT INTO events (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'task_event', ?, ?, ?)""",
                (
                    f"ev-{task_id}-rejected",
                    json.dumps({"event_subtype": "priority_upgrade_rejected", "cooldown_until": cooldown, "action": "owner_rejected"}, ensure_ascii=False),
                    task_id,
                    now_iso(),
                ),
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
        session_id: str | None = None,
        waiting_for: str | None = None,
        note: str | None = None,
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

        try:
            with self._write_tx() as conn:
                row = self._fetch_row(conn, task_id)
                if row is None:
                    raise TaskNotFoundError(f"任务 {task_id!r} 不存在")

                # G1 门禁检查在写事务内执行，与状态转换原子落盘
                # GateEngine 接受外部 conn，不再管理独立事务
                gate_result: GateResult | None = None
                if to_status == TaskStatus.IN_PROGRESS and self._enable_gate and self._gate_engine is not None:
                    task_obj = _row_to_taskcard(row)
                    gate_result = self._gate_engine.evaluate(task_obj, _STARTUP_GATE_ID, conn=conn)
                    if not gate_result.passed:
                        raise GateViolationError(gate_result)

                if to_status == TaskStatus.COMPLETED and self._enable_gate and self._gate_engine is not None:
                    task_obj = _row_to_taskcard(row)
                    gate_result = self._gate_engine.evaluate(task_obj, "G7", conn=conn)
                    if not gate_result.passed:
                        raise GateViolationError(gate_result)

                from_status = TaskStatus(row["status"])
                if not _is_valid_transition(from_status, to_status):
                    raise InvalidTransitionError(
                        f"非法转换 {from_status.value} → {to_status.value}（task_id={task_id!r}）"
                    )

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

        assert updated_row is not None

        from zephyr.hooks.event_hook import hook_registry, TransitionEvent
        hook_registry.fire(TransitionEvent(
            task_id=task_id,
            from_status=from_status.value,
            to_status=to_status.value,
            note=note or "",
            session_id=session_id,
        ))

        return _row_to_taskcard(updated_row)

    def _recalculate_dependent_status(
        self,
        conn: sqlite3.Connection,
        changed_task_id: str,
        new_status: TaskStatus,
    ) -> None:
        """当子任务状态变更时，重算依赖它的父任务状态。

        规则（蓝图 MOD-INF-006 盲点#1）：
        - 所有子任务 COMPLETED/VERIFIED → 父任务 READY（解锁继续施工）
        - 任一子任务 FAILED/CANCELLED → 父任务 BLOCKED
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

    # ------------------------------------------------------------------
    # ESCALATION GOVERNANCE（GOV-TASK-004 §2.7）
    # ------------------------------------------------------------------

    def check_escalation(self, task_id: str) -> dict | None:
        """检查任务是否需要升级到 Owner。

        触发条件（GOV-TASK-004 §2.7）：
        - P0 任务 BLOCKED 超过 2 次 → escalation:owner
        - 任何任务 BLOCKED 超过 5 次 → escalation:owner
        - P0 任务 FAILED 2 次 → escalation:owner

        返回 None 表示无需升级；返回 dict 表示需要升级，含 reason 和 triggers 字段。
        """
        task = self.get(task_id)
        if task is None:
            return None

        triggers = []
        is_p0 = task.priority == Priority.P0

        if is_p0 and task.block_sessions_count >= 2:
            triggers.append(f"P0 任务已 BLOCKED {task.block_sessions_count} 次（≥2）")
        elif task.block_sessions_count >= 5:
            triggers.append(f"任务已 BLOCKED {task.block_sessions_count} 次（≥5）")

        if is_p0:
            failed_count = self._count_failed_events(task_id)
            if failed_count >= 2:
                triggers.append(f"P0 任务已 FAILED {failed_count} 次（≥2）")

        if not triggers:
            return None

        return {
            "task_id": task_id,
            "priority": task.priority.value,
            "status": task.status.value,
            "block_sessions_count": task.block_sessions_count,
            "triggers": triggers,
            "escalation_level": "escalation:owner",
            "governance_ref": "GOV-TASK-004 §2.7",
        }

    def check_all_escalations(self) -> list[dict]:
        """检查所有活跃任务是否需要升级。"""
        escalations = []
        for task in self.list_active():
            result = self.check_escalation(task.task_id)
            if result is not None:
                escalations.append(result)
        return escalations

    def _count_failed_events(self, task_id: str) -> int:
        """统计任务在 events 表中 FAILED 的次数。"""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM events "
            "WHERE task_id = ? AND event_type = 'state_transition' "
            "AND json_extract(payload, '$.to') = 'FAILED'",
            (task_id,),
        ).fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------
    # TIMEOUT GOVERNANCE（GOV-TASK-004 §2.6）
    # ------------------------------------------------------------------

    def _is_timeout_exempt(self, task_id: str) -> bool:
        """检查任务是否携带 exempt:timeout 豁免标签（GOV-TASK-004 §2.6）。"""
        task = self.get(task_id)
        if task is None:
            return False
        tags = getattr(task, "tags", [])
        return "exempt:timeout" in tags

    def check_task_timeout(self, task_id: str) -> dict | None:
        """检查任务是否超时，返回超时信息或 None。

        GOV-TASK-004 §2.6 豁免规则：
        - 标签含 exempt:timeout → 跳过超时检查
        - 依赖外部第三方的任务（blocked_reason 注明"外部依赖"）→ 跳过超时检查
        """
        task = self.get(task_id)
        if task is None:
            return None

        if self._is_timeout_exempt(task_id):
            return None

        waiting_for = getattr(task, "waiting_for", "") or ""
        if "外部依赖" in waiting_for:
            return None

        timeout_minutes = getattr(task, "timeout_minutes", 30)
        created_str = getattr(task, "created_at", None)
        if not created_str:
            return None
        try:
            from datetime import datetime as dt

            created = dt.fromisoformat(str(created_str))
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            elapsed = (dt.now(UTC) - created).total_seconds() / 60
        except (ValueError, TypeError):
            return None

        if elapsed > timeout_minutes:
            return {
                "task_id": task_id,
                "status": task.status.value,
                "priority": task.priority.value,
                "timeout_minutes": timeout_minutes,
                "elapsed_minutes": round(elapsed, 1),
                "exempt": False,
                "governance_ref": "GOV-TASK-004 §2.6",
            }
        return None

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, task_id: str) -> bool:
        """
        软删除任务记录。设置 is_deleted=1 + deleted_at 时间戳。

        返回
        ----
        bool
            True 表示成功标记删除；False 表示 task_id 不存在或已被删除。
        """
        with self._write_tx() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET is_deleted = 1, deleted_at = ?, updated_at = ? "
                "WHERE task_id = ? AND is_deleted = 0",
                (now_iso(), now_iso(), task_id),
            )
            deleted = cursor.rowcount > 0
            if deleted:
                conn.execute("DELETE FROM task_files WHERE task_id = ?", (task_id,))
        return deleted

    def hard_delete(self, task_id: str) -> bool:
        """
        物理删除任务记录（级联 SET NULL events.task_id，级联删除 task_files）。

        仅在数据清理脚本中使用，日常开发用 soft delete。
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
            "SELECT * FROM tasks WHERE status = ? AND is_deleted = 0 ORDER BY phase ASC, updated_at DESC",
            (status.value,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_phase(self, phase: int) -> list[TaskCard]:
        """查询指定 Phase 的所有任务（按 status ASC, task_id ASC 排序）。"""
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE phase = ? AND is_deleted = 0 ORDER BY status ASC, task_id ASC",
            (phase,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_session(self, session_id: str) -> list[TaskCard]:
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
    ) -> list[TaskCard]:
        """复合条件列表（``task_manager.list_tasks`` / tool_contracts.yaml）。"""
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
        matched: list[TaskCard] = []
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

    def list_by_namespace(self, namespace: TaskNamespace | str) -> list[Task]:
        """查询指定命名空间的所有任务（按 seq ASC 排序）。"""
        if isinstance(namespace, TaskNamespace):
            namespace = namespace.value
        cursor = self._conn.execute(
            "SELECT * FROM tasks WHERE namespace = ? AND is_deleted = 0 ORDER BY seq ASC",
            (namespace,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    # ------------------------------------------------------------------
    # task_files 读写（#21 裁定：N:N 映射）
    # ------------------------------------------------------------------

    def add_file(self, task_id: str, file_path: str, role: str = "in_scope") -> None:
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
    # JSON1 查询（MOD-INF-012 v2.0）
    # ------------------------------------------------------------------

    def list_by_dependency(self, dependency_task_id: str) -> list[TaskCard]:
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

    def list_by_tag(self, tag: str) -> list[TaskCard]:
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

    def list_by_blocked_by(self, blocker_task_id: str) -> list[TaskCard]:
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

    # ------------------------------------------------------------------
    # UPSERT（scaffold 批量补录）
    # ------------------------------------------------------------------

    def upsert(self, task: Task, *, files: list[dict[str, str]] | None = None) -> Task:
        """
        ON CONFLICT DO UPDATE 语义：task_id 已存在则更新（保留 created_at），否则新建。

        用于 scaffold 任务补录（T-1-06）。
        """
        now = now_iso()
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
                    completed_at, created_at, updated_at, is_deleted,
                    source_blueprint, source_section, description,
                    upstream_files, downstream_outputs, allowed_touch,
                    forbidden_touch, applicable_rules, context_assembly_manifest,
                    rollback_instructions, estimated_tokens, timeout_minutes,
                    completed_gates, blocked_gates, assigned_pipeline,
                    pipeline_modules, blocked_by, artifact_paths,
                    audit_findings, ke_entries, ai_autonomy_level,
                    autonomy_checklist, construction_status, verification_status,
                    schema_version, approval_required, priority_proposed,
                    rejection_cooldown_until, block_sessions_count
                ) VALUES (
                    :task_id, :namespace, :seq, :title, :status, :priority, :phase,
                    :execution_model, :model_rationale, :fallback_model,
                    :safety_level, :directive, :idempotent, :classification,
                    :evolution_policy, :estimate_hours, :actual_hours,
                    :files_in_scope, :deliverables, :acceptance,
                    :depends_on, :tags, :session_id, :waiting_for, :ready_at,
                    :completed_at, :created_at, :updated_at, 0,
                    :source_blueprint, :source_section, :description,
                    :upstream_files, :downstream_outputs, :allowed_touch,
                    :forbidden_touch, :applicable_rules, :context_assembly_manifest,
                    :rollback_instructions, :estimated_tokens, :timeout_minutes,
                    :completed_gates, :blocked_gates, :assigned_pipeline,
                    :pipeline_modules, :blocked_by, :artifact_paths,
                    :audit_findings, :ke_entries, :ai_autonomy_level,
                    :autonomy_checklist, :construction_status, :verification_status,
                    :schema_version, :approval_required, :priority_proposed,
                    :rejection_cooldown_until, :block_sessions_count
                )
                ON CONFLICT(task_id) DO UPDATE SET
                    namespace = excluded.namespace,
                    seq = excluded.seq,
                    title = excluded.title,
                    status = excluded.status,
                    priority = excluded.priority,
                    phase = excluded.phase,
                    execution_model = excluded.execution_model,
                    model_rationale = excluded.model_rationale,
                    fallback_model = excluded.fallback_model,
                    safety_level = excluded.safety_level,
                    directive = excluded.directive,
                    idempotent = excluded.idempotent,
                    classification = excluded.classification,
                    evolution_policy = excluded.evolution_policy,
                    estimate_hours = excluded.estimate_hours,
                    actual_hours = excluded.actual_hours,
                    files_in_scope = excluded.files_in_scope,
                    deliverables = excluded.deliverables,
                    acceptance = excluded.acceptance,
                    depends_on = excluded.depends_on,
                    tags = excluded.tags,
                    session_id = excluded.session_id,
                    waiting_for = excluded.waiting_for,
                    ready_at = excluded.ready_at,
                    completed_at = excluded.completed_at,
                    updated_at = excluded.updated_at,
                    is_deleted = 0,
                    deleted_at = NULL,
                    source_blueprint = excluded.source_blueprint,
                    source_section = excluded.source_section,
                    description = excluded.description,
                    upstream_files = excluded.upstream_files,
                    downstream_outputs = excluded.downstream_outputs,
                    allowed_touch = excluded.allowed_touch,
                    forbidden_touch = excluded.forbidden_touch,
                    applicable_rules = excluded.applicable_rules,
                    context_assembly_manifest = excluded.context_assembly_manifest,
                    rollback_instructions = excluded.rollback_instructions,
                    estimated_tokens = excluded.estimated_tokens,
                    timeout_minutes = excluded.timeout_minutes,
                    completed_gates = excluded.completed_gates,
                    blocked_gates = excluded.blocked_gates,
                    assigned_pipeline = excluded.assigned_pipeline,
                    pipeline_modules = excluded.pipeline_modules,
                    blocked_by = excluded.blocked_by,
                    artifact_paths = excluded.artifact_paths,
                    audit_findings = excluded.audit_findings,
                    ke_entries = excluded.ke_entries,
                    ai_autonomy_level = excluded.ai_autonomy_level,
                    autonomy_checklist = excluded.autonomy_checklist,
                    construction_status = excluded.construction_status,
                    verification_status = excluded.verification_status,
                    schema_version = excluded.schema_version,
                    approval_required = excluded.approval_required,
                    priority_proposed = excluded.priority_proposed,
                    rejection_cooldown_until = excluded.rejection_cooldown_until,
                    block_sessions_count = excluded.block_sessions_count
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
                    "context_assembly_manifest": json.dumps(
                        getattr(task, "context_assembly_manifest", []), ensure_ascii=False
                    ),
                    "rollback_instructions": getattr(task, "rollback_instructions", ""),
                    "estimated_tokens": getattr(task, "estimated_tokens", 0),
                    "timeout_minutes": getattr(task, "timeout_minutes", 0),
                    "completed_gates": json.dumps(
                        getattr(task, "completed_gates", []), ensure_ascii=False, default=str
                    ),
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
                    "schema_version": "0.3.2",
                    "approval_required": int(getattr(task, "approval_required", False)),
                    "priority_proposed": getattr(task, "priority_proposed", None),
                    "rejection_cooldown_until": getattr(task, "rejection_cooldown_until", None),
                    "block_sessions_count": getattr(task, "block_sessions_count", 0),
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

    # ------------------------------------------------------------------
    # Multi-Worker Batch Coordination (MOD-INF-016)
    # ------------------------------------------------------------------

    def claim_next(self, batch_id: str, worker_id: str) -> TaskCard | None:
        """原子认领批量中下一个依赖已满足的 READY 任务。

        多个 AI 对话并发调用 → 各拿各的，不重复。
        依赖检查：depends_on 为 NULL/空 或所有依赖均已 COMPLETED。

        返回 None 表示当前无可认领任务。
        """
        now = datetime.now(UTC).isoformat()
        with self._write_tx() as conn:
            row = conn.execute(
                """UPDATE tasks SET status = 'IN_PROGRESS',
                                     claimed_by = :worker_id,
                                     claimed_at = :now,
                                     updated_at = :now
                   WHERE task_id = (
                       SELECT t.task_id FROM tasks t
                       WHERE t.status = 'READY'
                         AND t.batch_id = :batch_id
                         AND t.is_deleted = 0
                         AND (
                             t.depends_on IS NULL
                             OR t.depends_on = '[]'
                             OR NOT EXISTS (
                                 SELECT 1 FROM json_each(t.depends_on)
                                 WHERE value != ''
                                 AND (SELECT status FROM tasks WHERE task_id = value) != 'COMPLETED'
                             )
                         )
                       ORDER BY t.priority ASC, t.created_at ASC
                       LIMIT 1
                   )
                   RETURNING *""",
                {"batch_id": batch_id, "worker_id": worker_id, "now": now},
            ).fetchone()
            if row is None:
                return None
            return _row_to_taskcard(row)

    def recover_stale_claims(self, batch_id: str, timeout_minutes: int = 30) -> int:
        """释放超时未完成的 IN_PROGRESS 任务 → 回到 READY。

        每个 AI session 调用 claim_next() 前先调此方法，确保崩溃/超时的任务自动复活。
        返回回收的任务数。
        """
        from datetime import timedelta as td

        cutoff = (datetime.now(UTC) - td(minutes=timeout_minutes)).isoformat()
        with self._write_tx() as conn:
            cursor = conn.execute(
                """UPDATE tasks SET status = 'READY',
                                     claimed_by = NULL,
                                     claimed_at = NULL,
                                     updated_at = :now
                   WHERE status = 'IN_PROGRESS'
                     AND batch_id = :batch_id
                     AND claimed_at < :cutoff""",
                {"batch_id": batch_id, "cutoff": cutoff, "now": datetime.now(UTC).isoformat()},
            )
            return cursor.rowcount

    def batch_progress(self, batch_id: str) -> dict[str, int]:
        """返回批量进度聚合：READY / IN_PROGRESS / COMPLETED / FAILED 各多少。"""
        with self._write_tx() as conn:
            rows = conn.execute(
                """SELECT status, COUNT(*) AS cnt
                   FROM tasks
                   WHERE batch_id = :batch_id AND is_deleted = 0
                   GROUP BY status""",
                {"batch_id": batch_id},
            ).fetchall()
        result = {"READY": 0, "IN_PROGRESS": 0, "COMPLETED": 0, "FAILED": 0, "TOTAL": 0}
        for r in rows:
            s = r["status"]
            if s in result:
                result[s] = r["cnt"]
            result["TOTAL"] += r["cnt"]
        return result


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


# ---------------------------------------------------------------------------
# FTS5 全文搜索（T-DB-010）
# ---------------------------------------------------------------------------

def search(
    db_path: Path | str,
    query: str,
    *,
    limit: int = 50,
    namespace: str | None = None,
) -> list[dict[str, object]]:
    """T-DB-010: 使用 FTS5 全文搜索任务。

    query
        搜索词（支持 FTS5 查询语法）。
    namespace
        可选命名空间过滤。
    limit
        返回结果上限（默认 50，最大 200）。

    返回 list[dict{task_id, title, status, priority, phase, snippet}]
    """
    resolved = Path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(resolved))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks_fts'"
        )
        has_fts = cursor.fetchone() is not None
        if not has_fts:
            conn.execute(
                """CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts
                   USING fts5(task_id, title, description, directive, content='tasks',
                   content_rowid='rowid')"""
            )
            conn.execute(
                """INSERT INTO tasks_fts(tasks_fts) VALUES('rebuild')"""
            )

        cols = "task_id, title, status, priority, phase"
        params: list[object] = [query]
        if namespace:
            params.append(namespace)
            limit_val = min(max(limit, 1), 200)
            params.append(limit_val)
            result = conn.execute(
                f"""SELECT t.{cols},
                           snippet(tasks_fts, 1, '<b>', '</b>', '...', 32) AS snippet
                    FROM tasks_fts
                    JOIN tasks t ON tasks_fts.task_id = t.task_id
                    WHERE tasks_fts MATCH ? AND t.namespace = ? AND t.is_deleted = 0
                    ORDER BY rank
                    LIMIT ?""",
                tuple(params),
            )
        else:
            limit_val = min(max(limit, 1), 200)
            params.append(limit_val)
            result = conn.execute(
                f"""SELECT t.{cols},
                           snippet(tasks_fts, 1, '<b>', '</b>', '...', 32) AS snippet
                    FROM tasks_fts
                    JOIN tasks t ON tasks_fts.task_id = t.task_id
                    WHERE tasks_fts MATCH ? AND t.is_deleted = 0
                    ORDER BY rank
                    LIMIT ?""",
                tuple(params),
            )
        return [dict(r) for r in result.fetchall()]
    finally:
        conn.close()
