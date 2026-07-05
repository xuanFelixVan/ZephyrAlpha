# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md
# [MODULE] zephyr.governance.commit_gates.gate_repo
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.db_utils
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
# [A_module] module_id=MOD-DAT_gate_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
gate_repo.py — gates 表持久化仓库（AUDIT-07 P1-5: 从 gate_engine.py 提取）

职责：gates 表的 INSERT/SELECT 操作，供 gate_engine.py 和 task_repo.py 调用。
禁止 gate_engine.py 直接操作 SQL——所有 gates 表写入必须经过本仓库。

事务语义：
  - conn 参数非空时，不管理事务（由调用方负责 BEGIN/COMMIT/ROLLBACK）
  - conn 参数为 None 时，自行 BEGIN IMMEDIATE → COMMIT/ROLLBACK
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.utils.db_utils import get_db_connection

__all__ = [
    "GateRepo",
    "GateRunRecord",
]


@dataclass(frozen=True)
class GateRunRecord:
    gate_run_id: str
    gate_id: str
    passed: bool
    details: str
    artifact_path: str | None
    session_id: str | None
    task_id: str | None
    created_at: str


class GateRepo:
    """gates 表持久化仓库。"""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._conn = get_db_connection(self._db_path)

    def persist(
        self,
        *,
        gate_id: str,
        task_id: str | None,
        passed: bool,
        violations: list[dict[str, Any]],
        artifact_path: str | None = None,
        session_id: str | None = None,
        evaluated_at: str | None = None,
        conn: Any | None = None,
    ) -> str:
        gate_run_id = f"gr-{uuid.uuid4()}"
        composite_gate_id = f"{gate_id}:{task_id}" if task_id else gate_id
        details_json = json.dumps(violations, ensure_ascii=False)
        created_at = evaluated_at or datetime.now(UTC).isoformat()

        target = conn if conn is not None else self._conn
        manage_tx = conn is None

        if manage_tx:
            target.execute("BEGIN IMMEDIATE")
        try:
            target.execute(
                """
                INSERT INTO gate_runs
                    (gate_run_id, gate_id, passed, details, artifact_path,
                     session_id, task_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    gate_run_id,
                    composite_gate_id,
                    1 if passed else 0,
                    details_json,
                    artifact_path,
                    session_id,
                    task_id,
                    created_at,
                ),
            )
            if manage_tx:
                target.execute("COMMIT")
        except Exception:
            if manage_tx:
                target.execute("ROLLBACK")
            raise

        return gate_run_id

    def query_by_task(
        self,
        task_id: str,
        limit: int = 50,
    ) -> list[GateRunRecord]:
        conn = self._conn
        cursor = conn.execute(
            """
            SELECT gate_run_id, gate_id, passed, details,
                   artifact_path, session_id, task_id, created_at
            FROM gate_runs
            WHERE task_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (task_id, limit),
        )
        results: list[GateRunRecord] = []
        for row in cursor.fetchall():
            results.append(
                GateRunRecord(
                    gate_run_id=row["gate_run_id"],
                    gate_id=row["gate_id"],
                    passed=bool(row["passed"]),
                    details=row["details"],
                    artifact_path=row["artifact_path"],
                    session_id=row["session_id"],
                    task_id=row["task_id"],
                    created_at=row["created_at"],
                )
            )
        return results

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
