# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.data.persistence.circuit_breaker_repo
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.governance.persistence.circuit_breaker_types
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
# [A_module] module_id=MOD-DAT_circuit_breaker_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
circuit_breaker_repo.py — circuit_breaker_state 表持久化仓库（AUDIT-07 P1-5）

职责：circuit_breaker_state 表的 CRUD 操作，供 gates/circuit_breaker.py 调用。
禁止 circuit_breaker.py 直接操作 SQL——所有 circuit_breaker_state 表操作必须经过本仓库。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.governance.persistence.circuit_breaker_types import CircuitBreakerState
from zephyr.shared.utils.db_utils import DB_PATH, get_db_connection

__all__ = [
    "CircuitBreakerRecord",
    "CircuitBreakerRepo",
]


@dataclass(frozen=True)
class CircuitBreakerRecord:
    id: int
    caller_module: str
    target_module: str
    state: CircuitBreakerState
    failure_count: int
    last_failure_at: str | None
    opened_at: str | None
    reason: str | None
    created_at: str
    updated_at: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_record(row: Any) -> Self:
    return CircuitBreakerRecord(
        id=row["id"],
        caller_module=row["caller_module"],
        target_module=row["target_module"],
        state=CircuitBreakerState(row["state"]),
        failure_count=row["failure_count"],
        last_failure_at=row["last_failure_at"],
        opened_at=row["opened_at"],
        reason=row["reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class CircuitBreakerRepo:
    """circuit_breaker_state 表持久化仓库。"""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._conn = get_db_connection(self._db_path)

    def get_state(self, caller: str, target: str) -> CircuitBreakerRecord | None:
        cursor = self._conn.execute(
            "SELECT * FROM circuit_breaker_state WHERE caller_module = ? AND target_module = ?",
            (caller, target),
        )
        row = cursor.fetchone()
        return _row_to_record(row) if row else None

    def insert(
        self,
        *,
        caller: str,
        target: str,
        state: CircuitBreakerState,
        failure_count: int = 1,
        last_failure_at: str | None = None,
        opened_at: str | None = None,
        reason: str | None = None,
    ) -> int:
        now = _now_iso()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            cursor = self._conn.execute(
                """
                INSERT INTO circuit_breaker_state
                    (caller_module, target_module, state, failure_count,
                     last_failure_at, opened_at, reason, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (caller, target, state.value, failure_count, last_failure_at, opened_at, reason, now, now),
            )
            self._conn.execute("COMMIT")
            return cursor.lastrowid
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def update(
        self,
        *,
        caller: str,
        target: str,
        state: CircuitBreakerState,
        failure_count: int,
        last_failure_at: str | None,
        opened_at: str | None,
        reason: str | None,
    ) -> None:
        now = _now_iso()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                """
                UPDATE circuit_breaker_state
                SET state = ?, failure_count = ?, last_failure_at = ?,
                    opened_at = ?, reason = ?, updated_at = ?
                WHERE caller_module = ? AND target_module = ?
                """,
                (state.value, failure_count, last_failure_at, opened_at, reason, now, caller, target),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def reset(self, caller: str, target: str) -> None:
        now = _now_iso()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                """
                UPDATE circuit_breaker_state
                SET state = 'CLOSED', failure_count = 0,
                    opened_at = NULL, reason = NULL, updated_at = ?
                WHERE caller_module = ? AND target_module = ?
                """,
                (now, caller, target),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def list_open(self) -> list[CircuitBreakerRecord]:
        cursor = self._conn.execute("SELECT * FROM circuit_breaker_state WHERE state = 'OPEN' ORDER BY opened_at DESC")
        return [_row_to_record(row) for row in cursor.fetchall()]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
