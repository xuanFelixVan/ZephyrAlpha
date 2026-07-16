# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.progress_store
# [DOMAIN] D_DATA
# [DEPENDENCIES] sqlite3(标准库); zephyr.shared.io.paths(REPO_ROOT)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] SQLite 单文件存储(data/integrator_progress.db); task_progress 主键 task_id; task_runs 自增 run_id; WAL 模式支持并发读; check_same_thread=False + threading.Lock 保护写
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有方法返回 dict/list/None，不抛异常（sqlite3.Error -> log + return None/[]）
# [TESTS] tests/zephyr/data/test_progress_store.py
# [A_module] module_id=MOD-L00-004-progress_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "APScheduler"仅出现在L29注释中(解释check_same_thread=False因APScheduler线程池共用),本文件无任何调度逻辑,是纯SQLite进度存储
"""统一进度存储（MOD-L00-004 §7）。

取代 13 个 per-script JSON 文件（tmp/_ds_progress/fill_*.json），提供：
- task_progress 表：每个任务的最新状态（last_key/last_status/rows_total）
- task_runs 表：每次运行的详细记录（started_at/finished_at/rows_fetched/error_msg）

断点续传协议（§7.2）：
1. 任务启动 -> get_last_key(task_id) -> 作为本次 payload.start
2. 分批拉取 -> 每批写完 CH -> save_progress 更新 last_key
3. 异常中断 -> 下次启动从 last_key 继续

线程安全：
- SQLite 连接用 check_same_thread=False（APScheduler 线程池共用）
- 写操作用 threading.Lock 串行化（SQLite WAL 模式下读不阻塞）
- 每次操作创建新 cursor，用完即关（连接复用）
"""
from __future__ import annotations

import datetime
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

# 默认数据库路径（相对 REPO_ROOT）
_DEFAULT_DB_PATH = REPO_ROOT / "data" / "integrator_progress.db"


class ProgressStore:
    """统一进度存储（SQLite）。

    线程安全：check_same_thread=False + threading.Lock 保护写操作。
    幂等：save_progress 是 UPSERT，start_run 每次插入新行。
    """

    def __init__(self, db_path: str | Path | None = None):
        """初始化进度存储。

        Args:
            db_path: SQLite 文件路径。None 用默认 data/integrator_progress.db。
        """
        self._db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(
            str(self._db_path),
            check_same_thread=False,
            isolation_level=None,  # autocommit 模式，每个语句自动提交
        )
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """建表（IF NOT EXISTS）。启用 WAL 模式提升并发读性能。"""
        try:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_progress (
                    task_id        TEXT NOT NULL,
                    source         TEXT NOT NULL,
                    last_run_at    TIMESTAMP,
                    last_key       TEXT,
                    last_status    TEXT,
                    rows_total     INTEGER,
                    error_msg      TEXT,
                    PRIMARY KEY (task_id)
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_runs (
                    run_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id        TEXT NOT NULL,
                    started_at     TIMESTAMP NOT NULL,
                    finished_at    TIMESTAMP,
                    status         TEXT,
                    rows_fetched   INTEGER,
                    rows_written   INTEGER,
                    error_msg      TEXT
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_task_runs_started_at ON task_runs(started_at)"
            )
        except sqlite3.Error as e:
            log.error("ProgressStore._init_db 失败: %s", e)
            raise

    # ============== 断点续传 ==============

    def get_last_key(self, task_id: str) -> str | None:
        """查断点续传键（如最大日期 "2026-07-05"）。

        Returns:
            last_key 字符串，或 None（任务从未运行过）。
        """
        try:
            cur = self._conn.execute(
                "SELECT last_key FROM task_progress WHERE task_id=?", (task_id,)
            )
            row = cur.fetchone()
            cur.close()
            return row["last_key"] if row else None
        except sqlite3.Error as e:
            log.error("get_last_key(%s) 失败: %s", task_id, e)
            return None

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """查任务最新状态。"""
        try:
            cur = self._conn.execute(
                "SELECT * FROM task_progress WHERE task_id=?", (task_id,)
            )
            row = cur.fetchone()
            cur.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            log.error("get_task_status(%s) 失败: %s", task_id, e)
            return None

    # ============== 写入进度 ==============

    def save_progress(
        self,
        task_id: str,
        source: str,
        last_key: str,
        status: str,
        rows_total: int = 0,
        error_msg: str | None = None,
    ) -> bool:
        """UPSERT task_progress（更新或插入任务最新状态）。

        Args:
            task_id: 任务标识（如 "kline_daily_incremental"）
            source: 数据源（如 "ifind"）
            last_key: 断点续传键（如 "2026-07-05"）
            status: "SUCCESS" / "FAILED" / "RUNNING"
            rows_total: 累计拉取行数
            error_msg: 错误信息（成功时为 None）

        Returns:
            是否成功。
        """
        now = now_utc().isoformat(timespec="seconds")
        with self._lock:
            try:
                self._conn.execute(
                    """
                    INSERT INTO task_progress
                        (task_id, source, last_run_at, last_key, last_status, rows_total, error_msg)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(task_id) DO UPDATE SET
                        source=excluded.source,
                        last_run_at=excluded.last_run_at,
                        last_key=excluded.last_key,
                        last_status=excluded.last_status,
                        rows_total=excluded.rows_total,
                        error_msg=excluded.error_msg
                    """,
                    (task_id, source, now, last_key, status, rows_total, error_msg),
                )
                return True
            except sqlite3.Error as e:
                log.error("save_progress(%s) 失败: %s", task_id, e)
                return False

    # ============== 运行记录 ==============

    def start_run(self, task_id: str) -> int | None:
        """记录一次运行开始，返回 run_id。"""
        now = now_utc().isoformat(timespec="seconds")
        with self._lock:
            try:
                cur = self._conn.execute(
                    "INSERT INTO task_runs (task_id, started_at, status) VALUES (?, ?, 'RUNNING')",
                    (task_id, now),
                )
                run_id = cur.lastrowid
                cur.close()
                return run_id
            except sqlite3.Error as e:
                log.error("start_run(%s) 失败: %s", task_id, e)
                return None

    def finish_run(
        self,
        run_id: int,
        status: str,
        rows_fetched: int = 0,
        rows_written: int = 0,
        error_msg: str | None = None,
    ) -> bool:
        """记录一次运行结束。"""
        now = now_utc().isoformat(timespec="seconds")
        with self._lock:
            try:
                self._conn.execute(
                    """
                    UPDATE task_runs SET
                        finished_at=?, status=?, rows_fetched=?, rows_written=?, error_msg=?
                    WHERE run_id=?
                    """,
                    (now, status, rows_fetched, rows_written, error_msg, run_id),
                )
                return True
            except sqlite3.Error as e:
                log.error("finish_run(%s) 失败: %s", run_id, e)
                return False

    # ============== 查询 ==============

    def list_recent_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """查最近 N 条运行记录。"""
        try:
            cur = self._conn.execute(
                "SELECT * FROM task_runs ORDER BY started_at DESC LIMIT ?", (limit,)
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            return rows
        except sqlite3.Error as e:
            log.error("list_recent_runs 失败: %s", e)
            return []

    def list_failed_tasks(self) -> list[dict[str, Any]]:
        """查所有失败任务（last_status=FAILED）。"""
        try:
            cur = self._conn.execute(
                "SELECT * FROM task_progress WHERE last_status='FAILED' ORDER BY last_run_at DESC"
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            return rows
        except sqlite3.Error as e:
            log.error("list_failed_tasks 失败: %s", e)
            return []

    def list_tasks_by_source(self, source: str) -> list[dict[str, Any]]:
        """按数据源查所有任务。"""
        try:
            cur = self._conn.execute(
                "SELECT * FROM task_progress WHERE source=? ORDER BY task_id", (source,)
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            return rows
        except sqlite3.Error as e:
            log.error("list_tasks_by_source(%s) 失败: %s", source, e)
            return []

    def list_all_tasks(self) -> list[dict[str, Any]]:
        """查所有任务状态。"""
        try:
            cur = self._conn.execute(
                "SELECT * FROM task_progress ORDER BY source, task_id"
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            return rows
        except sqlite3.Error as e:
            log.error("list_all_tasks 失败: %s", e)
            return []

    def close(self) -> None:
        """关闭连接。"""
        with self._lock:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass


# ============== 模块级单例（懒初始化） ==============

_singleton: ProgressStore | None = None
_singleton_lock = threading.Lock()


def get_store(db_path: str | Path | None = None) -> ProgressStore:
    """获取模块级单例 ProgressStore。

    首次调用创建实例，后续调用返回同一实例。
    测试时传 db_path 用临时库；生产用默认路径。
    """
    global _singleton
    if _singleton is None or db_path is not None:
        with _singleton_lock:
            if _singleton is None or db_path is not None:
                _singleton = ProgressStore(db_path)
    return _singleton
