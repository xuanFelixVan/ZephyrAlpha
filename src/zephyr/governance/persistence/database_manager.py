# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.database_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.shared.io.paths; zephyr.gov_audit.audit_schema; zephyr.governance.observability_governance.query_metrics
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT-database_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "cron"在注释中，非实际cron调用

"""
DatabaseManager — 连接池 + 健康检查 + 自动备份 + WAL checkpoint（SH-DB-001 v2.0）
==================================================================================
Task       : SH-DB-001 v2.0 | database_manager
Safety     : HIGH（基础设施核心，管理所有 SQLite 连接的生命周期）
Depends    : sqlite_schema.py

设计要点
--------
1. **连接池**：单例 ThreadPool（size=2），1 个写连接 + 1 个读连接 reserve。
   与  §4.5 单 Writer 假设一致。
2. **健康检查**：每 60 秒自动 PRAGMA integrity_check + ping。失败则自动重连。
3. **自动备份**：每次 session 关闭前 + 调用者手动触发。使用 SQLite backup API
   （非 cp，保证一致性）。保留最近 7 天日备份 + 最近 4 周周末备份。
4. **WAL checkpoint**：shutdown 时执行 PRAGMA wal_checkpoint(TRUNCATE)，压缩 WAL 文件。
   定期 VACUUM 由外部 cron 触发（通过 maintenance() 方法）。

用法
----
    from zephyr.governance.database_manager import DatabaseManager

    dm = DatabaseManager()
    conn = dm.get_connection()
    dm.health_check()
    dm.backup()
    dm.close()  # 自动 WAL checkpoint + 备份
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from zephyr.governance.persistence.sqlite_schema import (
    get_db_connection,
    init_db,
    schema_version,
)
from zephyr.shared.foundation.errors import PoolExhaustedError
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.utils.time_utils import now_iso

__all__ = [
    "DatabaseHealthStatus",
    "DatabaseManager",
    "DatabaseManagerError",
    "PoolExhaustedError",
]

logger = logging.getLogger(__name__)

BACKUP_DIR: Final[Path] = REPO_ROOT / "data" / "backups"

# 5.66.6 修复：表名白名单，防止 f-string 拼接表名的 SQL 注入风险。
# verify_backup() 遍历 governance.db 的 sqlite_master 表名，白名单覆盖全部已知表名。
_ALLOWED_TABLES = frozenset(
    {
        "tasks",
        "events",
        "gate_runs",
        "circuit_breaker_state",
        "task_files",
        "_schema_version",
        "slow_queries",
        "tx_idempotency",
        "task_events",
        "task_snapshots",
        "fle_metrics",
        "fle_alerts",
        "fle_dispatch_log",
        "task_reviews",
        "f5_state",
    }
)

# 5.61.3 修复：retry_dlq retry_count 更新 SQL 集中化
# （NO-BARE-SQL gate 合规，常量名匹配 ^_?SQL_\w+$ 豁免正则）
SQL_UPDATE_EVENTS_RETRY_COUNT = "UPDATE events SET payload = ? WHERE event_id = ?"


def _validate_table_name(table: str) -> str:
    """5.66.6 修复：白名单校验表名，仅允许已知表名用于 SQL 拼接。"""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"table name not in whitelist: {table!r}")
    return table


def _check_db_integrity(conn):
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

    return integrity_ok, integrity_error


class DatabaseManagerError(RuntimeError):
    """DatabaseManager 基础异常。"""
    error_code = "ZA-GV-0029"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class DatabaseHealthStatus:
    """数据库健康状态快照。"""

    __slots__ = (
        "checked_at",
        "db_size_bytes",
        "error",
        "healthy",
        "integrity_ok",
        "schema_version",
        "table_count",
        "wal_size_bytes",
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
        # 5.110.7 修复: 原返回人类可读状态摘要(语义应为__str__), 改为可重建的 field=value 格式
        return (
            f"DatabaseHealthStatus(healthy={self.healthy!r}, "
            f"schema_version={self.schema_version!r}, error={self.error!r})"
        )


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
    max_overflow
        池耗尽时允许额外创建的临时连接上限（默认 10，5.61.5/5.64.4）。
    pool_timeout
        池+overflow 全部耗尽时阻塞等待的秒数，超时抛 PoolExhaustedError（默认 30s）。
    pool_recycle
        连接最大存活秒数，超龄连接在借出/归还时关闭重建（默认 3600s，5.64.3）。

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
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: float = 3600.0,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._backup_dir: Path = Path(backup_dir) if backup_dir is not None else BACKUP_DIR
        self._pool_size = pool_size
        # 5.61.5/5.64.3/5.64.4 修复：连接池上限与回收参数
        self._max_overflow = max_overflow
        self._pool_timeout = pool_timeout
        self._pool_recycle = pool_recycle
        self._lock = threading.Lock()
        # 5.64.4 修复：池耗尽时阻塞等待的条件变量（与 5.61.5 复用同一把锁）
        self._pool_cond = threading.Condition(self._lock)
        self._overflow_out = 0  # 当前已借出的 overflow 临时连接数
        # 5.64.3 修复：连接元数据侧表（sqlite3.Connection 不支持自定义属性，
        # 这是原 _last_used_at 从未设置、泄漏检测失效的根因）。
        # 键为 id(conn)，值含 created_at/last_used_at/overflow。
        self._conn_meta: dict[int, dict[str, float | bool]] = {}

        if auto_init:
            init_db(self._db_path)

        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._conn_pool: list[sqlite3.Connection] = []
        self._closed = False
        self._last_health: DatabaseHealthStatus | None = None

        self._fill_pool()

        logger.info(
            "database_manager_initialized",
            db_path=str(self._db_path),
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
            schema_version=schema_version(self._db_path),
        )

    @property
    def backup_dir(self) -> Path:
        """只读：backup_dir（Stage 4 公共化）。"""
        return self._backup_dir

    @backup_dir.setter
    def backup_dir(self, value):
        """写入：backup_dir（Stage 4 公共化）。"""
        self._backup_dir = value


    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def closed(self):
        """只读：closed（Stage 4 公共化）。"""
        return self._closed

    @closed.setter
    def closed(self, value):
        """写入：closed（Stage 4 公共化）。"""
        self._closed = value


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
        with self._lock:
            while len(self._conn_pool) < self._pool_size:
                conn = get_db_connection(self._db_path)
                self._touch_conn(conn, created=True)
                self._conn_pool.append(conn)

    # ------------------------------------------------------------------
    # 连接元数据（5.61.5/5.64.3/5.64.4）
    # ------------------------------------------------------------------

    def _touch_conn(self, conn: sqlite3.Connection, *, created: bool = False) -> None:
        """更新连接元数据（last_used_at；created=True 时同时记录创建时间）。

        调用方须持有 self._lock。sqlite3.Connection 不支持自定义属性，
        元数据存于侧表 self._conn_meta[id(conn)]。
        """
        now = time.time()
        meta = self._conn_meta.get(id(conn))
        if meta is None:
            meta = {"created_at": now, "last_used_at": now, "overflow": False}
            self._conn_meta[id(conn)] = meta
        if created:
            meta["created_at"] = now
        meta["last_used_at"] = now

    def _is_stale(self, conn: sqlite3.Connection) -> bool:
        """连接是否超过 pool_recycle 秒（调用方须持有 self._lock）。"""
        meta = self._conn_meta.get(id(conn))
        if meta is None:
            return False
        return (time.time() - float(meta["created_at"])) > self._pool_recycle

    def _is_overflow(self, conn: sqlite3.Connection) -> bool:
        """连接是否为 overflow 临时连接（调用方须持有 self._lock）。"""
        meta = self._conn_meta.get(id(conn))
        return bool(meta is not None and meta["overflow"])

    def _close_conn_quietly(self, conn: sqlite3.Connection) -> None:
        """关闭连接并清理元数据；异常降级为日志（5.64.5 同款异常隔离语义）。"""
        try:
            conn.close()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("suppressed error in database_manager", exc_info=True)
        with self._lock:
            self._conn_meta.pop(id(conn), None)

    def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取一个连接。

        5.61.5/5.64.3/5.64.4 修复：
        - 池空闲连接耗尽时，最多额外创建 max_overflow 个 overflow 临时连接（默认 10）；
        - overflow 也耗尽时在条件变量上阻塞等待（pool_timeout 秒，默认 30s），
          超时仍无可用连接抛 PoolExhaustedError；
        - 超过 pool_recycle 秒（默认 3600s）的陈旧连接借出时关闭重建。

        返回的连接调用方不应关闭——用 return_connection() 归还。

        异常
        ----
        DatabaseManagerError
            数据库已关闭时抛出。
        PoolExhaustedError
            池与 overflow 全部借出且等待超时。
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")
        deadline = time.monotonic() + self._pool_timeout
        result: sqlite3.Connection | None = None
        overflow_granted = False
        stale: list[sqlite3.Connection] = []
        with self._pool_cond:
            # 条件变量阻塞等待（事件驱动唤醒，非轮询——return_connection 归还时 notify）
            while result is None and not overflow_granted:
                # 池内取连接（顺带回收过期连接，锁外关闭）
                while self._conn_pool:
                    conn = self._conn_pool.pop()
                    if self._is_stale(conn):
                        stale.append(conn)
                        continue
                    result = conn
                    break
                if result is not None:
                    self._touch_conn(result)
                    break
                if self._closed:
                    raise DatabaseManagerError("DatabaseManager is closed")
                if self._overflow_out < self._max_overflow:
                    self._overflow_out += 1
                    overflow_granted = True
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise PoolExhaustedError(
                        f"连接池耗尽: pool_size={self._pool_size} + max_overflow={self._max_overflow} "
                        f"全部借出, 等待 {self._pool_timeout}s 超时",
                        details={
                            "pool_size": self._pool_size,
                            "max_overflow": self._max_overflow,
                            "pool_timeout": self._pool_timeout,
                        },
                    )
                self._pool_cond.wait(remaining)
        for conn in stale:
            self._close_conn_quietly(conn)
        if result is not None:
            return result
        # overflow_granted：锁外创建临时连接，避免长时间持锁
        try:
            conn = get_db_connection(self._db_path)
        except Exception:
            with self._pool_cond:
                self._overflow_out -= 1
                self._pool_cond.notify()
            raise
        with self._lock:
            self._touch_conn(conn, created=True)
            self._conn_meta[id(conn)]["overflow"] = True
        logger.debug("pool_exhausted_created_overflow_connection")
        return conn

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        归还连接到池（如果未超出 pool_size 且连接健康且未超 pool_recycle 年龄）。

        连接不再需要时应归还而非关闭，以便复用。

        5.61.5/5.64.3/5.64.4 修复：
        - 归还时更新 last_used_at（泄漏检测据此工作）；
        - overflow 临时连接归还时释放 overflow 配额并唤醒等待者；
        - 超龄（>pool_recycle 秒）或不健康的连接关闭而非入池。
        """
        if conn is None:
            return
        close_it = False
        with self._pool_cond:
            self._touch_conn(conn)
            if self._is_overflow(conn):
                self._overflow_out -= 1
                self._conn_meta[id(conn)]["overflow"] = False
            if self._closed:
                close_it = True
            elif self._is_stale(conn):
                close_it = True  # 5.64.3：超龄连接回收
            elif len(self._conn_pool) < self._pool_size:
                try:
                    conn.execute("SELECT 1")
                    self._conn_pool.append(conn)
                except sqlite3.Error:
                    close_it = True  # 连接不健康
            else:
                close_it = True  # 池满
            # 池有新连接或 overflow 配额释放，唤醒一个等待者
            self._pool_cond.notify()
        if close_it:
            self._close_conn_quietly(conn)

    # ------------------------------------------------------------------
    # 健康检查
    # ------------------------------------------------------------------

    def health_check(self) -> DatabaseHealthStatus:
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
        conn = None
        try:
            conn = get_db_connection(self._db_path)

            integrity_ok, integrity_error = _check_db_integrity(conn)

            ver = schema_version(self._db_path)

            db_size = 0
            if self._db_path.exists():
                db_size = self._db_path.stat().st_size

            wal_size = 0
            wal_path = Path(str(self._db_path) + "-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size

            tables = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]

            conn.close()
            conn = None

            healthy = integrity_ok
            status = DatabaseHealthStatus(
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

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            status = DatabaseHealthStatus(
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
        finally:
            # 5.61.4 修复：异常路径确保连接归还
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("suppressed error in database_manager", exc_info=True)

    @property
    def last_health(self) -> DatabaseHealthStatus | None:
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

        src = get_db_connection(str(self._db_path))
        dst = get_db_connection(str(backup_path))
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

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("db_backup_rotation_error: %s", exc, exc_info=True)

    # ------------------------------------------------------------------
    # WAL checkpoint
    # ------------------------------------------------------------------

    def _wal_checkpoint(self, mode: str = "PASSIVE") -> None:
        """执行 WAL checkpoint（PASSIVE / FULL / RESTART / TRUNCATE）。"""
        # 5.176 修复：mode 枚举白名单校验，防 PRAGMA 参数注入
        _VALID_MODES = frozenset({"PASSIVE", "FULL", "RESTART", "TRUNCATE"})
        if mode not in _VALID_MODES:
            raise ValueError(f"非法 wal_checkpoint mode: {mode!r}（仅允许 {sorted(_VALID_MODES)}）")
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            row = cursor.fetchone()
            conn.close()
            conn = None
            if row:
                logger.debug(
                    "wal_checkpoint",
                    mode=mode,
                    busy=row[0],
                    log=row[1],
                    checkpointed=row[2],
                )
        except sqlite3.Error as exc:
            logger.warning("wal_checkpoint_failed: mode=%s error=%s", mode, exc)
        finally:
            # 5.61.4 修复：异常路径确保连接归还
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("suppressed error in database_manager", exc_info=True)

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
            conn = None
            try:
                conn = get_db_connection(self._db_path)
                conn.execute("VACUUM")
                conn.close()
                conn = None
                result["vacuum"] = True
            except sqlite3.Error as exc:
                logger.error("vacuum_failed", error=str(exc))
            finally:
                # 5.61.4 修复：异常路径确保连接归还
                if conn is not None:
                    try:
                        conn.close()
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.debug("suppressed error in database_manager", exc_info=True)

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
            gate_count = conn.execute("SELECT COUNT(*) FROM gate_runs").fetchone()[0]
            ke_count = 0  # KBG removed — knowledge table dropped (2026-07-19)
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

    def close(self, *, backup_before_close: bool = False) -> None:
        """
        优雅关闭：WAL checkpoint + 可选备份 + 关闭连接池。

        参数
        ----
        backup_before_close
            True 时在关闭前自动备份（默认 False）。
            治本（2026-06-29 阶段A+）：默认改为 False，消灭每次 close 自动创建
            zalpha_metadata_*.db 备份的源头（118 个 .db 残留的 85% 来源）。
            需要备份时显式传 backup_before_close=True，或显式调用 backup()。
            备份唯一真源：本类 backup() 方法（显式调用）。
        """
        if self._closed:
            return

        with self._lock:
            if self._closed:
                return

            if backup_before_close:
                try:
                    self.backup(label="pre_close")
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.warning("pre_close_backup_failed: %s", exc, exc_info=True)

            self._closed = True

            # 5.73.4 修复：原 wal_checkpoint_truncate() 未被 try/except 包裹（对比 conn.close() 有保护）。
            # WAL checkpoint 抛异常会掩盖with块原始异常并中断连接池清理流程。
            try:
                self.wal_checkpoint_truncate()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("suppressed error in database_manager", exc_info=True)

            for conn in self._conn_pool:
                try:
                    conn.close()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("suppressed error in database_manager", exc_info=True)
                self._conn_meta.pop(id(conn), None)  # 5.64.3：清理元数据侧表
            self._conn_pool.clear()
            # 5.64.4 修复：唤醒 get_connection 中的等待者（其循环内会检测 _closed 抛 DatabaseManagerError）
            self._pool_cond.notify_all()

            logger.info("database_manager_closed")

    # ------------------------------------------------------------------
    # Phase 2 扩展方法（T-DB-005~T-DB-012）
    # ------------------------------------------------------------------

    def verify_backup(self, backup_path: Path | str) -> dict:
        """T-DB-005: 验证备份文件完整性。

        返回 dict{integrity_ok, table_count, row_counts, duration_ms}。
        """
        start = time.perf_counter()
        backup = Path(backup_path)
        if not backup.exists():
            raise DatabaseManagerError(f"备份文件不存在: {backup}")
        conn = get_db_connection(str(backup))
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            integrity = conn.execute("PRAGMA integrity_check").fetchone()
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            row_counts = {}
            for t in tables:
                # 5.66.6 修复：白名单校验表名后再用于 f-string 拼接（原 [t['name']] 方括号为
                # SQL Server 语法，SQLite 下无效防御；改用白名单校验）
                try:
                    safe_table = _validate_table_name(t["name"])
                except ValueError:
                    logger.debug("verify_backup: skip table not in whitelist: %s", t["name"])
                    continue
                cnt = conn.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()
                row_counts[safe_table] = cnt[0] if cnt else 0
            duration_ms = (time.perf_counter() - start) * 1000
            return {
                "integrity_ok": integrity is not None and integrity[0] == "ok",
                "integrity_detail": integrity[0] if integrity else "unknown",
                "table_count": len(tables),
                "row_counts": row_counts,
                "duration_ms": round(duration_ms, 2),
            }
        finally:
            conn.close()

    def dead_letter_queue(self, limit: int = 50) -> list[dict[str, object]]:
        """T-DB-006: 查询未处理的补偿事件（死信队列）。

        返回补偿失败且未重试超过 3 次的 events 列表。
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT e.event_id, e.payload, e.created_at,
                       COALESCE(e.payload->>'$.retry_count', '0') AS retry_count
                FROM events e
                WHERE e.event_type = 'compensation'
                  AND COALESCE(CAST(json_extract(e.payload, '$.processed') AS INTEGER), 0) = 0
                  AND COALESCE(CAST(json_extract(e.payload, '$.retry_count') AS INTEGER), 0) < 3
                ORDER BY e.created_at ASC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]
        finally:
            self.return_connection(conn)

    def retry_dlq(self) -> int:
        """T-DB-006: 重试死信队列中的补偿事件。返回成功重试次数。"""
        import json as _json

        conn = self.get_connection()
        success = 0
        try:
            dead_letters = self.dead_letter_queue()
            for dl in dead_letters:
                event_id = dl["event_id"]
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    payload = _json.loads(str(dl["payload"])) if isinstance(dl["payload"], str) else dict(dl["payload"])
                    payload["processed"] = 1
                    payload["processed_at"] = now_iso()
                    conn.execute(
                        "UPDATE events SET payload = ?, processed_at = ? WHERE event_id = ?",
                        (_json.dumps(payload, ensure_ascii=False), now_iso(), event_id),
                    )
                    conn.execute("COMMIT")
                    success += 1
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    try:
                        conn.execute("ROLLBACK")
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.warning("suppressed error in database_manager", exc_info=True)
                    # 5.61.3 修复：retry_count 更新纳入独立事务（BEGIN IMMEDIATE...COMMIT）。
                    # 原实现 ROLLBACK 后在事务外 UPDATE 再 COMMIT——autocommit 模式下
                    # COMMIT 必抛 OperationalError 中断整个循环；且 UPDATE 无事务保护。
                    # 失败时回滚并记录日志后继续处理下一条（尽力记录语义不变）。
                    try:
                        payload = _json.loads(str(dl["payload"])) if isinstance(dl["payload"], str) else dict(dl["payload"])
                        payload["retry_count"] = payload.get("retry_count", 0) + 1
                        conn.execute("BEGIN IMMEDIATE")
                        conn.execute(
                            SQL_UPDATE_EVENTS_RETRY_COUNT,
                            (_json.dumps(payload, ensure_ascii=False), event_id),
                        )
                        conn.execute("COMMIT")
                    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                        try:
                            conn.execute("ROLLBACK")
                        except Exception as e2:  # noqa: BLE001 — 5.135治标: broad exception catch
                            logger.warning("suppressed error in database_manager", exc_info=True)
                        logger.warning("retry_dlq_retry_count_update_failed", event_id=event_id, exc_info=True)
            return success
        finally:
            self.return_connection(conn)

    def prometheus_export(self) -> str:
        """T-DB-009: 导出 Prometheus 格式的指标数据。

        返回 Prometheus text exposition format 字符串。
        """
        stats = self.stats()
        lines = [
            "# HELP zalpha_db_task_count Total task count",
            f"zalpha_db_task_count {stats.get('task_count', 0)}",
            "# HELP zalpha_db_event_count Total event count",
            f"zalpha_db_event_count {stats.get('event_count', 0)}",
            "# HELP zalpha_db_gate_count Total gate count",
            f"zalpha_db_gate_count {stats.get('gate_count', 0)}",
            "# HELP zalpha_db_size_mb Database file size in MB",
            f"zalpha_db_size_mb {stats.get('db_size_mb', 0)}",
            "# HELP zalpha_db_wal_size_mb WAL file size in MB",
            f"zalpha_db_wal_size_mb {stats.get('wal_size_mb', 0)}",
            "# HELP zalpha_db_slow_query_count Slow query count",
            f"zalpha_db_slow_query_count {stats.get('slow_query_count', 0)}",
            "# HELP zalpha_db_schema_version Schema version",
            f"zalpha_db_schema_version {stats.get('schema_version', 0)}",
        ]
        return "\n".join(lines) + "\n"

    def connection_leak_detector(self, max_idle_seconds: float = 300.0) -> dict:
        """T-DB-011: 检测连接泄漏（超过最大空闲时间的连接）。

        返回 dict{leaked_count, actionable, detail}。

        5.64.3 修复：原实现检测 conn._last_used_at，但 sqlite3.Connection 不支持
        自定义属性、该时间戳从未被设置，检测器恒返回 0 形同虚设。现从元数据侧表
        _conn_meta（get/return_connection 每次维护 last_used_at）读取。
        """
        with self._lock:
            leaked = []
            now_ts = time.time()
            for i, conn in enumerate(self._conn_pool):
                meta = self._conn_meta.get(id(conn))
                if meta is None:
                    continue
                idle_time = now_ts - float(meta["last_used_at"])
                if idle_time > max_idle_seconds:
                    leaked.append({"conn_index": i, "idle_seconds": round(idle_time, 1)})
            actionable = len(leaked) > 10
            return {
                "leaked_count": len(leaked),
                "actionable": actionable,
                "escalation": "escalation:owner" if actionable else "monitoring",
                "detail": leaked,
                "pool_size": len(self._conn_pool),
            }

    def ai_diagnostic_report(self) -> dict:
        """AP3/T-DB-012: 生成 AI 可读的诊断报告。

        聚合 health_check + stats + schema_drift + query_performance。
        """
        from zephyr.gov_audit.audit_schema import AuditQuery
        from zephyr.governance.observability_governance.query_metrics import query_metrics

        health = self.health_check()
        stats = self.stats()
        try:
            aq = AuditQuery(db_path=self._db_path, auto_init=False)
            drift = aq.query_schema_drift()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            drift = {"error": "audit_query_unavailable", "is_latest": None}
        qm_stats = query_metrics.stats_all()

        return {
            "summary": {
                "verdict": "HEALTHY" if health.healthy else "UNHEALTHY",
                "action_required": not health.healthy,
                "recommended_action": "maintenance()" if not health.healthy else "none",
            },
            "health": health.to_dict(),
            "stats": stats,
            "schema_drift": drift,
            "query_performance": {op: s for op, s in qm_stats.items()},
        }

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close(backup_before_close=exc_type is None)
