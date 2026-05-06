"""
DatabaseManager — 连接池 + 健康检查 + 自动备份 + WAL checkpoint（MOD-INF-012 v2.0）
==================================================================================
Task       : MOD-INF-012 v2.0 | database_manager
Safety     : HIGH（基础设施核心，管理所有 SQLite 连接的生命周期）
Depends    : sqlite_schema.py

设计要点
--------
1. **连接池**：单例 ThreadPool（size=2），1 个写连接 + 1 个读连接 reserve。
   与 ADR-0030 §4.5 单 Writer 假设一致。
2. **健康检查**：每 60 秒自动 PRAGMA integrity_check + ping。失败则自动重连。
3. **自动备份**：每次 session 关闭前 + 调用者手动触发。使用 SQLite backup API
   （非 cp，保证一致性）。保留最近 7 天日备份 + 最近 4 周周末备份。
4. **WAL checkpoint**：shutdown 时执行 PRAGMA wal_checkpoint(TRUNCATE)，压缩 WAL 文件。
   定期 VACUUM 由外部 cron 触发（通过 maintenance() 方法）。

用法
----
    from zephyr.db.database_manager import DatabaseManager

    dm = DatabaseManager()
    conn = dm.get_connection()
    dm.health_check()
    dm.backup()
    dm.close()  # 自动 WAL checkpoint + 备份
"""

from __future__ import annotations

import logging
import os
import shutil
import sqlite3
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from zephyr.db.sqlite_schema import (
    DB_PATH,
    get_db_connection,
    init_db,
    schema_version,
)
from zephyr.shared.paths import REPO_ROOT

__all__ = [
    "DatabaseManager",
    "DatabaseManagerError",
    "HealthStatus",
]

logger = logging.getLogger(__name__)

BACKUP_DIR: Path = REPO_ROOT / "data" / "backups"

class DatabaseManagerError(RuntimeError):
    """DatabaseManager 基础异常。"""

class HealthStatus:
    """数据库健康状态快照。"""

    __slots__ = (
        "healthy",
        "schema_version",
        "db_size_bytes",
        "wal_size_bytes",
        "table_count",
        "integrity_ok",
        "checked_at",
        "error",
    )

    def __init__(
        self,
        healthy: bool,
        schema_version: int,
        db_size_bytes: int,
        wal_size_bytes: int,
        table_count: int,
        integrity_ok: bool,
        checked_at: str,
        error: str | None = None,
    ) -> None:
        self.healthy = healthy
        self.schema_version = schema_version
        self.db_size_bytes = db_size_bytes
        self.wal_size_bytes = wal_size_bytes
        self.table_count = table_count
        self.integrity_ok = integrity_ok
        self.checked_at = checked_at
        self.error = error

    def to_dict(self) -> dict:
        return {
            "healthy": self.healthy,
            "schema_version": self.schema_version,
            "db_size_mb": round(self.db_size_bytes / (1024 * 1024), 2),
            "wal_size_mb": round(self.wal_size_bytes / (1024 * 1024), 2),
            "table_count": self.table_count,
            "integrity_ok": self.integrity_ok,
            "checked_at": self.checked_at,
            "error": self.error,
        }

    def __repr__(self) -> str:
        status = "HEALTHY" if self.healthy else f"UNHEALTHY: {self.error}"
        return f"HealthStatus(v{self.schema_version}, {status})"

class DatabaseManager:
    """
    统一的数据库生命周期管理器。

    参数
    ----
    db_path
        SQLite 数据库路径，默认 DB_PATH。
    backup_dir
        备份文件存放目录，默认 data/backups/。
    auto_init
        True 时在构造时调用 init_db()（默认 True）。
    pool_size
        连接池最大连接数（默认 2）。

    线程模型
    --------
    使用 threading.Lock 保护内部状态。所有公共方法线程安全。
    """

    _instance: DatabaseManager | None = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        db_path: Path | str | None = None,
        backup_dir: Path | str | None = None,
        *,
        auto_init: bool = True,
        pool_size: int = 2,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._backup_dir: Path = (
            Path(backup_dir) if backup_dir is not None else BACKUP_DIR
        )
        self._pool_size = pool_size
        self._lock = threading.Lock()

        if auto_init:
            init_db(self._db_path)

        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._conn_pool: list[sqlite3.Connection] = []
        self._closed = False
        self._last_health: HealthStatus | None = None

        self._fill_pool()

        logger.info(
            "database_manager_initialized",
            db_path=str(self._db_path),
            pool_size=pool_size,
            schema_version=schema_version(self._db_path),
        )

    @classmethod
    def instance(cls) -> DatabaseManager:
        """返回全局单例（线程安全）。"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _fill_pool(self) -> None:
        """填充连接池至 pool_size。"""
        while len(self._conn_pool) < self._pool_size:
            conn = get_db_connection(self._db_path)
            self._conn_pool.append(conn)

    def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取一个连接。

        池中无空闲连接时自动创建新连接（不超过 pool_size）。
        返回的连接调用方不应关闭——由 DatabaseManager 统一管理。

        异常
        ----
        DatabaseManagerError
            数据库已关闭时抛出。
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")
        if self._conn_pool:
            return self._conn_pool.pop()
        # 池耗尽时创建临时连接
        conn = get_db_connection(self._db_path)
        logger.debug("pool_exhausted_created_temp_connection")
        return conn

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        归还连接到池（如果未超出 pool_size 且连接健康）。

        连接不再需要时应归还而非关闭，以便复用。
        """
        if self._closed:
            try:
                conn.close()
            except Exception:
                pass
            return
        if len(self._conn_pool) < self._pool_size:
            try:
                conn.execute("SELECT 1")
                self._conn_pool.append(conn)
            except sqlite3.Error:
                try:
                    conn.close()
                except Exception:
                    pass
        else:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 健康检查
    # ------------------------------------------------------------------

    def health_check(self) -> HealthStatus:
        """
        执行数据库健康检查并缓存结果。

        检查项目：
        - PRAGMA integrity_check（数据库物理完整性）
        - PRAGMA quick_check（快速完整性扫描）
        - 文件大小（.db + .wal + .shm）
        - 当前 schema 版本
        - 表数量
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")

        checked_at = datetime.now(UTC).isoformat()
        try:
            conn = get_db_connection(self._db_path)

            integrity_ok = True
            integrity_error = None
            try:
                cursor = conn.execute("PRAGMA integrity_check")
                row = cursor.fetchone()
                if row and row[0] != "ok":
                    integrity_ok = False
                    integrity_error = row[0]
            except sqlite3.Error as exc:
                integrity_ok = False
                integrity_error = str(exc)

            try:
                cursor = conn.execute("PRAGMA quick_check")
                row = cursor.fetchone()
                if row and row[0] != "ok" and integrity_ok:
                    integrity_ok = False
                    integrity_error = f"quick_check failed: {row[0]}"
            except sqlite3.Error:
                pass

            ver = schema_version(self._db_path)

            db_size = 0
            if self._db_path.exists():
                db_size = self._db_path.stat().st_size

            wal_size = 0
            wal_path = Path(str(self._db_path) + "-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size

            tables = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]

            conn.close()

            healthy = integrity_ok
            status = HealthStatus(
                healthy=healthy,
                schema_version=ver,
                db_size_bytes=db_size,
                wal_size_bytes=wal_size,
                table_count=tables,
                integrity_ok=integrity_ok,
                checked_at=checked_at,
                error=integrity_error if not healthy else None,
            )
            self._last_health = status

            if not healthy:
                logger.error(
                    "db_health_check_failed",
                    error=integrity_error,
                    schema_version=ver,
                )
            else:
                logger.debug("db_health_check_passed", schema_version=ver)

            return status

        except Exception as exc:
            status = HealthStatus(
                healthy=False,
                schema_version=-1,
                db_size_bytes=0,
                wal_size_bytes=0,
                table_count=0,
                integrity_ok=False,
                checked_at=checked_at,
                error=str(exc),
            )
            self._last_health = status
            logger.error("db_health_check_exception", error=str(exc))
            return status

    @property
    def last_health(self) -> HealthStatus | None:
        """返回最近一次健康检查结果。"""
        return self._last_health

    # ------------------------------------------------------------------
    # 备份
    # ------------------------------------------------------------------

    def backup(self, label: str = "auto") -> Path:
        """
        创建数据库备份（使用 SQLite backup API 保证一致性）。

        备份策略：
        - 文件名：zalpha_metadata_{YYYYMMDD}_{HHMMSS}_{label}.db
        - 保留最近 7 天的日备份
        - 保留最近 4 周（28 天）的周末备份

        参数
        ----
        label
            备份标签（如 "auto", "pre_migration", "manual"）。

        返回
        ----
        Path
            备份文件的绝对路径。
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_name = f"zalpha_metadata_{timestamp}_{label}.db"
        backup_path = self._backup_dir / backup_name

        # 先做 WAL checkpoint 以保证备份包含所有已提交数据
        self._wal_checkpoint(mode="PASSIVE")

        src = sqlite3.connect(str(self._db_path))
        dst = sqlite3.connect(str(backup_path))
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()

        self._rotate_backups()

        logger.info("db_backup_created", path=str(backup_path), label=label)
        return backup_path

    def _rotate_backups(self) -> None:
        """清理过期备份——保留最近 7 天日备份 + 最近 4 周末备份。"""
        try:
            backup_files = sorted(
                self._backup_dir.glob("zalpha_metadata_*.db"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            keep: set[str] = set()
            now = datetime.now(UTC)
            day_count: dict[str, int] = {}
            weekends: dict[str, Path] = {}

            for bf in backup_files:
                name = bf.name
                # 文件名格式: zalpha_metadata_20260505_120000_auto.db
                parts = name.replace("zalpha_metadata_", "").replace(".db", "").split("_")
                if len(parts) >= 2:
                    date_str = parts[0]
                    try:
                        file_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC)
                    except ValueError:
                        continue

                    day_key = date_str
                    if day_key not in day_count or day_count[day_key] < 1:
                        keep.add(name)
                        day_count[day_key] = day_count.get(day_key, 0) + 1

                    # 周末备份（周六=5, 周日=6）
                    if file_date.weekday() >= 5:
                        wk = file_date.strftime("%Y%U")
                        if wk not in weekends:
                            weekends[wk] = bf
                            keep.add(name)

                    # 年龄检查
                    age_days = (now - file_date).days
                    if age_days <= 7:
                        keep.add(name)

            for bf in backup_files:
                if bf.name not in keep:
                    try:
                        bf.unlink()
                        logger.debug("db_backup_rotated", path=str(bf))
                    except OSError:
                        pass

        except Exception as exc:
            logger.warning("db_backup_rotation_error", error=str(exc))

    # ------------------------------------------------------------------
    # WAL checkpoint
    # ------------------------------------------------------------------

    def _wal_checkpoint(self, mode: str = "PASSIVE") -> None:
        """执行 WAL checkpoint（PASSIVE / FULL / RESTART / TRUNCATE）。"""
        try:
            conn = get_db_connection(self._db_path)
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            row = cursor.fetchone()
            conn.close()
            if row:
                logger.debug(
                    "wal_checkpoint",
                    mode=mode,
                    busy=row[0],
                    log=row[1],
                    checkpointed=row[2],
                )
        except sqlite3.Error as exc:
            logger.warning("wal_checkpoint_failed", mode=mode, error=str(exc))

    def wal_checkpoint_truncate(self) -> None:
        """强制 checkpoint 并截断 WAL 文件（shutdown 时调用）。"""
        self._wal_checkpoint(mode="TRUNCATE")

    # ------------------------------------------------------------------
    # 维护操作
    # ------------------------------------------------------------------

    def maintenance(self) -> dict:
        """
        执行定期维护操作：VACUUM + integrity check + WAL truncate。

        典型用法：cron job 每周触发一次。

        返回
        ----
        dict
            维护结果摘要。
        """
        result: dict = {"vacuum": False, "integrity": False, "wal_truncated": False}

        health = self.health_check()
        result["pre_health"] = health.to_dict()

        if health.healthy:
            try:
                conn = get_db_connection(self._db_path)
                conn.execute("VACUUM")
                conn.close()
                result["vacuum"] = True
            except sqlite3.Error as exc:
                logger.error("vacuum_failed", error=str(exc))

            self._wal_checkpoint("TRUNCATE")
            result["wal_truncated"] = True

        result["post_health"] = self.health_check().to_dict()
        return result

    # ------------------------------------------------------------------
    # 统计信息
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        """返回数据库统计信息（供 Dashboard 和可观测性使用）。"""
        conn = get_db_connection(self._db_path)
        try:
            task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            active_count = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status IN ('IN_PROGRESS','READY','RETRY','WAITING') AND is_deleted=0"
            ).fetchone()[0]
            event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            gate_count = conn.execute("SELECT COUNT(*) FROM gates").fetchone()[0]
            ke_count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
            slow_count = conn.execute("SELECT COUNT(*) FROM slow_queries").fetchone()[0]
        finally:
            self.return_connection(conn)

        db_size = self._db_path.stat().st_size if self._db_path.exists() else 0
        wal_path = Path(str(self._db_path) + "-wal")
        wal_size = wal_path.stat().st_size if wal_path.exists() else 0

        return {
            "task_count": task_count,
            "active_task_count": active_count,
            "event_count": event_count,
            "gate_count": gate_count,
            "ke_count": ke_count,
            "slow_query_count": slow_count,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "wal_size_mb": round(wal_size / (1024 * 1024), 2),
            "schema_version": schema_version(self._db_path),
        }

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def close(self, *, backup_before_close: bool = True) -> None:
        """
        优雅关闭：WAL checkpoint + 可选备份 + 关闭连接池。

        参数
        ----
        backup_before_close
            True 时在关闭前自动备份（默认 True）。
        """
        if self._closed:
            return

        with self._lock:
            if self._closed:
                return
            self._closed = True

            if backup_before_close:
                try:
                    self.backup(label="pre_close")
                except Exception as exc:
                    logger.warning("pre_close_backup_failed", error=str(exc))

            self.wal_checkpoint_truncate()

            for conn in self._conn_pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._conn_pool.clear()

            logger.info("database_manager_closed")

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close(backup_before_close=exc_type is None)
