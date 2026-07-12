# [A_test] module_id: SRC-TST-1945 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-562 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_db_utils
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
=============================================
覆盖矩阵：
  db_utils.ensure_schema:
    - 委托给 init_db × 1
    - 幂等调用 × 1
  db_utils.get_db_connection:
    - 返回有效连接 × 1
    - PRAGMA 已应用 × 3
  db_utils.DB_PATH:
    - 类型正确 × 1
=============================================
"""

from pathlib import Path

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.utils.db_utils import ensure_schema, get_db_connection


class TestEnsureSchema:
    def test_ensure_schema_creates_tables(self, tmp_path: Path) -> None:
        db = tmp_path / "test_schema.db"
        ensure_schema(db)
        conn = sqlite3.connect(str(db))
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "tasks" in tables
        assert "events" in tables

    def test_ensure_schema_idempotent(self, tmp_path: Path) -> None:
        db = tmp_path / "test_schema.db"
        ensure_schema(db)
        ensure_schema(db)
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone()[0]
        conn.close()
        assert count == 1


class TestGetDbConnection:
    def test_returns_valid_connection(self, tmp_path: Path) -> None:
        db = tmp_path / "test_conn.db"
        ensure_schema(db)
        conn = get_db_connection(db)
        assert conn is not None
        conn.close()

    def test_wal_mode_enabled(self, tmp_path: Path) -> None:
        db = tmp_path / "test_pragma.db"
        ensure_schema(db)
        conn = get_db_connection(db)
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert journal_mode.lower() == "wal"

    def test_foreign_keys_enabled(self, tmp_path: Path) -> None:
        db = tmp_path / "test_fk.db"
        ensure_schema(db)
        conn = get_db_connection(db)
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        assert fk == 1

    def test_busy_timeout_set(self, tmp_path: Path) -> None:
        db = tmp_path / "test_busy.db"
        ensure_schema(db)
        conn = get_db_connection(db)
        timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        conn.close()
        assert timeout == 5000


from zephyr.shared.io.paths import DB_PATH
class TestDBPath:
    def test_db_path_is_path_instance(self) -> None:
        assert isinstance(DB_PATH, Path)


import sqlite3
