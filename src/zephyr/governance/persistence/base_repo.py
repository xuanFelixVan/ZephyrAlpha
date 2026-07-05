# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
# [MODULE] zephyr.governance.persistence.base_repo
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.__init__; zephyr.integration.shared.schema.severity_types
# [CONSUMERS] task_repo;query;transition
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _ALLOWED_TRANSITIONS 不可变; 异常类层次稳定; _row_to_taskcard 字段映射完整
# [MODIFY-GUARD] task_repo.py;query.py;transition.py（三模块共享基础设施）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TaskNotFoundError;InvalidTransitionError;DuplicateTaskError;DatabaseError;QueryError;DependencyError
# [TESTS] tests/db/
# [A_module] module_id=MOD-DAT_base_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md

base_repo — 异常类、状态机常量、工具函数（从 task_repo.py 拆分，SRC-0066）

==========================================================================

本模块包含 TaskRepository 的基础设施：

- 异常类层次（6 个异常）

- 状态机转换表（_ALLOWED_TRANSITIONS）

- 工具函数（_row_to_taskcard、now_iso、_new_id）

- 模块级查询助手（allowed_transitions、is_terminal）

- FTS5 全文搜索（search）

Safety : H（基础设施核心，状态机错误会影响整个任务流水线）

"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.schema.task_types import TaskCard, TaskStatus
from zephyr.shared.utils.time_utils import now_iso as _now_iso_true_source  # 5.12.3 修复：统一Z后缀真源

logger = logging.getLogger(__name__)


__all__ = [
    # 5.154.7 修复: 移除 _ALLOWED_TRANSITIONS/_is_valid_transition/_new_id/_row_to_taskcard 私有符号
    "InvalidTransitionError",
    "P0InflationFrozenError",
    "P0InflationWarning",
    "RejectedUpgradeCoolingOffError",
    "TaskNotFoundError",
    "TaskRepositoryError",
    "allowed_transitions",
    "is_terminal",
    "now_iso",
    "search",
]


# ---------------------------------------------------------------------------

# 异常类

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
    """返回当前 UTC 时间的 ISO 8601 字符串（Z 后缀真源：shared/utils/time_utils.now_iso）。"""
    # 5.12.3 修复：原 datetime.now(_UTC).isoformat() 产出 "+00:00" 后缀，
    # 与真源 shared/utils/time_utils.now_iso() 的 "Z" 后缀漂移，导致字符串排序错乱。
    return _now_iso_true_source()


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
            f"TaskCard {d.get('task_id', '?')} schema_version={schema_ver} 与当前 0.3.2 不匹配，"
            f"可能缺少新增字段（autonomy_checklist 等），数据完整性未经验证。",
            UserWarning,
            stacklevel=2,
        )

    return TaskCard.model_validate(d)


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
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks_fts'")

        has_fts = cursor.fetchone() is not None

        if not has_fts:
            conn.execute(
                """CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts

                   USING fts5(task_id, title, description, directive, content='tasks',

                   content_rowid='rowid')"""
            )

            conn.execute("""INSERT INTO tasks_fts(tasks_fts) VALUES('rebuild')""")

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
