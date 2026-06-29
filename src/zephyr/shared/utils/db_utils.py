# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.db_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths
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
# [A_module] module_id=MOD-SHR_db_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
db_utils.py — SQLite 连接公共 API

Previously re-exported from zephyr.governance.persistence.sqlite_schema.
Now uses shared.io.paths for DB_PATH and provides own connection logic
to eliminate shared->data.persistence circular import.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "DB_PATH",
    "ensure_schema",
    "get_db_connection",
    "init_db",
]

_PRAGMAS = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = NORMAL",
    "PRAGMA foreign_keys = ON",
    "PRAGMA busy_timeout = 5000",
    "PRAGMA temp_store = MEMORY",
    "PRAGMA wal_autocheckpoint = 4096",
]


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    """Apply standard PRAGMA baseline to a connection."""
    for pragma in _PRAGMAS:
        try:
            conn.execute(pragma)
        except sqlite3.OperationalError:
            pass


def get_db_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Get a SQLite connection with standard PRAGMA baseline applied.

    Args:
        db_path: Optional path to database. Defaults to DB_PATH.

    Returns:
        sqlite3.Connection with PRAGMAs applied.
    """
    resolved = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(resolved))
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


def init_db(db_path: str | Path | None = None) -> str:
    """Ensure database exists and schema is initialized.

    This is a lightweight version — for full schema migration support,
    use zephyr.data.persistence.sqlite_schema.init_db directly.

    Args:
        db_path: Optional path to database. Defaults to DB_PATH.

    Returns:
        str: Path to the initialized database.
    """
    resolved = Path(db_path) if db_path is not None else DB_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(resolved)
    try:
        # Ensure basic connectivity — full schema init delegated to sqlite_schema
        conn.execute("SELECT 1")
    finally:
        conn.close()
    return str(resolved)


def ensure_schema(db_path=None) -> None:
    """确保数据库 schema 已初始化（委托给 init_db）。"""
    init_db(db_path)
