# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# tests/conftest.py already adds src/ to sys.path.
# ARCH-034 P4: replaced manual importlib.util.spec_from_file_location loading
# (caused circular-import deadlocks via governance.audit_trail chain) with
# normal imports — test files import what they need directly.
#
# NOTE: sqlite_dumper mock removed (2026-08-17 audit fix) — sys.modules MagicMock
# injection at conftest scope pollutes the entire pytest process. Tests that need
# sqlite_dumper isolation should use monkeypatch/fixtures at test scope instead.

import sqlite3

import pytest

# ── WP1 改 1（2026-09-19）：gates 用例建库必须照活库 DDL 逐字抄 ──────────────────
# 旧夹具自建 `gates(gate_id, result)` 幻影结构（生产 governance.db 无 `result` 列），
# 与被修坏写入端共谋出"用例全绿却查不出静默空转"（施工台账 R-A4 / 回执站点一）。
# 下面这段是 2026-09-19 从 governance.db 的 `select sql from sqlite_master where
# name='gates'` 原文照抄（含缩进），不是 sqlite_schema.py 的源码 DDL——
# 两者已实测漂移过（D-17），断言结构一律以活库为准。
_LIVE_GATES_DDL = """CREATE TABLE "gates" (
                gate_run_id TEXT PRIMARY KEY,
                gate_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK(passed IN (0,1)),
                details TEXT NOT NULL DEFAULT '{}',
                artifact_path TEXT,
                session_id TEXT,
                task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            )"""

# 活库 tasks 的关键事实（同一 D-17 口径，实测 `pragma table_info(tasks)` + DDL 原文）：
# status 列是 `TEXT DEFAULT 'PENDING'`——**既无 NOT NULL 也无 CHECK**（源码 _DDL_TASKS 里有
# CHECK(status IN (10 值))，活库这条约束根本不存在）。用例建库只取本方法实际读取的
# task_id/status 两列，但必须复现"status 无 CHECK ⇒ 任意脏值可入库"这一生产属性，
# 否则 C-0 类误改（READY/BLOCKED 被判脏）在用例层面永远测不出来。
_LIVE_TASKS_PROJECTION_DDL = "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, title TEXT, status TEXT)"


@pytest.fixture
def live_gates_ddl() -> str:
    """活库 gates 真实列建表语句（禁改列名：用例结构必须从活库读，不造幻影表）。"""
    return _LIVE_GATES_DDL


@pytest.fixture
def live_tasks_projection_ddl() -> str:
    """tasks 的读取投影（task_id/status），保留活库属性：status 无 CHECK。"""
    return _LIVE_TASKS_PROJECTION_DDL


@pytest.fixture
def insert_live_gate_row():
    """向活库结构的 gates 插一行；details 可注入非 JSON 文本（活库该列无 CHECK）。"""

    def _insert(
        conn: sqlite3.Connection,
        gate_run_id: str,
        *,
        gate_id: str = "GATE-WP1",
        passed: int = 1,
        details: str = "{}",
    ) -> None:
        conn.execute(
            "INSERT INTO gates (gate_run_id, gate_id, passed, details, created_at) VALUES (?,?,?,?,?)",
            (gate_run_id, gate_id, passed, details, "2026-09-19T00:00:00Z"),
        )

    return _insert
