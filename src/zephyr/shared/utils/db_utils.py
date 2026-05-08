"""
db_utils.py — SQLite 连接工厂（AUDIT-07 P0-3: 消除 gates ↔ db 循环依赖）

从 db/sqlite_schema.py 提取的公共连接工具，供 gates/ 等上层模块使用，
避免 gates → db 的模块级 import 形成循环依赖。

真源声明：
  - DB_PATH 真源为 shared/paths.py
  - get_db_connection / _apply_pragmas 原始实现来自 db/sqlite_schema.py
  - sqlite_schema.py 现从本文件导入这两个函数，禁止重复定义
"""
from __future__ import annotations


import sqlite3
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "DB_PATH",
    "get_db_connection",
    "ensure_schema",
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
    for pragma in _PRAGMAS:
        conn.execute(pragma)


def get_db_connection(
    db_path: Path | str | None = None,
    *,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    resolved: Path = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(
        str(resolved),
        isolation_level=None,
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


def ensure_schema(db_path: Path | str | None = None) -> None:
    """确保数据库 schema 已初始化（委托给 sqlite_schema.init_db）。"""
    from zephyr.db.sqlite_schema import init_db

    init_db(db_path)
