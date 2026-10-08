"""活库真源夹具：gates/tasks 建库语句逐字照抄生产 DDL（禁幻影表，WP1 改 1 / 台账 R-A4）。

- live_gates_ddl ← src/zephyr/governance/persistence/sqlite_schema.py migration 34
  （gates 兼容表，与 gate_runs 同构；details 默认值 '{}' 是自愈修复值唯一真源）。
- live_tasks_projection_ddl ← tasks 表 verifier 触达列投影（task_id/title/status；
  活库 status 无 CHECK，合法值集唯一真源=_DDL_TASKS 的 CHECK(status IN (...))）。
- 旧版用例自建 gates(gate_id, result) 幻影表，与坏写入端共谋出静默空转——本夹具治本。
"""

from __future__ import annotations

import pytest

# 逐字照抄 sqlite_schema.py migration 34 的 CREATE TABLE gates（禁凭记忆改列）
_LIVE_GATES_DDL = """
CREATE TABLE gates (
    gate_run_id  TEXT PRIMARY KEY,
    gate_id      TEXT NOT NULL,
    passed       INTEGER NOT NULL CHECK(passed IN (0,1)),
    details      TEXT NOT NULL DEFAULT '{}',
    artifact_path TEXT,
    session_id   TEXT,
    task_id      TEXT,
    created_at   TEXT NOT NULL
)
"""

# tasks 触达列投影（列集与用例 bare INSERT VALUES 三元组对齐；status 活库无 CHECK）
_LIVE_TASKS_PROJECTION_DDL = """
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    title   TEXT NOT NULL,
    status  TEXT NOT NULL DEFAULT 'PENDING'
)
"""


@pytest.fixture
def live_gates_ddl() -> str:
    return _LIVE_GATES_DDL


@pytest.fixture
def live_tasks_projection_ddl() -> str:
    return _LIVE_TASKS_PROJECTION_DDL


@pytest.fixture
def insert_live_gate_row():
    """按活库实列插一行 gates（created_at NOT NULL 由夹具供值，details 默认=活库列默认）。"""

    def _insert(
        conn,
        gate_run_id: str,
        *,
        passed: int = 1,
        details: str = "{}",
        created_at: str = "2026-09-19T00:00:00Z",
    ) -> None:
        conn.execute(
            "INSERT INTO gates (gate_run_id, gate_id, passed, details, created_at) VALUES (?,?,?,?,?)",
            (gate_run_id, gate_run_id, passed, details, created_at),
        )

    return _insert
