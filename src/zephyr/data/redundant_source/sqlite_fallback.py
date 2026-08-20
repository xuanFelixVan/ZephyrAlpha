# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""CH 降级到本地 SQLite——CH 不可达时写本地 SQLite，查询层可读最近数据。

设计：
- 按 table 创建 SQLite 表（schema 与 CH 对齐，仅保留核心列）
- write_rows: 批量写入 SQLite（INSERT OR REPLACE 幂等）
- query_recent: 查询最近 N 条记录（查询层降级读取）
- 自动清理：超过 max_rows 的旧数据自动删除（FIFO）
- 回灌接口：get_pending_batches 返回待回灌数据

Usage::

    fallback = SQLiteFallback(db_path="data/fallback.sqlite")
    fallback.write_rows("tick_data", columns, rows)
    recent = fallback.query_recent("tick_data", limit=100)
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path

from zephyr.shared.observability.metrics import get_registry

log = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "data/fallback.sqlite"
_DEFAULT_MAX_ROWS = 500_000  # 每表最大行数（约 4 小时 tick 数据）


class SQLiteFallback:
    """CH 降级写本地 SQLite。

    线程安全：所有 SQLite 操作通过 _lock 串行化（SQLite 单写者模型）。
    """

    def __init__(
        self,
        db_path: str = _DEFAULT_DB_PATH,
        max_rows_per_table: int = _DEFAULT_MAX_ROWS,
    ) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._max_rows = max_rows_per_table
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._registry = get_registry()

    def _get_conn(self) -> sqlite3.Connection:
        """获取 SQLite 连接（惰性初始化）。"""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        return self._conn

    def ensure_table(self, table: str, columns: list[str]) -> None:
        """确保 SQLite 表存在（如不存在则创建）。

        Args:
            table: 表名（如 tick_data，不含 c1_market. 前缀）
            columns: 列名列表
        """
        cols_def = ", ".join(f'"{c}" TEXT' for c in columns)
        sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({cols_def})'
        with self._lock:
            conn = self._get_conn()
            conn.execute(sql)
            conn.commit()

    def write_rows(
        self,
        table: str,
        columns: list[str],
        rows: list[tuple],
    ) -> int:
        """批量写入行到 SQLite。

        Args:
            table: 表名
            columns: 列名列表
            rows: 行数据（与 columns 对齐）

        Returns:
            成功写入的行数
        """
        if not rows:
            return 0
        self.ensure_table(table, columns)
        placeholders = ", ".join("?" * len(columns))
        cols_str = ", ".join(f'"{c}"' for c in columns)
        sql = f'INSERT OR REPLACE INTO "{table}" ({cols_str}) VALUES ({placeholders})'

        with self._lock:
            try:
                conn = self._get_conn()
                conn.executemany(sql, rows)
                conn.commit()
                self._registry.inc("zephyr_sqlite_fallback_written_total", n=len(rows))

                # 自动清理旧数据
                self._cleanup_if_needed(table)
                return len(rows)
            except Exception as e:  # noqa: BLE001
                log.error("SQLiteFallback 写入 %s 失败: %s", table, e)
                self._registry.inc("zephyr_sqlite_fallback_failed_total")
                return 0

    def query_recent(
        self,
        table: str,
        limit: int = 100,
    ) -> list[dict]:
        """查询最近的 N 条记录（查询层降级读取）。

        Args:
            table: 表名
            limit: 最大返回行数

        Returns:
            行列表（dict 形式，key=列名）
        """
        sql = f'SELECT * FROM "{table}" ORDER BY rowid DESC LIMIT ?'
        with self._lock:
            try:
                conn = self._get_conn()
                cursor = conn.execute(sql, (limit,))
                cols = [d[0] for d in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
            except Exception as e:  # noqa: BLE001
                log.error("SQLiteFallback 查询 %s 失败: %s", table, e)
                return []

    def get_pending_count(self, table: str) -> int:
        """获取待回灌的行数。"""
        with self._lock:
            try:
                conn = self._get_conn()
                cursor = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
                return cursor.fetchone()[0]
            except Exception:
                return 0

    def get_pending_batch(
        self,
        table: str,
        batch_size: int = 1000,
    ) -> tuple[list[str], list[tuple]]:
        """获取一批待回灌数据（用于 CH 恢复后回灌）。

        Returns:
            (columns, rows) — 列名列表 + 行数据
        """
        with self._lock:
            try:
                conn = self._get_conn()
                cursor = conn.execute(f'SELECT * FROM "{table}" ORDER BY rowid LIMIT ?', (batch_size,))  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
                cols = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
                return cols, rows
            except Exception as e:  # noqa: BLE001
                log.error("SQLiteFallback 获取批次 %s 失败: %s", table, e)
                return [], []

    def delete_batch(self, table: str, batch_size: int = 1000) -> int:
        """删除已回灌的批次（FIFO）。"""
        with self._lock:
            try:
                conn = self._get_conn()
                cursor = conn.execute(
                    f'DELETE FROM "{table}" WHERE rowid IN (SELECT rowid FROM "{table}" ORDER BY rowid LIMIT ?)',  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
                    (batch_size,),
                )
                conn.commit()
                return cursor.rowcount
            except Exception as e:  # noqa: BLE001
                log.error("SQLiteFallback 删除批次 %s 失败: %s", table, e)
                return 0

    def _cleanup_if_needed(self, table: str) -> None:
        """超过 max_rows 时清理旧数据（调用方已持锁）。"""
        try:
            conn = self._get_conn()
            cursor = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            if count > self._max_rows:
                excess = count - self._max_rows
                conn.execute(
                    f'DELETE FROM "{table}" WHERE rowid IN (SELECT rowid FROM "{table}" ORDER BY rowid LIMIT ?)',  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
                    (excess,),
                )
                conn.commit()
                log.info("SQLiteFallback 清理 %s 旧数据 %d 行", table, excess)
        except Exception as e:  # noqa: BLE001
            log.debug("SQLiteFallback 清理检查失败: %s", e)

    def close(self) -> None:
        """关闭 SQLite 连接（含 WAL checkpoint 确保文件句柄释放）。"""
        with self._lock:
            if self._conn:
                try:
                    self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    self._conn.close()
                except Exception as e:  # noqa: BLE001
                    log.debug("SQLiteFallback close 异常: %s", e)
                finally:
                    self._conn = None
