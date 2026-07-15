# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.state_synchronizer
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.shared.io.paths; zephyr.shared.utils.time_utils; zephyr.trading.__init__
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
# [A_module] module_id=MOD-ORC_state_synchronizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StateSynchronizer — 同步 SQLite 状态与文件系统实际状态（T-2-04）
==============================================================
依据： §4.4（三态一致性校验）

功能
----
1. sync_all — 全量同步：磁盘状态 -> frontmatter -> tasks 表
2. sync_task — 单任务同步
3. detect_orphans — 检测孤儿文件（磁盘存在但无 task 记录）
4. detect_ghosts — 检测幽灵任务（task 存在但文件已删除）

三态一致性规则（ §4.4）
-----------------------------------
| 磁盘 | frontmatter | tasks   | 允许 | 不一致处置 |
|------|-------------|---------|------|-----------|
| 不存在 | — | PENDING/READY/WAITING | ✅ | — |
| 存在 | draft | IN_PROGRESS | ✅ | — |
| 存在 | accepted | COMPLETED/VERIFIED | ✅ | — |
| 存在 | accepted | PENDING | ❌ | -> VERIFIED |
| 不存在 | — | COMPLETED/VERIFIED | ❌ | -> PENDING |
| 存在 | draft | VERIFIED | ❌ | -> IN_PROGRESS |
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json as _json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.utils.db_utils import get_db_connection
from zephyr.shared.utils.time_utils import now_iso

__all__ = [
    "GhostTask",
    "OrphanFile",
    "StateSynchronizer",
    "SyncResult",
]


@dataclass
class SyncResult:
    task_id: str
    file_path: str
    action: str
    old_status: str
    new_status: str
    reason: str


@dataclass
class OrphanFile:
    file_path: str
    suggested_task_id: str


@dataclass
class GhostTask:
    task_id: str
    file_path: str
    task_status: str


def _is_state_acceptable(
    disk_exists: bool,
    frontmatter_status: str | None,
    task_status: str,
) -> bool:
    """Return True when the three-state combination is consistent (no action needed)."""
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


def _build_stale_task_result(task_id: str, file_path: str, task_status: str) -> SyncResult:
    """Build SyncResult for accepted-file-but-task-still-PENDING (upgrade to VERIFIED)."""
    return SyncResult(
        task_id=task_id,
        file_path=file_path,
        action="STALE_TASK_WARNING",
        old_status=task_status,
        new_status="VERIFIED",
        reason="File accepted but task still PENDING, upgrading to VERIFIED",
    )


def _build_missing_artifact_result(task_id: str, file_path: str, task_status: str) -> SyncResult:
    """Build SyncResult for completed/verified task whose file is missing (revert to PENDING)."""
    return SyncResult(
        task_id=task_id,
        file_path=file_path,
        action="MISSING_ARTIFACT_ERROR",
        old_status=task_status,
        new_status="PENDING",
        reason="Task completed/verified but file missing, reverting to PENDING",
    )


def _build_downgrade_result(task_id: str, file_path: str, task_status: str) -> SyncResult:
    """Build SyncResult for draft-file-but-task-VERIFIED (downgrade to IN_PROGRESS)."""
    return SyncResult(
        task_id=task_id,
        file_path=file_path,
        action="DOWNGRADE_WARNING",
        old_status=task_status,
        new_status="IN_PROGRESS",
        reason="File draft but task VERIFIED, downgrading to IN_PROGRESS",
    )


class StateSynchronizer:
    """
    同步 SQLite 状态与文件系统实际状态。
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DB_PATH

    def _iter_task_files(self, conn: object) -> list[tuple[str, str, str]]:
        """返回 [(task_id, file_path, status), ...] 过滤空 files_in_scope。"""
        rows = conn.execute(
            "SELECT task_id, files_in_scope, status FROM tasks "
            "WHERE files_in_scope IS NOT NULL AND files_in_scope != '[]'"
        ).fetchall()
        result: list[tuple[str, str, str]] = []
        for row in rows:
            try:
                file_list = _json.loads(row["files_in_scope"])
            except (_json.JSONDecodeError, TypeError):
                continue
            for fp in file_list:
                if isinstance(fp, str) and fp:
                    result.append((row["task_id"], fp, row["status"]))
        return result

    def sync_all(self, auto_fix: bool = False) -> list[SyncResult]:
        """
        全量同步：磁盘状态 -> frontmatter -> tasks 表。

        Parameters
        ----------
        auto_fix : bool
            为 True 时自动修复不一致（更新 tasks 表状态）。
        """
        results: list[SyncResult] = []

        conn = get_db_connection(self._db_path)
        try:
            for tid, fp, task_status in self._iter_task_files(conn):
                disk_path = REPO_ROOT / fp
                disk_exists = disk_path.exists()

                fm_status: str | None = None
                if disk_exists and disk_path.suffix == ".md":
                    fm_status = self._read_frontmatter_status(disk_path)

                result = self._check_and_fix(conn, tid, fp, disk_exists, fm_status, task_status, auto_fix)
                if result:
                    results.append(result)
        finally:
            conn.close()

        return results

    def sync_task(self, task_id: str, auto_fix: bool = False) -> SyncResult | None:
        """单任务同步。"""
        conn = get_db_connection(self._db_path)
        try:
            row = conn.execute(
                "SELECT task_id, files_in_scope, status FROM tasks "
                "WHERE task_id = ? AND files_in_scope IS NOT NULL AND files_in_scope != '[]'",
                (task_id,),
            ).fetchone()

            if not row:
                return None

            try:
                file_list = _json.loads(row["files_in_scope"])
            except (_json.JSONDecodeError, TypeError):
                return None

            task_status = row["status"]
            for fp in file_list:
                if not isinstance(fp, str) or not fp:
                    continue
                disk_path = REPO_ROOT / fp
                disk_exists = disk_path.exists()

                fm_status: str | None = None
                if disk_exists and disk_path.suffix == ".md":
                    fm_status = self._read_frontmatter_status(disk_path)

                return self._check_and_fix(conn, task_id, fp, disk_exists, fm_status, task_status, auto_fix)
            return None
        finally:
            conn.close()

    def detect_orphans(self, scan_dir: Path, pattern: str = "**/*.md") -> list[OrphanFile]:
        """检测孤儿文件（磁盘存在但无 task 记录）。"""
        orphans: list[OrphanFile] = []

        conn = get_db_connection(self._db_path)
        try:
            for f in sorted(scan_dir.rglob(pattern)):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(_REPO_ROOT)).replace("\\", "/")
                escaped = rel.replace("'", "''")
                row = conn.execute(
                    "SELECT task_id FROM tasks WHERE files_in_scope LIKE ?",
                    (f"%{escaped}%",),
                ).fetchone()
                if not row:
                    from zephyr.orchestrator.file_task_mapper import derive_task_id

                    orphans.append(
                        OrphanFile(
                            file_path=rel,
                            suggested_task_id=derive_task_id(rel),
                        )
                    )
        finally:
            conn.close()

        return orphans

    def detect_ghosts(self) -> list[GhostTask]:
        """检测幽灵任务（task 存在但文件已删除）。"""
        ghosts: list[GhostTask] = []

        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT task_id, files_in_scope, status FROM tasks "
                "WHERE files_in_scope IS NOT NULL AND files_in_scope != '[]'"
            ).fetchall()

            for row in rows:
                try:
                    file_list = _json.loads(row["files_in_scope"])
                except (_json.JSONDecodeError, TypeError):
                    continue
                for fp in file_list:
                    if not isinstance(fp, str) or not fp:
                        continue
                    disk_path = REPO_ROOT / fp
                    if not disk_path.exists():
                        ghosts.append(
                            GhostTask(
                                task_id=row["task_id"],
                                file_path=fp,
                                task_status=row["status"],
                            )
                        )
        finally:
            conn.close()

        return ghosts

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
            logger.warning("suppressed error in state_synchronizer", exc_info=True)
        return None

    def _check_and_fix(
        self,
        conn: object,
        task_id: str,
        file_path: str,
        disk_exists: bool,
        frontmatter_status: str | None,
        task_status: str,
        auto_fix: bool,
    ) -> SyncResult | None:
        if _is_state_acceptable(disk_exists, frontmatter_status, task_status):
            return None

        if disk_exists and frontmatter_status in ("accepted", "Active", "active") and task_status == "PENDING":
            result = _build_stale_task_result(task_id, file_path, task_status)
            if auto_fix:
                self._update_task_status(conn, task_id, result.new_status)
            return result

        if not disk_exists and task_status in ("COMPLETED", "VERIFIED"):
            result = _build_missing_artifact_result(task_id, file_path, task_status)
            if auto_fix:
                self._update_task_status(conn, task_id, result.new_status)
            return result

        if disk_exists and frontmatter_status in ("draft", "Draft") and task_status == "VERIFIED":
            result = _build_downgrade_result(task_id, file_path, task_status)
            if auto_fix:
                self._update_task_status(conn, task_id, result.new_status)
            return result

        return None

    def _update_task_status(self, conn: object, task_id: str, new_status: str) -> None:
        now = now_iso()
        conn.execute("BEGIN")
        conn.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
            (new_status, now, task_id),
        )
        conn.execute("COMMIT")
