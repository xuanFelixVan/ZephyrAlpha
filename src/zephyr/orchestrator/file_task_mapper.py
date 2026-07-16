# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.file_task_mapper
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.shared.io.paths; zephyr.shared.__init__; zephyr.shared.utils.time_utils
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
# [A_module] module_id=MOD-ORC_file_task_mapper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FileTaskMapper — 文件路径 ↔ Task N:N 映射器（#21 裁定重写）
============================================================
依据：#21 裁定（task_id 格式统一为 T-{SEQ}，N:N 映射取代 1:1）

变更（vs 旧版）
--------------
- derive_task_id() 废弃：task_id 不再从文件路径推导，改为全局自增 T-{SEQ}
- 1:1 映射改为 N:N：通过 task_files 表实现多对多
- 新增 namespace 字段：KBG/CP/KE/STD/DW/SRC/OPS 分类
- resolve/resolve_reverse 改为查询 task_files 表

功能
----
1. register_from_triage — 从 triage-result.yaml 批量写入 tasks + task_files 表
2. sync_file_state — 全量或单任务三态校验（磁盘/frontmatter/tasks）
3. rollback — 删除 tasks + task_files + events；不碰磁盘文件
4. resolve — 反向查询 file_path -> task_id 列表（N:N，可能多个）
5. resolve_reverse — 正向查询 task_id -> file_path 列表（N:N，可能多个）
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.utils.db_utils import get_db_connection, init_db
from zephyr.shared.utils.time_utils import now_iso
from zephyr.shared.schema.task_types import TaskNamespace

__all__ = [
    "FileTaskMapper",
    "RegisterReport",
    "SyncInconsistency",
    "SyncReport",
    "classify_file_to_namespace",
]


# 5.160.3 修复：SQL常量集中化
SQL_SELECT_TASK_FILE_BY_FILE_PATH = (
    "SELECT task_id FROM task_files WHERE file_path = ? ORDER BY task_id"
)
SQL_SELECT_TASK_FILE_BY_TASK_ID = (
    "SELECT file_path, role FROM task_files WHERE task_id = ? ORDER BY role, file_path"
)
SQL_SELECT_TASK_NEXT_SEQ = (
    "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM tasks WHERE namespace = ?"
)
SQL_INSERT_TASK = """INSERT INTO tasks
    (task_id, namespace, seq, phase, title, status, execution_model, safety_level,
     directive, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?, '', ?, ?)"""
SQL_INSERT_TASK_FILE = (
    "INSERT OR IGNORE INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)"
)
SQL_SELECT_TASK_FILE_JOIN_BY_TASK_ID = (
    "SELECT tf.task_id, tf.file_path, t.status "
    "FROM task_files tf JOIN tasks t ON tf.task_id = t.task_id "
    "WHERE tf.task_id = ? AND tf.role = 'primary'"
)
SQL_SELECT_TASK_FILE_JOIN_ALL = (
    "SELECT tf.task_id, tf.file_path, t.status "
    "FROM task_files tf JOIN tasks t ON tf.task_id = t.task_id "
    "WHERE tf.role = 'primary'"
)
SQL_DELETE_TASK_FILE = "DELETE FROM task_files WHERE task_id = ?"
SQL_DELETE_EVENT = "DELETE FROM events WHERE task_id = ?"
SQL_DELETE_TASK = "DELETE FROM tasks WHERE task_id = ?"


def classify_file_to_namespace(file_path: str) -> TaskNamespace:
    """
    从文件路径推导命名空间（#21 裁定：分类字段，不是 ID 的一部分）。

    推导优先级：
    1. KBG    -> 路径含 02_enterprise_architecture（企业架构真源区）
    2. CP     -> 路径含 construction-plan-
    3. KE     -> 路径含 KE-{数字} 或 ke-{数字}
    4. STD    -> 路径在 01_policies_and_standards/
    5. DW     -> 路径在 19_development_workspace/
    6. SRC    -> 路径在 src/zephyr/
    7. OPS    -> 兜底
    """
    p = file_path.replace("\\", "/")

    if "02_enterprise_architecture" in p:
        return TaskNamespace.KBG

    if "construction-plan-" in p:
        return TaskNamespace.CP

    if re.search(r"[Kk][Ee]-\d{3,}", p):
        return TaskNamespace.KE

    if "01_policies_and_standards" in p:
        return TaskNamespace.STD

    if "19_development_workspace" in p:
        return TaskNamespace.DW

    if p.startswith("src/zephyr/"):
        return TaskNamespace.SRC

    return TaskNamespace.OPS


@dataclass
class RegisterReport:
    total: int = 0
    inserted: int = 0
    skipped_existing: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class SyncInconsistency:
    task_id: str
    file_path: str
    disk_exists: bool
    frontmatter_status: str | None
    task_status: str
    issue: str


@dataclass
class SyncReport:
    checked: int = 0
    consistent: int = 0
    inconsistencies: list[SyncInconsistency] = field(default_factory=list)


def _check_consistency_is_ignored(
    disk_exists: bool,
    frontmatter_status: str | None,
    task_status: str,
) -> bool:
    if not disk_exists and task_status in ("PENDING", "READY", "WAITING"):
        return True

    if disk_exists and frontmatter_status in ("draft", "Draft") and task_status == "IN_PROGRESS":
        return True

    if (
        disk_exists
        and frontmatter_status in ("accepted", "Active", "active")
        and task_status in ("COMPLETED", "VERIFIED")
    ):
        return True

    return False


def _check_consistency_build_issue(
    disk_exists: bool,
    frontmatter_status: str | None,
    task_status: str,
) -> str | None:
    if disk_exists and frontmatter_status in ("accepted", "Active", "active") and task_status == "PENDING":
        return "STALE_TASK_WARNING: file accepted but task still PENDING"

    if not disk_exists and task_status in ("COMPLETED", "VERIFIED"):
        return "MISSING_ARTIFACT_ERROR: task completed/verified but file missing"

    if disk_exists and frontmatter_status in ("draft", "Draft") and task_status == "VERIFIED":
        return "DOWNGRADE_WARNING: file draft but task VERIFIED"

    return None


class FileTaskMapper:
    """
    文件路径 ↔ Task N:N 映射器。

    #21 裁定实现：通过 task_files 表实现多对多映射，
    取代 KBG-0038 的 1:1 双向映射。
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DB_PATH
        init_db(self._db_path)

    def resolve(self, file_path: str) -> list[str]:
        """反向查询 file_path -> task_id 列表（N:N，可能多个）。"""
        conn = get_db_connection(self._db_path)
        try:
            cursor = conn.execute(
                SQL_SELECT_TASK_FILE_BY_FILE_PATH,
                (file_path.replace("\\", "/"),),
            )
            return [row["task_id"] for row in cursor.fetchall()]
        finally:
            conn.close()

    def resolve_reverse(self, task_id: str) -> list[dict[str, str]]:
        """正向查询 task_id -> [{file_path, role}, ...] 列表。"""
        conn = get_db_connection(self._db_path)
        try:
            cursor = conn.execute(
                SQL_SELECT_TASK_FILE_BY_TASK_ID,
                (task_id,),
            )
            return [{"file_path": row["file_path"], "role": row["role"]} for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_tasks_for_file(self, file_path: str) -> list[str]:
        """获取涉及指定文件的所有任务 ID（resolve 的别名）。"""
        return self.resolve(file_path)

    def register_file(
        self,
        file_path: str,
        *,
        phase: int = 2,
        title: str = "",
        execution_model: str = "glm",
        safety_level: str = "M",
        role: str = "primary",
    ) -> str:
        """
        注册单个文件为任务，返回 task_id。

        task_id 格式为 {NAMESPACE}-{SEQ}（命名空间内自增）。
        """
        fp = file_path.replace("\\", "/")
        namespace = classify_file_to_namespace(fp)
        now = now_iso()

        conn = get_db_connection(self._db_path)
        try:
            cursor = conn.execute(
                SQL_SELECT_TASK_NEXT_SEQ,
                (namespace.value,),
            )
            next_seq = cursor.fetchone()["next_seq"]
            task_id = f"{namespace.value}-{next_seq}"

            task_title = title or Path(fp).stem

            conn.execute("BEGIN")
            conn.execute(
                SQL_INSERT_TASK,
                (task_id, namespace.value, next_seq, phase, task_title, execution_model, safety_level, now, now),
            )
            conn.execute(
                SQL_INSERT_TASK_FILE,
                (task_id, fp, role),
            )
            conn.execute("COMMIT")
            return task_id
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def register_from_triage(self, yaml_path: Path) -> RegisterReport:
        """从 triage-result.yaml 批量写入 tasks + task_files 表。"""
        report = RegisterReport()

        if not yaml_path.exists():
            report.errors.append(f"triage file not found: {yaml_path}")
            return report

        with open(yaml_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        entries = data.get("files", [])
        report.total = len(entries)

        conn = get_db_connection(self._db_path)
        try:
            for entry in entries:
                fp = str(entry.get("path", "")).replace("\\", "/")
                if not fp:
                    continue

                namespace = classify_file_to_namespace(fp)
                phase = entry.get("phase", 2)
                title = entry.get("title") or entry.get("name") or Path(fp).stem
                execution_model = entry.get("execution_model", "glm")
                safety_level = entry.get("safety_level", "M")
                role = entry.get("role", "primary")
                now = now_iso()

                try:
                    cursor = conn.execute(
                        SQL_SELECT_TASK_NEXT_SEQ,
                        (namespace.value,),
                    )
                    next_seq = cursor.fetchone()["next_seq"]
                    task_id = f"{namespace.value}-{next_seq}"

                    conn.execute("BEGIN")
                    conn.execute(
                        SQL_INSERT_TASK,
                        (task_id, namespace.value, next_seq, phase, title, execution_model, safety_level, now, now),
                    )
                    conn.execute(
                        SQL_INSERT_TASK_FILE,
                        (task_id, fp, role),
                    )
                    conn.execute("COMMIT")
                    report.inserted += 1
                except Exception as e:
                    conn.execute("ROLLBACK")
                    report.errors.append(f"{fp}: {e}")
        finally:
            conn.close()

        return report

    def sync_file_state(self, task_id: str | None = None) -> SyncReport:
        """
        全量或单任务三态校验（磁盘/frontmatter/tasks）。

        通过 task_files 表查询关联文件，而非 tasks.file_path。
        """
        report = SyncReport()
        repo_root = REPO_ROOT

        conn = get_db_connection(self._db_path)
        try:
            if task_id:
                rows = conn.execute(
                    SQL_SELECT_TASK_FILE_JOIN_BY_TASK_ID,
                    (task_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    SQL_SELECT_TASK_FILE_JOIN_ALL
                ).fetchall()

            for row in rows:
                tid = row["task_id"]
                fp = row["file_path"]
                task_status = row["status"]
                report.checked += 1

                disk_path = repo_root / fp
                disk_exists = disk_path.exists()

                fm_status: str | None = None
                if disk_exists and disk_path.suffix == ".md":
                    fm_status = self._read_frontmatter_status(disk_path)

                inconsistency = self._check_consistency(tid, fp, disk_exists, fm_status, task_status)
                if inconsistency:
                    report.inconsistencies.append(inconsistency)
                else:
                    report.consistent += 1
        finally:
            conn.close()

        return report

    def rollback(self, task_id: str) -> None:
        """删除 tasks + task_files + events；不碰磁盘文件。"""
        conn = get_db_connection(self._db_path)
        try:
            conn.execute("BEGIN")
            conn.execute(SQL_DELETE_TASK_FILE, (task_id,))
            conn.execute(SQL_DELETE_EVENT, (task_id,))
            conn.execute(SQL_DELETE_TASK, (task_id,))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def _read_frontmatter_status(self, filepath: Path) -> str | None:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            if not content.startswith("---"):
                return None
            end_idx = content.find("---", 3)
            if end_idx == -1:
                return None
            fm_text = content[3:end_idx].strip()
            fm = yaml.safe_load(fm_text)
            if isinstance(fm, dict):
                return str(fm.get("status", "")).strip() or None
        except Exception as e:
            logger.debug("suppressed error in file_task_mapper", exc_info=True)
        return None

    def _check_consistency(
        self,
        task_id: str,
        file_path: str,
        disk_exists: bool,
        frontmatter_status: str | None,
        task_status: str,
    ) -> SyncInconsistency | None:
        if _check_consistency_is_ignored(disk_exists, frontmatter_status, task_status):
            return None

        issue = _check_consistency_build_issue(disk_exists, frontmatter_status, task_status)
        if issue is not None:
            return SyncInconsistency(
                task_id=task_id,
                file_path=file_path,
                disk_exists=disk_exists,
                frontmatter_status=frontmatter_status,
                task_status=task_status,
                issue=issue,
            )

        return None
