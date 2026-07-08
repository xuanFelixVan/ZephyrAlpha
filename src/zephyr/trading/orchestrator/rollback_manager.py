# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.rollback_manager
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_rollback_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackManager — 仅调试用途的 DB-state 快照，不用于自动回滚。
================================================================

⚠️ 降级声明（MOD-INF-021 D-021-04）：
    本模块已被双轨回滚体系（git-native + SQLite dump JSONL）取代。
    checkpoint() / rollback_to() / list_checkpoints() / undo_last()
    仅保留用于手动调试场景的 DB 状态快照，不再参与自动回滚链路。

自动回滚路径：
    -> src/zephyr/rollback/rollback_executor.py（文件+DB 双轨联动）
    -> src/zephyr/rollback/sqlite_dumper.py（SQLite dump/restore/verify）

原设计（已废弃）：
    依据： §4.5（回滚策略）
    功能：
    1. checkpoint — 创建检查点（快照 tasks + events 表状态）
    2. rollback_to — 回滚到指定检查点
    3. list_checkpoints — 列出所有检查点
    4. undo_last — 撤销最近一次操作
    回滚策略：
    - 检查点存储在 events 表（event_type = 'checkpoint'）
    - 回滚时：恢复 tasks 表状态到检查点时刻
    - 不碰磁盘文件（只恢复数据库状态）
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.utils.db_utils import get_db_connection
from zephyr.shared.utils.time_utils import now_iso
from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "Checkpoint",
    "RollbackManager",
]


@dataclass
class Checkpoint:
    checkpoint_id: str
    created_at: str
    description: str
    task_count: int


class RollbackManager:
    """
    实现状态回滚：记录操作日志、支持 undo。
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DB_PATH

    def checkpoint(self, description: str = "") -> str:
        """
        创建检查点（快照 tasks 表状态）。

        Returns
        -------
        str
            检查点 ID（时间戳格式）。
        """
        now = now_iso()
        cp_id = f"CP-{now.replace(':', '-').replace('+', 'Z')}"

        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT task_id, status, phase, title, execution_model, safety_level, "
                "directive, depends_on, files_in_scope, session_id, waiting_for, ready_at "
                "FROM tasks"
            ).fetchall()

            snapshot: list[dict] = []
            for row in rows:
                snapshot.append(
                    {
                        "task_id": row["task_id"],
                        "status": row["status"],
                        "phase": row["phase"],
                        "title": row["title"],
                        "execution_model": row["execution_model"],
                        "safety_level": row["safety_level"],
                        "directive": row["directive"],
                        "depends_on": row["depends_on"],
                        "files_in_scope": row["files_in_scope"],
                        "session_id": row["session_id"],
                        "waiting_for": row["waiting_for"],
                        "ready_at": row["ready_at"],
                    }
                )

            payload = json.dumps(snapshot, ensure_ascii=False)

            conn.execute("BEGIN")
            conn.execute(
                """INSERT INTO events
                   (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'manual_event', ?, NULL, ?)""",
                (cp_id, payload, now),
            )
            conn.execute("COMMIT")
        except ValueError:
            raise
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception as e:
                logger.debug("suppressed error in rollback_manager", exc_info=True)
            raise
        finally:
            conn.close()

        return cp_id

    def rollback_to(self, checkpoint_id: str) -> int:
        """
        回滚到指定检查点。

        Returns
        -------
        int
            恢复的任务数量。
        """
        conn = get_db_connection(self._db_path)
        try:
            row = conn.execute(
                "SELECT payload FROM events WHERE event_type = 'manual_event' AND event_id = ?",
                (checkpoint_id,),
            ).fetchone()

            if not row:
                raise ValueError(f"Checkpoint not found: {checkpoint_id}")

            snapshot: list[dict] = json.loads(row["payload"])

            conn.execute("BEGIN")
            for task_data in snapshot:
                conn.execute(
                    """UPDATE tasks SET
                       status = ?, phase = ?, title = ?, execution_model = ?,
                       safety_level = ?, directive = ?, depends_on = ?,
                       files_in_scope = ?, session_id = ?, waiting_for = ?,
                       ready_at = ?, updated_at = ?
                       WHERE task_id = ?""",
                    (
                        task_data["status"],
                        task_data["phase"],
                        task_data["title"],
                        task_data["execution_model"],
                        task_data["safety_level"],
                        task_data["directive"],
                        task_data["depends_on"],
                        task_data["files_in_scope"],
                        task_data["session_id"],
                        task_data["waiting_for"],
                        task_data["ready_at"],
                        now_iso(),
                        task_data["task_id"],
                    ),
                )

            now = now_iso()
            conn.execute(
                """INSERT INTO events
                   (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'manual_event', ?, ?, ?)""",
                (f"ROLLBACK-{now.replace(':', '-')}", f'{{"action":"rollback","target":"{checkpoint_id}"}}', None, now),
            )
            conn.execute("COMMIT")

            return len(snapshot)
        except ValueError:
            conn.close()
            raise
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception as e:
                logger.debug("suppressed error in rollback_manager", exc_info=True)
            raise
        finally:
            conn.close()

    def list_checkpoints(self) -> list[Checkpoint]:
        """列出所有检查点。"""
        conn = get_db_connection(self._db_path)
        try:
            rows = conn.execute(
                "SELECT event_id, payload, created_at FROM events WHERE event_type = 'manual_event' AND event_id LIKE 'CP-%' ORDER BY created_at DESC"
            ).fetchall()

            checkpoints: list[Checkpoint] = []
            for row in rows:
                try:
                    snapshot: list[dict] = json.loads(row["payload"])
                    if isinstance(snapshot, list):
                        checkpoints.append(
                            Checkpoint(
                                checkpoint_id=row["event_id"],
                                created_at=row["created_at"],
                                description=f"Snapshot with {len(snapshot)} tasks",
                                task_count=len(snapshot),
                            )
                        )
                except (json.JSONDecodeError, TypeError):
                    continue
            return checkpoints
        finally:
            conn.close()

    def undo_last(self) -> str | None:
        """
        撤销最近一次操作（回滚到上一个检查点）。

        Returns
        -------
        str or None
            回滚到的检查点 ID，若无可用检查点则返回 None。
        """
        cps = self.list_checkpoints()
        if not cps:
            return None

        target_cp = cps[0]
        self.rollback_to(target_cp.checkpoint_id)
        return target_cp.checkpoint_id
